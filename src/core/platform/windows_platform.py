"""
Windows Platform Implementation for JARVIS Computer Assistant

This module provides Windows-specific implementations of the platform abstraction layer.
"""

import platform
import psutil
import subprocess
import win32api
import win32con
import win32gui
import win32process
import win32clipboard
import win32com.client
import ctypes
from ctypes import wintypes
import sounddevice as sd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
import time
import os
import tempfile

from .base_platform import BasePlatform, PlatformType, SystemInfo, AudioDevice

logger = logging.getLogger(__name__)

class WindowsPlatform(BasePlatform):
    """Windows-specific platform implementation"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize COM for Windows
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception as e:
            logger.warning(f"Failed to initialize COM: {e}")
        
        try:
            self._shell = win32com.client.Dispatch("WScript.Shell")
        except Exception as e:
            logger.warning(f"Failed to initialize WScript.Shell: {e}")
            self._shell = None
        
        self._audio_interface = None
    
    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.WINDOWS
    
    @property
    def platform_name(self) -> str:
        return "Windows"
    
    def get_platform_name(self) -> str:
        """Get platform name"""
        return self.platform_name
    
    @property
    def is_supported(self) -> bool:
        return platform.system() == "Windows"
    
    def _initialize_platform(self) -> None:
        """Initialize Windows-specific components"""
        try:
            # Initialize audio interface
            self._audio_interface = sd.query_devices()
            logger.info("Windows platform initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Windows platform: {e}")
            raise
    
    def get_system_info(self) -> SystemInfo:
        """Get Windows system information"""
        try:
            # Get system information
            uname = platform.uname()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            
            return SystemInfo(
                platform=uname.system,
                version=uname.version,
                architecture=uname.machine,
                cpu_count=psutil.cpu_count(),
                memory_total=memory.total,
                memory_available=memory.available,
                disk_total=disk.total,
                disk_available=disk.free
            )
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            raise
    
    def get_audio_devices(self) -> List[AudioDevice]:
        """Get available audio devices on Windows"""
        try:
            devices = []
            audio_devices = sd.query_devices()
            
            for i, device in enumerate(audio_devices):
                if device['max_input_channels'] > 0 or device['max_output_channels'] > 0:
                    devices.append(AudioDevice(
                        name=device['name'],
                        device_id=i,
                        is_default=device['name'] == sd.default.device[0] if sd.default.device[0] else False,
                        channels=max(device['max_input_channels'], device['max_output_channels']),
                        sample_rate=int(device['default_samplerate'])
                    ))
            
            return devices
        except Exception as e:
            logger.error(f"Failed to get audio devices: {e}")
            return []
    
    def get_default_audio_device(self) -> Optional[AudioDevice]:
        """Get default audio device on Windows"""
        try:
            devices = self.get_audio_devices()
            return next((d for d in devices if d.is_default), devices[0] if devices else None)
        except Exception as e:
            logger.error(f"Failed to get default audio device: {e}")
            return None
    
    def get_volume(self) -> int:
        """Get current system volume on Windows"""
        try:
            # Use Windows API to get volume
            import ctypes
            from ctypes import wintypes
            
            # Load Windows API
            winmm = ctypes.windll.winmm
            
            # Get volume
            volume = wintypes.DWORD()
            winmm.waveOutGetVolume(0, ctypes.byref(volume))
            
            # Convert to percentage
            return int((volume.value & 0xFFFF) / 655.35)
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return 50  # Default volume
    
    def set_volume(self, volume: int) -> bool:
        """Set system volume on Windows"""
        try:
            # Use Windows API to set volume
            import ctypes
            from ctypes import wintypes
            
            # Clamp volume to 0-100
            volume = max(0, min(100, volume))
            
            # Load Windows API
            winmm = ctypes.windll.winmm
            
            # Convert to Windows format
            volume_value = int(volume * 655.35)
            volume_value = volume_value | (volume_value << 16)
            
            # Set volume
            result = winmm.waveOutSetVolume(0, volume_value)
            return result == 0
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return False
    
    def mute_volume(self) -> bool:
        """Mute system volume on Windows"""
        try:
            # Use Windows API to mute
            import ctypes
            from ctypes import wintypes
            
            winmm = ctypes.windll.winmm
            result = winmm.waveOutSetVolume(0, 0)
            return result == 0
        except Exception as e:
            logger.error(f"Failed to mute volume: {e}")
            return False
    
    def unmute_volume(self) -> bool:
        """Unmute system volume on Windows"""
        try:
            # Restore previous volume or set to 50%
            return self.set_volume(50)
        except Exception as e:
            logger.error(f"Failed to unmute volume: {e}")
            return False
    
    def get_brightness(self) -> int:
        """Get current display brightness on Windows"""
        try:
            import wmi
            c = wmi.WMI(namespace='wmi')
            brightness = c.WmiMonitorBrightness()[0].CurrentBrightness
            return brightness
        except Exception as e:
            logger.error(f"Failed to get brightness: {e}")
            return 50  # Default brightness
    
    def set_brightness(self, brightness: int) -> bool:
        """Set display brightness on Windows"""
        try:
            import wmi
            c = wmi.WMI(namespace='wmi')
            brightness = max(0, min(100, brightness))
            c.WmiMonitorBrightnessMethods()[0].WmiSetBrightness(1, brightness)
            return True
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return False
    
    def get_power_status(self) -> Dict[str, Any]:
        """Get power management status on Windows"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "battery_percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
            else:
                return {"battery_percent": None, "power_plugged": True, "time_left": None}
        except Exception as e:
            logger.error(f"Failed to get power status: {e}")
            return {"battery_percent": None, "power_plugged": True, "time_left": None}
    
    def shutdown(self, delay: int = 0) -> bool:
        """Shutdown Windows system"""
        try:
            cmd = f"shutdown /s /t {delay}"
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to shutdown: {e}")
            return False
    
    def restart(self, delay: int = 0) -> bool:
        """Restart Windows system"""
        try:
            cmd = f"shutdown /r /t {delay}"
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to restart: {e}")
            return False
    
    def sleep(self) -> bool:
        """Put Windows system to sleep"""
        try:
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to sleep: {e}")
            return False
    
    def hibernate(self) -> bool:
        """Hibernate Windows system"""
        try:
            ctypes.windll.powrprof.SetSuspendState(1, 1, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to hibernate: {e}")
            return False
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get list of running processes on Windows"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return processes
        except Exception as e:
            logger.error(f"Failed to get processes: {e}")
            return []
    
    def kill_process(self, process_id: int) -> bool:
        """Kill a process by ID on Windows"""
        try:
            process = psutil.Process(process_id)
            process.terminate()
            return True
        except Exception as e:
            logger.error(f"Failed to kill process {process_id}: {e}")
            return False
    
    def start_process(self, command: str, args: List[str] = None) -> Optional[int]:
        """Start a new process on Windows"""
        try:
            if args:
                cmd = [command] + args
            else:
                cmd = command
            
            process = subprocess.Popen(cmd, shell=True)
            return process.pid
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            return None
    
    def get_home_directory(self) -> str:
        """Get user home directory on Windows"""
        return str(Path.home())
    
    def get_temp_directory(self) -> str:
        """Get temporary directory on Windows"""
        return tempfile.gettempdir()
    
    def get_app_data_directory(self) -> str:
        """Get application data directory on Windows"""
        return str(Path.home() / "AppData" / "Roaming")
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interface information on Windows"""
        try:
            interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == 2:  # AF_INET
                        interfaces.append({
                            'name': interface,
                            'ip': addr.address,
                            'netmask': addr.netmask,
                            'broadcast': addr.broadcast
                        })
            return interfaces
        except Exception as e:
            logger.error(f"Failed to get network interfaces: {e}")
            return []
    
    def get_ip_address(self) -> Optional[str]:
        """Get primary IP address on Windows"""
        try:
            interfaces = self.get_network_interfaces()
            for interface in interfaces:
                if interface['ip'] and not interface['ip'].startswith('127.'):
                    return interface['ip']
            return None
        except Exception as e:
            logger.error(f"Failed to get IP address: {e}")
            return None
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get active window information on Windows"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                title = win32gui.GetWindowText(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                return {
                    'hwnd': hwnd,
                    'title': title,
                    'rect': rect
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of all windows on Windows"""
        try:
            windows = []
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'rect': rect
                        })
                return True
            
            win32gui.EnumWindows(enum_windows_callback, windows)
            return windows
        except Exception as e:
            logger.error(f"Failed to get window list: {e}")
            return []
    
    def focus_window(self, window_id: int) -> bool:
        """Focus a specific window on Windows"""
        try:
            win32gui.SetForegroundWindow(window_id)
            return True
        except Exception as e:
            logger.error(f"Failed to focus window {window_id}: {e}")
            return False
    
    def minimize_window(self, window_id: int) -> bool:
        """Minimize a window on Windows"""
        try:
            win32gui.ShowWindow(window_id, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            logger.error(f"Failed to minimize window {window_id}: {e}")
            return False
    
    def maximize_window(self, window_id: int) -> bool:
        """Maximize a window on Windows"""
        try:
            win32gui.ShowWindow(window_id, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            logger.error(f"Failed to maximize window {window_id}: {e}")
            return False
    
    def close_window(self, window_id: int) -> bool:
        """Close a window on Windows"""
        try:
            win32gui.PostMessage(window_id, win32con.WM_CLOSE, 0, 0)
            return True
        except Exception as e:
            logger.error(f"Failed to close window {window_id}: {e}")
            return False
    
    def take_screenshot(self, file_path: str) -> bool:
        """Take a screenshot on Windows"""
        try:
            import PIL.ImageGrab as ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    def get_clipboard_text(self) -> Optional[str]:
        """Get clipboard text content on Windows"""
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
            win32clipboard.CloseClipboard()
            return data.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to get clipboard text: {e}")
            return None
    
    def set_clipboard_text(self, text: str) -> bool:
        """Set clipboard text content on Windows"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            logger.error(f"Failed to set clipboard text: {e}")
            return False
    
    def show_notification(self, title: str, message: str, duration: int = 5) -> bool:
        """Show system notification on Windows"""
        try:
            # Use Windows 10/11 toast notifications
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(title, message, duration=duration)
            return True
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
            return False
    
    def execute_command(self, command: str, args: List[str] = None, 
                       timeout: int = 30) -> Tuple[int, str, str]:
        """Execute a system command on Windows"""
        try:
            if args:
                cmd = [command] + args
            else:
                cmd = command
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return -1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return -1, "", str(e)
    
    def get_shell_command(self) -> str:
        """Get the default shell command for Windows"""
        return "cmd"
    
    def get_platform_features(self) -> List[str]:
        """Get list of Windows-specific features"""
        return [
            "windows_speech_platform",
            "sapi5_tts",
            "win32_api",
            "wmi_integration",
            "powershell",
            "registry_access",
            "windows_notifications",
            "directx_audio"
        ]
    
    def is_feature_available(self, feature: str) -> bool:
        """Check if a specific feature is available on Windows"""
        try:
            if feature == "windows_speech_platform":
                import win32com.client
                return True
            elif feature == "sapi5_tts":
                import pyttsx3
                return True
            elif feature == "win32_api":
                import win32api
                return True
            elif feature == "wmi_integration":
                import wmi
                return True
            elif feature == "powershell":
                return True
            elif feature == "registry_access":
                import winreg
                return True
            elif feature == "windows_notifications":
                import win10toast
                return True
            elif feature == "directx_audio":
                import sounddevice
                return True
            else:
                return False
        except ImportError:
            return False
    
    def _cleanup_platform(self) -> None:
        """Cleanup Windows-specific resources"""
        try:
            if self._audio_interface:
                self._audio_interface = None
            logger.info("Windows platform cleaned up")
        except Exception as e:
            logger.error(f"Failed to cleanup Windows platform: {e}")
