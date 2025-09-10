"""
WebSocket Server for JARVIS Computer Assistant

This module provides real-time remote control capabilities through WebSocket
connections, enabling mobile and web clients to control JARVIS remotely.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
import threading
from datetime import datetime

# Import JARVIS components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.platform import get_platform
from features.terminal_integration import get_terminal_manager
from features.ai_integration import get_ai_manager, get_rag_system
from integrations.speech_engines import get_speech_manager
from features.settings import get_settings_manager

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """WebSocket message types"""
    # Authentication
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    
    # Voice Control
    VOICE_COMMAND = "voice_command"
    VOICE_RESPONSE = "voice_response"
    VOICE_STATUS = "voice_status"
    
    # Terminal Control
    TERMINAL_COMMAND = "terminal_command"
    TERMINAL_RESPONSE = "terminal_response"
    TERMINAL_OUTPUT = "terminal_output"
    
    # AI Integration
    AI_REQUEST = "ai_request"
    AI_RESPONSE = "ai_response"
    
    # System Control
    SYSTEM_INFO = "system_info"
    SYSTEM_CONTROL = "system_control"
    SYSTEM_RESPONSE = "system_response"
    
    # File Operations
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_LIST = "file_list"
    FILE_RESPONSE = "file_response"
    
    # Status and Health
    PING = "ping"
    PONG = "pong"
    STATUS = "status"
    ERROR = "error"
    
    # Remote Control
    SCREENSHOT = "screenshot"
    SCREENSHOT_RESPONSE = "screenshot_response"
    KEYBOARD_INPUT = "keyboard_input"
    MOUSE_INPUT = "mouse_input"

@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    type: MessageType
    data: Dict[str, Any]
    timestamp: float
    message_id: str
    client_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "client_id": self.client_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        """Create from dictionary"""
        return cls(
            type=MessageType(data["type"]),
            data=data["data"],
            timestamp=data["timestamp"],
            message_id=data["message_id"],
            client_id=data.get("client_id")
        )

@dataclass
class ClientInfo:
    """Client connection information"""
    client_id: str
    websocket: WebSocketServerProtocol
    authenticated: bool
    connected_at: float
    last_activity: float
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    permissions: List[str] = None

class WebSocketServer:
    """WebSocket server for remote control"""
    
    def __init__(self, host: str = None, port: int = None, 
                 auth_token: Optional[str] = None):
        # Get settings from settings manager
        self.settings_manager = get_settings_manager()
        self.settings = self.settings_manager.get_settings()
        remote_settings = self.settings.get('remote', {})
        
        self.host = host or remote_settings.get('websocket_host', '0.0.0.0')
        self.port = port or remote_settings.get('websocket_port', 8766)
        self.auth_token = auth_token or self._generate_auth_token()
        self.clients: Dict[str, ClientInfo] = {}
        self.server = None
        self.running = False
        
        # Background tasks tracking
        self.background_tasks: List[asyncio.Task] = []
        
        # JARVIS components
        self.platform = get_platform()
        self.terminal_manager = get_terminal_manager()
        self.ai_manager = None
        self.rag_system = None
        self.speech_manager = None
        
        # Message handlers
        self.message_handlers = {
            MessageType.AUTH_REQUEST: self._handle_auth_request,
            MessageType.VOICE_COMMAND: self._handle_voice_command,
            MessageType.TERMINAL_COMMAND: self._handle_terminal_command,
            MessageType.AI_REQUEST: self._handle_ai_request,
            MessageType.SYSTEM_CONTROL: self._handle_system_control,
            MessageType.FILE_LIST: self._handle_file_list,
            MessageType.SCREENSHOT: self._handle_screenshot,
            MessageType.PING: self._handle_ping,
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize WebSocket server"""
        try:
            # Initialize JARVIS components
            await self._initialize_components()
            self.logger.info("WebSocket server initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket server: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup WebSocket server"""
        try:
            await self.stop()
            self.logger.info("WebSocket server cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup WebSocket server: {e}")
    
    def _generate_auth_token(self) -> str:
        """Generate authentication token"""
        return str(uuid.uuid4())
    
    async def start(self) -> None:
        """Start WebSocket server"""
        try:
            self.logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
            
            # Initialize JARVIS components
            await self._initialize_components()
            
            # Start server with proper task management
            self.server = await websockets.serve(
                lambda websocket, path: self._handle_client(websocket, path),
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )
            
            # Wait a bit for server to fully initialize
            await asyncio.sleep(0.1)
            
            self.logger.info(f"WebSocket server created: {self.server}")
            self.logger.info("Server task will be handled by websockets library")
            
            self.running = True
            self.logger.info(f"WebSocket server started successfully on {self.host}:{self.port}")
            self.logger.info(f"Authentication token: {self.auth_token}")
            
            # Start background tasks with proper error handling
            try:
                cleanup_task = asyncio.create_task(self._cleanup_inactive_clients())
                cleanup_task.set_name('_cleanup_inactive_clients')
                self.background_tasks.append(cleanup_task)
                
                broadcast_task = asyncio.create_task(self._broadcast_status())
                broadcast_task.set_name('_broadcast_status')
                self.background_tasks.append(broadcast_task)
                
                self.logger.info("Background tasks started successfully")
            except Exception as e:
                self.logger.warning(f"Failed to start background tasks: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop WebSocket server"""
        try:
            self.running = False
            
            # Check if event loop is still running
            try:
                loop = asyncio.get_running_loop()
                if loop.is_closed():
                    self.logger.warning("Event loop is closed, cannot stop WebSocket server properly")
                    return
            except RuntimeError:
                self.logger.warning("No running event loop, cannot stop WebSocket server properly")
                return
            
            # Cancel background tasks individually with proper cleanup
            self.logger.info(f"Cancelling {len(self.background_tasks)} background tasks")
            for i, task in enumerate(self.background_tasks):
                self.logger.info(f"Cancelling task {i}: {task.get_name() if hasattr(task, 'get_name') else 'unnamed'} - done: {task.done()}")
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=0.5)
                        self.logger.info(f"Task {i} cancelled successfully")
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        self.logger.info(f"Task {i} cancelled with timeout or cancellation")
                        pass
                    except Exception as e:
                        self.logger.warning(f"Error cancelling background task {i}: {e}")
            
            # Wait a bit for all tasks to be properly cancelled
            await asyncio.sleep(0.1)
            
            # Clear background tasks list
            self.background_tasks.clear()
            
            # Close all client connections
            for client in list(self.clients.values()):
                try:
                    if not client.websocket.closed:
                        await asyncio.wait_for(client.websocket.close(), timeout=0.5)
                except (asyncio.TimeoutError, Exception) as e:
                    self.logger.warning(f"Error closing client connection: {e}")
            
            # Clear clients
            self.clients.clear()
            
            # Close server
            if self.server:
                try:
                    self.server.close()
                    await asyncio.wait_for(self.server.wait_closed(), timeout=1.0)
                except (asyncio.TimeoutError, Exception) as e:
                    self.logger.warning(f"Error waiting for server to close: {e}")
                finally:
                    self.server = None
            
            self.logger.info("WebSocket server stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping WebSocket server: {e}")
    
    async def restart(self) -> bool:
        """Restart WebSocket server with updated settings"""
        try:
            self.logger.info("Restarting WebSocket server...")
            
            # Stop current server
            await self.stop()
            
            # Update settings from settings manager
            self.settings = self.settings_manager.get_settings()
            remote_settings = self.settings.get('remote', {})
            
            self.host = remote_settings.get('websocket_host', '0.0.0.0')
            self.port = remote_settings.get('websocket_port', 8766)
            
            # Start server with new settings
            await self.start()
            
            self.logger.info(f"WebSocket server restarted on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart WebSocket server: {e}")
            return False
    
    def update_settings(self) -> bool:
        """Update server settings from settings manager"""
        try:
            self.settings = self.settings_manager.get_settings()
            remote_settings = self.settings.get('remote', {})
            
            old_host = self.host
            old_port = self.port
            
            self.host = remote_settings.get('websocket_host', '0.0.0.0')
            self.port = remote_settings.get('websocket_port', 8766)
            
            # Check if settings changed
            if old_host != self.host or old_port != self.port:
                self.logger.info(f"WebSocket settings updated: {old_host}:{old_port} -> {self.host}:{self.port}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update WebSocket settings: {e}")
            return False
    
    async def _initialize_components(self) -> None:
        """Initialize JARVIS components"""
        try:
            # Initialize AI manager
            self.ai_manager = get_ai_manager()
            if not self.ai_manager.initialize():
                self.logger.warning("AI manager initialization failed")
            
            # Initialize RAG system
            self.rag_system = get_rag_system()
            if not await self.rag_system.initialize():
                self.logger.warning("RAG system initialization failed")
            
            # Initialize speech manager
            self.speech_manager = get_speech_manager()
            if not self.speech_manager.initialize():
                self.logger.warning("Speech manager initialization failed")
            
            self.logger.info("JARVIS components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize JARVIS components: {e}")
    
    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """Handle new client connection"""
        client_id = str(uuid.uuid4())
        client_info = ClientInfo(
            client_id=client_id,
            websocket=websocket,
            authenticated=False,
            connected_at=time.time(),
            last_activity=time.time(),
            user_agent=websocket.request_headers.get("User-Agent"),
            ip_address=websocket.remote_address[0] if websocket.remote_address else None,
            permissions=[]
        )
        
        self.clients[client_id] = client_info
        self.logger.info(f"Client connected: {client_id} from {client_info.ip_address}")
        
        try:
            async for message in websocket:
                await self._process_message(client_id, message)
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
    
    async def _process_message(self, client_id: str, message: str) -> None:
        """Process incoming message from client"""
        try:
            # Parse message
            data = json.loads(message)
            ws_message = WebSocketMessage.from_dict(data)
            ws_message.client_id = client_id
            
            # Update client activity
            if client_id in self.clients:
                self.clients[client_id].last_activity = time.time()
            
            # Check authentication for protected endpoints
            if ws_message.type not in [MessageType.AUTH_REQUEST, MessageType.PING]:
                if not self.clients[client_id].authenticated:
                    await self._send_error(client_id, "Authentication required")
                    return
            
            # Handle message
            if ws_message.type in self.message_handlers:
                await self.message_handlers[ws_message.type](ws_message)
            else:
                await self._send_error(client_id, f"Unknown message type: {ws_message.type}")
        
        except json.JSONDecodeError:
            await self._send_error(client_id, "Invalid JSON message")
        except Exception as e:
            self.logger.error(f"Error processing message from {client_id}: {e}")
            await self._send_error(client_id, f"Message processing error: {str(e)}")
    
    async def _handle_auth_request(self, message: WebSocketMessage) -> None:
        """Handle authentication request"""
        client_id = message.client_id
        token = message.data.get("token")
        
        if token == self.auth_token:
            self.clients[client_id].authenticated = True
            self.clients[client_id].permissions = message.data.get("permissions", [])
            
            response = WebSocketMessage(
                type=MessageType.AUTH_RESPONSE,
                data={"success": True, "message": "Authentication successful"},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            await self._send_message(client_id, response)
            self.logger.info(f"Client {client_id} authenticated successfully")
        else:
            response = WebSocketMessage(
                type=MessageType.AUTH_RESPONSE,
                data={"success": False, "message": "Invalid authentication token"},
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            await self._send_message(client_id, response)
            self.logger.warning(f"Client {client_id} authentication failed")
    
    async def _handle_voice_command(self, message: WebSocketMessage) -> None:
        """Handle voice command from client"""
        client_id = message.client_id
        command = message.data.get("command", "")
        
        try:
            # Process voice command through speech manager
            if self.speech_manager:
                # Simulate voice command processing
                response_text = f"Voice command received: {command}"
                
                # Send response
                response = WebSocketMessage(
                    type=MessageType.VOICE_RESPONSE,
                    data={
                        "command": command,
                        "response": response_text,
                        "success": True
                    },
                    timestamp=time.time(),
                    message_id=str(uuid.uuid4()),
                    client_id=client_id
                )
                
                await self._send_message(client_id, response)
            else:
                await self._send_error(client_id, "Speech manager not available")
        
        except Exception as e:
            self.logger.error(f"Error handling voice command: {e}")
            await self._send_error(client_id, f"Voice command error: {str(e)}")
    
    async def _handle_terminal_command(self, message: WebSocketMessage) -> None:
        """Handle terminal command from client"""
        client_id = message.client_id
        command = message.data.get("command", "")
        terminal_type = message.data.get("terminal_type")
        
        try:
            # Execute terminal command
            result = await self.terminal_manager.execute_command(
                command, 
                terminal_type=terminal_type
            )
            
            # Send response
            response = WebSocketMessage(
                type=MessageType.TERMINAL_RESPONSE,
                data={
                    "command": command,
                    "output": result.output,
                    "error": result.error,
                    "exit_code": result.exit_code,
                    "success": result.success,
                    "execution_time": result.execution_time
                },
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            await self._send_message(client_id, response)
        
        except Exception as e:
            self.logger.error(f"Error handling terminal command: {e}")
            await self._send_error(client_id, f"Terminal command error: {str(e)}")
    
    async def _handle_ai_request(self, message: WebSocketMessage) -> None:
        """Handle AI request from client"""
        client_id = message.client_id
        prompt = message.data.get("prompt", "")
        model = message.data.get("model")
        
        try:
            if self.ai_manager:
                # Create AI request
                from features.ai_integration import AIRequest
                ai_request = AIRequest(
                    prompt=prompt,
                    model=model or "gpt-3.5-turbo",
                    max_tokens=message.data.get("max_tokens", 1000),
                    temperature=message.data.get("temperature", 0.7)
                )
                
                # Generate response
                ai_response = await self.ai_manager.generate_response(ai_request)
                
                if ai_response:
                    response = WebSocketMessage(
                        type=MessageType.AI_RESPONSE,
                        data={
                            "prompt": prompt,
                            "response": ai_response.content,
                            "model": ai_response.model,
                            "tokens_used": ai_response.tokens_used,
                            "cost": ai_response.cost,
                            "success": True
                        },
                        timestamp=time.time(),
                        message_id=str(uuid.uuid4()),
                        client_id=client_id
                    )
                else:
                    response = WebSocketMessage(
                        type=MessageType.AI_RESPONSE,
                        data={
                            "prompt": prompt,
                            "response": "AI response generation failed",
                            "success": False
                        },
                        timestamp=time.time(),
                        message_id=str(uuid.uuid4()),
                        client_id=client_id
                    )
                
                await self._send_message(client_id, response)
            else:
                await self._send_error(client_id, "AI manager not available")
        
        except Exception as e:
            self.logger.error(f"Error handling AI request: {e}")
            await self._send_error(client_id, f"AI request error: {str(e)}")
    
    async def _handle_system_control(self, message: WebSocketMessage) -> None:
        """Handle system control command"""
        client_id = message.client_id
        action = message.data.get("action", "")
        params = message.data.get("params", {})
        
        try:
            result = await self._execute_system_control(action, params)
            
            response = WebSocketMessage(
                type=MessageType.SYSTEM_RESPONSE,
                data={
                    "action": action,
                    "result": result,
                    "success": True
                },
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            await self._send_message(client_id, response)
        
        except Exception as e:
            self.logger.error(f"Error handling system control: {e}")
            await self._send_error(client_id, f"System control error: {str(e)}")
    
    async def _handle_file_list(self, message: WebSocketMessage) -> None:
        """Handle file list request"""
        client_id = message.client_id
        path = message.data.get("path", ".")
        
        try:
            # Get file list
            import os
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                files.append({
                    "name": item,
                    "path": item_path,
                    "is_directory": os.path.isdir(item_path),
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
                })
            
            response = WebSocketMessage(
                type=MessageType.FILE_RESPONSE,
                data={
                    "path": path,
                    "files": files,
                    "success": True
                },
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            await self._send_message(client_id, response)
        
        except Exception as e:
            self.logger.error(f"Error handling file list: {e}")
            await self._send_error(client_id, f"File list error: {str(e)}")
    
    async def _handle_screenshot(self, message: WebSocketMessage) -> None:
        """Handle screenshot request"""
        client_id = message.client_id
        
        try:
            # Take screenshot using platform
            screenshot_data = await self.platform.take_screenshot()
            
            response = WebSocketMessage(
                type=MessageType.SCREENSHOT_RESPONSE,
                data={
                    "screenshot": screenshot_data,
                    "success": True
                },
                timestamp=time.time(),
                message_id=str(uuid.uuid4()),
                client_id=client_id
            )
            
            await self._send_message(client_id, response)
        
        except Exception as e:
            self.logger.error(f"Error handling screenshot: {e}")
            await self._send_error(client_id, f"Screenshot error: {str(e)}")
    
    async def _handle_ping(self, message: WebSocketMessage) -> None:
        """Handle ping message"""
        client_id = message.client_id
        
        response = WebSocketMessage(
            type=MessageType.PONG,
            data={"timestamp": time.time()},
            timestamp=time.time(),
            message_id=str(uuid.uuid4()),
            client_id=client_id
        )
        
        await self._send_message(client_id, response)
    
    async def _execute_system_control(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system control action"""
        try:
            if action == "get_system_info":
                return await self.platform.get_system_info()
            elif action == "get_audio_devices":
                return await self.platform.get_audio_devices()
            elif action == "set_volume":
                volume = params.get("volume", 50)
                await self.platform.set_volume(volume)
                return {"volume": volume}
            elif action == "set_brightness":
                brightness = params.get("brightness", 50)
                await self.platform.set_brightness(brightness)
                return {"brightness": brightness}
            else:
                return {"error": f"Unknown action: {action}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    async def _send_message(self, client_id: str, message: WebSocketMessage) -> None:
        """Send message to specific client"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].websocket.send(json.dumps(message.to_dict()))
            except Exception as e:
                self.logger.error(f"Error sending message to {client_id}: {e}")
    
    async def _send_error(self, client_id: str, error_message: str) -> None:
        """Send error message to client"""
        error_msg = WebSocketMessage(
            type=MessageType.ERROR,
            data={"error": error_message},
            timestamp=time.time(),
            message_id=str(uuid.uuid4()),
            client_id=client_id
        )
        
        await self._send_message(client_id, error_msg)
    
    async def _broadcast_message(self, message: WebSocketMessage) -> None:
        """Broadcast message to all connected clients"""
        for client_id in list(self.clients.keys()):
            await self._send_message(client_id, message)
    
    async def _cleanup_inactive_clients(self) -> None:
        """Clean up inactive client connections"""
        try:
            while self.running:
                try:
                    # Check if we should continue
                    if not self.running:
                        break
                    
                    current_time = time.time()
                    inactive_clients = []
                    
                    # Create a copy of clients to avoid modification during iteration
                    clients_copy = dict(self.clients)
                    
                    for client_id, client in clients_copy.items():
                        if current_time - client.last_activity > 300:  # 5 minutes
                            inactive_clients.append(client_id)
                    
                    for client_id in inactive_clients:
                        if client_id in self.clients:
                            try:
                                if not self.clients[client_id].websocket.closed:
                                    await asyncio.wait_for(
                                        self.clients[client_id].websocket.close(),
                                        timeout=1.0
                                    )
                            except (asyncio.TimeoutError, Exception):
                                pass  # Ignore errors when closing
                            finally:
                                if client_id in self.clients:
                                    del self.clients[client_id]
                                    self.logger.info(f"Cleaned up inactive client: {client_id}")
                    
                    # Use asyncio.sleep with cancellation support
                    try:
                        await asyncio.sleep(60)  # Check every minute
                    except asyncio.CancelledError:
                        break
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error in cleanup task: {e}")
                    try:
                        await asyncio.sleep(60)
                    except asyncio.CancelledError:
                        break
        except asyncio.CancelledError:
            pass  # Expected when task is cancelled
        except Exception as e:
            self.logger.error(f"Fatal error in cleanup task: {e}")
    
    async def _broadcast_status(self) -> None:
        """Broadcast server status to all clients"""
        try:
            while self.running:
                try:
                    # Check if we should continue
                    if not self.running:
                        break
                    
                    # Only broadcast if we have clients
                    if self.clients:
                        status_msg = WebSocketMessage(
                            type=MessageType.STATUS,
                            data={
                                "server_time": time.time(),
                                "connected_clients": len(self.clients),
                                "uptime": time.time() - (self.clients[list(self.clients.keys())[0]].connected_at if self.clients else time.time())
                            },
                            timestamp=time.time(),
                            message_id=str(uuid.uuid4())
                        )
                        
                        await self._broadcast_message(status_msg)
                    
                    # Use asyncio.sleep with cancellation support
                    try:
                        await asyncio.sleep(30)  # Broadcast every 30 seconds
                    except asyncio.CancelledError:
                        break
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"Error broadcasting status: {e}")
                    try:
                        await asyncio.sleep(30)
                    except asyncio.CancelledError:
                        break
        except asyncio.CancelledError:
            pass  # Expected when task is cancelled
        except Exception as e:
            self.logger.error(f"Fatal error in broadcast status task: {e}")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "host": self.host,
            "port": self.port,
            "running": self.running,
            "connected_clients": len(self.clients),
            "auth_token": self.auth_token,
            "uptime": time.time() - (self.clients[list(self.clients.keys())[0]].connected_at if self.clients else time.time())
        }

# Global WebSocket server instance
_websocket_server: Optional[WebSocketServer] = None

def get_websocket_server(host: str = None, port: int = None) -> WebSocketServer:
    """Get global WebSocket server instance"""
    global _websocket_server
    if _websocket_server is None:
        _websocket_server = WebSocketServer(host, port)
    return _websocket_server
