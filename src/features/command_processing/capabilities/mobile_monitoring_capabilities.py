"""
Mobile Monitoring Capabilities for JARVIS Computer Assistant

Provides capabilities for real-time mobile monitoring and status updates.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from ..mobile_monitoring_system import MobileMonitoringSystem, MobileEventType, get_mobile_monitoring

logger = logging.getLogger(__name__)

class MobileMonitoringExecutor:
    """Mobile monitoring capabilities executor"""
    
    def __init__(self):
        self.mobile_monitoring = get_mobile_monitoring()
        self._is_initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize mobile monitoring executor"""
        try:
            if not self.mobile_monitoring._is_running:
                success = await self.mobile_monitoring.start()
                if not success:
                    return False
            
            self._is_initialized = True
            self.logger.info("Mobile monitoring executor initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize mobile monitoring executor: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # Don't stop the global mobile monitoring system here
            # as it might be used by other components
            self._is_initialized = False
            self.logger.info("Mobile monitoring executor cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup mobile monitoring executor: {e}")
    
    def _can_handle(self, parameters: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("mobile_monitoring" in parameters or
                "track_command" in parameters or
                "send_event" in parameters or
                "mobile_status" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute mobile monitoring capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Mobile monitoring executor not initialized"}
            
            operation = parameters.get("operation")
            if not operation:
                return {"success": False, "error": "Operation not specified"}
            
            if operation == "start_monitoring":
                return await self._start_monitoring(parameters)
            elif operation == "stop_monitoring":
                return await self._stop_monitoring(parameters)
            elif operation == "track_command_start":
                return await self._track_command_start(parameters)
            elif operation == "track_command_progress":
                return await self._track_command_progress(parameters)
            elif operation == "track_command_completed":
                return await self._track_command_completed(parameters)
            elif operation == "track_command_failed":
                return await self._track_command_failed(parameters)
            elif operation == "send_log_message":
                return await self._send_log_message(parameters)
            elif operation == "send_error":
                return await self._send_error(parameters)
            elif operation == "send_terminal_output":
                return await self._send_terminal_output(parameters)
            elif operation == "send_file_operation":
                return await self._send_file_operation(parameters)
            elif operation == "send_application_event":
                return await self._send_application_event(parameters)
            elif operation == "get_connection_status":
                return await self._get_connection_status(parameters)
            elif operation == "get_execution_status":
                return await self._get_execution_status(parameters)
            elif operation == "get_stats":
                return await self._get_stats(parameters)
            elif operation == "send_custom_event":
                return await self._send_custom_event(parameters)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        
        except Exception as e:
            self.logger.error(f"Failed to execute mobile monitoring capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _start_monitoring(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Start mobile monitoring system"""
        try:
            host = parameters.get("host", "localhost")
            port = parameters.get("port", 8765)
            
            # Update host and port if provided
            if host != self.mobile_monitoring.host or port != self.mobile_monitoring.port:
                self.mobile_monitoring.host = host
                self.mobile_monitoring.port = port
            
            if not self.mobile_monitoring._is_running:
                success = await self.mobile_monitoring.start()
                if not success:
                    return {"success": False, "error": "Failed to start mobile monitoring system"}
            
            return {
                "success": True,
                "message": "Mobile monitoring system started",
                "host": host,
                "port": port,
                "is_running": self.mobile_monitoring._is_running
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stop_monitoring(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Stop mobile monitoring system"""
        try:
            if self.mobile_monitoring._is_running:
                await self.mobile_monitoring.stop()
            
            return {
                "success": True,
                "message": "Mobile monitoring system stopped",
                "is_running": self.mobile_monitoring._is_running
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _track_command_start(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Track command execution start"""
        try:
            execution_id = parameters.get("execution_id")
            command = parameters.get("command")
            metadata = parameters.get("metadata", {})
            
            if not execution_id or not command:
                return {"success": False, "error": "Execution ID and command are required"}
            
            await self.mobile_monitoring.track_command_start(execution_id, command, metadata)
            
            return {
                "success": True,
                "message": "Command tracking started",
                "execution_id": execution_id,
                "command": command
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _track_command_progress(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Track command execution progress"""
        try:
            execution_id = parameters.get("execution_id")
            progress = parameters.get("progress", 0.0)
            message = parameters.get("message")
            
            if not execution_id:
                return {"success": False, "error": "Execution ID is required"}
            
            if not 0 <= progress <= 100:
                return {"success": False, "error": "Progress must be between 0 and 100"}
            
            await self.mobile_monitoring.track_command_progress(execution_id, progress, message)
            
            return {
                "success": True,
                "message": "Command progress updated",
                "execution_id": execution_id,
                "progress": progress
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _track_command_completed(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Track command execution completion"""
        try:
            execution_id = parameters.get("execution_id")
            output = parameters.get("output", "")
            metadata = parameters.get("metadata", {})
            
            if not execution_id:
                return {"success": False, "error": "Execution ID is required"}
            
            await self.mobile_monitoring.track_command_completed(execution_id, output, metadata)
            
            return {
                "success": True,
                "message": "Command completion tracked",
                "execution_id": execution_id
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _track_command_failed(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Track command execution failure"""
        try:
            execution_id = parameters.get("execution_id")
            error = parameters.get("error", "Unknown error")
            metadata = parameters.get("metadata", {})
            
            if not execution_id:
                return {"success": False, "error": "Execution ID is required"}
            
            await self.mobile_monitoring.track_command_failed(execution_id, error, metadata)
            
            return {
                "success": True,
                "message": "Command failure tracked",
                "execution_id": execution_id,
                "error": error
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_log_message(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send log message to mobile apps"""
        try:
            level = parameters.get("level", "info")
            message = parameters.get("message")
            metadata = parameters.get("metadata", {})
            
            if not message:
                return {"success": False, "error": "Message is required"}
            
            await self.mobile_monitoring.send_log_message(level, message, metadata)
            
            return {
                "success": True,
                "message": "Log message sent to mobile apps",
                "level": level
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_error(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send error to mobile apps"""
        try:
            error = parameters.get("error")
            context = parameters.get("context", {})
            
            if not error:
                return {"success": False, "error": "Error message is required"}
            
            await self.mobile_monitoring.send_error(error, context)
            
            return {
                "success": True,
                "message": "Error sent to mobile apps"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_terminal_output(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send terminal output to mobile apps"""
        try:
            execution_id = parameters.get("execution_id")
            output = parameters.get("output")
            
            if not execution_id or not output:
                return {"success": False, "error": "Execution ID and output are required"}
            
            await self.mobile_monitoring.send_terminal_output(execution_id, output)
            
            return {
                "success": True,
                "message": "Terminal output sent to mobile apps",
                "execution_id": execution_id
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_file_operation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send file operation event to mobile apps"""
        try:
            operation = parameters.get("operation")
            file_path = parameters.get("file_path")
            status = parameters.get("status")
            metadata = parameters.get("metadata", {})
            
            if not all([operation, file_path, status]):
                return {"success": False, "error": "Operation, file_path, and status are required"}
            
            await self.mobile_monitoring.send_file_operation(operation, file_path, status, metadata)
            
            return {
                "success": True,
                "message": "File operation event sent to mobile apps",
                "operation": operation,
                "file_path": file_path
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_application_event(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send application event to mobile apps"""
        try:
            app_name = parameters.get("app_name")
            event = parameters.get("event")
            metadata = parameters.get("metadata", {})
            
            if not all([app_name, event]):
                return {"success": False, "error": "App name and event are required"}
            
            await self.mobile_monitoring.send_application_event(app_name, event, metadata)
            
            return {
                "success": True,
                "message": "Application event sent to mobile apps",
                "app_name": app_name,
                "event": event
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_connection_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get mobile connection status"""
        try:
            connection_count = self.mobile_monitoring.get_connection_count()
            is_running = self.mobile_monitoring._is_running
            
            return {
                "success": True,
                "connection_count": connection_count,
                "is_running": is_running,
                "host": self.mobile_monitoring.host,
                "port": self.mobile_monitoring.port
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_execution_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get execution tracking status"""
        try:
            execution_id = parameters.get("execution_id")
            
            if execution_id:
                # Get specific execution status
                if execution_id in self.mobile_monitoring.executions:
                    execution = self.mobile_monitoring.executions[execution_id]
                    return {
                        "success": True,
                        "execution": {
                            "execution_id": execution.execution_id,
                            "command": execution.command,
                            "status": execution.status,
                            "start_time": execution.start_time,
                            "end_time": execution.end_time,
                            "progress": execution.progress,
                            "output": execution.output,
                            "error": execution.error,
                            "metadata": execution.metadata
                        }
                    }
                else:
                    return {"success": False, "error": "Execution not found"}
            else:
                # Get all executions
                executions = []
                for exec_id, execution in self.mobile_monitoring.executions.items():
                    executions.append({
                        "execution_id": execution.execution_id,
                        "command": execution.command,
                        "status": execution.status,
                        "start_time": execution.start_time,
                        "end_time": execution.end_time,
                        "progress": execution.progress
                    })
                
                return {
                    "success": True,
                    "executions": executions,
                    "total_executions": len(executions)
                }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_stats(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get mobile monitoring statistics"""
        try:
            stats = self.mobile_monitoring.get_stats()
            
            return {
                "success": True,
                "stats": stats
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_custom_event(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send custom event to mobile apps"""
        try:
            event_type_str = parameters.get("event_type")
            data = parameters.get("data", {})
            priority = parameters.get("priority", 1)
            requires_ack = parameters.get("requires_ack", False)
            
            if not event_type_str:
                return {"success": False, "error": "Event type is required"}
            
            try:
                event_type = MobileEventType(event_type_str)
            except ValueError:
                return {"success": False, "error": f"Invalid event type: {event_type_str}"}
            
            # Create and send custom event
            from ..mobile_monitoring_system import MobileEvent
            event = MobileEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                timestamp=time.time(),
                data=data,
                priority=priority,
                requires_ack=requires_ack
            )
            
            await self.mobile_monitoring.event_queue.put(event)
            
            return {
                "success": True,
                "message": "Custom event sent to mobile apps",
                "event_type": event_type_str,
                "event_id": event.event_id
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}

