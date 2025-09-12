"""
WebSocket Command Handler
Handles command processing through WebSocket connections
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import asdict
import time

from .nlp_engine import NLPEngine, ProcessedCommand
from .command_executor import CommandExecutor, CommandResult
from ..remote_control.websocket_server import WebSocketServer
from shared.websocket_protocol import MessageType, MessageStatus, WebSocketMessage

logger = logging.getLogger(__name__)


class WebSocketCommandHandler:
    """Handles command processing through WebSocket connections"""
    
    def __init__(self, websocket_server: WebSocketServer):
        self.websocket_server = websocket_server
        self.logger = logging.getLogger(__name__)
        self.nlp_engine = NLPEngine()
        self.command_executor = CommandExecutor()
        self._is_initialized = False
        self._command_history: List[Dict[str, Any]] = []
        self._max_history = 100
    
    async def initialize(self) -> bool:
        """Initialize the command handler"""
        try:
            # Initialize command executor
            if not self.command_executor.initialize():
                self.logger.error("Failed to initialize command executor")
                return False
            
            # Register WebSocket message handlers
            self.websocket_server.register_handler(MessageType.VOICE_COMMAND, self._handle_voice_command)
            self.websocket_server.register_handler(MessageType.AI_REQUEST, self._handle_ai_request)
            self.websocket_server.register_handler(MessageType.SYSTEM_CONTROL, self._handle_system_control)
            
            self._is_initialized = True
            self.logger.info("WebSocket command handler initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket command handler: {e}")
            return False
    
    async def _handle_voice_command(self, message: WebSocketMessage) -> None:
        """Handle voice command messages"""
        try:
            client_id = message.client_id
            self.logger.info(f"Processing voice command from client {client_id}: {message.data.get('command', '')}")
            
            # Extract command text
            command_text = message.data.get('command', '')
            if not command_text:
                await self._send_error_response(client_id, "No command provided", message.message_id)
                return
            
            # Process command through NLP engine
            processed_command = self.nlp_engine.process_command(command_text)
            
            # Execute command
            result = await self.command_executor.execute_command(processed_command)
            
            # Add to history
            self._add_to_history({
                "client_id": client_id,
                "command": command_text,
                "processed_command": processed_command,
                "result": result,
                "timestamp": time.time()
            })
            
            # Send response
            await self._send_command_response(client_id, result, message.message_id)
            
        except Exception as e:
            self.logger.error(f"Error handling voice command: {e}")
            await self._send_error_response(client_id, f"Error processing command: {e}", message.message_id)
    
    async def _handle_ai_request(self, message: WebSocketMessage) -> None:
        """Handle AI request messages"""
        try:
            client_id = message.client_id
            self.logger.info(f"Processing AI request from client {client_id}")
            
            # Extract request data
            query = message.data.get('query', '')
            if not query:
                await self._send_error_response(client_id, "No query provided", message.message_id)
                return
            
            # Process as command if it looks like one
            if self._is_likely_command(query):
                processed_command = self.nlp_engine.process_command(query)
                result = await self.command_executor.execute_command(processed_command)
                
                # Add to history
                self._add_to_history({
                    "client_id": client_id,
                    "command": query,
                    "processed_command": processed_command,
                    "result": result,
                    "timestamp": time.time(),
                    "type": "ai_request"
                })
                
                await self._send_command_response(client_id, result, message.message_id)
            else:
                # Handle as regular AI query
                await self._handle_regular_ai_query(client_id, query, message.message_id)
            
        except Exception as e:
            self.logger.error(f"Error handling AI request: {e}")
            await self._send_error_response(client_id, f"Error processing AI request: {e}", message.message_id)
    
    async def _handle_system_control(self, message: WebSocketMessage) -> None:
        """Handle system control messages"""
        try:
            client_id = message.client_id
            self.logger.info(f"Processing system control from client {client_id}")
            
            # Extract control data
            control_type = message.data.get('type', '')
            parameters = message.data.get('parameters', {})
            
            if not control_type:
                await self._send_error_response(client_id, "No control type provided", message.message_id)
                return
            
            # Create processed command
            processed_command = ProcessedCommand(
                original_text=f"System control: {control_type}",
                category=self._get_category_for_control_type(control_type),
                intent=self._get_intent_for_control_type(control_type),
                action=control_type,
                parameters=parameters,
                confidence=1.0
            )
            
            # Execute command
            result = await self.command_executor.execute_command(processed_command)
            
            # Add to history
            self._add_to_history({
                "client_id": client_id,
                "command": f"System control: {control_type}",
                "processed_command": processed_command,
                "result": result,
                "timestamp": time.time(),
                "type": "system_control"
            })
            
            # Send response
            await self._send_command_response(client_id, result, message.message_id)
            
        except Exception as e:
            self.logger.error(f"Error handling system control: {e}")
            await self._send_error_response(client_id, f"Error processing system control: {e}", message.message_id)
    
    async def _handle_regular_ai_query(self, client_id: str, query: str, message_id: str) -> None:
        """Handle regular AI query (not a command)"""
        try:
            # This would integrate with your existing AI system
            # For now, we'll send a simple response
            
            response_data = {
                "response": f"AI Query received: {query}",
                "type": "ai_response",
                "timestamp": time.time()
            }
            
            response_message = WebSocketMessage(
                message_id=message_id,
                type=MessageType.AI_RESPONSE,
                status=MessageStatus.SUCCESS,
                data=response_data,
                timestamp=time.time()
            )
            
            await self.websocket_server._send_message(client_id, response_message)
            
        except Exception as e:
            self.logger.error(f"Error handling regular AI query: {e}")
            await self._send_error_response(client_id, f"Error processing AI query: {e}", message_id)
    
    def _is_likely_command(self, text: str) -> bool:
        """Check if text is likely a command"""
        command_indicators = [
            'yaz', 'type', 'write', 'aç', 'open', 'kapat', 'close',
            'ara', 'search', 'çal', 'play', 'dur', 'pause',
            'yeni', 'new', 'sil', 'delete', 'kopyala', 'copy'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in command_indicators)
    
    def _get_category_for_control_type(self, control_type: str):
        """Get command category for control type"""
        from .command_classifier import CommandCategory
        
        category_mapping = {
            'typing': CommandCategory.TYPING,
            'application': CommandCategory.APPLICATION,
            'browser': CommandCategory.BROWSER,
            'system': CommandCategory.SYSTEM,
            'media': CommandCategory.MEDIA,
            'file': CommandCategory.FILE
        }
        
        return category_mapping.get(control_type, CommandCategory.UNKNOWN)
    
    def _get_intent_for_control_type(self, control_type: str):
        """Get intent for control type"""
        from .nlp_engine import IntentType
        return IntentType.EXECUTE  # Most system controls are execute intents
    
    async def _send_command_response(self, client_id: str, result: CommandResult, message_id: str) -> None:
        """Send command execution response"""
        try:
            response_data = {
                "success": result.success,
                "message": result.message,
                "data": result.data or {},
                "execution_time": result.execution_time,
                "status": result.status.value,
                "timestamp": time.time()
            }
            
            if result.error:
                response_data["error"] = result.error
            
            response_message = WebSocketMessage(
                message_id=message_id,
                type=MessageType.VOICE_RESPONSE,
                status=MessageStatus.SUCCESS if result.success else MessageStatus.ERROR,
                data=response_data,
                timestamp=time.time()
            )
            
            await self.websocket_server._send_message(client_id, response_message)
            
        except Exception as e:
            self.logger.error(f"Error sending command response: {e}")
            await self._send_error_response(client_id, f"Error sending response: {e}", message_id)
    
    async def _send_error_response(self, client_id: str, error_message: str, message_id: str) -> None:
        """Send error response"""
        try:
            error_data = {
                "error": error_message,
                "timestamp": time.time()
            }
            
            error_message_obj = WebSocketMessage(
                message_id=message_id,
                type=MessageType.ERROR,
                status=MessageStatus.ERROR,
                data=error_data,
                timestamp=time.time()
            )
            
            await self.websocket_server._send_message(client_id, error_message_obj)
            
        except Exception as e:
            self.logger.error(f"Error sending error response: {e}")
    
    def _add_to_history(self, entry: Dict[str, Any]) -> None:
        """Add entry to command history"""
        self._command_history.append(entry)
        if len(self._command_history) > self._max_history:
            self._command_history.pop(0)
    
    def get_command_history(self, client_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get command history"""
        history = self._command_history
        
        if client_id:
            history = [entry for entry in history if entry.get('client_id') == client_id]
        
        return history[-limit:] if history else []
    
    async def process_command(self, message: WebSocketMessage) -> str:
        """Process incoming command message"""
        try:
            command_text = message.data.get("command", "")
            if not command_text:
                return "No command provided"
            
            # Process command through NLP engine
            processed_command = self.nlp_engine.process_command(command_text)
            
            # Execute command through command executor
            result = await self.command_executor.execute_command(processed_command)
            
            if result.success:
                return result.message or f"Command '{command_text}' executed successfully"
            else:
                return f"Command failed: {result.message or 'Unknown error'}"
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"Error processing command: {str(e)}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "initialized": self._is_initialized,
            "command_executor_status": self.command_executor.get_executor_status(),
            "total_commands_processed": len(self._command_history),
            "active_clients": len(self.websocket_server.clients)
        }
    
    async def cleanup(self) -> None:
        """Cleanup command handler"""
        try:
            if self.command_executor:
                self.command_executor.cleanup()
            
            self._command_history.clear()
            self._is_initialized = False
            self.logger.info("WebSocket command handler cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
