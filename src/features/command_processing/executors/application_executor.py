"""
Application Command Executor
Handles application control commands (open, close, switch, list)
"""

import asyncio
import logging
import subprocess
import psutil
from typing import Dict, Any, Optional, List
import platform
import time

from ..command_classifier import CommandCategory
from ..nlp_engine import ProcessedCommand, IntentType
from ..command_executor import BaseExecutor, CommandResult, ExecutionStatus

logger = logging.getLogger(__name__)


class ApplicationManager:
    """Manages application operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
        self._app_mappings = self._setup_app_mappings()
        self._running_apps = {}
    
    def _setup_app_mappings(self) -> Dict[str, Dict[str, str]]:
        """Setup application name mappings for different platforms"""
        if self.platform == "windows":
            return {
                "cursor": {"executable": "Cursor.exe", "path": ""},
                "vscode": {"executable": "Code.exe", "path": ""},
                "chrome": {"executable": "chrome.exe", "path": ""},
                "firefox": {"executable": "firefox.exe", "path": ""},
                "edge": {"executable": "msedge.exe", "path": ""},
                "notepad": {"executable": "notepad.exe", "path": ""},
                "calculator": {"executable": "calc.exe", "path": ""},
                "explorer": {"executable": "explorer.exe", "path": ""},
                "word": {"executable": "WINWORD.EXE", "path": ""},
                "excel": {"executable": "EXCEL.EXE", "path": ""},
                "powerpoint": {"executable": "POWERPNT.EXE", "path": ""}
            }
        elif self.platform == "linux":
            return {
                "cursor": {"executable": "cursor", "path": ""},
                "vscode": {"executable": "code", "path": ""},
                "chrome": {"executable": "google-chrome", "path": ""},
                "firefox": {"executable": "firefox", "path": ""},
                "gedit": {"executable": "gedit", "path": ""},
                "calculator": {"executable": "gnome-calculator", "path": ""},
                "nautilus": {"executable": "nautilus", "path": ""},
                "libreoffice": {"executable": "libreoffice", "path": ""}
            }
        else:
            return {}
    
    def get_app_executable(self, app_name: str) -> Optional[str]:
        """Get executable path for application"""
        app_info = self._app_mappings.get(app_name.lower())
        if app_info:
            return app_info["executable"]
        return None
    
    def get_running_applications(self) -> List[Dict[str, Any]]:
        """Get list of currently running applications"""
        running_apps = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['name']:
                        running_apps.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'exe': proc_info['exe'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_percent': proc_info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Error getting running applications: {e}")
        
        return running_apps
    
    def is_app_running(self, app_name: str) -> bool:
        """Check if application is running"""
        running_apps = self.get_running_applications()
        executable = self.get_app_executable(app_name)
        
        if not executable:
            return False
        
        for app in running_apps:
            if app['name'].lower() == executable.lower():
                return True
        
        return False
    
    async def launch_application(self, app_name: str) -> bool:
        """Launch an application"""
        try:
            executable = self.get_app_executable(app_name)
            if not executable:
                self.logger.error(f"Unknown application: {app_name}")
                return False
            
            # Check if already running
            if self.is_app_running(app_name):
                self.logger.info(f"Application {app_name} is already running")
                return True
            
            # Launch application
            if self.platform == "windows":
                # Use start command on Windows
                subprocess.Popen([executable], shell=True)
            else:
                # Use direct execution on Linux
                subprocess.Popen([executable])
            
            # Wait a bit and check if it started
            await asyncio.sleep(1)
            
            if self.is_app_running(app_name):
                self.logger.info(f"Successfully launched {app_name}")
                return True
            else:
                self.logger.error(f"Failed to launch {app_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error launching {app_name}: {e}")
            return False
    
    async def close_application(self, app_name: str) -> bool:
        """Close an application"""
        try:
            executable = self.get_app_executable(app_name)
            if not executable:
                self.logger.error(f"Unknown application: {app_name}")
                return False
            
            running_apps = self.get_running_applications()
            closed_any = False
            
            for app in running_apps:
                if app['name'].lower() == executable.lower():
                    try:
                        proc = psutil.Process(app['pid'])
                        proc.terminate()
                        closed_any = True
                        self.logger.info(f"Terminated {app_name} (PID: {app['pid']})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        self.logger.warning(f"Could not terminate {app_name}: {e}")
            
            if closed_any:
                # Wait for process to close
                await asyncio.sleep(1)
                return not self.is_app_running(app_name)
            else:
                self.logger.warning(f"No running instances of {app_name} found")
                return True
                
        except Exception as e:
            self.logger.error(f"Error closing {app_name}: {e}")
            return False
    
    def find_application_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find application by name (fuzzy matching)"""
        running_apps = self.get_running_applications()
        
        # Exact match first
        for app in running_apps:
            if app['name'].lower() == name.lower():
                return app
        
        # Fuzzy match
        for app in running_apps:
            if name.lower() in app['name'].lower():
                return app
        
        return None


class ApplicationExecutor(BaseExecutor):
    """Executor for application control commands"""
    
    def __init__(self):
        super().__init__()
        self.app_manager = ApplicationManager()
        self._is_running = False
    
    def can_handle(self, command: ProcessedCommand) -> bool:
        """Check if this executor can handle the command"""
        return command.category == CommandCategory.APPLICATION
    
    async def execute(self, command: ProcessedCommand) -> CommandResult:
        """Execute application command"""
        try:
            self._is_running = True
            self.logger.info(f"Executing application command: {command.action}")
            
            if command.action == "open_app":
                return await self._execute_open_app(command)
            elif command.action == "close_app":
                return await self._execute_close_app(command)
            elif command.action == "switch_app":
                return await self._execute_switch_app(command)
            elif command.action == "list_apps":
                return await self._execute_list_apps(command)
            else:
                return self._create_result(
                    success=False,
                    message=f"Unknown application action: {command.action}",
                    status=ExecutionStatus.FAILED
                )
        
        except Exception as e:
            self.logger.error(f"Error executing application command: {e}")
            return self._create_result(
                success=False,
                message=f"Error executing application command: {e}",
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
        finally:
            self._is_running = False
    
    async def _execute_open_app(self, command: ProcessedCommand) -> CommandResult:
        """Execute open application command"""
        app_name = command.parameters.get('app_name', '')
        if not app_name:
            return self._create_result(
                success=False,
                message="No application name provided",
                status=ExecutionStatus.FAILED
            )
        
        # Check if already running
        if self.app_manager.is_app_running(app_name):
            return self._create_result(
                success=True,
                message=f"{app_name} is already running",
                data={"app_name": app_name, "status": "already_running"}
            )
        
        # Launch application
        success = await self.app_manager.launch_application(app_name)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Successfully opened {app_name}",
                data={"app_name": app_name, "status": "opened"}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to open {app_name}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_close_app(self, command: ProcessedCommand) -> CommandResult:
        """Execute close application command"""
        app_name = command.parameters.get('app_name', '')
        if not app_name:
            return self._create_result(
                success=False,
                message="No application name provided",
                status=ExecutionStatus.FAILED
            )
        
        # Check if running
        if not self.app_manager.is_app_running(app_name):
            return self._create_result(
                success=True,
                message=f"{app_name} is not running",
                data={"app_name": app_name, "status": "not_running"}
            )
        
        # Close application
        success = await self.app_manager.close_application(app_name)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Successfully closed {app_name}",
                data={"app_name": app_name, "status": "closed"}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to close {app_name}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_switch_app(self, command: ProcessedCommand) -> CommandResult:
        """Execute switch application command"""
        app_name = command.parameters.get('app_name', '')
        if not app_name:
            return self._create_result(
                success=False,
                message="No application name provided",
                status=ExecutionStatus.FAILED
            )
        
        # Find application
        app_info = self.app_manager.find_application_by_name(app_name)
        if not app_info:
            return self._create_result(
                success=False,
                message=f"Application {app_name} not found",
                status=ExecutionStatus.FAILED
            )
        
        # Try to bring to front (platform-specific)
        try:
            if platform.system().lower() == "windows":
                import win32gui
                import win32con
                
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        if app_name.lower() in window_text.lower():
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    win32gui.SetForegroundWindow(windows[0])
                    return self._create_result(
                        success=True,
                        message=f"Switched to {app_name}",
                        data={"app_name": app_name, "status": "switched"}
                    )
                else:
                    return self._create_result(
                        success=False,
                        message=f"Could not find window for {app_name}",
                        status=ExecutionStatus.FAILED
                    )
            else:
                # Linux - use wmctrl if available
                try:
                    subprocess.run(['wmctrl', '-a', app_name], check=True)
                    return self._create_result(
                        success=True,
                        message=f"Switched to {app_name}",
                        data={"app_name": app_name, "status": "switched"}
                    )
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return self._create_result(
                        success=False,
                        message=f"Could not switch to {app_name} (wmctrl not available)",
                        status=ExecutionStatus.FAILED
                    )
        
        except Exception as e:
            self.logger.error(f"Error switching to {app_name}: {e}")
            return self._create_result(
                success=False,
                message=f"Error switching to {app_name}: {e}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_list_apps(self, command: ProcessedCommand) -> CommandResult:
        """Execute list applications command"""
        try:
            running_apps = self.app_manager.get_running_applications()
            
            # Filter and format applications
            formatted_apps = []
            for app in running_apps:
                formatted_apps.append({
                    'name': app['name'],
                    'pid': app['pid'],
                    'cpu_percent': app['cpu_percent'],
                    'memory_percent': app['memory_percent']
                })
            
            # Sort by name
            formatted_apps.sort(key=lambda x: x['name'])
            
            return self._create_result(
                success=True,
                message=f"Found {len(formatted_apps)} running applications",
                data={"applications": formatted_apps, "count": len(formatted_apps)}
            )
        
        except Exception as e:
            self.logger.error(f"Error listing applications: {e}")
            return self._create_result(
                success=False,
                message=f"Error listing applications: {e}",
                status=ExecutionStatus.FAILED
            )
    
    def cleanup(self) -> None:
        """Cleanup executor resources"""
        self._is_running = False
        self.logger.info("Application executor cleaned up")
