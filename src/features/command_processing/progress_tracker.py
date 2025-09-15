"""
Real-time Progress Tracking System for JARVIS Computer Assistant

Provides live command execution monitoring and progress tracking.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ProgressStatus(Enum):
    """Progress status types"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class ProgressEventType(Enum):
    """Progress event types"""
    STARTED = "started"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    PROGRESS_UPDATE = "progress_update"
    STATUS_CHANGE = "status_change"
    MESSAGE = "message"
    ERROR = "error"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class ProgressEvent:
    """Progress event data"""
    event_id: str
    execution_id: str
    event_type: ProgressEventType
    timestamp: datetime
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    step_id: Optional[str] = None
    progress_percentage: Optional[float] = None

@dataclass
class ProgressStep:
    """Progress step information"""
    step_id: str
    name: str
    description: str
    status: ProgressStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    error_message: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProgressExecution:
    """Progress execution tracking"""
    execution_id: str
    command: str
    status: ProgressStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_steps: int = 0
    completed_steps: int = 0
    current_step: Optional[str] = None
    progress_percentage: float = 0.0
    steps: List[ProgressStep] = field(default_factory=list)
    events: List[ProgressEvent] = field(default_factory=list)
    error_message: Optional[str] = None
    result_data: Dict[str, Any] = field(default_factory=dict)

class ProgressTracker:
    """Main progress tracking system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.executions: Dict[str, ProgressExecution] = {}
        self.subscribers: Set[Callable[[ProgressEvent], None]] = set()
        self.event_history: List[ProgressEvent] = []
        self.max_history_size = 1000
        
    def subscribe(self, callback: Callable[[ProgressEvent], None]) -> str:
        """Subscribe to progress events"""
        self.subscribers.add(callback)
        return f"subscriber_{len(self.subscribers)}"
    
    def unsubscribe(self, callback: Callable[[ProgressEvent], None]):
        """Unsubscribe from progress events"""
        self.subscribers.discard(callback)
    
    async def _notify_subscribers(self, event: ProgressEvent):
        """Notify all subscribers of a progress event"""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {e}")
    
    def start_execution(self, command: str, total_steps: int = 0) -> str:
        """Start tracking a new execution"""
        execution_id = str(uuid.uuid4())
        
        execution = ProgressExecution(
            execution_id=execution_id,
            command=command,
            status=ProgressStatus.PENDING,
            started_at=datetime.now(),
            total_steps=total_steps
        )
        
        self.executions[execution_id] = execution
        
        # Create start event
        event = ProgressEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            event_type=ProgressEventType.STARTED,
            timestamp=datetime.now(),
            message=f"Started execution: {command}",
            data={"command": command, "total_steps": total_steps}
        )
        
        execution.events.append(event)
        self.event_history.append(event)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(event))
        
        return execution_id
    
    def update_status(self, execution_id: str, status: ProgressStatus, 
                     message: str = "", data: Dict[str, Any] = None):
        """Update execution status"""
        if execution_id not in self.executions:
            self.logger.warning(f"Execution not found: {execution_id}")
            return
        
        execution = self.executions[execution_id]
        old_status = execution.status
        execution.status = status
        
        if status == ProgressStatus.COMPLETED:
            execution.completed_at = datetime.now()
            execution.progress_percentage = 100.0
        elif status == ProgressStatus.FAILED:
            execution.completed_at = datetime.now()
        
        # Create status change event
        event = ProgressEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            event_type=ProgressEventType.STATUS_CHANGE,
            timestamp=datetime.now(),
            message=message or f"Status changed from {old_status.value} to {status.value}",
            data=data or {},
            progress_percentage=execution.progress_percentage
        )
        
        execution.events.append(event)
        self.event_history.append(event)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(event))
    
    def add_step(self, execution_id: str, step_id: str, name: str, 
                description: str = "") -> bool:
        """Add a step to execution"""
        if execution_id not in self.executions:
            self.logger.warning(f"Execution not found: {execution_id}")
            return False
        
        execution = self.executions[execution_id]
        
        step = ProgressStep(
            step_id=step_id,
            name=name,
            description=description,
            status=ProgressStatus.PENDING
        )
        
        execution.steps.append(step)
        execution.total_steps = len(execution.steps)
        
        return True
    
    def start_step(self, execution_id: str, step_id: str, 
                  message: str = "", data: Dict[str, Any] = None) -> bool:
        """Start a step execution"""
        if execution_id not in self.executions:
            self.logger.warning(f"Execution not found: {execution_id}")
            return False
        
        execution = self.executions[execution_id]
        step = self._find_step(execution, step_id)
        
        if not step:
            self.logger.warning(f"Step not found: {step_id}")
            return False
        
        step.status = ProgressStatus.RUNNING
        step.started_at = datetime.now()
        execution.current_step = step_id
        execution.status = ProgressStatus.RUNNING
        
        # Create step started event
        event = ProgressEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            event_type=ProgressEventType.STEP_STARTED,
            timestamp=datetime.now(),
            message=message or f"Started step: {step.name}",
            data=data or {},
            step_id=step_id
        )
        
        execution.events.append(event)
        self.event_history.append(event)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(event))
        
        return True
    
    def complete_step(self, execution_id: str, step_id: str, 
                    message: str = "", data: Dict[str, Any] = None) -> bool:
        """Complete a step execution"""
        if execution_id not in self.executions:
            self.logger.warning(f"Execution not found: {execution_id}")
            return False
        
        execution = self.executions[execution_id]
        step = self._find_step(execution, step_id)
        
        if not step:
            self.logger.warning(f"Step not found: {step_id}")
            return False
        
        step.status = ProgressStatus.COMPLETED
        step.completed_at = datetime.now()
        step.progress_percentage = 100.0
        execution.completed_steps += 1
        
        # Update overall progress
        if execution.total_steps > 0:
            execution.progress_percentage = (execution.completed_steps / execution.total_steps) * 100.0
        
        # Check if all steps completed
        if execution.completed_steps >= execution.total_steps:
            execution.status = ProgressStatus.COMPLETED
            execution.completed_at = datetime.now()
        
        # Create step completed event
        event = ProgressEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            event_type=ProgressEventType.STEP_COMPLETED,
            timestamp=datetime.now(),
            message=message or f"Completed step: {step.name}",
            data=data or {},
            step_id=step_id,
            progress_percentage=execution.progress_percentage
        )
        
        execution.events.append(event)
        self.event_history.append(event)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(event))
        
        return True
    
    def fail_step(self, execution_id: str, step_id: str, error_message: str,
                 data: Dict[str, Any] = None) -> bool:
        """Mark a step as failed"""
        if execution_id not in self.executions:
            self.logger.warning(f"Execution not found: {execution_id}")
            return False
        
        execution = self.executions[execution_id]
        step = self._find_step(execution, step_id)
        
        if not step:
            self.logger.warning(f"Step not found: {step_id}")
            return False
        
        step.status = ProgressStatus.FAILED
        step.completed_at = datetime.now()
        step.error_message = error_message
        execution.status = ProgressStatus.FAILED
        execution.error_message = error_message
        execution.completed_at = datetime.now()
        
        # Create step failed event
        event = ProgressEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            event_type=ProgressEventType.STEP_FAILED,
            timestamp=datetime.now(),
            message=f"Failed step: {step.name} - {error_message}",
            data=data or {},
            step_id=step_id
        )
        
        execution.events.append(event)
        self.event_history.append(event)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(event))
        
        return True
    
    def update_progress(self, execution_id: str, progress_percentage: float,
                       message: str = "", data: Dict[str, Any] = None) -> bool:
        """Update execution progress"""
        if execution_id not in self.executions:
            self.logger.warning(f"Execution not found: {execution_id}")
            return False
        
        execution = self.executions[execution_id]
        execution.progress_percentage = min(100.0, max(0.0, progress_percentage))
        
        # Create progress update event
        event = ProgressEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            event_type=ProgressEventType.PROGRESS_UPDATE,
            timestamp=datetime.now(),
            message=message or f"Progress: {progress_percentage:.1f}%",
            data=data or {},
            progress_percentage=execution.progress_percentage
        )
        
        execution.events.append(event)
        self.event_history.append(event)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(event))
        
        return True
    
    def add_message(self, execution_id: str, message: str, 
                   data: Dict[str, Any] = None) -> bool:
        """Add a message to execution"""
        if execution_id not in self.executions:
            self.logger.warning(f"Execution not found: {execution_id}")
            return False
        
        execution = self.executions[execution_id]
        
        # Create message event
        event = ProgressEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            event_type=ProgressEventType.MESSAGE,
            timestamp=datetime.now(),
            message=message,
            data=data or {}
        )
        
        execution.events.append(event)
        self.event_history.append(event)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(event))
        
        return True
    
    def add_error(self, execution_id: str, error_message: str,
                 data: Dict[str, Any] = None) -> bool:
        """Add an error to execution"""
        if execution_id not in self.executions:
            self.logger.warning(f"Execution not found: {execution_id}")
            return False
        
        execution = self.executions[execution_id]
        execution.status = ProgressStatus.FAILED
        execution.error_message = error_message
        execution.completed_at = datetime.now()
        
        # Create error event
        event = ProgressEvent(
            event_id=str(uuid.uuid4()),
            execution_id=execution_id,
            event_type=ProgressEventType.ERROR,
            timestamp=datetime.now(),
            message=error_message,
            data=data or {}
        )
        
        execution.events.append(event)
        self.event_history.append(event)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(event))
        
        return True
    
    def get_execution(self, execution_id: str) -> Optional[ProgressExecution]:
        """Get execution by ID"""
        return self.executions.get(execution_id)
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status summary"""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        return {
            "execution_id": execution.execution_id,
            "command": execution.command,
            "status": execution.status.value,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "total_steps": execution.total_steps,
            "completed_steps": execution.completed_steps,
            "current_step": execution.current_step,
            "progress_percentage": execution.progress_percentage,
            "error_message": execution.error_message,
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "description": step.description,
                    "status": step.status.value,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "progress_percentage": step.progress_percentage,
                    "error_message": step.error_message
                }
                for step in execution.steps
            ]
        }
    
    def list_executions(self, status_filter: Optional[ProgressStatus] = None) -> List[Dict[str, Any]]:
        """List executions with optional status filter"""
        executions = []
        
        for execution in self.executions.values():
            if status_filter and execution.status != status_filter:
                continue
            
            executions.append(self.get_execution_status(execution.execution_id))
        
        return executions
    
    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        recent_events = self.event_history[-limit:]
        
        return [
            {
                "event_id": event.event_id,
                "execution_id": event.execution_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp.isoformat(),
                "message": event.message,
                "data": event.data,
                "step_id": event.step_id,
                "progress_percentage": event.progress_percentage
            }
            for event in recent_events
        ]
    
    def cleanup_old_executions(self, older_than_hours: int = 24):
        """Cleanup old completed executions"""
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
        
        to_remove = []
        for execution_id, execution in self.executions.items():
            if (execution.status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED, ProgressStatus.CANCELLED] and
                execution.completed_at and
                execution.completed_at.timestamp() < cutoff_time):
                to_remove.append(execution_id)
        
        for execution_id in to_remove:
            del self.executions[execution_id]
        
        self.logger.info(f"Cleaned up {len(to_remove)} old executions")
    
    def _find_step(self, execution: ProgressExecution, step_id: str) -> Optional[ProgressStep]:
        """Find step by ID"""
        for step in execution.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _trim_history(self):
        """Trim event history to max size"""
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]

class ProgressTrackerExecutor:
    """Executor for progress tracking operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.tracker = ProgressTracker()
    
    async def initialize(self) -> bool:
        """Initialize progress tracker executor"""
        try:
            self._is_initialized = True
            self.logger.info("Progress tracker executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize progress tracker executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("progress_tracking" in parameters or
                "start_execution" in parameters or
                "update_progress" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute progress tracking capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Progress tracker executor not initialized"}
            
            operation = parameters.get("operation", "start_execution")
            
            if operation == "start_execution":
                return await self._execute_start_execution(parameters, context)
            elif operation == "update_status":
                return await self._execute_update_status(parameters, context)
            elif operation == "add_step":
                return await self._execute_add_step(parameters, context)
            elif operation == "start_step":
                return await self._execute_start_step(parameters, context)
            elif operation == "complete_step":
                return await self._execute_complete_step(parameters, context)
            elif operation == "fail_step":
                return await self._execute_fail_step(parameters, context)
            elif operation == "update_progress":
                return await self._execute_update_progress(parameters, context)
            elif operation == "add_message":
                return await self._execute_add_message(parameters, context)
            elif operation == "add_error":
                return await self._execute_add_error(parameters, context)
            elif operation == "get_execution_status":
                return await self._execute_get_execution_status(parameters, context)
            elif operation == "list_executions":
                return await self._execute_list_executions(parameters, context)
            elif operation == "get_recent_events":
                return await self._execute_get_recent_events(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing progress tracking capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_start_execution(self, parameters: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute start execution operation"""
        try:
            command = parameters.get("command", "")
            total_steps = parameters.get("total_steps", 0)
            
            if not command:
                return {"success": False, "error": "Command required"}
            
            execution_id = self.tracker.start_execution(command, total_steps)
            
            return {
                "success": True,
                "execution_id": execution_id,
                "message": f"Started tracking execution: {command}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_update_status(self, parameters: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update status operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            status_str = parameters.get("status", "")
            message = parameters.get("message", "")
            data = parameters.get("data", {})
            
            if not execution_id or not status_str:
                return {"success": False, "error": "Execution ID and status required"}
            
            try:
                status = ProgressStatus(status_str)
            except ValueError:
                return {"success": False, "error": f"Invalid status: {status_str}"}
            
            self.tracker.update_status(execution_id, status, message, data)
            
            return {
                "success": True,
                "execution_id": execution_id,
                "message": f"Updated status to {status.value}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_add_step(self, parameters: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute add step operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            step_id = parameters.get("step_id", "")
            name = parameters.get("name", "")
            description = parameters.get("description", "")
            
            if not execution_id or not step_id or not name:
                return {"success": False, "error": "Execution ID, step ID, and name required"}
            
            success = self.tracker.add_step(execution_id, step_id, name, description)
            
            return {
                "success": success,
                "execution_id": execution_id,
                "step_id": step_id,
                "message": f"Step {step_id} {'added' if success else 'failed to add'}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_start_step(self, parameters: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute start step operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            step_id = parameters.get("step_id", "")
            message = parameters.get("message", "")
            data = parameters.get("data", {})
            
            if not execution_id or not step_id:
                return {"success": False, "error": "Execution ID and step ID required"}
            
            success = self.tracker.start_step(execution_id, step_id, message, data)
            
            return {
                "success": success,
                "execution_id": execution_id,
                "step_id": step_id,
                "message": f"Step {step_id} {'started' if success else 'failed to start'}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_complete_step(self, parameters: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete step operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            step_id = parameters.get("step_id", "")
            message = parameters.get("message", "")
            data = parameters.get("data", {})
            
            if not execution_id or not step_id:
                return {"success": False, "error": "Execution ID and step ID required"}
            
            success = self.tracker.complete_step(execution_id, step_id, message, data)
            
            return {
                "success": success,
                "execution_id": execution_id,
                "step_id": step_id,
                "message": f"Step {step_id} {'completed' if success else 'failed to complete'}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_fail_step(self, parameters: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fail step operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            step_id = parameters.get("step_id", "")
            error_message = parameters.get("error_message", "")
            data = parameters.get("data", {})
            
            if not execution_id or not step_id or not error_message:
                return {"success": False, "error": "Execution ID, step ID, and error message required"}
            
            success = self.tracker.fail_step(execution_id, step_id, error_message, data)
            
            return {
                "success": success,
                "execution_id": execution_id,
                "step_id": step_id,
                "message": f"Step {step_id} {'failed' if success else 'failed to mark as failed'}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_update_progress(self, parameters: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update progress operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            progress_percentage = parameters.get("progress_percentage", 0.0)
            message = parameters.get("message", "")
            data = parameters.get("data", {})
            
            if not execution_id:
                return {"success": False, "error": "Execution ID required"}
            
            success = self.tracker.update_progress(execution_id, progress_percentage, message, data)
            
            return {
                "success": success,
                "execution_id": execution_id,
                "progress_percentage": progress_percentage,
                "message": f"Progress updated to {progress_percentage:.1f}%"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_add_message(self, parameters: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute add message operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            message = parameters.get("message", "")
            data = parameters.get("data", {})
            
            if not execution_id or not message:
                return {"success": False, "error": "Execution ID and message required"}
            
            success = self.tracker.add_message(execution_id, message, data)
            
            return {
                "success": success,
                "execution_id": execution_id,
                "message": "Message added"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_add_error(self, parameters: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute add error operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            error_message = parameters.get("error_message", "")
            data = parameters.get("data", {})
            
            if not execution_id or not error_message:
                return {"success": False, "error": "Execution ID and error message required"}
            
            success = self.tracker.add_error(execution_id, error_message, data)
            
            return {
                "success": success,
                "execution_id": execution_id,
                "message": "Error added"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_get_execution_status(self, parameters: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get execution status operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            
            if not execution_id:
                return {"success": False, "error": "Execution ID required"}
            
            status = self.tracker.get_execution_status(execution_id)
            
            if not status:
                return {"success": False, "error": "Execution not found"}
            
            return {
                "success": True,
                "execution_status": status
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_list_executions(self, parameters: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute list executions operation"""
        try:
            status_filter = parameters.get("status_filter")
            
            if status_filter:
                try:
                    status = ProgressStatus(status_filter)
                    executions = self.tracker.list_executions(status)
                except ValueError:
                    return {"success": False, "error": f"Invalid status filter: {status_filter}"}
            else:
                executions = self.tracker.list_executions()
            
            return {
                "success": True,
                "executions": executions,
                "total_executions": len(executions)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_get_recent_events(self, parameters: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get recent events operation"""
        try:
            limit = parameters.get("limit", 100)
            
            events = self.tracker.get_recent_events(limit)
            
            return {
                "success": True,
                "events": events,
                "total_events": len(events)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
