"""
Remote Control Capabilities for JARVIS Computer Assistant

Provides capabilities for remote computer control through mobile applications.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from ..remote_control_interface import RemoteControlInterface, get_remote_control

logger = logging.getLogger(__name__)

class RemoteControlExecutor:
    """Remote control capabilities executor"""
    
    def __init__(self):
        self.remote_control = get_remote_control()
        self._is_initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize remote control executor"""
        try:
            if not self.remote_control._is_running:
                success = await self.remote_control.start()
                if not success:
                    return False
            
            self._is_initialized = True
            self.logger.info("Remote control executor initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize remote control executor: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # Don't stop the global remote control interface here
            # as it might be used by other components
            self._is_initialized = False
            self.logger.info("Remote control executor cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup remote control executor: {e}")
    
    def _can_handle(self, parameters: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("remote_control" in parameters or
                "start_remote_interface" in parameters or
                "stop_remote_interface" in parameters or
                "remote_status" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute remote control capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Remote control executor not initialized"}
            
            operation = parameters.get("operation")
            if not operation:
                return {"success": False, "error": "Operation not specified"}
            
            if operation == "start_interface":
                return await self._start_interface(parameters)
            elif operation == "stop_interface":
                return await self._stop_interface(parameters)
            elif operation == "get_connection_status":
                return await self._get_connection_status(parameters)
            elif operation == "get_command_status":
                return await self._get_command_status(parameters)
            elif operation == "get_stats":
                return await self._get_stats(parameters)
            elif operation == "send_remote_command":
                return await self._send_remote_command(parameters)
            elif operation == "broadcast_message":
                return await self._broadcast_message(parameters)
            elif operation == "get_active_connections":
                return await self._get_active_connections(parameters)
            elif operation == "disconnect_client":
                return await self._disconnect_client(parameters)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        
        except Exception as e:
            self.logger.error(f"Failed to execute remote control capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _start_interface(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Start remote control interface"""
        try:
            host = parameters.get("host", "localhost")
            port = parameters.get("port", 8767)
            
            # Update host and port if provided
            if host != self.remote_control.host or port != self.remote_control.port:
                self.remote_control.host = host
                self.remote_control.port = port
            
            if not self.remote_control._is_running:
                success = await self.remote_control.start()
                if not success:
                    return {"success": False, "error": "Failed to start remote control interface"}
            
            return {
                "success": True,
                "message": "Remote control interface started",
                "host": host,
                "port": port,
                "is_running": self.remote_control._is_running
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stop_interface(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Stop remote control interface"""
        try:
            if self.remote_control._is_running:
                await self.remote_control.stop()
            
            return {
                "success": True,
                "message": "Remote control interface stopped",
                "is_running": self.remote_control._is_running
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_connection_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get connection status"""
        try:
            connection_id = parameters.get("connection_id")
            
            if connection_id:
                # Get specific connection status
                if connection_id in self.remote_control.connections:
                    connection = self.remote_control.connections[connection_id]
                    return {
                        "success": True,
                        "connection": {
                            "connection_id": connection.connection_id,
                            "user_id": connection.user_id,
                            "device_id": connection.device_id,
                            "is_authenticated": connection.is_authenticated,
                            "permissions": list(connection.permissions),
                            "last_ping": connection.last_ping,
                            "created_at": connection.created_at
                        }
                    }
                else:
                    return {"success": False, "error": "Connection not found"}
            else:
                # Get all connections
                connections = []
                for conn_id, connection in self.remote_control.connections.items():
                    connections.append({
                        "connection_id": connection.connection_id,
                        "user_id": connection.user_id,
                        "device_id": connection.device_id,
                        "is_authenticated": connection.is_authenticated,
                        "permissions": list(connection.permissions),
                        "last_ping": connection.last_ping,
                        "created_at": connection.created_at
                    })
                
                return {
                    "success": True,
                    "connections": connections,
                    "total_connections": len(connections)
                }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_command_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get command status"""
        try:
            command_id = parameters.get("command_id")
            
            if command_id:
                # Get specific command status
                if command_id in self.remote_control.commands:
                    command = self.remote_control.commands[command_id]
                    return {
                        "success": True,
                        "command": {
                            "command_id": command.command_id,
                            "command_type": command.command_type.value,
                            "action": command.action,
                            "user_id": command.user_id,
                            "device_id": command.device_id,
                            "status": command.status.value,
                            "timestamp": command.timestamp,
                            "execution_time": command.execution_time,
                            "result": command.result,
                            "error": command.error,
                            "metadata": command.metadata
                        }
                    }
                else:
                    return {"success": False, "error": "Command not found"}
            else:
                # Get all commands
                commands = []
                for cmd_id, command in self.remote_control.commands.items():
                    commands.append({
                        "command_id": command.command_id,
                        "command_type": command.command_type.value,
                        "action": command.action,
                        "user_id": command.user_id,
                        "device_id": command.device_id,
                        "status": command.status.value,
                        "timestamp": command.timestamp,
                        "execution_time": command.execution_time
                    })
                
                return {
                    "success": True,
                    "commands": commands,
                    "total_commands": len(commands)
                }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_stats(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get remote control statistics"""
        try:
            stats = self.remote_control.get_stats()
            
            return {
                "success": True,
                "stats": stats
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _send_remote_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Send command to remote clients"""
        try:
            connection_id = parameters.get("connection_id")
            command_type = parameters.get("command_type")
            action = parameters.get("action")
            parameters_data = parameters.get("parameters", {})
            
            if not all([connection_id, command_type, action]):
                return {"success": False, "error": "Connection ID, command type, and action are required"}
            
            if connection_id not in self.remote_control.connections:
                return {"success": False, "error": "Connection not found"}
            
            connection = self.remote_control.connections[connection_id]
            
            # Send command to client
            await self.remote_control._send_response(connection, {
                "type": "remote_command",
                "command_type": command_type,
                "action": action,
                "parameters": parameters_data
            })
            
            return {
                "success": True,
                "message": "Command sent to remote client",
                "connection_id": connection_id
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _broadcast_message(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast message to all connected clients"""
        try:
            message_type = parameters.get("message_type", "broadcast")
            data = parameters.get("data", {})
            user_filter = parameters.get("user_filter")  # Optional user filter
            
            sent_count = 0
            for connection in self.remote_control.connections.values():
                # Apply user filter if specified
                if user_filter and connection.user_id != user_filter:
                    continue
                
                try:
                    await self.remote_control._send_response(connection, {
                        "type": message_type,
                        "data": data,
                        "timestamp": time.time()
                    })
                    sent_count += 1
                except Exception as e:
                    self.logger.warning(f"Failed to send broadcast to {connection.connection_id}: {e}")
            
            return {
                "success": True,
                "message": f"Broadcast sent to {sent_count} clients",
                "sent_count": sent_count
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_active_connections(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get active connections with details"""
        try:
            connections = []
            for conn_id, connection in self.remote_control.connections.items():
                connections.append({
                    "connection_id": connection.connection_id,
                    "user_id": connection.user_id,
                    "device_id": connection.device_id,
                    "device_info": connection.device_info,
                    "is_authenticated": connection.is_authenticated,
                    "permissions": list(connection.permissions),
                    "last_ping": connection.last_ping,
                    "created_at": connection.created_at,
                    "is_active": time.time() - connection.last_ping < 60  # 60 second timeout
                })
            
            return {
                "success": True,
                "connections": connections,
                "total_connections": len(connections),
                "active_connections": len([c for c in connections if c["is_active"]])
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _disconnect_client(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Disconnect a specific client"""
        try:
            connection_id = parameters.get("connection_id")
            if not connection_id:
                return {"success": False, "error": "Connection ID is required"}
            
            if connection_id not in self.remote_control.connections:
                return {"success": False, "error": "Connection not found"}
            
            connection = self.remote_control.connections[connection_id]
            await connection.websocket.close()
            
            return {
                "success": True,
                "message": f"Client {connection_id} disconnected",
                "connection_id": connection_id
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}

