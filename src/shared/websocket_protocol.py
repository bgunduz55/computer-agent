"""
WebSocket Protocol Definitions

Standardized message protocol for communication between
Flutter client and Python server.
"""

import json
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """WebSocket message types"""
    # Connection Management
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    HEARTBEAT = "heartbeat"
    
    # Authentication
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    
    # Voice Control
    VOICE_COMMAND = "voiceCommand"
    VOICE_RESPONSE = "voiceResponse"
    VOICE_STATUS = "voiceStatus"
    
    # Command Processing
    COMMAND = "command"
    COMMAND_RESPONSE = "commandResponse"
    
    # Intelligent Commands
    INTELLIGENT_COMMAND = "intelligentCommand"
    INTELLIGENT_COMMAND_RESPONSE = "intelligentCommandResponse"
    INTELLIGENT_COMMAND_PROGRESS = "intelligentCommandProgress"
    INTELLIGENT_COMMAND_STEP = "intelligentCommandStep"
    
    # Quick Commands
    QUICK_COMMAND = "quickCommand"
    QUICK_COMMAND_RESPONSE = "quickCommandResponse"
    
    # Capability System
    CAPABILITY_REQUEST = "capabilityRequest"
    CAPABILITY_RESPONSE = "capabilityResponse"
    CAPABILITY_UPDATE = "capabilityUpdate"
    
    # Terminal Control
    TERMINAL_COMMAND = "terminalCommand"
    TERMINAL_RESPONSE = "terminalResponse"
    TERMINAL_OUTPUT = "terminalOutput"
    
    # AI Integration
    AI_REQUEST = "aiRequest"
    AI_RESPONSE = "aiResponse"
    
    # System Control
    SYSTEM_INFO = "systemInfo"
    SYSTEM_CONTROL = "systemControl"
    SYSTEM_RESPONSE = "systemResponse"
    
    # File Operations
    FILE_LIST = "fileList"
    FILE_UPLOAD = "fileUpload"
    FILE_DOWNLOAD = "fileDownload"
    FILE_RESPONSE = "fileResponse"
    
    # RAG System
    RAG_DOCUMENTS = "ragDocuments"
    RAG_SEARCH = "ragSearch"
    RAG_ADD_DOCUMENT = "ragAddDocument"
    RAG_DELETE_DOCUMENT = "ragDeleteDocument"
    RAG_RESPONSE = "ragResponse"
    
    # Status and Health
    STATUS = "status"
    ERROR = "error"
    NOTIFICATION = "notification"
    
    # Remote Control
    SCREENSHOT = "screenshot"
    SCREENSHOT_RESPONSE = "screenshot_response"
    KEYBOARD_INPUT = "keyboard_input"
    MOUSE_INPUT = "mouse_input"

class MessageStatus(Enum):
    """Message status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"

@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    type: MessageType
    data: Dict[str, Any]
    timestamp: float
    message_id: str
    client_id: Optional[str] = None
    status: MessageStatus = MessageStatus.PENDING
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "client_id": self.client_id,
            "status": self.status.value,
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        """Create from dictionary"""
        return cls(
            type=MessageType(data["type"]),
            data=data["data"],
            timestamp=data["timestamp"],
            message_id=data.get("message_id") or data.get("messageId", ""),
            client_id=data.get("client_id") or data.get("clientId"),
            status=MessageStatus(data.get("status", "pending")),
            correlation_id=data.get("correlation_id") or data.get("correlationId"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3)
        )
    
    @classmethod
    def create_request(cls, message_type: MessageType, data: Dict[str, Any], 
                      client_id: Optional[str] = None) -> 'WebSocketMessage':
        """Create a request message"""
        return cls(
            type=message_type,
            data=data,
            timestamp=time.time(),
            message_id=str(uuid.uuid4()),
            client_id=client_id,
            status=MessageStatus.PENDING
        )
    
    @classmethod
    def create_response(cls, request: 'WebSocketMessage', data: Dict[str, Any], 
                       success: bool = True, error_message: Optional[str] = None) -> 'WebSocketMessage':
        """Create a response message"""
        response_data = data.copy()
        if not success and error_message:
            response_data["error"] = error_message
        
        return cls(
            type=cls._get_response_type(request.type),
            data=response_data,
            timestamp=time.time(),
            message_id=str(uuid.uuid4()),
            client_id=request.client_id,
            status=MessageStatus.SUCCESS if success else MessageStatus.ERROR,
            correlation_id=request.message_id
        )
    
    @staticmethod
    def _get_response_type(request_type: MessageType) -> MessageType:
        """Get response type for request type"""
        response_map = {
            MessageType.AUTH_REQUEST: MessageType.AUTH_RESPONSE,
            MessageType.VOICE_COMMAND: MessageType.VOICE_RESPONSE,
            MessageType.COMMAND: MessageType.COMMAND_RESPONSE,
            MessageType.INTELLIGENT_COMMAND: MessageType.INTELLIGENT_COMMAND_RESPONSE,
            MessageType.QUICK_COMMAND: MessageType.QUICK_COMMAND_RESPONSE,
            MessageType.CAPABILITY_REQUEST: MessageType.CAPABILITY_RESPONSE,
            MessageType.AI_REQUEST: MessageType.AI_RESPONSE,
            MessageType.SYSTEM_CONTROL: MessageType.SYSTEM_RESPONSE,
            MessageType.FILE_LIST: MessageType.FILE_RESPONSE,
            MessageType.FILE_UPLOAD: MessageType.FILE_RESPONSE,
            MessageType.FILE_DOWNLOAD: MessageType.FILE_RESPONSE,
            MessageType.RAG_DOCUMENTS: MessageType.RAG_RESPONSE,
            MessageType.RAG_SEARCH: MessageType.RAG_RESPONSE,
            MessageType.RAG_ADD_DOCUMENT: MessageType.RAG_RESPONSE,
            MessageType.RAG_DELETE_DOCUMENT: MessageType.RAG_RESPONSE,
            MessageType.SCREENSHOT: MessageType.SCREENSHOT_RESPONSE,
            MessageType.PING: MessageType.PONG,
        }
        return response_map.get(request_type, MessageType.ERROR)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WebSocketMessage':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def is_request(self) -> bool:
        """Check if message is a request"""
        return self.type in [
            MessageType.AUTH_REQUEST,
            MessageType.VOICE_COMMAND,
            MessageType.COMMAND,
            MessageType.INTELLIGENT_COMMAND,
            MessageType.QUICK_COMMAND,
            MessageType.CAPABILITY_REQUEST,
            MessageType.AI_REQUEST,
            MessageType.SYSTEM_CONTROL,
            MessageType.FILE_LIST,
            MessageType.FILE_UPLOAD,
            MessageType.FILE_DOWNLOAD,
            MessageType.RAG_DOCUMENTS,
            MessageType.RAG_SEARCH,
            MessageType.RAG_ADD_DOCUMENT,
            MessageType.RAG_DELETE_DOCUMENT,
            MessageType.SCREENSHOT,
            MessageType.PING
        ]
    
    def is_response(self) -> bool:
        """Check if message is a response"""
        return self.type in [
            MessageType.AUTH_RESPONSE,
            MessageType.VOICE_RESPONSE,
            MessageType.COMMAND_RESPONSE,
            MessageType.INTELLIGENT_COMMAND_RESPONSE,
            MessageType.INTELLIGENT_COMMAND_PROGRESS,
            MessageType.INTELLIGENT_COMMAND_STEP,
            MessageType.QUICK_COMMAND_RESPONSE,
            MessageType.CAPABILITY_RESPONSE,
            MessageType.CAPABILITY_UPDATE,
            MessageType.AI_RESPONSE,
            MessageType.SYSTEM_RESPONSE,
            MessageType.FILE_RESPONSE,
            MessageType.RAG_RESPONSE,
            MessageType.SCREENSHOT_RESPONSE,
            MessageType.PONG,
            MessageType.ERROR
        ]
    
    def should_retry(self) -> bool:
        """Check if message should be retried"""
        return (self.status == MessageStatus.ERROR and 
                self.retry_count < self.max_retries)
    
    def increment_retry(self) -> 'WebSocketMessage':
        """Increment retry count"""
        self.retry_count += 1
        return self

# Message Builder for common message types
class MessageBuilder:
    """Builder for common WebSocket messages"""
    
    @staticmethod
    def create_voice_command(command: str, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create voice command message"""
        return WebSocketMessage.create_request(
            MessageType.VOICE_COMMAND,
            {"command": command},
            client_id
        )
    
    @staticmethod
    def create_ai_request(prompt: str, model: Optional[str] = None, 
                         client_id: Optional[str] = None) -> WebSocketMessage:
        """Create AI request message"""
        data = {"prompt": prompt}
        if model:
            data["model"] = model
        return WebSocketMessage.create_request(
            MessageType.AI_REQUEST,
            data,
            client_id
        )
    
    @staticmethod
    def create_ping(client_id: Optional[str] = None) -> WebSocketMessage:
        """Create ping message"""
        return WebSocketMessage.create_request(
            MessageType.PING,
            {"timestamp": time.time()},
            client_id
        )
    
    @staticmethod
    def create_auth_request(token: str, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create authentication request"""
        return WebSocketMessage.create_request(
            MessageType.AUTH_REQUEST,
            {"token": token},
            client_id
        )
    
    @staticmethod
    def create_system_info_request(client_id: Optional[str] = None) -> WebSocketMessage:
        """Create system info request"""
        return WebSocketMessage.create_request(
            MessageType.SYSTEM_INFO,
            {},
            client_id
        )
    
    @staticmethod
    def create_error_response(message: str, client_id: str = None, message_id: str = None) -> WebSocketMessage:
        """Create error response"""
        return WebSocketMessage(
            message_type=MessageType.ERROR,
            data={"error": message},
            client_id=client_id,
            message_id=message_id,
            success=False,
            error_message=message
        )
    
    @staticmethod
    def create_success_response(request: WebSocketMessage, data: Dict[str, Any]) -> WebSocketMessage:
        """Create success response"""
        return WebSocketMessage.create_response(
            request,
            data,
            success=True
        )
    
    @staticmethod
    def create_notification(message: str, notification_type: str = "info", client_id: Optional[str] = None) -> WebSocketMessage:
        """Create notification message"""
        return WebSocketMessage.create_request(
            MessageType.NOTIFICATION,
            {
                "message": message,
                "type": notification_type
            },
            client_id
        )
    
    @staticmethod
    def create_voice_response(command: str, response: str, success: bool = True, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create voice response message"""
        return WebSocketMessage.create_request(
            MessageType.VOICE_RESPONSE,
            {
                "command": command,
                "response": response,
                "success": success
            },
            client_id
        )
    
    @staticmethod
    def create_pong(timestamp: float, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create pong message"""
        return WebSocketMessage.create_request(
            MessageType.PONG,
            {"timestamp": timestamp},
            client_id
        )
    
    @staticmethod
    def create_status(server_time: float, connected_clients: int, uptime: float, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create status message"""
        return WebSocketMessage.create_request(
            MessageType.STATUS,
            {
                "server_time": server_time,
                "connected_clients": connected_clients,
                "uptime": uptime
            },
            client_id
        )
    
    @staticmethod
    def create_intelligent_command(command: str, context: Optional[Dict[str, Any]] = None, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create intelligent command message"""
        data = {"command": command}
        if context:
            data["context"] = context
        return WebSocketMessage.create_request(
            MessageType.INTELLIGENT_COMMAND,
            data,
            client_id
        )
    
    @staticmethod
    def create_quick_command(command: str, language: Optional[str] = None, confidence: Optional[float] = None, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create quick command message"""
        data = {"command": command}
        if language:
            data["language"] = language
        if confidence:
            data["confidence"] = confidence
        return WebSocketMessage.create_request(
            MessageType.QUICK_COMMAND,
            data,
            client_id
        )
    
    @staticmethod
    def create_capability_request(client_id: Optional[str] = None) -> WebSocketMessage:
        """Create capability request message"""
        return WebSocketMessage.create_request(
            MessageType.CAPABILITY_REQUEST,
            {},
            client_id
        )
    
    @staticmethod
    def create_intelligent_command_response(command: str, response: str, success: bool = True, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create intelligent command response message"""
        return WebSocketMessage.create_request(
            MessageType.INTELLIGENT_COMMAND_RESPONSE,
            {
                "command": command,
                "response": response,
                "success": success
            },
            client_id
        )
    
    @staticmethod
    def create_intelligent_command_progress(progress: int, status: str, current_step: str, steps: Optional[List[Dict[str, Any]]] = None, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create intelligent command progress message"""
        data = {
            "progress": progress,
            "status": status,
            "currentStep": current_step
        }
        if steps:
            data["steps"] = steps
        return WebSocketMessage.create_request(
            MessageType.INTELLIGENT_COMMAND_PROGRESS,
            data,
            client_id
        )
    
    @staticmethod
    def create_intelligent_command_step(step_name: str, step_status: str, step_progress: int, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create intelligent command step message"""
        return WebSocketMessage.create_request(
            MessageType.INTELLIGENT_COMMAND_STEP,
            {
                "stepName": step_name,
                "stepStatus": step_status,
                "stepProgress": step_progress
            },
            client_id
        )
    
    @staticmethod
    def create_quick_command_response(command: str, response: str, success: bool = True, client_id: Optional[str] = None) -> WebSocketMessage:
        """Create quick command response message"""
        return WebSocketMessage.create_request(
            MessageType.QUICK_COMMAND_RESPONSE,
            {
                "command": command,
                "response": response,
                "success": success
            },
            client_id
        )
    
    @staticmethod
    def create_capability_response(capabilities: List[Dict[str, Any]], client_id: Optional[str] = None) -> WebSocketMessage:
        """Create capability response message"""
        return WebSocketMessage.create_request(
            MessageType.CAPABILITY_RESPONSE,
            {"capabilities": capabilities},
            client_id
        )
