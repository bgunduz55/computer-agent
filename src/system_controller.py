import psutil
import os
import screen_brightness_control as sbc
import sounddevice as sd
import numpy as np
import subprocess
from datetime import datetime
from pathlib import Path
from config_manager import ConfigManager

class SystemController:
    def __init__(self):
        self.config_manager = ConfigManager()
        system_config = self.config_manager.get_config("system")
        
        self.volume_step = system_config.get("volume_step", 10)
        self.brightness_step = system_config.get("brightness_step", 10)
        self.screenshot_dir = Path(system_config.get("screenshot_dir", "screenshots"))
        self.log_dir = Path(system_config.get("log_dir", "data/logs"))
        
        # Dizinleri oluştur
        self.screenshot_dir.mkdir(exist_ok=True, parents=True)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        self.previous_volume = None
        
    def get_system_info(self):
        """Sistem bilgilerini al"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        battery = psutil.sensors_battery()
        
        return {
            "CPU Kullanımı": f"%{cpu}",
            "RAM Kullanımı": f"%{memory.percent}",
            "Disk Kullanımı": f"%{disk.percent}",
            "Pil Durumu": f"%{battery.percent if battery else 'Bilgi yok'}"
        }
        
    def control_brightness(self, value=None, increase=False, decrease=False):
        """Ekran parlaklığını kontrol et"""
        current = sbc.get_brightness()[0]
        
        if increase:
            new_value = min(current + 10, 100)
        elif decrease:
            new_value = max(current - 10, 0)
        else:
            new_value = max(0, min(value if value else current, 100))
            
        sbc.set_brightness(new_value)
        return f"Parlaklık %{new_value} olarak ayarlandı"
        
    def control_volume(self, value=None, mute=False, unmute=False):
        """Ses seviyesini kontrol et"""
        if mute:
            if self.previous_volume is None:
                self.previous_volume = sd.default.device[1]
            sd.default.device = (sd.default.device[0], 0)
            return "Ses kapatıldı"
            
        if unmute and self.previous_volume is not None:
            sd.default.device = (sd.default.device[0], self.previous_volume)
            self.previous_volume = None
            return "Ses açıldı"
            
        if value is not None:
            sd.default.device = (sd.default.device[0], max(0, min(value, 100)))
            return f"Ses seviyesi %{value} olarak ayarlandı"
            
    def power_management(self, action):
        """Güç yönetimi"""
        if action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Bilgisayar uyku moduna alınıyor"
        elif action == "shutdown":
            os.system("shutdown /s /t 60")
            return "Bilgisayar 1 dakika içinde kapanacak"
        elif action == "restart":
            os.system("shutdown /r /t 60")
            return "Bilgisayar 1 dakika içinde yeniden başlatılacak"
        elif action == "cancel":
            os.system("shutdown /a")
            return "Güç işlemi iptal edildi" 