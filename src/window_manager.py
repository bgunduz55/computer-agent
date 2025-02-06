import pygetwindow as gw
import screeninfo
from typing import Dict, List, Optional, Tuple
from config_manager import ConfigManager
from language_manager import LanguageManager
import subprocess
import time
import logging

class WindowManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager()
        self.logger = logging.getLogger("AICodeEditor.Window")
        
        self.window_config = self.config_manager.get_config("window_management")
        
        # Monitör bilgilerini al
        self.monitors = screeninfo.get_monitors()
        self.layouts = self.window_config.get("layouts", {})
        
    def apply_layout(self, layout_name: str) -> str:
        """Belirli bir pencere düzenini uygula"""
        try:
            if layout_name not in self.layouts:
                return self.language_manager.get_message("errors.layout_not_found")
                
            layout = self.layouts[layout_name]
            
            # Her monitör için düzeni uygula
            for monitor_id, monitor_layout in layout.items():
                monitor_index = int(monitor_id.replace("monitor", "")) - 1
                if monitor_index < len(self.monitors):
                    monitor = self.monitors[monitor_index]
                    self._apply_monitor_layout(monitor, monitor_layout)
                    
            return self.language_manager.get_message("success.layout_applied", layout=layout_name)
            
        except Exception as e:
            self.logger.error(f"Düzen uygulama hatası: {str(e)}")
            return self.language_manager.get_message("errors.layout_apply_failed")
            
    def _apply_monitor_layout(self, monitor: screeninfo.Monitor, layout: dict):
        """Monitöre özel düzeni uygula"""
        try:
            for window_name, window_config in layout.items():
                if window_name == "main":
                    # Ana pencere
                    window = self._find_window(window_config)
                    if window:
                        self._position_window(window, window_config["position"], monitor)
                else:
                    # Bölünmüş pencereler
                    window = self._find_window(window_config)
                    if window:
                        if window_name == "top":
                            self._position_window(window, "top", monitor)
                        elif window_name == "bottom":
                            self._position_window(window, "bottom", monitor)
                        elif window_name == "left":
                            self._position_window(window, "left", monitor)
                        elif window_name == "right":
                            self._position_window(window, "right", monitor)
                            
        except Exception as e:
            self.logger.error(f"Monitör düzeni uygulama hatası: {str(e)}")
            
    def _find_window(self, app_name: str) -> Optional[gw.Window]:
        """Pencereyi bul veya uygulamayı başlat"""
        try:
            # Mevcut pencereleri kontrol et
            for window in gw.getAllWindows():
                if app_name.lower() in window.title.lower():
                    return window
                    
            # Uygulama açık değilse başlat
            subprocess.Popen(app_name)
            time.sleep(2)  # Uygulamanın açılmasını bekle
            
            # Yeni pencereyi bul
            for window in gw.getAllWindows():
                if app_name.lower() in window.title.lower():
                    return window
                    
        except Exception as e:
            self.logger.error(f"Pencere bulma hatası: {str(e)}")
            return None
            
    def _position_window(self, window: gw.Window, position: str, monitor: screeninfo.Monitor):
        """Pencereyi konumlandır"""
        try:
            if position == "maximized":
                window.maximize()
            elif position == "centered":
                x = monitor.x + (monitor.width - window.width) // 2
                y = monitor.y + (monitor.height - window.height) // 2
                window.moveTo(x, y)
            elif position == "top":
                window.moveTo(monitor.x, monitor.y)
                window.resizeTo(monitor.width, monitor.height // 2)
            elif position == "bottom":
                window.moveTo(monitor.x, monitor.y + monitor.height // 2)
                window.resizeTo(monitor.width, monitor.height // 2)
            elif position == "left":
                window.moveTo(monitor.x, monitor.y)
                window.resizeTo(monitor.width // 2, monitor.height)
            elif position == "right":
                window.moveTo(monitor.x + monitor.width // 2, monitor.y)
                window.resizeTo(monitor.width // 2, monitor.height)
                
        except Exception as e:
            self.logger.error(f"Pencere konumlandırma hatası: {str(e)}")
        
    def get_active_window(self) -> Optional[gw.Window]:
        """Aktif pencereyi getir"""
        try:
            return gw.getActiveWindow()
        except:
            return None
            
    def switch_to_window(self, title: str) -> bool:
        """Belirli bir pencereye geç"""
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                windows[0].activate()
                return True
            return False
        except:
            return False
            
    def arrange_windows(self, arrangement: str = "tile"):
        """Tüm pencereleri düzenle"""
        try:
            windows = gw.getAllWindows()
            if not windows:
                return
                
            if arrangement == "tile":
                self._tile_windows(windows)
            elif arrangement == "cascade":
                self._cascade_windows(windows)
                
        except Exception as e:
            print(f"Pencere düzenleme hatası: {str(e)}")
            
    def _tile_windows(self, windows: List[gw.Window]):
        """Pencereleri döşe"""
        monitor = self.monitors[0]  # Ana monitörü kullan
        window_count = len(windows)
        
        if window_count == 0:
            return
            
        # Izgara boyutlarını hesapla
        cols = int(window_count ** 0.5)
        rows = (window_count + cols - 1) // cols
        
        width = monitor.width // cols
        height = monitor.height // rows
        
        for i, window in enumerate(windows):
            row = i // cols
            col = i % cols
            x = monitor.x + col * width
            y = monitor.y + row * height
            
            window.moveTo(x, y)
            window.resizeTo(width, height)
            
    def _cascade_windows(self, windows: List[gw.Window]):
        """Pencereleri basamakla"""
        monitor = self.monitors[0]
        offset = 30
        
        for i, window in enumerate(windows):
            x = monitor.x + i * offset
            y = monitor.y + i * offset
            window.moveTo(x, y)
            window.resizeTo(800, 600) 