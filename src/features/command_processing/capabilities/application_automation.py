"""
Application Automation Capabilities for JARVIS Computer Assistant

Provides advanced application control, automation, and workflow orchestration.
"""

import asyncio
import logging
import os
import time
import subprocess
import psutil
import platform
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class ApplicationState(Enum):
    """Application states"""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    UNKNOWN = "unknown"

class ApplicationAction(Enum):
    """Application actions"""
    LAUNCH = "launch"
    CLOSE = "close"
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    RESTORE = "restore"
    FOCUS = "focus"
    SEND_KEY = "send_key"
    SEND_TEXT = "send_text"
    CLICK = "click"
    SCREENSHOT = "screenshot"

@dataclass
class ApplicationInfo:
    """Application information"""
    name: str
    process_id: int
    window_title: str
    executable_path: str
    state: ApplicationState
    memory_usage: int
    cpu_usage: float
    start_time: datetime
    window_handle: Optional[int] = None

@dataclass
class ApplicationActionResult:
    """Result of application action"""
    success: bool
    action: ApplicationAction
    application_name: str
    execution_time: float
    error: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowStep:
    """Workflow step definition"""
    step_id: str
    application_name: str
    action: ApplicationAction
    parameters: Dict[str, Any]
    delay_after: float = 0.0
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    success: bool
    workflow_name: str
    steps_executed: int
    total_steps: int
    execution_time: float
    errors: List[str] = None
    step_results: List[ApplicationActionResult] = None

class ApplicationDetector:
    """Detects and monitors applications"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
    
    def get_running_applications(self) -> List[ApplicationInfo]:
        """Get list of running applications"""
        applications = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time', 'memory_info', 'cpu_percent']):
                try:
                    # Skip system processes
                    if proc.info['pid'] == 0 or proc.info['name'] in ['System', 'Idle']:
                        continue
                    
                    app_info = ApplicationInfo(
                        name=proc.info['name'],
                        process_id=proc.info['pid'],
                        window_title=proc.info['name'],
                        executable_path=proc.info['exe'] or '',
                        state=ApplicationState.RUNNING,
                        memory_usage=proc.info['memory_info'].rss if proc.info['memory_info'] else 0,
                        cpu_usage=proc.info['cpu_percent'] or 0.0,
                        start_time=datetime.fromtimestamp(proc.info['create_time'])
                    )
                    
                    applications.append(app_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error getting running applications: {e}")
        
        return applications
    
    def find_application_by_name(self, name: str) -> Optional[ApplicationInfo]:
        """Find application by name"""
        applications = self.get_running_applications()
        
        for app in applications:
            if name.lower() in app.name.lower():
                return app
        
        return None
    
    def find_application_by_pid(self, pid: int) -> Optional[ApplicationInfo]:
        """Find application by process ID"""
        applications = self.get_running_applications()
        
        for app in applications:
            if app.process_id == pid:
                return app
        
        return None
    
    def is_application_running(self, name: str) -> bool:
        """Check if application is running"""
        return self.find_application_by_name(name) is not None

class ApplicationController:
    """Controls application operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.detector = ApplicationDetector()
        self.platform = platform.system().lower()
    
    async def launch_application(self, app_name: str, app_path: str = "", 
                               arguments: List[str] = None) -> ApplicationActionResult:
        """Launch an application"""
        start_time = time.time()
        
        try:
            if not app_path:
                app_path = await self._find_application_path(app_name)
                if not app_path:
                    return ApplicationActionResult(
                        success=False,
                        action=ApplicationAction.LAUNCH,
                        application_name=app_name,
                        execution_time=time.time() - start_time,
                        error=f"Application not found: {app_name}"
                    )
            
            # Prepare command
            cmd = [app_path]
            if arguments:
                cmd.extend(arguments)
            
            # Launch application
            if self.platform == "windows":
                # Use CREATE_NEW_PROCESS_GROUP on Windows
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                subprocess.Popen(cmd)
            
            # Wait a moment for application to start
            await asyncio.sleep(1.0)
            
            # Verify application started
            if self.detector.is_application_running(app_name):
                return ApplicationActionResult(
                    success=True,
                    action=ApplicationAction.LAUNCH,
                    application_name=app_name,
                    execution_time=time.time() - start_time,
                    result_data={"app_path": app_path, "arguments": arguments}
                )
            else:
                return ApplicationActionResult(
                    success=False,
                    action=ApplicationAction.LAUNCH,
                    application_name=app_name,
                    execution_time=time.time() - start_time,
                    error="Application failed to start"
                )
                
        except Exception as e:
            return ApplicationActionResult(
                success=False,
                action=ApplicationAction.LAUNCH,
                application_name=app_name,
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    async def close_application(self, app_name: str, force: bool = False) -> ApplicationActionResult:
        """Close an application"""
        start_time = time.time()
        
        try:
            app_info = self.detector.find_application_by_name(app_name)
            if not app_info:
                return ApplicationActionResult(
                    success=False,
                    action=ApplicationAction.CLOSE,
                    application_name=app_name,
                    execution_time=time.time() - start_time,
                    error=f"Application not running: {app_name}"
                )
            
            # Close application
            if force:
                if self.platform == "windows":
                    subprocess.run(["taskkill", "/f", "/pid", str(app_info.process_id)], 
                                 check=False, capture_output=True)
                else:
                    subprocess.run(["kill", "-9", str(app_info.process_id)], 
                                 check=False, capture_output=True)
            else:
                if self.platform == "windows":
                    subprocess.run(["taskkill", "/pid", str(app_info.process_id)], 
                                 check=False, capture_output=True)
                else:
                    subprocess.run(["kill", str(app_info.process_id)], 
                                 check=False, capture_output=True)
            
            # Wait for application to close
            await asyncio.sleep(1.0)
            
            # Verify application closed
            if not self.detector.is_application_running(app_name):
                return ApplicationActionResult(
                    success=True,
                    action=ApplicationAction.CLOSE,
                    application_name=app_name,
                    execution_time=time.time() - start_time
                )
            else:
                return ApplicationActionResult(
                    success=False,
                    action=ApplicationAction.CLOSE,
                    application_name=app_name,
                    execution_time=time.time() - start_time,
                    error="Application failed to close"
                )
                
        except Exception as e:
            return ApplicationActionResult(
                success=False,
                action=ApplicationAction.CLOSE,
                application_name=app_name,
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    async def send_key_to_application(self, app_name: str, key: str) -> ApplicationActionResult:
        """Send key to application"""
        start_time = time.time()
        
        try:
            app_info = self.detector.find_application_by_name(app_name)
            if not app_info:
                return ApplicationActionResult(
                    success=False,
                    action=ApplicationAction.SEND_KEY,
                    application_name=app_name,
                    execution_time=time.time() - start_time,
                    error=f"Application not running: {app_name}"
                )
            
            # Send key using platform-specific method
            if self.platform == "windows":
                await self._send_key_windows(key)
            else:
                await self._send_key_linux(key)
            
            return ApplicationActionResult(
                success=True,
                action=ApplicationAction.SEND_KEY,
                application_name=app_name,
                execution_time=time.time() - start_time,
                result_data={"key": key}
            )
            
        except Exception as e:
            return ApplicationActionResult(
                success=False,
                action=ApplicationAction.SEND_KEY,
                application_name=app_name,
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    async def send_text_to_application(self, app_name: str, text: str) -> ApplicationActionResult:
        """Send text to application"""
        start_time = time.time()
        
        try:
            app_info = self.detector.find_application_by_name(app_name)
            if not app_info:
                return ApplicationActionResult(
                    success=False,
                    action=ApplicationAction.SEND_TEXT,
                    application_name=app_name,
                    execution_time=time.time() - start_time,
                    error=f"Application not running: {app_name}"
                )
            
            # Send text using platform-specific method
            if self.platform == "windows":
                await self._send_text_windows(text)
            else:
                await self._send_text_linux(text)
            
            return ApplicationActionResult(
                success=True,
                action=ApplicationAction.SEND_TEXT,
                application_name=app_name,
                execution_time=time.time() - start_time,
                result_data={"text": text}
            )
            
        except Exception as e:
            return ApplicationActionResult(
                success=False,
                action=ApplicationAction.SEND_TEXT,
                application_name=app_name,
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    async def take_screenshot(self, app_name: str = None) -> ApplicationActionResult:
        """Take screenshot of application or entire screen"""
        start_time = time.time()
        
        try:
            # This would require additional libraries like PIL, pyautogui, etc.
            # For now, we'll simulate the operation
            screenshot_path = f"screenshot_{int(time.time())}.png"
            
            # Simulate screenshot taking
            await asyncio.sleep(0.1)
            
            return ApplicationActionResult(
                success=True,
                action=ApplicationAction.SCREENSHOT,
                application_name=app_name or "screen",
                execution_time=time.time() - start_time,
                result_data={"screenshot_path": screenshot_path}
            )
            
        except Exception as e:
            return ApplicationActionResult(
                success=False,
                action=ApplicationAction.SCREENSHOT,
                application_name=app_name or "screen",
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    async def _find_application_path(self, app_name: str) -> Optional[str]:
        """Find application executable path"""
        # Common application paths
        common_paths = {
            "notepad": "notepad.exe" if self.platform == "windows" else "gedit",
            "calculator": "calc.exe" if self.platform == "windows" else "gnome-calculator",
            "chrome": "chrome.exe" if self.platform == "windows" else "google-chrome",
            "firefox": "firefox.exe" if self.platform == "windows" else "firefox",
            "vscode": "code.exe" if self.platform == "windows" else "code",
            "explorer": "explorer.exe" if self.platform == "windows" else "nautilus"
        }
        
        return common_paths.get(app_name.lower())
    
    async def _send_key_windows(self, key: str):
        """Send key on Windows"""
        # This would use Windows API or pyautogui
        # For now, we'll simulate
        await asyncio.sleep(0.1)
    
    async def _send_key_linux(self, key: str):
        """Send key on Linux"""
        # This would use xdotool or similar
        # For now, we'll simulate
        await asyncio.sleep(0.1)
    
    async def _send_text_windows(self, text: str):
        """Send text on Windows"""
        # This would use Windows API or pyautogui
        # For now, we'll simulate
        await asyncio.sleep(0.1)
    
    async def _send_text_linux(self, text: str):
        """Send text on Linux"""
        # This would use xdotool or similar
        # For now, we'll simulate
        await asyncio.sleep(0.1)

class WorkflowOrchestrator:
    """Orchestrates application workflows"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.controller = ApplicationController()
        self.workflows: Dict[str, List[WorkflowStep]] = {}
    
    def register_workflow(self, name: str, steps: List[WorkflowStep]) -> bool:
        """Register a workflow"""
        try:
            self.workflows[name] = steps
            self.logger.info(f"Registered workflow: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error registering workflow {name}: {e}")
            return False
    
    async def execute_workflow(self, workflow_name: str, 
                             parameters: Dict[str, Any] = None) -> WorkflowResult:
        """Execute a workflow"""
        start_time = time.time()
        
        try:
            if workflow_name not in self.workflows:
                return WorkflowResult(
                    success=False,
                    workflow_name=workflow_name,
                    steps_executed=0,
                    total_steps=0,
                    execution_time=time.time() - start_time,
                    errors=[f"Workflow not found: {workflow_name}"]
                )
            
            workflow_steps = self.workflows[workflow_name]
            step_results = []
            errors = []
            steps_executed = 0
            
            for step in workflow_steps:
                try:
                    # Execute step
                    result = await self._execute_workflow_step(step, parameters or {})
                    step_results.append(result)
                    steps_executed += 1
                    
                    if not result.success:
                        errors.append(f"Step {step.step_id} failed: {result.error}")
                        if step.retry_count < step.max_retries:
                            step.retry_count += 1
                            # Retry step
                            await asyncio.sleep(1.0)
                            result = await self._execute_workflow_step(step, parameters or {})
                            step_results.append(result)
                            steps_executed += 1
                    
                    # Delay after step
                    if step.delay_after > 0:
                        await asyncio.sleep(step.delay_after)
                    
                except Exception as e:
                    error_msg = f"Error executing step {step.step_id}: {e}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            execution_time = time.time() - start_time
            success = len(errors) == 0
            
            return WorkflowResult(
                success=success,
                workflow_name=workflow_name,
                steps_executed=steps_executed,
                total_steps=len(workflow_steps),
                execution_time=execution_time,
                errors=errors,
                step_results=step_results
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return WorkflowResult(
                success=False,
                workflow_name=workflow_name,
                steps_executed=0,
                total_steps=0,
                execution_time=execution_time,
                errors=[str(e)]
            )
    
    async def _execute_workflow_step(self, step: WorkflowStep, 
                                   parameters: Dict[str, Any]) -> ApplicationActionResult:
        """Execute a single workflow step"""
        try:
            if step.action == ApplicationAction.LAUNCH:
                return await self.controller.launch_application(
                    step.application_name,
                    step.parameters.get("app_path", ""),
                    step.parameters.get("arguments", [])
                )
            elif step.action == ApplicationAction.CLOSE:
                return await self.controller.close_application(
                    step.application_name,
                    step.parameters.get("force", False)
                )
            elif step.action == ApplicationAction.SEND_KEY:
                return await self.controller.send_key_to_application(
                    step.application_name,
                    step.parameters.get("key", "")
                )
            elif step.action == ApplicationAction.SEND_TEXT:
                return await self.controller.send_text_to_application(
                    step.application_name,
                    step.parameters.get("text", "")
                )
            elif step.action == ApplicationAction.SCREENSHOT:
                return await self.controller.take_screenshot(step.application_name)
            else:
                return ApplicationActionResult(
                    success=False,
                    action=step.action,
                    application_name=step.application_name,
                    execution_time=0,
                    error=f"Unsupported action: {step.action}"
                )
                
        except Exception as e:
            return ApplicationActionResult(
                success=False,
                action=step.action,
                application_name=step.application_name,
                execution_time=0,
                error=str(e)
            )
    
    def list_workflows(self) -> List[str]:
        """List registered workflows"""
        return list(self.workflows.keys())
    
    def get_workflow_steps(self, workflow_name: str) -> List[WorkflowStep]:
        """Get workflow steps"""
        return self.workflows.get(workflow_name, [])

class ApplicationAutomationExecutor:
    """Executor for application automation operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.controller = ApplicationController()
        self.orchestrator = WorkflowOrchestrator()
        self._load_default_workflows()
    
    async def initialize(self) -> bool:
        """Initialize application automation executor"""
        try:
            self._is_initialized = True
            self.logger.info("Application automation executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application automation executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("application_automation" in parameters or
                "launch_application" in parameters or
                "close_application" in parameters or
                "execute_workflow" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute application automation capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Application automation executor not initialized"}
            
            operation = parameters.get("operation", "launch_application")
            
            if operation == "launch_application":
                return await self._execute_launch_application(parameters, context)
            elif operation == "close_application":
                return await self._execute_close_application(parameters, context)
            elif operation == "send_key":
                return await self._execute_send_key(parameters, context)
            elif operation == "send_text":
                return await self._execute_send_text(parameters, context)
            elif operation == "take_screenshot":
                return await self._execute_take_screenshot(parameters, context)
            elif operation == "execute_workflow":
                return await self._execute_workflow(parameters, context)
            elif operation == "list_applications":
                return await self._execute_list_applications(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing application automation capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_launch_application(self, parameters: Dict[str, Any], 
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute launch application operation"""
        try:
            app_name = parameters.get("app_name", "")
            app_path = parameters.get("app_path", "")
            arguments = parameters.get("arguments", [])
            
            if not app_name:
                return {"success": False, "error": "Application name required"}
            
            result = await self.controller.launch_application(app_name, app_path, arguments)
            
            return {
                "success": result.success,
                "action": result.action.value,
                "application_name": result.application_name,
                "execution_time": result.execution_time,
                "error": result.error,
                "result_data": result.result_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_close_application(self, parameters: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute close application operation"""
        try:
            app_name = parameters.get("app_name", "")
            force = parameters.get("force", False)
            
            if not app_name:
                return {"success": False, "error": "Application name required"}
            
            result = await self.controller.close_application(app_name, force)
            
            return {
                "success": result.success,
                "action": result.action.value,
                "application_name": result.application_name,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_send_key(self, parameters: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute send key operation"""
        try:
            app_name = parameters.get("app_name", "")
            key = parameters.get("key", "")
            
            if not app_name or not key:
                return {"success": False, "error": "Application name and key required"}
            
            result = await self.controller.send_key_to_application(app_name, key)
            
            return {
                "success": result.success,
                "action": result.action.value,
                "application_name": result.application_name,
                "execution_time": result.execution_time,
                "error": result.error,
                "result_data": result.result_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_send_text(self, parameters: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute send text operation"""
        try:
            app_name = parameters.get("app_name", "")
            text = parameters.get("text", "")
            
            if not app_name or not text:
                return {"success": False, "error": "Application name and text required"}
            
            result = await self.controller.send_text_to_application(app_name, text)
            
            return {
                "success": result.success,
                "action": result.action.value,
                "application_name": result.application_name,
                "execution_time": result.execution_time,
                "error": result.error,
                "result_data": result.result_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_take_screenshot(self, parameters: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute take screenshot operation"""
        try:
            app_name = parameters.get("app_name")
            
            result = await self.controller.take_screenshot(app_name)
            
            return {
                "success": result.success,
                "action": result.action.value,
                "application_name": result.application_name,
                "execution_time": result.execution_time,
                "error": result.error,
                "result_data": result.result_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_workflow(self, parameters: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow operation"""
        try:
            workflow_name = parameters.get("workflow_name", "")
            
            if not workflow_name:
                return {"success": False, "error": "Workflow name required"}
            
            result = await self.orchestrator.execute_workflow(workflow_name, parameters)
            
            return {
                "success": result.success,
                "workflow_name": result.workflow_name,
                "steps_executed": result.steps_executed,
                "total_steps": result.total_steps,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "step_results": [
                    {
                        "success": step.success,
                        "action": step.action.value,
                        "application_name": step.application_name,
                        "execution_time": step.execution_time,
                        "error": step.error
                    }
                    for step in result.step_results or []
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_list_applications(self, parameters: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute list applications operation"""
        try:
            applications = self.controller.detector.get_running_applications()
            
            app_list = []
            for app in applications:
                app_list.append({
                    "name": app.name,
                    "process_id": app.process_id,
                    "window_title": app.window_title,
                    "executable_path": app.executable_path,
                    "state": app.state.value,
                    "memory_usage": app.memory_usage,
                    "cpu_usage": app.cpu_usage,
                    "start_time": app.start_time.isoformat()
                })
            
            return {
                "success": True,
                "applications": app_list,
                "total_applications": len(app_list)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_default_workflows(self):
        """Load default workflows"""
        # Text editing workflow
        text_editing_workflow = [
            WorkflowStep(
                step_id="launch_editor",
                application_name="notepad",
                action=ApplicationAction.LAUNCH,
                parameters={"app_path": ""},
                delay_after=2.0
            ),
            WorkflowStep(
                step_id="type_text",
                application_name="notepad",
                action=ApplicationAction.SEND_TEXT,
                parameters={"text": "Hello, this is automated text!"},
                delay_after=1.0
            ),
            WorkflowStep(
                step_id="save_document",
                application_name="notepad",
                action=ApplicationAction.SEND_KEY,
                parameters={"key": "ctrl+s"},
                delay_after=1.0
            )
        ]
        
        self.orchestrator.register_workflow("text_editing", text_editing_workflow)
        
        # Web browsing workflow
        web_browsing_workflow = [
            WorkflowStep(
                step_id="launch_browser",
                application_name="chrome",
                action=ApplicationAction.LAUNCH,
                parameters={"app_path": ""},
                delay_after=3.0
            ),
            WorkflowStep(
                step_id="navigate_to_url",
                application_name="chrome",
                action=ApplicationAction.SEND_KEY,
                parameters={"key": "ctrl+l"},
                delay_after=1.0
            ),
            WorkflowStep(
                step_id="type_url",
                application_name="chrome",
                action=ApplicationAction.SEND_TEXT,
                parameters={"text": "https://www.google.com"},
                delay_after=1.0
            ),
            WorkflowStep(
                step_id="press_enter",
                application_name="chrome",
                action=ApplicationAction.SEND_KEY,
                parameters={"key": "enter"},
                delay_after=2.0
            )
        ]
        
        self.orchestrator.register_workflow("web_browsing", web_browsing_workflow)

