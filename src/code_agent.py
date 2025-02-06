import ollama_python as ollama
from pathlib import Path
import sys
from colorama import init, Fore, Style
import json
from cursor_integration import CursorIntegration
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt
import pyautogui
import time
import win32gui  # Windows için
import win32con  # Windows için
import win32com.client  # Windows COM API'si için
import os
import subprocess
import webbrowser
import psutil
import keyboard  # Klavye kontrolü için
import screen_brightness_control as sbc  # Ekran parlaklığı kontrolü
import sounddevice as sd  # Ses kontrolü
import numpy as np
from datetime import datetime, timedelta
import winreg  # Windows kayıt defteri işlemleri için
import re
import cv2
import pytesseract
from PIL import ImageGrab, ImageDraw
import pygetwindow as gw
import pyttsx3  # TTS için
from screen_scraper import ScreenScraper
from src.system_controller import SystemController
from src.reminder_manager import ReminderManager
from src.context_reminder import ContextReminder
from src.code_todo_manager import CodeTodoManager
from src.task_manager import TaskBoard, TaskStatus, TaskPriority
from src.error_handler import ErrorHandler
import random
from src.language_manager import LanguageManager
from base_agent import BaseAgent
import logging
from typing import Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.config_manager import ConfigManager
from media_manager import MediaManager
from automation_manager import AutomationManager
from notification_manager import NotificationManager
from window_manager import WindowManager
from security_manager import SecurityManager
from performance_manager import PerformanceManager
from error_manager import ErrorManager
import shutil
import ctypes

# Colorama'yı başlat
init()

class CodeEditorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        # Model ayarlarını config'den al
        model_config = self.config_manager.get_model_config()
        self.model = self.config_manager.config["ai"]["default_model"]
        self.temperature = model_config.get("temperature", 0.7)
        self.max_tokens = model_config.get("max_tokens", 2048)
        self.system_prompt = model_config.get("system_prompt", "")
        self.context = []
        self.cursor = CursorIntegration()
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.show_welcome_message()
        self.language_manager = LanguageManager()
        self.logger = logging.getLogger('AICodeEditor.CodeAgent')
        self.common_apps = self._get_installed_apps()
        
        self.keyboard_shortcuts = {
            "kopyala": ["ctrl", "c"],
            "yapıştır": ["ctrl", "v"],
            "kes": ["ctrl", "x"],
            "geri al": ["ctrl", "z"],
            "ileri al": ["ctrl", "y"],
            "kaydet": ["ctrl", "s"],
            "tümünü seç": ["ctrl", "a"],
            "yeni dosya": ["ctrl", "n"],
            "bul": ["ctrl", "f"],
            "değiştir": ["ctrl", "h"],
        }
        
        self.media_keys = {
            "ses artır": "volume_up",
            "ses azalt": "volume_down",
            "sessiz": "volume_mute",
            "oynat": "play/pause_media",
            "durdur": "stop_media",
            "ileri": "next_track",
            "geri": "previous_track",
        }
        
        # OCR için Tesseract yolunu ayarla (Windows için)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # TTS motorunu başlat
        try:
            # Önce Windows SAPI5'i dene
            self.tts_engine = win32com.client.Dispatch("SAPI.SpVoice")
            # Türkçe ses varsa onu seç
            voices = self.tts_engine.GetVoices()
            for voice in voices:
                if "Turkish" in voice.GetDescription():
                    self.tts_engine.Voice = voice
                    break
        except:
            # Windows değilse pyttsx3 kullan
            self.tts_engine = pyttsx3.init()
            # Türkçe ses varsa onu seç
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if "turkish" in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            # Konuşma hızını ayarla
            self.tts_engine.setProperty('rate', 150)
        
        self.error_handler = ErrorHandler()
        self.language = "tr"  # Varsayılan dil Türkçe
        self.responses = {
            "tr": {
                "welcome": [
                    "Merhaba! Size nasıl yardımcı olabilirim?",
                    "Hoş geldiniz! Ne yapmak istersiniz?",
                    "Buyrun, sizi dinliyorum!"
                ],
                "error": "Bu işlemi yaparken bir hata oluştu: {error}\nHata detaylarını görmek ister misiniz?",
                "error_shown": "Hata detayları VS Code'da açıldı.",
                "error_hidden": "Hata detayları gizlendi.",
                "task_added": "✅ Yeni görev eklendi: {title} (ID: {id})",
                "task_updated": "✅ Görev durumu güncellendi: {title} → {status}",
                "todo_added": "✅ TODO notu eklendi: {message}",
                "reminder_added": "✅ Hatırlatıcı ayarlandı: {message} ({time})",
                # ... diğer mesajlar ...
            },
            "en": {
                # İngilizce mesajlar...
            }
        }
        
        # Uygulama listesini güncelle
        self.apps = self._get_installed_apps()
        self.logger.info(f"Bulunan uygulamalar: {self.apps}")
        
        # Komut kalıpları
        self.command_patterns = {
            'youtube_search': [
                r'youtube(?:\'da)?\s+(.*?)(?:dinle|izle|aç|arat|bul|ara)',
                r'(.*?)(?:dinle|izle|aç)\s+youtube(?:\'da)?',
            ],
            'youtube_video': [
                r'youtube(?:\'da)?\s+(.*?)(?:videosunu|şarkısını|müziğini)?\s+(?:aç|oynat|başlat|dinle)',
                r'(.*?)(?:videosunu|şarkısını|müziğini)?\s+(?:youtube(?:\'da)?\s+)?(?:aç|oynat|başlat|dinle)',
            ],
            'web_open': [
                r'(?:aç|git|ziyaret et)\s+((?:https?://)?(?:[\w-]+\.)+[\w-]+(?:/[^\s]*)?)',
                r'((?:https?://)?(?:[\w-]+\.)+[\w-]+(?:/[^\s]*)?)(?:\s+(?:aç|git|ziyaret et))',
            ],
            'close_app': [
                r'(.*?)(?:\s+)?(?:kapat|sonlandır|çık)',
                r'(?:kapat|sonlandır|çık)\s+(.*)',
            ]
        }
        
        self.driver = None
        self.default_browser = None
        
        # Alt sistemleri başlat
        self.media_manager = MediaManager()
        self.automation_manager = AutomationManager()
        self.notification_manager = NotificationManager()
        self.window_manager = WindowManager()
        self.security_manager = SecurityManager()
        self.performance_manager = PerformanceManager()
        self.error_manager = ErrorManager()
        
        # Otomasyon sistemini başlat
        self.automation_manager.start()
        
    def _get_installed_apps(self) -> Dict[str, str]:
        """Sistemde kurulu uygulamaları bul"""
        apps = {
            "chrome": "chrome.exe",
            "google chrome": "chrome.exe",
            "cursor": "cursor.exe",
            "cursor editör": "cursor.exe",
            "cursor editor": "cursor.exe",
            "vscode": "code.exe",
            "visual studio code": "code.exe",
            "notepad": "notepad.exe"
        }
        
        try:
            # Windows kayıt defterinden kurulu uygulamaları al
            paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        i = 0
                        while True:
                            try:
                                app_key = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, app_key) as app:
                                    try:
                                        path = winreg.QueryValue(app, None)
                                        if path and path.endswith('.exe'):
                                            name = os.path.splitext(os.path.basename(path))[0].lower()
                                            exe = os.path.basename(path)
                                            apps[name] = exe
                                    except:
                                        pass
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    continue

            self.logger.info(f"Bulunan uygulamalar: {list(apps.keys())}")
            return apps

        except Exception as e:
            self.logger.error(f"Uygulama listesi alınırken hata: {str(e)}")
            return apps
        
    def show_welcome_message(self):
        """Hoş geldin mesajını göster"""
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}🤖 AI Code Editor Agent'a Hoş Geldiniz!")
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.GREEN}Kullanılabilir Komutlar:")
        print(f"{Fore.WHITE}1. 'Hey Alimer' diyerek beni aktifleştirebilirsiniz")
        print(f"2. Kod geliştirme için: 'geliştir', 'ekle', 'yaz', 'oluştur'")
        print(f"3. Kod inceleme için: 'incele', 'kontrol et', 'review'")
        print(f"4. Çıkmak için: 'Hey Alimer dur' veya 'dur'")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
        
    async def get_response(self, prompt: str) -> str:
        try:
            # System prompt'u config'den al
            system_prompt = self.system_prompt
            
            messages = [
                {"role": "system", "content": system_prompt},
                *self.context,
                {"role": "user", "content": prompt}
            ]
            
            # Model parametrelerini config'den kullan
            response = await ollama.chat(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            content = response['message']['content']
            
            # Bağlamı güncelle
            self.context.append({"role": "user", "content": prompt})
            self.context.append({"role": "assistant", "content": content})
            if len(self.context) > 10:  # Son 10 mesajı tut
                self.context = self.context[-10:]
            
            return content
            
        except Exception as e:
            return f"❌ Hata oluştu: {str(e)}"
            
    async def edit_file(self, file_path: str, instruction: str):
        try:
            print(f"{Fore.CYAN}📂 Dosya okunuyor: {file_path}{Style.RESET_ALL}")
            content = Path(file_path).read_text()
            
            prompt = f"""
            Dosya içeriği:
            {content}
            
            Yapılacak değişiklik:
            {instruction}
            
            Lütfen güncellenmiş dosya içeriğini döndür.
            """
            
            updated_content = await self.get_response(prompt)
            
            # Değişiklikleri göster
            print(f"\n{Fore.YELLOW}📝 Önerilen değişiklikler:{Style.RESET_ALL}")
            print(updated_content)
            
            # Dosyayı güncelle
            Path(file_path).write_text(updated_content)
            return f"{Fore.GREEN}✅ Dosya başarıyla güncellendi.{Style.RESET_ALL}"
            
        except Exception as e:
            return f"{Fore.RED}❌ Dosya düzenlenirken hata oluştu: {str(e)}{Style.RESET_ALL}"
    
    def get_message(self, key: str, **kwargs) -> str:
        """Dil yöneticisinden mesaj al"""
        return self.language_manager.get_message(key, **kwargs)

    def show_error_dialog(self, message: str) -> bool:
        """Hata dialogu göster"""
        from PyQt6.QtWidgets import QMessageBox
        
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(self.language_manager.get_message("error_dialog_title"))
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        # Buton metinlerini çevir
        dialog.button(QMessageBox.StandardButton.Yes).setText(self.language_manager.get_message("yes"))
        dialog.button(QMessageBox.StandardButton.No).setText(self.language_manager.get_message("no"))
        
        return dialog.exec() == QMessageBox.StandardButton.Yes

    def process_command(self, command: str) -> str:
        """Komutu işle ve yanıt döndür"""
        try:
            # Performans ölçümünü başlat
            self.performance_manager.start_command_timing(command)
            
            # Güvenlik kontrolü
            if not self.security_manager.verify_command(command):
                return "Bu komut için yetkiniz yok."
            
            # Komut türünü belirle ve ilgili yöneticiye yönlendir
            command = command.lower().strip()
            
            # Web komutları
            if "google" in command or "web'de" in command or "internette" in command:
                search_term = command.replace("google'da", "").replace("google", "").replace("web'de", "").replace("internette", "").strip()
                url = f"https://www.google.com/search?q={search_term}"
                self._open_url(url)
                return f"✅ Google'da '{search_term}' araması yapılıyor..."
                
            # YouTube komutları
            elif "youtube" in command:
                if any(pattern in command for pattern in ["dinle", "izle", "aç", "oynat", "başlat"]):
                    search_term = command.replace("youtube'da", "").replace("youtube", "")
                    for word in ["dinle", "izle", "aç", "oynat", "başlat"]:
                        search_term = search_term.replace(word, "")
                    return self._handle_youtube_video(search_term.strip())
                else:
                    search_term = command.replace("youtube'da ara", "").replace("youtube ara", "").strip()
                    return self._handle_youtube_search(search_term)
                    
            # Uygulama komutları
            elif "aç" in command:
                for app_name in self.common_apps:
                    if app_name in command:
                        success = self.automation_manager.open_application(app_name)
                        if success:
                            time.sleep(1)  # Uygulamanın açılmasını bekle
                            return f"✅ {app_name} açılıyor..."
                        else:
                            return f"❌ {app_name} açılamadı."
                        
            # Pencere komutları
            elif any(word in command for word in ["pencere", "ekran", "uygulama"]):
                return self.handle_window_command(command)
                
            # Medya komutları
            elif any(word in command for word in ["ses", "parlaklık", "müzik", "video"]):
                return self.handle_media_command(command)
                
            # Bildirim komutları
            elif "bildirim" in command:
                return self.handle_notification_command(command)
                
            # Geliştirme komutları
            elif any(word in command for word in ["geliştir", "düzenle", "ekle", "yaz", "oluştur"]):
                return self.handle_development(command)
                
            # İnceleme komutları
            elif any(word in command for word in ["incele", "kontrol et", "review", "gözden geçir"]):
                return self.handle_code_review(command)
                
            # Görev yönetimi
            elif any(word in command for word in ["görev", "task", "todo"]):
                return self.handle_task_management(command)
                
            # Sistem komutları
            elif any(word in command for word in ["sistem", "bilgisayar", "pc"]):
                return self.handle_system_operations(command)
                
            # Yazı yazma komutları
            elif any(word in command for word in ["yaz", "yazdır", "metin gir"]):
                text = command.split("yaz", 1)[-1].strip()
                if not text:
                    text = command.split("yazdır", 1)[-1].strip()
                if not text:
                    text = command.split("metin gir", 1)[-1].strip()
                
                if text:
                    import pyautogui
                    import pygetwindow as gw
                    
                    # Aktif pencereyi al
                    active_window = gw.getActiveWindow()
                    if active_window:
                        # Pencereyi aktif et
                        active_window.activate()
                        time.sleep(0.5)  # Pencerenin aktif olmasını bekle
                        
                        # Metni yaz
                        pyautogui.write(text)
                        return f"✅ Metin yazıldı: {text}"
                    else:
                        return "❌ Aktif pencere bulunamadı."
                else:
                    return "❌ Yazılacak metin bulunamadı."
                
            # Bilinmeyen komut
            else:
                return "❌ Komut anlaşılamadı. Lütfen tekrar deneyin."
            
            # Performans ölçümünü bitir
            self.performance_manager.end_command_timing(command)
            
        except Exception as e:
            # Hatayı kaydet ve çözüm öner
            self.error_manager.log_error(str(e), "command_processing")
            solutions = self.error_manager.suggest_solutions(str(e))
            
            # Kullanıcıyı bilgilendir
            error_message = f"Hata oluştu: {str(e)}"
            if solutions:
                error_message += f"\nÖnerilen çözümler:\n" + "\n".join(
                    [s["message"] for s in solutions]
                )
            
            # Bildirimi göster
            self.notification_manager.show_notification(
                title=self.language_manager.get_message("command_error_title"),
                message=error_message,
                notification_type="error"
            )
            
            return error_message
            
    def handle_window_command(self, command: str) -> str:
        """Pencere komutlarını işle"""
        try:
            if "düzen" in command:
                layout_name = command.split("düzen")[-1].strip()
                return self.window_manager.apply_layout(layout_name)
            elif "döşe" in command:
                self.window_manager.arrange_windows("tile")
                return "Pencereler döşendi"
            # ... diğer pencere komutları
        except Exception as e:
            self.error_manager.log_error(str(e), "window_command")
            return f"Pencere kontrolü hatası: {str(e)}"
            
    def handle_media_command(self, command: str) -> str:
        """Medya komutlarını işle"""
        try:
            if "ses" in command:
                if "artır" in command:
                    return self.media_manager.control_volume("up")
                elif "azalt" in command:
                    return self.media_manager.control_volume("down")
            elif "parlaklık" in command:
                if "artır" in command:
                    return self.media_manager.control_brightness("up")
                elif "azalt" in command:
                    return self.media_manager.control_brightness("down")
            # ... diğer medya komutları
        except Exception as e:
            self.error_manager.log_error(str(e), "media_command")
            return f"Medya kontrolü hatası: {str(e)}"

    def handle_notification_command(self, command: str) -> str:
        """Bildirim komutlarını işle"""
        try:
            # Bildirim işlemleri burada yapılabilir
            return "Bildirim işlemleri burada yapılabilir"
        except Exception as e:
            self.error_manager.log_error(str(e), "notification_command")
            return f"Bildirim işlemleri hatası: {str(e)}"

    def _handle_youtube_video(self, search_term: str) -> str:
        """YouTube video açma işlemi"""
        try:
            url = f"https://www.youtube.com/results?search_query={search_term}"
            self._open_url(url)
            return f"✅ YouTube'da '{search_term}' araması yapılıyor..."
            
        except Exception as e:
            self.logger.error(f"YouTube video işleme hatası: {str(e)}")
            return f"❌ Video açılamadı: {str(e)}"

    def _handle_youtube_search(self, search_term: str) -> str:
        """YouTube'da arama yapma işlemi"""
        try:
            url = f"https://www.youtube.com/results?search_query={search_term}"
            self._open_url(url)
            time.sleep(2)  # Sayfanın yüklenmesini bekle
            
            # Selenium ile video kontrolü
            if self.driver:
                wait = WebDriverWait(self.driver, 10)
                videos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-video-renderer")))
                
                if videos:
                    # İlk videoyu tıkla
                    video_title = videos[0].find_element(By.CSS_SELECTOR, "#video-title")
                    video_title.click()
                    return f"✅ İlk video açılıyor: {video_title.text}"
                    
            return f"✅ YouTube'da '{search_term}' araması yapıldı"
            
        except Exception as e:
            self.logger.error(f"YouTube arama hatası: {str(e)}")
            return f"❌ Arama başarısız: {str(e)}"

    def _extract_url_from_command(self, cmd: str) -> Optional[str]:
        """Komuttan URL çıkar"""
        # URL kalıplarını kontrol et
        for pattern in [self.command_patterns['web_open'][0], self.command_patterns['web_open'][1]]:
            matches = re.findall(pattern, cmd)
            if matches:
                url = matches[0]
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
        
        # YouTube özel kontrolü
        if "youtube" in cmd.lower():
            # Video ID veya playlist ID kontrolü
            video_id = self._extract_youtube_id(cmd)
            if video_id:
                return f"https://www.youtube.com/watch?v={video_id}"
        
        return None

    def _extract_youtube_id(self, text: str) -> Optional[str]:
        """YouTube video/playlist ID çıkar"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/\?v=)([^&\n?]+)',
            r'(?:youtube\.com\/playlist\?list=)([^&\n?]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def _open_url(self, url: str):
        """URL'yi varsayılan tarayıcıda aç"""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            self.logger.error(f"URL açma hatası: {str(e)}")
            raise

    def _get_default_browser(self) -> str:
        """Varsayılan tarayıcıyı al"""
        try:
            if not self.default_browser:
                # Windows Registry'den varsayılan tarayıcıyı al
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                    r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                    browser = winreg.QueryValueEx(key, "ProgId")[0]
                    
                if "chrome" in browser.lower():
                    self.default_browser = "chrome"
                elif "firefox" in browser.lower():
                    self.default_browser = "firefox"
                elif "edge" in browser.lower():
                    self.default_browser = "edge"
                else:
                    self.default_browser = "default"
                    
            return self.default_browser
            
        except Exception as e:
            self.logger.error(f"Varsayılan tarayıcı belirleme hatası: {str(e)}")
            return "default"

    def _handle_close_app(self, app_name: str) -> str:
        """Uygulama kapatma işlemi"""
        try:
            app_name = app_name.lower().strip()
            
            # Onay mesajı
            confirm_msg = self.language_manager.get_message("confirm_close_app", app=app_name)
            self.confirmation_requested.emit(confirm_msg)
            
            if self.wait_for_confirmation() == "evet":
                if app_name in ["chrome", "google chrome"]:
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
                    return f"✅ {app_name} kapatıldı"
                elif app_name == "youtube":
                    if self.driver:
                        # Sadece YouTube sekmesini kapat
                        current_url = self.driver.current_url
                        if "youtube.com" in current_url:
                            self.driver.close()
                            return "✅ YouTube sekmesi kapatıldı"
                    return "❌ Açık YouTube sekmesi bulunamadı"
                else:
                    return f"❌ '{app_name}' uygulaması desteklenmiyor"
            else:
                return self.language_manager.get_message("operation_cancelled")

        except Exception as e:
            self.logger.error(f"Uygulama kapatma hatası: {str(e)}")
            return f"❌ Uygulama kapatılamadı: {str(e)}"

    def wait_for_confirmation(self) -> str:
        """Kullanıcıdan onay bekler"""
        try:
            # GUI'den yanıt gelene kadar bekle
            response = self.confirmation_response.get(timeout=10)
            return response
        except Exception:
            return "hayır"  # Timeout durumunda varsayılan olarak hayır
            
    def handle_file_operations(self, cmd: str) -> str:
        """Dosya işlemleri"""
        try:
            # Yetki kontrolü
            def check_permissions(path: str) -> bool:
                try:
                    if os.path.exists(path):
                        # Okuma yetkisi kontrolü
                        if not os.access(path, os.R_OK):
                            raise PermissionError(f"Okuma izni yok: {path}")
                        # Yazma yetkisi kontrolü
                        if not os.access(path, os.W_OK):
                            raise PermissionError(f"Yazma izni yok: {path}")
                    return True
                except Exception as e:
                    self.logger.error(f"Yetki kontrolü hatası: {str(e)}")
                    raise

            # Dosya/klasör oluşturma
            if "oluştur" in cmd:
                path = self._extract_path(cmd)
                check_permissions(os.path.dirname(path))
                if "klasör" in cmd:
                    os.makedirs(path, exist_ok=True)
                else:
                    Path(path).touch()
                return f"✅ {path} oluşturuldu"
                
            # Dosya/klasör silme
            elif "sil" in cmd:
                path = self._extract_path(cmd)
                check_permissions(path)
                
                # Kullanıcıdan onay al
                if os.path.isdir(path) and any(os.scandir(path)):  # Klasör dolu mu?
                    onay = self.show_error_dialog(f"'{path}' klasörü dolu. Tüm içeriğiyle birlikte silinecek. Onaylıyor musunuz?")
                    if not onay:
                        return "❌ İşlem iptal edildi"
                    shutil.rmtree(path)
                else:
                    if os.path.isdir(path):
                        os.rmdir(path)
                    else:
                        os.remove(path)
                return f"✅ {path} silindi"
                
            # Dosya/klasör taşıma
            elif "taşı" in cmd:
                source = self._extract_path(cmd, "kaynak")
                target = self._extract_path(cmd, "hedef")
                
                # Kaynak ve hedef yetki kontrolü
                check_permissions(source)
                check_permissions(os.path.dirname(target))
                
                # Hedef dizin yoksa oluştur
                os.makedirs(os.path.dirname(target), exist_ok=True)
                
                # Hedef zaten varsa onay al
                if os.path.exists(target):
                    onay = self.show_error_dialog(f"'{target}' zaten mevcut. Üzerine yazılsın mı?")
                    if not onay:
                        return "❌ İşlem iptal edildi"
                
                shutil.move(source, target)
                return f"✅ {source} -> {target} taşındı"
                
        except PermissionError as e:
            return f"❌ Yetki hatası: {str(e)}"
        except FileNotFoundError as e:
            return f"❌ Dosya bulunamadı: {str(e)}"
        except Exception as e:
            self.logger.error(f"Dosya işleminde hata: {str(e)}")
            return f"❌ Dosya işleminde hata: {str(e)}"
            
    def handle_web_operations(self, cmd: str) -> str:
        """Web işlemleri"""
        try:
            if "aç" in cmd or "git" in cmd:
                url = self._extract_url(cmd)
                webbrowser.open(url)
                return f"✅ {url} açıldı"
                
        except Exception as e:
            return f"❌ Web işleminde hata: {str(e)}"
            
    def handle_system_operations(self, cmd: str) -> str:
        """Sistem işlemleri"""
        try:
            # Kritik komut kontrolü
            def is_critical_command(cmd: str) -> bool:
                critical_keywords = ["kapat", "yeniden başlat", "format", "sil", "güncelle"]
                return any(keyword in cmd.lower() for keyword in critical_keywords)
            
            # Yetki kontrolü
            def check_admin_rights() -> bool:
                try:
                    return ctypes.windll.shell32.IsUserAnAdmin()
                except:
                    return False
            
            # Kritik komut için onay ve yetki kontrolü
            if is_critical_command(cmd):
                # Admin yetkisi kontrolü
                if not check_admin_rights():
                    return "❌ Bu işlem için yönetici hakları gerekiyor"
                
                # Kullanıcı onayı
                onay_mesaji = "Bu kritik bir sistem işlemidir. Onaylıyor musunuz?"
                if not self.show_error_dialog(onay_mesaji):
                    return "❌ İşlem iptal edildi"
            
            # Sistem komutlarını işle
            if "yeniden başlat" in cmd:
                if "iptal" in cmd:
                    os.system("shutdown /a")
                    return "✅ Yeniden başlatma iptal edildi"
                else:
                    # Açık uygulamaları kontrol et
                    running_apps = self._get_running_apps()
                    if running_apps:
                        onay = self.show_error_dialog(
                            f"Aşağıdaki uygulamalar açık:\n{running_apps}\n\n"
                            "Yeniden başlatmak istediğinize emin misiniz?"
                        )
                        if not onay:
                            return "❌ İşlem iptal edildi"
                    
                    os.system("shutdown /r /t 60")
                    return "✅ Bilgisayar 1 dakika içinde yeniden başlatılacak"
            
            elif "kapat" in cmd:
                if "iptal" in cmd:
                    os.system("shutdown /a")
                    return "✅ Kapatma iptal edildi"
                else:
                    # Açık uygulamaları kontrol et
                    running_apps = self._get_running_apps()
                    if running_apps:
                        onay = self.show_error_dialog(
                            f"Aşağıdaki uygulamalar açık:\n{running_apps}\n\n"
                            "Kapatmak istediğinize emin misiniz?"
                        )
                        if not onay:
                            return "❌ İşlem iptal edildi"
                    
                    os.system("shutdown /s /t 60")
                    return "✅ Bilgisayar 1 dakika içinde kapatılacak"
            
            elif "uyku" in cmd:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return "✅ Bilgisayar uyku moduna alınıyor"
            
            elif "hibernate" in cmd:
                os.system("shutdown /h")
                return "✅ Bilgisayar hazırda bekleme moduna alınıyor"
            
        except Exception as e:
            self.logger.error(f"Sistem işleminde hata: {str(e)}")
            return f"❌ Sistem işleminde hata: {str(e)}"
    
    def _get_running_apps(self) -> str:
        """Çalışan uygulamaları listele"""
        try:
            running_apps = []
            for proc in psutil.process_iter(['name', 'status']):
                try:
                    if proc.info['status'] == 'running' and proc.info['name'] not in ['svchost.exe', 'System', 'Registry']:
                        running_apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return "\n".join(sorted(set(running_apps)))
        except Exception as e:
            self.logger.error(f"Çalışan uygulamalar listelenirken hata: {str(e)}")
            return ""

    def handle_text_input(self, cmd: str) -> str:
        """Metin giriş işlemleri"""
        try:
            text_to_type = cmd
            # Komut kelimelerini temizle
            for keyword in ["yazı yaz", "metin yaz", "yaz bunu"]:
                text_to_type = text_to_type.replace(keyword, "")
            text_to_type = text_to_type.strip()
            
            # Aktif pencereye metin yaz
            self.type_text(text_to_type)
            return f"✅ Yazı yazıldı: {text_to_type}"
            
        except Exception as e:
            return f"❌ Metin girişinde hata: {str(e)}"
            
    def handle_input_operations(self, cmd: str) -> str:
        """Fare/Klavye işlemleri"""
        try:
            if "tıkla" in cmd:
                x, y = self._extract_coordinates(cmd)
                pyautogui.click(x, y)
                return f"✅ {x},{y} koordinatlarına tıklandı"
                
            elif "sağ tıkla" in cmd:
                x, y = self._extract_coordinates(cmd)
                pyautogui.rightClick(x, y)
                return "✅ Sağ tıklama yapıldı"
                
            elif "kaydır" in cmd:
                amount = self._extract_scroll_amount(cmd)
                pyautogui.scroll(amount)
                return f"✅ Sayfa {amount} birim kaydırıldı"
                
        except Exception as e:
            return f"❌ Fare/klavye işleminde hata: {str(e)}"
            
    def _extract_path(self, cmd: str, type_hint="") -> str:
        """Komuttan dosya/klasör yolunu çıkarır"""
        # Basit bir implementasyon - geliştirilebilir
        words = cmd.split()
        for i, word in enumerate(words):
            if "." in word or "\\" in word or "/" in word:
                return word
        return ""
        
    def _extract_url(self, cmd: str) -> str:
        """Komuttan URL'yi çıkarır"""
        words = cmd.split()
        for word in words:
            if word.startswith(("http://", "https://", "www.")):
                return word
            elif "." in word and " " not in word:
                return f"https://{word}"
        return ""
        
    def _extract_coordinates(self, cmd: str) -> tuple:
        """Komuttan koordinatları çıkarır"""
        # Örnek: "500,300 koordinatlarına tıkla"
        for word in cmd.split():
            if "," in word:
                try:
                    x, y = map(int, word.split(","))
                    return (x, y)
                except:
                    pass
        return pyautogui.position()  # Mevcut fare pozisyonu
        
    def _extract_scroll_amount(self, cmd: str) -> int:
        """Komuttan kaydırma miktarını çıkarır"""
        # Yukarı/aşağı yönünü ve miktarı belirle
        amount = 3  # Varsayılan miktar
        if "yukarı" in cmd:
            amount *= 1
        elif "aşağı" in cmd:
            amount *= -1
            
        # Sayısal değer varsa onu kullan
        words = cmd.split()
        for word in words:
            try:
                num = int(word)
                amount = num if "yukarı" in cmd else -num
                break
            except:
                continue
                
        return amount 

    def handle_keyboard_shortcut(self, cmd: str) -> str:
        """Klavye kısayollarını yönetir"""
        try:
            for shortcut_name, keys in self.keyboard_shortcuts.items():
                if shortcut_name in cmd:
                    keyboard.press_and_release('+'.join(keys))
                    return f"✅ '{shortcut_name}' kısayolu uygulandı"
            return "❌ Kısayol bulunamadı"
        except Exception as e:
            return f"❌ Klavye kısayolu hatası: {str(e)}"

    def handle_media_control(self, cmd: str) -> str:
        """Medya kontrollerini yönetir"""
        try:
            for action, key in self.media_keys.items():
                if action in cmd:
                    keyboard.press_and_release(key)
                    return f"✅ Medya kontrolü: {action}"
            return "❌ Medya kontrolü bulunamadı"
        except Exception as e:
            return f"❌ Medya kontrolü hatası: {str(e)}"

    def handle_screen_control(self, cmd: str) -> str:
        """Ekran parlaklığını kontrol eder"""
        try:
            current = sbc.get_brightness()[0]
            if "artır" in cmd or "yükselt" in cmd:
                new_brightness = min(current + 10, 100)
                sbc.set_brightness(new_brightness)
                return f"✅ Parlaklık {new_brightness}% yapıldı"
            elif "azalt" in cmd or "düşür" in cmd:
                new_brightness = max(current - 10, 0)
                sbc.set_brightness(new_brightness)
                return f"✅ Parlaklık {new_brightness}% yapıldı"
            elif "ayarla" in cmd:
                # Sayıyı bul
                numbers = re.findall(r'\d+', cmd)
                if numbers:
                    brightness = min(max(int(numbers[0]), 0), 100)
                    sbc.set_brightness(brightness)
                    return f"✅ Parlaklık {brightness}% yapıldı"
            return "❌ Parlaklık komutu anlaşılamadı"
        except Exception as e:
            return f"❌ Ekran kontrolü hatası: {str(e)}"

    def handle_reminder(self, cmd: str) -> str:
        """Hatırlatıcı ve zamanlayıcı işlemlerini yönetir"""
        try:
            # Zamanı çıkar (örn: "5 dakika sonra", "2 saat sonra")
            time_match = re.search(r'(\d+)\s*(dakika|saat|saniye)', cmd)
            if time_match:
                amount = int(time_match.group(1))
                unit = time_match.group(2)
                
                # Hatırlatma mesajını çıkar
                message = cmd.split("hatırlat")[-1].strip()
                if not message:
                    message = "⏰ Hatırlatıcı!"

                # Zamanı hesapla
                now = datetime.now()
                if unit == "dakika":
                    remind_time = now + timedelta(minutes=amount)
                elif unit == "saat":
                    remind_time = now + timedelta(hours=amount)
                else:
                    remind_time = now + timedelta(seconds=amount)

                # Windows görev zamanlayıcıya ekle
                self._create_scheduled_task(message, remind_time)
                
                return f"✅ Hatırlatıcı ayarlandı: {message} ({remind_time.strftime('%H:%M')})"
            return "❌ Hatırlatıcı zamanı anlaşılamadı"
        except Exception as e:
            return f"❌ Hatırlatıcı hatası: {str(e)}"

    def _create_scheduled_task(self, message: str, remind_time: datetime):
        # Bu metodun içeriği, Windows görev zamanlayıcısına bir görev eklemek için kullanılabilir.
        # Bu işlem için win32com.client kullanılabilir.
        # Bu örnekte, win32com.client kullanımı gösterilmektedir.
        # Daha karmaşık bir işlem için, örneğin, bir veritabanına görev eklemek veya bir API'ye istek göndermek gerekebilir.
        pass 

    def handle_text_interaction(self, cmd: str) -> str:
        """Ekrandaki metne göre etkileşim sağlar"""
        try:
            # Ekran görüntüsü al
            screen = np.array(ImageGrab.grab())
            gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
            
            # OCR ile metinleri tanı
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            # Aranan metni bul
            search_text = self._extract_target_text(cmd)
            if not search_text:
                return "❌ Aranacak metin bulunamadı"
                
            # Bulunan tüm eşleşmeleri işaretle
            matches = []
            for i, text in enumerate(data['text']):
                if search_text.lower() in text.lower():
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    matches.append((x + w//2, y + h//2, text))
            
            if not matches:
                return f"❌ '{search_text}' metni ekranda bulunamadı"
                
            # Her eşleşme için onay al
            for x, y, text in matches:
                # Mouse'u pozisyona götür
                current_x, current_y = pyautogui.position()  # Mevcut pozisyonu kaydet
                pyautogui.moveTo(x, y, duration=0.5)  # Yavaşça hareket et
                
                # Görsel geri bildirim (isteğe bağlı highlight efekti)
                self._highlight_area(x-5, y-5, 10, 10)
                
                # Sesli onay iste
                print(f"🤔 '{text}' metnine mi tıklamak istiyorsunuz? (evet/hayır)")
                
                # GUI üzerinden onay mesajı göster
                self.confirmation_requested.emit(f"'{text}' metnine tıklamak istediğinizden emin misiniz?")
                
                # Onay bekle
                response = self.wait_for_confirmation()
                
                if response.lower() in ['evet', 'e', 'yes', 'y']:
                    pyautogui.click(x, y)
                    return f"✅ '{text}' metnine tıklandı"
                else:
                    # Mouse'u orijinal pozisyona geri götür
                    pyautogui.moveTo(current_x, current_y, duration=0.3)
            
            return "❌ İşlem iptal edildi"
            
        except Exception as e:
            return f"❌ Metin etkileşimi hatası: {str(e)}"
            
    def _highlight_area(self, x, y, w, h, duration=0.5):
        """Ekranda bir alanı geçici olarak vurgula"""
        try:
            # Ekran görüntüsünü al
            screen = ImageGrab.grab()
            draw = ImageDraw.Draw(screen)
            
            # Dikdörtgen çiz
            draw.rectangle([x, y, x+w, y+h], outline='red', width=2)
            
            # Vurguyu göster
            screen.show()
            time.sleep(duration)
            
        except Exception:
            pass  # Vurgulama başarısız olursa sessizce devam et

    def handle_tab_interaction(self, cmd: str) -> str:
        """Tab ve pencere etkileşimlerini yönetir"""
        try:
            # Pencere başlığından hedefi bul
            target = self._extract_target_text(cmd)
            if not target:
                return "❌ Hedef pencere/sekme belirtilmedi"
                
            # Tüm pencereleri listele
            windows = gw.getAllWindows()
            
            # Hedef pencereyi bul
            for window in windows:
                if target.lower() in window.title.lower():
                    # Pencereyi aktif yap
                    window.activate()
                    
                    # Tab değiştirme komutu varsa
                    if "sekme" in cmd or "tab" in cmd:
                        pyautogui.hotkey('ctrl', 'tab')
                        
                    return f"✅ '{target}' penceresine geçildi"
                    
            return f"❌ '{target}' penceresi bulunamadı"
            
        except Exception as e:
            return f"❌ Pencere etkileşimi hatası: {str(e)}"
            
    def _extract_target_text(self, cmd: str) -> str:
        """Komuttan hedef metni çıkarır"""
        # Tırnak içindeki metni ara
        quoted = re.findall(r'"([^"]*)"', cmd)
        if quoted:
            return quoted[0]
            
        # Özel kelimeleri temizle
        words = cmd.replace("tıkla", "").replace("bas", "").replace("seç", "")
        words = words.replace("yazı", "").replace("metin", "").replace("buton", "")
        words = words.replace("tab", "").replace("sekme", "").replace("pencere", "")
        
        # Son kelimeyi al
        words = words.strip().split()
        if words:
            return words[-1]
            
        return ""

    def speak(self, text: str):
        """Metni seslendir"""
        try:
            # Emoji ve özel karakterleri temizle
            text = re.sub(r'[^\w\s.,?!]', '', text)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Konuşma hatası: {str(e)}")
            
    def _clean_text_for_speech(self, text: str) -> str:
        """Metni seslendirme için temizle"""
        # Emoji ve özel karakterleri temizle
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        text = emoji_pattern.sub(r'', text)
        
        # Özel karakterleri düzelt
        replacements = {
            "✅": "tamam",
            "❌": "hata",
            "→": "ok",
            "•": "",
            "|": "",
            "*": "",
            "#": "",
            "`": "",
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text

    def handle_screen_scraping(self, cmd: str) -> str:
        """Ekran üzerinden veri çekme işlemlerini yönet"""
        try:
            if not hasattr(self, 'scraper'):
                self.scraper = ScreenScraper()
            
            if "seç" in cmd.lower() or "alan" in cmd.lower():
                self.speak("Lütfen veri çekmek istediğiniz alanı fare ile seçin")
                screenshot = self.scraper.capture_area()
                self.speak("Alan seçildi. Ne yapmak istersiniz?")
                return "✅ Alan seçildi. 'metin çıkar', 'tablo çıkar' veya 'kaydet' komutlarını kullanabilirsiniz"
            
            elif "metin" in cmd.lower() or "yazı" in cmd.lower():
                text = self.scraper.extract_text()
                self.current_data = {"text": text}
                return f"✅ Çıkarılan metin:\n{text}"
            
            elif "tablo" in cmd.lower():
                tables = self.scraper.extract_tables()
                self.current_data = tables.to_dict('records')
                return f"✅ {len(self.current_data)} satır veri çıkarıldı"
            
            elif "kaydet" in cmd.lower():
                format = "json"  # varsayılan format
                if "xml" in cmd.lower():
                    format = "xml"
                elif "txt" in cmd.lower():
                    format = "txt"
                
                return self.scraper.save_data(self.current_data, format)
            
            return "❌ Anlaşılamayan scraping komutu"
        
        except Exception as e:
            return f"❌ Veri çekme hatası: {str(e)}"

    def handle_system_control(self, cmd: str) -> str:
        """Sistem kontrol komutlarını işle"""
        try:
            if not hasattr(self, 'system_controller'):
                self.system_controller = SystemController()
            
            if "parlaklık" in cmd:
                if "artır" in cmd:
                    return self.system_controller.control_brightness(increase=True)
                elif "azalt" in cmd:
                    return self.system_controller.control_brightness(decrease=True)
                
            elif "ses" in cmd:
                if "kapat" in cmd:
                    return self.system_controller.control_volume(mute=True)
                elif "aç" in cmd:
                    return self.system_controller.control_volume(unmute=True)
                
            elif "sistem bilgisi" in cmd:
                info = self.system_controller.get_system_info()
                return "\n".join([f"{k}: {v}" for k, v in info.items()])
            
            elif "uyku" in cmd:
                return self.system_controller.power_management("sleep")
            
            return "❌ Anlaşılamayan sistem komutu"
        
        except Exception as e:
            return f"❌ Sistem kontrolü hatası: {str(e)}"
        
    def handle_reminders(self, cmd: str) -> str:
        """Hatırlatıcı komutlarını işle"""
        try:
            if not hasattr(self, 'reminder_manager'):
                self.reminder_manager = ReminderManager()
            
            if "hatırlat" in cmd:
                # Basit NLP ile zamanı ve metni ayır
                text = re.search(r"hatırlat\s+(.+?)\s+(?:saat|gün|dakika)", cmd)
                when = re.search(r"(\d+)\s+(saat|gün|dakika)", cmd)
                
                if text and when:
                    text = text.group(1)
                    amount = int(when.group(1))
                    unit = when.group(2)
                    
                    now = datetime.now()
                    if unit == "saat":
                        when = now + timedelta(hours=amount)
                    elif unit == "gün":
                        when = now + timedelta(days=amount)
                    else:
                        when = now + timedelta(minutes=amount)
                    
                    return self.reminder_manager.add_reminder(text, when.isoformat())
                
            return "❌ Anlaşılamayan hatırlatıcı komutu"
        
        except Exception as e:
            return f"❌ Hatırlatıcı hatası: {str(e)}"

    def handle_context_reminder(self, cmd: str) -> str:
        """Bağlamsal hatırlatıcıları yönet"""
        try:
            if not hasattr(self, 'context_reminder'):
                self.context_reminder = ContextReminder()
            
            # Hatırlatıcı ekleme
            if "daha sonra" in cmd or "hatırlat" in cmd:
                # Bağlamı ve hatırlatıcı metnini ayır
                context_match = re.search(r"(?:yaparken|ederken|için)\s+(.+?)\s+(?:hatırlat|daha sonra)", cmd)
                text = cmd.split("hatırlat")[-1].strip() if "hatırlat" in cmd else cmd.split("daha sonra")[-1].strip()
                
                context = context_match.group(1) if context_match else None
                return self.context_reminder.add_reminder(text, context)
            
            # Tüm hatırlatıcıları listele
            elif any(keyword in cmd for keyword in ["hatırlatıcıları göster", "neler vardı", "yapılacaklar"]):
                return self.context_reminder.get_all_reminders()
            
            # Bağlam değiştiğinde kontrol et
            elif "yapıyorum" in cmd or "başlıyorum" in cmd:
                context = cmd.split("yapıyorum")[0].strip() if "yapıyorum" in cmd else cmd.split("başlıyorum")[0].strip()
                reminders = self.context_reminder.set_current_context(context)
                if reminders:
                    return reminders
                
            return None
        
        except Exception as e:
            return f"❌ Hatırlatıcı hatası: {str(e)}"

    def handle_code_todo(self, cmd: str) -> str:
        """Kod TODO notlarını yönet"""
        try:
            if not hasattr(self, 'todo_manager'):
                self.todo_manager = CodeTodoManager()
            
            # Dosya adını ve mesajı ayıkla
            file_match = re.search(r'(?:dosyasına|dosyaya|burada)\s+(.+?)\s+(?:için|diye)', cmd)
            message = cmd.split("not ekle")[-1].strip() if "not ekle" in cmd else None
            
            if file_match and message:
                file_path = file_match.group(1)
                # Eğer dosya uzantısı belirtilmemişse .py ekle
                if not Path(file_path).suffix:
                    file_path += '.py'
                
                return self.todo_manager.add_todo(file_path, message)
            
            # TODO listesini göster
            elif "todo" in cmd.lower() and "göster" in cmd:
                todos = self.todo_manager.get_todos(self.current_file)
                if todos:
                    return "📝 TODO Listesi:\n" + "\n".join(
                        f"- {todo['text']} (Satır: {todo['line']})" 
                        for todo in todos
                    )
                return "Aktif TODO notu bulunmuyor."
            
            return None
        
        except Exception as e:
            return f"❌ TODO işlemi hatası: {str(e)}"

    def handle_task_management(self, cmd: str) -> str:
        """Görev yönetimi komutlarını işle"""
        try:
            if not hasattr(self, 'task_board'):
                self.task_board = TaskBoard()
            
            # Yeni görev ekleme
            if "yeni görev" in cmd or "task ekle" in cmd:
                title = re.search(r"(?:görev|task)\s+(.+?)(?:\s+öncelik|$)", cmd)
                priority_match = re.search(r"öncelik\s+(yüksek|orta|düşük)", cmd, re.IGNORECASE)
                
                if title:
                    priority = "HIGH" if priority_match and "yüksek" in priority_match.group(1).lower() else \
                              "LOW" if priority_match and "düşük" in priority_match.group(1).lower() else "MEDIUM"
                              
                    task = self.task_board.add_task(title.group(1), priority=priority)
                    return f"✅ Yeni görev eklendi: {task.title} (ID: {task.id})"
                
            # Görev durumu güncelleme
            elif any(status in cmd.lower() for status in ["başla", "tamamla", "iptal et"]):
                task_id = re.search(r"görev\s+(\d+)", cmd)
                if task_id:
                    status = TaskStatus.IN_PROGRESS if "başla" in cmd else \
                             TaskStatus.COMPLETED if "tamamla" in cmd else \
                             TaskStatus.CANCELED if "iptal" in cmd else None
                             
                    if status:
                        task = self.task_board.update_task_status(task_id.group(1), status)
                        if task:
                            return f"✅ Görev durumu güncellendi: {task.title} → {status.value}"
                        
            # Görev tahtasını göster
            elif "görevleri göster" in cmd or "task board" in cmd:
                board = self.task_board.get_board_view()
                output = ["📋 Görev Tahtası:"]
                
                for status, tasks in board.items():
                    if tasks:
                        output.append(f"\n{status}:")
                        for task in tasks:
                            priority_emoji = "🔴" if task.priority == TaskPriority.HIGH else \
                                          "🟡" if task.priority == TaskPriority.MEDIUM else "🟢"
                            output.append(f"  {priority_emoji} [{task.id}] {task.title}")
                            
                return "\n".join(output)
                
            # Görev detayları
            elif "görev detay" in cmd:
                task_id = re.search(r"görev\s+(\d+)", cmd)
                if task_id:
                    details = self.task_board.get_task_details(task_id.group(1))
                    if details:
                        output = [
                            f"📝 Görev Detayları: {details['title']}",
                            f"Durum: {details['status']}",
                            f"Öncelik: {details['priority']}",
                            f"Oluşturulma: {details['created_at']}"
                        ]
                        
                        if details['notes']:
                            output.append("\nNotlar:")
                            output.extend(f"- {note['text']}" for note in details['notes'])
                            
                        if details['todos']:
                            output.append("\nİlgili TODO'lar:")
                            output.extend(f"- {todo['text']} ({todo['file']})" 
                                        for todo in details['todos'])
                                        
                        return "\n".join(output)
                        
            return "❌ Görev komutu anlaşılamadı"
            
        except Exception as e:
            return f"❌ Görev yönetimi hatası: {str(e)}"

    def handle_development(self, cmd: str) -> str:
        """Kod geliştirme işlemleri"""
        try:
            # Geliştirme komutlarını işle
            if "yeni dosya" in cmd or "oluştur" in cmd:
                file_match = re.search(r'(?:dosya|file)\s+(.+?)(?:\s+|$)', cmd)
                if file_match:
                    file_path = file_match.group(1)
                    if not Path(file_path).suffix:
                        file_path += '.py'
                    Path(file_path).touch()
                    return f"✅ Yeni dosya oluşturuldu: {file_path}"
                    
            elif "geliştir" in cmd or "düzenle" in cmd:
                # Mevcut dosyayı düzenle
                if hasattr(self, 'current_file'):
                    return self.edit_file(self.current_file, cmd)
                else:
                    return "❌ Lütfen önce bir dosya seçin"
                    
            return self.language_manager.get_message("command_not_understood")
            
        except Exception as e:
            error_data = self.error_handler.log_error(
                error=e,
                command=cmd,
                context="Development"
            )
            return self.language_manager.get_message("failure", reason=str(e))

    def handle_code_review(self, cmd: str) -> str:
        """Kod inceleme işlemleri"""
        try:
            # Kod inceleme komutlarını işle
            if "incele" in cmd or "review" in cmd:
                if hasattr(self, 'current_file'):
                    content = Path(self.current_file).read_text()
                    prompt = f"""
                    Lütfen bu kodu incele:
                    {content}
                    
                    Şu kriterlere göre değerlendir:
                    1. Kod kalitesi
                    2. Olası hatalar
                    3. İyileştirme önerileri
                    """
                    return self.get_response(prompt)
                else:
                    return "❌ Lütfen önce bir dosya seçin"
                    
            elif "kontrol et" in cmd:
                # Belirli bir dosyayı kontrol et
                file_match = re.search(r'(?:dosya|file)\s+(.+?)(?:\s+|$)', cmd)
                if file_match:
                    file_path = file_match.group(1)
                    if Path(file_path).exists():
                        content = Path(file_path).read_text()
                        return self.get_response(f"Bu dosyayı kontrol et:\n{content}")
                    else:
                        return f"❌ Dosya bulunamadı: {file_path}"
                        
            return self.language_manager.get_message("command_not_understood")
            
        except Exception as e:
            error_data = self.error_handler.log_error(
                error=e,
                command=cmd,
                context="Code Review"
            )
            return self.language_manager.get_message("failure", reason=str(e))

    def handle_error(self, error: Exception, command: str = "", context: str = ""):
        """Hata yönetimi"""
        try:
            # Hata analizi yap
            error_data, error_summary, solutions = self.error_handler.handle_error_with_analysis(error, command, context)
            
            # Kullanıcıya bilgi ver
            message = f"❌ Bir hata oluştu: {str(error)}\n\n"
            
            # Hata özetini ekle
            if error_summary:
                message += "📊 Hata Özeti:\n"
                message += f"- Toplam Hata: {error_summary['total_errors']}\n"
                message += f"- Ses Hataları: {error_summary['speech_errors']}\n"
                message += f"- Bağlantı Hataları: {error_summary['connection_errors']}\n"
                message += f"- Komut Hataları: {error_summary['command_errors']}\n\n"
            
            # Çözüm önerilerini ekle
            if solutions:
                message += "💡 Çözüm Önerileri:\n"
                for solution in solutions:
                    message += f"\n{solution['message']}:\n"
                    for suggestion in solution['suggestions']:
                        message += f"- {suggestion}\n"
                    
            self.speak(message)
            return message
            
        except Exception as e:
            self.logger.error(f"Hata yönetimi sırasında hata: {str(e)}")
            return f"❌ Kritik hata oluştu: {str(e)}"

    def __del__(self):
        """Sınıf silinirken tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()