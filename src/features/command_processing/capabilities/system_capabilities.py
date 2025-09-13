"""
System Capability Executors

Implements concrete executors for system control operations including
shutdown, restart, volume control, brightness control, and system information.
"""

import asyncio
import logging
import platform
import subprocess
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..capability_system import BaseCapabilityExecutor

logger = logging.getLogger(__name__)

@dataclass
class SystemInfo:
    """System information data structure"""
    platform: str
    version: str
    architecture: str
    processor: str
    memory_total: int
    memory_available: int
    disk_usage: Dict[str, Any]
    uptime: float

class SystemShutdownExecutor(BaseCapabilityExecutor):
    """Executor for system shutdown and restart operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system shutdown or restart"""
        try:
            action = parameters.get('action', 'shutdown')
            delay = parameters.get('delay', 0)
            force = parameters.get('force', False)
            
            if delay > 0:
                await asyncio.sleep(delay)
            
            if platform.system() == "Windows":
                return await self._execute_windows_shutdown(action, force)
            else:
                return await self._execute_linux_shutdown(action, force)
                
        except Exception as e:
            logger.error(f"Error executing system shutdown: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if shutdown can be executed safely"""
        # Add safety checks - require explicit confirmation for shutdown
        if not context.get('user_confirmed', False):
            return False
        
        # Check if system is in a safe state
        return True
    
    async def _execute_windows_shutdown(self, action: str, force: bool) -> Dict[str, Any]:
        """Execute shutdown on Windows"""
        try:
            if action == "shutdown":
                cmd = ["shutdown", "/s", "/t", "0"]
            elif action == "restart":
                cmd = ["shutdown", "/r", "/t", "0"]
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            if force:
                cmd.append("/f")
            
            subprocess.run(cmd, check=True)
            return {"success": True, "message": f"System {action} initiated"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to execute {action}: {e}"}
    
    async def _execute_linux_shutdown(self, action: str, force: bool) -> Dict[str, Any]:
        """Execute shutdown on Linux"""
        try:
            if action == "shutdown":
                cmd = ["sudo", "shutdown", "-h", "now"]
            elif action == "restart":
                cmd = ["sudo", "shutdown", "-r", "now"]
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            subprocess.run(cmd, check=True)
            return {"success": True, "message": f"System {action} initiated"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Failed to execute {action}: {e}"}

class VolumeControlExecutor(BaseCapabilityExecutor):
    """Executor for audio volume control operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute volume control operation"""
        try:
            action = parameters.get('action', 'set')
            level = parameters.get('level', 50)
            
            if platform.system() == "Windows":
                return await self._execute_windows_volume_control(action, level)
            else:
                return await self._execute_linux_volume_control(action, level)
                
        except Exception as e:
            logger.error(f"Error executing volume control: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if volume control can be executed"""
        level = parameters.get('level', 50)
        return 0 <= level <= 100
    
    async def _execute_windows_volume_control(self, action: str, level: int) -> Dict[str, Any]:
        """Execute volume control on Windows"""
        try:
            import pycaw
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            
            if action == "set":
                volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            elif action == "increase":
                current_volume = volume.GetMasterVolumeLevelScalar()
                new_level = min(1.0, current_volume + (level / 100.0))
                volume.SetMasterVolumeLevelScalar(new_level, None)
            elif action == "decrease":
                current_volume = volume.GetMasterVolumeLevelScalar()
                new_level = max(0.0, current_volume - (level / 100.0))
                volume.SetMasterVolumeLevelScalar(new_level, None)
            elif action == "mute":
                volume.SetMute(True, None)
            elif action == "unmute":
                volume.SetMute(False, None)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            return {"success": True, "message": f"Volume {action} completed"}
            
        except ImportError:
            # Fallback to PowerShell command
            return await self._execute_windows_volume_powershell(action, level)
        except Exception as e:
            return {"success": False, "error": f"Volume control failed: {e}"}
    
    async def _execute_windows_volume_powershell(self, action: str, level: int) -> Dict[str, Any]:
        """Execute volume control using PowerShell"""
        try:
            if action == "set":
                cmd = f"powershell -Command \"(new-object -com wscript.shell).SendKeys([char]173)\""
            elif action == "mute":
                cmd = "powershell -Command \"(new-object -com wscript.shell).SendKeys([char]173)\""
            elif action == "unmute":
                cmd = "powershell -Command \"(new-object -com wscript.shell).SendKeys([char]174)\""
            else:
                return {"success": False, "error": f"Action {action} not supported via PowerShell"}
            
            subprocess.run(cmd, shell=True, check=True)
            return {"success": True, "message": f"Volume {action} completed via PowerShell"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"PowerShell volume control failed: {e}"}
    
    async def _execute_linux_volume_control(self, action: str, level: int) -> Dict[str, Any]:
        """Execute volume control on Linux"""
        try:
            if action == "set":
                cmd = ["amixer", "set", "Master", f"{level}%"]
            elif action == "increase":
                cmd = ["amixer", "set", "Master", f"{level}%+"]
            elif action == "decrease":
                cmd = ["amixer", "set", "Master", f"{level}%-"]
            elif action == "mute":
                cmd = ["amixer", "set", "Master", "mute"]
            elif action == "unmute":
                cmd = ["amixer", "set", "Master", "unmute"]
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            subprocess.run(cmd, check=True)
            return {"success": True, "message": f"Volume {action} completed"}
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Linux volume control failed: {e}"}

class BrightnessControlExecutor(BaseCapabilityExecutor):
    """Executor for display brightness control operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute brightness control operation"""
        try:
            action = parameters.get('action', 'set')
            level = parameters.get('level', 50)
            
            if platform.system() == "Windows":
                return await self._execute_windows_brightness_control(action, level)
            else:
                return await self._execute_linux_brightness_control(action, level)
                
        except Exception as e:
            logger.error(f"Error executing brightness control: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if brightness control can be executed"""
        level = parameters.get('level', 50)
        return 0 <= level <= 100
    
    async def _execute_windows_brightness_control(self, action: str, level: int) -> Dict[str, Any]:
        """Execute brightness control on Windows"""
        try:
            import wmi
            
            w = wmi.WMI(namespace='wmi')
            monitors = w.WmiMonitorBrightnessMethods()
            
            if not monitors:
                return {"success": False, "error": "No brightness controllable monitors found"}
            
            for monitor in monitors:
                if action == "set":
                    monitor.WmiSetBrightness(level, 0)
                elif action == "increase":
                    # Get current brightness and increase
                    current = monitor.WmiGetBrightness()[0]
                    new_level = min(100, current + level)
                    monitor.WmiSetBrightness(new_level, 0)
                elif action == "decrease":
                    # Get current brightness and decrease
                    current = monitor.WmiGetBrightness()[0]
                    new_level = max(0, current - level)
                    monitor.WmiSetBrightness(new_level, 0)
                else:
                    return {"success": False, "error": f"Unknown action: {action}"}
            
            return {"success": True, "message": f"Brightness {action} completed"}
            
        except ImportError:
            return {"success": False, "error": "WMI library not available for brightness control"}
        except Exception as e:
            return {"success": False, "error": f"Windows brightness control failed: {e}"}
    
    async def _execute_linux_brightness_control(self, action: str, level: int) -> Dict[str, Any]:
        """Execute brightness control on Linux"""
        try:
            import os
            
            # Find brightness control files
            brightness_paths = [
                "/sys/class/backlight/intel_backlight/brightness",
                "/sys/class/backlight/acpi_video0/brightness",
                "/sys/class/backlight/amdgpu_bl0/brightness"
            ]
            
            brightness_path = None
            max_brightness_path = None
            
            for path in brightness_paths:
                if os.path.exists(path):
                    brightness_path = path
                    max_brightness_path = path.replace("brightness", "max_brightness")
                    break
            
            if not brightness_path:
                return {"success": False, "error": "No brightness control found"}
            
            # Read max brightness
            with open(max_brightness_path, 'r') as f:
                max_brightness = int(f.read().strip())
            
            if action == "set":
                new_brightness = int((level / 100.0) * max_brightness)
            elif action == "increase":
                with open(brightness_path, 'r') as f:
                    current = int(f.read().strip())
                new_brightness = min(max_brightness, current + int((level / 100.0) * max_brightness))
            elif action == "decrease":
                with open(brightness_path, 'r') as f:
                    current = int(f.read().strip())
                new_brightness = max(0, current - int((level / 100.0) * max_brightness))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            # Write new brightness
            with open(brightness_path, 'w') as f:
                f.write(str(new_brightness))
            
            return {"success": True, "message": f"Brightness {action} completed"}
            
        except Exception as e:
            return {"success": False, "error": f"Linux brightness control failed: {e}"}

class SystemInfoExecutor(BaseCapabilityExecutor):
    """Executor for system information retrieval"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system information retrieval"""
        try:
            info_type = parameters.get('info_type', 'all')
            
            if info_type == "all":
                return await self._get_all_system_info()
            elif info_type == "memory":
                return await self._get_memory_info()
            elif info_type == "disk":
                return await self._get_disk_info()
            elif info_type == "processes":
                return await self._get_process_info()
            else:
                return {"success": False, "error": f"Unknown info type: {info_type}"}
                
        except Exception as e:
            logger.error(f"Error executing system info: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if system info can be retrieved"""
        return True
    
    async def _get_all_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            import psutil
            
            system_info = {
                "platform": platform.system(),
                "version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": {},
                "uptime": time.time() - psutil.boot_time(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1)
            }
            
            # Get disk usage for all mounted drives
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    system_info["disk_usage"][partition.device] = {
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue
            
            return {"success": True, "data": system_info}
            
        except ImportError:
            return {"success": False, "error": "psutil library not available"}
        except Exception as e:
            return {"success": False, "error": f"Failed to get system info: {e}"}
    
    async def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent
            }
            
            return {"success": True, "data": memory_info}
            
        except ImportError:
            return {"success": False, "error": "psutil library not available"}
        except Exception as e:
            return {"success": False, "error": f"Failed to get memory info: {e}"}
    
    async def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            import psutil
            
            disk_info = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue
            
            return {"success": True, "data": disk_info}
            
        except ImportError:
            return {"success": False, "error": "psutil library not available"}
        except Exception as e:
            return {"success": False, "error": f"Failed to get disk info: {e}"}
    
    async def _get_process_info(self) -> Dict[str, Any]:
        """Get process information"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            return {"success": True, "data": processes[:20]}  # Top 20 processes
            
        except ImportError:
            return {"success": False, "error": "psutil library not available"}
        except Exception as e:
            return {"success": False, "error": f"Failed to get process info: {e}"}

# Export all executors
__all__ = [
    'SystemShutdownExecutor',
    'VolumeControlExecutor', 
    'BrightnessControlExecutor',
    'SystemInfoExecutor'
]
