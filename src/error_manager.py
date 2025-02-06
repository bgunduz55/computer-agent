import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from config_manager import ConfigManager
from language_manager import LanguageManager
import traceback
import sys
import shutil
import threading
import time

class ErrorManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager()
        self.logger = logging.getLogger("AICodeEditor.Error")
        
        # Log dizinleri
        self.log_dir = Path("data/logs")
        self.backup_dir = Path("data/backups")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Log dosyaları
        self.error_log = self.log_dir / "errors.json"
        self.crash_log = self.log_dir / "crashes.log"
        self.debug_log = self.log_dir / "debug.log"
        
        # Hata veritabanı
        self.error_db = self._load_error_db()
        
        # Otomatik yedekleme için zamanlayıcı başlat
        self.backup_thread = threading.Thread(target=self._auto_backup, daemon=True)
        self.backup_thread.start()
        
        # Hata çözüm şablonları
        self.recovery_actions = {
            "FileNotFoundError": self._handle_file_not_found,
            "PermissionError": self._handle_permission_error,
            "MemoryError": self._handle_memory_error,
            "ConnectionError": self._handle_connection_error,
            "TimeoutError": self._handle_timeout_error
        }
        
    def _auto_backup(self):
        """Otomatik yedekleme işlemi"""
        while True:
            try:
                # Her 6 saatte bir yedekle
                self._create_backup()
                time.sleep(6 * 3600)  # 6 saat bekle
            except Exception as e:
                self.logger.error(f"Otomatik yedekleme hatası: {str(e)}")
                time.sleep(3600)  # Hata durumunda 1 saat bekle
    
    def _create_backup(self):
        """Yedek oluştur"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            # Önemli dosyaları yedekle
            critical_files = [
                "config/default.json",
                "config/user.json",
                "data/logs/errors.json",
                "data/logs/crashes.log"
            ]
            
            for file_path in critical_files:
                src = Path(file_path)
                if src.exists():
                    dst = backup_path / src.name
                    shutil.copy2(src, dst)
            
            # Eski yedekleri temizle (son 5 yedek kalsın)
            self._cleanup_old_backups()
            
            self.logger.info(f"Yedek oluşturuldu: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Yedek oluşturma hatası: {str(e)}")
    
    def _cleanup_old_backups(self):
        """Eski yedekleri temizle"""
        try:
            backups = sorted(self.backup_dir.glob("backup_*"))
            if len(backups) > 5:
                for backup in backups[:-5]:
                    shutil.rmtree(backup)
        except Exception as e:
            self.logger.error(f"Eski yedek temizleme hatası: {str(e)}")
    
    def handle_error(self, error: Exception, context: str = "") -> bool:
        """Hatayı yakala ve uygun kurtarma işlemini başlat"""
        try:
            # Hatayı kaydet
            error_data = self.log_error(error, context)
            
            # Hata tipine göre kurtarma işlemini başlat
            error_type = type(error).__name__
            if error_type in self.recovery_actions:
                return self.recovery_actions[error_type](error, context)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Hata yönetimi sırasında hata: {str(e)}")
            return False
    
    def _handle_file_not_found(self, error: Exception, context: str) -> bool:
        """Dosya bulunamadı hatası için kurtarma"""
        try:
            missing_file = str(error).split("'")[1]
            
            # Yedekten geri yüklemeyi dene
            latest_backup = self._find_latest_backup()
            if latest_backup:
                backup_file = latest_backup / Path(missing_file).name
                if backup_file.exists():
                    shutil.copy2(backup_file, missing_file)
                    self.logger.info(f"Dosya yedekten geri yüklendi: {missing_file}")
                    return True
            
            # Varsayılan dosyayı oluştur
            if "config" in missing_file:
                self._create_default_config(missing_file)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Dosya kurtarma hatası: {str(e)}")
            return False
    
    def _handle_permission_error(self, error: Exception, context: str) -> bool:
        """İzin hatası için kurtarma"""
        try:
            file_path = str(error).split("'")[1]
            
            # Dosya izinlerini düzeltmeyi dene
            try:
                import os
                os.chmod(file_path, 0o666)  # Okuma/yazma izni ver
                self.logger.info(f"Dosya izinleri düzeltildi: {file_path}")
                return True
            except:
                return False
                
        except Exception as e:
            self.logger.error(f"İzin düzeltme hatası: {str(e)}")
            return False
    
    def _handle_memory_error(self, error: Exception, context: str) -> bool:
        """Bellek hatası için kurtarma"""
        try:
            # Garbage collector'ı çalıştır
            import gc
            gc.collect()
            
            # Temp dosyalarını temizle
            temp_dir = Path("data/temp")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                temp_dir.mkdir()
            
            self.logger.info("Bellek temizlendi")
            return True
            
        except Exception as e:
            self.logger.error(f"Bellek temizleme hatası: {str(e)}")
            return False
    
    def _handle_connection_error(self, error: Exception, context: str) -> bool:
        """Bağlantı hatası için kurtarma"""
        try:
            # Çevrimdışı moda geç
            self.config_manager.set_offline_mode(True)
            
            # Yerel önbelleği kullan
            cache_dir = Path("data/cache")
            if cache_dir.exists():
                self.logger.info("Çevrimdışı moda geçildi, yerel önbellek kullanılıyor")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Bağlantı kurtarma hatası: {str(e)}")
            return False
    
    def _handle_timeout_error(self, error: Exception, context: str) -> bool:
        """Zaman aşımı hatası için kurtarma"""
        try:
            # Yeniden deneme sayacı
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    # İşlemi yeniden dene
                    if context == "api_call":
                        # API çağrısını yeniden dene
                        pass
                    elif context == "file_operation":
                        # Dosya işlemini yeniden dene
                        pass
                    
                    return True
                    
                except TimeoutError:
                    retry_count += 1
                    time.sleep(2 ** retry_count)  # Üstel bekleme
            
            return False
            
        except Exception as e:
            self.logger.error(f"Timeout kurtarma hatası: {str(e)}")
            return False
    
    def _find_latest_backup(self) -> Optional[Path]:
        """En son yedeği bul"""
        try:
            backups = sorted(self.backup_dir.glob("backup_*"))
            return backups[-1] if backups else None
        except Exception as e:
            self.logger.error(f"Yedek arama hatası: {str(e)}")
            return None
    
    def _create_default_config(self, config_path: str):
        """Varsayılan config dosyası oluştur"""
        try:
            default_config = {
                "language": {"default": "tr"},
                "ai": {
                    "default_model": "deepseek-r1:7b",
                    "models": {
                        "deepseek-r1:7b": {
                            "temperature": 0.7,
                            "max_tokens": 2048
                        }
                    }
                }
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
                
            self.logger.info(f"Varsayılan config oluşturuldu: {config_path}")
            
        except Exception as e:
            self.logger.error(f"Varsayılan config oluşturma hatası: {str(e)}")
    
    def restore_from_backup(self, timestamp: str = None) -> bool:
        """Yedekten geri yükle"""
        try:
            if timestamp:
                backup_path = self.backup_dir / f"backup_{timestamp}"
            else:
                backup_path = self._find_latest_backup()
            
            if not backup_path or not backup_path.exists():
                return False
            
            # Kritik dosyaları geri yükle
            for backup_file in backup_path.glob("*"):
                if backup_file.name.endswith(('.json', '.log')):
                    target_path = self.log_dir / backup_file.name
                    shutil.copy2(backup_file, target_path)
            
            self.logger.info(f"Sistem yedekten geri yüklendi: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Yedekten geri yükleme hatası: {str(e)}")
            return False
            
    def _load_error_db(self) -> dict:
        """Hata veritabanını yükle"""
        try:
            if self.error_log.exists():
                return json.loads(self.error_log.read_text(encoding='utf-8'))
            return {"errors": [], "statistics": {}}
        except Exception as e:
            self.logger.error(f"Hata veritabanı yükleme hatası: {str(e)}")
            return {"errors": [], "statistics": {}}
            
    def log_error(self, error: Exception, context: str = "", severity: str = "ERROR") -> dict:
        """Hatayı kaydet ve analiz et"""
        try:
            error_data = {
                "timestamp": datetime.now().isoformat(),
                "type": type(error).__name__,
                "message": str(error),
                "context": context,
                "severity": severity,
                "traceback": traceback.format_exc()
            }
            
            # Hatayı veritabanına ekle
            self.error_db["errors"].append(error_data)
            
            # İstatistikleri güncelle
            error_type = type(error).__name__
            self.error_db["statistics"][error_type] = self.error_db["statistics"].get(error_type, 0) + 1
            
            # Veritabanını kaydet
            self._save_error_db()
            
            return error_data
            
        except Exception as e:
            self.logger.error(f"Hata kaydı sırasında hata: {str(e)}")
            return {}
            
    def analyze_errors(self, time_window: str = "24h") -> Dict:
        """Hataları analiz et ve özet çıkar"""
        try:
            cutoff_time = self._parse_time_window(time_window)
            recent_errors = [
                error for error in self.error_db["errors"]
                if datetime.fromisoformat(error["timestamp"]) > cutoff_time
            ]
            
            analysis = {
                "total_errors": len(recent_errors),
                "error_types": {},
                "most_common": None,
                "critical_errors": [],
                "trends": self._analyze_error_trends(recent_errors)
            }
            
            # Hata tiplerini say
            for error in recent_errors:
                error_type = error["type"]
                analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
                
                if error["severity"] == "CRITICAL":
                    analysis["critical_errors"].append(error)
                    
            # En sık görülen hatayı bul
            if analysis["error_types"]:
                analysis["most_common"] = max(
                    analysis["error_types"].items(),
                    key=lambda x: x[1]
                )
                
            return analysis
            
        except Exception as e:
            self.logger.error(f"Hata analizi sırasında hata: {str(e)}")
            return {}
            
    def suggest_solutions(self, error_type: str) -> List[dict]:
        """Hata için çözüm önerileri sun"""
        solutions = []
        
        if "speech" in error_type.lower():
            solutions.append(self.solution_templates["speech_error"])
        elif "memory" in error_type.lower():
            solutions.append(self.solution_templates["memory_error"])
        elif "connection" in error_type.lower():
            solutions.append(self.solution_templates["connection_error"])
            
        return solutions 

    def _save_error_db(self):
        """Hata veritabanını kaydet"""
        try:
            with open(self.error_log, 'w', encoding='utf-8') as f:
                json.dump(self.error_db, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Hata veritabanı kaydetme hatası: {str(e)}") 