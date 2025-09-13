"""
Base Platform Interface for JARVIS Computer Assistant

This module defines the abstract base class for platform-specific implementations,
ensuring cross-platform compatibility between Windows and Linux.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platform types"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    ANDROID = "android"
    IOS = "ios"

@dataclass
class SystemInfo:
    """System information data structure"""
    platform: str
    version: str
    architecture: str
    cpu_count: int
    memory_total: int
    memory_available: int
    disk_total: int
    disk_available: int

@dataclass
class AudioDevice:
    """Audio device information"""
    name: str
    device_id: int
    is_default: bool
    channels: int
    sample_rate: int

class BasePlatform(ABC):
    """
    Abstract base class for platform-specific implementations.
    
    This class defines the interface that all platform implementations
    must follow to ensure cross-platform compatibility.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
    
    @property
    @abstractmethod
    def platform_type(self) -> PlatformType:
        """Platform type identifier"""
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Human-readable platform name"""
        pass
    
    @property
    @abstractmethod
    def is_supported(self) -> bool:
        """Check if platform is supported"""
        pass
    
    def initialize(self) -> bool:
        """
        Initialize the platform-specific components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if self._initialized:
            return True
            
        try:
            self._initialize_platform()
            self._initialized = True
            self.logger.info(f"Platform {self.platform_name} initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize platform {self.platform_name}: {e}")
            return False
    
    @abstractmethod
    def _initialize_platform(self) -> None:
        """Platform-specific initialization"""
        pass
    
    # System Information
    @abstractmethod
    def get_system_info(self) -> SystemInfo:
        """Get system information"""
        pass
    
    @abstractmethod
    def get_audio_devices(self) -> List[AudioDevice]:
        """Get available audio devices"""
        pass
    
    @abstractmethod
    def get_default_audio_device(self) -> Optional[AudioDevice]:
        """Get default audio device"""
        pass
    
    # Audio Control
    @abstractmethod
    def get_volume(self) -> int:
        """Get current system volume (0-100)"""
        pass
    
    @abstractmethod
    def set_volume(self, volume: int) -> bool:
        """Set system volume (0-100)"""
        pass
    
    @abstractmethod
    def mute_volume(self) -> bool:
        """Mute system volume"""
        pass
    
    @abstractmethod
    def unmute_volume(self) -> bool:
        """Unmute system volume"""
        pass
    
    # Display Control
    @abstractmethod
    def get_brightness(self) -> int:
        """Get current display brightness (0-100)"""
        pass
    
    @abstractmethod
    def set_brightness(self, brightness: int) -> bool:
        """Set display brightness (0-100)"""
        pass
    
    # Power Management
    @abstractmethod
    def get_power_status(self) -> Dict[str, Any]:
        """Get power management status"""
        pass
    
    @abstractmethod
    def shutdown(self, delay: int = 0) -> bool:
        """Shutdown system"""
        pass
    
    @abstractmethod
    def restart(self, delay: int = 0) -> bool:
        """Restart system"""
        pass
    
    @abstractmethod
    def sleep(self) -> bool:
        """Put system to sleep"""
        pass
    
    @abstractmethod
    def hibernate(self) -> bool:
        """Hibernate system"""
        pass
    
    # Process Management
    @abstractmethod
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get list of running processes"""
        pass
    
    @abstractmethod
    def kill_process(self, process_id: int) -> bool:
        """Kill a process by ID"""
        pass
    
    @abstractmethod
    def start_process(self, command: str, args: List[str] = None) -> Optional[int]:
        """Start a new process"""
        pass
    
    # File System
    @abstractmethod
    def get_home_directory(self) -> str:
        """Get user home directory path"""
        pass
    
    @abstractmethod
    def get_temp_directory(self) -> str:
        """Get temporary directory path"""
        pass
    
    @abstractmethod
    def get_app_data_directory(self) -> str:
        """Get application data directory path"""
        pass
    
    # Network
    @abstractmethod
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interface information"""
        pass
    
    @abstractmethod
    def get_ip_address(self) -> Optional[str]:
        """Get primary IP address"""
        pass
    
    # Window Management
    @abstractmethod
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get active window information"""
        pass
    
    @abstractmethod
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of all windows"""
        pass
    
    @abstractmethod
    def focus_window(self, window_id: int) -> bool:
        """Focus a specific window"""
        pass
    
    @abstractmethod
    def minimize_window(self, window_id: int) -> bool:
        """Minimize a window"""
        pass
    
    @abstractmethod
    def maximize_window(self, window_id: int) -> bool:
        """Maximize a window"""
        pass
    
    @abstractmethod
    def close_window(self, window_id: int) -> bool:
        """Close a window"""
        pass
    
    # Screenshot
    @abstractmethod
    def take_screenshot(self, file_path: str) -> bool:
        """Take a screenshot and save to file"""
        pass
    
    # Clipboard
    @abstractmethod
    def get_clipboard_text(self) -> Optional[str]:
        """Get clipboard text content"""
        pass
    
    @abstractmethod
    def set_clipboard_text(self, text: str) -> bool:
        """Set clipboard text content"""
        pass
    
    # Notifications
    @abstractmethod
    def show_notification(self, title: str, message: str, duration: int = 5) -> bool:
        """Show system notification"""
        pass
    
    # Terminal/Command Execution
    @abstractmethod
    def execute_command(self, command: str, args: List[str] = None, 
                       timeout: int = 30) -> Tuple[int, str, str]:
        """
        Execute a system command
        
        Returns:
            Tuple[int, str, str]: (return_code, stdout, stderr)
        """
        pass
    
    @abstractmethod
    def get_shell_command(self) -> str:
        """Get the default shell command for the platform"""
        pass
    
    # Platform-specific Features
    @abstractmethod
    def get_platform_features(self) -> List[str]:
        """Get list of platform-specific features"""
        pass
    
    @abstractmethod
    def is_feature_available(self, feature: str) -> bool:
        """Check if a specific feature is available"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup platform-specific resources"""
        if self._initialized:
            self._cleanup_platform()
            self._initialized = False
            self.logger.info(f"Platform {self.platform_name} cleaned up")
    
    @abstractmethod
    def _cleanup_platform(self) -> None:
        """Platform-specific cleanup"""
        pass
    
    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
