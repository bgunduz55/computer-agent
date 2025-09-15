"""
Terminal Session Management Capabilities for JARVIS Computer Assistant

Provides capabilities for persistent terminal session management with history
and context preservation.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from ..terminal_session_manager import TerminalSessionManager, SessionType, SessionStatus, get_terminal_session_manager

logger = logging.getLogger(__name__)

class TerminalSessionExecutor:
    """Terminal session management capabilities executor"""
    
    def __init__(self):
        self.session_manager = get_terminal_session_manager()
        self._is_initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize terminal session executor"""
        try:
            if not self.session_manager._is_initialized:
                success = await self.session_manager.initialize()
                if not success:
                    return False
            
            self._is_initialized = True
            self.logger.info("Terminal session executor initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize terminal session executor: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # Don't stop the global session manager here
            # as it might be used by other components
            self._is_initialized = False
            self.logger.info("Terminal session executor cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup terminal session executor: {e}")
    
    def _can_handle(self, parameters: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("terminal_session" in parameters or
                "create_session" in parameters or
                "session_management" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute terminal session capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Terminal session executor not initialized"}
            
            operation = parameters.get("operation")
            if not operation:
                return {"success": False, "error": "Operation not specified"}
            
            if operation == "create_session":
                return await self._create_session(parameters)
            elif operation == "activate_session":
                return await self._activate_session(parameters)
            elif operation == "suspend_session":
                return await self._suspend_session(parameters)
            elif operation == "terminate_session":
                return await self._terminate_session(parameters)
            elif operation == "execute_command":
                return await self._execute_command(parameters)
            elif operation == "get_session_info":
                return await self._get_session_info(parameters)
            elif operation == "list_sessions":
                return await self._list_sessions(parameters)
            elif operation == "update_context":
                return await self._update_context(parameters)
            elif operation == "get_history":
                return await self._get_history(parameters)
            elif operation == "search_history":
                return await self._search_history(parameters)
            elif operation == "create_group":
                return await self._create_group(parameters)
            elif operation == "execute_in_group":
                return await self._execute_in_group(parameters)
            elif operation == "get_stats":
                return await self._get_stats(parameters)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        
        except Exception as e:
            self.logger.error(f"Failed to execute terminal session capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new terminal session"""
        try:
            name = parameters.get("name")
            session_type_str = parameters.get("session_type", "interactive")
            terminal_type_str = parameters.get("terminal_type")
            working_directory = parameters.get("working_directory")
            description = parameters.get("description", "")
            tags = set(parameters.get("tags", []))
            parent_session_id = parameters.get("parent_session_id")
            
            if not name:
                return {"success": False, "error": "Session name is required"}
            
            # Convert session type
            try:
                session_type = SessionType(session_type_str)
            except ValueError:
                return {"success": False, "error": f"Invalid session type: {session_type_str}"}
            
            # Convert terminal type if provided
            terminal_type = None
            if terminal_type_str:
                try:
                    from ..terminal_integration.terminal_manager import TerminalType
                    terminal_type = TerminalType(terminal_type_str)
                except ValueError:
                    return {"success": False, "error": f"Invalid terminal type: {terminal_type_str}"}
            
            session_id = await self.session_manager.create_session(
                name=name,
                session_type=session_type,
                terminal_type=terminal_type,
                working_directory=working_directory,
                description=description,
                tags=tags,
                parent_session_id=parent_session_id
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "message": f"Session '{name}' created successfully"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _activate_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a terminal session"""
        try:
            session_id = parameters.get("session_id")
            if not session_id:
                return {"success": False, "error": "Session ID is required"}
            
            success = await self.session_manager.activate_session(session_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Session {session_id} activated"
                }
            else:
                return {"success": False, "error": "Failed to activate session"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _suspend_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Suspend a terminal session"""
        try:
            session_id = parameters.get("session_id")
            if not session_id:
                return {"success": False, "error": "Session ID is required"}
            
            success = await self.session_manager.suspend_session(session_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Session {session_id} suspended"
                }
            else:
                return {"success": False, "error": "Failed to suspend session"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _terminate_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate a terminal session"""
        try:
            session_id = parameters.get("session_id")
            if not session_id:
                return {"success": False, "error": "Session ID is required"}
            
            success = await self.session_manager.terminate_session(session_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Session {session_id} terminated"
                }
            else:
                return {"success": False, "error": "Failed to terminate session"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command in a terminal session"""
        try:
            session_id = parameters.get("session_id")
            command = parameters.get("command")
            timeout = parameters.get("timeout", 30)
            
            if not session_id or not command:
                return {"success": False, "error": "Session ID and command are required"}
            
            result = await self.session_manager.execute_command(session_id, command, timeout)
            
            return {
                "success": True,
                "result": {
                    "command": result.command,
                    "output": result.output,
                    "error": result.error,
                    "exit_code": result.exit_code,
                    "execution_time": result.execution_time,
                    "success": result.success
                }
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_session_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get session information"""
        try:
            session_id = parameters.get("session_id")
            if not session_id:
                return {"success": False, "error": "Session ID is required"}
            
            info = await self.session_manager.get_session_info(session_id)
            
            if info:
                return {
                    "success": True,
                    "session_info": info
                }
            else:
                return {"success": False, "error": "Session not found"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_sessions(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List terminal sessions"""
        try:
            status_filter_str = parameters.get("status_filter")
            session_type_filter_str = parameters.get("session_type_filter")
            tag_filter = parameters.get("tag_filter")
            
            # Convert filters
            status_filter = None
            if status_filter_str:
                try:
                    status_filter = SessionStatus(status_filter_str)
                except ValueError:
                    return {"success": False, "error": f"Invalid status filter: {status_filter_str}"}
            
            session_type_filter = None
            if session_type_filter_str:
                try:
                    session_type_filter = SessionType(session_type_filter_str)
                except ValueError:
                    return {"success": False, "error": f"Invalid session type filter: {session_type_filter_str}"}
            
            sessions = await self.session_manager.list_sessions(
                status_filter=status_filter,
                session_type_filter=session_type_filter,
                tag_filter=tag_filter
            )
            
            return {
                "success": True,
                "sessions": sessions,
                "total_sessions": len(sessions)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _update_context(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update session context"""
        try:
            session_id = parameters.get("session_id")
            context_updates = parameters.get("context_updates", {})
            
            if not session_id:
                return {"success": False, "error": "Session ID is required"}
            
            success = await self.session_manager.update_session_context(session_id, context_updates)
            
            if success:
                return {
                    "success": True,
                    "message": f"Context updated for session {session_id}"
                }
            else:
                return {"success": False, "error": "Failed to update context"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_history(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get session command history"""
        try:
            session_id = parameters.get("session_id")
            limit = parameters.get("limit", 100)
            
            if not session_id:
                return {"success": False, "error": "Session ID is required"}
            
            history = await self.session_manager.get_session_history(session_id, limit)
            
            return {
                "success": True,
                "history": history,
                "total_commands": len(history)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _search_history(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search session command history"""
        try:
            session_id = parameters.get("session_id")
            query = parameters.get("query")
            limit = parameters.get("limit", 50)
            
            if not session_id or not query:
                return {"success": False, "error": "Session ID and query are required"}
            
            results = await self.session_manager.search_history(session_id, query, limit)
            
            return {
                "success": True,
                "results": results,
                "total_matches": len(results)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_group(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a session group"""
        try:
            group_name = parameters.get("group_name")
            session_ids = parameters.get("session_ids", [])
            
            if not group_name:
                return {"success": False, "error": "Group name is required"}
            
            success = await self.session_manager.create_session_group(group_name, session_ids)
            
            if success:
                return {
                    "success": True,
                    "message": f"Session group '{group_name}' created with {len(session_ids)} sessions"
                }
            else:
                return {"success": False, "error": "Failed to create session group"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_in_group(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command in a session group"""
        try:
            group_name = parameters.get("group_name")
            command = parameters.get("command")
            timeout = parameters.get("timeout", 30)
            
            if not group_name or not command:
                return {"success": False, "error": "Group name and command are required"}
            
            results = await self.session_manager.execute_in_group(group_name, command, timeout)
            
            return {
                "success": True,
                "results": {
                    session_id: {
                        "command": result.command,
                        "output": result.output,
                        "error": result.error,
                        "exit_code": result.exit_code,
                        "execution_time": result.execution_time,
                        "success": result.success
                    }
                    for session_id, result in results.items()
                },
                "total_sessions": len(results)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_stats(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get session manager statistics"""
        try:
            stats = self.session_manager.get_stats()
            
            return {
                "success": True,
                "stats": stats
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
