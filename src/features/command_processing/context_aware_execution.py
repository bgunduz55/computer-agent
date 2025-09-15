"""
Context-Aware Execution Manager for JARVIS Computer Assistant

This module manages execution context and memory across command sequences,
providing intelligent context tracking and memory management capabilities.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of context information"""
    USER_PREFERENCE = "user_preference"
    SYSTEM_STATE = "system_state"
    EXECUTION_HISTORY = "execution_history"
    ENVIRONMENT = "environment"
    TEMPORARY = "temporary"

class ContextPriority(Enum):
    """Priority levels for context entries"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class MemoryEntry:
    """Represents a single entry in the memory system"""
    entry_id: str
    session_id: str
    key: str
    value: Any
    context_type: ContextType
    priority: ContextPriority
    timestamp: float
    tags: List[str] = field(default_factory=list)
    expires_at: Optional[float] = None

@dataclass
class ExecutionContext:
    """Represents the context of an ongoing command execution session"""
    session_id: str
    user_id: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    command_sequence: List[str] = field(default_factory=list)
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    status: str = "active"
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContextAwareExecutionManager:
    """Manages execution context and memory for intelligent commands"""
    
    def __init__(self):
        self.active_contexts: Dict[str, ExecutionContext] = {}
        self.memory_store: List[MemoryEntry] = []
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False

    async def initialize(self) -> bool:
        """Initialize the context manager"""
        try:
            self._is_initialized = True
            self.logger.info("Context-aware execution manager initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize context manager: {e}")
            return False

    async def create_execution_context(self, 
                                     session_id: str, 
                                     user_id: Optional[str] = None,
                                     command_sequence: Optional[List[str]] = None) -> ExecutionContext:
        """Create a new execution context"""
        try:
            context = ExecutionContext(
                session_id=session_id,
                user_id=user_id,
                command_sequence=command_sequence or [],
                total_steps=len(command_sequence) if command_sequence else None
            )
            
            self.active_contexts[session_id] = context
            self.logger.info(f"Created execution context for session {session_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to create execution context: {e}")
            raise

    async def get_execution_context(self, session_id: str) -> Optional[ExecutionContext]:
        """Get execution context by session ID"""
        return self.active_contexts.get(session_id)

    async def update_execution_context(self, session_id: str, updates: Dict[str, Any]) -> Optional[ExecutionContext]:
        """Update execution context with new information"""
        try:
            context = self.active_contexts.get(session_id)
            if not context:
                return None
            
            # Update context fields
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
                else:
                    context.metadata[key] = value
            
            context.last_activity = time.time()
            self.logger.debug(f"Updated execution context for session {session_id}")
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to update execution context: {e}")
            return None

    async def store_memory_entry(self, 
                               session_id: str, 
                               key: str, 
                               value: Any, 
                               context_type: ContextType,
                               priority: ContextPriority = ContextPriority.MEDIUM,
                               tags: Optional[List[str]] = None,
                               expires_at: Optional[float] = None) -> MemoryEntry:
        """Store a memory entry"""
        try:
            entry = MemoryEntry(
                entry_id=str(uuid.uuid4()),
                session_id=session_id,
                key=key,
                value=value,
                context_type=context_type,
                priority=priority,
                timestamp=time.time(),
                tags=tags or [],
                expires_at=expires_at
            )
            
            self.memory_store.append(entry)
            self.logger.debug(f"Stored memory entry: {key} for session {session_id}")
            return entry
            
        except Exception as e:
            self.logger.error(f"Failed to store memory entry: {e}")
            raise

    async def search_memory_entries(self, 
                                  session_id: str, 
                                  query: Optional[str] = None,
                                  context_type: Optional[ContextType] = None,
                                  priority: Optional[ContextPriority] = None,
                                  tags: Optional[List[str]] = None,
                                  limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries with filters"""
        try:
            filtered_entries = []
            
            for entry in self.memory_store:
                # Filter by session
                if entry.session_id != session_id:
                    continue
                
                # Filter by context type
                if context_type and entry.context_type != context_type:
                    continue
                
                # Filter by priority
                if priority and entry.priority != priority:
                    continue
                
                # Filter by tags
                if tags and not any(tag in entry.tags for tag in tags):
                    continue
                
                # Filter by query
                if query and query.lower() not in str(entry.value).lower():
                    continue
                
                # Check expiration
                if entry.expires_at and time.time() > entry.expires_at:
                    continue
                
                filtered_entries.append(entry)
            
            # Sort by timestamp (newest first)
            filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            return filtered_entries[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to search memory entries: {e}")
            return []

    async def get_context_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the execution context"""
        try:
            context = self.active_contexts.get(session_id)
            if not context:
                return {}
            
            # Get recent memory entries
            recent_memories = await self.search_memory_entries(
                session_id=session_id,
                limit=5
            )
            
            return {
                "session_id": session_id,
                "user_id": context.user_id,
                "status": context.status,
                "current_step": context.current_step,
                "total_steps": context.total_steps,
                "command_sequence": context.command_sequence,
                "variables": context.variables,
                "recent_memories": [
                    {
                        "key": entry.key,
                        "value": str(entry.value)[:100],  # Truncate long values
                        "context_type": entry.context_type.value,
                        "priority": entry.priority.value,
                        "timestamp": entry.timestamp
                    }
                    for entry in recent_memories
                ],
                "metadata": context.metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get context summary: {e}")
            return {}

    async def cleanup(self):
        """Cleanup the context manager"""
        try:
            # Remove expired memory entries
            current_time = time.time()
            self.memory_store = [
                entry for entry in self.memory_store
                if not entry.expires_at or entry.expires_at > current_time
            ]
            
            # Clear inactive contexts
            inactive_time = time.time() - 3600  # 1 hour
            self.active_contexts = {
                session_id: context
                for session_id, context in self.active_contexts.items()
                if context.last_activity > inactive_time
            }
            
            self.logger.info("Context manager cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Global instance
_context_manager: Optional[ContextAwareExecutionManager] = None

def get_context_manager() -> ContextAwareExecutionManager:
    """Get the global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextAwareExecutionManager()
    return _context_manager
