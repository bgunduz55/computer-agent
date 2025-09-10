"""
Platform Factory for JARVIS Computer Assistant

This module provides a factory pattern implementation for creating platform-specific
instances based on the current operating system.
"""

import platform
import logging
from typing import Optional, Type
from .base_platform import BasePlatform, PlatformType
from .windows_platform import WindowsPlatform
from .linux_platform import LinuxPlatform

logger = logging.getLogger(__name__)

class PlatformFactory:
    """
    Factory class for creating platform-specific implementations.
    
    This class automatically detects the current platform and creates
    the appropriate platform implementation.
    """
    
    _platforms = {
        PlatformType.WINDOWS: WindowsPlatform,
        PlatformType.LINUX: LinuxPlatform,
    }
    
    @classmethod
    def create_platform(cls) -> Optional[BasePlatform]:
        """
        Create a platform instance based on the current operating system.
        
        Returns:
            Optional[BasePlatform]: Platform instance or None if unsupported
        """
        try:
            current_platform = cls._detect_platform()
            if current_platform is None:
                logger.error("Unsupported platform detected")
                return None
            
            platform_class = cls._platforms.get(current_platform)
            if platform_class is None:
                logger.error(f"No implementation found for platform: {current_platform}")
                return None
            
            platform_instance = platform_class()
            
            # Check if platform is supported
            if not platform_instance.is_supported:
                logger.error(f"Platform {current_platform} is not supported on this system")
                return None
            
            # Initialize the platform
            if platform_instance.initialize():
                logger.info(f"Platform {current_platform.value} created successfully")
                return platform_instance
            else:
                logger.error(f"Failed to initialize platform {current_platform.value}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create platform: {e}")
            return None
    
    @classmethod
    def create_platform_by_type(cls, platform_type: PlatformType) -> Optional[BasePlatform]:
        """
        Create a platform instance by specific platform type.
        
        Args:
            platform_type: The platform type to create
            
        Returns:
            Optional[BasePlatform]: Platform instance or None if not supported
        """
        try:
            platform_class = cls._platforms.get(platform_type)
            if platform_class is None:
                logger.error(f"No implementation found for platform: {platform_type}")
                return None
            
            platform_instance = platform_class()
            
            # Check if platform is supported
            if not platform_instance.is_supported:
                logger.error(f"Platform {platform_type} is not supported on this system")
                return None
            
            # Initialize the platform
            if platform_instance.initialize():
                logger.info(f"Platform {platform_type.value} created successfully")
                return platform_instance
            else:
                logger.error(f"Failed to initialize platform {platform_type.value}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create platform {platform_type}: {e}")
            return None
    
    @classmethod
    def get_supported_platforms(cls) -> list[PlatformType]:
        """
        Get list of supported platform types.
        
        Returns:
            list[PlatformType]: List of supported platform types
        """
        return list(cls._platforms.keys())
    
    @classmethod
    def is_platform_supported(cls, platform_type: PlatformType) -> bool:
        """
        Check if a specific platform type is supported.
        
        Args:
            platform_type: The platform type to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        return platform_type in cls._platforms
    
    @classmethod
    def register_platform(cls, platform_type: PlatformType, platform_class: Type[BasePlatform]) -> None:
        """
        Register a new platform implementation.
        
        Args:
            platform_type: The platform type
            platform_class: The platform implementation class
        """
        cls._platforms[platform_type] = platform_class
        logger.info(f"Registered platform: {platform_type.value}")
    
    @classmethod
    def unregister_platform(cls, platform_type: PlatformType) -> None:
        """
        Unregister a platform implementation.
        
        Args:
            platform_type: The platform type to unregister
        """
        if platform_type in cls._platforms:
            del cls._platforms[platform_type]
            logger.info(f"Unregistered platform: {platform_type.value}")
    
    @classmethod
    def _detect_platform(cls) -> Optional[PlatformType]:
        """
        Detect the current platform.
        
        Returns:
            Optional[PlatformType]: Detected platform type or None if unsupported
        """
        try:
            system = platform.system().lower()
            
            if system == "windows":
                return PlatformType.WINDOWS
            elif system == "linux":
                return PlatformType.LINUX
            elif system == "darwin":
                return PlatformType.MACOS
            else:
                logger.warning(f"Unsupported platform detected: {system}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to detect platform: {e}")
            return None
    
    @classmethod
    def get_platform_info(cls) -> dict:
        """
        Get information about the current platform.
        
        Returns:
            dict: Platform information
        """
        try:
            uname = platform.uname()
            return {
                "system": uname.system,
                "node": uname.node,
                "release": uname.release,
                "version": uname.version,
                "machine": uname.machine,
                "processor": uname.processor,
                "python_version": platform.python_version(),
                "python_implementation": platform.python_implementation(),
                "detected_platform": cls._detect_platform().value if cls._detect_platform() else None
            }
        except Exception as e:
            logger.error(f"Failed to get platform info: {e}")
            return {}


def get_platform() -> Optional[BasePlatform]:
    """
    Convenience function to get the current platform instance.
    
    Returns:
        Optional[BasePlatform]: Platform instance or None if unsupported
    """
    return PlatformFactory.create_platform()


def get_platform_by_type(platform_type: PlatformType) -> Optional[BasePlatform]:
    """
    Convenience function to get a platform instance by type.
    
    Args:
        platform_type: The platform type to create
        
    Returns:
        Optional[BasePlatform]: Platform instance or None if unsupported
    """
    return PlatformFactory.create_platform_by_type(platform_type)


def is_platform_supported(platform_type: PlatformType) -> bool:
    """
    Convenience function to check if a platform is supported.
    
    Args:
        platform_type: The platform type to check
        
    Returns:
        bool: True if supported, False otherwise
    """
    return PlatformFactory.is_platform_supported(platform_type)


def get_supported_platforms() -> list[PlatformType]:
    """
    Convenience function to get supported platform types.
    
    Returns:
        list[PlatformType]: List of supported platform types
    """
    return PlatformFactory.get_supported_platforms()


def get_platform_info() -> dict:
    """
    Convenience function to get platform information.
    
    Returns:
        dict: Platform information
    """
    return PlatformFactory.get_platform_info()
