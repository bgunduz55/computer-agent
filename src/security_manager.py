import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from language_manager import LanguageManager
from config_manager import ConfigManager
import logging
import shutil

class SecurityManager:
    def __init__(self):
        self.language_manager = LanguageManager()
        self.config_manager = ConfigManager()
        self.logger = logging.getLogger("AICodeEditor.Security")
        
        # Güvenlik ayarlarını yükle
        self.config_dir = Path("config")
        self.security_config = self._load_security_config()
        
        # Güvenlik ayarlarını al
        self.voice_security = self.security_config.get("voice_recognition", {})
        self.data_privacy = self.security_config.get("data_privacy", {})
        
        # Şifreleme anahtarını oluştur/yükle
        self.key_file = Path("data/security/encryption.key")
        self.key = self._load_or_create_key()
        self.cipher_suite = Fernet(self.key)
        
        # Geçici veri dizini
        self.temp_dir = Path("data/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_security_config(self) -> dict:
        """Güvenlik yapılandırmasını yükle"""
        try:
            config_file = self.config_dir / "default.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("security", {})
            return {}
        except Exception as e:
            self.logger.error(f"Güvenlik yapılandırması yükleme hatası: {str(e)}")
            return {}
        
    def _load_or_create_key(self) -> bytes:
        """Şifreleme anahtarını yükle veya oluştur"""
        try:
            if self.key_file.exists():
                return self.key_file.read_bytes()
            else:
                key = Fernet.generate_key()
                self.key_file.parent.mkdir(parents=True, exist_ok=True)
                self.key_file.write_bytes(key)
                return key
        except Exception as e:
            self.logger.error(f"Anahtar yükleme hatası: {str(e)}")
            return Fernet.generate_key()
            
    def verify_voice(self, voice_data: bytes) -> bool:
        """Ses verisini doğrula"""
        if not self.voice_security.get("enabled", False):
            return True
            
        try:
            # Ses tanıma ve doğrulama işlemleri
            authorized_voices = self.voice_security.get("authorized_voices", [])
            voice_hash = hashlib.sha256(voice_data).hexdigest()
            
            return voice_hash in authorized_voices
        except Exception as e:
            self.logger.error(f"Ses doğrulama hatası: {str(e)}")
            return False
            
    def encrypt_data(self, data: str) -> bytes:
        """Veriyi şifrele"""
        try:
            return self.cipher_suite.encrypt(data.encode())
        except Exception as e:
            self.logger.error(f"Şifreleme hatası: {str(e)}")
            return b""
            
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Şifrelenmiş veriyi çöz"""
        try:
            return self.cipher_suite.decrypt(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Şifre çözme hatası: {str(e)}")
            return ""
            
    def store_command_history(self, command: str):
        """Komut geçmişini kaydet"""
        if not self.data_privacy.get("store_commands", False):
            return
            
        try:
            history_file = self.temp_dir / "command_history.enc"
            commands = []
            
            # Mevcut geçmişi yükle
            if history_file.exists():
                encrypted_data = history_file.read_bytes()
                decrypted_data = self.decrypt_data(encrypted_data)
                commands = json.loads(decrypted_data)
                
            # Yeni komutu ekle
            commands.append({
                "timestamp": datetime.now().isoformat(),
                "command": command
            })
            
            # Şifreleyerek kaydet
            encrypted = self.encrypt_data(json.dumps(commands))
            history_file.write_bytes(encrypted)
            
        except Exception as e:
            self.logger.error(f"Komut geçmişi kaydetme hatası: {str(e)}")
            
    def clear_history(self, older_than: str = None):
        """Geçmişi temizle"""
        try:
            if older_than is None:
                older_than = self.data_privacy.get("auto_clear_history", "24h")
                
            if not older_than:
                return
                
            # Zaman aralığını hesapla
            duration = int(older_than[:-1])
            unit = older_than[-1].lower()
            
            if unit == 'h':
                delta = timedelta(hours=duration)
            elif unit == 'd':
                delta = timedelta(days=duration)
            elif unit == 'w':
                delta = timedelta(weeks=duration)
            else:
                return
                
            cutoff_time = datetime.now() - delta
            
            # Geçmiş dosyalarını temizle
            for file in self.temp_dir.glob("*.enc"):
                if file.stat().st_mtime < cutoff_time.timestamp():
                    file.unlink()
                    
        except Exception as e:
            self.logger.error(f"Geçmiş temizleme hatası: {str(e)}")
            
    def secure_delete(self, file_path: Path):
        """Güvenli dosya silme"""
        try:
            if not file_path.exists():
                return
                
            # Dosyayı rastgele verilerle üzerine yaz
            file_size = file_path.stat().st_size
            with open(file_path, 'wb') as f:
                f.write(os.urandom(file_size))
                
            # Dosyayı sil
            file_path.unlink()
            
        except Exception as e:
            self.logger.error(f"Güvenli silme hatası: {str(e)}")
            
    def verify_command(self, command: str) -> bool:
        """Komutu doğrula ve güvenlik kontrollerini yap"""
        try:
            # Komut içeriğini kontrol et
            command = command.lower()
            
            # Güvenlik ayarlarını al
            security_config = self.security_config.get("voice_recognition", {})
            allowed_commands = security_config.get("allowed_commands", [])
            
            # Eğer izin verilen komut listesi boşsa veya "all" içeriyorsa, tüm komutlara izin ver
            if not allowed_commands or "all" in allowed_commands:
                return True
                
            # Komutları config'den al
            commands_config = self.config_manager.get_config("commands", {})
            action_groups = commands_config.get("actions", {})
            
            # Her bir komut grubu için kontrol et
            for group_name, commands in action_groups.items():
                # Eğer bu grup izin verilen komutlar içindeyse ve komut bu gruptaysa
                if group_name in allowed_commands and any(cmd in command for cmd in commands):
                    return True
                    
            # Hiçbir izin verilen komut grubuyla eşleşme olmadıysa
            return False
            
        except Exception as e:
            self.logger.error(f"Komut doğrulama hatası: {str(e)}")
            return False 