"""
Settings UI for JARVIS Computer Assistant

This module provides a comprehensive settings interface for managing
all aspects of the JARVIS assistant configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import logging

from .settings_manager import SettingsManager, SettingCategory, get_settings_manager

logger = logging.getLogger(__name__)

class SettingsUI:
    """Comprehensive settings UI"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.settings_manager = get_settings_manager()
        self.root = None
        self.variables = {}
        self.callbacks = {}
        
        # Create UI
        self._create_ui()
        
        # Load settings
        self._load_settings()
        
        # Add settings change listener
        self.settings_manager.add_listener('setting_changed', self._on_setting_changed)
    
    def _create_ui(self):
        """Create the settings UI"""
        if self.parent:
            self.root = tk.Toplevel(self.parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("JARVIS Settings")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create tabs
        self._create_general_page()
        self._create_voice_page()
        self._create_ai_page()
        self._create_system_page()
        self._create_security_page()
        self._create_remote_page()
        self._create_performance_page()
        self._create_notifications_page()
        
        # Create buttons
        self._create_buttons(main_frame)
        
        # Create status bar
        self._create_status_bar(main_frame)
    
    def _create_general_page(self):
        """Create general settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="General")
        
        # Theme
        ttk.Label(frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['general.theme'] = tk.StringVar(value=self.settings_manager.general.theme)
        theme_combo = ttk.Combobox(frame, textvariable=self.variables['general.theme'],
                                 values=['light', 'dark', 'auto'], state='readonly')
        theme_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Language
        ttk.Label(frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['general.language'] = tk.StringVar(value=self.settings_manager.general.language)
        lang_combo = ttk.Combobox(frame, textvariable=self.variables['general.language'],
                                values=['en', 'tr', 'es', 'fr', 'de'], state='readonly')
        lang_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Timezone
        ttk.Label(frame, text="Timezone:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['general.timezone'] = tk.StringVar(value=self.settings_manager.general.timezone)
        tz_entry = ttk.Entry(frame, textvariable=self.variables['general.timezone'])
        tz_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Analytics
        self.variables['general.analytics_enabled'] = tk.BooleanVar(value=self.settings_manager.general.analytics_enabled)
        ttk.Checkbutton(frame, text="Enable Analytics", 
                       variable=self.variables['general.analytics_enabled']).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Crash Reporting
        self.variables['general.crash_reporting'] = tk.BooleanVar(value=self.settings_manager.general.crash_reporting)
        ttk.Checkbutton(frame, text="Enable Crash Reporting", 
                       variable=self.variables['general.crash_reporting']).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_voice_page(self):
        """Create voice settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Voice")
        
        # Engine
        ttk.Label(frame, text="Voice Engine:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['voice.engine'] = tk.StringVar(value=self.settings_manager.voice.engine)
        engine_combo = ttk.Combobox(frame, textvariable=self.variables['voice.engine'],
                                  values=['google', 'sphinx', 'azure'], state='readonly')
        engine_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Language
        ttk.Label(frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['voice.language'] = tk.StringVar(value=self.settings_manager.voice.language)
        lang_combo = ttk.Combobox(frame, textvariable=self.variables['voice.language'],
                                values=['en-US', 'tr-TR', 'es-ES', 'fr-FR'], state='readonly')
        lang_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Wake Word
        ttk.Label(frame, text="Wake Word:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['voice.wake_word'] = tk.StringVar(value=self.settings_manager.voice.wake_word)
        wake_entry = ttk.Entry(frame, textvariable=self.variables['voice.wake_word'])
        wake_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Confidence Threshold
        ttk.Label(frame, text="Confidence Threshold:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['voice.confidence_threshold'] = tk.DoubleVar(value=self.settings_manager.voice.confidence_threshold)
        conf_scale = ttk.Scale(frame, from_=0.0, to=1.0, variable=self.variables['voice.confidence_threshold'],
                              orient=tk.HORIZONTAL)
        conf_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Auto Listen
        self.variables['voice.auto_listen'] = tk.BooleanVar(value=self.settings_manager.voice.auto_listen)
        ttk.Checkbutton(frame, text="Auto Listen on Start", 
                       variable=self.variables['voice.auto_listen']).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_ai_page(self):
        """Create AI settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="AI")
        
        # Default Provider
        ttk.Label(frame, text="Default Provider:").grid(row=0, column=0, sticky=tk.W, pady=5)
        default_provider = getattr(self.settings_manager.ai, 'default_provider', 'ollama')
        self.variables['ai.default_provider'] = tk.StringVar(value=default_provider)
        provider_combo = ttk.Combobox(frame, textvariable=self.variables['ai.default_provider'],
                                    values=['ollama', 'openai', 'gemini', 'openrouter', 'anthropic'], state='readonly')
        provider_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Default Model
        ttk.Label(frame, text="Default Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        default_model = getattr(self.settings_manager.ai, 'default_model', 'llama2')
        self.variables['ai.default_model'] = tk.StringVar(value=default_model)
        model_entry = ttk.Entry(frame, textvariable=self.variables['ai.default_model'])
        model_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Max Tokens
        ttk.Label(frame, text="Max Tokens:").grid(row=2, column=0, sticky=tk.W, pady=5)
        max_tokens = getattr(self.settings_manager.ai, 'max_tokens', 1000)
        self.variables['ai.max_tokens'] = tk.IntVar(value=max_tokens)
        tokens_spin = ttk.Spinbox(frame, from_=100, to=4000, textvariable=self.variables['ai.max_tokens'])
        tokens_spin.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Temperature
        ttk.Label(frame, text="Temperature:").grid(row=3, column=0, sticky=tk.W, pady=5)
        temperature = getattr(self.settings_manager.ai, 'temperature', 0.7)
        self.variables['ai.temperature'] = tk.DoubleVar(value=temperature)
        temp_scale = ttk.Scale(frame, from_=0.0, to=2.0, variable=self.variables['ai.temperature'],
                              orient=tk.HORIZONTAL)
        temp_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # RAG Enabled
        rag_enabled = getattr(self.settings_manager.ai, 'rag_enabled', True)
        self.variables['ai.rag_enabled'] = tk.BooleanVar(value=rag_enabled)
        ttk.Checkbutton(frame, text="Enable RAG", 
                       variable=self.variables['ai.rag_enabled']).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # API Keys Section
        ttk.Separator(frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        ttk.Label(frame, text="API Keys", font=('Arial', 12, 'bold')).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # OpenAI API Key
        ttk.Label(frame, text="OpenAI API Key:").grid(row=7, column=0, sticky=tk.W, pady=5)
        openai_key = getattr(self.settings_manager.ai, 'openai_api_key', '')
        self.variables['ai.openai_api_key'] = tk.StringVar(value=openai_key)
        openai_entry = ttk.Entry(frame, textvariable=self.variables['ai.openai_api_key'], show="*")
        openai_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Gemini API Key
        ttk.Label(frame, text="Gemini API Key:").grid(row=8, column=0, sticky=tk.W, pady=5)
        gemini_key = getattr(self.settings_manager.ai, 'gemini_api_key', '')
        self.variables['ai.gemini_api_key'] = tk.StringVar(value=gemini_key)
        gemini_entry = ttk.Entry(frame, textvariable=self.variables['ai.gemini_api_key'], show="*")
        gemini_entry.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # OpenRouter API Key
        ttk.Label(frame, text="OpenRouter API Key:").grid(row=9, column=0, sticky=tk.W, pady=5)
        openrouter_key = getattr(self.settings_manager.ai, 'openrouter_api_key', '')
        self.variables['ai.openrouter_api_key'] = tk.StringVar(value=openrouter_key)
        openrouter_entry = ttk.Entry(frame, textvariable=self.variables['ai.openrouter_api_key'], show="*")
        openrouter_entry.grid(row=9, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Anthropic API Key
        ttk.Label(frame, text="Anthropic API Key:").grid(row=10, column=0, sticky=tk.W, pady=5)
        anthropic_key = getattr(self.settings_manager.ai, 'anthropic_api_key', '')
        self.variables['ai.anthropic_api_key'] = tk.StringVar(value=anthropic_key)
        anthropic_entry = ttk.Entry(frame, textvariable=self.variables['ai.anthropic_api_key'], show="*")
        anthropic_entry.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Provider Settings Section
        ttk.Separator(frame, orient='horizontal').grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        ttk.Label(frame, text="Provider Settings", font=('Arial', 12, 'bold')).grid(row=12, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Provider Enable/Disable
        openai_enabled = getattr(self.settings_manager.ai, 'openai_enabled', False)
        self.variables['ai.openai_enabled'] = tk.BooleanVar(value=openai_enabled)
        ttk.Checkbutton(frame, text="Enable OpenAI", 
                       variable=self.variables['ai.openai_enabled']).grid(row=13, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        gemini_enabled = getattr(self.settings_manager.ai, 'gemini_enabled', False)
        self.variables['ai.gemini_enabled'] = tk.BooleanVar(value=gemini_enabled)
        ttk.Checkbutton(frame, text="Enable Gemini", 
                       variable=self.variables['ai.gemini_enabled']).grid(row=14, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        openrouter_enabled = getattr(self.settings_manager.ai, 'openrouter_enabled', False)
        self.variables['ai.openrouter_enabled'] = tk.BooleanVar(value=openrouter_enabled)
        ttk.Checkbutton(frame, text="Enable OpenRouter", 
                       variable=self.variables['ai.openrouter_enabled']).grid(row=15, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        anthropic_enabled = getattr(self.settings_manager.ai, 'anthropic_enabled', False)
        self.variables['ai.anthropic_enabled'] = tk.BooleanVar(value=anthropic_enabled)
        ttk.Checkbutton(frame, text="Enable Anthropic", 
                       variable=self.variables['ai.anthropic_enabled']).grid(row=16, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ollama_enabled = getattr(self.settings_manager.ai, 'ollama_enabled', True)
        self.variables['ai.ollama_enabled'] = tk.BooleanVar(value=ollama_enabled)
        ttk.Checkbutton(frame, text="Enable Ollama (Local)", 
                       variable=self.variables['ai.ollama_enabled']).grid(row=17, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_system_page(self):
        """Create system settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="System")
        
        # Auto Start
        self.variables['system.auto_start'] = tk.BooleanVar(value=self.settings_manager.system.auto_start)
        ttk.Checkbutton(frame, text="Auto Start", 
                       variable=self.variables['system.auto_start']).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Minimize to Tray
        self.variables['system.minimize_to_tray'] = tk.BooleanVar(value=self.settings_manager.system.minimize_to_tray)
        ttk.Checkbutton(frame, text="Minimize to Tray", 
                       variable=self.variables['system.minimize_to_tray']).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Log Level
        ttk.Label(frame, text="Log Level:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['system.log_level'] = tk.StringVar(value=self.settings_manager.system.log_level)
        log_combo = ttk.Combobox(frame, textvariable=self.variables['system.log_level'],
                               values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], state='readonly')
        log_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_security_page(self):
        """Create security settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Security")
        
        # Encryption Enabled
        self.variables['security.encryption_enabled'] = tk.BooleanVar(value=self.settings_manager.security.encryption_enabled)
        ttk.Checkbutton(frame, text="Enable Encryption", 
                       variable=self.variables['security.encryption_enabled']).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Require Authentication
        self.variables['security.require_authentication'] = tk.BooleanVar(value=self.settings_manager.security.require_authentication)
        ttk.Checkbutton(frame, text="Require Authentication", 
                       variable=self.variables['security.require_authentication']).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Session Timeout
        ttk.Label(frame, text="Session Timeout (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['security.session_timeout'] = tk.IntVar(value=self.settings_manager.security.session_timeout)
        timeout_spin = ttk.Spinbox(frame, from_=60, to=86400, textvariable=self.variables['security.session_timeout'])
        timeout_spin.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_remote_page(self):
        """Create remote settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Remote")
        
        # WebSocket Enabled
        self.variables['remote.websocket_enabled'] = tk.BooleanVar(value=self.settings_manager.remote.websocket_enabled)
        ttk.Checkbutton(frame, text="Enable WebSocket Server", 
                       variable=self.variables['remote.websocket_enabled']).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # WebSocket Port
        ttk.Label(frame, text="WebSocket Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['remote.websocket_port'] = tk.IntVar(value=self.settings_manager.remote.websocket_port)
        port_spin = ttk.Spinbox(frame, from_=1024, to=65535, textvariable=self.variables['remote.websocket_port'])
        port_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Allow Remote Control
        self.variables['remote.allow_remote_control'] = tk.BooleanVar(value=self.settings_manager.remote.allow_remote_control)
        ttk.Checkbutton(frame, text="Allow Remote Control", 
                       variable=self.variables['remote.allow_remote_control']).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_performance_page(self):
        """Create performance settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Performance")
        
        # Max Memory Usage
        ttk.Label(frame, text="Max Memory Usage (MB):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['performance.max_memory_usage'] = tk.IntVar(value=self.settings_manager.performance.max_memory_usage)
        memory_spin = ttk.Spinbox(frame, from_=256, to=8192, textvariable=self.variables['performance.max_memory_usage'])
        memory_spin.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Max CPU Usage
        ttk.Label(frame, text="Max CPU Usage (%):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['performance.max_cpu_usage'] = tk.DoubleVar(value=self.settings_manager.performance.max_cpu_usage)
        cpu_scale = ttk.Scale(frame, from_=10.0, to=100.0, variable=self.variables['performance.max_cpu_usage'],
                             orient=tk.HORIZONTAL)
        cpu_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Metrics Collection
        self.variables['performance.metrics_collection'] = tk.BooleanVar(value=self.settings_manager.performance.metrics_collection)
        ttk.Checkbutton(frame, text="Enable Metrics Collection", 
                       variable=self.variables['performance.metrics_collection']).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_notifications_page(self):
        """Create notifications settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Notifications")
        
        # Notifications Enabled
        self.variables['notifications.enabled'] = tk.BooleanVar(value=self.settings_manager.notifications.enabled)
        ttk.Checkbutton(frame, text="Enable Notifications", 
                       variable=self.variables['notifications.enabled']).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Sound Enabled
        self.variables['notifications.sound_enabled'] = tk.BooleanVar(value=self.settings_manager.notifications.sound_enabled)
        ttk.Checkbutton(frame, text="Enable Sound", 
                       variable=self.variables['notifications.sound_enabled']).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Desktop Notifications
        self.variables['notifications.desktop_notifications'] = tk.BooleanVar(value=self.settings_manager.notifications.desktop_notifications)
        ttk.Checkbutton(frame, text="Desktop Notifications", 
                       variable=self.variables['notifications.desktop_notifications']).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Notification Sound
        ttk.Label(frame, text="Notification Sound:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['notifications.notification_sound'] = tk.StringVar(value=self.settings_manager.notifications.notification_sound)
        sound_combo = ttk.Combobox(frame, textvariable=self.variables['notifications.notification_sound'],
                                 values=['default', 'chime', 'beep', 'ding'], state='readonly')
        sound_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_buttons(self, parent):
        """Create control buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Save button
        save_btn = ttk.Button(button_frame, text="Save", command=self._save_settings)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset button
        reset_btn = ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_settings)
        reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        export_btn = ttk.Button(button_frame, text="Export", command=self._export_settings)
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Import button
        import_btn = ttk.Button(button_frame, text="Import", command=self._import_settings)
        import_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(button_frame, text="Close", command=self._close_settings)
        close_btn.pack(side=tk.RIGHT)
    
    def _create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Last saved time
        self.last_saved_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.last_saved_var).pack(side=tk.RIGHT)
    
    def _load_settings(self):
        """Load settings into UI variables"""
        try:
            logger.info("Loading settings into UI...")
            
            # Load general settings
            self.variables['general.theme'].set(self.settings_manager.general.theme)
            self.variables['general.language'].set(self.settings_manager.general.language)
            self.variables['general.timezone'].set(self.settings_manager.general.timezone)
            self.variables['general.analytics_enabled'].set(self.settings_manager.general.analytics_enabled)
            self.variables['general.crash_reporting'].set(self.settings_manager.general.crash_reporting)
            
            # Load voice settings
            self.variables['voice.engine'].set(self.settings_manager.voice.engine)
            self.variables['voice.language'].set(self.settings_manager.voice.language)
            self.variables['voice.wake_word'].set(self.settings_manager.voice.wake_word)
            self.variables['voice.confidence_threshold'].set(self.settings_manager.voice.confidence_threshold)
            self.variables['voice.auto_listen'].set(self.settings_manager.voice.auto_listen)
            
            # Load AI settings
            default_provider = getattr(self.settings_manager.ai, 'default_provider', 'ollama')
            self.variables['ai.default_provider'].set(default_provider)
            
            default_model = getattr(self.settings_manager.ai, 'default_model', 'llama2')
            self.variables['ai.default_model'].set(default_model)
            
            max_tokens = getattr(self.settings_manager.ai, 'max_tokens', 1000)
            self.variables['ai.max_tokens'].set(max_tokens)
            
            temperature = getattr(self.settings_manager.ai, 'temperature', 0.7)
            self.variables['ai.temperature'].set(temperature)
            
            rag_enabled = getattr(self.settings_manager.ai, 'rag_enabled', True)
            self.variables['ai.rag_enabled'].set(rag_enabled)
            
            # Load AI API keys
            openai_key = getattr(self.settings_manager.ai, 'openai_api_key', '')
            logger.info(f"Loading AI API keys: openai={openai_key[:10] if openai_key else 'None'}...")
            self.variables['ai.openai_api_key'].set(openai_key)
            
            gemini_key = getattr(self.settings_manager.ai, 'gemini_api_key', '')
            self.variables['ai.gemini_api_key'].set(gemini_key)
            
            openrouter_key = getattr(self.settings_manager.ai, 'openrouter_api_key', '')
            self.variables['ai.openrouter_api_key'].set(openrouter_key)
            
            anthropic_key = getattr(self.settings_manager.ai, 'anthropic_api_key', '')
            self.variables['ai.anthropic_api_key'].set(anthropic_key)
            
            # Load AI provider settings
            openai_enabled = getattr(self.settings_manager.ai, 'openai_enabled', False)
            logger.info(f"Loading AI provider settings: openai_enabled={openai_enabled}")
            self.variables['ai.openai_enabled'].set(openai_enabled)
            
            gemini_enabled = getattr(self.settings_manager.ai, 'gemini_enabled', False)
            self.variables['ai.gemini_enabled'].set(gemini_enabled)
            
            openrouter_enabled = getattr(self.settings_manager.ai, 'openrouter_enabled', False)
            self.variables['ai.openrouter_enabled'].set(openrouter_enabled)
            
            anthropic_enabled = getattr(self.settings_manager.ai, 'anthropic_enabled', False)
            self.variables['ai.anthropic_enabled'].set(anthropic_enabled)
            
            ollama_enabled = getattr(self.settings_manager.ai, 'ollama_enabled', True)
            self.variables['ai.ollama_enabled'].set(ollama_enabled)
            
            # Load system settings
            self.variables['system.auto_start'].set(self.settings_manager.system.auto_start)
            self.variables['system.minimize_to_tray'].set(self.settings_manager.system.minimize_to_tray)
            self.variables['system.log_level'].set(self.settings_manager.system.log_level)
            
            # Load security settings
            self.variables['security.encryption_enabled'].set(self.settings_manager.security.encryption_enabled)
            self.variables['security.require_authentication'].set(self.settings_manager.security.require_authentication)
            self.variables['security.session_timeout'].set(self.settings_manager.security.session_timeout)
            
            # Load remote settings
            self.variables['remote.websocket_enabled'].set(self.settings_manager.remote.websocket_enabled)
            self.variables['remote.websocket_port'].set(self.settings_manager.remote.websocket_port)
            self.variables['remote.allow_remote_control'].set(self.settings_manager.remote.allow_remote_control)
            
            # Load performance settings
            self.variables['performance.max_memory_usage'].set(self.settings_manager.performance.max_memory_usage)
            self.variables['performance.max_cpu_usage'].set(self.settings_manager.performance.max_cpu_usage)
            self.variables['performance.metrics_collection'].set(self.settings_manager.performance.metrics_collection)
            
            # Load notification settings
            self.variables['notifications.enabled'].set(self.settings_manager.notifications.enabled)
            self.variables['notifications.sound_enabled'].set(self.settings_manager.notifications.sound_enabled)
            self.variables['notifications.desktop_notifications'].set(self.settings_manager.notifications.desktop_notifications)
            self.variables['notifications.notification_sound'].set(self.settings_manager.notifications.notification_sound)
            
            self.status_var.set("Settings loaded")
            logger.info("Settings loaded successfully into UI")
            
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self.status_var.set("Error loading settings")
    
    def _save_settings(self):
        """Save settings from UI variables"""
        try:
            # Save general settings
            self.settings_manager.general.theme = self.variables['general.theme'].get()
            self.settings_manager.general.language = self.variables['general.language'].get()
            self.settings_manager.general.timezone = self.variables['general.timezone'].get()
            self.settings_manager.general.analytics_enabled = self.variables['general.analytics_enabled'].get()
            self.settings_manager.general.crash_reporting = self.variables['general.crash_reporting'].get()
            
            # Save voice settings
            self.settings_manager.voice.engine = self.variables['voice.engine'].get()
            self.settings_manager.voice.language = self.variables['voice.language'].get()
            self.settings_manager.voice.wake_word = self.variables['voice.wake_word'].get()
            self.settings_manager.voice.confidence_threshold = self.variables['voice.confidence_threshold'].get()
            self.settings_manager.voice.auto_listen = self.variables['voice.auto_listen'].get()
            
            # Save AI settings
            self.settings_manager.ai.default_provider = self.variables['ai.default_provider'].get()
            self.settings_manager.ai.default_model = self.variables['ai.default_model'].get()
            self.settings_manager.ai.max_tokens = self.variables['ai.max_tokens'].get()
            self.settings_manager.ai.temperature = self.variables['ai.temperature'].get()
            self.settings_manager.ai.rag_enabled = self.variables['ai.rag_enabled'].get()
            
            # Save AI API keys
            self.settings_manager.ai.openai_api_key = self.variables['ai.openai_api_key'].get()
            self.settings_manager.ai.gemini_api_key = self.variables['ai.gemini_api_key'].get()
            self.settings_manager.ai.openrouter_api_key = self.variables['ai.openrouter_api_key'].get()
            self.settings_manager.ai.anthropic_api_key = self.variables['ai.anthropic_api_key'].get()
            
            # Save AI provider settings
            self.settings_manager.ai.openai_enabled = self.variables['ai.openai_enabled'].get()
            self.settings_manager.ai.gemini_enabled = self.variables['ai.gemini_enabled'].get()
            self.settings_manager.ai.openrouter_enabled = self.variables['ai.openrouter_enabled'].get()
            self.settings_manager.ai.anthropic_enabled = self.variables['ai.anthropic_enabled'].get()
            self.settings_manager.ai.ollama_enabled = self.variables['ai.ollama_enabled'].get()
            
            # Save system settings
            self.settings_manager.system.auto_start = self.variables['system.auto_start'].get()
            self.settings_manager.system.minimize_to_tray = self.variables['system.minimize_to_tray'].get()
            self.settings_manager.system.log_level = self.variables['system.log_level'].get()
            
            # Save security settings
            self.settings_manager.security.encryption_enabled = self.variables['security.encryption_enabled'].get()
            self.settings_manager.security.require_authentication = self.variables['security.require_authentication'].get()
            self.settings_manager.security.session_timeout = self.variables['security.session_timeout'].get()
            
            # Save remote settings
            self.settings_manager.remote.websocket_enabled = self.variables['remote.websocket_enabled'].get()
            self.settings_manager.remote.websocket_port = self.variables['remote.websocket_port'].get()
            self.settings_manager.remote.allow_remote_control = self.variables['remote.allow_remote_control'].get()
            
            # Save performance settings
            self.settings_manager.performance.max_memory_usage = self.variables['performance.max_memory_usage'].get()
            self.settings_manager.performance.max_cpu_usage = self.variables['performance.max_cpu_usage'].get()
            self.settings_manager.performance.metrics_collection = self.variables['performance.metrics_collection'].get()
            
            # Save notification settings
            self.settings_manager.notifications.enabled = self.variables['notifications.enabled'].get()
            self.settings_manager.notifications.sound_enabled = self.variables['notifications.sound_enabled'].get()
            self.settings_manager.notifications.desktop_notifications = self.variables['notifications.desktop_notifications'].get()
            self.settings_manager.notifications.notification_sound = self.variables['notifications.notification_sound'].get()
            
            # Save to file
            self.settings_manager.save_settings()
            
            self.status_var.set("Settings saved successfully")
            self.last_saved_var.set(f"Last saved: {time.strftime('%H:%M:%S')}")
            
            logger.info("Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            self.status_var.set("Error saving settings")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.settings_manager.reset_to_defaults()
            self._load_settings()
            self.status_var.set("Settings reset to defaults")
    
    def _export_settings(self):
        """Export settings to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            if self.settings_manager.export_settings(file_path):
                self.status_var.set(f"Settings exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export settings")
    
    def _import_settings(self):
        """Import settings from a file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            if self.settings_manager.import_settings(file_path):
                self._load_settings()
                self.status_var.set(f"Settings imported from {file_path}")
            else:
                messagebox.showerror("Error", "Failed to import settings")
    
    def _close_settings(self):
        """Close settings window"""
        self.root.destroy()
    
    def _on_setting_changed(self, event: str, value: Any):
        """Handle settings changes"""
        logger.info(f"Setting changed: {event} = {value}")
    
    def show(self):
        """Show the settings window"""
        self.root.mainloop()

def show_settings(parent=None):
    """Show settings window"""
    ui = SettingsUI(parent)
    ui.show()
    return ui
