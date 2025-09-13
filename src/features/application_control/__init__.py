"""
Application Control Feature
Manages running applications and browser control
"""

from .application_manager import (
    ApplicationManager,
    ApplicationInfo,
    BrowserTab,
    get_application_manager,
    cleanup_application_manager
)

__all__ = [
    'ApplicationManager',
    'ApplicationInfo',
    'BrowserTab',
    'get_application_manager',
    'cleanup_application_manager'
]
