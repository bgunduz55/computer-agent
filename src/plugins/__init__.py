"""
Plugin System for JARVIS Computer Assistant
Provides extensible plugin architecture for adding new features
"""

from .plugin_manager import PluginManager, get_plugin_manager
from .base_plugin import BasePlugin, PluginType, PluginStatus
# Core plugins will be loaded dynamically

__all__ = [
    'PluginManager',
    'get_plugin_manager',
    'BasePlugin',
    'PluginType',
    'PluginStatus'
]
