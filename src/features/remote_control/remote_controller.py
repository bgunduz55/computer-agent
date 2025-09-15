"""
Remote Controller for JARVIS Computer Assistant

This module provides high-level remote control functionality that integrates
with the WebSocket server and provides easy-to-use remote control methods.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .websocket_server import WebSocketServer, MessageType, WebSocketMessage, get_websocket_server

logger = logging.getLogger(__name__)

class RemoteAction(Enum):
    """Remote control actions"""
    VOICE_COMMAND = "voice_command"
    TERMINAL_COMMAND = "terminal_command"
    AI_REQUEST = "ai_request"
    SYSTEM_CONTROL = "system_control"
    FILE_OPERATION = "file_operation"
    SCREENSHOT = "screenshot"
    SYSTEM_INFO = "system_info"

@dataclass
class RemoteResponse:
    """Remote control response"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: float = 0.0

class RemoteController:
    """High-level remote control interface"""
    
    def __init__(self, websocket_server: Optional[WebSocketServer] = None):
        self.websocket_server = websocket_server or get_websocket_server()
        self.logger = logging.getLogger(__name__)
        self.response_handlers: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
    
    async def initialize(self) -> bool:
        """Initialize remote controller"""
        try:
            self.logger.info("Remote controller initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize remote controller: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup remote controller"""
        try:
            await self.stop_server()
            self.logger.info("Remote controller cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup remote controller: {e}")
    
    async def start_server(self, host: str = None, port: int = None) -> None:
        """Start the remote control server"""
        try:
            await self.websocket_server.start()
            self.logger.info("Remote control server started")
        except Exception as e:
            self.logger.error(f"Failed to start remote control server: {e}")
            raise
    
    async def stop_server(self) -> None:
        """Stop the remote control server"""
        try:
            if self.websocket_server:
                await self.websocket_server.stop()
            self.logger.info("Remote control server stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop remote control server: {e}")
            raise
    
    async def execute_voice_command(self, command: str, client_id: Optional[str] = None) -> RemoteResponse:
        """Execute voice command remotely"""
        try:
            start_time = time.time()
            
            message = WebSocketMessage(
                type=MessageType.VOICE_COMMAND,
                data={"command": command},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            # Send message to all clients or specific client
            if client_id:
                await self.websocket_server._send_message(client_id, message)
            else:
                await self.websocket_server._broadcast_message(message)
            
            execution_time = time.time() - start_time
            
            return RemoteResponse(
                success=True,
                data={"command": command, "execution_time": execution_time},
                execution_time=execution_time,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Error executing voice command: {e}")
            return RemoteResponse(
                success=False,
                data={},
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=time.time()
            )
    
    async def execute_terminal_command(self, command: str, terminal_type: Optional[str] = None,
                                     client_id: Optional[str] = None) -> RemoteResponse:
        """Execute terminal command remotely"""
        try:
            start_time = time.time()
            
            message = WebSocketMessage(
                type=MessageType.TERMINAL_COMMAND,
                data={"command": command, "terminal_type": terminal_type},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            # Send message to all clients or specific client
            if client_id:
                await self.websocket_server._send_message(client_id, message)
            else:
                await self.websocket_server._broadcast_message(message)
            
            execution_time = time.time() - start_time
            
            return RemoteResponse(
                success=True,
                data={"command": command, "terminal_type": terminal_type, "execution_time": execution_time},
                execution_time=execution_time,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Error executing terminal command: {e}")
            return RemoteResponse(
                success=False,
                data={},
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=time.time()
            )
    
    async def execute_ai_request(self, prompt: str, model: Optional[str] = None,
                               max_tokens: int = 1000, temperature: float = 0.7,
                               client_id: Optional[str] = None) -> RemoteResponse:
        """Execute AI request remotely"""
        try:
            start_time = time.time()
            
            message = WebSocketMessage(
                type=MessageType.AI_REQUEST,
                data={
                    "prompt": prompt,
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            # Send message to all clients or specific client
            if client_id:
                await self.websocket_server._send_message(client_id, message)
            else:
                await self.websocket_server._broadcast_message(message)
            
            execution_time = time.time() - start_time
            
            return RemoteResponse(
                success=True,
                data={"prompt": prompt, "model": model, "execution_time": execution_time},
                execution_time=execution_time,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Error executing AI request: {e}")
            return RemoteResponse(
                success=False,
                data={},
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=time.time()
            )
    
    async def execute_system_control(self, action: str, params: Dict[str, Any] = None,
                                   client_id: Optional[str] = None) -> RemoteResponse:
        """Execute system control action remotely"""
        try:
            start_time = time.time()
            
            message = WebSocketMessage(
                type=MessageType.SYSTEM_CONTROL,
                data={"action": action, "params": params or {}},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            # Send message to all clients or specific client
            if client_id:
                await self.websocket_server._send_message(client_id, message)
            else:
                await self.websocket_server._broadcast_message(message)
            
            execution_time = time.time() - start_time
            
            return RemoteResponse(
                success=True,
                data={"action": action, "params": params, "execution_time": execution_time},
                execution_time=execution_time,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Error executing system control: {e}")
            return RemoteResponse(
                success=False,
                data={},
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=time.time()
            )
    
    async def get_system_info(self, client_id: Optional[str] = None) -> RemoteResponse:
        """Get system information remotely"""
        try:
            start_time = time.time()
            
            message = WebSocketMessage(
                type=MessageType.SYSTEM_INFO,
                data={},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            # Send message to all clients or specific client
            if client_id:
                await self.websocket_server._send_message(client_id, message)
            else:
                await self.websocket_server._broadcast_message(message)
            
            execution_time = time.time() - start_time
            
            return RemoteResponse(
                success=True,
                data={"execution_time": execution_time},
                execution_time=execution_time,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return RemoteResponse(
                success=False,
                data={},
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=time.time()
            )
    
    async def take_screenshot(self, client_id: Optional[str] = None) -> RemoteResponse:
        """Take screenshot remotely"""
        try:
            start_time = time.time()
            
            message = WebSocketMessage(
                type=MessageType.SCREENSHOT,
                data={},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            # Send message to all clients or specific client
            if client_id:
                await self.websocket_server._send_message(client_id, message)
            else:
                await self.websocket_server._broadcast_message(message)
            
            execution_time = time.time() - start_time
            
            return RemoteResponse(
                success=True,
                data={"execution_time": execution_time},
                execution_time=execution_time,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return RemoteResponse(
                success=False,
                data={},
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=time.time()
            )
    
    async def list_files(self, path: str = ".", client_id: Optional[str] = None) -> RemoteResponse:
        """List files in directory remotely"""
        try:
            start_time = time.time()
            
            message = WebSocketMessage(
                type=MessageType.FILE_LIST,
                data={"path": path},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            # Send message to all clients or specific client
            if client_id:
                await self.websocket_server._send_message(client_id, message)
            else:
                await self.websocket_server._broadcast_message(message)
            
            execution_time = time.time() - start_time
            
            return RemoteResponse(
                success=True,
                data={"path": path, "execution_time": execution_time},
                execution_time=execution_time,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return RemoteResponse(
                success=False,
                data={},
                error=str(e),
                execution_time=time.time() - start_time,
                timestamp=time.time()
            )
    
    def get_connected_clients(self) -> List[Dict[str, Any]]:
        """Get list of connected clients"""
        clients = []
        for client_id, client_info in self.websocket_server.clients.items():
            clients.append({
                "client_id": client_id,
                "authenticated": client_info.authenticated,
                "connected_at": client_info.connected_at,
                "last_activity": client_info.last_activity,
                "user_agent": client_info.user_agent,
                "ip_address": client_info.ip_address,
                "permissions": client_info.permissions
            })
        return clients
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status information"""
        return self.websocket_server.get_server_info()
    
    async def broadcast_message(self, message_type: MessageType, data: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients"""
        try:
            message = WebSocketMessage(
                type=message_type,
                data=data,
                timestamp=time.time(),
                message_id=str(uuid.uuid4())
            )
            
            await self.websocket_server._broadcast_message(message)
            self.logger.info(f"Broadcasted {message_type.value} message to all clients")
        
        except Exception as e:
            self.logger.error(f"Error broadcasting message: {e}")
    
    async def send_message_to_client(self, client_id: str, message_type: MessageType, 
                                   data: Dict[str, Any]) -> bool:
        """Send message to specific client"""
        try:
            message = WebSocketMessage(
                type=message_type,
                data=data,
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            await self.websocket_server._send_message(client_id, message)
            self.logger.info(f"Sent {message_type.value} message to client {client_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error sending message to client {client_id}: {e}")
            return False

# Global remote controller instance
_remote_controller: Optional[RemoteController] = None

def get_remote_controller() -> RemoteController:
    """Get global remote controller instance"""
    global _remote_controller
    if _remote_controller is None:
        _remote_controller = RemoteController()
    return _remote_controller
