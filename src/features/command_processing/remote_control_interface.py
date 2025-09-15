"""
Remote Computer Control Interface for JARVIS Computer Assistant

Provides comprehensive remote control capabilities through mobile applications,
including command execution, file operations, system control, and real-time monitoring.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol

from .capability_system import CapabilityManager, get_capability_manager
from .mobile_monitoring_system import MobileMonitoringSystem, get_mobile_monitoring

logger = logging.getLogger(__name__)

class RemoteCommandType(Enum):
    """Types of remote commands"""
    SYSTEM_CONTROL = "system_control"
    FILE_OPERATION = "file_operation"
    APPLICATION_CONTROL = "application_control"
    TERMINAL_COMMAND = "terminal_command"
    BROWSER_AUTOMATION = "browser_automation"
    TEXT_INPUT = "text_input"
    MEDIA_CONTROL = "media_control"
    MONITORING = "monitoring"
    CUSTOM = "custom"

class RemoteCommandStatus(Enum):
    """Remote command execution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class RemoteCommand:
    """Remote command from mobile app"""
    command_id: str
    command_type: RemoteCommandType
    action: str
    parameters: Dict[str, Any]
    user_id: str
    device_id: str
    timestamp: float
    status: RemoteCommandStatus = RemoteCommandStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RemoteConnection:
    """Remote mobile app connection"""
    connection_id: str
    websocket: WebSocketServerProtocol
    user_id: str
    device_id: str
    device_info: Dict[str, Any]
    last_ping: float
    is_authenticated: bool = False
    permissions: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)

class RemoteControlInterface:
    """Remote computer control interface"""
    
    def __init__(self, host: str = "localhost", port: int = 8767):
        self.host = host
        self.port = port
        self.connections: Dict[str, RemoteConnection] = {}
        self.commands: Dict[str, RemoteCommand] = {}
        self.capability_manager = None  # Will be initialized when needed
        self.mobile_monitoring = get_mobile_monitoring()
        self.server: Optional[websockets.WebSocketServer] = None
        self._is_running = False
        self.logger = logging.getLogger(__name__)
        
        # Command handlers
        self.command_handlers: Dict[RemoteCommandType, Callable] = {
            RemoteCommandType.SYSTEM_CONTROL: self._handle_system_control,
            RemoteCommandType.FILE_OPERATION: self._handle_file_operation,
            RemoteCommandType.APPLICATION_CONTROL: self._handle_application_control,
            RemoteCommandType.TERMINAL_COMMAND: self._handle_terminal_command,
            RemoteCommandType.BROWSER_AUTOMATION: self._handle_browser_automation,
            RemoteCommandType.TEXT_INPUT: self._handle_text_input,
            RemoteCommandType.MEDIA_CONTROL: self._handle_media_control,
            RemoteCommandType.MONITORING: self._handle_monitoring,
            RemoteCommandType.CUSTOM: self._handle_custom_command
        }
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0
        }
    
    async def start(self) -> bool:
        """Start the remote control interface"""
        try:
            # Initialize capability manager
            await self.capability_manager.initialize()
            
            # Start WebSocket server
            self.server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port
            )
            self._is_running = True
            
            # Start background tasks
            asyncio.create_task(self._command_processor())
            asyncio.create_task(self._connection_monitor())
            asyncio.create_task(self._stats_reporter())
            
            self.logger.info(f"Remote control interface started on {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start remote control interface: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the remote control interface"""
        try:
            self._is_running = False
            
            # Close all connections
            for connection in self.connections.values():
                await connection.websocket.close()
            
            # Close server
            if self.server:
                self.server.close()
                await self.server.wait_closed()
            
            # Cleanup capability manager
            await self.capability_manager.cleanup()
            
            self.logger.info("Remote control interface stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop remote control interface: {e}")
    
    async def _handle_connection(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """Handle new mobile app connection"""
        connection_id = str(uuid.uuid4())
        
        try:
            # Get authentication and device info
            auth_data = await self._authenticate_connection(websocket)
            if not auth_data:
                await websocket.close(code=4001, reason="Authentication failed")
                return
            
            user_id = auth_data["user_id"]
            device_id = auth_data["device_id"]
            device_info = auth_data["device_info"]
            permissions = auth_data.get("permissions", set())
            
            # Create connection
            connection = RemoteConnection(
                connection_id=connection_id,
                websocket=websocket,
                user_id=user_id,
                device_id=device_id,
                device_info=device_info,
                last_ping=time.time(),
                is_authenticated=True,
                permissions=permissions
            )
            
            self.connections[connection_id] = connection
            self.stats["total_connections"] += 1
            self.stats["active_connections"] += 1
            
            self.logger.info(f"Remote connection established: {connection_id} (User: {user_id})")
            
            # Send welcome message
            await self._send_response(connection, {
                "type": "connection_established",
                "connection_id": connection_id,
                "server_time": time.time(),
                "permissions": list(permissions)
            })
            
            # Handle messages from mobile app
            async for message in websocket:
                await self._handle_remote_message(connection, message)
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Remote connection closed: {connection_id}")
        except Exception as e:
            self.logger.error(f"Error handling remote connection {connection_id}: {e}")
        finally:
            # Cleanup connection
            if connection_id in self.connections:
                del self.connections[connection_id]
                self.stats["active_connections"] -= 1
    
    async def _authenticate_connection(self, websocket: WebSocketServerProtocol) -> Optional[Dict[str, Any]]:
        """Authenticate mobile app connection"""
        try:
            # Wait for authentication message
            message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            data = json.loads(message)
            
            if data.get("type") == "authenticate":
                auth_data = data.get("data", {})
                user_id = auth_data.get("user_id")
                device_id = auth_data.get("device_id")
                device_info = auth_data.get("device_info", {})
                permissions = set(auth_data.get("permissions", []))
                
                if user_id and device_id:
                    # Simple authentication - in production, implement proper auth
                    return {
                        "user_id": user_id,
                        "device_id": device_id,
                        "device_info": device_info,
                        "permissions": permissions
                    }
            
            return None
        except Exception as e:
            self.logger.warning(f"Authentication failed: {e}")
            return None
    
    async def _handle_remote_message(self, connection: RemoteConnection, message: str) -> None:
        """Handle message from mobile app"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "command":
                await self._handle_remote_command(connection, data)
            elif message_type == "ping":
                connection.last_ping = time.time()
                await self._send_response(connection, {"type": "pong", "timestamp": time.time()})
            elif message_type == "get_status":
                await self._send_system_status(connection)
            elif message_type == "cancel_command":
                await self._cancel_command(connection, data)
            else:
                self.logger.warning(f"Unknown message type from remote: {message_type}")
        
        except json.JSONDecodeError:
            self.logger.warning(f"Invalid JSON from remote app: {message}")
        except Exception as e:
            self.logger.error(f"Error handling remote message: {e}")
    
    async def _handle_remote_command(self, connection: RemoteConnection, data: Dict[str, Any]) -> None:
        """Handle remote command from mobile app"""
        try:
            command_data = data.get("data", {})
            command_type_str = command_data.get("command_type", "custom")
            action = command_data.get("action")
            parameters = command_data.get("parameters", {})
            
            # Create command
            command_id = str(uuid.uuid4())
            try:
                command_type = RemoteCommandType(command_type_str)
            except ValueError:
                command_type = RemoteCommandType.CUSTOM
            
            command = RemoteCommand(
                command_id=command_id,
                command_type=command_type,
                action=action,
                parameters=parameters,
                user_id=connection.user_id,
                device_id=connection.device_id,
                timestamp=time.time(),
                metadata={"connection_id": connection.connection_id}
            )
            
            self.commands[command_id] = command
            self.stats["total_commands"] += 1
            
            # Check permissions
            if not self._check_permissions(connection, command_type, action):
                await self._send_command_result(connection, command_id, {
                    "success": False,
                    "error": "Insufficient permissions for this command"
                })
                return
            
            # Send acknowledgment
            await self._send_response(connection, {
                "type": "command_received",
                "command_id": command_id,
                "status": "pending"
            })
            
            # Process command asynchronously
            asyncio.create_task(self._process_command(connection, command))
        
        except Exception as e:
            self.logger.error(f"Error handling remote command: {e}")
            await self._send_response(connection, {
                "type": "error",
                "error": str(e)
            })
    
    async def _process_command(self, connection: RemoteConnection, command: RemoteCommand) -> None:
        """Process remote command"""
        try:
            command.status = RemoteCommandStatus.PROCESSING
            start_time = time.time()
            
            # Get command handler
            handler = self.command_handlers.get(command.command_type)
            if not handler:
                raise ValueError(f"No handler for command type: {command.command_type}")
            
            # Execute command
            result = await handler(command)
            
            # Update command
            command.status = RemoteCommandStatus.COMPLETED
            command.result = result
            command.execution_time = time.time() - start_time
            
            # Send result
            await self._send_command_result(connection, command.command_id, result)
            
            # Update stats
            if result.get("success", False):
                self.stats["successful_commands"] += 1
            else:
                self.stats["failed_commands"] += 1
        
        except Exception as e:
            command.status = RemoteCommandStatus.FAILED
            command.error = str(e)
            command.execution_time = time.time() - start_time
            
            await self._send_command_result(connection, command.command_id, {
                "success": False,
                "error": str(e)
            })
            
            self.stats["failed_commands"] += 1
    
    async def _handle_system_control(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle system control commands"""
        try:
            action = command.action
            parameters = command.parameters
            
            if action == "shutdown":
                delay = parameters.get("delay", 0)
                return await self.capability_manager.execute_capability("system_shutdown", {
                    "delay": delay
                }, {})
            
            elif action == "restart":
                delay = parameters.get("delay", 0)
                return await self.capability_manager.execute_capability("system_restart", {
                    "delay": delay
                }, {})
            
            elif action == "sleep":
                return await self.capability_manager.execute_capability("system_sleep", {}, {})
            
            elif action == "hibernate":
                return await self.capability_manager.execute_capability("system_hibernate", {}, {})
            
            elif action == "set_volume":
                volume = parameters.get("volume", 50)
                return await self.capability_manager.execute_capability("volume_control", {
                    "action": "set",
                    "volume": volume
                }, {})
            
            elif action == "set_brightness":
                brightness = parameters.get("brightness", 50)
                return await self.capability_manager.execute_capability("brightness_control", {
                    "action": "set",
                    "brightness": brightness
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown system control action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_file_operation(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle file operation commands"""
        try:
            action = command.action
            parameters = command.parameters
            
            if action == "list_files":
                path = parameters.get("path", ".")
                return await self.capability_manager.execute_capability("file_manager", {
                    "operation": "list_files",
                    "path": path
                }, {})
            
            elif action == "create_file":
                path = parameters.get("path")
                content = parameters.get("content", "")
                return await self.capability_manager.execute_capability("file_manager", {
                    "operation": "create_file",
                    "path": path,
                    "content": content
                }, {})
            
            elif action == "read_file":
                path = parameters.get("path")
                return await self.capability_manager.execute_capability("file_manager", {
                    "operation": "read_file",
                    "path": path
                }, {})
            
            elif action == "write_file":
                path = parameters.get("path")
                content = parameters.get("content", "")
                return await self.capability_manager.execute_capability("file_manager", {
                    "operation": "write_file",
                    "path": path,
                    "content": content
                }, {})
            
            elif action == "delete_file":
                path = parameters.get("path")
                return await self.capability_manager.execute_capability("file_manager", {
                    "operation": "delete_file",
                    "path": path
                }, {})
            
            elif action == "organize_files":
                path = parameters.get("path", ".")
                rule_type = parameters.get("rule_type", "by_extension")
                return await self.capability_manager.execute_capability("file_organization", {
                    "operation": "organize_files",
                    "path": path,
                    "rule_type": rule_type
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown file operation action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_application_control(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle application control commands"""
        try:
            action = command.action
            parameters = command.parameters
            
            if action == "launch_app":
                app_name = parameters.get("app_name")
                return await self.capability_manager.execute_capability("application_automation", {
                    "operation": "launch_application",
                    "app_name": app_name
                }, {})
            
            elif action == "close_app":
                app_name = parameters.get("app_name")
                return await self.capability_manager.execute_capability("application_automation", {
                    "operation": "close_application",
                    "app_name": app_name
                }, {})
            
            elif action == "list_apps":
                return await self.capability_manager.execute_capability("application_automation", {
                    "operation": "list_applications"
                }, {})
            
            elif action == "send_keys":
                app_name = parameters.get("app_name")
                keys = parameters.get("keys")
                return await self.capability_manager.execute_capability("application_automation", {
                    "operation": "send_keys",
                    "app_name": app_name,
                    "keys": keys
                }, {})
            
            elif action == "send_text":
                app_name = parameters.get("app_name")
                text = parameters.get("text")
                return await self.capability_manager.execute_capability("application_automation", {
                    "operation": "send_text",
                    "app_name": app_name,
                    "text": text
                }, {})
            
            elif action == "take_screenshot":
                app_name = parameters.get("app_name")
                return await self.capability_manager.execute_capability("application_automation", {
                    "operation": "take_screenshot",
                    "app_name": app_name
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown application control action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_terminal_command(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle terminal command execution"""
        try:
            action = command.action
            parameters = command.parameters
            
            if action == "execute":
                cmd = parameters.get("command")
                terminal_type = parameters.get("terminal_type", "powershell")
                working_directory = parameters.get("working_directory")
                timeout = parameters.get("timeout", 30)
                
                return await self.capability_manager.execute_capability("advanced_terminal", {
                    "operation": "execute_command",
                    "command": cmd,
                    "terminal_type": terminal_type,
                    "working_directory": working_directory,
                    "timeout": timeout
                }, {})
            
            elif action == "execute_chain":
                commands = parameters.get("commands", [])
                chain_type = parameters.get("chain_type", "sequential")
                terminal_type = parameters.get("terminal_type", "powershell")
                
                return await self.capability_manager.execute_capability("advanced_terminal", {
                    "operation": "execute_command_chain",
                    "commands": commands,
                    "chain_type": chain_type,
                    "terminal_type": terminal_type
                }, {})
            
            elif action == "create_session":
                terminal_type = parameters.get("terminal_type", "powershell")
                working_directory = parameters.get("working_directory")
                
                return await self.capability_manager.execute_capability("advanced_terminal", {
                    "operation": "create_session",
                    "terminal_type": terminal_type,
                    "working_directory": working_directory
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown terminal action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_browser_automation(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle browser automation commands"""
        try:
            action = command.action
            parameters = command.parameters
            
            if action == "open_url":
                url = parameters.get("url")
                return await self.capability_manager.execute_capability("browser_automation", {
                    "operation": "open_url",
                    "url": url
                }, {})
            
            elif action == "search_youtube":
                query = parameters.get("query")
                return await self.capability_manager.execute_capability("youtube_automation", {
                    "operation": "search_videos",
                    "query": query
                }, {})
            
            elif action == "send_whatsapp":
                message = parameters.get("message")
                contact = parameters.get("contact")
                return await self.capability_manager.execute_capability("whatsapp_automation", {
                    "operation": "send_message",
                    "message": message,
                    "contact": contact
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown browser automation action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_text_input(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle text input commands"""
        try:
            action = command.action
            parameters = command.parameters
            
            if action == "type_text":
                text = parameters.get("text")
                return await self.capability_manager.execute_capability("text_input", {
                    "operation": "type_text",
                    "text": text
                }, {})
            
            elif action == "press_key":
                key = parameters.get("key")
                return await self.capability_manager.execute_capability("keyboard_control", {
                    "operation": "press_key",
                    "key": key
                }, {})
            
            elif action == "fill_form":
                form_data = parameters.get("form_data", {})
                return await self.capability_manager.execute_capability("form_filling", {
                    "operation": "fill_form",
                    "form_data": form_data
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown text input action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_media_control(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle media control commands"""
        try:
            action = command.action
            parameters = command.parameters
            
            if action == "play":
                return await self.capability_manager.execute_capability("media_control", {
                    "operation": "play"
                }, {})
            
            elif action == "pause":
                return await self.capability_manager.execute_capability("media_control", {
                    "operation": "pause"
                }, {})
            
            elif action == "stop":
                return await self.capability_manager.execute_capability("media_control", {
                    "operation": "stop"
                }, {})
            
            elif action == "next":
                return await self.capability_manager.execute_capability("media_control", {
                    "operation": "next"
                }, {})
            
            elif action == "previous":
                return await self.capability_manager.execute_capability("media_control", {
                    "operation": "previous"
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown media control action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_monitoring(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle monitoring commands"""
        try:
            action = command.action
            parameters = command.parameters
            
            if action == "get_status":
                return await self.capability_manager.execute_capability("mobile_monitoring", {
                    "operation": "get_connection_status"
                }, {})
            
            elif action == "get_executions":
                return await self.capability_manager.execute_capability("mobile_monitoring", {
                    "operation": "get_execution_status"
                }, {})
            
            elif action == "get_stats":
                return await self.capability_manager.execute_capability("mobile_monitoring", {
                    "operation": "get_stats"
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown monitoring action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_custom_command(self, command: RemoteCommand) -> Dict[str, Any]:
        """Handle custom commands"""
        try:
            # For custom commands, we can implement specific logic
            # or delegate to appropriate capabilities based on action
            action = command.action
            parameters = command.parameters
            
            # Example: Custom AI command processing
            if action == "ai_command":
                command_text = parameters.get("command")
                return await self.capability_manager.execute_capability("intelligent_command_processing", {
                    "command": command_text
                }, {})
            
            # Example: Custom workflow execution
            elif action == "execute_workflow":
                workflow_name = parameters.get("workflow_name")
                workflow_params = parameters.get("parameters", {})
                return await self.capability_manager.execute_capability("workflow_orchestration", {
                    "operation": "execute_workflow",
                    "workflow_name": workflow_name,
                    "parameters": workflow_params
                }, {})
            
            else:
                return {"success": False, "error": f"Unknown custom action: {action}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_permissions(self, connection: RemoteConnection, command_type: RemoteCommandType, action: str) -> bool:
        """Check if connection has permissions for command"""
        # Simple permission check - in production, implement proper RBAC
        if not connection.is_authenticated:
            return False
        
        # Check if user has required permissions
        required_permission = f"{command_type.value}.{action}"
        return required_permission in connection.permissions or "admin" in connection.permissions
    
    async def _send_response(self, connection: RemoteConnection, data: Dict[str, Any]) -> None:
        """Send response to mobile app"""
        try:
            message = json.dumps(data, default=str)
            await connection.websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            connection.is_authenticated = False
        except Exception as e:
            self.logger.error(f"Failed to send response to mobile app: {e}")
    
    async def _send_command_result(self, connection: RemoteConnection, command_id: str, result: Dict[str, Any]) -> None:
        """Send command execution result to mobile app"""
        await self._send_response(connection, {
            "type": "command_result",
            "command_id": command_id,
            "result": result
        })
    
    async def _send_system_status(self, connection: RemoteConnection) -> None:
        """Send system status to mobile app"""
        status_data = {
            "type": "system_status",
            "server_time": time.time(),
            "active_connections": len(self.connections),
            "total_commands": len(self.commands),
            "stats": self.stats
        }
        await self._send_response(connection, status_data)
    
    async def _cancel_command(self, connection: RemoteConnection, data: Dict[str, Any]) -> None:
        """Cancel a command"""
        try:
            command_id = data.get("data", {}).get("command_id")
            if command_id and command_id in self.commands:
                command = self.commands[command_id]
                if command.status == RemoteCommandStatus.PROCESSING:
                    command.status = RemoteCommandStatus.CANCELLED
                    await self._send_command_result(connection, command_id, {
                        "success": False,
                        "error": "Command cancelled by user"
                    })
        except Exception as e:
            self.logger.error(f"Error cancelling command: {e}")
    
    async def _command_processor(self) -> None:
        """Background command processor"""
        while self._is_running:
            try:
                # Process any pending commands
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error in command processor: {e}")
    
    async def _connection_monitor(self) -> None:
        """Monitor connections and clean up inactive ones"""
        while self._is_running:
            try:
                current_time = time.time()
                
                for connection_id, connection in list(self.connections.items()):
                    # Check if connection is still alive
                    if current_time - connection.last_ping > 60:  # 60 second timeout
                        await connection.websocket.close()
                        del self.connections[connection_id]
                        self.stats["active_connections"] -= 1
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in connection monitor: {e}")
    
    async def _stats_reporter(self) -> None:
        """Report statistics periodically"""
        while self._is_running:
            try:
                self.logger.info(f"Remote control stats: {self.stats}")
                await asyncio.sleep(60)  # Report every minute
            except Exception as e:
                self.logger.error(f"Error in stats reporter: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get remote control interface statistics"""
        return {
            **self.stats,
            "active_connections": len(self.connections),
            "total_commands": len(self.commands),
            "is_running": self._is_running
        }

# Global remote control interface instance
_remote_control: Optional[RemoteControlInterface] = None

def get_remote_control() -> RemoteControlInterface:
    """Get global remote control interface instance"""
    global _remote_control
    if _remote_control is None:
        _remote_control = RemoteControlInterface()
    return _remote_control

