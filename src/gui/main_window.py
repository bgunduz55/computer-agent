"""
JARVIS Main Window
Kapsamlı ana arayüz penceresi
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import asyncio
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import sys
import json
from datetime import datetime
import webbrowser

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.jarvis_core import get_jarvis_core
from features.settings import get_settings_manager
from .voice_commands import VoiceCommandHandler, VoiceCommandsWindow
from .ai_integration import AIIntegrationWindow
from .terminal_integration import TerminalIntegrationWindow

logger = logging.getLogger(__name__)

class JARVISMainWindow:
    """JARVIS Ana Pencere"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.jarvis_core = None
        self.settings_manager = None
        self.is_running = False
        self.log_text = None
        self.status_labels = {}
        self.voice_handler = None
        self.voice_window = None
        self.ai_window = None
        self.terminal_window = None
        self.setup_window()
        self.create_widgets()
        self.initialize_jarvis()
        
    def setup_window(self):
        """Pencere ayarlarını yap"""
        self.root.title("🤖 JARVIS Computer Assistant v1.0.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Pencere ikonu
        try:
            self.root.iconbitmap("icons/jarvis.ico")
        except:
            pass
        
        # Pencere kapatma olayı
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_widgets(self):
        """Widget'ları oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Başlık
        self.create_header(main_frame)
        
        # Kontrol paneli
        self.create_control_panel(main_frame)
        
        # Ana içerik alanı
        self.create_main_content(main_frame)
        
        # Alt panel
        self.create_bottom_panel(main_frame)
        
    def create_header(self, parent):
        """Başlık bölümünü oluştur"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Logo ve başlık
        title_label = ttk.Label(header_frame, text="🤖 JARVIS Computer Assistant", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Durum göstergesi
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT)
        
        self.status_indicator = ttk.Label(status_frame, text="●", foreground="red", 
                                        font=('Arial', 16, 'bold'))
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_text = ttk.Label(status_frame, text="Stopped", font=('Arial', 12))
        self.status_text.pack(side=tk.LEFT)
        
    def create_control_panel(self, parent):
        """Kontrol panelini oluştur"""
        control_frame = ttk.LabelFrame(parent, text="Control Panel", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Sol taraf - Ana kontroller
        left_frame = ttk.Frame(control_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Başlat/Durdur butonları
        self.start_btn = ttk.Button(left_frame, text="🚀 Start JARVIS", 
                                   command=self.start_jarvis, style="Accent.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(left_frame, text="⏹️ Stop JARVIS", 
                                  command=self.stop_jarvis, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.restart_btn = ttk.Button(left_frame, text="🔄 Restart", 
                                     command=self.restart_jarvis, state=tk.DISABLED)
        self.restart_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Sağ taraf - Hızlı erişim
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Button(right_frame, text="⚙️ Settings", 
                  command=self.open_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="🎤 Voice", 
                  command=self.open_voice_commands).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="🤖 AI", 
                  command=self.open_ai_integration).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="💻 Terminal", 
                  command=self.open_terminal_integration).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="📊 Analytics", 
                  command=self.open_analytics).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="🔌 Plugins", 
                  command=self.open_plugins).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="📱 Remote", 
                  command=self.open_remote).pack(side=tk.LEFT)
        
    def create_main_content(self, parent):
        """Ana içerik alanını oluştur"""
        # Notebook (sekmeli arayüz)
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Status sekmesi
        self.create_status_tab()
        
        # Logs sekmesi
        self.create_logs_tab()
        
        # Voice sekmesi
        self.create_voice_tab()
        
        # AI sekmesi
        self.create_ai_tab()
        
        # Terminal sekmesi
        self.create_terminal_tab()
        
        # System sekmesi
        self.create_system_tab()
        
    def create_status_tab(self):
        """Status sekmesini oluştur"""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="📊 Status")
        
        # Sol panel - Sistem durumu
        left_panel = ttk.LabelFrame(status_frame, text="System Status", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Durum bilgileri
        status_info = [
            ("JARVIS Core", "status_core"),
            ("Voice Recognition", "status_voice"),
            ("AI Integration", "status_ai"),
            ("WebSocket Server", "status_websocket"),
            ("Plugin Manager", "status_plugins"),
            ("Performance Monitor", "status_performance"),
            ("Security Manager", "status_security"),
            ("Analytics", "status_analytics")
        ]
        
        for i, (label, key) in enumerate(status_info):
            row_frame = ttk.Frame(left_panel)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"{label}:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            
            status_label = ttk.Label(row_frame, text="Inactive", foreground="red")
            status_label.pack(side=tk.RIGHT)
            
            self.status_labels[key] = status_label
        
        # Sağ panel - Sistem bilgileri
        right_panel = ttk.LabelFrame(status_frame, text="System Information", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Sistem bilgileri
        self.system_info_text = scrolledtext.ScrolledText(right_panel, height=15, width=40)
        self.system_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Sistem bilgilerini güncelle
        self.update_system_info()
        
    def create_logs_tab(self):
        """Logs sekmesini oluştur"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📝 Logs")
        
        # Log kontrolleri
        controls_frame = ttk.Frame(logs_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="🔄 Refresh", 
                  command=self.refresh_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="🗑️ Clear", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="💾 Save", 
                  command=self.save_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # Log seviyesi seçimi
        ttk.Label(controls_frame, text="Level:").pack(side=tk.LEFT, padx=(20, 5))
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(controls_frame, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                      state="readonly", width=10)
        log_level_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # Log metni
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=25, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Log'ları yükle
        self.load_logs()
        
    def create_voice_tab(self):
        """Voice sekmesini oluştur"""
        voice_frame = ttk.Frame(self.notebook)
        self.notebook.add(voice_frame, text="🎤 Voice")
        
        # Voice kontrolleri
        controls_frame = ttk.LabelFrame(voice_frame, text="Voice Controls", padding="10")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Mikrofon durumu
        mic_frame = ttk.Frame(controls_frame)
        mic_frame.pack(fill=tk.X, pady=5)
        
        self.mic_status = ttk.Label(mic_frame, text="🎤 Microphone: Not Connected", 
                                   foreground="red", font=('Arial', 12, 'bold'))
        self.mic_status.pack(side=tk.LEFT)
        
        ttk.Button(mic_frame, text="🔧 Test Microphone", 
                  command=self.test_microphone).pack(side=tk.RIGHT)
        
        # Voice komutları
        commands_frame = ttk.LabelFrame(voice_frame, text="Voice Commands", padding="10")
        commands_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Komut listesi
        commands_text = """
Available Voice Commands:

🎯 Basic Commands:
• "Hey JARVIS" - Wake up the assistant
• "What time is it?" - Get current time
• "Open Google" - Open web browser
• "Close current tab" - Close browser tab

🖥️ System Commands:
• "Show running applications" - List running apps
• "Close Chrome" - Close specific application
• "Increase volume" - Adjust system volume
• "Set brightness to 50%" - Adjust screen brightness

💻 Terminal Commands:
• "Run git status" - Execute git command
• "Install package numpy" - Install Python package
• "List files in current directory" - Show directory contents

🔌 Plugin Commands:
• "What's the weather?" - Get weather information
• "Show my calendar" - Display calendar events
• "Check my emails" - Check email inbox
• "Show system status" - Display system information
        """
        
        commands_display = scrolledtext.ScrolledText(commands_frame, height=20, width=80)
        commands_display.pack(fill=tk.BOTH, expand=True)
        commands_display.insert(tk.END, commands_text)
        commands_display.config(state=tk.DISABLED)
        
    def create_ai_tab(self):
        """AI sekmesini oluştur"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="🤖 AI")
        
        # AI Provider seçimi
        provider_frame = ttk.LabelFrame(ai_frame, text="AI Provider", padding="10")
        provider_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(provider_frame, text="Current Provider:").pack(side=tk.LEFT)
        self.ai_provider_var = tk.StringVar(value="Ollama")
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.ai_provider_var,
                                     values=["Ollama", "OpenAI", "Google Gemini", "Anthropic"],
                                     state="readonly", width=20)
        provider_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Button(provider_frame, text="⚙️ Configure", 
                  command=self.configure_ai).pack(side=tk.LEFT)
        
        # AI Test alanı
        test_frame = ttk.LabelFrame(ai_frame, text="AI Test", padding="10")
        test_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Test input
        input_frame = ttk.Frame(test_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Test Message:").pack(side=tk.LEFT)
        self.ai_test_input = ttk.Entry(input_frame, width=50)
        self.ai_test_input.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        
        ttk.Button(input_frame, text="Send", command=self.test_ai).pack(side=tk.RIGHT)
        
        # AI Response
        ttk.Label(test_frame, text="AI Response:").pack(anchor=tk.W)
        self.ai_response_text = scrolledtext.ScrolledText(test_frame, height=15, width=80)
        self.ai_response_text.pack(fill=tk.BOTH, expand=True)
        
    def create_terminal_tab(self):
        """Terminal sekmesini oluştur"""
        terminal_frame = ttk.Frame(self.notebook)
        self.notebook.add(terminal_frame, text="💻 Terminal")
        
        # Terminal kontrolleri
        controls_frame = ttk.Frame(terminal_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Command:").pack(side=tk.LEFT)
        self.terminal_input = ttk.Entry(controls_frame, width=50)
        self.terminal_input.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.terminal_input.bind('<Return>', self.execute_terminal_command)
        
        ttk.Button(controls_frame, text="Execute", 
                  command=self.execute_terminal_command).pack(side=tk.RIGHT)
        
        # Terminal çıktısı
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, height=20, width=100)
        self.terminal_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Terminal çıktısını yükle
        self.load_terminal_output()
        
    def create_system_tab(self):
        """System sekmesini oluştur"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="🖥️ System")
        
        # Sistem bilgileri
        info_frame = ttk.LabelFrame(system_frame, text="System Information", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.system_details_text = scrolledtext.ScrolledText(info_frame, height=25, width=100)
        self.system_details_text.pack(fill=tk.BOTH, expand=True)
        
        # Sistem bilgilerini yükle
        self.load_system_details()
        
    def create_bottom_panel(self, parent):
        """Alt paneli oluştur"""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Sol taraf - Hızlı durum
        left_info = ttk.Label(bottom_frame, text="Ready to assist you with your computing needs!")
        left_info.pack(side=tk.LEFT)
        
        # Sağ taraf - Hızlı butonlar
        right_buttons = ttk.Frame(bottom_frame)
        right_buttons.pack(side=tk.RIGHT)
        
        ttk.Button(right_buttons, text="📖 Help", command=self.show_help).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="🐛 Debug", command=self.toggle_debug).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_buttons, text="❌ Exit", command=self.on_closing).pack(side=tk.LEFT)
        
    def initialize_jarvis(self):
        """JARVIS'i başlat"""
        try:
            self.jarvis_core = get_jarvis_core()
            self.settings_manager = get_settings_manager()
            
            # Voice handler'ı initialize et
            self.voice_handler = VoiceCommandHandler(self.jarvis_core)
            
            # JARVIS'i initialize et
            def init_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.jarvis_core.initialize())
                self.root.after(0, self.update_status)
            
            thread = threading.Thread(target=init_async, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Failed to initialize JARVIS: {e}")
            messagebox.showerror("Error", f"Failed to initialize JARVIS: {e}")
    
    def start_jarvis(self):
        """JARVIS'i başlat"""
        try:
            def start_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.jarvis_core.start())
                self.is_running = True
                self.root.after(0, self.update_status)
            
            thread = threading.Thread(target=start_async, daemon=True)
            thread.start()
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.restart_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            logger.error(f"Failed to start JARVIS: {e}")
            messagebox.showerror("Error", f"Failed to start JARVIS: {e}")
    
    def stop_jarvis(self):
        """JARVIS'i durdur"""
        try:
            def stop_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.jarvis_core.stop())
                self.is_running = False
                self.root.after(0, self.update_status)
            
            thread = threading.Thread(target=stop_async, daemon=True)
            thread.start()
            
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.restart_btn.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Failed to stop JARVIS: {e}")
            messagebox.showerror("Error", f"Failed to stop JARVIS: {e}")
    
    def restart_jarvis(self):
        """JARVIS'i yeniden başlat"""
        self.stop_jarvis()
        self.root.after(2000, self.start_jarvis)  # 2 saniye bekle
    
    def update_status(self):
        """Durumu güncelle"""
        if self.jarvis_core:
            try:
                status = self.jarvis_core.get_status()
                
                # Ana durum
                if status.get('is_running'):
                    self.status_indicator.config(foreground="green")
                    self.status_text.config(text="Running")
                else:
                    self.status_indicator.config(foreground="red")
                    self.status_text.config(text="Stopped")
                
                # Servis durumları
                services = status.get('services', {})
                for key, label in self.status_labels.items():
                    service_name = key.replace('status_', '')
                    if service_name in services:
                        if services[service_name]:
                            label.config(text="Active", foreground="green")
                        else:
                            label.config(text="Inactive", foreground="red")
                    else:
                        label.config(text="Unknown", foreground="gray")
                        
            except Exception as e:
                logger.error(f"Failed to update status: {e}")
    
    def update_system_info(self):
        """Sistem bilgilerini güncelle"""
        try:
            import platform
            import psutil
            
            info = f"""System Information:
Platform: {platform.system()} {platform.release()}
Architecture: {platform.architecture()[0]}
Processor: {platform.processor()}
Python Version: {platform.python_version()}

Memory:
Total: {psutil.virtual_memory().total // (1024**3)} GB
Available: {psutil.virtual_memory().available // (1024**3)} GB
Used: {psutil.virtual_memory().percent}%

Disk:
Total: {psutil.disk_usage('/').total // (1024**3)} GB
Free: {psutil.disk_usage('/').free // (1024**3)} GB
Used: {psutil.disk_usage('/').percent}%

CPU:
Cores: {psutil.cpu_count()}
Usage: {psutil.cpu_percent()}%
            """
            
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(tk.END, info)
            
        except Exception as e:
            logger.error(f"Failed to update system info: {e}")
    
    def load_logs(self):
        """Log'ları yükle"""
        try:
            log_file = Path("data/logs/voice.log")
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.log_text.delete(1.0, tk.END)
                    self.log_text.insert(tk.END, content)
                    self.log_text.see(tk.END)
        except Exception as e:
            logger.error(f"Failed to load logs: {e}")
    
    def refresh_logs(self):
        """Log'ları yenile"""
        self.load_logs()
    
    def clear_logs(self):
        """Log'ları temizle"""
        self.log_text.delete(1.0, tk.END)
    
    def save_logs(self):
        """Log'ları kaydet"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", "Logs saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save logs: {e}")
    
    def test_microphone(self):
        """Mikrofonu test et"""
        messagebox.showinfo("Info", "Microphone test functionality will be implemented")
    
    def configure_ai(self):
        """AI'yi yapılandır"""
        messagebox.showinfo("Info", "AI configuration will open settings")
        self.open_settings()
    
    def test_ai(self):
        """AI'yi test et"""
        message = self.ai_test_input.get()
        if message:
            self.ai_response_text.delete(1.0, tk.END)
            self.ai_response_text.insert(tk.END, f"Testing AI with: {message}\n\nProcessing...")
            
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if self.jarvis_core and hasattr(self.jarvis_core, 'ai_manager'):
                        response = loop.run_until_complete(
                            self.jarvis_core.ai_manager.process_query(message)
                        )
                        self.root.after(0, lambda r=response: self._update_ai_response(r))
                    else:
                        self.root.after(0, lambda: self._update_ai_response("AI Manager not available"))
                except Exception as e:
                    error_msg = f"Error: {e}"
                    self.root.after(0, lambda: self._update_ai_response(error_msg))
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            
            self.ai_test_input.delete(0, tk.END)
    
    def _update_ai_response(self, response: str):
        """AI response'unu güncelle"""
        self.ai_response_text.delete(1.0, tk.END)
        self.ai_response_text.insert(tk.END, f"AI Response:\n\n{response}")
    
    def execute_terminal_command(self, event=None):
        """Terminal komutu çalıştır"""
        command = self.terminal_input.get()
        if command:
            self.terminal_output.insert(tk.END, f"$ {command}\n")
            
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if self.jarvis_core and hasattr(self.jarvis_core, 'terminal_manager'):
                        result = loop.run_until_complete(
                            self.jarvis_core.terminal_manager.execute_command(command)
                        )
                        self.root.after(0, lambda r=result: self._update_terminal_output(r))
                    else:
                        self.root.after(0, lambda: self._update_terminal_output("Terminal Manager not available"))
                except Exception as e:
                    error_msg = f"Error: {e}"
                    self.root.after(0, lambda: self._update_terminal_output(error_msg))
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            
            self.terminal_input.delete(0, tk.END)
    
    def _update_terminal_output(self, result):
        """Terminal çıktısını güncelle"""
        if isinstance(result, dict):
            if result.get("success"):
                self.terminal_output.insert(tk.END, result.get("output", ""))
            else:
                self.terminal_output.insert(tk.END, f"Error: {result.get('error', 'Unknown error')}")
        else:
            self.terminal_output.insert(tk.END, str(result))
        
        self.terminal_output.insert(tk.END, "\n\n")
        self.terminal_output.see(tk.END)
    
    def load_terminal_output(self):
        """Terminal çıktısını yükle"""
        self.terminal_output.insert(tk.END, "JARVIS Terminal Ready\n")
        self.terminal_output.insert(tk.END, "Type commands and press Enter to execute\n\n")
    
    def load_system_details(self):
        """Sistem detaylarını yükle"""
        try:
            import psutil
            import platform
            
            details = f"""Detailed System Information:

Operating System:
- System: {platform.system()}
- Release: {platform.release()}
- Version: {platform.version()}
- Machine: {platform.machine()}
- Processor: {platform.processor()}

Hardware:
- CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical
- CPU Usage: {psutil.cpu_percent(interval=1)}%
- Memory Total: {psutil.virtual_memory().total // (1024**3)} GB
- Memory Available: {psutil.virtual_memory().available // (1024**3)} GB
- Memory Used: {psutil.virtual_memory().percent}%
- Disk Total: {psutil.disk_usage('/').total // (1024**3)} GB
- Disk Free: {psutil.disk_usage('/').free // (1024**3)} GB
- Disk Used: {psutil.disk_usage('/').percent}%

Network:
- Boot Time: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}
- Processes: {len(psutil.pids())}
            """
            
            self.system_details_text.delete(1.0, tk.END)
            self.system_details_text.insert(tk.END, details)
            
        except Exception as e:
            logger.error(f"Failed to load system details: {e}")
    
    def open_settings(self):
        """Ayarları aç"""
        try:
            from features.settings import show_settings
            show_settings()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def open_analytics(self):
        """Analytics'i aç"""
        messagebox.showinfo("Info", "Analytics panel will be implemented")
    
    def open_plugins(self):
        """Plugin'leri aç"""
        messagebox.showinfo("Info", "Plugin manager will be implemented")
    
    def open_remote(self):
        """Remote control'ü aç"""
        messagebox.showinfo("Info", "Remote control panel will be implemented")
    
    def open_voice_commands(self):
        """Sesli komutları aç"""
        try:
            if not self.voice_window:
                self.voice_window = VoiceCommandsWindow(self.root, self.voice_handler)
            self.voice_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open voice commands: {e}")
    
    def open_ai_integration(self):
        """AI entegrasyonunu aç"""
        try:
            if not self.ai_window:
                self.ai_window = AIIntegrationWindow(self.root, self.jarvis_core)
            self.ai_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open AI integration: {e}")
    
    def open_terminal_integration(self):
        """Terminal entegrasyonunu aç"""
        try:
            if not self.terminal_window:
                self.terminal_window = TerminalIntegrationWindow(self.root, self.jarvis_core)
            self.terminal_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open terminal integration: {e}")
    
    def show_help(self):
        """Yardım göster"""
        help_text = """
JARVIS Computer Assistant Help

This is a comprehensive voice-controlled computer assistant with the following features:

🎤 Voice Recognition: Advanced voice recognition with noise filtering
🤖 AI Integration: Multiple AI providers (Ollama, OpenAI, Google Gemini)
💻 Terminal Control: Execute commands in various shells
📱 Remote Control: WebSocket-based remote control
🔌 Plugin System: Extensible plugin architecture
⚙️ Settings: Comprehensive configuration management

For more information, visit the documentation or check the voice commands tab.
        """
        messagebox.showinfo("Help", help_text)
    
    def toggle_debug(self):
        """Debug modunu aç/kapat"""
        messagebox.showinfo("Info", "Debug mode toggle will be implemented")
    
    def on_closing(self):
        """Pencere kapatılırken"""
        if messagebox.askokcancel("Quit", "Do you want to quit JARVIS?"):
            if self.is_running:
                self.stop_jarvis()
            self.root.destroy()
    
    def run(self):
        """Ana pencereyi çalıştır"""
        self.root.mainloop()

def main():
    """Ana entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run main window
    app = JARVISMainWindow()
    app.run()

if __name__ == "__main__":
    main()
