from plyer import notification
import pyttsx3
import logging
from typing import Optional
from pathlib import Path
from config_manager import ConfigManager
from language_manager import LanguageManager
from datetime import datetime
import json

class NotificationManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager()
        self.logger = logging.getLogger("AICodeEditor.Notification")
        
        # Bildirim ayarlarını yükle
        notification_config = self.config_manager.get_config("notifications")
        speech_config = self.config_manager.get_config("speech")
        
        # Varsayılan değerler
        self.voice_feedback = notification_config.get("voice_feedback", True)
        self.max_history = notification_config.get("max_history", 100)
        self.default_timeout = notification_config.get("default_timeout", 10)
        
        # İkon yolları
        self.icon_dir = Path("icons")
        self.default_icon = str(self.icon_dir / "app.ico")
        self.error_icon = str(self.icon_dir / "error.ico")
        self.warning_icon = str(self.icon_dir / "warning.ico")
        self.info_icon = str(self.icon_dir / "info.ico")
        
        # İkon dosyalarının varlığını kontrol et
        self._check_icons()
        
        # Bildirim geçmişi
        self.history = []
        
    def _check_icons(self):
        """İkon dosyalarının varlığını kontrol et ve yoksa varsayılan ikonları oluştur"""
        try:
            # İkon dizinini oluştur
            self.icon_dir.mkdir(exist_ok=True)
            
            # Varsayılan ikonları kopyala veya oluştur
            if not Path(self.default_icon).exists():
                # Burada varsayılan bir ikon dosyası oluşturabilir veya kopyalayabilirsiniz
                pass
                
            if not Path(self.error_icon).exists():
                # Hata ikonu yoksa varsayılan ikonu kullan
                self.error_icon = self.default_icon
                
            if not Path(self.warning_icon).exists():
                # Uyarı ikonu yoksa varsayılan ikonu kullan
                self.warning_icon = self.default_icon
                
            if not Path(self.info_icon).exists():
                # Bilgi ikonu yoksa varsayılan ikonu kullan
                self.info_icon = self.default_icon
                
        except Exception as e:
            self.logger.error(f"İkon kontrolü hatası: {str(e)}")
            # Hata durumunda tüm ikonlar için varsayılan değeri None kullan
            self.default_icon = None
            self.error_icon = None
            self.warning_icon = None
            self.info_icon = None

    def show_notification(self, title: str, message: str, notification_type: str = "info", timeout: int = None):
        """Bildirim göster"""
        try:
            # Timeout değerini ayarla
            if timeout is None:
                timeout = self.default_timeout
            
            try:
                # İkonsuz bildirim göster
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    timeout=timeout
                )
            except Exception as notify_error:
                self.logger.error(f"Bildirim gösterme hatası: {str(notify_error)}")
                # Bildirim gösterilemezse konsola yaz
                print(f"\n{title}: {message}")
            
            # Geçmişe ekle
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "message": message,
                "type": notification_type
            })
            
            # Geçmiş limitini kontrol et
            if len(self.history) > self.max_history:
                self.history.pop(0)
                
            # Sesli geri bildirim
            if self.voice_feedback:
                self._speak_notification(message)
                
        except Exception as e:
            self.logger.error(f"Bildirim hatası: {str(e)}")
            # Hata durumunda konsola yaz
            print(f"\nBildirim Hatası: {str(e)}")
            
    def _speak_notification(self, message: str):
        """Bildirimi seslendir"""
        try:
            engine = pyttsx3.init()
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Sesli bildirim hatası: {str(e)}")
            
    def get_history(self, limit: int = None) -> list:
        """Bildirim geçmişini getir"""
        if limit is None:
            return self.history
        return self.history[-limit:] 