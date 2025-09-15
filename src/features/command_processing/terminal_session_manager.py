"""
Terminal Session Management for JARVIS Computer Assistant

Provides persistent terminal sessions with history, context preservation,
and advanced session management capabilities.
"""

import asyncio
import json
import logging
import os
import pickle
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from pathlib import Path

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from ..terminal_integration.terminal_manager import TerminalManager, TerminalType, CommandResult, TerminalSession

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Terminal session status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ERROR = "error"

class SessionType(Enum):
    """Types of terminal sessions"""
    INTERACTIVE = "interactive"
    BATCH = "batch"
    SCRIPT = "script"
    MONITORING = "monitoring"
    DEBUG = "debug"

@dataclass
class SessionContext:
    """Context information for a terminal session"""
    working_directory: str
    environment_variables: Dict[str, str]
    aliases: Dict[str, str]
    history: List[str]
    bookmarks: Dict[str, str]
    custom_prompts: Dict[str, str]
    session_variables: Dict[str, Any] = field(default_factory=dict)
    last_command: Optional[str] = None
    command_count: int = 0
    error_count: int = 0
    success_count: int = 0

@dataclass
class SessionHistory:
    """Command history for a session"""
    command_id: str
    command: str
    timestamp: float
    working_directory: str
    exit_code: int
    execution_time: float
    output: str
    error: str
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PersistentSession:
    """Persistent terminal session with full context"""
    session_id: str
    name: str
    session_type: SessionType
    terminal_type: TerminalType
    status: SessionStatus
    created_at: float
    last_activity: float
    context: SessionContext
    history: List[SessionHistory]
    tags: Set[str] = field(default_factory=set)
    description: str = ""
    auto_save: bool = True
    max_history_size: int = 1000
    session_data: Dict[str, Any] = field(default_factory=dict)
    parent_session_id: Optional[str] = None
    child_sessions: List[str] = field(default_factory=list)

class TerminalSessionManager:
    """Advanced terminal session management system"""
    
    def __init__(self, data_directory: str = "data/sessions"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        self.sessions: Dict[str, PersistentSession] = {}
        self.active_sessions: Set[str] = set()
        self.session_groups: Dict[str, Set[str]] = {}
        self.terminal_manager = TerminalManager()
        
        self._is_initialized = False
        self.logger = logging.getLogger(__name__)
        
        # Session event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            "session_created": [],
            "session_activated": [],
            "session_suspended": [],
            "session_terminated": [],
            "command_executed": [],
            "context_updated": []
        }
        
        # Auto-save settings
        self.auto_save_interval = 30  # seconds
        self.max_sessions = 100
        self.session_timeout = 3600  # 1 hour
        
        # Statistics
        self.stats = {
            "total_sessions_created": 0,
            "active_sessions": 0,
            "total_commands_executed": 0,
            "sessions_auto_saved": 0
        }
    
    async def initialize(self) -> bool:
        """Initialize terminal session manager"""
        try:
            # Initialize terminal manager
            if not self.terminal_manager.initialize():
                return False
            
            # Load existing sessions
            await self._load_sessions()
            
            # Start background tasks
            asyncio.create_task(self._auto_save_worker())
            asyncio.create_task(self._session_cleanup_worker())
            asyncio.create_task(self._stats_reporter())
            
            self._is_initialized = True
            self.logger.info("Terminal session manager initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize terminal session manager: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup terminal session manager"""
        try:
            # Save all sessions
            await self._save_all_sessions()
            
            # Cleanup terminal manager
            self.terminal_manager.cleanup()
            
            self._is_initialized = False
            self.logger.info("Terminal session manager cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup terminal session manager: {e}")
    
    async def create_session(self, name: str, session_type: SessionType = SessionType.INTERACTIVE,
                           terminal_type: TerminalType = None, working_directory: str = None,
                           description: str = "", tags: Set[str] = None,
                           parent_session_id: str = None) -> str:
        """Create a new persistent terminal session"""
        try:
            session_id = str(uuid.uuid4())
            
            if terminal_type is None:
                terminal_type = self.terminal_manager.terminal_configs["default"]
            
            if working_directory is None:
                working_directory = os.getcwd()
            
            # Create session context
            context = SessionContext(
                working_directory=working_directory,
                environment_variables=os.environ.copy(),
                aliases={},
                history=[],
                bookmarks={},
                custom_prompts={}
            )
            
            # Create persistent session
            session = PersistentSession(
                session_id=session_id,
                name=name,
                session_type=session_type,
                terminal_type=terminal_type,
                status=SessionStatus.ACTIVE,
                created_at=time.time(),
                last_activity=time.time(),
                context=context,
                history=[],
                tags=tags or set(),
                description=description,
                parent_session_id=parent_session_id
            )
            
            # Create underlying terminal session
            terminal_session_id = self.terminal_manager.create_session(
                terminal_type=terminal_type,
                working_directory=working_directory
            )
            
            session.session_data["terminal_session_id"] = terminal_session_id
            
            # Store session
            self.sessions[session_id] = session
            self.active_sessions.add(session_id)
            
            # Update parent session if specified
            if parent_session_id and parent_session_id in self.sessions:
                self.sessions[parent_session_id].child_sessions.append(session_id)
            
            # Update stats
            self.stats["total_sessions_created"] += 1
            self.stats["active_sessions"] = len(self.active_sessions)
            
            # Emit event
            await self._emit_event("session_created", session)
            
            self.logger.info(f"Created terminal session: {session_id} ({name})")
            return session_id
        
        except Exception as e:
            self.logger.error(f"Failed to create terminal session: {e}")
            raise
    
    async def activate_session(self, session_id: str) -> bool:
        """Activate a terminal session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session.status = SessionStatus.ACTIVE
            session.last_activity = time.time()
            
            self.active_sessions.add(session_id)
            self.stats["active_sessions"] = len(self.active_sessions)
            
            # Emit event
            await self._emit_event("session_activated", session)
            
            self.logger.info(f"Activated terminal session: {session_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to activate session {session_id}: {e}")
            return False
    
    async def suspend_session(self, session_id: str) -> bool:
        """Suspend a terminal session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session.status = SessionStatus.SUSPENDED
            session.last_activity = time.time()
            
            self.active_sessions.discard(session_id)
            self.stats["active_sessions"] = len(self.active_sessions)
            
            # Save session
            await self._save_session(session_id)
            
            # Emit event
            await self._emit_event("session_suspended", session)
            
            self.logger.info(f"Suspended terminal session: {session_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to suspend session {session_id}: {e}")
            return False
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate a terminal session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            session.status = SessionStatus.TERMINATED
            session.last_activity = time.time()
            
            # Close underlying terminal session
            terminal_session_id = session.session_data.get("terminal_session_id")
            if terminal_session_id:
                self.terminal_manager.close_session(terminal_session_id)
            
            # Terminate child sessions
            for child_id in session.child_sessions:
                await self.terminate_session(child_id)
            
            self.active_sessions.discard(session_id)
            self.stats["active_sessions"] = len(self.active_sessions)
            
            # Save session before removing
            await self._save_session(session_id)
            
            # Emit event
            await self._emit_event("session_terminated", session)
            
            # Remove from active sessions but keep in memory for history
            self.logger.info(f"Terminated terminal session: {session_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to terminate session {session_id}: {e}")
            return False
    
    async def execute_command(self, session_id: str, command: str, 
                            timeout: int = 30) -> CommandResult:
        """Execute command in a terminal session"""
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            if session.status != SessionStatus.ACTIVE:
                raise ValueError(f"Session {session_id} is not active")
            
            # Get terminal session ID
            terminal_session_id = session.session_data.get("terminal_session_id")
            if not terminal_session_id:
                raise ValueError(f"No terminal session for {session_id}")
            
            # Execute command
            result = await self.terminal_manager.execute_command(
                command=command,
                terminal_type=session.terminal_type,
                working_directory=session.context.working_directory,
                timeout=timeout
            )
            
            # Update session context
            session.context.last_command = command
            session.context.command_count += 1
            session.context.history.append(command)
            
            if result.success:
                session.context.success_count += 1
            else:
                session.context.error_count += 1
            
            # Create history entry
            history_entry = SessionHistory(
                command_id=str(uuid.uuid4()),
                command=command,
                timestamp=time.time(),
                working_directory=session.context.working_directory,
                exit_code=result.exit_code,
                execution_time=result.execution_time,
                output=result.output,
                error=result.error,
                success=result.success,
                metadata=result.metadata
            )
            
            session.history.append(history_entry)
            session.last_activity = time.time()
            
            # Trim history if too long
            if len(session.history) > session.max_history_size:
                session.history = session.history[-session.max_history_size:]
            
            # Update stats
            self.stats["total_commands_executed"] += 1
            
            # Emit event
            await self._emit_event("command_executed", session, history_entry)
            
            # Auto-save if enabled
            if session.auto_save:
                await self._save_session(session_id)
            
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to execute command in session {session_id}: {e}")
            raise
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed session information"""
        try:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            return {
                "session_id": session.session_id,
                "name": session.name,
                "session_type": session.session_type.value,
                "terminal_type": session.terminal_type.value,
                "status": session.status.value,
                "created_at": session.created_at,
                "last_activity": session.last_activity,
                "description": session.description,
                "tags": list(session.tags),
                "context": {
                    "working_directory": session.context.working_directory,
                    "command_count": session.context.command_count,
                    "success_count": session.context.success_count,
                    "error_count": session.context.error_count,
                    "last_command": session.context.last_command,
                    "environment_variables": session.context.environment_variables,
                    "aliases": session.context.aliases,
                    "bookmarks": session.context.bookmarks
                },
                "history_count": len(session.history),
                "parent_session_id": session.parent_session_id,
                "child_sessions": session.child_sessions,
                "auto_save": session.auto_save
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get session info for {session_id}: {e}")
            return None
    
    async def list_sessions(self, status_filter: Optional[SessionStatus] = None,
                          session_type_filter: Optional[SessionType] = None,
                          tag_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List terminal sessions with optional filters"""
        try:
            sessions = []
            
            for session in self.sessions.values():
                # Apply filters
                if status_filter and session.status != status_filter:
                    continue
                
                if session_type_filter and session.session_type != session_type_filter:
                    continue
                
                if tag_filter and tag_filter not in session.tags:
                    continue
                
                sessions.append({
                    "session_id": session.session_id,
                    "name": session.name,
                    "session_type": session.session_type.value,
                    "terminal_type": session.terminal_type.value,
                    "status": session.status.value,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "description": session.description,
                    "tags": list(session.tags),
                    "command_count": session.context.command_count,
                    "history_count": len(session.history)
                })
            
            return sessions
        
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
            return []
    
    async def update_session_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        """Update session context"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            # Update context fields
            if "working_directory" in context_updates:
                session.context.working_directory = context_updates["working_directory"]
            
            if "aliases" in context_updates:
                session.context.aliases.update(context_updates["aliases"])
            
            if "bookmarks" in context_updates:
                session.context.bookmarks.update(context_updates["bookmarks"])
            
            if "custom_prompts" in context_updates:
                session.context.custom_prompts.update(context_updates["custom_prompts"])
            
            if "session_variables" in context_updates:
                session.context.session_variables.update(context_updates["session_variables"])
            
            session.last_activity = time.time()
            
            # Emit event
            await self._emit_event("context_updated", session)
            
            # Auto-save if enabled
            if session.auto_save:
                await self._save_session(session_id)
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to update session context for {session_id}: {e}")
            return False
    
    async def get_session_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get command history for a session"""
        try:
            if session_id not in self.sessions:
                return []
            
            session = self.sessions[session_id]
            history = session.history[-limit:] if limit > 0 else session.history
            
            return [
                {
                    "command_id": entry.command_id,
                    "command": entry.command,
                    "timestamp": entry.timestamp,
                    "working_directory": entry.working_directory,
                    "exit_code": entry.exit_code,
                    "execution_time": entry.execution_time,
                    "output": entry.output,
                    "error": entry.error,
                    "success": entry.success,
                    "metadata": entry.metadata
                }
                for entry in history
            ]
        
        except Exception as e:
            self.logger.error(f"Failed to get session history for {session_id}: {e}")
            return []
    
    async def search_history(self, session_id: str, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search command history"""
        try:
            if session_id not in self.sessions:
                return []
            
            session = self.sessions[session_id]
            results = []
            
            for entry in reversed(session.history):
                if query.lower() in entry.command.lower():
                    results.append({
                        "command_id": entry.command_id,
                        "command": entry.command,
                        "timestamp": entry.timestamp,
                        "working_directory": entry.working_directory,
                        "success": entry.success
                    })
                    
                    if len(results) >= limit:
                        break
            
            return results
        
        except Exception as e:
            self.logger.error(f"Failed to search history for session {session_id}: {e}")
            return []
    
    async def create_session_group(self, group_name: str, session_ids: List[str]) -> bool:
        """Create a session group"""
        try:
            self.session_groups[group_name] = set(session_ids)
            self.logger.info(f"Created session group: {group_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create session group {group_name}: {e}")
            return False
    
    async def execute_in_group(self, group_name: str, command: str, 
                             timeout: int = 30) -> Dict[str, CommandResult]:
        """Execute command in all sessions in a group"""
        try:
            if group_name not in self.session_groups:
                raise ValueError(f"Session group {group_name} not found")
            
            results = {}
            session_ids = list(self.session_groups[group_name])
            
            # Execute command in all sessions concurrently
            tasks = []
            for session_id in session_ids:
                if session_id in self.sessions:
                    task = asyncio.create_task(
                        self.execute_command(session_id, command, timeout)
                    )
                    tasks.append((session_id, task))
            
            # Wait for all tasks to complete
            for session_id, task in tasks:
                try:
                    result = await task
                    results[session_id] = result
                except Exception as e:
                    results[session_id] = CommandResult(
                        command=command,
                        output="",
                        error=str(e),
                        exit_code=-1,
                        execution_time=0,
                        command_type=None,
                        success=False
                    )
            
            return results
        
        except Exception as e:
            self.logger.error(f"Failed to execute command in group {group_name}: {e}")
            raise
    
    async def _load_sessions(self) -> None:
        """Load sessions from disk"""
        try:
            session_files = list(self.data_directory.glob("session_*.json"))
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r') as f:
                        data = json.load(f)
                    
                    # Reconstruct session from saved data
                    session = self._deserialize_session(data)
                    self.sessions[session.session_id] = session
                    
                    if session.status == SessionStatus.ACTIVE:
                        self.active_sessions.add(session.session_id)
                
                except Exception as e:
                    self.logger.warning(f"Failed to load session from {session_file}: {e}")
            
            self.logger.info(f"Loaded {len(self.sessions)} sessions from disk")
        
        except Exception as e:
            self.logger.error(f"Failed to load sessions: {e}")
    
    async def _save_session(self, session_id: str) -> None:
        """Save session to disk"""
        try:
            if session_id not in self.sessions:
                return
            
            session = self.sessions[session_id]
            session_file = self.data_directory / f"session_{session_id}.json"
            
            # Serialize session
            data = self._serialize_session(session)
            
            with open(session_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.stats["sessions_auto_saved"] += 1
        
        except Exception as e:
            self.logger.error(f"Failed to save session {session_id}: {e}")
    
    async def _save_all_sessions(self) -> None:
        """Save all sessions to disk"""
        try:
            for session_id in self.sessions:
                await self._save_session(session_id)
            
            self.logger.info("Saved all sessions to disk")
        
        except Exception as e:
            self.logger.error(f"Failed to save all sessions: {e}")
    
    def _serialize_session(self, session: PersistentSession) -> Dict[str, Any]:
        """Serialize session for storage"""
        return {
            "session_id": session.session_id,
            "name": session.name,
            "session_type": session.session_type.value,
            "terminal_type": session.terminal_type.value,
            "status": session.status.value,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "context": asdict(session.context),
            "history": [asdict(entry) for entry in session.history],
            "tags": list(session.tags),
            "description": session.description,
            "auto_save": session.auto_save,
            "max_history_size": session.max_history_size,
            "session_data": session.session_data,
            "parent_session_id": session.parent_session_id,
            "child_sessions": session.child_sessions
        }
    
    def _deserialize_session(self, data: Dict[str, Any]) -> PersistentSession:
        """Deserialize session from storage"""
        # Reconstruct enums
        session_type = SessionType(data["session_type"])
        terminal_type = TerminalType(data["terminal_type"])
        status = SessionStatus(data["status"])
        
        # Reconstruct context
        context_data = data["context"]
        context = SessionContext(
            working_directory=context_data["working_directory"],
            environment_variables=context_data["environment_variables"],
            aliases=context_data["aliases"],
            history=context_data["history"],
            bookmarks=context_data["bookmarks"],
            custom_prompts=context_data["custom_prompts"],
            session_variables=context_data.get("session_variables", {}),
            last_command=context_data.get("last_command"),
            command_count=context_data.get("command_count", 0),
            error_count=context_data.get("error_count", 0),
            success_count=context_data.get("success_count", 0)
        )
        
        # Reconstruct history
        history = []
        for entry_data in data["history"]:
            history.append(SessionHistory(
                command_id=entry_data["command_id"],
                command=entry_data["command"],
                timestamp=entry_data["timestamp"],
                working_directory=entry_data["working_directory"],
                exit_code=entry_data["exit_code"],
                execution_time=entry_data["execution_time"],
                output=entry_data["output"],
                error=entry_data["error"],
                success=entry_data["success"],
                metadata=entry_data.get("metadata", {})
            ))
        
        return PersistentSession(
            session_id=data["session_id"],
            name=data["name"],
            session_type=session_type,
            terminal_type=terminal_type,
            status=status,
            created_at=data["created_at"],
            last_activity=data["last_activity"],
            context=context,
            history=history,
            tags=set(data.get("tags", [])),
            description=data.get("description", ""),
            auto_save=data.get("auto_save", True),
            max_history_size=data.get("max_history_size", 1000),
            session_data=data.get("session_data", {}),
            parent_session_id=data.get("parent_session_id"),
            child_sessions=data.get("child_sessions", [])
        )
    
    async def _emit_event(self, event_type: str, session: PersistentSession, data: Any = None) -> None:
        """Emit session event"""
        try:
            for handler in self.event_handlers.get(event_type, []):
                try:
                    if data:
                        await handler(session, data)
                    else:
                        await handler(session)
                except Exception as e:
                    self.logger.error(f"Event handler failed for {event_type}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to emit event {event_type}: {e}")
    
    async def _auto_save_worker(self) -> None:
        """Background auto-save worker"""
        while self._is_initialized:
            try:
                await asyncio.sleep(self.auto_save_interval)
                
                # Save all active sessions
                for session_id in self.active_sessions:
                    if session_id in self.sessions:
                        session = self.sessions[session_id]
                        if session.auto_save:
                            await self._save_session(session_id)
            
            except Exception as e:
                self.logger.error(f"Error in auto-save worker: {e}")
    
    async def _session_cleanup_worker(self) -> None:
        """Background session cleanup worker"""
        while self._is_initialized:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = time.time()
                sessions_to_terminate = []
                
                # Find sessions that have been inactive too long
                for session_id, session in self.sessions.items():
                    if (session.status == SessionStatus.ACTIVE and 
                        current_time - session.last_activity > self.session_timeout):
                        sessions_to_terminate.append(session_id)
                
                # Terminate inactive sessions
                for session_id in sessions_to_terminate:
                    await self.terminate_session(session_id)
                
                # Clean up old terminated sessions if we have too many
                if len(self.sessions) > self.max_sessions:
                    # Remove oldest terminated sessions
                    terminated_sessions = [
                        (session_id, session) for session_id, session in self.sessions.items()
                        if session.status == SessionStatus.TERMINATED
                    ]
                    terminated_sessions.sort(key=lambda x: x[1].last_activity)
                    
                    sessions_to_remove = terminated_sessions[:len(self.sessions) - self.max_sessions]
                    for session_id, _ in sessions_to_remove:
                        del self.sessions[session_id]
            
            except Exception as e:
                self.logger.error(f"Error in session cleanup worker: {e}")
    
    async def _stats_reporter(self) -> None:
        """Background stats reporter"""
        while self._is_initialized:
            try:
                await asyncio.sleep(60)  # Report every minute
                self.logger.info(f"Terminal session manager stats: {self.stats}")
            except Exception as e:
                self.logger.error(f"Error in stats reporter: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session manager statistics"""
        return {
            **self.stats,
            "active_sessions": len(self.active_sessions),
            "total_sessions": len(self.sessions),
            "session_groups": len(self.session_groups),
            "is_initialized": self._is_initialized
        }

# Global terminal session manager instance
_terminal_session_manager: Optional[TerminalSessionManager] = None

def get_terminal_session_manager() -> TerminalSessionManager:
    """Get global terminal session manager instance"""
    global _terminal_session_manager
    if _terminal_session_manager is None:
        _terminal_session_manager = TerminalSessionManager()
    return _terminal_session_manager
