import keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
import comtypes
import screen_brightness_control as sbc
from config_manager import ConfigManager
from language_manager import LanguageManager
import logging
from typing import Dict, Optional

class MediaManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager()
        self.logger = logging.getLogger("AICodeEditor.Media")
        
        # Ses aygıtını al
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        # Medya tuşları
        self.media_keys = {
            "play": "play/pause media",
            "pause": "play/pause media",
            "next": "next track",
            "previous": "previous track",
            "stop": "stop media",
            "mute": "volume mute"
        }
        
        # Sistem ayarları
        self.system_config = self.config_manager.get_config("system")
        self.volume_step = self.system_config.get("volume_step", 10)
        self.brightness_step = self.system_config.get("brightness_step", 10)
        
    def control_volume(self, action: str, value: Optional[int] = None) -> str:
        """Ses seviyesini kontrol et"""
        try:
            current_volume = int(self.volume.GetMasterVolumeLevelScalar() * 100)
            
            if action == "up":
                new_volume = min(current_volume + self.volume_step, 100)
                self.volume.SetMasterVolumeLevelScalar(new_volume / 100, None)
                return self.language_manager.get_message("commands.volume.up", level=new_volume)
                
            elif action == "down":
                new_volume = max(current_volume - self.volume_step, 0)
                self.volume.SetMasterVolumeLevelScalar(new_volume / 100, None)
                return self.language_manager.get_message("commands.volume.down", level=new_volume)
                
            elif action == "set" and value is not None:
                new_volume = max(0, min(value, 100))
                self.volume.SetMasterVolumeLevelScalar(new_volume / 100, None)
                return f"Ses seviyesi %{new_volume} olarak ayarlandı"
                
            elif action == "mute":
                self.volume.SetMute(True, None)
                return self.language_manager.get_message("commands.volume.mute")
                
            elif action == "unmute":
                self.volume.SetMute(False, None)
                return self.language_manager.get_message("commands.volume.unmute")
                
        except Exception as e:
            self.logger.error(f"Ses kontrolü hatası: {str(e)}")
            return "Ses kontrolü sırasında hata oluştu"
            
    def control_media(self, action: str) -> str:
        """Medya kontrollerini yönet"""
        try:
            if action in self.media_keys:
                keyboard.press_and_release(self.media_keys[action])
                return f"Medya kontrolü: {action}"
            return "Geçersiz medya kontrolü"
            
        except Exception as e:
            self.logger.error(f"Medya kontrolü hatası: {str(e)}")
            return "Medya kontrolü sırasında hata oluştu"
            
    def control_brightness(self, action: str, value: Optional[int] = None) -> str:
        """Ekran parlaklığını kontrol et"""
        try:
            current = sbc.get_brightness()[0]
            
            if action == "up":
                new_brightness = min(current + self.brightness_step, 100)
                sbc.set_brightness(new_brightness)
                return self.language_manager.get_message("commands.brightness.up", level=new_brightness)
                
            elif action == "down":
                new_brightness = max(current - self.brightness_step, 0)
                sbc.set_brightness(new_brightness)
                return self.language_manager.get_message("commands.brightness.down", level=new_brightness)
                
            elif action == "set" and value is not None:
                new_brightness = max(0, min(value, 100))
                sbc.set_brightness(new_brightness)
                return f"Parlaklık %{new_brightness} olarak ayarlandı"
                
        except Exception as e:
            self.logger.error(f"Parlaklık kontrolü hatası: {str(e)}")
            return "Parlaklık kontrolü sırasında hata oluştu" 