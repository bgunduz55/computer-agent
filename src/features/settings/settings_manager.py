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
    wake_word: str = "jarvis"
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
    default_model: str = "gpt-3.5-turbo"
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

@dataclass
class SystemSettings:
    """System control settings"""
    auto_start: bool = True
    minimize_to_tray: bool = True
    show_notifications: bool = True
    log_level: str = "INFO"
    max_log_size: int = 100  # MB
    log_retention_days: int = 30
    backup_enabled: bool = True
    backup_interval: int = 24  # hours
    max_backups: int = 10
    performance_monitoring: bool = True
    auto_update: bool = True
    update_channel: str = "stable"

@dataclass
class SecuritySettings:
    """Security settings"""
    encryption_enabled: bool = True
    encryption_key: Optional[str] = None
    session_timeout: int = 3600  # seconds
    max_failed_attempts: int = 5
    lockout_duration: int = 300  # seconds
    require_authentication: bool = True
    biometric_auth: bool = False
    two_factor_auth: bool = False
    audit_logging: bool = True
    data_retention_days: int = 365

@dataclass
class RemoteSettings:
    """Remote control settings"""
    websocket_enabled: bool = True
    websocket_port: int = 8765
    websocket_host: str = "100.109.80.8"
    websocket_ssl: bool = False
    websocket_cert: Optional[str] = None
    websocket_key: Optional[str] = None
    max_connections: int = 10
    connection_timeout: int = 300
    heartbeat_interval: int = 30
    allow_remote_control: bool = True
    require_authentication: bool = True
    allowed_ips: List[str] = None

@dataclass
class PerformanceSettings:
    """Performance settings"""
    max_memory_usage: int = 1024  # MB
    max_cpu_usage: float = 80.0  # percentage
    cache_size: int = 256  # MB
    cache_ttl: int = 3600  # seconds
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
    priority_levels: Dict[str, str] = None

@dataclass
class GeneralSettings:
    """General application settings"""
    theme: str = "system"
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
    """Comprehensive settings manager"""
    
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
        self._listeners: Dict[str, List[callable]] = {}
        self._lock = threading.RLock()
        
        # Load settings
        self.load_settings()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks for settings management"""
        if self.system.backup_enabled:
            threading.Thread(target=self._backup_task, daemon=True).start()
        
        if self.performance.metrics_collection:
            threading.Thread(target=self._metrics_task, daemon=True).start()
    
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
            self.save_settings()  # Save defaults
    
    def save_settings(self) -> None:
        """Save settings to file"""
        try:
            with self._lock:
                # Create backup before saving
                if self.settings_file.exists():
                    self._create_backup()
                
                # Prepare settings data
                data = {
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
                
                # Save to file
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                logger.info("Settings saved successfully")
                
                # Notify listeners
                self._notify_listeners('settings_saved', data)
        
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def _create_backup(self) -> None:
        """Create backup of current settings"""
        try:
            timestamp = int(time.time())
            backup_file = self.backup_dir / f"settings_backup_{timestamp}.json"
            
            with open(self.settings_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            # Clean old backups
            self._cleanup_backups()
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
    
    def _cleanup_backups(self) -> None:
        """Clean up old backup files"""
        try:
            backup_files = list(self.backup_dir.glob("settings_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the most recent backups
            for backup_file in backup_files[self.system.max_backups:]:
                backup_file.unlink()
        
        except Exception as e:
            logger.error(f"Failed to cleanup backups: {e}")
    
    def get_setting(self, category: SettingCategory, key: str) -> Any:
        """Get a specific setting value"""
        try:
            settings_obj = getattr(self, category.value)
            return getattr(settings_obj, key)
        except AttributeError:
            logger.error(f"Setting not found: {category.value}.{key}")
            return None
    
    def set_setting(self, category: SettingCategory, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        try:
            with self._lock:
                settings_obj = getattr(self, category.value)
                setattr(settings_obj, key, value)
                
                # Save settings
                self.save_settings()
                
                # Notify listeners
                self._notify_listeners('setting_changed', {
                    'category': category.value,
                    'key': key,
                    'value': value
                })
                
                return True
        
        except Exception as e:
            logger.error(f"Failed to set setting {category.value}.{key}: {e}")
            return False
    
    def get_category_settings(self, category: SettingCategory) -> Dict[str, Any]:
        """Get all settings for a category"""
        try:
            settings_obj = getattr(self, category.value)
            return asdict(settings_obj)
        except AttributeError:
            logger.error(f"Category not found: {category.value}")
            return {}
    
    def set_category_settings(self, category: SettingCategory, settings: Dict[str, Any]) -> bool:
        """Set all settings for a category"""
        try:
            with self._lock:
                settings_obj = getattr(self, category.value)
                
                # Update settings
                for key, value in settings.items():
                    if hasattr(settings_obj, key):
                        setattr(settings_obj, key, value)
                
                # Save settings
                self.save_settings()
                
                # Notify listeners
                self._notify_listeners('category_changed', {
                    'category': category.value,
                    'settings': settings
                })
                
                return True
        
        except Exception as e:
            logger.error(f"Failed to set category settings {category.value}: {e}")
            return False
    
    def reset_settings(self, category: Optional[SettingCategory] = None) -> bool:
        """Reset settings to defaults"""
        try:
            with self._lock:
                if category:
                    # Reset specific category
                    if category == SettingCategory.VOICE:
                        self.voice = VoiceSettings()
                    elif category == SettingCategory.AI:
                        self.ai = AISettings()
                    elif category == SettingCategory.SYSTEM:
                        self.system = SystemSettings()
                    elif category == SettingCategory.SECURITY:
                        self.security = SecuritySettings()
                    elif category == SettingCategory.REMOTE:
                        self.remote = RemoteSettings()
                    elif category == SettingCategory.PERFORMANCE:
                        self.performance = PerformanceSettings()
                    elif category == SettingCategory.NOTIFICATIONS:
                        self.notifications = NotificationSettings()
                    elif category == SettingCategory.GENERAL:
                        self.general = GeneralSettings()
                else:
                    # Reset all settings
                    self.voice = VoiceSettings()
                    self.ai = AISettings()
                    self.system = SystemSettings()
                    self.security = SecuritySettings()
                    self.remote = RemoteSettings()
                    self.performance = PerformanceSettings()
                    self.notifications = NotificationSettings()
                    self.general = GeneralSettings()
                
                # Save settings
                self.save_settings()
                
                # Notify listeners
                self._notify_listeners('settings_reset', {'category': category.value if category else 'all'})
                
                return True
        
        except Exception as e:
            logger.error(f"Failed to reset settings: {e}")
            return False
    
    def export_settings(self, file_path: str) -> bool:
        """Export settings to file"""
        try:
            data = {
                'voice': asdict(self.voice),
                'ai': asdict(self.ai),
                'system': asdict(self.system),
                'security': asdict(self.security),
                'remote': asdict(self.remote),
                'performance': asdict(self.performance),
                'notifications': asdict(self.notifications),
                'general': asdict(self.general),
                'exported_at': time.time()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings exported to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False
    
    def update_remote_settings(self, host: str = None, port: int = None, 
                              enabled: bool = None, ssl: bool = None,
                              max_connections: int = None, 
                              connection_timeout: int = None,
                              heartbeat_interval: int = None,
                              allow_remote_control: bool = None,
                              require_authentication: bool = None,
                              allowed_ips: List[str] = None) -> bool:
        """Update remote control settings"""
        try:
            updated = False
            
            if host is not None:
                self.remote.websocket_host = host
                updated = True
                logger.info(f"WebSocket host updated to: {host}")
            
            if port is not None:
                self.remote.websocket_port = port
                updated = True
                logger.info(f"WebSocket port updated to: {port}")
            
            if enabled is not None:
                self.remote.websocket_enabled = enabled
                updated = True
                logger.info(f"WebSocket enabled: {enabled}")
            
            if ssl is not None:
                self.remote.websocket_ssl = ssl
                updated = True
                logger.info(f"WebSocket SSL: {ssl}")
            
            if max_connections is not None:
                self.remote.max_connections = max_connections
                updated = True
                logger.info(f"Max connections updated to: {max_connections}")
            
            if connection_timeout is not None:
                self.remote.connection_timeout = connection_timeout
                updated = True
                logger.info(f"Connection timeout updated to: {connection_timeout}")
            
            if heartbeat_interval is not None:
                self.remote.heartbeat_interval = heartbeat_interval
                updated = True
                logger.info(f"Heartbeat interval updated to: {heartbeat_interval}")
            
            if allow_remote_control is not None:
                self.remote.allow_remote_control = allow_remote_control
                updated = True
                logger.info(f"Allow remote control: {allow_remote_control}")
            
            if require_authentication is not None:
                self.remote.require_authentication = require_authentication
                updated = True
                logger.info(f"Require authentication: {require_authentication}")
            
            if allowed_ips is not None:
                self.remote.allowed_ips = allowed_ips
                updated = True
                logger.info(f"Allowed IPs updated: {allowed_ips}")
            
            if updated:
                self.save_settings()
                logger.info("Remote settings updated successfully")
            
            return updated
        
        except Exception as e:
            logger.error(f"Failed to update remote settings: {e}")
            return False
    
    def get_remote_settings(self) -> Dict[str, Any]:
        """Get current remote settings"""
        return asdict(self.remote)
    
    def validate_remote_settings(self) -> List[str]:
        """Validate remote settings and return any errors"""
        errors = []
        
        try:
            # Validate host
            if not self.remote.websocket_host:
                errors.append("WebSocket host cannot be empty")
            elif self.remote.websocket_host not in ["0.0.0.0", "localhost", "127.0.0.1", "100.109.80.8"]:
                # Basic IP validation
                parts = self.remote.websocket_host.split('.')
                if len(parts) != 4:
                    errors.append("Invalid IP address format")
                else:
                    for part in parts:
                        if not part.isdigit() or not 0 <= int(part) <= 255:
                            errors.append("Invalid IP address range")
                            break
            
            # Validate port
            if not 1 <= self.remote.websocket_port <= 65535:
                errors.append("Port must be between 1 and 65535")
            
            # Validate max connections
            if self.remote.max_connections < 1:
                errors.append("Max connections must be at least 1")
            
            # Validate timeouts
            if self.remote.connection_timeout < 1:
                errors.append("Connection timeout must be at least 1 second")
            
            if self.remote.heartbeat_interval < 1:
                errors.append("Heartbeat interval must be at least 1 second")
            
            # Validate allowed IPs
            if self.remote.allowed_ips:
                for ip in self.remote.allowed_ips:
                    if ip not in ["0.0.0.0", "localhost", "127.0.0.1", "100.109.80.8"]:
                        parts = ip.split('.')
                        if len(parts) != 4:
                            errors.append(f"Invalid allowed IP format: {ip}")
                        else:
                            for part in parts:
                                if not part.isdigit() or not 0 <= int(part) <= 255:
                                    errors.append(f"Invalid allowed IP range: {ip}")
                                    break
        
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
    
    def import_settings(self, file_path: str) -> bool:
        """Import settings from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate and import settings
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
            
            # Save imported settings
            self.save_settings()
            
            logger.info(f"Settings imported from {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False
    
    def add_listener(self, event: str, callback: callable) -> None:
        """Add event listener"""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
    
    def remove_listener(self, event: str, callback: callable) -> None:
        """Remove event listener"""
        if event in self._listeners:
            try:
                self._listeners[event].remove(callback)
            except ValueError:
                pass
    
    def _notify_listeners(self, event: str, data: Any) -> None:
        """Notify all listeners of an event"""
        if event in self._listeners:
            for callback in self._listeners[event]:
                try:
                    callback(event, data)
                except Exception as e:
                    logger.error(f"Error in settings listener: {e}")
    
    def _backup_task(self) -> None:
        """Background task for automatic backups"""
        while True:
            try:
                time.sleep(self.system.backup_interval * 3600)  # Convert hours to seconds
                self._create_backup()
            except Exception as e:
                logger.error(f"Backup task error: {e}")
    
    def _metrics_task(self) -> None:
        """Background task for performance metrics"""
        while True:
            try:
                time.sleep(60)  # Collect metrics every minute
                # Implement metrics collection here
                pass
            except Exception as e:
                logger.error(f"Metrics task error: {e}")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get all settings"""
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
    
    def get_settings_summary(self) -> Dict[str, Any]:
        """Get summary of all settings"""
        return {
            'voice': {
                'engine': self.voice.engine,
                'language': self.voice.language,
                'wake_word': self.voice.wake_word,
                'auto_listen': self.voice.auto_listen
            },
            'ai': {
                'default_provider': self.ai.default_provider,
                'default_model': self.ai.default_model,
                'rag_enabled': self.ai.rag_enabled
            },
            'system': {
                'auto_start': self.system.auto_start,
                'log_level': self.system.log_level,
                'backup_enabled': self.system.backup_enabled
            },
            'security': {
                'encryption_enabled': self.security.encryption_enabled,
                'require_authentication': self.security.require_authentication
            },
            'remote': {
                'websocket_enabled': self.remote.websocket_enabled,
                'websocket_port': self.remote.websocket_port,
                'allow_remote_control': self.remote.allow_remote_control
            },
            'performance': {
                'max_memory_usage': self.performance.max_memory_usage,
                'metrics_collection': self.performance.metrics_collection
            },
            'notifications': {
                'enabled': self.notifications.enabled,
                'sound_enabled': self.notifications.sound_enabled
            },
            'general': {
                'theme': self.general.theme,
                'language': self.general.language,
                'first_run': self.general.first_run
            }
        }

# Global settings manager instance
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
        _settings_manager = None
