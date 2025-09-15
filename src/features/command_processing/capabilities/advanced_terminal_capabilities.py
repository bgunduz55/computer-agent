"""
Advanced Terminal Capabilities for JARVIS Computer Assistant

Provides enhanced terminal integration including real-time monitoring,
session management, command chaining, and intelligent execution.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from ...terminal_integration.terminal_manager import TerminalManager, TerminalType, CommandType, CommandResult, TerminalSession

logger = logging.getLogger(__name__)

class TerminalStatus(Enum):
    """Terminal execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class CommandChainType(Enum):
    """Command chain execution types"""
    SEQUENTIAL = "sequential"  # Execute one after another
    PARALLEL = "parallel"      # Execute simultaneously
    CONDITIONAL = "conditional"  # Execute based on previous results
    PIPELINE = "pipeline"      # Pipe output between commands

@dataclass
class TerminalExecution:
    """Terminal execution tracking"""
    execution_id: str
    session_id: str
    command: str
    status: TerminalStatus
    start_time: float
    end_time: Optional[float] = None
    result: Optional[CommandResult] = None
    error_message: Optional[str] = None
    progress_percentage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CommandChain:
    """Command chain definition"""
    chain_id: str
    name: str
    commands: List[str]
    chain_type: CommandChainType
    working_directory: Optional[str] = None
    terminal_type: Optional[TerminalType] = None
    timeout: int = 300
    stop_on_error: bool = True
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TerminalMonitor:
    """Real-time terminal monitoring"""
    monitor_id: str
    session_id: str
    callback: Callable[[TerminalExecution], None]
    is_active: bool = True
    created_at: float = field(default_factory=time.time)

class AdvancedTerminalExecutor:
    """Advanced terminal execution capabilities"""
    
    def __init__(self):
        self.terminal_manager = TerminalManager()
        self.executions: Dict[str, TerminalExecution] = {}
        self.command_chains: Dict[str, CommandChain] = {}
        self.monitors: Dict[str, TerminalMonitor] = {}
        self._is_initialized = False
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize advanced terminal executor"""
        try:
            if not self.terminal_manager.initialize():
                return False
            
            self._is_initialized = True
            self.logger.info("Advanced terminal executor initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize advanced terminal executor: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            # Cancel all active executions
            for execution in self.executions.values():
                if execution.status == TerminalStatus.RUNNING:
                    execution.status = TerminalStatus.CANCELLED
                    execution.end_time = time.time()
            
            # Stop all monitors
            for monitor in self.monitors.values():
                monitor.is_active = False
            
            # Cleanup terminal manager
            self.terminal_manager.cleanup()
            
            self._is_initialized = False
            self.logger.info("Advanced terminal executor cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup advanced terminal executor: {e}")
    
    def _can_handle(self, parameters: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("advanced_terminal" in parameters or
                "terminal_execution" in parameters or
                "command_chain" in parameters or
                "terminal_monitoring" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute advanced terminal capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Advanced terminal executor not initialized"}
            
            operation = parameters.get("operation")
            if not operation:
                return {"success": False, "error": "Operation not specified"}
            
            if operation == "execute_command":
                return await self._execute_command(parameters)
            elif operation == "execute_command_chain":
                return await self._execute_command_chain(parameters)
            elif operation == "create_session":
                return await self._create_session(parameters)
            elif operation == "get_session_info":
                return await self._get_session_info(parameters)
            elif operation == "close_session":
                return await self._close_session(parameters)
            elif operation == "list_sessions":
                return await self._list_sessions(parameters)
            elif operation == "monitor_session":
                return await self._monitor_session(parameters)
            elif operation == "stop_monitoring":
                return await self._stop_monitoring(parameters)
            elif operation == "get_execution_status":
                return await self._get_execution_status(parameters)
            elif operation == "cancel_execution":
                return await self._cancel_execution(parameters)
            elif operation == "get_command_history":
                return await self._get_command_history(parameters)
            elif operation == "create_command_chain":
                return await self._create_command_chain(parameters)
            elif operation == "execute_command_chain":
                return await self._execute_command_chain(parameters)
            elif operation == "list_command_chains":
                return await self._list_command_chains(parameters)
            elif operation == "get_system_info":
                return await self._get_system_info(parameters)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
        
        except Exception as e:
            self.logger.error(f"Failed to execute advanced terminal capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_command(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single command with advanced tracking"""
        try:
            command = parameters.get("command")
            if not command:
                return {"success": False, "error": "Command not specified"}
            
            session_id = parameters.get("session_id")
            terminal_type = parameters.get("terminal_type")
            working_directory = parameters.get("working_directory")
            timeout = parameters.get("timeout", 30)
            
            # Create execution tracking
            execution_id = str(uuid.uuid4())
            execution = TerminalExecution(
                execution_id=execution_id,
                session_id=session_id or "default",
                command=command,
                status=TerminalStatus.PENDING,
                start_time=time.time()
            )
            self.executions[execution_id] = execution
            
            # Convert terminal type if provided
            if terminal_type and isinstance(terminal_type, str):
                try:
                    terminal_type = TerminalType(terminal_type)
                except ValueError:
                    terminal_type = None
            
            # Execute command
            execution.status = TerminalStatus.RUNNING
            execution.progress_percentage = 10.0
            
            # Notify monitors
            await self._notify_monitors(execution)
            
            result = await self.terminal_manager.execute_command(
                command=command,
                terminal_type=terminal_type,
                working_directory=working_directory,
                timeout=timeout
            )
            
            # Update execution
            execution.result = result
            execution.status = TerminalStatus.COMPLETED if result.success else TerminalStatus.FAILED
            execution.end_time = time.time()
            execution.progress_percentage = 100.0
            execution.error_message = result.error if not result.success else None
            
            # Notify monitors
            await self._notify_monitors(execution)
            
            return {
                "success": True,
                "execution_id": execution_id,
                "result": {
                    "command": result.command,
                    "output": result.output,
                    "error": result.error,
                    "exit_code": result.exit_code,
                    "execution_time": result.execution_time,
                    "success": result.success
                },
                "execution_status": {
                    "status": execution.status.value,
                    "start_time": execution.start_time,
                    "end_time": execution.end_time,
                    "progress_percentage": execution.progress_percentage
                }
            }
        
        except Exception as e:
            if execution_id in self.executions:
                execution = self.executions[execution_id]
                execution.status = TerminalStatus.FAILED
                execution.end_time = time.time()
                execution.error_message = str(e)
                await self._notify_monitors(execution)
            
            return {"success": False, "error": str(e)}
    
    async def _execute_command_chain(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a chain of commands"""
        try:
            chain_id = parameters.get("chain_id")
            commands = parameters.get("commands", [])
            chain_type = parameters.get("chain_type", "sequential")
            working_directory = parameters.get("working_directory")
            terminal_type = parameters.get("terminal_type")
            timeout = parameters.get("timeout", 300)
            stop_on_error = parameters.get("stop_on_error", True)
            
            if not commands:
                return {"success": False, "error": "No commands provided"}
            
            # Convert chain type
            try:
                chain_type_enum = CommandChainType(chain_type)
            except ValueError:
                chain_type_enum = CommandChainType.SEQUENTIAL
            
            # Convert terminal type if provided
            if terminal_type and isinstance(terminal_type, str):
                try:
                    terminal_type = TerminalType(terminal_type)
                except ValueError:
                    terminal_type = None
            
            # Create chain if not exists
            if not chain_id:
                chain_id = str(uuid.uuid4())
                chain = CommandChain(
                    chain_id=chain_id,
                    name=f"Chain_{int(time.time())}",
                    commands=commands,
                    chain_type=chain_type_enum,
                    working_directory=working_directory,
                    terminal_type=terminal_type,
                    timeout=timeout,
                    stop_on_error=stop_on_error
                )
                self.command_chains[chain_id] = chain
            
            # Execute based on chain type
            if chain_type_enum == CommandChainType.SEQUENTIAL:
                return await self._execute_sequential_chain(chain_id, commands, terminal_type, working_directory, timeout, stop_on_error)
            elif chain_type_enum == CommandChainType.PARALLEL:
                return await self._execute_parallel_chain(chain_id, commands, terminal_type, working_directory, timeout)
            elif chain_type_enum == CommandChainType.PIPELINE:
                return await self._execute_pipeline_chain(chain_id, commands, terminal_type, working_directory, timeout)
            else:
                return {"success": False, "error": f"Unsupported chain type: {chain_type}"}
        
        except Exception as e:
            self.logger.error(f"Failed to execute command chain: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_sequential_chain(self, chain_id: str, commands: List[str], 
                                      terminal_type: Optional[TerminalType], 
                                      working_directory: Optional[str], 
                                      timeout: int, stop_on_error: bool) -> Dict[str, Any]:
        """Execute commands sequentially"""
        results = []
        execution_id = str(uuid.uuid4())
        
        for i, command in enumerate(commands):
            try:
                # Create execution tracking
                execution = TerminalExecution(
                    execution_id=f"{execution_id}_{i}",
                    session_id=chain_id,
                    command=command,
                    status=TerminalStatus.PENDING,
                    start_time=time.time()
                )
                self.executions[execution[execution_id]] = execution
                
                # Execute command
                execution.status = TerminalStatus.RUNNING
                result = await self.terminal_manager.execute_command(
                    command=command,
                    terminal_type=terminal_type,
                    working_directory=working_directory,
                    timeout=timeout
                )
                
                # Update execution
                execution.result = result
                execution.status = TerminalStatus.COMPLETED if result.success else TerminalStatus.FAILED
                execution.end_time = time.time()
                execution.progress_percentage = 100.0
                
                results.append({
                    "command": command,
                    "result": result,
                    "execution_id": execution.execution_id
                })
                
                # Stop on error if configured
                if not result.success and stop_on_error:
                    break
                
            except Exception as e:
                execution.status = TerminalStatus.FAILED
                execution.end_time = time.time()
                execution.error_message = str(e)
                results.append({
                    "command": command,
                    "error": str(e),
                    "execution_id": execution.execution_id
                })
                
                if stop_on_error:
                    break
        
        return {
            "success": True,
            "chain_id": chain_id,
            "execution_type": "sequential",
            "results": results,
            "total_commands": len(commands),
            "successful_commands": len([r for r in results if r.get("result", {}).get("success", False)])
        }
    
    async def _execute_parallel_chain(self, chain_id: str, commands: List[str], 
                                    terminal_type: Optional[TerminalType], 
                                    working_directory: Optional[str], 
                                    timeout: int) -> Dict[str, Any]:
        """Execute commands in parallel"""
        try:
            # Create tasks for all commands
            tasks = []
            for i, command in enumerate(commands):
                task = asyncio.create_task(
                    self.terminal_manager.execute_command(
                        command=command,
                        terminal_type=terminal_type,
                        working_directory=working_directory,
                        timeout=timeout
                    )
                )
                tasks.append((command, task))
            
            # Wait for all tasks to complete
            results = []
            for command, task in tasks:
                try:
                    result = await task
                    results.append({
                        "command": command,
                        "result": result,
                        "success": result.success
                    })
                except Exception as e:
                    results.append({
                        "command": command,
                        "error": str(e),
                        "success": False
                    })
            
            return {
                "success": True,
                "chain_id": chain_id,
                "execution_type": "parallel",
                "results": results,
                "total_commands": len(commands),
                "successful_commands": len([r for r in results if r.get("success", False)])
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_pipeline_chain(self, chain_id: str, commands: List[str], 
                                    terminal_type: Optional[TerminalType], 
                                    working_directory: Optional[str], 
                                    timeout: int) -> Dict[str, Any]:
        """Execute commands in pipeline (output of one becomes input of next)"""
        try:
            results = []
            current_input = None
            
            for i, command in enumerate(commands):
                try:
                    # Modify command to use previous output if available
                    if current_input and i > 0:
                        if terminal_type == TerminalType.POWERSHELL:
                            command = f"echo '{current_input}' | {command}"
                        else:
                            command = f"echo '{current_input}' | {command}"
                    
                    result = await self.terminal_manager.execute_command(
                        command=command,
                        terminal_type=terminal_type,
                        working_directory=working_directory,
                        timeout=timeout
                    )
                    
                    results.append({
                        "command": command,
                        "result": result,
                        "success": result.success
                    })
                    
                    # Use output as input for next command
                    if result.success and result.output:
                        current_input = result.output.strip()
                    else:
                        break
                
                except Exception as e:
                    results.append({
                        "command": command,
                        "error": str(e),
                        "success": False
                    })
                    break
            
            return {
                "success": True,
                "chain_id": chain_id,
                "execution_type": "pipeline",
                "results": results,
                "total_commands": len(commands),
                "successful_commands": len([r for r in results if r.get("success", False)])
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new terminal session"""
        try:
            terminal_type = parameters.get("terminal_type")
            working_directory = parameters.get("working_directory")
            
            if terminal_type and isinstance(terminal_type, str):
                try:
                    terminal_type = TerminalType(terminal_type)
                except ValueError:
                    return {"success": False, "error": f"Invalid terminal type: {terminal_type}"}
            
            session_id = self.terminal_manager.create_session(
                terminal_type=terminal_type,
                working_directory=working_directory
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "terminal_type": terminal_type.value if terminal_type else "default",
                "working_directory": working_directory or "current"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_session_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get terminal session information"""
        try:
            session_id = parameters.get("session_id")
            if not session_id:
                return {"success": False, "error": "Session ID not specified"}
            
            session = self.terminal_manager.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            return {
                "success": True,
                "session": {
                    "session_id": session.session_id,
                    "terminal_type": session.terminal_type.value,
                    "working_directory": session.working_directory,
                    "is_active": session.is_active,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity
                }
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _close_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Close terminal session"""
        try:
            session_id = parameters.get("session_id")
            if not session_id:
                return {"success": False, "error": "Session ID not specified"}
            
            success = self.terminal_manager.close_session(session_id)
            return {
                "success": success,
                "message": f"Session {session_id} {'closed' if success else 'not found'}"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_sessions(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List all terminal sessions"""
        try:
            sessions = []
            for session in self.terminal_manager.sessions.values():
                sessions.append({
                    "session_id": session.session_id,
                    "terminal_type": session.terminal_type.value,
                    "working_directory": session.working_directory,
                    "is_active": session.is_active,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity
                })
            
            return {
                "success": True,
                "sessions": sessions,
                "total_sessions": len(sessions)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _monitor_session(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Start monitoring a terminal session"""
        try:
            session_id = parameters.get("session_id")
            if not session_id:
                return {"success": False, "error": "Session ID not specified"}
            
            # Create monitor
            monitor_id = str(uuid.uuid4())
            monitor = TerminalMonitor(
                monitor_id=monitor_id,
                session_id=session_id,
                callback=self._default_monitor_callback
            )
            self.monitors[monitor_id] = monitor
            
            return {
                "success": True,
                "monitor_id": monitor_id,
                "session_id": session_id,
                "message": "Monitoring started"
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stop_monitoring(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Stop monitoring a terminal session"""
        try:
            monitor_id = parameters.get("monitor_id")
            if not monitor_id:
                return {"success": False, "error": "Monitor ID not specified"}
            
            if monitor_id in self.monitors:
                self.monitors[monitor_id].is_active = False
                del self.monitors[monitor_id]
                return {"success": True, "message": "Monitoring stopped"}
            else:
                return {"success": False, "error": "Monitor not found"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_execution_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get execution status"""
        try:
            execution_id = parameters.get("execution_id")
            if not execution_id:
                return {"success": False, "error": "Execution ID not specified"}
            
            if execution_id not in self.executions:
                return {"success": False, "error": "Execution not found"}
            
            execution = self.executions[execution_id]
            return {
                "success": True,
                "execution": {
                    "execution_id": execution.execution_id,
                    "session_id": execution.session_id,
                    "command": execution.command,
                    "status": execution.status.value,
                    "start_time": execution.start_time,
                    "end_time": execution.end_time,
                    "progress_percentage": execution.progress_percentage,
                    "error_message": execution.error_message
                }
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _cancel_execution(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel execution"""
        try:
            execution_id = parameters.get("execution_id")
            if not execution_id:
                return {"success": False, "error": "Execution ID not specified"}
            
            if execution_id not in self.executions:
                return {"success": False, "error": "Execution not found"}
            
            execution = self.executions[execution_id]
            if execution.status == TerminalStatus.RUNNING:
                execution.status = TerminalStatus.CANCELLED
                execution.end_time = time.time()
                return {"success": True, "message": "Execution cancelled"}
            else:
                return {"success": False, "error": "Execution not running"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_command_history(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get command execution history"""
        try:
            limit = parameters.get("limit", 50)
            history = self.terminal_manager.get_command_history(limit)
            
            return {
                "success": True,
                "history": [
                    {
                        "command": result.command,
                        "output": result.output,
                        "error": result.error,
                        "exit_code": result.exit_code,
                        "execution_time": result.execution_time,
                        "success": result.success,
                        "command_type": result.command_type.value,
                        "metadata": result.metadata
                    }
                    for result in history
                ],
                "total_commands": len(history)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_command_chain(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a command chain"""
        try:
            name = parameters.get("name", f"Chain_{int(time.time())}")
            commands = parameters.get("commands", [])
            chain_type = parameters.get("chain_type", "sequential")
            working_directory = parameters.get("working_directory")
            terminal_type = parameters.get("terminal_type")
            timeout = parameters.get("timeout", 300)
            stop_on_error = parameters.get("stop_on_error", True)
            
            if not commands:
                return {"success": False, "error": "No commands provided"}
            
            # Convert chain type
            try:
                chain_type_enum = CommandChainType(chain_type)
            except ValueError:
                return {"success": False, "error": f"Invalid chain type: {chain_type}"}
            
            # Convert terminal type if provided
            if terminal_type and isinstance(terminal_type, str):
                try:
                    terminal_type = TerminalType(terminal_type)
                except ValueError:
                    terminal_type = None
            
            chain_id = str(uuid.uuid4())
            chain = CommandChain(
                chain_id=chain_id,
                name=name,
                commands=commands,
                chain_type=chain_type_enum,
                working_directory=working_directory,
                terminal_type=terminal_type,
                timeout=timeout,
                stop_on_error=stop_on_error
            )
            
            self.command_chains[chain_id] = chain
            
            return {
                "success": True,
                "chain_id": chain_id,
                "chain": {
                    "chain_id": chain.chain_id,
                    "name": chain.name,
                    "commands": chain.commands,
                    "chain_type": chain.chain_type.value,
                    "working_directory": chain.working_directory,
                    "terminal_type": chain.terminal_type.value if chain.terminal_type else None,
                    "timeout": chain.timeout,
                    "stop_on_error": chain.stop_on_error,
                    "created_at": chain.created_at
                }
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_command_chains(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List all command chains"""
        try:
            chains = []
            for chain in self.command_chains.values():
                chains.append({
                    "chain_id": chain.chain_id,
                    "name": chain.name,
                    "commands": chain.commands,
                    "chain_type": chain.chain_type.value,
                    "working_directory": chain.working_directory,
                    "terminal_type": chain.terminal_type.value if chain.terminal_type else None,
                    "timeout": chain.timeout,
                    "stop_on_error": chain.stop_on_error,
                    "created_at": chain.created_at
                })
            
            return {
                "success": True,
                "chains": chains,
                "total_chains": len(chains)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_system_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get terminal system information"""
        try:
            info = self.terminal_manager.get_system_info()
            return {
                "success": True,
                "system_info": info,
                "active_executions": len([e for e in self.executions.values() if e.status == TerminalStatus.RUNNING]),
                "total_executions": len(self.executions),
                "active_monitors": len([m for m in self.monitors.values() if m.is_active]),
                "command_chains": len(self.command_chains)
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _notify_monitors(self, execution: TerminalExecution) -> None:
        """Notify all active monitors about execution updates"""
        try:
            for monitor in self.monitors.values():
                if monitor.is_active and monitor.session_id == execution.session_id:
                    try:
                        await monitor.callback(execution)
                    except Exception as e:
                        self.logger.error(f"Monitor callback failed: {e}")
        except Exception as e:
            self.logger.error(f"Failed to notify monitors: {e}")
    
    def _default_monitor_callback(self, execution: TerminalExecution) -> None:
        """Default monitor callback"""
        self.logger.info(f"Execution {execution.execution_id}: {execution.status.value} - {execution.command}")
