"""
Real-time Mobile Monitoring System for JARVIS Computer Assistant

Provides live command execution monitoring and status updates for mobile applications
through WebSocket connections and real-time data streaming.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

class MobileEventType(Enum):
    """Types of events sent to mobile app"""
    COMMAND_STARTED = "command_started"
    COMMAND_PROGRESS = "command_progress"
    COMMAND_COMPLETED = "command_completed"
    COMMAND_FAILED = "command_failed"
    SYSTEM_STATUS = "system_status"
    LOG_MESSAGE = "log_message"
    ERROR_OCCURRED = "error_occurred"
    SESSION_UPDATE = "session_update"
    TERMINAL_OUTPUT = "terminal_output"
    FILE_OPERATION = "file_operation"
    APPLICATION_EVENT = "application_event"

class MobileConnectionStatus(Enum):
    """Mobile connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

@dataclass
class MobileEvent:
    """Event sent to mobile app"""
    event_id: str
    event_type: MobileEventType
    timestamp: float
    data: Dict[str, Any]
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    requires_ack: bool = False

@dataclass
class MobileConnection:
    """Mobile app connection"""
    connection_id: str
    websocket: WebSocketServerProtocol
    device_info: Dict[str, Any]
    last_ping: float
    status: MobileConnectionStatus
    subscribed_events: Set[MobileEventType] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)

@dataclass
class CommandExecution:
    """Command execution tracking for mobile monitoring"""
    execution_id: str
    command: str
    status: str
    start_time: float
    end_time: Optional[float] = None
    progress: float = 0.0
    output: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class MobileMonitoringSystem:
    """Real-time mobile monitoring system"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connections: Dict[str, MobileConnection] = {}
        self.executions: Dict[str, CommandExecution] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.server: Optional[websockets.WebSocketServer] = None
        self._is_running = False
        self.logger = logging.getLogger(__name__)
        
        # Event handlers
        self.event_handlers: Dict[MobileEventType, List[Callable]] = {}
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_events_sent": 0,
            "total_executions_tracked": 0
        }
    
    async def start(self) -> bool:
        """Start the mobile monitoring system"""
        try:
            self.server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port
            )
            self._is_running = True
            
            # Start background tasks
            asyncio.create_task(self._event_processor())
            asyncio.create_task(self._heartbeat_monitor())
            asyncio.create_task(self._stats_reporter())
            
            self.logger.info(f"Mobile monitoring system started on {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start mobile monitoring system: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the mobile monitoring system"""
        try:
            self._is_running = False
            
            # Close all connections
            for connection in self.connections.values():
                await connection.websocket.close()
            
            # Close server
            if self.server:
                self.server.close()
                await self.server.wait_closed()
            
            self.logger.info("Mobile monitoring system stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop mobile monitoring system: {e}")
    
    async def _handle_connection(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """Handle new mobile app connection"""
        connection_id = str(uuid.uuid4())
        
        try:
            # Get device info from initial message
            device_info = await self._get_device_info(websocket)
            
            # Create connection
            connection = MobileConnection(
                connection_id=connection_id,
                websocket=websocket,
                device_info=device_info,
                last_ping=time.time(),
                status=MobileConnectionStatus.CONNECTED
            )
            
            self.connections[connection_id] = connection
            self.stats["total_connections"] += 1
            self.stats["active_connections"] += 1
            
            self.logger.info(f"Mobile app connected: {connection_id}")
            
            # Send welcome message
            await self._send_event(connection, MobileEventType.SYSTEM_STATUS, {
                "message": "Connected to JARVIS Computer Assistant",
                "server_time": time.time(),
                "connection_id": connection_id
            })
            
            # Handle messages from mobile app
            async for message in websocket:
                await self._handle_mobile_message(connection, message)
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Mobile app disconnected: {connection_id}")
        except Exception as e:
            self.logger.error(f"Error handling mobile connection {connection_id}: {e}")
        finally:
            # Cleanup connection
            if connection_id in self.connections:
                del self.connections[connection_id]
                self.stats["active_connections"] -= 1
    
    async def _get_device_info(self, websocket: WebSocketServerProtocol) -> Dict[str, Any]:
        """Get device information from mobile app"""
        try:
            # Wait for device info message
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(message)
            
            if data.get("type") == "device_info":
                return data.get("data", {})
        except Exception as e:
            self.logger.warning(f"Failed to get device info: {e}")
        
        return {
            "platform": "unknown",
            "app_version": "unknown",
            "device_id": "unknown"
        }
    
    async def _handle_mobile_message(self, connection: MobileConnection, message: str) -> None:
        """Handle message from mobile app"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                # Subscribe to specific event types
                event_types = data.get("event_types", [])
                for event_type_str in event_types:
                    try:
                        event_type = MobileEventType(event_type_str)
                        connection.subscribed_events.add(event_type)
                    except ValueError:
                        self.logger.warning(f"Unknown event type: {event_type_str}")
                
                await self._send_event(connection, MobileEventType.SYSTEM_STATUS, {
                    "message": f"Subscribed to {len(event_types)} event types",
                    "subscribed_events": list(connection.subscribed_events)
                })
            
            elif message_type == "unsubscribe":
                # Unsubscribe from specific event types
                event_types = data.get("event_types", [])
                for event_type_str in event_types:
                    try:
                        event_type = MobileEventType(event_type_str)
                        connection.subscribed_events.discard(event_type)
                    except ValueError:
                        pass
                
                await self._send_event(connection, MobileEventType.SYSTEM_STATUS, {
                    "message": f"Unsubscribed from {len(event_types)} event types",
                    "subscribed_events": list(connection.subscribed_events)
                })
            
            elif message_type == "ping":
                # Handle ping
                connection.last_ping = time.time()
                await self._send_event(connection, MobileEventType.SYSTEM_STATUS, {
                    "message": "pong",
                    "timestamp": time.time()
                })
            
            elif message_type == "get_status":
                # Send current system status
                await self._send_system_status(connection)
            
            else:
                self.logger.warning(f"Unknown message type from mobile: {message_type}")
        
        except json.JSONDecodeError:
            self.logger.warning(f"Invalid JSON from mobile app: {message}")
        except Exception as e:
            self.logger.error(f"Error handling mobile message: {e}")
    
    async def _send_event(self, connection: MobileConnection, event_type: MobileEventType, 
                         data: Dict[str, Any], priority: int = 1, requires_ack: bool = False) -> None:
        """Send event to mobile app"""
        try:
            # Check if connection is subscribed to this event type
            if connection.subscribed_events and event_type not in connection.subscribed_events:
                return
            
            event = MobileEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                timestamp=time.time(),
                data=data,
                priority=priority,
                requires_ack=requires_ack
            )
            
            message = json.dumps(asdict(event), default=str)
            await connection.websocket.send(message)
            
            self.stats["total_events_sent"] += 1
            
        except websockets.exceptions.ConnectionClosed:
            connection.status = MobileConnectionStatus.DISCONNECTED
        except Exception as e:
            self.logger.error(f"Failed to send event to mobile app: {e}")
    
    async def _send_system_status(self, connection: MobileConnection) -> None:
        """Send current system status to mobile app"""
        status_data = {
            "server_time": time.time(),
            "active_connections": len(self.connections),
            "active_executions": len([e for e in self.executions.values() if e.status == "running"]),
            "total_executions": len(self.executions),
            "stats": self.stats
        }
        
        await self._send_event(connection, MobileEventType.SYSTEM_STATUS, status_data)
    
    async def _event_processor(self) -> None:
        """Process events from queue and send to mobile apps"""
        while self._is_running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # Send to all connected mobile apps
                for connection in self.connections.values():
                    if connection.status == MobileConnectionStatus.CONNECTED:
                        await self._send_event(
                            connection, 
                            event.event_type, 
                            event.data, 
                            event.priority, 
                            event.requires_ack
                        )
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
    
    async def _heartbeat_monitor(self) -> None:
        """Monitor mobile app connections and send heartbeats"""
        while self._is_running:
            try:
                current_time = time.time()
                
                for connection in self.connections.values():
                    # Check if connection is still alive
                    if current_time - connection.last_ping > 30:  # 30 second timeout
                        connection.status = MobileConnectionStatus.DISCONNECTED
                        await connection.websocket.close()
                        continue
                    
                    # Send heartbeat every 10 seconds
                    if current_time - connection.last_ping > 10:
                        await self._send_event(connection, MobileEventType.SYSTEM_STATUS, {
                            "message": "heartbeat",
                            "timestamp": current_time
                        })
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat monitor: {e}")
    
    async def _stats_reporter(self) -> None:
        """Report statistics periodically"""
        while self._is_running:
            try:
                self.logger.info(f"Mobile monitoring stats: {self.stats}")
                await asyncio.sleep(60)  # Report every minute
            except Exception as e:
                self.logger.error(f"Error in stats reporter: {e}")
    
    # Public API methods for other components
    
    async def track_command_start(self, execution_id: str, command: str, metadata: Dict[str, Any] = None) -> None:
        """Track command execution start"""
        execution = CommandExecution(
            execution_id=execution_id,
            command=command,
            status="running",
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        self.executions[execution_id] = execution
        self.stats["total_executions_tracked"] += 1
        
        # Send event to mobile apps
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.COMMAND_STARTED,
            timestamp=time.time(),
            data={
                "execution_id": execution_id,
                "command": command,
                "start_time": execution.start_time,
                "metadata": metadata or {}
            },
            priority=2
        ))
    
    async def track_command_progress(self, execution_id: str, progress: float, message: str = None) -> None:
        """Track command execution progress"""
        if execution_id not in self.executions:
            return
        
        execution = self.executions[execution_id]
        execution.progress = progress
        
        # Send event to mobile apps
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.COMMAND_PROGRESS,
            timestamp=time.time(),
            data={
                "execution_id": execution_id,
                "command": execution.command,
                "progress": progress,
                "message": message,
                "elapsed_time": time.time() - execution.start_time
            },
            priority=1
        ))
    
    async def track_command_completed(self, execution_id: str, output: str = "", metadata: Dict[str, Any] = None) -> None:
        """Track command execution completion"""
        if execution_id not in self.executions:
            return
        
        execution = self.executions[execution_id]
        execution.status = "completed"
        execution.end_time = time.time()
        execution.output = output
        if metadata:
            execution.metadata.update(metadata)
        
        # Send event to mobile apps
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.COMMAND_COMPLETED,
            timestamp=time.time(),
            data={
                "execution_id": execution_id,
                "command": execution.command,
                "output": output,
                "start_time": execution.start_time,
                "end_time": execution.end_time,
                "duration": execution.end_time - execution.start_time,
                "metadata": execution.metadata
            },
            priority=2
        ))
    
    async def track_command_failed(self, execution_id: str, error: str, metadata: Dict[str, Any] = None) -> None:
        """Track command execution failure"""
        if execution_id not in self.executions:
            return
        
        execution = self.executions[execution_id]
        execution.status = "failed"
        execution.end_time = time.time()
        execution.error = error
        if metadata:
            execution.metadata.update(metadata)
        
        # Send event to mobile apps
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.COMMAND_FAILED,
            timestamp=time.time(),
            data={
                "execution_id": execution_id,
                "command": execution.command,
                "error": error,
                "start_time": execution.start_time,
                "end_time": execution.end_time,
                "duration": execution.end_time - execution.start_time,
                "metadata": execution.metadata
            },
            priority=3
        ))
    
    async def send_log_message(self, level: str, message: str, metadata: Dict[str, Any] = None) -> None:
        """Send log message to mobile apps"""
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.LOG_MESSAGE,
            timestamp=time.time(),
            data={
                "level": level,
                "message": message,
                "metadata": metadata or {}
            },
            priority=1
        ))
    
    async def send_error(self, error: str, context: Dict[str, Any] = None) -> None:
        """Send error to mobile apps"""
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.ERROR_OCCURRED,
            timestamp=time.time(),
            data={
                "error": error,
                "context": context or {}
            },
            priority=4
        ))
    
    async def send_terminal_output(self, execution_id: str, output: str) -> None:
        """Send terminal output to mobile apps"""
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.TERMINAL_OUTPUT,
            timestamp=time.time(),
            data={
                "execution_id": execution_id,
                "output": output
            },
            priority=1
        ))
    
    async def send_file_operation(self, operation: str, file_path: str, status: str, metadata: Dict[str, Any] = None) -> None:
        """Send file operation event to mobile apps"""
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.FILE_OPERATION,
            timestamp=time.time(),
            data={
                "operation": operation,
                "file_path": file_path,
                "status": status,
                "metadata": metadata or {}
            },
            priority=1
        ))
    
    async def send_application_event(self, app_name: str, event: str, metadata: Dict[str, Any] = None) -> None:
        """Send application event to mobile apps"""
        await self.event_queue.put(MobileEvent(
            event_id=str(uuid.uuid4()),
            event_type=MobileEventType.APPLICATION_EVENT,
            timestamp=time.time(),
            data={
                "app_name": app_name,
                "event": event,
                "metadata": metadata or {}
            },
            priority=1
        ))
    
    def get_connection_count(self) -> int:
        """Get number of active mobile connections"""
        return len(self.connections)
    
    def get_execution_count(self) -> int:
        """Get number of tracked executions"""
        return len(self.executions)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring system statistics"""
        return {
            **self.stats,
            "active_connections": len(self.connections),
            "active_executions": len([e for e in self.executions.values() if e.status == "running"]),
            "is_running": self._is_running
        }

# Global mobile monitoring system instance
_mobile_monitoring: Optional[MobileMonitoringSystem] = None

def get_mobile_monitoring() -> MobileMonitoringSystem:
    """Get global mobile monitoring system instance"""
    global _mobile_monitoring
    if _mobile_monitoring is None:
        _mobile_monitoring = MobileMonitoringSystem()
    return _mobile_monitoring

