"""
Core module for JARVIS Computer Assistant

This module contains the core functionality and platform abstraction layer.
"""

from .platform import (
    BasePlatform,
    PlatformType,
    SystemInfo,
    AudioDevice,
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
    "get_platform",
    "get_platform_by_type",
    "is_platform_supported",
    "get_supported_platforms",
    "get_platform_info"
]

__version__ = "1.0.0"
