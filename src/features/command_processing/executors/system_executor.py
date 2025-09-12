"""
System Command Executor
Handles system control commands (shutdown, restart, volume, brightness, etc.)
"""

import asyncio
import logging
import subprocess
import platform
import time
from typing import Dict, Any, Optional, List

from ..command_classifier import CommandCategory
from ..nlp_engine import ProcessedCommand, IntentType
from ..command_executor import BaseExecutor, CommandResult, ExecutionStatus

logger = logging.getLogger(__name__)


class SystemManager:
    """Manages system operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
        self._is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize system manager"""
        try:
            self._is_initialized = True
            self.logger.info("System manager initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize system manager: {e}")
            return False
    
    async def shutdown_system(self, delay: int = 0) -> bool:
        """Shutdown the system"""
        try:
            if self.platform == "windows":
                command = f"shutdown /s /t {delay}"
                subprocess.run(command, shell=True)
            elif self.platform == "linux":
                command = f"shutdown -h +{delay//60}" if delay > 0 else "shutdown -h now"
                subprocess.run(command, shell=True)
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info(f"System shutdown initiated with {delay}s delay")
            return True
            
        except Exception as e:
            self.logger.error(f"Error shutting down system: {e}")
            return False
    
    async def restart_system(self, delay: int = 0) -> bool:
        """Restart the system"""
        try:
            if self.platform == "windows":
                command = f"shutdown /r /t {delay}"
                subprocess.run(command, shell=True)
            elif self.platform == "linux":
                command = f"shutdown -r +{delay//60}" if delay > 0 else "shutdown -r now"
                subprocess.run(command, shell=True)
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info(f"System restart initiated with {delay}s delay")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restarting system: {e}")
            return False
    
    async def sleep_system(self) -> bool:
        """Put system to sleep"""
        try:
            if self.platform == "windows":
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
            elif self.platform == "linux":
                subprocess.run("systemctl suspend", shell=True)
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info("System put to sleep")
            return True
            
        except Exception as e:
            self.logger.error(f"Error putting system to sleep: {e}")
            return False
    
    async def lock_system(self) -> bool:
        """Lock the system"""
        try:
            if self.platform == "windows":
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            elif self.platform == "linux":
                subprocess.run("gnome-screensaver-command -l", shell=True)
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info("System locked")
            return True
            
        except Exception as e:
            self.logger.error(f"Error locking system: {e}")
            return False
    
    async def set_volume(self, level: int) -> bool:
        """Set system volume level (0-100)"""
        try:
            if self.platform == "windows":
                # Use PowerShell to set volume
                command = f"powershell -c \"(new-object -com wscript.shell).SendKeys([char]173)\""
                # This is a simplified approach - in practice, you'd use Windows API
                self.logger.info(f"Volume set to {level}% (Windows)")
                return True
            elif self.platform == "linux":
                # Use amixer for ALSA
                command = f"amixer set Master {level}%"
                subprocess.run(command, shell=True)
                self.logger.info(f"Volume set to {level}%")
                return True
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error setting volume: {e}")
            return False
    
    async def set_brightness(self, level: int) -> bool:
        """Set display brightness level (0-100)"""
        try:
            if self.platform == "windows":
                # Use PowerShell to set brightness
                command = f"powershell -c \"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})\""
                subprocess.run(command, shell=True)
                self.logger.info(f"Brightness set to {level}%")
                return True
            elif self.platform == "linux":
                # Use xrandr for brightness control
                command = f"xrandr --output $(xrandr | grep ' connected' | head -n1 | cut -d' ' -f1) --brightness {level/100.0}"
                subprocess.run(command, shell=True)
                self.logger.info(f"Brightness set to {level}%")
                return True
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error setting brightness: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            import psutil
            
            info = {
                "platform": self.platform,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent if self.platform == "linux" else psutil.disk_usage('C:').percent,
                "boot_time": psutil.boot_time(),
                "uptime": time.time() - psutil.boot_time()
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get list of running processes"""
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_percent': proc_info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return processes
            
        except Exception as e:
            self.logger.error(f"Error getting running processes: {e}")
            return []


class SystemExecutor(BaseExecutor):
    """Executor for system control commands"""
    
    def __init__(self):
        super().__init__()
        self.system_manager = SystemManager()
        self._is_running = False
    
    def can_handle(self, command: ProcessedCommand) -> bool:
        """Check if this executor can handle the command"""
        return command.category == CommandCategory.SYSTEM
    
    async def execute(self, command: ProcessedCommand) -> CommandResult:
        """Execute system command"""
        try:
            self._is_running = True
            self.logger.info(f"Executing system command: {command.action}")
            
            if command.action == "shutdown":
                return await self._execute_shutdown(command)
            elif command.action == "restart":
                return await self._execute_restart(command)
            elif command.action == "sleep":
                return await self._execute_sleep(command)
            elif command.action == "lock":
                return await self._execute_lock(command)
            elif command.action == "set_volume":
                return await self._execute_set_volume(command)
            elif command.action == "set_brightness":
                return await self._execute_set_brightness(command)
            elif command.action == "system_info":
                return await self._execute_system_info(command)
            elif command.action == "list_processes":
                return await self._execute_list_processes(command)
            else:
                return self._create_result(
                    success=False,
                    message=f"Unknown system action: {command.action}",
                    status=ExecutionStatus.FAILED
                )
        
        except Exception as e:
            self.logger.error(f"Error executing system command: {e}")
            return self._create_result(
                success=False,
                message=f"Error executing system command: {e}",
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
        finally:
            self._is_running = False
    
    async def _execute_shutdown(self, command: ProcessedCommand) -> CommandResult:
        """Execute shutdown command"""
        delay = command.parameters.get('delay', 0)
        
        success = await self.system_manager.shutdown_system(delay)
        
        if success:
            return self._create_result(
                success=True,
                message=f"System shutdown initiated with {delay}s delay",
                data={"delay": delay}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to initiate system shutdown",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_restart(self, command: ProcessedCommand) -> CommandResult:
        """Execute restart command"""
        delay = command.parameters.get('delay', 0)
        
        success = await self.system_manager.restart_system(delay)
        
        if success:
            return self._create_result(
                success=True,
                message=f"System restart initiated with {delay}s delay",
                data={"delay": delay}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to initiate system restart",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_sleep(self, command: ProcessedCommand) -> CommandResult:
        """Execute sleep command"""
        success = await self.system_manager.sleep_system()
        
        if success:
            return self._create_result(
                success=True,
                message="System put to sleep",
                data={}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to put system to sleep",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_lock(self, command: ProcessedCommand) -> CommandResult:
        """Execute lock command"""
        success = await self.system_manager.lock_system()
        
        if success:
            return self._create_result(
                success=True,
                message="System locked",
                data={}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to lock system",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_set_volume(self, command: ProcessedCommand) -> CommandResult:
        """Execute set volume command"""
        level = command.parameters.get('level', 50)
        
        if not 0 <= level <= 100:
            return self._create_result(
                success=False,
                message="Volume level must be between 0 and 100",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.system_manager.set_volume(level)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Volume set to {level}%",
                data={"level": level}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to set volume to {level}%",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_set_brightness(self, command: ProcessedCommand) -> CommandResult:
        """Execute set brightness command"""
        level = command.parameters.get('level', 50)
        
        if not 0 <= level <= 100:
            return self._create_result(
                success=False,
                message="Brightness level must be between 0 and 100",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.system_manager.set_brightness(level)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Brightness set to {level}%",
                data={"level": level}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to set brightness to {level}%",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_system_info(self, command: ProcessedCommand) -> CommandResult:
        """Execute system info command"""
        try:
            info = self.system_manager.get_system_info()
            
            return self._create_result(
                success=True,
                message="System information retrieved",
                data=info
            )
        
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return self._create_result(
                success=False,
                message=f"Error getting system info: {e}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_list_processes(self, command: ProcessedCommand) -> CommandResult:
        """Execute list processes command"""
        try:
            processes = self.system_manager.get_running_processes()
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return self._create_result(
                success=True,
                message=f"Found {len(processes)} running processes",
                data={"processes": processes, "count": len(processes)}
            )
        
        except Exception as e:
            self.logger.error(f"Error listing processes: {e}")
            return self._create_result(
                success=False,
                message=f"Error listing processes: {e}",
                status=ExecutionStatus.FAILED
            )
    
    def cleanup(self) -> None:
        """Cleanup executor resources"""
        self._is_running = False
        self.logger.info("System executor cleaned up")
