"""
Command Execution Engine
Executes processed commands using appropriate executors
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import time

from .command_classifier import CommandCategory
from .nlp_engine import ProcessedCommand, IntentType

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    message: str
    data: Dict[str, Any] = None
    execution_time: float = 0.0
    status: ExecutionStatus = ExecutionStatus.COMPLETED
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class BaseExecutor:
    """Base class for command executors"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_running = False
    
    async def execute(self, command: ProcessedCommand) -> CommandResult:
        """Execute a command"""
        raise NotImplementedError("Subclasses must implement execute method")
    
    def can_handle(self, command: ProcessedCommand) -> bool:
        """Check if this executor can handle the command"""
        raise NotImplementedError("Subclasses must implement can_handle method")
    
    def _create_result(self, success: bool, message: str, **kwargs) -> CommandResult:
        """Create a command result"""
        return CommandResult(
            success=success,
            message=message,
            **kwargs
        )


class CommandExecutor:
    """Main command execution engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.executors: Dict[CommandCategory, BaseExecutor] = {}
        self._execution_history: List[CommandResult] = []
        self._max_history = 100
        self._is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize the command executor"""
        try:
            # Import executors here to avoid circular imports
            from .executors.typing_executor import TypingExecutor
            from .executors.application_executor import ApplicationExecutor
            from .executors.browser_executor import BrowserExecutor
            from .executors.system_executor import SystemExecutor
            from .executors.media_executor import MediaExecutor
            from .executors.file_executor import FileExecutor
            
            # Initialize executors
            self.executors = {
                CommandCategory.TYPING: TypingExecutor(),
                CommandCategory.APPLICATION: ApplicationExecutor(),
                CommandCategory.BROWSER: BrowserExecutor(),
                CommandCategory.SYSTEM: SystemExecutor(),
                CommandCategory.MEDIA: MediaExecutor(),
                CommandCategory.FILE: FileExecutor()
            }
            
            self._is_initialized = True
            self.logger.info("Command executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize command executor: {e}")
            return False
    
    async def execute_command(self, command: ProcessedCommand) -> CommandResult:
        """
        Execute a processed command
        
        Args:
            command: Processed command to execute
            
        Returns:
            CommandResult with execution details
        """
        if not self._is_initialized:
            return CommandResult(
                success=False,
                message="Command executor not initialized",
                status=ExecutionStatus.FAILED,
                error="Not initialized"
            )
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Executing command: {command.action} ({command.category.value})")
            
            # Check if command requires confirmation
            if command.requires_confirmation:
                confirmation_result = await self._request_confirmation(command)
                if not confirmation_result:
                    return CommandResult(
                        success=False,
                        message="Command cancelled by user",
                        status=ExecutionStatus.CANCELLED
                    )
            
            # Get appropriate executor
            executor = self.executors.get(command.category)
            if not executor:
                return CommandResult(
                    success=False,
                    message=f"No executor available for category: {command.category.value}",
                    status=ExecutionStatus.FAILED,
                    error="No executor available"
                )
            
            # Check if executor can handle the command
            if not executor.can_handle(command):
                return CommandResult(
                    success=False,
                    message=f"Executor cannot handle command: {command.action}",
                    status=ExecutionStatus.FAILED,
                    error="Cannot handle command"
                )
            
            # Execute the command
            result = await executor.execute(command)
            
            # Add execution time
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            # Add to history
            self._add_to_history(result)
            
            self.logger.info(f"Command executed: {command.action} - "
                           f"Success: {result.success}, Time: {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error executing command: {e}"
            self.logger.error(error_msg)
            
            result = CommandResult(
                success=False,
                message=error_msg,
                execution_time=execution_time,
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
            
            self._add_to_history(result)
            return result
    
    async def _request_confirmation(self, command: ProcessedCommand) -> bool:
        """
        Request user confirmation for dangerous commands
        
        Args:
            command: Command requiring confirmation
            
        Returns:
            True if confirmed, False if cancelled
        """
        # For now, we'll implement a simple confirmation mechanism
        # In a real implementation, this would interact with the UI
        
        confirmation_messages = {
            'shutdown': "Sistem kapatılacak. Devam etmek istiyor musunuz?",
            'restart': "Sistem yeniden başlatılacak. Devam etmek istiyor musunuz?",
            'delete_file': "Dosya silinecek. Devam etmek istiyor musunuz?",
            'close_app': f"{command.parameters.get('app_name', 'Uygulama')} kapatılacak. Devam etmek istiyor musunuz?"
        }
        
        message = confirmation_messages.get(command.action, "Bu komut çalıştırılacak. Devam etmek istiyor musunuz?")
        
        # TODO: Implement actual UI confirmation dialog
        # For now, we'll assume confirmation is granted for testing
        self.logger.info(f"Confirmation requested: {message}")
        return True
    
    def _add_to_history(self, result: CommandResult) -> None:
        """Add result to execution history"""
        self._execution_history.append(result)
        if len(self._execution_history) > self._max_history:
            self._execution_history.pop(0)
    
    def get_execution_history(self, limit: int = 10) -> List[CommandResult]:
        """Get recent execution history"""
        return self._execution_history[-limit:] if self._execution_history else []
    
    def get_executor_status(self) -> Dict[str, Any]:
        """Get status of all executors"""
        status = {}
        for category, executor in self.executors.items():
            status[category.value] = {
                "available": executor is not None,
                "running": getattr(executor, '_is_running', False)
            }
        return status
    
    def cleanup(self) -> None:
        """Cleanup executor resources"""
        try:
            for executor in self.executors.values():
                if hasattr(executor, 'cleanup'):
                    executor.cleanup()
            
            self._execution_history.clear()
            self._is_initialized = False
            self.logger.info("Command executor cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class CommandExecutionManager:
    """Manages command execution with advanced features"""
    
    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.logger = logging.getLogger(__name__)
        self._pending_commands: List[ProcessedCommand] = []
        self._execution_queue = asyncio.Queue()
        self._is_running = False
    
    async def start(self) -> None:
        """Start the execution manager"""
        if self._is_running:
            return
        
        self._is_running = True
        self.logger.info("Command execution manager started")
        
        # Start background task for processing queue
        asyncio.create_task(self._process_queue())
    
    async def stop(self) -> None:
        """Stop the execution manager"""
        self._is_running = False
        self.logger.info("Command execution manager stopped")
    
    async def queue_command(self, command: ProcessedCommand) -> None:
        """Queue a command for execution"""
        await self._execution_queue.put(command)
        self.logger.info(f"Command queued: {command.action}")
    
    async def _process_queue(self) -> None:
        """Process commands from the queue"""
        while self._is_running:
            try:
                # Wait for command with timeout
                command = await asyncio.wait_for(
                    self._execution_queue.get(), 
                    timeout=1.0
                )
                
                # Execute command
                result = await self.executor.execute_command(command)
                
                # Log result
                if result.success:
                    self.logger.info(f"Command completed: {command.action}")
                else:
                    self.logger.error(f"Command failed: {command.action} - {result.message}")
                
            except asyncio.TimeoutError:
                # No commands in queue, continue
                continue
            except Exception as e:
                self.logger.error(f"Error processing command queue: {e}")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        return {
            "queue_size": self._execution_queue.qsize(),
            "is_running": self._is_running,
            "pending_commands": len(self._pending_commands)
        }
