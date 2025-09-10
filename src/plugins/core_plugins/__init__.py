"""
Core Plugins for JARVIS Computer Assistant
Built-in plugins that provide essential functionality
"""

from .weather_plugin import WeatherPlugin
from .calendar_plugin import CalendarPlugin
from .email_plugin import EmailPlugin
from .news_plugin import NewsPlugin
from .system_monitor_plugin import SystemMonitorPlugin

__all__ = [
    'WeatherPlugin',
    'CalendarPlugin', 
    'EmailPlugin',
    'NewsPlugin',
    'SystemMonitorPlugin'
]
