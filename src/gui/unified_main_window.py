"""
JARVIS Unified Main Window
Tek birleşik arayüz - tüm özellikler tek yerde
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
import psutil
import platform
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.jarvis_core import get_jarvis_core
from features.settings.simple_settings_manager import get_simple_settings_manager

logger = logging.getLogger(__name__)

class JARVISUnifiedWindow:
    """JARVIS Unified Main Window - Tüm özellikler tek yerde"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.jarvis_core = None
        self.settings_manager = None
        self.is_running = False
        self.is_initialized = False
        
        # Türkçe karakter desteği için encoding ayarı
        try:
            import locale
            locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
            except:
                pass
        
        self.setup_window()
        self.create_widgets()
        self.initialize_jarvis()
        
    def setup_window(self):
        """Pencere ayarlarını yap"""
        self.root.title("🤖 JARVIS Computer Assistant v1.0.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Pencere kapatma olayı
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        
        # Renk şeması
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Status.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Accent.TButton', font=('Arial', 9, 'bold'))
        
    def create_widgets(self):
        """Widget'ları oluştur"""
        # Ana container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_container)
        
        # Main content area with notebook
        self.create_main_content(main_container)
        
        # Footer
        self.create_footer(main_container)
        
    def create_header(self, parent):
        """Header bölümünü oluştur"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sol taraf - Logo ve başlık
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(left_frame, text="🤖 JARVIS Computer Assistant", style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(left_frame, text="Intelligent Voice-Controlled Assistant", 
                                  font=('Arial', 10), foreground='#7f8c8d')
        subtitle_label.pack(anchor=tk.W)
        
        # Sağ taraf - Durum ve kontroller
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Durum göstergesi
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        self.status_indicator = ttk.Label(status_frame, text="●", 
                                        font=('Arial', 16), foreground='red')
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_text = ttk.Label(status_frame, text="Initializing...", style='Status.TLabel')
        self.status_text.pack(side=tk.LEFT)
        
        # Ana kontrol butonları
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(side=tk.RIGHT, padx=(0, 20))
        
        self.start_btn = ttk.Button(control_frame, text="▶️ Start", 
                                   command=self.start_jarvis, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop", 
                                  command=self.stop_jarvis, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
    def create_main_content(self, parent):
        """Ana içerik alanını oluştur"""
        # Notebook oluştur
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab change event'i ekle
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        
        # Dashboard sekmesi
        self.create_dashboard_tab()
        
        # Voice sekmesi
        self.create_voice_tab()
        
        # AI sekmesi
        self.create_ai_tab()
        
        # Terminal sekmesi
        self.create_terminal_tab()
        
        # Settings sekmesi
        self.create_settings_tab()
        
        # System sekmesi
        self.create_system_tab()
        
    def create_dashboard_tab(self):
        """Dashboard sekmesini oluştur"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Sol panel - Hızlı erişim
        left_panel = ttk.LabelFrame(dashboard_frame, text="Quick Actions", padding="15")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left_panel.configure(width=300)
        
        # Hızlı erişim butonları
        buttons = [
            ("🎤 Test Voice", self.test_voice_command, "Test voice recognition"),
            ("🤖 Test AI", self.test_ai_chat, "Test AI integration"),
            ("💻 Run Command", self.run_terminal_command, "Execute terminal command"),
            ("📊 System Status", self.refresh_system_status, "Refresh system information"),
            ("⚙️ Open Settings", self.open_settings, "Configure JARVIS"),
            ("📝 View Logs", self.view_logs, "Check activity logs"),
            ("❓ Help", self.show_help, "Get help and support")
        ]
        
        for text, command, tooltip in buttons:
            btn = ttk.Button(left_panel, text=text, command=command, width=25)
            btn.pack(fill=tk.X, pady=3)
            self.create_tooltip(btn, tooltip)
        
        # Sistem durumu
        status_frame = ttk.LabelFrame(left_panel, text="System Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_labels = {}
        status_items = [
            ("Voice Recognition", "status_voice"),
            ("AI Integration", "status_ai"),
            ("Terminal Control", "status_terminal"),
            ("WebSocket Server", "status_websocket"),
            ("Plugin System", "status_plugins"),
            ("Performance", "status_performance")
        ]
        
        for label, key in status_items:
            row_frame = ttk.Frame(status_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"{label}:", font=('Arial', 9)).pack(side=tk.LEFT)
            
            status_label = ttk.Label(row_frame, text="Inactive", foreground="red", font=('Arial', 9, 'bold'))
            status_label.pack(side=tk.RIGHT)
            
            self.status_labels[key] = status_label
        
        # Sağ panel - Sistem bilgileri
        right_panel = ttk.LabelFrame(dashboard_frame, text="System Information", padding="15")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        self.system_info_text = scrolledtext.ScrolledText(right_panel, height=20, width=60, 
                                                         font=('Consolas', 9))
        self.system_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Sistem bilgilerini yükle
        self.update_system_info()
        
    def create_voice_tab(self):
        """Voice sekmesini oluştur"""
        voice_frame = ttk.Frame(self.notebook)
        self.notebook.add(voice_frame, text="🎤 Voice")
        
        # Voice kontrolleri
        controls_frame = ttk.LabelFrame(voice_frame, text="Voice Controls", padding="15")
        controls_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Mikrofon durumu
        mic_frame = ttk.Frame(controls_frame)
        mic_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.mic_status = ttk.Label(mic_frame, text="🎤 Microphone: Checking...", 
                                   font=('Arial', 12, 'bold'), foreground='orange')
        self.mic_status.pack(side=tk.LEFT)
        
        ttk.Button(mic_frame, text="🔧 Test Microphone", 
                  command=self.test_microphone).pack(side=tk.RIGHT)
        
        # Mikrofon durumunu kontrol et
        self.check_microphone_status()
        
        # Voice komut testi
        test_frame = ttk.LabelFrame(voice_frame, text="Test Voice Command", padding="15")
        test_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Input
        input_frame = ttk.Frame(test_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Command:").pack(side=tk.LEFT)
        self.voice_test_input = ttk.Entry(input_frame, width=50)
        self.voice_test_input.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.voice_test_input.bind('<Return>', self.test_voice_command)
        
        ttk.Button(input_frame, text="Test", command=self.test_voice_command).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Voice recording button
        self.voice_record_btn = ttk.Button(input_frame, text="🎤 Record", 
                                         command=self.start_voice_recording)
        self.voice_record_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Voice recording status
        self.voice_recording_status = ttk.Label(input_frame, text="", foreground="red")
        self.voice_recording_status.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Response
        ttk.Label(test_frame, text="Response:").pack(anchor=tk.W, pady=(10, 5))
        self.voice_response_text = scrolledtext.ScrolledText(test_frame, height=10, width=80)
        self.voice_response_text.pack(fill=tk.BOTH, expand=True)
        
        # Hızlı komutlar
        quick_frame = ttk.LabelFrame(voice_frame, text="Quick Commands", padding="15")
        quick_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        commands = [
            "Hey JARVIS", "What time is it?", "Open Google", "Show running applications",
            "Increase volume", "Run git status", "What's the weather?"
        ]
        
        for i, cmd in enumerate(commands):
            btn = ttk.Button(quick_frame, text=cmd, 
                           command=lambda c=cmd: self.set_voice_input(c))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Grid ağırlıkları
        for i in range(4):
            quick_frame.columnconfigure(i, weight=1)
        
    def create_ai_tab(self):
        """AI sekmesini oluştur"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="🤖 AI")
        
        # AI provider seçimi
        provider_frame = ttk.LabelFrame(ai_frame, text="AI Provider", padding="15")
        provider_frame.pack(fill=tk.X, padx=20, pady=20)
        
        provider_row = ttk.Frame(provider_frame)
        provider_row.pack(fill=tk.X)
        
        ttk.Label(provider_row, text="Current Provider:").pack(side=tk.LEFT)
        
        # Load current provider from settings
        current_provider = "Ollama"
        if self.settings_manager:
            provider_name = self.settings_manager.get_setting('ai', 'default_provider', 'ollama')
            provider_mapping = {
                "gemini": "Google Gemini",
                "google_gemini": "Google Gemini", 
                "openai": "OpenAI",
                "openrouter": "OpenRouter",
                "anthropic": "Anthropic",
                "ollama": "Ollama"
            }
            current_provider = provider_mapping.get(provider_name, "Ollama")
        
        self.ai_provider_var = tk.StringVar(value=current_provider)
        provider_combo = ttk.Combobox(provider_row, textvariable=self.ai_provider_var, 
                                     values=["Ollama", "OpenAI", "Google Gemini", "OpenRouter", "Anthropic"], 
                                     state="readonly", width=20)
        provider_combo.pack(side=tk.LEFT, padx=(10, 10))
        
        ttk.Button(provider_row, text="⚙️ Configure", 
                  command=self.configure_ai_provider).pack(side=tk.RIGHT)
        
        # AI test alanı
        test_frame = ttk.LabelFrame(ai_frame, text="AI Chat", padding="15")
        test_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Input
        input_frame = ttk.Frame(test_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Message:").pack(side=tk.LEFT)
        self.ai_input = ttk.Entry(input_frame, width=50)
        self.ai_input.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.ai_input.bind('<Return>', self.send_ai_message)
        
        # Türkçe karakter desteği için input encoding
        self.ai_input.configure(validate='key', validatecommand=(self.ai_input.register(self.validate_turkish_input), '%P'))
        
        ttk.Button(input_frame, text="Send", command=self.send_ai_message).pack(side=tk.RIGHT)
        
        # Chat area
        self.ai_chat_text = scrolledtext.ScrolledText(test_frame, height=15, width=80, 
                                                     font=('Arial', 10))
        self.ai_chat_text.pack(fill=tk.BOTH, expand=True)
        
        # AI durumu
        status_frame = ttk.Frame(ai_frame)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.ai_status_label = ttk.Label(status_frame, text="AI Status: Not Connected", 
                                        font=('Arial', 10), foreground='red')
        self.ai_status_label.pack(side=tk.LEFT)
        
    def create_terminal_tab(self):
        """Terminal sekmesini oluştur"""
        terminal_frame = ttk.Frame(self.notebook)
        self.notebook.add(terminal_frame, text="💻 Terminal")
        
        # Terminal çıktısı
        output_frame = ttk.LabelFrame(terminal_frame, text="Terminal Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.terminal_output = scrolledtext.ScrolledText(output_frame, height=15, width=80, 
                                                        font=('Consolas', 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        
        # Komut girişi
        input_frame = ttk.Frame(terminal_frame)
        input_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Label(input_frame, text="Command:").pack(side=tk.LEFT)
        self.terminal_input = ttk.Entry(input_frame, width=50)
        self.terminal_input.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.terminal_input.bind('<Return>', self.execute_terminal_command)
        
        ttk.Button(input_frame, text="Execute", command=self.execute_terminal_command).pack(side=tk.RIGHT)
        
        # Hızlı komutlar
        quick_frame = ttk.Frame(terminal_frame)
        quick_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        commands = [
            ("Git Status", "git status"),
            ("List Files", "dir" if sys.platform == "win32" else "ls -la"),
            ("Python Version", "python --version"),
            ("Pip List", "pip list"),
            ("System Info", "systeminfo" if sys.platform == "win32" else "uname -a")
        ]
        
        for text, cmd in commands:
            ttk.Button(quick_frame, text=text, 
                      command=lambda c=cmd: self.set_terminal_input(c)).pack(side=tk.LEFT, padx=(0, 5))
        
    def create_settings_tab(self):
        """Settings sekmesini oluştur"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings content
        content_frame = ttk.Frame(settings_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # General Settings
        general_frame = ttk.LabelFrame(content_frame, text="General Settings", padding="15")
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Language
        lang_row = ttk.Frame(general_frame)
        lang_row.pack(fill=tk.X, pady=5)
        ttk.Label(lang_row, text="Language:").pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value="en")
        lang_combo = ttk.Combobox(lang_row, textvariable=self.language_var, 
                                 values=["en", "tr", "es", "fr", "de", "it", "ru", "zh", "ja", "ko"], 
                                 state="readonly", width=20)
        lang_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Theme
        theme_row = ttk.Frame(general_frame)
        theme_row.pack(fill=tk.X, pady=5)
        ttk.Label(theme_row, text="Theme:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value="light")
        theme_combo = ttk.Combobox(theme_row, textvariable=self.theme_var, 
                                  values=["light", "dark", "auto"], state="readonly", width=20)
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Timezone
        timezone_row = ttk.Frame(general_frame)
        timezone_row.pack(fill=tk.X, pady=5)
        ttk.Label(timezone_row, text="Timezone:").pack(side=tk.LEFT)
        self.timezone_var = tk.StringVar(value="UTC")
        timezone_combo = ttk.Combobox(timezone_row, textvariable=self.timezone_var, 
                                     values=["UTC", "Europe/Istanbul", "America/New_York", "Asia/Tokyo"], 
                                     state="readonly", width=20)
        timezone_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Startup Settings
        startup_row = ttk.Frame(general_frame)
        startup_row.pack(fill=tk.X, pady=5)
        self.auto_start_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(startup_row, text="Start JARVIS automatically on startup", 
                       variable=self.auto_start_var).pack(side=tk.LEFT)
        
        # Minimize to tray
        tray_row = ttk.Frame(general_frame)
        tray_row.pack(fill=tk.X, pady=5)
        self.minimize_to_tray_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tray_row, text="Minimize to system tray", 
                       variable=self.minimize_to_tray_var).pack(side=tk.LEFT)
        
        # Voice Settings
        voice_frame = ttk.LabelFrame(content_frame, text="Voice Settings", padding="15")
        voice_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Speech Recognition
        sr_row = ttk.Frame(voice_frame)
        sr_row.pack(fill=tk.X, pady=5)
        ttk.Label(sr_row, text="Speech Recognition Engine:").pack(side=tk.LEFT)
        self.sr_engine_var = tk.StringVar(value="google")
        sr_combo = ttk.Combobox(sr_row, textvariable=self.sr_engine_var, 
                               values=["google", "sphinx", "azure", "bing"], 
                               state="readonly", width=20)
        sr_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # TTS Engine
        tts_row = ttk.Frame(voice_frame)
        tts_row.pack(fill=tk.X, pady=5)
        ttk.Label(tts_row, text="Text-to-Speech Engine:").pack(side=tk.LEFT)
        self.tts_engine_var = tk.StringVar(value="sapi5")
        tts_combo = ttk.Combobox(tts_row, textvariable=self.tts_engine_var, 
                                values=["sapi5", "edge", "espeak", "festival"], 
                                state="readonly", width=20)
        tts_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Voice Language
        voice_lang_row = ttk.Frame(voice_frame)
        voice_lang_row.pack(fill=tk.X, pady=5)
        ttk.Label(voice_lang_row, text="Voice Language:").pack(side=tk.LEFT)
        self.voice_lang_var = tk.StringVar(value="en-US")
        voice_lang_combo = ttk.Combobox(voice_lang_row, textvariable=self.voice_lang_var, 
                                       values=["en-US", "tr-TR", "es-ES", "fr-FR", "de-DE"], 
                                       state="readonly", width=20)
        voice_lang_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Confidence Threshold
        conf_row = ttk.Frame(voice_frame)
        conf_row.pack(fill=tk.X, pady=5)
        ttk.Label(conf_row, text="Confidence Threshold:").pack(side=tk.LEFT)
        self.confidence_var = tk.DoubleVar(value=0.7)
        conf_scale = ttk.Scale(conf_row, from_=0.1, to=1.0, variable=self.confidence_var, 
                              orient=tk.HORIZONTAL, length=200)
        conf_scale.pack(side=tk.LEFT, padx=(10, 0))
        conf_label = ttk.Label(conf_row, text="0.7")
        conf_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Voice Rate
        rate_row = ttk.Frame(voice_frame)
        rate_row.pack(fill=tk.X, pady=5)
        ttk.Label(rate_row, text="Voice Rate:").pack(side=tk.LEFT)
        self.rate_var = tk.IntVar(value=150)
        rate_scale = ttk.Scale(rate_row, from_=50, to=300, variable=self.rate_var, 
                              orient=tk.HORIZONTAL, length=200)
        rate_scale.pack(side=tk.LEFT, padx=(10, 0))
        rate_label = ttk.Label(rate_row, text="150")
        rate_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Voice Volume
        volume_row = ttk.Frame(voice_frame)
        volume_row.pack(fill=tk.X, pady=5)
        ttk.Label(volume_row, text="Voice Volume:").pack(side=tk.LEFT)
        self.volume_var = tk.DoubleVar(value=0.9)
        volume_scale = ttk.Scale(volume_row, from_=0.0, to=1.0, variable=self.volume_var, 
                                orient=tk.HORIZONTAL, length=200)
        volume_scale.pack(side=tk.LEFT, padx=(10, 0))
        volume_label = ttk.Label(volume_row, text="0.9")
        volume_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # AI Settings
        ai_frame = ttk.LabelFrame(content_frame, text="AI Settings", padding="15")
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        # AI Provider
        ai_row = ttk.Frame(ai_frame)
        ai_row.pack(fill=tk.X, pady=5)
        ttk.Label(ai_row, text="AI Provider:").pack(side=tk.LEFT)
        self.ai_provider_setting_var = tk.StringVar(value="ollama")
        ai_provider_combo = ttk.Combobox(ai_row, textvariable=self.ai_provider_setting_var, 
                                        values=["ollama", "openai", "google_gemini", "openrouter", "anthropic"], 
                                        state="readonly", width=20)
        ai_provider_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # AI Model
        model_row = ttk.Frame(ai_frame)
        model_row.pack(fill=tk.X, pady=5)
        ttk.Label(model_row, text="AI Model:").pack(side=tk.LEFT)
        self.ai_model_var = tk.StringVar(value="llama2")
        model_combo = ttk.Combobox(model_row, textvariable=self.ai_model_var, 
                                  values=["llama2", "gpt-3.5-turbo", "gpt-4", "gemini-pro"], 
                                  state="readonly", width=20)
        model_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # API Key
        api_key_row = ttk.Frame(ai_frame)
        api_key_row.pack(fill=tk.X, pady=5)
        ttk.Label(api_key_row, text="API Key:").pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value="")
        api_key_entry = ttk.Entry(api_key_row, textvariable=self.api_key_var, 
                                 show="*", width=30)
        api_key_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Temperature
        temp_row = ttk.Frame(ai_frame)
        temp_row.pack(fill=tk.X, pady=5)
        ttk.Label(temp_row, text="Temperature:").pack(side=tk.LEFT)
        self.temperature_var = tk.DoubleVar(value=0.7)
        temp_scale = ttk.Scale(temp_row, from_=0.0, to=2.0, variable=self.temperature_var, 
                              orient=tk.HORIZONTAL, length=200)
        temp_scale.pack(side=tk.LEFT, padx=(10, 0))
        temp_label = ttk.Label(temp_row, text="0.7")
        temp_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Max Tokens
        tokens_row = ttk.Frame(ai_frame)
        tokens_row.pack(fill=tk.X, pady=5)
        ttk.Label(tokens_row, text="Max Tokens:").pack(side=tk.LEFT)
        self.max_tokens_var = tk.IntVar(value=1000)
        tokens_entry = ttk.Entry(tokens_row, textvariable=self.max_tokens_var, width=10)
        tokens_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Remote Settings
        remote_frame = ttk.LabelFrame(content_frame, text="Remote Control", padding="15")
        remote_frame.pack(fill=tk.X, pady=(0, 10))
        
        # WebSocket Host
        host_row = ttk.Frame(remote_frame)
        host_row.pack(fill=tk.X, pady=5)
        ttk.Label(host_row, text="Host:").pack(side=tk.LEFT)
        self.host_var = tk.StringVar(value="0.0.0.0")
        host_entry = ttk.Entry(host_row, textvariable=self.host_var, width=25)
        host_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # WebSocket Port
        port_row = ttk.Frame(remote_frame)
        port_row.pack(fill=tk.X, pady=5)
        ttk.Label(port_row, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="8765")
        port_entry = ttk.Entry(port_row, textvariable=self.port_var, width=25)
        port_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Authentication
        auth_row = ttk.Frame(remote_frame)
        auth_row.pack(fill=tk.X, pady=5)
        self.auth_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(auth_row, text="Enable Authentication", 
                       variable=self.auth_enabled_var).pack(side=tk.LEFT)
        
        # API Token
        token_row = ttk.Frame(remote_frame)
        token_row.pack(fill=tk.X, pady=5)
        ttk.Label(token_row, text="API Token:").pack(side=tk.LEFT)
        self.api_token_var = tk.StringVar(value="")
        token_entry = ttk.Entry(token_row, textvariable=self.api_token_var, 
                               show="*", width=30)
        token_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Mobile App Settings
        mobile_row = ttk.Frame(remote_frame)
        mobile_row.pack(fill=tk.X, pady=5)
        ttk.Label(mobile_row, text="Mobile App:").pack(side=tk.LEFT)
        ttk.Button(mobile_row, text="Generate QR Code", 
                  command=self.generate_qr_code).pack(side=tk.LEFT, padx=(10, 0))
        
        # Connection Info
        info_row = ttk.Frame(remote_frame)
        info_row.pack(fill=tk.X, pady=5)
        ttk.Label(info_row, text="Connection Info:").pack(side=tk.LEFT)
        self.connection_info_var = tk.StringVar(value="ws://0.0.0.0:8765")
        info_entry = ttk.Entry(info_row, textvariable=self.connection_info_var, 
                              state="readonly", width=30)
        info_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Save button
        save_frame = ttk.Frame(content_frame)
        save_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(save_frame, text="💾 Save Settings", 
                  command=self.save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(save_frame, text="🔄 Reset to Defaults", 
                  command=self.reset_settings_to_defaults).pack(side=tk.RIGHT, padx=(5, 0))
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            # Settings'i topla
            settings = {
                "general": {
                    "language": self.language_var.get(),
                    "theme": self.theme_var.get(),
                    "timezone": self.timezone_var.get(),
                    "auto_start": self.auto_start_var.get(),
                    "minimize_to_tray": self.minimize_to_tray_var.get()
                },
                "voice": {
                    "sr_engine": self.sr_engine_var.get(),
                    "tts_engine": self.tts_engine_var.get(),
                    "voice_language": self.voice_lang_var.get(),
                    "confidence_threshold": self.confidence_var.get(),
                    "rate": self.rate_var.get(),
                    "volume": self.volume_var.get()
                },
                "ai": {
                    "provider": self.ai_provider_setting_var.get(),
                    "model": self.ai_model_var.get(),
                    "api_key": self.api_key_var.get(),
                    "temperature": self.temperature_var.get(),
                    "max_tokens": self.max_tokens_var.get()
                },
                "remote": {
                    "host": self.host_var.get(),
                    "port": self.port_var.get(),
                    "auth_enabled": self.auth_enabled_var.get(),
                    "api_token": self.api_token_var.get()
                }
            }
            
            # Settings'i kaydet
            if self.settings_manager:
                self.settings_manager.save_settings(settings)
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                messagebox.showerror("Error", "Settings manager not available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings_to_defaults(self):
        """Ayarları varsayılan değerlere sıfırla"""
        try:
            # Varsayılan değerleri ayarla
            self.language_var.set("en")
            self.theme_var.set("light")
            self.timezone_var.set("UTC")
            self.auto_start_var.set(True)
            self.minimize_to_tray_var.set(True)
            
            self.sr_engine_var.set("google")
            self.tts_engine_var.set("sapi5")
            self.voice_lang_var.set("en-US")
            self.confidence_var.set(0.7)
            self.rate_var.set(150)
            self.volume_var.set(0.9)
            
            self.ai_provider_setting_var.set("ollama")
            self.ai_model_var.set("llama2")
            self.api_key_var.set("")
            self.temperature_var.set(0.7)
            self.max_tokens_var.set(1000)
            
            self.host_var.set("0.0.0.0")
            self.port_var.set("8765")
            self.auth_enabled_var.set(False)
            self.api_token_var.set("")
            
            messagebox.showinfo("Success", "Settings reset to defaults!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def generate_qr_code(self):
        """QR kod oluştur"""
        try:
            import qrcode
            from PIL import ImageTk
            
            # Connection info
            host = self.host_var.get()
            port = self.port_var.get()
            connection_url = f"ws://{host}:{port}"
            
            # QR kod oluştur
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(connection_url)
            qr.make(fit=True)
            
            # QR kod penceresi
            qr_window = tk.Toplevel(self.root)
            qr_window.title("JARVIS Connection QR Code")
            qr_window.geometry("400x500")
            
            # QR kod görüntüsü
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image = qr_image.resize((300, 300))
            qr_photo = ImageTk.PhotoImage(qr_image)
            
            qr_label = ttk.Label(qr_window, image=qr_photo)
            qr_label.pack(pady=20)
            
            # Connection info
            info_label = ttk.Label(qr_window, text=f"Connection URL:\n{connection_url}", 
                                  font=('Arial', 10))
            info_label.pack(pady=10)
            
            # Close button
            ttk.Button(qr_window, text="Close", command=qr_window.destroy).pack(pady=10)
            
            # Keep reference to prevent garbage collection
            qr_window.qr_photo = qr_photo
            
        except ImportError:
            messagebox.showerror("Error", "qrcode library not available. Install with: pip install qrcode[pil]")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {e}")
        
    def create_system_tab(self):
        """System sekmesini oluştur"""
        system_frame = ttk.Frame(self.notebook)
        self.notebook.add(system_frame, text="🖥️ System")
        
        # System info
        info_frame = ttk.LabelFrame(system_frame, text="System Information", padding="15")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.system_detailed_text = scrolledtext.ScrolledText(info_frame, height=20, width=80, 
                                                             font=('Consolas', 9))
        self.system_detailed_text.pack(fill=tk.BOTH, expand=True)
        
        # System actions
        actions_frame = ttk.LabelFrame(system_frame, text="System Actions", padding="15")
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Button(actions_frame, text="🔄 Refresh System Info", 
                  command=self.refresh_system_status).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="📊 Performance Monitor", 
                  command=self.open_performance_monitor).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="🔒 Security Status", 
                  command=self.open_security_status).pack(side=tk.LEFT)
        
    def create_footer(self, parent):
        """Footer bölümünü oluştur"""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Sol taraf - Bilgi
        info_label = ttk.Label(footer_frame, text="JARVIS Computer Assistant v1.0.0 | Ready to assist you!")
        info_label.pack(side=tk.LEFT)
        
        # Sağ taraf - Butonlar
        button_frame = ttk.Frame(footer_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ Exit", command=self.on_closing).pack(side=tk.LEFT)
        
    def create_tooltip(self, widget, text):
        """Tooltip oluştur"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="lightyellow", 
                            font=('Arial', 9), padding="5")
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def initialize_jarvis(self):
        """JARVIS'i başlat"""
        try:
            self.jarvis_core = get_jarvis_core()
            self.settings_manager = get_simple_settings_manager()
            
            # JARVIS'i initialize et
            def init_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.jarvis_core.initialize())
                    self.is_initialized = True
                    self.root.after(0, self.update_status)
                    # Otomatik başlat
                    self.root.after(1000, self.auto_start_jarvis)
                except Exception as e:
                    logger.error(f"Failed to initialize JARVIS: {e}")
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to initialize JARVIS: {e}"))
                finally:
                    loop.close()
            
            thread = threading.Thread(target=init_async, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Failed to initialize JARVIS: {e}")
            messagebox.showerror("Error", f"Failed to initialize JARVIS: {e}")
    
    def auto_start_jarvis(self):
        """JARVIS'i otomatik başlat"""
        if self.is_initialized and not self.is_running:
            self.start_jarvis()
    
    def start_jarvis(self):
        """JARVIS'i başlat"""
        try:
            def start_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.jarvis_core.start())
                    self.is_running = True
                    self.root.after(0, self.update_status)
                    self.root.after(0, self._start_ai_status_updates)
                except Exception as e:
                    logger.error(f"Failed to start JARVIS: {e}")
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start JARVIS: {e}"))
                finally:
                    loop.close()
            
            thread = threading.Thread(target=start_async, daemon=True)
            thread.start()
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start JARVIS: {e}")
    
    def stop_jarvis(self):
        """JARVIS'i durdur"""
        try:
            def stop_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.jarvis_core.stop())
                    self.is_running = False
                    self.root.after(0, self.update_status)
                except Exception as e:
                    logger.error(f"Failed to stop JARVIS: {e}")
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to stop JARVIS: {e}"))
                finally:
                    loop.close()
            
            thread = threading.Thread(target=stop_async, daemon=True)
            thread.start()
            
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop JARVIS: {e}")
    
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

JARVIS Status:
Voice Recognition: {'Active' if self.is_running else 'Inactive'}
AI Integration: {'Active' if self.is_running else 'Inactive'}
Terminal Control: {'Active' if self.is_running else 'Inactive'}
WebSocket Server: {'Active' if self.is_running else 'Inactive'}
            """
            
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(tk.END, info)
            
        except Exception as e:
            logger.error(f"Failed to update system info: {e}")
    
    def check_microphone_status(self):
        """Mikrofon durumunu kontrol et"""
        try:
            import sounddevice as sd
            # Mikrofon cihazlarını listele
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if input_devices:
                self.mic_status.config(text="🎤 Microphone: Connected", foreground="green")
            else:
                self.mic_status.config(text="🎤 Microphone: No Input Device", foreground="red")
        except ImportError:
            self.mic_status.config(text="🎤 Microphone: sounddevice not installed", foreground="orange")
            logger.warning("sounddevice library not available")
        except Exception as e:
            self.mic_status.config(text="🎤 Microphone: Error", foreground="red")
            logger.error(f"Failed to check microphone status: {e}")
    
    def test_microphone(self):
        """Mikrofonu test et"""
        try:
            import sounddevice as sd
            import numpy as np
            
            # Mikrofon testi
            self.mic_status.config(text="🎤 Microphone: Testing...", foreground="orange")
            
            def test_async():
                try:
                    # 1 saniye ses kaydet
                    duration = 1.0
                    sample_rate = 44100
                    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
                    sd.wait()
                    
                    # Ses seviyesini kontrol et
                    max_volume = np.max(np.abs(recording))
                    
                    if max_volume > 0.01:  # Ses algılandı
                        self.root.after(0, lambda: self.mic_status.config(
                            text="🎤 Microphone: Working", foreground="green"))
                        self.root.after(0, lambda: messagebox.showinfo("Success", "Microphone test successful!"))
                    else:
                        self.root.after(0, lambda: self.mic_status.config(
                            text="🎤 Microphone: No Sound", foreground="orange"))
                        self.root.after(0, lambda: messagebox.showwarning("Warning", "No sound detected. Check microphone."))
                        
                except Exception as e:
                    self.root.after(0, lambda: self.mic_status.config(
                        text="🎤 Microphone: Error", foreground="red"))
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Microphone test failed: {e}"))
            
            thread = threading.Thread(target=test_async, daemon=True)
            thread.start()
            
        except ImportError:
            messagebox.showerror("Error", "sounddevice library not available. Install with: pip install sounddevice")
        except Exception as e:
            messagebox.showerror("Error", f"Microphone test failed: {e}")
    
    def test_voice_command(self, event=None):
        """Sesli komut test et - gerçek voice command processing"""
        command = self.voice_test_input.get()
        if command:
            self.voice_response_text.delete(1.0, tk.END)
            self.voice_response_text.insert(tk.END, f"Testing: {command}\n\nProcessing...")
            
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if self.jarvis_core and hasattr(self.jarvis_core, 'speech_manager'):
                        # Import voice command handler
                        from gui.voice_commands import VoiceCommandHandler
                        
                        # Create voice command handler
                        voice_handler = VoiceCommandHandler(self.jarvis_core)
                        
                        # Process the command
                        response = loop.run_until_complete(
                            voice_handler.process_command(command)
                        )
                        
                        self.root.after(0, lambda r=response: self._update_voice_response(r))
                    else:
                        self.root.after(0, lambda: self._update_voice_response("Speech manager not available"))
                except Exception as e:
                    error_msg = f"Error: {e}"
                    self.root.after(0, lambda: self._update_voice_response(error_msg))
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            
            self.voice_test_input.delete(0, tk.END)
    
    def _update_voice_response(self, response: str):
        """Voice response'unu güncelle"""
        self.voice_response_text.delete(1.0, tk.END)
        self.voice_response_text.insert(tk.END, f"Response:\n\n{response}")
    
    def set_voice_input(self, text: str):
        """Voice input'unu ayarla"""
        self.voice_test_input.delete(0, tk.END)
        self.voice_test_input.insert(0, text)
    
    def start_voice_recording(self):
        """Sesli komut kaydetmeye başla"""
        if not self.jarvis_core or not hasattr(self.jarvis_core, 'speech_manager'):
            messagebox.showerror("Error", "Speech manager not available")
            return
        
        try:
            # Update UI
            self.voice_record_btn.config(text="⏹️ Stop", command=self.stop_voice_recording)
            self.voice_recording_status.config(text="Recording...", foreground="red")
            
            # Start voice recognition
            def run_voice_recognition():
                try:
                    # Use speech manager to recognize speech
                    recognized_text = self.jarvis_core.speech_manager.recognize_speech(timeout=5)
                    
                    if recognized_text:
                        # Update input field with recognized text
                        self.root.after(0, lambda: self.voice_test_input.delete(0, tk.END))
                        self.root.after(0, lambda: self.voice_test_input.insert(0, recognized_text))
                        
                        # Automatically test the command
                        self.root.after(0, self.test_voice_command)
                    else:
                        self.root.after(0, lambda: self.voice_recording_status.config(
                            text="No speech detected", foreground="orange"))
                    
                    # Reset UI
                    self.root.after(0, self.reset_voice_recording_ui)
                    
                except Exception as e:
                    self.root.after(0, lambda: self.voice_recording_status.config(
                        text=f"Error: {e}", foreground="red"))
                    self.root.after(0, self.reset_voice_recording_ui)
            
            thread = threading.Thread(target=run_voice_recognition, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Voice recording failed: {e}")
            self.reset_voice_recording_ui()
    
    def stop_voice_recording(self):
        """Sesli komut kaydını durdur"""
        # This would be called if we had a way to stop the recognition
        # For now, just reset the UI
        self.reset_voice_recording_ui()
    
    def reset_voice_recording_ui(self):
        """Voice recording UI'ını sıfırla"""
        self.voice_record_btn.config(text="🎤 Record", command=self.start_voice_recording)
        self.voice_recording_status.config(text="", foreground="red")
    
    def test_ai_chat(self):
        """AI chat test et"""
        self.notebook.select(2)  # AI sekmesine git
        self.ai_input.focus()
    
    def send_ai_message(self, event=None):
        """AI mesajı gönder"""
        message = self.ai_input.get()
        if message:
            self.ai_chat_text.insert(tk.END, f"You: {message}\n")
            self.ai_chat_text.insert(tk.END, "JARVIS: Thinking...\n\n")
            self.ai_chat_text.see(tk.END)
            
            def run_async():
                try:
                    # Check if JARVIS core is initialized
                    if not self.jarvis_core:
                        self.root.after(0, lambda: self._update_ai_chat("JARVIS Core not initialized"))
                        return
                    
                    # Check if AI manager is available
                    if not hasattr(self.jarvis_core, 'ai_manager') or not self.jarvis_core.ai_manager:
                        self.root.after(0, lambda: self._update_ai_chat("AI Manager not available"))
                        return
                    
                    # Create new event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        # Process AI query
                        response = loop.run_until_complete(
                            self.jarvis_core.ai_manager.process_query(message)
                        )
                        
                        # Extract response text if it's an AIResponse object
                        if hasattr(response, 'content'):
                            response_text = response.content
                        elif hasattr(response, 'text'):
                            response_text = response.text
                        else:
                            response_text = str(response)
                        
                        self.root.after(0, lambda r=response_text: self._update_ai_chat(r))
                    finally:
                        loop.close()
                        
                except Exception as e:
                    error_msg = f"Error: {e}"
                    self.root.after(0, lambda: self._update_ai_chat(error_msg))
            
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            
            self.ai_input.delete(0, tk.END)
    
    def _update_ai_chat(self, response: str):
        """AI chat'i güncelle - düzeltilmiş versiyon"""
        try:
            # "Thinking..." satırını kaldır
            self.ai_chat_text.delete("end-2l", "end-1l")
            
            # Response'u güvenli şekilde işle
            if response is None:
                response = "No response received"
            elif isinstance(response, bytes):
                response = response.decode('utf-8', errors='ignore')
            elif not isinstance(response, str):
                response = str(response)
            
            # Türkçe karakter encoding düzeltmesi
            response = response.replace('ý', 'ı').replace('Ý', 'I')
            response = response.replace('ð', 'ğ').replace('Ð', 'Ğ')
            response = response.replace('þ', 'ş').replace('Þ', 'Ş')
            
            # AI response'unu ekle
            self.ai_chat_text.insert(tk.END, f"JARVIS: {response}\n\n")
            self.ai_chat_text.see(tk.END)
            
        except Exception as e:
            # Hata durumunda güvenli fallback
            self.ai_chat_text.delete("end-2l", "end-1l")
            self.ai_chat_text.insert(tk.END, f"JARVIS: Error processing response: {str(e)}\n\n")
            self.ai_chat_text.see(tk.END)
    
    def _update_ai_status(self):
        """AI durumunu güncelle"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'ai_manager'):
                if hasattr(self.jarvis_core.ai_manager, '_initialized') and self.jarvis_core.ai_manager._initialized:
                    self.ai_status_label.config(text="AI Status: Connected", foreground="green")
                else:
                    self.ai_status_label.config(text="AI Status: Initializing...", foreground="orange")
            else:
                self.ai_status_label.config(text="AI Status: Not Available", foreground="red")
        except Exception as e:
            self.ai_status_label.config(text="AI Status: Error", foreground="red")
            logger.error(f"Failed to update AI status: {e}")
    
    def _start_ai_status_updates(self):
        """AI status güncellemelerini başlat"""
        self._update_ai_status()
        # Her 5 saniyede bir güncelle
        self.root.after(5000, self._start_ai_status_updates)
    
    def on_tab_change(self, event):
        """Tab değiştiğinde çağrılır"""
        try:
            selected_tab = event.widget.tab('current')['text']
            if selected_tab == "System":
                self._update_system_info()
        except Exception as e:
            logger.error(f"Error in tab change: {e}")
    
    def validate_turkish_input(self, value):
        """Türkçe karakter input validation"""
        try:
            # Türkçe karakterleri normalize et
            if value:
                value = value.replace('ý', 'ı').replace('Ý', 'I')
                value = value.replace('ð', 'ğ').replace('Ð', 'Ğ')
                value = value.replace('þ', 'ş').replace('Þ', 'Ş')
            return True
        except:
            return True
    
    def _update_system_info(self):
        """System info'yu güncelle"""
        try:
            # System info text'ini temizle
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(tk.END, "Loading system information...\n")
            self.root.update()  # Force GUI update
            
            if self.jarvis_core and hasattr(self.jarvis_core, 'system_info_manager'):
                self.system_info_text.insert(tk.END, "✓ JARVIS core and system_info_manager found\n")
                self.root.update()  # Force GUI update
                
                system_info = self.jarvis_core.system_info_manager.get_system_info()
                self.system_info_text.insert(tk.END, f"✓ System info retrieved: {type(system_info)}\n")
                self.root.update()  # Force GUI update
                
                # System info text'ini temizle ve yeni bilgiyi ekle
                self.system_info_text.delete(1.0, tk.END)
                
                # System info'yu ekle
                info = f"""🖥️ System Information
═══════════════════════════════════════

📊 Basic Info:
• OS: {system_info.get('os_name', 'Unknown')} {system_info.get('os_version', '')}
• Architecture: {system_info.get('architecture', 'Unknown')}
• Python: {system_info.get('python_version', 'Unknown')}
• Uptime: {system_info.get('uptime', 'Unknown')}

💾 Memory:
• Total: {system_info.get('memory_total', 'Unknown')}
• Available: {system_info.get('memory_available', 'Unknown')}
• Used: {system_info.get('memory_used_percent', 'Unknown')}%

🖥️ CPU:
• Cores: {system_info.get('cpu_cores', 'Unknown')}
• Usage: {system_info.get('cpu_usage', 'Unknown')}%

💽 Disk:
• Total: {system_info.get('disk_total', 'Unknown')}
• Free: {system_info.get('disk_free', 'Unknown')}
• Used: {system_info.get('disk_used_percent', 'Unknown')}%

🌐 Network:
• Hostname: {system_info.get('hostname', 'Unknown')}
• IP: {system_info.get('ip_address', 'Unknown')}

⏰ Time:
• Current: {system_info.get('current_time', 'Unknown')}
• Timezone: {system_info.get('timezone', 'Unknown')}

═══════════════════════════════════════
Last updated: {system_info.get('timestamp', 'Unknown')}
"""
                self.system_info_text.insert(tk.END, info)
            else:
                self.system_info_text.delete(1.0, tk.END)
                self.system_info_text.insert(tk.END, "System info manager not available")
                
        except Exception as e:
            logger.error(f"Failed to update system info: {e}")
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(tk.END, f"Error loading system info: {e}")
    
    def run_terminal_command(self):
        """Terminal komut çalıştır"""
        self.notebook.select(3)  # Terminal sekmesine git
        self.terminal_input.focus()
    
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
    
    def set_terminal_input(self, command: str):
        """Terminal input'unu ayarla"""
        self.terminal_input.delete(0, tk.END)
        self.terminal_input.insert(0, command)
    
    def open_settings(self):
        """Ayarları aç"""
        self.notebook.select(4)  # Settings sekmesine git
    
    def configure_ai_provider(self):
        """AI provider'ı yapılandır"""
        try:
            # AI Provider configuration window
            config_window = tk.Toplevel(self.root)
            config_window.title("AI Provider Configuration")
            config_window.geometry("500x400")
            config_window.resizable(False, False)
            
            # Center the window
            config_window.transient(self.root)
            config_window.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(config_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Provider selection
            provider_frame = ttk.LabelFrame(main_frame, text="AI Provider", padding="15")
            provider_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(provider_frame, text="Select AI Provider:").pack(anchor=tk.W, pady=(0, 10))
            
            self.config_provider_var = tk.StringVar(value=self.ai_provider_var.get())
            provider_combo = ttk.Combobox(provider_frame, textvariable=self.config_provider_var, 
                                         values=["Ollama", "OpenAI", "Google Gemini", "OpenRouter"], 
                                         state="readonly", width=30)
            provider_combo.pack(fill=tk.X, pady=(0, 10))
            
            # Model selection
            model_frame = ttk.LabelFrame(main_frame, text="Model Configuration", padding="15")
            model_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(model_frame, text="Model:").pack(anchor=tk.W, pady=(0, 5))
            self.config_model_var = tk.StringVar(value="deepseek-r1:8b")
            model_entry = ttk.Entry(model_frame, textvariable=self.config_model_var, width=30)
            model_entry.pack(fill=tk.X, pady=(0, 10))
            
            # API Key (if needed)
            api_frame = ttk.LabelFrame(main_frame, text="API Configuration", padding="15")
            api_frame.pack(fill=tk.X, pady=(0, 15))
            
            ttk.Label(api_frame, text="API Key (if required):").pack(anchor=tk.W, pady=(0, 5))
            self.config_api_key_var = tk.StringVar()
            api_entry = ttk.Entry(api_frame, textvariable=self.config_api_key_var, width=30, show="*")
            api_entry.pack(fill=tk.X, pady=(0, 10))
            
            # Advanced settings
            advanced_frame = ttk.LabelFrame(main_frame, text="Advanced Settings", padding="15")
            advanced_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Temperature
            temp_frame = ttk.Frame(advanced_frame)
            temp_frame.pack(fill=tk.X, pady=(0, 5))
            ttk.Label(temp_frame, text="Temperature:").pack(side=tk.LEFT)
            self.config_temp_var = tk.DoubleVar(value=0.7)
            temp_scale = ttk.Scale(temp_frame, from_=0.0, to=2.0, variable=self.config_temp_var, 
                                  orient=tk.HORIZONTAL, length=200)
            temp_scale.pack(side=tk.RIGHT, padx=(10, 0))
            
            # Max tokens
            tokens_frame = ttk.Frame(advanced_frame)
            tokens_frame.pack(fill=tk.X, pady=(0, 5))
            ttk.Label(tokens_frame, text="Max Tokens:").pack(side=tk.LEFT)
            self.config_tokens_var = tk.IntVar(value=1000)
            tokens_spin = ttk.Spinbox(tokens_frame, from_=100, to=4000, textvariable=self.config_tokens_var, 
                                     width=10)
            tokens_spin.pack(side=tk.RIGHT, padx=(10, 0))
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(button_frame, text="Test Connection", 
                      command=self.test_ai_connection).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(button_frame, text="Save", 
                      command=lambda: self.save_ai_config(config_window)).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(button_frame, text="Cancel", 
                      command=config_window.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open AI configuration: {e}")
    
    def test_ai_connection(self):
        """AI bağlantısını test et"""
        try:
            provider = self.config_provider_var.get()
            model = self.config_model_var.get()
            
            messagebox.showinfo("Info", f"Testing connection to {provider} with model {model}...")
            
            # Test connection using a simple approach
            def test_sync():
                try:
                    if self.jarvis_core and hasattr(self.jarvis_core, 'ai_manager'):
                        # Test if AI manager is initialized
                        ai_manager = self.jarvis_core.ai_manager
                        if hasattr(ai_manager, 'get_current_provider'):
                            current_provider = ai_manager.get_current_provider()
                            if current_provider:
                                self.root.after(0, lambda: messagebox.showinfo("Success", f"AI connection test successful! Provider: {current_provider.provider_type.value}"))
                            else:
                                self.root.after(0, lambda: messagebox.showerror("Error", "No AI provider available"))
                        else:
                            self.root.after(0, lambda: messagebox.showerror("Error", "AI Manager not properly initialized"))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", "AI Manager not available"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"AI connection test failed: {e}"))
            
            thread = threading.Thread(target=test_sync, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test AI connection: {e}")
    
    def save_ai_config(self, window):
        """AI yapılandırmasını kaydet"""
        try:
            # Settings'i güncelle
            if self.settings_manager:
                self.settings_manager.ai.provider = self.config_provider_var.get().lower()
                self.settings_manager.ai.model = self.config_model_var.get()
                self.settings_manager.ai.temperature = self.config_temp_var.get()
                self.settings_manager.ai.max_tokens = self.config_tokens_var.get()
                
                if self.config_api_key_var.get():
                    self.settings_manager.ai.api_key = self.config_api_key_var.get()
                
                # Kaydet
                self.settings_manager.save_settings()
                
                # UI'yi güncelle
                self.ai_provider_var.set(self.config_provider_var.get())
                
                messagebox.showinfo("Success", "AI configuration saved successfully!")
                window.destroy()
            else:
                messagebox.showerror("Error", "Settings manager not available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save AI configuration: {e}")
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            # Settings'i güncelle
            if self.settings_manager:
                # General settings
                self.settings_manager.general.language = self.language_var.get()
                self.settings_manager.general.theme = self.theme_var.get()
                
                # Voice settings
                self.settings_manager.voice.engine = self.voice_engine_var.get()
                
                # AI settings
                self.settings_manager.ai.provider = self.ai_provider_setting_var.get()
                
                # Remote settings
                self.settings_manager.remote.host = self.host_var.get()
                self.settings_manager.remote.port = int(self.port_var.get())
                
                # Kaydet
                self.settings_manager.save_settings()
                
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                messagebox.showerror("Error", "Settings manager not available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def refresh_system_status(self):
        """Sistem durumunu yenile"""
        self.update_system_info()
        self.update_status()
        messagebox.showinfo("Info", "System status refreshed!")
    
    def view_logs(self):
        """Log'ları görüntüle"""
        # Open log viewer
        try:
            log_window = tk.Toplevel(self.root)
            log_window.title("JARVIS Log Viewer")
            log_window.geometry("800x600")
            
            # Create text widget for logs
            log_text = scrolledtext.ScrolledText(log_window, wrap=tk.WORD)
            log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Load recent logs
            log_file = "data/debug.log"
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = f.read()
                    log_text.insert(tk.END, logs)
            else:
                log_text.insert(tk.END, "No log file found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log viewer: {e}")
    
    def show_help(self):
        """Yardım göster"""
        help_text = """
JARVIS Computer Assistant Help

Quick Start:
1. JARVIS automatically starts when you open the application
2. Use the Dashboard tab for quick actions
3. Test voice commands in the Voice tab
4. Chat with AI in the AI tab
5. Run commands in the Terminal tab
6. Configure settings in the Settings tab

Features:
• Voice Recognition: Enhanced noise reduction + VAD
• AI Integration: Multiple providers + RAG
• Terminal Control: Cross-platform commands
• System Monitoring: Real-time status
• Remote Control: WebSocket + Mobile app
• Plugin System: Extensible architecture

For more help, check the documentation.
        """
        messagebox.showinfo("Help", help_text)
    
    def open_performance_monitor(self):
        """Performance monitor'u aç"""
        # Open performance monitor
        try:
            perf_window = tk.Toplevel(self.root)
            perf_window.title("Performance Monitor")
            perf_window.geometry("600x400")
            
            # Create text widget for performance data
            perf_text = scrolledtext.ScrolledText(perf_window, wrap=tk.WORD)
            perf_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Get performance data
            if self.jarvis_core and hasattr(self.jarvis_core, 'performance_manager'):
                perf_data = self.jarvis_core.performance_manager.get_performance_metrics()
                perf_text.insert(tk.END, f"Performance Metrics:\n{perf_data}")
            else:
                perf_text.insert(tk.END, "Performance manager not available.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open performance monitor: {e}")
    
    def open_security_status(self):
        """Security status'u aç"""
        # Open security status
        try:
            security_window = tk.Toplevel(self.root)
            security_window.title("Security Status")
            security_window.geometry("600x400")
            
            # Create text widget for security data
            security_text = scrolledtext.ScrolledText(security_window, wrap=tk.WORD)
            security_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Get security data
            if self.jarvis_core and hasattr(self.jarvis_core, 'security_manager'):
                security_data = self.jarvis_core.security_manager.get_security_status()
                security_text.insert(tk.END, f"Security Status:\n{security_data}")
            else:
                security_text.insert(tk.END, "Security manager not available.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open security status: {e}")
    
    def refresh_all(self):
        """Her şeyi yenile"""
        self.update_status()
        self.update_system_info()
        messagebox.showinfo("Info", "All data refreshed!")
    
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
    app = JARVISUnifiedWindow()
    app.run()

if __name__ == "__main__":
    main()
