"""
Linux Platform Implementation for JARVIS Computer Assistant

This module provides Linux-specific implementations of the platform abstraction layer.
"""

import platform
import psutil
import subprocess
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
import time
import shutil

from .base_platform import BasePlatform, PlatformType, SystemInfo, AudioDevice

logger = logging.getLogger(__name__)

class LinuxPlatform(BasePlatform):
    """Linux-specific platform implementation"""
    
    def __init__(self):
        super().__init__()
        self._pulse_audio_available = False
        self._alsa_available = False
    
    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.LINUX
    
    @property
    def platform_name(self) -> str:
        return "Linux"
    
    def get_platform_name(self) -> str:
        """Get platform name"""
        return self.platform_name
    
    @property
    def is_supported(self) -> bool:
        return platform.system() == "Linux"
    
    def _initialize_platform(self) -> None:
        """Initialize Linux-specific components"""
        try:
            # Check for audio systems
            self._pulse_audio_available = shutil.which("pactl") is not None
            self._alsa_available = shutil.which("amixer") is not None
            
            logger.info("Linux platform initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Linux platform: {e}")
            raise
    
    def get_system_info(self) -> SystemInfo:
        """Get Linux system information"""
        try:
            uname = platform.uname()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
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
        """Get available audio devices on Linux"""
        try:
            devices = []
            
            if self._pulse_audio_available:
                # Use PulseAudio
                result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = line.split('\t')
                            if len(parts) >= 2:
                                device_id = int(parts[0])
                                name = parts[1]
                                devices.append(AudioDevice(
                                    name=name,
                                    device_id=device_id,
                                    is_default=len(devices) == 0,  # First device is default
                                    channels=2,  # Default stereo
                                    sample_rate=44100  # Default sample rate
                                ))
            elif self._alsa_available:
                # Use ALSA
                result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if 'card' in line and ':' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                device_id = int(parts[0].split()[-1])
                                name = parts[1].strip()
                                devices.append(AudioDevice(
                                    name=name,
                                    device_id=device_id,
                                    is_default=len(devices) == 0,
                                    channels=2,
                                    sample_rate=44100
                                ))
            
            return devices
        except Exception as e:
            logger.error(f"Failed to get audio devices: {e}")
            return []
    
    def get_default_audio_device(self) -> Optional[AudioDevice]:
        """Get default audio device on Linux"""
        try:
            devices = self.get_audio_devices()
            return next((d for d in devices if d.is_default), devices[0] if devices else None)
        except Exception as e:
            logger.error(f"Failed to get default audio device: {e}")
            return None
    
    def get_volume(self) -> int:
        """Get current system volume on Linux"""
        try:
            if self._pulse_audio_available:
                # Use PulseAudio
                result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse volume percentage
                    volume_str = result.stdout.strip()
                    if '%' in volume_str:
                        volume = int(volume_str.split('%')[0].split()[-1])
                        return volume
            elif self._alsa_available:
                # Use ALSA
                result = subprocess.run(['amixer', 'get', 'Master'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if '[' in line and '%' in line:
                            volume_str = line.split('[')[1].split('%')[0]
                            return int(volume_str)
            
            return 50  # Default volume
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return 50
    
    def set_volume(self, volume: int) -> bool:
        """Set system volume on Linux"""
        try:
            volume = max(0, min(100, volume))
            
            if self._pulse_audio_available:
                # Use PulseAudio
                result = subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume}%'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            elif self._alsa_available:
                # Use ALSA
                result = subprocess.run(['amixer', 'set', 'Master', f'{volume}%'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            
            return False
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return False
    
    def mute_volume(self) -> bool:
        """Mute system volume on Linux"""
        try:
            if self._pulse_audio_available:
                result = subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '1'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            elif self._alsa_available:
                result = subprocess.run(['amixer', 'set', 'Master', 'mute'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            
            return False
        except Exception as e:
            logger.error(f"Failed to mute volume: {e}")
            return False
    
    def unmute_volume(self) -> bool:
        """Unmute system volume on Linux"""
        try:
            if self._pulse_audio_available:
                result = subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', '0'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            elif self._alsa_available:
                result = subprocess.run(['amixer', 'set', 'Master', 'unmute'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            
            return False
        except Exception as e:
            logger.error(f"Failed to unmute volume: {e}")
            return False
    
    def get_brightness(self) -> int:
        """Get current display brightness on Linux"""
        try:
            # Try different brightness control methods
            brightness_paths = [
                '/sys/class/backlight/intel_backlight/brightness',
                '/sys/class/backlight/acpi_video0/brightness',
                '/sys/class/backlight/nvidia_backlight/brightness'
            ]
            
            for path in brightness_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        current = int(f.read().strip())
                    
                    # Get max brightness
                    max_path = path.replace('brightness', 'max_brightness')
                    if os.path.exists(max_path):
                        with open(max_path, 'r') as f:
                            max_brightness = int(f.read().strip())
                        return int((current / max_brightness) * 100)
            
            return 50  # Default brightness
        except Exception as e:
            logger.error(f"Failed to get brightness: {e}")
            return 50
    
    def set_brightness(self, brightness: int) -> bool:
        """Set display brightness on Linux"""
        try:
            brightness = max(0, min(100, brightness))
            
            # Try different brightness control methods
            brightness_paths = [
                '/sys/class/backlight/intel_backlight/brightness',
                '/sys/class/backlight/acpi_video0/brightness',
                '/sys/class/backlight/nvidia_backlight/brightness'
            ]
            
            for path in brightness_paths:
                if os.path.exists(path):
                    # Get max brightness
                    max_path = path.replace('brightness', 'max_brightness')
                    if os.path.exists(max_path):
                        with open(max_path, 'r') as f:
                            max_brightness = int(f.read().strip())
                        
                        # Calculate new brightness value
                        new_brightness = int((brightness / 100) * max_brightness)
                        
                        # Write new brightness
                        with open(path, 'w') as f:
                            f.write(str(new_brightness))
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return False
    
    def get_power_status(self) -> Dict[str, Any]:
        """Get power management status on Linux"""
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
        """Shutdown Linux system"""
        try:
            if delay > 0:
                cmd = f"shutdown -h +{delay//60}"
            else:
                cmd = "shutdown -h now"
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to shutdown: {e}")
            return False
    
    def restart(self, delay: int = 0) -> bool:
        """Restart Linux system"""
        try:
            if delay > 0:
                cmd = f"shutdown -r +{delay//60}"
            else:
                cmd = "shutdown -r now"
            subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to restart: {e}")
            return False
    
    def sleep(self) -> bool:
        """Put Linux system to sleep"""
        try:
            subprocess.run("systemctl suspend", shell=True, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to sleep: {e}")
            return False
    
    def hibernate(self) -> bool:
        """Hibernate Linux system"""
        try:
            subprocess.run("systemctl hibernate", shell=True, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to hibernate: {e}")
            return False
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get list of running processes on Linux"""
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
        """Kill a process by ID on Linux"""
        try:
            process = psutil.Process(process_id)
            process.terminate()
            return True
        except Exception as e:
            logger.error(f"Failed to kill process {process_id}: {e}")
            return False
    
    def start_process(self, command: str, args: List[str] = None) -> Optional[int]:
        """Start a new process on Linux"""
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
        """Get user home directory on Linux"""
        return str(Path.home())
    
    def get_temp_directory(self) -> str:
        """Get temporary directory on Linux"""
        return tempfile.gettempdir()
    
    def get_app_data_directory(self) -> str:
        """Get application data directory on Linux"""
        return str(Path.home() / ".local" / "share")
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """Get network interface information on Linux"""
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
        """Get primary IP address on Linux"""
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
        """Get active window information on Linux"""
        try:
            # Use xdotool if available
            result = subprocess.run(['xdotool', 'getactivewindow'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                window_id = int(result.stdout.strip())
                title_result = subprocess.run(['xdotool', 'getwindowname', str(window_id)], 
                                            capture_output=True, text=True)
                title = title_result.stdout.strip() if title_result.returncode == 0 else ""
                
                return {
                    'window_id': window_id,
                    'title': title
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of all windows on Linux"""
        try:
            windows = []
            # Use xdotool if available
            result = subprocess.run(['xdotool', 'search', '--name', ''], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for window_id_str in result.stdout.strip().split('\n'):
                    if window_id_str:
                        window_id = int(window_id_str)
                        title_result = subprocess.run(['xdotool', 'getwindowname', window_id_str], 
                                                    capture_output=True, text=True)
                        title = title_result.stdout.strip() if title_result.returncode == 0 else ""
                        
                        windows.append({
                            'window_id': window_id,
                            'title': title
                        })
            return windows
        except Exception as e:
            logger.error(f"Failed to get window list: {e}")
            return []
    
    def focus_window(self, window_id: int) -> bool:
        """Focus a specific window on Linux"""
        try:
            result = subprocess.run(['xdotool', 'windowactivate', str(window_id)], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to focus window {window_id}: {e}")
            return False
    
    def minimize_window(self, window_id: int) -> bool:
        """Minimize a window on Linux"""
        try:
            result = subprocess.run(['xdotool', 'windowminimize', str(window_id)], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to minimize window {window_id}: {e}")
            return False
    
    def maximize_window(self, window_id: int) -> bool:
        """Maximize a window on Linux"""
        try:
            result = subprocess.run(['xdotool', 'windowstate', str(window_id), 'maximized'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to maximize window {window_id}: {e}")
            return False
    
    def close_window(self, window_id: int) -> bool:
        """Close a window on Linux"""
        try:
            result = subprocess.run(['xdotool', 'windowclose', str(window_id)], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to close window {window_id}: {e}")
            return False
    
    def take_screenshot(self, file_path: str) -> bool:
        """Take a screenshot on Linux"""
        try:
            # Try different screenshot tools
            tools = ['gnome-screenshot', 'scrot', 'import']
            
            for tool in tools:
                if shutil.which(tool):
                    if tool == 'gnome-screenshot':
                        result = subprocess.run([tool, '-f', file_path], 
                                              capture_output=True, text=True)
                    elif tool == 'scrot':
                        result = subprocess.run([tool, file_path], 
                                              capture_output=True, text=True)
                    elif tool == 'import':
                        result = subprocess.run([tool, file_path], 
                                              capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    def get_clipboard_text(self) -> Optional[str]:
        """Get clipboard text content on Linux"""
        try:
            # Try different clipboard tools
            tools = ['xclip', 'xsel']
            
            for tool in tools:
                if shutil.which(tool):
                    if tool == 'xclip':
                        result = subprocess.run([tool, '-selection', 'clipboard', '-o'], 
                                              capture_output=True, text=True)
                    elif tool == 'xsel':
                        result = subprocess.run([tool, '-b'], 
                                              capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        return result.stdout.strip()
            
            return None
        except Exception as e:
            logger.error(f"Failed to get clipboard text: {e}")
            return None
    
    def set_clipboard_text(self, text: str) -> bool:
        """Set clipboard text content on Linux"""
        try:
            # Try different clipboard tools
            tools = ['xclip', 'xsel']
            
            for tool in tools:
                if shutil.which(tool):
                    if tool == 'xclip':
                        result = subprocess.run([tool, '-selection', 'clipboard'], 
                                              input=text, text=True)
                    elif tool == 'xsel':
                        result = subprocess.run([tool, '-b', '-i'], 
                                              input=text, text=True)
                    
                    if result.returncode == 0:
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to set clipboard text: {e}")
            return False
    
    def show_notification(self, title: str, message: str, duration: int = 5) -> bool:
        """Show system notification on Linux"""
        try:
            # Try different notification tools
            tools = ['notify-send', 'kdialog', 'zenity']
            
            for tool in tools:
                if shutil.which(tool):
                    if tool == 'notify-send':
                        result = subprocess.run([tool, title, message, '-t', str(duration * 1000)], 
                                              capture_output=True, text=True)
                    elif tool == 'kdialog':
                        result = subprocess.run([tool, '--passivepopup', f"{title}: {message}", str(duration)], 
                                              capture_output=True, text=True)
                    elif tool == 'zenity':
                        result = subprocess.run([tool, '--info', '--text', f"{title}: {message}", '--timeout', str(duration)], 
                                              capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
            return False
    
    def execute_command(self, command: str, args: List[str] = None, 
                       timeout: int = 30) -> Tuple[int, str, str]:
        """Execute a system command on Linux"""
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
        """Get the default shell command for Linux"""
        return "bash"
    
    def get_platform_features(self) -> List[str]:
        """Get list of Linux-specific features"""
        features = [
            "pulse_audio",
            "alsa_audio",
            "x11_windows",
            "wayland_windows",
            "systemd",
            "dbus",
            "bash_shell",
            "zsh_shell",
            "fish_shell"
        ]
        
        # Check for available features
        if shutil.which("pactl"):
            features.append("pulse_audio_available")
        if shutil.which("amixer"):
            features.append("alsa_available")
        if shutil.which("xdotool"):
            features.append("x11_tools")
        if shutil.which("notify-send"):
            features.append("notifications")
        
        return features
    
    def is_feature_available(self, feature: str) -> bool:
        """Check if a specific feature is available on Linux"""
        try:
            if feature == "pulse_audio":
                return shutil.which("pactl") is not None
            elif feature == "alsa_audio":
                return shutil.which("amixer") is not None
            elif feature == "x11_windows":
                return shutil.which("xdotool") is not None
            elif feature == "wayland_windows":
                return "WAYLAND_DISPLAY" in os.environ
            elif feature == "systemd":
                return shutil.which("systemctl") is not None
            elif feature == "dbus":
                return shutil.which("dbus-send") is not None
            elif feature == "bash_shell":
                return shutil.which("bash") is not None
            elif feature == "zsh_shell":
                return shutil.which("zsh") is not None
            elif feature == "fish_shell":
                return shutil.which("fish") is not None
            elif feature == "notifications":
                return shutil.which("notify-send") is not None
            else:
                return False
        except Exception:
            return False
    
    def _cleanup_platform(self) -> None:
        """Cleanup Linux-specific resources"""
        try:
            self._pulse_audio_available = False
            self._alsa_available = False
            logger.info("Linux platform cleaned up")
        except Exception as e:
            logger.error(f"Failed to cleanup Linux platform: {e}")
