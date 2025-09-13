"""
Platform Abstraction Layer for JARVIS Computer Assistant

This package provides cross-platform abstraction for system operations,
ensuring compatibility between Windows and Linux platforms.
"""

from .base_platform import BasePlatform, PlatformType, SystemInfo, AudioDevice
from .windows_platform import WindowsPlatform
from .linux_platform import LinuxPlatform
from .platform_factory import (
    PlatformFactory,
    get_platform,
    get_platform_by_type,
    is_platform_supported,
    get_supported_platforms,
    get_platform_info
)

__all__ = [
    "BasePlatform",
    "PlatformType", 
    "SystemInfo",
    "AudioDevice",
    "WindowsPlatform",
    "LinuxPlatform",
    "PlatformFactory",
    "get_platform",
    "get_platform_by_type",
    "is_platform_supported",
    "get_supported_platforms",
    "get_platform_info"
]

__version__ = "1.0.0"
