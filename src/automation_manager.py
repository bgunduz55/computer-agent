import schedule
import time
import threading
import psutil
from datetime import datetime
from pathlib import Path
import shutil
import logging
from typing import Dict, List, Optional
from config_manager import ConfigManager
from language_manager import LanguageManager
from notification_manager import NotificationManager
import os
import subprocess

class AutomationManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager()
        self.notification_manager = NotificationManager()
        self.logger = logging.getLogger("AICodeEditor.Automation")
        
        self.automation_config = self.config_manager.get_config("automation")
        self.running = False
        self.thread = None
        
        # Zamanlanmış görevleri yükle
        self._setup_schedules()
        # Tetikleyicileri başlat
        self._setup_triggers()
        
        # Uygulama listesini hazırla
        self.installed_apps = self._scan_installed_apps()
        self.common_apps = {
            "chrome": {
                "exe": "chrome.exe",
                "install_url": "https://www.google.com/chrome/",
                "name": "Google Chrome"
            },
            "firefox": {
                "exe": "firefox.exe",
                "install_url": "https://www.mozilla.org/firefox/",
                "name": "Mozilla Firefox"
            },
            "brave": {
                "exe": "brave.exe",
                "install_url": "https://brave.com/download/",
                "name": "Brave Browser"
            },
            "edge": {
                "exe": "msedge.exe",
                "name": "Microsoft Edge"
            },
            "notepad": {
                "exe": "notepad.exe",
                "name": "Notepad"
            },
            "cursor": {
                "exe": "cursor.exe",
                "install_url": "https://cursor.sh/",
                "name": "Cursor Editor"
            },
            "vscode": {
                "exe": "code.exe",
                "install_url": "https://code.visualstudio.com/download",
                "name": "Visual Studio Code"
            },
            "terminal": {
                "exe": "wt.exe",
                "install_url": "https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701",
                "name": "Windows Terminal"
            },
            "vlc": {
                "exe": "vlc.exe",
                "install_url": "https://www.videolan.org/vlc/",
                "name": "VLC Media Player"
            },
            "winrar": {
                "exe": "winrar.exe",
                "install_url": "https://www.win-rar.com/download.html",
                "name": "WinRAR"
            }
        }
        
    def _setup_schedules(self):
        """Zamanlanmış görevleri ayarla"""
        schedules = self.automation_config.get("schedules", {})
        
        for task_name, task_config in schedules.items():
            if "time" in task_config:
                if "day" in task_config:
                    # Haftalık görev
                    getattr(schedule.every(), task_config["day"]).at(task_config["time"]).do(
                        self._run_task, task_name, task_config
                    )
                else:
                    # Günlük görev
                    schedule.every().day.at(task_config["time"]).do(
                        self._run_task, task_name, task_config
                    )
                    
    def _setup_triggers(self):
        """Tetikleyicileri ayarla"""
        self.triggers = self.automation_config.get("triggers", {})
        
    def _run_task(self, task_name: str, task_config: dict):
        """Görevi çalıştır"""
        try:
            self.logger.info(f"Görev başlatılıyor: {task_name}")
            
            if "action" in task_config:
                action = task_config["action"]
                if hasattr(self, f"_action_{action}"):
                    result = getattr(self, f"_action_{action}")(task_config.get("params", {}))
                    self.notification_manager.send_notification(
                        title=f"Görev Tamamlandı: {task_name}",
                        message=result
                    )
            elif "actions" in task_config:
                results = []
                for action in task_config["actions"]:
                    if hasattr(self, f"_action_{action}"):
                        result = getattr(self, f"_action_{action}")({})
                        results.append(result)
                self.notification_manager.send_notification(
                    title=f"Görev Grubu Tamamlandı: {task_name}",
                    message="\n".join(results)
                )
                        
        except Exception as e:
            error_msg = f"Görev çalıştırma hatası ({task_name}): {str(e)}"
            self.logger.error(error_msg)
            self.notification_manager.show_notification(
                title=self.language_manager.get_message("automation_error_title"),
                message=str(e),
                notification_type="error"
            )
            
            # Başarılı işlem bildirimi
            self.notification_manager.show_notification(
                title=self.language_manager.get_message("automation_success_title"),
                message=self.language_manager.get_message("task_completed"),
                notification_type="info"
            )
            
            # Uyarı bildirimi
            warning_message = self.language_manager.get_message("automation_warning_message")
            self.notification_manager.show_notification(
                title=self.language_manager.get_message("automation_warning_title"),
                message=warning_message,
                notification_type="warning"
            )
            
            # Kritik hata bildirimi
            critical_message = self.language_manager.get_message("automation_critical_message")
            self.notification_manager.show_notification(
                title=self.language_manager.get_message("automation_critical_title"),
                message=critical_message,
                notification_type="error"
            )
            
    def start(self):
        """Otomasyon sistemini başlat"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop)
            self.thread.daemon = True
            self.thread.start()
            self.logger.info("Otomasyon sistemi başlatıldı")
            
    def stop(self):
        """Otomasyon sistemini durdur"""
        self.running = False
        if self.thread:
            self.thread.join()
            self.logger.info("Otomasyon sistemi durduruldu")
            
    def _run_loop(self):
        """Ana çalışma döngüsü"""
        while self.running:
            try:
                # Zamanlanmış görevleri kontrol et
                schedule.run_pending()
                
                # Tetikleyicileri kontrol et
                self._check_triggers()
                
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Otomasyon döngüsü hatası: {str(e)}")
                
    def _check_triggers(self):
        """Tetikleyicileri kontrol et"""
        for trigger_name, trigger_config in self.triggers.items():
            try:
                condition = trigger_config["condition"]
                if self._evaluate_condition(condition):
                    action = trigger_config["action"]
                    if hasattr(self, f"_action_{action}"):
                        result = getattr(self, f"_action_{action}")({})
                        self.notification_manager.send_notification(
                            title=f"Tetikleyici Çalıştı: {trigger_name}",
                            message=result
                        )
            except Exception as e:
                self.logger.error(f"Tetikleyici hatası ({trigger_name}): {str(e)}")
                
    def _evaluate_condition(self, condition: str) -> bool:
        """Koşulu değerlendir"""
        try:
            if "battery_level" in condition:
                battery = psutil.sensors_battery()
                if battery:
                    return eval(condition.replace("battery_level", str(battery.percent)))
            elif "cpu_usage" in condition:
                cpu_percent = psutil.cpu_percent()
                return eval(condition.replace("cpu_usage", str(cpu_percent)))
            return False
        except:
            return False
            
    # Eylem metodları
    def _action_backup_project_files(self, params: dict):
        """Proje dosyalarını yedekle"""
        source = Path(params.get("source", "projects/"))
        dest = Path(params.get("destination", "backups/"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = dest / f"backup_{timestamp}"
        
        try:
            shutil.copytree(source, backup_dir)
            print(f"Yedekleme tamamlandı: {backup_dir}")
        except Exception as e:
            print(f"Yedekleme hatası: {str(e)}")
            
    def _action_clear_temp_files(self, params: dict):
        """Geçici dosyaları temizle"""
        temp_dir = Path(params.get("temp_dir", "temp/"))
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
            
    def _action_enable_power_save(self, params: dict):
        """Güç tasarrufu modunu etkinleştir"""
        # Platform'a özgü güç tasarrufu komutları
        pass
        
    def _action_notify_user(self, params: dict):
        """Kullanıcıyı bilgilendir"""
        # Bildirim gönderme işlemi
        pass

    def _scan_installed_apps(self) -> dict:
        """Sistemde yüklü uygulamaları tara"""
        installed_apps = {}
        try:
            # Windows için Program Files dizinlerini tara
            program_dirs = [
                os.environ.get("ProgramFiles", "C:/Program Files"),
                os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"),
                os.environ.get("LocalAppData", ""),
                os.path.join(os.environ.get("LocalAppData", ""), "Programs"),
                os.environ.get("AppData", "")
            ]

            for program_dir in program_dirs:
                if os.path.exists(program_dir):
                    for root, dirs, files in os.walk(program_dir):
                        for file in files:
                            if file.endswith('.exe'):
                                app_name = os.path.splitext(file)[0].lower()
                                installed_apps[app_name] = {
                                    "exe": file,
                                    "path": os.path.join(root, file),
                                    "name": app_name.title()
                                }

            self.logger.info(f"Bulunan uygulamalar: {list(installed_apps.keys())}")
            return installed_apps

        except Exception as e:
            self.logger.error(f"Uygulama tarama hatası: {str(e)}")
            return {}

    def open_application(self, app_name: str) -> bool:
        """Uygulamayı aç"""
        try:
            # Uygulama listesini yenile
            self.refresh_installed_apps()
            
            # Uygulama adını küçük harfe çevir
            app_name = app_name.lower()
            
            # Özel durumlar
            if app_name in ["cursor", "cursor editör", "cursor editor"]:
                import subprocess
                try:
                    subprocess.Popen(["cursor"])
                    return True
                except:
                    # Alternatif yol dene
                    try:
                        import os
                        cursor_path = os.path.expandvars("%LOCALAPPDATA%\\Programs\\Cursor\\Cursor.exe")
                        if os.path.exists(cursor_path):
                            subprocess.Popen([cursor_path])
                            return True
                    except:
                        pass
                return False
                
            # Uygulama adını bul
            if app_name in self.installed_apps:
                executable = self.installed_apps[app_name]
                try:
                    import subprocess
                    subprocess.Popen([executable])
                    return True
                except Exception as e:
                    self.logger.error(f"Uygulama açma hatası ({app_name}): {str(e)}")
                    return False
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Uygulama açma hatası: {str(e)}")
            return False

    def refresh_installed_apps(self):
        """Yüklü uygulama listesini yenile"""
        self.installed_apps = self._scan_installed_apps() 