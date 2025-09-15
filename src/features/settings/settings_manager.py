"""
Settings Manager for JARVIS Computer Assistant

This module provides comprehensive settings management including
AI providers, voice settings, system configurations, and security settings.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
import time

logger = logging.getLogger(__name__)

class SettingCategory(Enum):
    """Settings categories"""
    GENERAL = "general"
    VOICE = "voice"
    AI = "ai"
    SYSTEM = "system"
    SECURITY = "security"
    REMOTE = "remote"
    PERFORMANCE = "performance"
    NOTIFICATIONS = "notifications"

@dataclass
class VoiceSettings:
    """Voice recognition and TTS settings"""
    engine: str = "google"
    language: str = "en-US"
    wake_word: str = "hey jarvis"
    listen_timeout: float = 5.0
    confidence_threshold: float = 0.7
    tts_engine: str = "edge"
    tts_voice: str = "en-US-AriaNeural"
    tts_rate: float = 1.0
    tts_volume: float = 1.0
    tts_pitch: float = 1.0
    noise_reduction: bool = True
    auto_listen: bool = False
    continuous_listening: bool = False

@dataclass
class AISettings:
    """AI provider settings"""
    default_provider: str = "ollama"
    default_model: str = "deepseek-r1:8b"
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: float = 30.0
    retry_attempts: int = 3
    cost_limit: float = 100.0
    rag_enabled: bool = True
    rag_threshold: float = 0.8
    context_window: int = 4000
    
    # API Keys
    openai_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Provider Settings
    openai_enabled: bool = False
    gemini_enabled: bool = False
    openrouter_enabled: bool = False
    anthropic_enabled: bool = False
    ollama_enabled: bool = True
    
    # Model Settings
    openai_model: str = "gpt-4"
    gemini_model: str = "gemini-pro"
    openrouter_model: str = "openai/gpt-4"
    anthropic_model: str = "claude-3-sonnet"
    
    # Cost Optimization
    cost_optimization: bool = True
    rate_limiting: bool = True
    fallback_provider: str = "openai"

@dataclass
class SystemSettings:
    """System configuration settings"""
    auto_start: bool = True
    minimize_to_tray: bool = True
    show_notifications: bool = True
    log_level: str = "INFO"
    max_log_size: int = 100
    log_retention_days: int = 30
    backup_enabled: bool = True
    backup_interval: int = 12
    max_backups: int = 10
    performance_monitoring: bool = True
    auto_update: bool = True
    update_channel: str = "stable"

@dataclass
class SecuritySettings:
    """Security and authentication settings"""
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    session_timeout: int = 3600
    max_failed_attempts: int = 5
    lockout_duration: int = 300
    require_authentication: bool = True
    biometric_auth: bool = False
    two_factor_auth: bool = False
    audit_logging: bool = True
    data_retention_days: int = 365

@dataclass
class RemoteSettings:
    """Remote control and WebSocket settings"""
    websocket_enabled: bool = True
    websocket_port: int = 8765
    websocket_host: str = "0.0.0.0"
    websocket_ssl: bool = False
    websocket_cert: Optional[str] = None
    websocket_key: Optional[str] = None
    max_connections: int = 10
    connection_timeout: int = 300
    heartbeat_interval: int = 30
    allow_remote_control: bool = True
    require_authentication: bool = True
    allowed_ips: Optional[List[str]] = None

@dataclass
class PerformanceSettings:
    """Performance and resource management settings"""
    max_memory_usage: int = 1024
    max_cpu_usage: float = 80.0
    cache_size: int = 256
    cache_ttl: int = 3600
    thread_pool_size: int = 10
    async_workers: int = 5
    gc_threshold: int = 1000
    profiling_enabled: bool = False
    metrics_collection: bool = True

@dataclass
class NotificationSettings:
    """Notification settings"""
    enabled: bool = True
    sound_enabled: bool = True
    vibration_enabled: bool = True
    desktop_notifications: bool = True
    email_notifications: bool = False
    sms_notifications: bool = False
    notification_sound: str = "default"
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    priority_levels: Optional[Dict[str, int]] = None

@dataclass
class GeneralSettings:
    """General application settings"""
    theme: str = "dark"
    language: str = "en"
    timezone: str = "UTC"
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    currency: str = "USD"
    units: str = "metric"
    first_run: bool = True
    analytics_enabled: bool = True
    crash_reporting: bool = True
    telemetry: bool = False

class SettingsManager:
    """Comprehensive settings management system"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".jarvis" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.settings_file = self.config_dir / "settings.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Settings instances
        self.voice = VoiceSettings()
        self.ai = AISettings()
        self.system = SystemSettings()
        self.security = SecuritySettings()
        self.remote = RemoteSettings()
        self.performance = PerformanceSettings()
        self.notifications = NotificationSettings()
        self.general = GeneralSettings()
        
        # Settings change listeners
        self.listeners: Dict[str, List[callable]] = {}
        self._lock = threading.Lock()
        
        # Load settings
        self.load_settings()
        
        logger.info("Settings manager initialized")
    
    def load_settings(self) -> None:
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load each category
                if 'voice' in data:
                    self.voice = VoiceSettings(**data['voice'])
                if 'ai' in data:
                    self.ai = AISettings(**data['ai'])
                if 'system' in data:
                    self.system = SystemSettings(**data['system'])
                if 'security' in data:
                    self.security = SecuritySettings(**data['security'])
                if 'remote' in data:
                    self.remote = RemoteSettings(**data['remote'])
                if 'performance' in data:
                    self.performance = PerformanceSettings(**data['performance'])
                if 'notifications' in data:
                    self.notifications = NotificationSettings(**data['notifications'])
                if 'general' in data:
                    self.general = GeneralSettings(**data['general'])
                
                logger.info("Settings loaded successfully")
            else:
                logger.info("No settings file found, using defaults")
                self.save_settings()
                
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            logger.info("Using default settings")
    
    def save_settings(self) -> None:
        """Save settings to file"""
        try:
            with self._lock:
                # Create backup if file exists
                if self.settings_file.exists():
                    backup_file = self.backup_dir / f"settings_backup_{int(time.time())}.json"
                    with open(self.settings_file, 'r', encoding='utf-8') as src:
                        with open(backup_file, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                
                # Save current settings
                settings_data = {
                    'voice': asdict(self.voice),
                    'ai': asdict(self.ai),
                    'system': asdict(self.system),
                    'security': asdict(self.security),
                    'remote': asdict(self.remote),
                    'performance': asdict(self.performance),
                    'notifications': asdict(self.notifications),
                    'general': asdict(self.general),
                    'last_updated': time.time()
                }
                
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings_data, f, indent=2, ensure_ascii=False)
                
                logger.info("Settings saved successfully")
                
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get_setting(self, category: SettingCategory, key: str) -> Any:
        """Get a specific setting value"""
        try:
            settings_obj = getattr(self, category.value)
            return getattr(settings_obj, key)
        except AttributeError:
            logger.error(f"Setting {category.value}.{key} not found")
            return None
    
    def set_setting(self, category: SettingCategory, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        try:
            settings_obj = getattr(self, category.value)
            setattr(settings_obj, key, value)
            
            # Notify listeners
            self._notify_listeners(f"{category.value}.{key}", value)
            
            return True
        except AttributeError:
            logger.error(f"Setting {category.value}.{key} not found")
            return False
    
    def update_setting(self, category: SettingCategory, key: str, value: Any) -> bool:
        """Update a setting and save"""
        if self.set_setting(category, key, value):
            self.save_settings()
            return True
        return False
    
    def get_settings_summary(self) -> Dict[str, Any]:
        """Get a summary of all settings"""
        return {
            'voice': asdict(self.voice),
            'ai': asdict(self.ai),
            'system': asdict(self.system),
            'security': asdict(self.security),
            'remote': asdict(self.remote),
            'performance': asdict(self.performance),
            'notifications': asdict(self.notifications),
            'general': asdict(self.general)
        }
    
    def add_listener(self, event: str, callback: callable) -> None:
        """Add a settings change listener"""
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)
    
    def remove_listener(self, event: str, callback: callable) -> None:
        """Remove a settings change listener"""
        if event in self.listeners:
            try:
                self.listeners[event].remove(callback)
            except ValueError:
                pass
    
    def _notify_listeners(self, event: str, value: Any) -> None:
        """Notify listeners of a setting change"""
        if event in self.listeners:
            for callback in self.listeners[event]:
                try:
                    callback(event, value)
                except Exception as e:
                    logger.error(f"Error in settings listener: {e}")
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.voice = VoiceSettings()
        self.ai = AISettings()
        self.system = SystemSettings()
        self.security = SecuritySettings()
        self.remote = RemoteSettings()
        self.performance = PerformanceSettings()
        self.notifications = NotificationSettings()
        self.general = GeneralSettings()
        
        self.save_settings()
        logger.info("Settings reset to defaults")
    
    def export_settings(self, file_path: str) -> bool:
        """Export settings to a file"""
        try:
            settings_data = self.get_settings_summary()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Import settings from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update settings
            if 'voice' in data:
                self.voice = VoiceSettings(**data['voice'])
            if 'ai' in data:
                self.ai = AISettings(**data['ai'])
            if 'system' in data:
                self.system = SystemSettings(**data['system'])
            if 'security' in data:
                self.security = SecuritySettings(**data['security'])
            if 'remote' in data:
                self.remote = RemoteSettings(**data['remote'])
            if 'performance' in data:
                self.performance = PerformanceSettings(**data['performance'])
            if 'notifications' in data:
                self.notifications = NotificationSettings(**data['notifications'])
            if 'general' in data:
                self.general = GeneralSettings(**data['general'])
            
            self.save_settings()
            return True
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False

# Global instance
_settings_manager: Optional[SettingsManager] = None

def get_settings_manager() -> SettingsManager:
    """Get global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

def cleanup_settings_manager() -> None:
    """Cleanup global settings manager instance"""
    global _settings_manager
    if _settings_manager:
        _settings_manager.save_settings()
        _settings_manager = None