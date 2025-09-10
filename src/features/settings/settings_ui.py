"""
Settings UI for JARVIS Computer Assistant

This module provides a comprehensive settings interface for managing
all aspects of the JARVIS assistant configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
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
        self.notebook = None
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
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create toolbar
        self._create_toolbar(main_frame)
        
        # Create notebook for settings categories
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create settings pages
        self._create_general_page()
        self._create_voice_page()
        self._create_ai_page()
        self._create_system_page()
        self._create_security_page()
        self._create_remote_page()
        self._create_performance_page()
        self._create_notifications_page()
        
        # Create status bar
        self._create_status_bar(main_frame)
    
    def _create_toolbar(self, parent):
        """Create toolbar with action buttons"""
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        ttk.Button(toolbar, text="Save", command=self._save_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Reset", command=self._reset_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Export", command=self._export_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Import", command=self._import_settings).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Search
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Close button
        ttk.Button(toolbar, text="Close", command=self._close).pack(side=tk.RIGHT)
    
    def _create_general_page(self):
        """Create general settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="General")
        
        # Theme
        ttk.Label(frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['general.theme'] = tk.StringVar(value=self.settings_manager.general.theme)
        theme_combo = ttk.Combobox(frame, textvariable=self.variables['general.theme'], 
                                 values=['light', 'dark', 'system'], state='readonly')
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
        
        # Voice Engine
        ttk.Label(frame, text="Voice Engine:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['voice.engine'] = tk.StringVar(value=self.settings_manager.voice.engine)
        engine_combo = ttk.Combobox(frame, textvariable=self.variables['voice.engine'],
                                  values=['google', 'windows', 'linux'], state='readonly')
        engine_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Language
        ttk.Label(frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['voice.language'] = tk.StringVar(value=self.settings_manager.voice.language)
        lang_entry = ttk.Entry(frame, textvariable=self.variables['voice.language'])
        lang_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Wake Word
        ttk.Label(frame, text="Wake Word:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['voice.wake_word'] = tk.StringVar(value=self.settings_manager.voice.wake_word)
        wake_entry = ttk.Entry(frame, textvariable=self.variables['voice.wake_word'])
        wake_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Confidence Threshold
        ttk.Label(frame, text="Confidence Threshold:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['voice.confidence_threshold'] = tk.DoubleVar(value=self.settings_manager.voice.confidence_threshold)
        conf_scale = ttk.Scale(frame, from_=0.1, to=1.0, variable=self.variables['voice.confidence_threshold'],
                              orient=tk.HORIZONTAL)
        conf_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # TTS Engine
        ttk.Label(frame, text="TTS Engine:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.variables['voice.tts_engine'] = tk.StringVar(value=self.settings_manager.voice.tts_engine)
        tts_combo = ttk.Combobox(frame, textvariable=self.variables['voice.tts_engine'],
                               values=['edge', 'sapi5', 'espeak', 'festival'], state='readonly')
        tts_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Auto Listen
        self.variables['voice.auto_listen'] = tk.BooleanVar(value=self.settings_manager.voice.auto_listen)
        ttk.Checkbutton(frame, text="Auto Listen", 
                       variable=self.variables['voice.auto_listen']).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Continuous Listening
        self.variables['voice.continuous_listening'] = tk.BooleanVar(value=self.settings_manager.voice.continuous_listening)
        ttk.Checkbutton(frame, text="Continuous Listening", 
                       variable=self.variables['voice.continuous_listening']).grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_ai_page(self):
        """Create AI settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="AI")
        
        # Default Provider
        ttk.Label(frame, text="Default Provider:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.variables['ai.default_provider'] = tk.StringVar(value=self.settings_manager.ai.default_provider)
        provider_combo = ttk.Combobox(frame, textvariable=self.variables['ai.default_provider'],
                                    values=['ollama', 'openai', 'gemini', 'openrouter'], state='readonly')
        provider_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Default Model
        ttk.Label(frame, text="Default Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['ai.default_model'] = tk.StringVar(value=self.settings_manager.ai.default_model)
        model_entry = ttk.Entry(frame, textvariable=self.variables['ai.default_model'])
        model_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Max Tokens
        ttk.Label(frame, text="Max Tokens:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['ai.max_tokens'] = tk.IntVar(value=self.settings_manager.ai.max_tokens)
        tokens_spin = ttk.Spinbox(frame, from_=100, to=4000, textvariable=self.variables['ai.max_tokens'])
        tokens_spin.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Temperature
        ttk.Label(frame, text="Temperature:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['ai.temperature'] = tk.DoubleVar(value=self.settings_manager.ai.temperature)
        temp_scale = ttk.Scale(frame, from_=0.0, to=2.0, variable=self.variables['ai.temperature'],
                              orient=tk.HORIZONTAL)
        temp_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # RAG Enabled
        self.variables['ai.rag_enabled'] = tk.BooleanVar(value=self.settings_manager.ai.rag_enabled)
        ttk.Checkbutton(frame, text="Enable RAG", 
                       variable=self.variables['ai.rag_enabled']).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Cost Limit
        ttk.Label(frame, text="Cost Limit ($):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.variables['ai.cost_limit'] = tk.DoubleVar(value=self.settings_manager.ai.cost_limit)
        cost_spin = ttk.Spinbox(frame, from_=0.0, to=1000.0, textvariable=self.variables['ai.cost_limit'])
        cost_spin.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
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
        
        # Backup Enabled
        self.variables['system.backup_enabled'] = tk.BooleanVar(value=self.settings_manager.system.backup_enabled)
        ttk.Checkbutton(frame, text="Enable Backups", 
                       variable=self.variables['system.backup_enabled']).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Backup Interval
        ttk.Label(frame, text="Backup Interval (hours):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.variables['system.backup_interval'] = tk.IntVar(value=self.settings_manager.system.backup_interval)
        backup_spin = ttk.Spinbox(frame, from_=1, to=168, textvariable=self.variables['system.backup_interval'])
        backup_spin.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Performance Monitoring
        self.variables['system.performance_monitoring'] = tk.BooleanVar(value=self.settings_manager.system.performance_monitoring)
        ttk.Checkbutton(frame, text="Performance Monitoring", 
                       variable=self.variables['system.performance_monitoring']).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
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
        
        # Max Failed Attempts
        ttk.Label(frame, text="Max Failed Attempts:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['security.max_failed_attempts'] = tk.IntVar(value=self.settings_manager.security.max_failed_attempts)
        attempts_spin = ttk.Spinbox(frame, from_=1, to=10, textvariable=self.variables['security.max_failed_attempts'])
        attempts_spin.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Audit Logging
        self.variables['security.audit_logging'] = tk.BooleanVar(value=self.settings_manager.security.audit_logging)
        ttk.Checkbutton(frame, text="Audit Logging", 
                       variable=self.variables['security.audit_logging']).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_remote_page(self):
        """Create remote control settings page"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Remote")
        
        # WebSocket Enabled
        self.variables['remote.websocket_enabled'] = tk.BooleanVar(value=self.settings_manager.remote.websocket_enabled)
        ttk.Checkbutton(frame, text="Enable WebSocket", 
                       variable=self.variables['remote.websocket_enabled']).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # WebSocket Port
        ttk.Label(frame, text="WebSocket Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.variables['remote.websocket_port'] = tk.IntVar(value=self.settings_manager.remote.websocket_port)
        port_spin = ttk.Spinbox(frame, from_=1024, to=65535, textvariable=self.variables['remote.websocket_port'])
        port_spin.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # WebSocket Host
        ttk.Label(frame, text="WebSocket Host:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['remote.websocket_host'] = tk.StringVar(value=self.settings_manager.remote.websocket_host)
        host_entry = ttk.Entry(frame, textvariable=self.variables['remote.websocket_host'])
        host_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Allow Remote Control
        self.variables['remote.allow_remote_control'] = tk.BooleanVar(value=self.settings_manager.remote.allow_remote_control)
        ttk.Checkbutton(frame, text="Allow Remote Control", 
                       variable=self.variables['remote.allow_remote_control']).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Max Connections
        ttk.Label(frame, text="Max Connections:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.variables['remote.max_connections'] = tk.IntVar(value=self.settings_manager.remote.max_connections)
        conn_spin = ttk.Spinbox(frame, from_=1, to=100, textvariable=self.variables['remote.max_connections'])
        conn_spin.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
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
        
        # Cache Size
        ttk.Label(frame, text="Cache Size (MB):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variables['performance.cache_size'] = tk.IntVar(value=self.settings_manager.performance.cache_size)
        cache_spin = ttk.Spinbox(frame, from_=64, to=2048, textvariable=self.variables['performance.cache_size'])
        cache_spin.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Thread Pool Size
        ttk.Label(frame, text="Thread Pool Size:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variables['performance.thread_pool_size'] = tk.IntVar(value=self.settings_manager.performance.thread_pool_size)
        thread_spin = ttk.Spinbox(frame, from_=1, to=50, textvariable=self.variables['performance.thread_pool_size'])
        thread_spin.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Metrics Collection
        self.variables['performance.metrics_collection'] = tk.BooleanVar(value=self.settings_manager.performance.metrics_collection)
        ttk.Checkbutton(frame, text="Enable Metrics Collection", 
                       variable=self.variables['performance.metrics_collection']).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
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
        
        # Quiet Hours Start
        ttk.Label(frame, text="Quiet Hours Start:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.variables['notifications.quiet_hours_start'] = tk.StringVar(value=self.settings_manager.notifications.quiet_hours_start)
        quiet_start_entry = ttk.Entry(frame, textvariable=self.variables['notifications.quiet_hours_start'])
        quiet_start_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Quiet Hours End
        ttk.Label(frame, text="Quiet Hours End:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.variables['notifications.quiet_hours_end'] = tk.StringVar(value=self.settings_manager.notifications.quiet_hours_end)
        quiet_end_entry = ttk.Entry(frame, textvariable=self.variables['notifications.quiet_hours_end'])
        quiet_end_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def _create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Last saved time
        self.last_saved_var = tk.StringVar(value="")
        ttk.Label(status_frame, textvariable=self.last_saved_var).pack(side=tk.RIGHT)
    
    def _load_settings(self):
        """Load settings into UI variables"""
        try:
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
            self.variables['voice.tts_engine'].set(self.settings_manager.voice.tts_engine)
            self.variables['voice.auto_listen'].set(self.settings_manager.voice.auto_listen)
            self.variables['voice.continuous_listening'].set(self.settings_manager.voice.continuous_listening)
            
            # Load AI settings
            self.variables['ai.default_provider'].set(self.settings_manager.ai.default_provider)
            self.variables['ai.default_model'].set(self.settings_manager.ai.default_model)
            self.variables['ai.max_tokens'].set(self.settings_manager.ai.max_tokens)
            self.variables['ai.temperature'].set(self.settings_manager.ai.temperature)
            self.variables['ai.rag_enabled'].set(self.settings_manager.ai.rag_enabled)
            self.variables['ai.cost_limit'].set(self.settings_manager.ai.cost_limit)
            
            # Load system settings
            self.variables['system.auto_start'].set(self.settings_manager.system.auto_start)
            self.variables['system.minimize_to_tray'].set(self.settings_manager.system.minimize_to_tray)
            self.variables['system.log_level'].set(self.settings_manager.system.log_level)
            self.variables['system.backup_enabled'].set(self.settings_manager.system.backup_enabled)
            self.variables['system.backup_interval'].set(self.settings_manager.system.backup_interval)
            self.variables['system.performance_monitoring'].set(self.settings_manager.system.performance_monitoring)
            
            # Load security settings
            self.variables['security.encryption_enabled'].set(self.settings_manager.security.encryption_enabled)
            self.variables['security.require_authentication'].set(self.settings_manager.security.require_authentication)
            self.variables['security.session_timeout'].set(self.settings_manager.security.session_timeout)
            self.variables['security.max_failed_attempts'].set(self.settings_manager.security.max_failed_attempts)
            self.variables['security.audit_logging'].set(self.settings_manager.security.audit_logging)
            
            # Load remote settings
            self.variables['remote.websocket_enabled'].set(self.settings_manager.remote.websocket_enabled)
            self.variables['remote.websocket_port'].set(self.settings_manager.remote.websocket_port)
            self.variables['remote.websocket_host'].set(self.settings_manager.remote.websocket_host)
            self.variables['remote.allow_remote_control'].set(self.settings_manager.remote.allow_remote_control)
            self.variables['remote.max_connections'].set(self.settings_manager.remote.max_connections)
            
            # Load performance settings
            self.variables['performance.max_memory_usage'].set(self.settings_manager.performance.max_memory_usage)
            self.variables['performance.max_cpu_usage'].set(self.settings_manager.performance.max_cpu_usage)
            self.variables['performance.cache_size'].set(self.settings_manager.performance.cache_size)
            self.variables['performance.thread_pool_size'].set(self.settings_manager.performance.thread_pool_size)
            self.variables['performance.metrics_collection'].set(self.settings_manager.performance.metrics_collection)
            
            # Load notification settings
            self.variables['notifications.enabled'].set(self.settings_manager.notifications.enabled)
            self.variables['notifications.sound_enabled'].set(self.settings_manager.notifications.sound_enabled)
            self.variables['notifications.desktop_notifications'].set(self.settings_manager.notifications.desktop_notifications)
            self.variables['notifications.notification_sound'].set(self.settings_manager.notifications.notification_sound)
            self.variables['notifications.quiet_hours_start'].set(self.settings_manager.notifications.quiet_hours_start)
            self.variables['notifications.quiet_hours_end'].set(self.settings_manager.notifications.quiet_hours_end)
            
            self.status_var.set("Settings loaded")
            
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
            self.settings_manager.voice.tts_engine = self.variables['voice.tts_engine'].get()
            self.settings_manager.voice.auto_listen = self.variables['voice.auto_listen'].get()
            self.settings_manager.voice.continuous_listening = self.variables['voice.continuous_listening'].get()
            
            # Save AI settings
            self.settings_manager.ai.default_provider = self.variables['ai.default_provider'].get()
            self.settings_manager.ai.default_model = self.variables['ai.default_model'].get()
            self.settings_manager.ai.max_tokens = self.variables['ai.max_tokens'].get()
            self.settings_manager.ai.temperature = self.variables['ai.temperature'].get()
            self.settings_manager.ai.rag_enabled = self.variables['ai.rag_enabled'].get()
            self.settings_manager.ai.cost_limit = self.variables['ai.cost_limit'].get()
            
            # Save system settings
            self.settings_manager.system.auto_start = self.variables['system.auto_start'].get()
            self.settings_manager.system.minimize_to_tray = self.variables['system.minimize_to_tray'].get()
            self.settings_manager.system.log_level = self.variables['system.log_level'].get()
            self.settings_manager.system.backup_enabled = self.settings_manager.system.backup_enabled
            self.settings_manager.system.backup_interval = self.variables['system.backup_interval'].get()
            self.settings_manager.system.performance_monitoring = self.variables['system.performance_monitoring'].get()
            
            # Save security settings
            self.settings_manager.security.encryption_enabled = self.variables['security.encryption_enabled'].get()
            self.settings_manager.security.require_authentication = self.variables['security.require_authentication'].get()
            self.settings_manager.security.session_timeout = self.variables['security.session_timeout'].get()
            self.settings_manager.security.max_failed_attempts = self.variables['security.max_failed_attempts'].get()
            self.settings_manager.security.audit_logging = self.variables['security.audit_logging'].get()
            
            # Save remote settings
            self.settings_manager.remote.websocket_enabled = self.variables['remote.websocket_enabled'].get()
            self.settings_manager.remote.websocket_port = self.variables['remote.websocket_port'].get()
            self.settings_manager.remote.websocket_host = self.variables['remote.websocket_host'].get()
            self.settings_manager.remote.allow_remote_control = self.variables['remote.allow_remote_control'].get()
            self.settings_manager.remote.max_connections = self.variables['remote.max_connections'].get()
            
            # Save performance settings
            self.settings_manager.performance.max_memory_usage = self.variables['performance.max_memory_usage'].get()
            self.settings_manager.performance.max_cpu_usage = self.variables['performance.max_cpu_usage'].get()
            self.settings_manager.performance.cache_size = self.variables['performance.cache_size'].get()
            self.settings_manager.performance.thread_pool_size = self.variables['performance.thread_pool_size'].get()
            self.settings_manager.performance.metrics_collection = self.variables['performance.metrics_collection'].get()
            
            # Save notification settings
            self.settings_manager.notifications.enabled = self.variables['notifications.enabled'].get()
            self.settings_manager.notifications.sound_enabled = self.variables['notifications.sound_enabled'].get()
            self.settings_manager.notifications.desktop_notifications = self.variables['notifications.desktop_notifications'].get()
            self.settings_manager.notifications.notification_sound = self.variables['notifications.notification_sound'].get()
            self.settings_manager.notifications.quiet_hours_start = self.variables['notifications.quiet_hours_start'].get()
            self.settings_manager.notifications.quiet_hours_end = self.variables['notifications.quiet_hours_end'].get()
            
            # Save to file
            self.settings_manager.save_settings()
            
            self.status_var.set("Settings saved")
            self.last_saved_var.set(f"Last saved: {time.strftime('%H:%M:%S')}")
            
            # Notify callbacks
            for callback in self.callbacks.get('on_save', []):
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Error in save callback: {e}")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            self.status_var.set("Error saving settings")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            try:
                self.settings_manager.reset_settings()
                self._load_settings()
                self.status_var.set("Settings reset to defaults")
            except Exception as e:
                logger.error(f"Failed to reset settings: {e}")
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def _export_settings(self):
        """Export settings to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if self.settings_manager.export_settings(file_path):
                    self.status_var.set(f"Settings exported to {file_path}")
                    messagebox.showinfo("Success", "Settings exported successfully")
                else:
                    messagebox.showerror("Error", "Failed to export settings")
            except Exception as e:
                logger.error(f"Failed to export settings: {e}")
                messagebox.showerror("Error", f"Failed to export settings: {e}")
    
    def _import_settings(self):
        """Import settings from file"""
        file_path = filedialog.askopenfilename(
            title="Import Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if self.settings_manager.import_settings(file_path):
                    self._load_settings()
                    self.status_var.set(f"Settings imported from {file_path}")
                    messagebox.showinfo("Success", "Settings imported successfully")
                else:
                    messagebox.showerror("Error", "Failed to import settings")
            except Exception as e:
                logger.error(f"Failed to import settings: {e}")
                messagebox.showerror("Error", f"Failed to import settings: {e}")
    
    def _on_search(self, *args):
        """Handle search functionality"""
        search_term = self.search_var.get().lower()
        if not search_term:
            return
        
        # Simple search implementation
        # This would need to be enhanced for a real search feature
        pass
    
    def _on_setting_changed(self, event, data):
        """Handle settings change events"""
        if event == 'setting_changed':
            category = data.get('category')
            key = data.get('key')
            value = data.get('value')
            
            # Update UI if needed
            var_name = f"{category}.{key}"
            if var_name in self.variables:
                self.variables[var_name].set(value)
    
    def _close(self):
        """Close settings window"""
        if messagebox.askyesno("Close", "Do you want to save changes before closing?"):
            self._save_settings()
        self.root.destroy()
    
    def add_callback(self, event: str, callback: Callable):
        """Add callback for events"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def show(self):
        """Show settings window"""
        self.root.mainloop()

def show_settings(parent=None):
    """Show settings window"""
    app = SettingsUI(parent)
    app.show()

if __name__ == "__main__":
    show_settings()
