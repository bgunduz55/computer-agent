"""
Settings Management for JARVIS Computer Assistant

This package provides comprehensive settings management including
configuration, UI, and validation for all aspects of the JARVIS assistant.
"""

from .settings_manager import (
    SettingsManager,
    SettingCategory,
    VoiceSettings,
    AISettings,
    SystemSettings,
    SecuritySettings,
    RemoteSettings,
    PerformanceSettings,
    NotificationSettings,
    GeneralSettings,
    get_settings_manager,
    cleanup_settings_manager
)

from .settings_ui import (
    SettingsUI,
    show_settings
)

__all__ = [
    # Settings Manager
    "SettingsManager",
    "SettingCategory",
    "VoiceSettings",
    "AISettings",
    "SystemSettings",
    "SecuritySettings",
    "RemoteSettings",
    "PerformanceSettings",
    "NotificationSettings",
    "GeneralSettings",
    "get_settings_manager",
    "cleanup_settings_manager",
    
    # Settings UI
    "SettingsUI",
    "show_settings"
]

__version__ = "1.0.0"
