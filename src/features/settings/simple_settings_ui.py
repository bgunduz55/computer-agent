"""
Simple Settings UI for JARVIS Computer Assistant

A clean, working settings UI that actually saves and loads values.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict, Any
from .simple_settings_manager import get_simple_settings_manager, SimpleSettingsManager

logger = logging.getLogger(__name__)

class SimpleSettingsUI:
    """Simple settings UI that actually works"""
    
    def __init__(self, parent=None):
        self.settings_manager = get_simple_settings_manager()
        self.variables = {}
        self.window = None
        self.parent = parent
        
    def show_settings(self):
        """Show settings window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("JARVIS Settings - Simple")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        
        # Center window
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self._create_ui()
        self._load_settings()
        
        # Center on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
    def _create_ui(self):
        """Create the UI"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_ai_tab()
        self._create_voice_tab()
        self._create_system_tab()
        self._create_remote_tab()
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Reset", command=self._reset_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self._close_settings).pack(side=tk.RIGHT)
        
    def _create_ai_tab(self):
        """Create AI settings tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="AI")
        
        # Default Provider
        ttk.Label(frame, text="Default Provider:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['ai.default_provider'] = tk.StringVar()
        provider_combo = ttk.Combobox(frame, textvariable=self.variables['ai.default_provider'],
                                    values=['ollama', 'openai', 'gemini', 'openrouter', 'anthropic'], 
                                    state='readonly')
        provider_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Default Model
        ttk.Label(frame, text="Default Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['ai.default_model'] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.variables['ai.default_model']).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Max Tokens
        ttk.Label(frame, text="Max Tokens:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['ai.max_tokens'] = tk.IntVar()
        ttk.Spinbox(frame, textvariable=self.variables['ai.max_tokens'], from_=100, to=4000).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Temperature
        ttk.Label(frame, text="Temperature:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['ai.temperature'] = tk.DoubleVar()
        ttk.Scale(frame, from_=0.0, to=2.0, variable=self.variables['ai.temperature'], 
                 orient=tk.HORIZONTAL).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Enable RAG
        self.variables['ai.enable_rag'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable RAG", variable=self.variables['ai.enable_rag']).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Separator
        ttk.Separator(frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        # API Keys section
        ttk.Label(frame, text="API Keys", font=('Arial', 12, 'bold')).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # OpenAI API Key
        ttk.Label(frame, text="OpenAI API Key:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.variables['ai.openai_api_key'] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.variables['ai.openai_api_key'], show="*").grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Gemini API Key
        ttk.Label(frame, text="Gemini API Key:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.variables['ai.gemini_api_key'] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.variables['ai.gemini_api_key'], show="*").grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # OpenRouter API Key
        ttk.Label(frame, text="OpenRouter API Key:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.variables['ai.openrouter_api_key'] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.variables['ai.openrouter_api_key'], show="*").grid(row=9, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Anthropic API Key
        ttk.Label(frame, text="Anthropic API Key:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.variables['ai.anthropic_api_key'] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.variables['ai.anthropic_api_key'], show="*").grid(row=10, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Separator
        ttk.Separator(frame, orient='horizontal').grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        # Provider Settings section
        ttk.Label(frame, text="Provider Settings", font=('Arial', 12, 'bold')).grid(row=12, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Provider checkboxes
        self.variables['ai.openai_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable OpenAI", variable=self.variables['ai.openai_enabled']).grid(row=13, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.variables['ai.gemini_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable Gemini", variable=self.variables['ai.gemini_enabled']).grid(row=14, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.variables['ai.openrouter_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable OpenRouter", variable=self.variables['ai.openrouter_enabled']).grid(row=15, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.variables['ai.anthropic_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable Anthropic", variable=self.variables['ai.anthropic_enabled']).grid(row=16, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.variables['ai.ollama_enabled'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Enable Ollama (Local)", variable=self.variables['ai.ollama_enabled']).grid(row=17, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        
    def _create_voice_tab(self):
        """Create voice settings tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Voice")
        
        # Voice Engine
        ttk.Label(frame, text="Voice Engine:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['voice.engine'] = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.variables['voice.engine'],
                    values=['google', 'sphinx', 'azure'], state='readonly').grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Language
        ttk.Label(frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['voice.language'] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.variables['voice.language']).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Wake Word
        ttk.Label(frame, text="Wake Word:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['voice.wake_word'] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.variables['voice.wake_word']).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Confidence Threshold
        ttk.Label(frame, text="Confidence Threshold:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['voice.confidence_threshold'] = tk.DoubleVar()
        ttk.Scale(frame, from_=0.0, to=1.0, variable=self.variables['voice.confidence_threshold'], 
                 orient=tk.HORIZONTAL).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Auto Listen
        self.variables['voice.auto_listen'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Auto Listen on Start", variable=self.variables['voice.auto_listen']).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        
    def _create_system_tab(self):
        """Create system settings tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="System")
        
        # Auto Start
        self.variables['system.auto_start'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Auto Start with Windows", variable=self.variables['system.auto_start']).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Minimize to Tray
        self.variables['system.minimize_to_tray'] = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Minimize to System Tray", variable=self.variables['system.minimize_to_tray']).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Log Level
        ttk.Label(frame, text="Log Level:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['system.log_level'] = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.variables['system.log_level'],
                    values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], state='readonly').grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        
    def _create_remote_tab(self):
        """Create remote settings tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Remote")
        
        # WebSocket Host
        ttk.Label(frame, text="WebSocket Host:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['remote.websocket_host'] = tk.StringVar()
        ttk.Entry(frame, textvariable=self.variables['remote.websocket_host']).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # WebSocket Port
        ttk.Label(frame, text="WebSocket Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['remote.websocket_port'] = tk.IntVar()
        ttk.Spinbox(frame, textvariable=self.variables['remote.websocket_port'], from_=1000, to=65535).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        
    def _load_settings(self):
        """Load settings into UI"""
        try:
            logger.info("Loading settings into UI...")
            
            # Load AI settings
            self.variables['ai.default_provider'].set(self.settings_manager.get_setting('ai', 'default_provider', 'ollama'))
            self.variables['ai.default_model'].set(self.settings_manager.get_setting('ai', 'default_model', 'llama2'))
            self.variables['ai.max_tokens'].set(self.settings_manager.get_setting('ai', 'max_tokens', 1000))
            self.variables['ai.temperature'].set(self.settings_manager.get_setting('ai', 'temperature', 0.7))
            self.variables['ai.enable_rag'].set(self.settings_manager.get_setting('ai', 'enable_rag', True))
            
            # Load API keys
            self.variables['ai.openai_api_key'].set(self.settings_manager.get_setting('ai', 'openai_api_key', ''))
            self.variables['ai.gemini_api_key'].set(self.settings_manager.get_setting('ai', 'gemini_api_key', ''))
            self.variables['ai.openrouter_api_key'].set(self.settings_manager.get_setting('ai', 'openrouter_api_key', ''))
            self.variables['ai.anthropic_api_key'].set(self.settings_manager.get_setting('ai', 'anthropic_api_key', ''))
            
            # Load provider settings
            self.variables['ai.openai_enabled'].set(self.settings_manager.get_setting('ai', 'openai_enabled', False))
            self.variables['ai.gemini_enabled'].set(self.settings_manager.get_setting('ai', 'gemini_enabled', False))
            self.variables['ai.openrouter_enabled'].set(self.settings_manager.get_setting('ai', 'openrouter_enabled', False))
            self.variables['ai.anthropic_enabled'].set(self.settings_manager.get_setting('ai', 'anthropic_enabled', False))
            self.variables['ai.ollama_enabled'].set(self.settings_manager.get_setting('ai', 'ollama_enabled', True))
            
            # Load voice settings
            self.variables['voice.engine'].set(self.settings_manager.get_setting('voice', 'engine', 'google'))
            self.variables['voice.language'].set(self.settings_manager.get_setting('voice', 'language', 'en-US'))
            self.variables['voice.wake_word'].set(self.settings_manager.get_setting('voice', 'wake_word', 'hey jarvis'))
            self.variables['voice.confidence_threshold'].set(self.settings_manager.get_setting('voice', 'confidence_threshold', 0.7))
            self.variables['voice.auto_listen'].set(self.settings_manager.get_setting('voice', 'auto_listen', False))
            
            # Load system settings
            self.variables['system.auto_start'].set(self.settings_manager.get_setting('system', 'auto_start', False))
            self.variables['system.minimize_to_tray'].set(self.settings_manager.get_setting('system', 'minimize_to_tray', True))
            self.variables['system.log_level'].set(self.settings_manager.get_setting('system', 'log_level', 'INFO'))
            
            # Load remote settings
            self.variables['remote.websocket_host'].set(self.settings_manager.get_setting('remote', 'websocket_host', '0.0.0.0'))
            self.variables['remote.websocket_port'].set(self.settings_manager.get_setting('remote', 'websocket_port', 8765))
            
            logger.info("Settings loaded successfully into UI")
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            messagebox.showerror("Error", f"Error loading settings: {e}")
    
    def _save_settings(self):
        """Save settings from UI"""
        try:
            logger.info("Saving settings from UI...")
            
            # Save AI settings
            self.settings_manager.set_setting('ai', 'default_provider', self.variables['ai.default_provider'].get())
            self.settings_manager.set_setting('ai', 'default_model', self.variables['ai.default_model'].get())
            self.settings_manager.set_setting('ai', 'max_tokens', self.variables['ai.max_tokens'].get())
            self.settings_manager.set_setting('ai', 'temperature', self.variables['ai.temperature'].get())
            self.settings_manager.set_setting('ai', 'enable_rag', self.variables['ai.enable_rag'].get())
            
            # Save API keys
            self.settings_manager.set_setting('ai', 'openai_api_key', self.variables['ai.openai_api_key'].get())
            self.settings_manager.set_setting('ai', 'gemini_api_key', self.variables['ai.gemini_api_key'].get())
            self.settings_manager.set_setting('ai', 'openrouter_api_key', self.variables['ai.openrouter_api_key'].get())
            self.settings_manager.set_setting('ai', 'anthropic_api_key', self.variables['ai.anthropic_api_key'].get())
            
            # Save provider settings
            self.settings_manager.set_setting('ai', 'openai_enabled', self.variables['ai.openai_enabled'].get())
            self.settings_manager.set_setting('ai', 'gemini_enabled', self.variables['ai.gemini_enabled'].get())
            self.settings_manager.set_setting('ai', 'openrouter_enabled', self.variables['ai.openrouter_enabled'].get())
            self.settings_manager.set_setting('ai', 'anthropic_enabled', self.variables['ai.anthropic_enabled'].get())
            self.settings_manager.set_setting('ai', 'ollama_enabled', self.variables['ai.ollama_enabled'].get())
            
            # Save voice settings
            self.settings_manager.set_setting('voice', 'engine', self.variables['voice.engine'].get())
            self.settings_manager.set_setting('voice', 'language', self.variables['voice.language'].get())
            self.settings_manager.set_setting('voice', 'wake_word', self.variables['voice.wake_word'].get())
            self.settings_manager.set_setting('voice', 'confidence_threshold', self.variables['voice.confidence_threshold'].get())
            self.settings_manager.set_setting('voice', 'auto_listen', self.variables['voice.auto_listen'].get())
            
            # Save system settings
            self.settings_manager.set_setting('system', 'auto_start', self.variables['system.auto_start'].get())
            self.settings_manager.set_setting('system', 'minimize_to_tray', self.variables['system.minimize_to_tray'].get())
            self.settings_manager.set_setting('system', 'log_level', self.variables['system.log_level'].get())
            
            # Save remote settings
            self.settings_manager.set_setting('remote', 'websocket_host', self.variables['remote.websocket_host'].get())
            self.settings_manager.set_setting('remote', 'websocket_port', self.variables['remote.websocket_port'].get())
            
            # Save to file
            if self.settings_manager.save_settings():
                logger.info("Settings saved successfully")
                messagebox.showinfo("Success", "Settings saved successfully!")
            else:
                logger.error("Failed to save settings")
                messagebox.showerror("Error", "Failed to save settings!")
                
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Error saving settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        try:
            if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
                self.settings_manager.reset_to_defaults()
                self._load_settings()
                messagebox.showinfo("Success", "Settings reset to defaults!")
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            messagebox.showerror("Error", f"Error resetting settings: {e}")
    
    def _close_settings(self):
        """Close settings window"""
        if self.window:
            self.window.destroy()
            self.window = None



