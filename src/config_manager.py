from pathlib import Path
import json
import logging
from typing import Any, Dict, Optional, Tuple, List
import shutil
import jsonschema
from jsonschema import validate
from datetime import datetime, timedelta
import threading
import time
from cryptography.fernet import Fernet
import hashlib
import requests
import os
import tempfile

class ConfigManager:
    def __init__(self):
        self.config_dir = Path("config")  # Ana dizindeki config klasörü
        self.backup_dir = Path("data/backups")
        self.default_config_path = self.config_dir / "default.json"
        self.user_config_path = self.config_dir / "user.json"
        self.schema_path = self.config_dir / "schema.json"
        self.logger = logging.getLogger("AICodeEditor.Config")
        
        # Config dizinini oluştur
        self.config_dir.mkdir(exist_ok=True, parents=True)
        self.backup_dir.mkdir(exist_ok=True, parents=True)
        
        # Değişiklik izleme
        self._last_modified = {}
        self._config_lock = threading.Lock()
        
        # Şema ve varsayılan yapılandırmayı yükle
        self.schema = self._load_schema()
        self.config = self._load_default_config()
        
        # Kullanıcı yapılandırmasını yükle ve birleştir
        self._load_user_config()
        
        # Kullanıcı yapılandırma şablonunu oluştur
        self._create_user_config_template()
        
        # Otomatik yedekleme için zamanlayıcı başlat
        self._start_backup_timer()
        
        # Şifreleme için
        self.encryption_key = self._load_or_create_encryption_key()
        self.encryption_enabled = self.config.get("security", {}).get("data_privacy", {}).get("encryption_enabled", False)
        
        # Senkronizasyon için
        self.sync_interval = 300  # 5 dakika
        self.sync_url = "https://api.example.com/config/sync"  # Örnek URL
        self._start_sync_timer()
        
        # Thread-safe yapı için lock eklenmeli
        self._lock = threading.Lock()
        
    def _start_backup_timer(self):
        """Otomatik yedekleme zamanlayıcısını başlat"""
        def backup_task():
            while True:
                time.sleep(3600)  # Her saat başı
                self._create_backup()
                
        self.backup_thread = threading.Thread(target=backup_task, daemon=True)
        self.backup_thread.start()
        
    def _create_backup(self):
        """Mevcut yapılandırmanın yedeğini oluştur"""
        try:
            # Yedekleme dizini kontrolü eksik
            self.backup_dir = Path("data/backups")
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"config_backup_{timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            # Dosyaları yedekle
            shutil.copy2(self.default_config_path, backup_path)
            shutil.copy2(self.user_config_path, backup_path)
            shutil.copy2(self.schema_path, backup_path)
            
            # Eski yedekleri temizle (son 5 yedek kalsın)
            backups = sorted(self.backup_dir.glob("config_backup_*"))
            if len(backups) > 5:
                for backup in backups[:-5]:
                    shutil.rmtree(backup)
                    
            self.logger.info(f"Yapılandırma yedeği oluşturuldu: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Yedekleme hatası: {str(e)}")
            
    def _load_schema(self) -> dict:
        """JSON şemasını yükle"""
        try:
            if not self.schema_path.exists():
                self.logger.warning("Şema dosyası bulunamadı")
                return {}
                
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Şema yükleme hatası: {str(e)}")
            return {}
            
    def _validate_config(self, config: dict) -> bool:
        """Yapılandırmayı doğrula"""
        try:
            if self.schema:
                validate(instance=config, schema=self.schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            self.logger.error(f"Yapılandırma doğrulama hatası: {str(e)}")
            return False
            
    def _validate_config_extended(self, config: dict) -> Tuple[bool, List[str]]:
        """Gelişmiş yapılandırma doğrulaması"""
        if not isinstance(config, dict):
            return False, ["Yapılandırma bir sözlük olmalıdır"]
        
        errors = []
        
        try:
            # JSON Schema doğrulaması
            validate(instance=config, schema=self.schema)
            
            # Özel doğrulama kuralları
            if "speech" in config:
                speech_config = config["speech"]
                
                # Ses sentezi ayarları kontrolü
                if "synthesis" in speech_config:
                    synthesis = speech_config["synthesis"]
                    if synthesis.get("rate", 0) > 300:
                        errors.append("Konuşma hızı çok yüksek (maksimum 300)")
                    if synthesis.get("volume", 0) > 1:
                        errors.append("Ses seviyesi 0-1 arasında olmalı")
                        
            # Pencere boyutu kontrolü
            if "interface" in config:
                window_size = config["interface"].get("window_size", {})
                min_width, min_height = 640, 480
                
                if window_size.get("width", min_width) < min_width:
                    errors.append(f"Pencere genişliği en az {min_width} olmalı")
                if window_size.get("height", min_height) < min_height:
                    errors.append(f"Pencere yüksekliği en az {min_height} olmalı")
                    
            # Güvenlik ayarları kontrolü
            if "security" in config:
                security = config["security"]
                if "voice_recognition" in security:
                    threshold = security["voice_recognition"].get("confidence_threshold", 0)
                    if threshold < 0.5:
                        errors.append("Güven eşiği çok düşük (minimum 0.5)")
                        
            return len(errors) == 0, errors
            
        except jsonschema.exceptions.ValidationError as e:
            errors.append(f"Şema doğrulama hatası: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Doğrulama hatası: {str(e)}")
            return False, errors
            
    def _create_user_config_template(self):
        """Kullanıcı yapılandırma şablonunu oluştur"""
        if not self.user_config_path.exists():
            template = {
                "interface": {
                    "theme": "dark",
                    "font_size": 12
                },
                "speech": {
                    "synthesis": {
                        "rate": 150,
                        "volume": 0.9
                    }
                },
                "system": {
                    "volume_step": 10,
                    "brightness_step": 10
                }
            }
            
            try:
                with open(self.user_config_path, 'w', encoding='utf-8') as f:
                    json.dump(template, f, indent=4, ensure_ascii=False)
                self.logger.info("Kullanıcı yapılandırma şablonu oluşturuldu")
            except Exception as e:
                self.logger.error(f"Şablon oluşturma hatası: {str(e)}")
                
    def _load_default_config(self) -> dict:
        """Varsayılan yapılandırmayı yükle"""
        try:
            if not self.default_config_path.exists():
                self.logger.warning("Varsayılan yapılandırma dosyası bulunamadı")
                return {}
                    
            with open(self.default_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Varsayılan yapılandırma yükleme hatası: {str(e)}")
            return {}
        
    def _load_user_config(self):
        """Kullanıcı yapılandırmasını yükle ve birleştir"""
        try:
            if self.user_config_path.exists():
                with open(self.user_config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
        except Exception as e:
            self.logger.error(f"Kullanıcı yapılandırması yükleme hatası: {str(e)}")
            
    def _save_config(self, config: dict):
        """Konfigürasyonu kaydet"""
        try:
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Config kaydetme hatası: {str(e)}")
            
    def get_model_config(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Model konfigürasyonunu getir"""
        if not model_name:
            model_name = self.config["ai"]["default_model"]
            
        return self.config["ai"]["models"].get(model_name, {})
        
    def set_model(self, model_name: str) -> bool:
        """Varsayılan modeli değiştir"""
        if model_name in self.config["ai"]["models"]:
            self.config["ai"]["default_model"] = model_name
            self._save_config(self.config)
            return True
        return False
        
    def update_model_config(self, model_name: str, params: dict) -> bool:
        """Model parametrelerini güncelle"""
        try:
            if model_name in self.config["ai"]["models"]:
                self.config["ai"]["models"][model_name].update(params)
                self._save_config(self.config)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Model config güncelleme hatası: {str(e)}")
            return False
            
    def get_config(self, section: str, default: Any = None) -> Any:
        """Belirli bir bölümün yapılandırmasını getir"""
        try:
            if section in self.config:
                return self.config[section]
            return default if default is not None else {}
        except Exception as e:
            self.logger.error(f"Yapılandırma alma hatası: {str(e)}")
            return default if default is not None else {}

    def update_config(self, section: str, key: str, value: Any) -> bool:
        """Yapılandırmayı güncelle ve doğrula"""
        try:
            # Derin güncelleme yap
            current = self.config.get(section, {})
            keys = key.split('.')
            temp = current
            for k in keys[:-1]:
                temp = temp.setdefault(k, {})
            temp[keys[-1]] = value
            
            # Değişiklikleri geçici olarak uygula
            temp_config = self.config.copy()
            temp_config[section] = current
            
            # Doğrula
            if self._validate_config(temp_config):
                self.config = temp_config
                self._save_config(self.config)
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Yapılandırma güncelleme hatası: {str(e)}")
            return False

    def reset_config(self, section: Optional[str] = None):
        """Yapılandırmayı sıfırla"""
        try:
            with self._config_lock:
                if section:
                    # Belirli bir bölümü sıfırla
                    default_section = self._load_default_config().get(section, {})
                    self.config[section] = default_section
                else:
                    # Tüm yapılandırmayı sıfırla
                    self.config = self._load_default_config()
                    
                # Kullanıcı yapılandırmasını güncelle
                self._save_user_config()
                self.logger.info(f"Yapılandırma sıfırlandı: {section if section else 'tümü'}")
                
        except Exception as e:
            self.logger.error(f"Sıfırlama hatası: {str(e)}")
            
    def _save_user_config(self):
        """Kullanıcı yapılandırmasını kaydet"""
        try:
            # Varsayılan yapılandırmadan farklı olan ayarları bul
            default_config = self._load_default_config()
            user_config = {}
            
            for section, values in self.config.items():
                if section in default_config:
                    diff = self._get_config_diff(default_config[section], values)
                    if diff:
                        user_config[section] = diff
                        
            # Kullanıcı yapılandırmasını kaydet
            with open(self.user_config_path, 'w', encoding='utf-8') as f:
                json.dump(user_config, f, indent=4, ensure_ascii=False)
                
            self._last_modified[self.user_config_path] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Kullanıcı yapılandırması kaydetme hatası: {str(e)}")
            
    def _get_config_diff(self, default: dict, current: dict) -> dict:
        """İki yapılandırma arasındaki farkları bul"""
        diff = {}
        for key, value in current.items():
            if key not in default or default[key] != value:
                if isinstance(value, dict) and isinstance(default.get(key, {}), dict):
                    sub_diff = self._get_config_diff(default[key], value)
                    if sub_diff:
                        diff[key] = sub_diff
                else:
                    diff[key] = value
        return diff 

    def _save_config_history(self, old_config: dict, new_config: dict):
        """Yapılandırma değişiklik geçmişini kaydet"""
        try:
            history_dir = Path("data/config_history")
            history_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = history_dir / f"changes_{timestamp}.json"
            
            changes = {
                "timestamp": timestamp,
                "changes": self._get_config_changes(old_config, new_config)
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(changes, f, indent=4, ensure_ascii=False)
                
            # Eski geçmiş dosyalarını temizle (son 30 gün)
            self._cleanup_history_files(history_dir)
            
        except Exception as e:
            self.logger.error(f"Geçmiş kaydetme hatası: {str(e)}")
            
    def _get_config_changes(self, old: dict, new: dict, path: str = "") -> list:
        """İki yapılandırma arasındaki değişiklikleri bul"""
        changes = []
        
        for key in set(old.keys()) | set(new.keys()):
            current_path = f"{path}.{key}" if path else key
            
            if key not in old:
                changes.append({
                    "type": "added",
                    "path": current_path,
                    "value": new[key]
                })
            elif key not in new:
                changes.append({
                    "type": "removed",
                    "path": current_path,
                    "value": old[key]
                })
            elif isinstance(old[key], dict) and isinstance(new[key], dict):
                changes.extend(self._get_config_changes(old[key], new[key], current_path))
            elif old[key] != new[key]:
                changes.append({
                    "type": "modified",
                    "path": current_path,
                    "old_value": old[key],
                    "new_value": new[key]
                })
                
        return changes
        
    def _cleanup_history_files(self, history_dir: Path):
        """Eski geçmiş dosyalarını temizle"""
        try:
            # Maksimum dosya sayısı kontrolü eksik
            max_files = self.config.get("history", {}).get("max_files", 100)
            files = sorted(history_dir.glob("changes_*.json"), key=lambda x: x.stat().st_mtime)
            
            if len(files) > max_files:
                for file in files[:-max_files]:
                    file.unlink()
        except Exception as e:
            self.logger.error(f"Geçmiş temizleme hatası: {str(e)}")
            
    def compare_configs(self, config1_path: str, config2_path: str) -> dict:
        """İki yapılandırmayı karşılaştır"""
        try:
            # Yapılandırmaları yükle
            with open(config1_path, 'r', encoding='utf-8') as f:
                config1 = json.load(f)
            with open(config2_path, 'r', encoding='utf-8') as f:
                config2 = json.load(f)
                
            comparison = {
                "added": [],
                "removed": [],
                "modified": [],
                "unchanged": []
            }
            
            def compare_recursive(path: str, c1: dict, c2: dict):
                for key in set(c1.keys()) | set(c2.keys()):
                    current_path = f"{path}.{key}" if path else key
                    
                    if key not in c1:
                        comparison["added"].append({
                            "path": current_path,
                            "value": c2[key]
                        })
                    elif key not in c2:
                        comparison["removed"].append({
                            "path": current_path,
                            "value": c1[key]
                        })
                    elif isinstance(c1[key], dict) and isinstance(c2[key], dict):
                        compare_recursive(current_path, c1[key], c2[key])
                    elif c1[key] != c2[key]:
                        comparison["modified"].append({
                            "path": current_path,
                            "old_value": c1[key],
                            "new_value": c2[key]
                        })
                    else:
                        comparison["unchanged"].append({
                            "path": current_path,
                            "value": c1[key]
                        })
                        
            compare_recursive("", config1, config2)
            return comparison
            
        except Exception as e:
            self.logger.error(f"Karşılaştırma hatası: {str(e)}")
            return {}

    def _create_config_template(self, template_name: str) -> dict:
        """Yapılandırma şablonu oluştur"""
        templates = {
            "minimal": {
                "interface": {
                    "theme": "dark",
                    "font_size": 12
                },
                "speech": {
                    "synthesis": {
                        "rate": 150,
                        "volume": 0.9
                    }
                }
            },
            "development": {
                "interface": {
                    "theme": "dark",
                    "font_size": 14,
                    "window_size": {
                        "width": 1920,
                        "height": 1080
                    }
                },
                "system": {
                    "default_apps": {
                        "editor": "cursor",
                        "terminal": "windowsterminal",
                        "browser": "brave"
                    }
                },
                "performance": {
                    "monitoring": {
                        "enabled": True,
                        "metrics": ["cpu", "memory", "response_time"]
                    }
                }
            }
        }
        
        return templates.get(template_name, templates["minimal"])

    def backup_config(self, backup_name: str = None) -> bool:
        """Yapılandırma yedeği oluştur"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_name or f"config_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Yapılandırma dosyalarını yedekle
            config_files = {
                "user": self.user_config_path,
                "default": self.default_config_path,
                "schema": self.schema_path
            }
            
            backup_info = {
                "timestamp": timestamp,
                "files": {},
                "checksum": {}
            }
            
            for name, path in config_files.items():
                if path.exists():
                    # Dosya içeriğini şifrele
                    if self.encryption_enabled:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            encrypted = self.encrypt_data(content)
                            backup_file = backup_path / f"{name}.enc"
                            backup_file.write_bytes(encrypted)
                    else:
                        backup_file = backup_path / f"{name}.json"
                        shutil.copy2(path, backup_file)
                        
                    # Checksum hesapla
                    backup_info["checksum"][name] = self._calculate_checksum(path)
                    backup_info["files"][name] = backup_file.name
                    
            # Yedek bilgilerini kaydet
            with open(backup_path / "backup_info.json", 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=4)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Yedekleme hatası: {str(e)}")
            return False
            
    def restore_config(self, backup_name: str) -> bool:
        """Yapılandırmayı geri yükle"""
        try:
            backup_path = self.backup_dir / backup_name
            if not backup_path.exists():
                self.logger.error(f"Yedek bulunamadı: {backup_name}")
                return False
                
            # Yedek bilgilerini oku
            with open(backup_path / "backup_info.json", 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
                
            # Dosyaları geri yükle
            for name, filename in backup_info["files"].items():
                file_path = backup_path / filename
                target_path = getattr(self, f"{name}_config_path")
                
                if ".enc" in filename:
                    # Şifrelenmiş dosyayı çöz
                    encrypted_data = file_path.read_bytes()
                    decrypted = self.decrypt_data(encrypted_data)
                    target_path.write_text(decrypted, encoding='utf-8')
                else:
                    shutil.copy2(file_path, target_path)
                    
                # Checksum kontrolü
                if self._calculate_checksum(target_path) != backup_info["checksum"][name]:
                    raise ValueError(f"Checksum uyuşmazlığı: {name}")
                    
            # Yapılandırmayı yeniden yükle
            self.config = self._load_default_config()
            self._load_user_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Geri yükleme hatası: {str(e)}")
            return False
            
    def _start_sync_timer(self):
        """Senkronizasyon zamanlayıcısını başlat"""
        def sync_task():
            while True:
                try:
                    self._sync_config()
                except Exception as e:
                    self.logger.error(f"Senkronizasyon hatası: {str(e)}")
                time.sleep(self.sync_interval)
                
        self.sync_thread = threading.Thread(target=sync_task, daemon=True)
        self.sync_thread.start()
        
    def _sync_config(self):
        """Yapılandırmayı senkronize et"""
        if not self.get_config("sync_enabled", False):
            return
            
        try:
            # sync_url tanımlanmamış
            self.sync_url = self.config.get("sync", {}).get("url", "https://api.example.com/config/sync")
            
            # _get_auth_token metodu eksik
            def _get_auth_token(self):
                return self.encrypt_data("").decode()
            
            # Yerel değişiklikleri kontrol et
            local_hash = self._calculate_checksum(self.user_config_path)
            
            # Sunucu ile senkronize et
            response = requests.post(
                self.sync_url,
                json={
                    "config_hash": local_hash,
                    "config_data": self._get_encrypted_config()
                }
            )
            
            if response.status_code == 200:
                server_data = response.json()
                if server_data["hash"] != local_hash:
                    # Sunucudan gelen yapılandırmayı uygula
                    self._apply_server_config(server_data["config"])
                    
        except Exception as e:
            self.logger.error(f"Senkronizasyon hatası: {str(e)}")
            
    def _calculate_checksum(self, file_path: Path) -> str:
        """Dosya için checksum hesapla"""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _get_encrypted_config(self) -> str:
        """Yapılandırmayı şifrelenmiş formatta al"""
        try:
            config_str = json.dumps(self.config)
            return self.encrypt_data(config_str)
        except Exception as e:
            self.logger.error(f"Şifreleme hatası: {str(e)}")
            return ""

    def _apply_server_config(self, server_config: dict) -> bool:
        """Sunucudan gelen yapılandırmayı uygula"""
        try:
            # Gelen yapılandırmayı doğrula
            is_valid, errors = self._validate_config_extended(server_config)
            if not is_valid:
                self.logger.error(f"Sunucu yapılandırması geçersiz: {errors}")
                return False
            
            # Geçici dosyaya kaydet
            temp_file = Path(tempfile.gettempdir()) / "temp_config.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(server_config, f, ensure_ascii=False, indent=2)
            
            # Mevcut yapılandırmayı yedekle
            self._create_backup()
            
            # Yeni yapılandırmayı uygula
            shutil.move(str(temp_file), str(self.user_config_path))
            
            # Yapılandırmayı yeniden yükle
            self._load_user_config()
            
            self.logger.info("Sunucu yapılandırması başarıyla uygulandı")
            return True
            
        except Exception as e:
            self.logger.error(f"Sunucu yapılandırması uygulama hatası: {str(e)}")
            return False

    def resolve_conflicts(self, local_config: dict, server_config: dict) -> dict:
        """Yapılandırma çakışmalarını çöz"""
        try:
            resolved_config = {}
            conflicts = []
            
            # Çakışmaları tespit et
            for section in set(local_config.keys()) | set(server_config.keys()):
                if section in local_config and section in server_config:
                    if local_config[section] != server_config[section]:
                        # Çakışma var
                        conflicts.append({
                            "section": section,
                            "local": local_config[section],
                            "server": server_config[section],
                            "timestamp": {
                                "local": self._last_modified.get(section, "unknown"),
                                "server": server_config.get("_metadata", {}).get("modified", "unknown")
                            }
                        })
                    else:
                        # Çakışma yok, değeri kopyala
                        resolved_config[section] = local_config[section]
                elif section in local_config:
                    resolved_config[section] = local_config[section]
                else:
                    resolved_config[section] = server_config[section]
                    
            # Çakışmaları çöz
            if conflicts:
                for conflict in conflicts:
                    section = conflict["section"]
                    # En son değiştirileni seç
                    local_time = datetime.fromisoformat(str(conflict["timestamp"]["local"]))
                    server_time = datetime.fromisoformat(str(conflict["timestamp"]["server"]))
                    
                    if local_time > server_time:
                        resolved_config[section] = conflict["local"]
                        self.logger.info(f"Yerel yapılandırma tercih edildi: {section}")
                    else:
                        resolved_config[section] = conflict["server"]
                        self.logger.info(f"Sunucu yapılandırması tercih edildi: {section}")
                        
                    # Çakışma geçmişini kaydet
                    self._save_conflict_history(conflict)
                    
            return resolved_config
            
        except Exception as e:
            self.logger.error(f"Çakışma çözme hatası: {str(e)}")
            return local_config
            
    def _save_conflict_history(self, conflict: dict):
        """Çakışma geçmişini kaydet"""
        try:
            history_file = Path("data/config_history/conflicts.json")
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
                
            conflict["resolved_at"] = datetime.now().isoformat()
            history.append(conflict)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Çakışma geçmişi kaydetme hatası: {str(e)}")
            
    def view_config_history(self, section: str = None, limit: int = 10) -> list:
        """Yapılandırma geçmişini görüntüle"""
        try:
            history = []
            history_dir = Path("data/config_history")
            
            # Değişiklik geçmişini oku
            for file in sorted(history_dir.glob("changes_*.json"), reverse=True):
                with open(file, 'r', encoding='utf-8') as f:
                    changes = json.load(f)
                    
                if section:
                    # Belirli bir bölümün değişikliklerini filtrele
                    filtered_changes = []
                    for change in changes["changes"]:
                        if change["path"].startswith(section):
                            filtered_changes.append(change)
                            
                    if filtered_changes:
                        changes["changes"] = filtered_changes
                        history.append(changes)
                else:
                    history.append(changes)
                    
                if len(history) >= limit:
                    break
                    
            return history
            
        except Exception as e:
            self.logger.error(f"Geçmiş görüntüleme hatası: {str(e)}")
            return []
            
    def get_remote_configs(self) -> dict:
        """Uzak yapılandırmaları getir"""
        try:
            response = requests.get(
                f"{self.sync_url}/configs",
                headers={"Authorization": f"Bearer {self._get_auth_token()}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Uzak yapılandırma getirme hatası: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Uzak yapılandırma getirme hatası: {str(e)}")
            return {}
            
    def push_config_to_remote(self, config_name: str = "default") -> bool:
        """Yapılandırmayı uzak sunucuya gönder"""
        try:
            encrypted_config = self._get_encrypted_config()
            response = requests.post(
                f"{self.sync_url}/configs/{config_name}",
                headers={"Authorization": f"Bearer {self._get_auth_token()}"},
                json={
                    "config": encrypted_config,
                    "metadata": {
                        "version": "1.0",
                        "modified": datetime.now().isoformat(),
                        "checksum": self._calculate_checksum(self.user_config_path)
                    }
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Uzak yapılandırma gönderme hatası: {str(e)}")
            return False

    def set_sync_policy(self, policy: dict):
        """Senkronizasyon politikasını ayarla"""
        try:
            self.sync_policy = {
                "interval": policy.get("interval", 300),  # 5 dakika
                "retry_count": policy.get("retry_count", 3),
                "retry_delay": policy.get("retry_delay", 60),
                "conflict_resolution": policy.get("conflict_resolution", "server_wins"),
                "sync_sections": policy.get("sync_sections", ["all"]),
                "exclude_sections": policy.get("exclude_sections", []),
                "encryption": policy.get("encryption", True),
                "compression": policy.get("compression", True)
            }
            
            # Zamanlayıcıyı güncelle
            self.sync_interval = self.sync_policy["interval"]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Politika ayarlama hatası: {str(e)}")
            return False

    def rollback_config(self, version: str = None) -> bool:
        """Yapılandırmayı geri al"""
        try:
            if version:
                # Belirli bir versiyona geri dön
                backup_path = self.backup_dir / f"config_backup_{version}"
                if not backup_path.exists():
                    self.logger.error(f"Versiyon bulunamadı: {version}")
                    return False
            else:
                # Son yedeğe geri dön
                backups = sorted(self.backup_dir.glob("config_backup_*"))
                if not backups:
                    self.logger.error("Yedek bulunamadı")
                    return False
                backup_path = backups[-1]
                
            # Mevcut yapılandırmayı yedekle
            self._create_backup()
            
            # Yedeği geri yükle
            for file in backup_path.glob("*.json"):
                if file.stem == "user":
                    shutil.copy2(file, self.user_config_path)
                elif file.stem == "default":
                    shutil.copy2(file, self.default_config_path)
                    
            # Yapılandırmayı yeniden yükle
            self.config = self._load_default_config()
            self._load_user_config()
            
            self.logger.info(f"Yapılandırma geri alındı: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Geri alma hatası: {str(e)}")
            return False

    def save_config(self):
        """Yapılandırmayı kaydet"""
        with self._lock:
            try:
                # Önce yapılandırmayı doğrula
                is_valid, errors = self._validate_config_extended(self.config)
                if not is_valid:
                    self.logger.error(f"Yapılandırma geçersiz: {errors}")
                    return False
                    
                # Yedek oluştur
                self._create_backup()
                
                # Yapılandırmayı kaydet
                with open(self.user_config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                    
                self._last_modified = datetime.now().isoformat()
                self.logger.info("Yapılandırma başarıyla kaydedildi")
                return True
                
            except Exception as e:
                self.logger.error(f"Yapılandırma kaydetme hatası: {str(e)}")
                return False

    def _get_auth_token(self) -> str:
        """Kimlik doğrulama token'ını al"""
        try:
            return self.encrypt_data("").decode()
        except Exception as e:
            self.logger.error(f"Token alma hatası: {str(e)}")
            return ""

    def _load_or_create_encryption_key(self) -> bytes:
        """Şifreleme anahtarını yükle veya oluştur"""
        key_file = Path("data/security/encryption.key")
        try:
            if key_file.exists():
                return key_file.read_bytes()
            else:
                key = Fernet.generate_key()
                key_file.parent.mkdir(parents=True, exist_ok=True)
                key_file.write_bytes(key)
                return key
        except Exception as e:
            self.logger.error(f"Şifreleme anahtarı yükleme hatası: {str(e)}")
            return Fernet.generate_key()

    def encrypt_data(self, data: str) -> bytes:
        """Veriyi şifrele"""
        if not self.encryption_enabled:
            return data.encode()
        try:
            cipher_suite = Fernet(self.encryption_key)
            return cipher_suite.encrypt(data.encode())
        except Exception as e:
            self.logger.error(f"Şifreleme hatası: {str(e)}")
            return data.encode()

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Şifrelenmiş veriyi çöz"""
        if not self.encryption_enabled:
            return encrypted_data.decode()
        try:
            cipher_suite = Fernet(self.encryption_key)
            return cipher_suite.decrypt(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Şifre çözme hatası: {str(e)}")
            return "" 