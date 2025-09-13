"""
JARVIS Voice Commands Handler
Sesli komut işleme ve yönetim sistemi
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import asyncio
import logging
from typing import Dict, List, Optional, Callable
import re
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class VoiceCommandHandler:
    """Sesli komut işleyici"""
    
    def __init__(self, jarvis_core=None):
        self.jarvis_core = jarvis_core
        self.commands = {}
        self.is_listening = False
        self.setup_commands()
        
    def setup_commands(self):
        """Komutları tanımla"""
        self.commands = {
            # Temel komutlar
            "hey jarvis": self._wake_up,
            "what time is it": self._get_time,
            "what's the time": self._get_time,
            "hello": self._greet,
            "hi": self._greet,
            
            # Sistem komutları
            "show running applications": self._show_apps,
            "list applications": self._show_apps,
            "close chrome": self._close_app,
            "close firefox": self._close_app,
            "close edge": self._close_app,
            "increase volume": self._increase_volume,
            "decrease volume": self._decrease_volume,
            "mute": self._mute_volume,
            "unmute": self._unmute_volume,
            "set brightness": self._set_brightness,
            
            # Terminal komutları
            "run git status": self._run_git_status,
            "run git log": self._run_git_log,
            "list files": self._list_files,
            "show directory": self._list_files,
            "install package": self._install_package,
            "update packages": self._update_packages,
            
            # Web komutları
            "open google": self._open_google,
            "open youtube": self._open_youtube,
            "open github": self._open_github,
            "search for": self._search_web,
            "close current tab": self._close_tab,
            "open new tab": self._open_new_tab,
            
            # Plugin komutları
            "what's the weather": self._get_weather,
            "show weather": self._get_weather,
            "show my calendar": self._show_calendar,
            "check my emails": self._check_emails,
            "show system status": self._show_system_status,
            "show system info": self._show_system_info,
            
            # Yardım komutları
            "help": self._show_help,
            "what can you do": self._show_help,
            "show commands": self._show_commands,
        }
    
    async def process_command(self, text: str) -> str:
        """Komutu işle"""
        try:
            # Metni temizle ve küçük harfe çevir
            clean_text = re.sub(r'[^\w\s]', '', text.lower().strip())
            
            # En iyi eşleşmeyi bul
            best_match = None
            best_score = 0
            
            for command, handler in self.commands.items():
                score = self._calculate_similarity(clean_text, command)
                if score > best_score and score > 0.6:  # %60 benzerlik eşiği
                    best_score = score
                    best_match = command
            
            if best_match:
                logger.info(f"Executing command: {best_match}")
                result = await self.commands[best_match](clean_text)
                return result
            else:
                # AI'ye yönlendir
                return await self._handle_ai_query(text)
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"Sorry, I couldn't process that command: {e}"
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """İki metin arasındaki benzerliği hesapla"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def _wake_up(self, text: str) -> str:
        """Uyanma komutu"""
        return "Hello! I'm JARVIS, your computer assistant. How can I help you today?"
    
    async def _get_time(self, text: str) -> str:
        """Saat bilgisi"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        return f"The current time is {current_time} on {current_date}"
    
    async def _greet(self, text: str) -> str:
        """Selamlama"""
        return "Hello! How can I assist you today?"
    
    async def _show_apps(self, text: str) -> str:
        """Çalışan uygulamaları göster"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'application_manager'):
                apps = await self.jarvis_core.application_manager.get_running_applications()
                if apps:
                    app_list = "\n".join([f"- {app['name']} (PID: {app['pid']})" for app in apps[:10]])
                    return f"Running applications:\n{app_list}"
                else:
                    return "No running applications found"
            else:
                return "Application manager not available"
        except Exception as e:
            return f"Could not get running applications: {e}"
    
    async def _close_app(self, text: str) -> str:
        """Uygulama kapat"""
        try:
            app_name = text.split()[-1]  # Son kelimeyi uygulama adı olarak al
            if self.jarvis_core and hasattr(self.jarvis_core, 'application_manager'):
                success = await self.jarvis_core.application_manager.close_application(app_name)
                if success:
                    return f"Successfully closed {app_name}"
                else:
                    return f"Could not close {app_name}"
            else:
                return "Application manager not available"
        except Exception as e:
            return f"Error closing application: {e}"
    
    async def _increase_volume(self, text: str) -> str:
        """Sesi artır"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'platform'):
                await self.jarvis_core.platform.increase_volume()
                return "Volume increased"
            else:
                return "Volume control not available"
        except Exception as e:
            return f"Error increasing volume: {e}"
    
    async def _decrease_volume(self, text: str) -> str:
        """Sesi azalt"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'platform'):
                await self.jarvis_core.platform.decrease_volume()
                return "Volume decreased"
            else:
                return "Volume control not available"
        except Exception as e:
            return f"Error decreasing volume: {e}"
    
    async def _mute_volume(self, text: str) -> str:
        """Sesi kapat"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'platform'):
                await self.jarvis_core.platform.set_volume(0)
                return "Volume muted"
            else:
                return "Volume control not available"
        except Exception as e:
            return f"Error muting volume: {e}"
    
    async def _unmute_volume(self, text: str) -> str:
        """Sesi aç"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'platform'):
                await self.jarvis_core.platform.set_volume(50)
                return "Volume unmuted"
            else:
                return "Volume control not available"
        except Exception as e:
            return f"Error unmuting volume: {e}"
    
    async def _set_brightness(self, text: str) -> str:
        """Parlaklığı ayarla"""
        try:
            # Metinden sayıyı çıkar
            numbers = re.findall(r'\d+', text)
            if numbers:
                brightness = int(numbers[0])
                if self.jarvis_core and hasattr(self.jarvis_core, 'platform'):
                    await self.jarvis_core.platform.set_brightness(brightness)
                    return f"Brightness set to {brightness}%"
                else:
                    return "Brightness control not available"
            else:
                return "Please specify brightness percentage (0-100)"
        except Exception as e:
            return f"Error setting brightness: {e}"
    
    async def _run_git_status(self, text: str) -> str:
        """Git status çalıştır"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'terminal_manager'):
                result = await self.jarvis_core.terminal_manager.execute_command("git status")
                return f"Git status:\n{result['output']}"
            else:
                return "Terminal manager not available"
        except Exception as e:
            return f"Error running git status: {e}"
    
    async def _run_git_log(self, text: str) -> str:
        """Git log çalıştır"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'terminal_manager'):
                result = await self.jarvis_core.terminal_manager.execute_command("git log --oneline -5")
                return f"Recent git commits:\n{result['output']}"
            else:
                return "Terminal manager not available"
        except Exception as e:
            return f"Error running git log: {e}"
    
    async def _list_files(self, text: str) -> str:
        """Dosyaları listele"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'terminal_manager'):
                result = await self.jarvis_core.terminal_manager.execute_command("dir" if "windows" in text.lower() else "ls -la")
                return f"Directory contents:\n{result['output']}"
            else:
                return "Terminal manager not available"
        except Exception as e:
            return f"Error listing files: {e}"
    
    async def _install_package(self, text: str) -> str:
        """Paket yükle"""
        try:
            # Metinden paket adını çıkar
            words = text.split()
            package_name = None
            for i, word in enumerate(words):
                if word in ["install", "package"] and i + 1 < len(words):
                    package_name = words[i + 1]
                    break
            
            if package_name:
                if self.jarvis_core and hasattr(self.jarvis_core, 'package_manager'):
                    result = await self.jarvis_core.package_manager.install_package(package_name)
                    return f"Installing {package_name}... {result}"
                else:
                    return "Package manager not available"
            else:
                return "Please specify package name"
        except Exception as e:
            return f"Error installing package: {e}"
    
    async def _update_packages(self, text: str) -> str:
        """Paketleri güncelle"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'package_manager'):
                result = await self.jarvis_core.package_manager.update_packages()
                return f"Updating packages... {result}"
            else:
                return "Package manager not available"
        except Exception as e:
            return f"Error updating packages: {e}"
    
    async def _open_google(self, text: str) -> str:
        """Google'ı aç"""
        try:
            import webbrowser
            webbrowser.open("https://www.google.com")
            return "Opening Google..."
        except Exception as e:
            return f"Error opening Google: {e}"
    
    async def _open_youtube(self, text: str) -> str:
        """YouTube'u aç"""
        try:
            import webbrowser
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube..."
        except Exception as e:
            return f"Error opening YouTube: {e}"
    
    async def _open_github(self, text: str) -> str:
        """GitHub'ı aç"""
        try:
            import webbrowser
            webbrowser.open("https://www.github.com")
            return "Opening GitHub..."
        except Exception as e:
            return f"Error opening GitHub: {e}"
    
    async def _search_web(self, text: str) -> str:
        """Web'de ara"""
        try:
            # "search for" kelimelerini çıkar
            query = text.replace("search for", "").strip()
            if query:
                import webbrowser
                search_url = f"https://www.google.com/search?q={query}"
                webbrowser.open(search_url)
                return f"Searching for: {query}"
            else:
                return "Please specify what to search for"
        except Exception as e:
            return f"Error searching web: {e}"
    
    async def _close_tab(self, text: str) -> str:
        """Sekmeyi kapat"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'application_manager'):
                success = await self.jarvis_core.application_manager.close_current_tab()
                if success:
                    return "Current tab closed"
                else:
                    return "Could not close current tab"
            else:
                return "Application manager not available"
        except Exception as e:
            return f"Error closing tab: {e}"
    
    async def _open_new_tab(self, text: str) -> str:
        """Yeni sekme aç"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'application_manager'):
                success = await self.jarvis_core.application_manager.open_new_tab()
                if success:
                    return "New tab opened"
                else:
                    return "Could not open new tab"
            else:
                return "Application manager not available"
        except Exception as e:
            return f"Error opening new tab: {e}"
    
    async def _get_weather(self, text: str) -> str:
        """Hava durumu"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'plugin_manager'):
                # Weather plugin'ini çağır
                result = await self.jarvis_core.plugin_manager.execute_plugin_command("weather", "get_current_weather")
                return result
            else:
                return "Weather plugin not available"
        except Exception as e:
            return f"Error getting weather: {e}"
    
    async def _show_calendar(self, text: str) -> str:
        """Takvim göster"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'plugin_manager'):
                result = await self.jarvis_core.plugin_manager.execute_plugin_command("calendar", "get_events")
                return result
            else:
                return "Calendar plugin not available"
        except Exception as e:
            return f"Error showing calendar: {e}"
    
    async def _check_emails(self, text: str) -> str:
        """E-postaları kontrol et"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'plugin_manager'):
                result = await self.jarvis_core.plugin_manager.execute_plugin_command("email", "check_emails")
                return result
            else:
                return "Email plugin not available"
        except Exception as e:
            return f"Error checking emails: {e}"
    
    async def _show_system_status(self, text: str) -> str:
        """Sistem durumu"""
        try:
            if self.jarvis_core:
                status = self.jarvis_core.get_status()
                return f"System Status: {json.dumps(status, indent=2)}"
            else:
                return "JARVIS Core not available"
        except Exception as e:
            return f"Error getting system status: {e}"
    
    async def _show_system_info(self, text: str) -> str:
        """Sistem bilgisi"""
        try:
            import platform
            import psutil
            
            info = f"""System Information:
Platform: {platform.system()} {platform.release()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
Memory: {psutil.virtual_memory().total // (1024**3)} GB
CPU Cores: {psutil.cpu_count()}
Disk Space: {psutil.disk_usage('/').free // (1024**3)} GB free
            """
            return info
        except Exception as e:
            return f"Error getting system info: {e}"
    
    async def _show_help(self, text: str) -> str:
        """Yardım göster"""
        return """I can help you with:

🎯 Basic Commands:
• "Hey JARVIS" - Wake me up
• "What time is it?" - Get current time
• "Hello" - Greet me

🖥️ System Commands:
• "Show running applications" - List running apps
• "Close [app name]" - Close specific app
• "Increase/Decrease volume" - Control volume
• "Set brightness to X%" - Adjust brightness

💻 Terminal Commands:
• "Run git status" - Execute git commands
• "List files" - Show directory contents
• "Install package [name]" - Install packages

🌐 Web Commands:
• "Open Google/YouTube/GitHub" - Open websites
• "Search for [query]" - Search the web
• "Close current tab" - Close browser tab

🔌 Plugin Commands:
• "What's the weather?" - Get weather
• "Show my calendar" - Display calendar
• "Check my emails" - Check emails
• "Show system status" - System info

Just say "Hey JARVIS" followed by any command!"""
    
    async def _show_commands(self, text: str) -> str:
        """Komutları listele"""
        commands = list(self.commands.keys())
        return f"Available commands:\n" + "\n".join([f"• {cmd}" for cmd in commands[:20]])
    
    async def _handle_ai_query(self, text: str) -> str:
        """AI'ye yönlendir"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'ai_manager'):
                response = await self.jarvis_core.ai_manager.process_query(text)
                return response
            else:
                return "I didn't understand that command. Try saying 'help' for available commands."
        except Exception as e:
            return f"Error processing AI query: {e}"

class VoiceCommandsWindow:
    """Sesli komutlar penceresi"""
    
    def __init__(self, parent, voice_handler: VoiceCommandHandler):
        self.parent = parent
        self.voice_handler = voice_handler
        self.window = None
        
    def show(self):
        """Pencereyi göster"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("🎤 Voice Commands")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Ana frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🎤 Voice Commands", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Komut test alanı
        test_frame = ttk.LabelFrame(main_frame, text="Test Voice Command", padding="10")
        test_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Input alanı
        input_frame = ttk.Frame(test_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Command:").pack(side=tk.LEFT)
        self.command_input = ttk.Entry(input_frame, width=50)
        self.command_input.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.command_input.bind('<Return>', self.test_command)
        
        ttk.Button(input_frame, text="Test", command=self.test_command).pack(side=tk.RIGHT)
        
        # Response alanı
        ttk.Label(test_frame, text="Response:").pack(anchor=tk.W, pady=(10, 5))
        self.response_text = scrolledtext.ScrolledText(test_frame, height=8, width=80)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # Komut listesi
        commands_frame = ttk.LabelFrame(main_frame, text="Available Commands", padding="10")
        commands_frame.pack(fill=tk.BOTH, expand=True)
        
        # Komut kategorileri
        categories = {
            "Basic Commands": [
                "hey jarvis", "what time is it", "hello", "hi"
            ],
            "System Commands": [
                "show running applications", "close chrome", "increase volume", 
                "decrease volume", "mute", "unmute", "set brightness"
            ],
            "Terminal Commands": [
                "run git status", "run git log", "list files", 
                "install package", "update packages"
            ],
            "Web Commands": [
                "open google", "open youtube", "open github", 
                "search for", "close current tab", "open new tab"
            ],
            "Plugin Commands": [
                "what's the weather", "show my calendar", 
                "check my emails", "show system status"
            ]
        }
        
        # Notebook oluştur
        notebook = ttk.Notebook(commands_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        for category, commands in categories.items():
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=category)
            
            # Komut listesi
            commands_text = scrolledtext.ScrolledText(frame, height=15, width=80)
            commands_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            for cmd in commands:
                commands_text.insert(tk.END, f"• {cmd}\n")
            
            commands_text.config(state=tk.DISABLED)
        
        # Alt butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_commands).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="❌ Close", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def test_command(self, event=None):
        """Komutu test et"""
        command = self.command_input.get()
        if command:
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, "Processing command...\n")
            
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self.voice_handler.process_command(command))
                    self.window.after(0, lambda: self._update_response(result))
                except Exception as e:
                    self.window.after(0, lambda: self._update_response(f"Error: {e}"))
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            
            self.command_input.delete(0, tk.END)
    
    def _update_response(self, response: str):
        """Response'u güncelle"""
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, response)
    
    def refresh_commands(self):
        """Komutları yenile"""
        self.voice_handler.setup_commands()
        messagebox.showinfo("Info", "Commands refreshed!")

