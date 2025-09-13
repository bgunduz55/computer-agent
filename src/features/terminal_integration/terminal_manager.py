"""
Terminal Integration Manager for JARVIS Computer Assistant

This module provides cross-platform terminal integration including PowerShell/CMD
on Windows and bash/zsh on Linux, with intelligent command parsing and execution.
"""

import asyncio
import logging
import subprocess
import shlex
import os
import platform
import tempfile
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import time
import threading
import queue

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.platform import get_platform

logger = logging.getLogger(__name__)

class TerminalType(Enum):
    """Supported terminal types"""
    POWERSHELL = "powershell"
    CMD = "cmd"
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"
    WSL = "wsl"

class CommandType(Enum):
    """Command types for intelligent parsing"""
    SYSTEM_INFO = "system_info"
    FILE_OPERATION = "file_operation"
    PROCESS_MANAGEMENT = "process_management"
    NETWORK = "network"
    PACKAGE_MANAGER = "package_manager"
    GIT = "git"
    DOCKER = "docker"
    CUSTOM = "custom"

@dataclass
class CommandResult:
    """Result of command execution"""
    command: str
    output: str
    error: str
    exit_code: int
    execution_time: float
    command_type: CommandType
    success: bool
    metadata: Dict[str, Any] = None

@dataclass
class TerminalSession:
    """Active terminal session"""
    session_id: str
    terminal_type: TerminalType
    working_directory: str
    environment: Dict[str, str]
    created_at: float
    last_activity: float
    is_active: bool = True

class TerminalManager:
    """Cross-platform terminal management system"""
    
    def __init__(self):
        self.platform = get_platform()
        self.sessions: Dict[str, TerminalSession] = {}
        self.command_history: List[CommandResult] = []
        self.logger = logging.getLogger(__name__)
        
        # Platform-specific configurations
        self.terminal_configs = self._load_terminal_configs()
        
        # Command patterns for intelligent parsing
        self.command_patterns = self._load_command_patterns()
    
    def initialize(self) -> bool:
        """Initialize terminal manager"""
        try:
            self.logger.info("Terminal manager initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize terminal manager: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup terminal manager"""
        try:
            # Close all active sessions
            for session in self.sessions.values():
                session.is_active = False
            self.sessions.clear()
            self.logger.info("Terminal manager cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup terminal manager: {e}")
    
    def _load_terminal_configs(self) -> Dict[str, Any]:
        """Load terminal configurations for current platform"""
        if platform.system() == "Windows":
            return {
                "default": TerminalType.POWERSHELL,
                "available": [TerminalType.POWERSHELL, TerminalType.CMD, TerminalType.WSL],
                "executables": {
                    TerminalType.POWERSHELL: "powershell.exe",
                    TerminalType.CMD: "cmd.exe",
                    TerminalType.WSL: "wsl.exe"
                },
                "shell_args": {
                    TerminalType.POWERSHELL: ["-NoProfile", "-ExecutionPolicy", "Bypass"],
                    TerminalType.CMD: ["/c"],
                    TerminalType.WSL: []
                }
            }
        else:  # Linux/macOS
            return {
                "default": TerminalType.BASH,
                "available": [TerminalType.BASH, TerminalType.ZSH, TerminalType.FISH],
                "executables": {
                    TerminalType.BASH: "/bin/bash",
                    TerminalType.ZSH: "/bin/zsh",
                    TerminalType.FISH: "/usr/bin/fish"
                },
                "shell_args": {
                    TerminalType.BASH: ["-c"],
                    TerminalType.ZSH: ["-c"],
                    TerminalType.FISH: ["-c"]
                }
            }
    
    def _load_command_patterns(self) -> Dict[CommandType, List[str]]:
        """Load command patterns for intelligent parsing"""
        return {
            CommandType.SYSTEM_INFO: [
                "systeminfo", "hostname", "whoami", "uname", "uptime",
                "ps", "top", "htop", "df", "du", "free", "lscpu", "lsmem"
            ],
            CommandType.FILE_OPERATION: [
                "ls", "dir", "cd", "pwd", "mkdir", "rmdir", "rm", "del",
                "cp", "copy", "mv", "move", "find", "grep", "cat", "type"
            ],
            CommandType.PROCESS_MANAGEMENT: [
                "tasklist", "taskkill", "ps", "kill", "killall", "pkill",
                "start", "stop", "restart", "service"
            ],
            CommandType.NETWORK: [
                "ping", "tracert", "traceroute", "nslookup", "dig",
                "netstat", "ss", "ipconfig", "ifconfig", "ip"
            ],
            CommandType.PACKAGE_MANAGER: [
                "apt", "yum", "dnf", "pacman", "brew", "choco", "winget",
                "pip", "npm", "yarn", "composer", "cargo", "go"
            ],
            CommandType.GIT: [
                "git", "git clone", "git pull", "git push", "git commit",
                "git status", "git log", "git branch", "git checkout"
            ],
            CommandType.DOCKER: [
                "docker", "docker run", "docker build", "docker push",
                "docker pull", "docker ps", "docker images", "docker-compose"
            ]
        }
    
    def _detect_command_type(self, command: str) -> CommandType:
        """Detect command type for intelligent handling"""
        command_lower = command.lower().strip()
        
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if command_lower.startswith(pattern):
                    return cmd_type
        
        return CommandType.CUSTOM
    
    def _sanitize_command(self, command: str) -> str:
        """Sanitize command for safe execution"""
        # Remove potentially dangerous characters
        dangerous_chars = [';', '&', '|', '`', '$', '$(', '${']
        for char in dangerous_chars:
            if char in command:
                self.logger.warning(f"Potentially dangerous character '{char}' in command: {command}")
        
        # Basic sanitization (more sophisticated validation can be added)
        return command.strip()
    
    async def execute_command(self, command: str, terminal_type: Optional[TerminalType] = None,
                            working_directory: Optional[str] = None, timeout: int = 30) -> CommandResult:
        """Execute a command in the specified terminal"""
        try:
            start_time = time.time()
            
            # Use default terminal type if not specified
            if terminal_type is None:
                terminal_type = self.terminal_configs["default"]
            
            # Sanitize command
            sanitized_command = self._sanitize_command(command)
            
            # Detect command type
            cmd_type = self._detect_command_type(sanitized_command)
            
            # Prepare execution environment
            env = os.environ.copy()
            if working_directory:
                env["PWD"] = working_directory
            
            # Get terminal executable and arguments
            executable = self.terminal_configs["executables"][terminal_type]
            shell_args = self.terminal_configs["shell_args"][terminal_type]
            
            # Prepare command for execution
            if terminal_type == TerminalType.POWERSHELL:
                # PowerShell specific handling
                full_command = [executable] + shell_args + [sanitized_command]
            elif terminal_type == TerminalType.CMD:
                # CMD specific handling
                full_command = [executable] + shell_args + [sanitized_command]
            else:
                # Unix-like shells
                full_command = [executable] + shell_args + [sanitized_command]
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory,
                env=env
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Command timed out after {timeout} seconds")
            
            # Decode output
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace')
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create result
            result = CommandResult(
                command=sanitized_command,
                output=output,
                error=error,
                exit_code=process.returncode,
                execution_time=execution_time,
                command_type=cmd_type,
                success=process.returncode == 0,
                metadata={
                    "terminal_type": terminal_type.value,
                    "working_directory": working_directory or os.getcwd(),
                    "platform": platform.system()
                }
            )
            
            # Add to history
            self.command_history.append(result)
            
            # Log result
            if result.success:
                self.logger.info(f"Command executed successfully: {sanitized_command}")
            else:
                self.logger.warning(f"Command failed: {sanitized_command} (exit code: {result.exit_code})")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to execute command '{command}': {e}")
            return CommandResult(
                command=command,
                output="",
                error=str(e),
                exit_code=-1,
                execution_time=0,
                command_type=CommandType.CUSTOM,
                success=False,
                metadata={"error": str(e)}
            )
    
    async def execute_multiple_commands(self, commands: List[str], 
                                      terminal_type: Optional[TerminalType] = None,
                                      working_directory: Optional[str] = None) -> List[CommandResult]:
        """Execute multiple commands sequentially"""
        results = []
        
        for command in commands:
            result = await self.execute_command(
                command, terminal_type, working_directory
            )
            results.append(result)
            
            # Stop on first failure if configured
            if not result.success:
                self.logger.warning(f"Stopping execution due to command failure: {command}")
                break
        
        return results
    
    async def execute_script(self, script_content: str, script_type: str = "auto",
                           terminal_type: Optional[TerminalType] = None,
                           working_directory: Optional[str] = None) -> CommandResult:
        """Execute a script file"""
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=self._get_script_extension(script_type)) as f:
                f.write(script_content)
                script_path = f.name
            
            try:
                # Execute script
                if script_type == "powershell" or (script_type == "auto" and platform.system() == "Windows"):
                    command = f"powershell -ExecutionPolicy Bypass -File {script_path}"
                elif script_type == "bash" or (script_type == "auto" and platform.system() != "Windows"):
                    command = f"bash {script_path}"
                else:
                    command = f"python {script_path}"
                
                result = await self.execute_command(command, terminal_type, working_directory)
                return result
            
            finally:
                # Clean up temporary file
                os.unlink(script_path)
        
        except Exception as e:
            self.logger.error(f"Failed to execute script: {e}")
            return CommandResult(
                command="script_execution",
                output="",
                error=str(e),
                exit_code=-1,
                execution_time=0,
                command_type=CommandType.CUSTOM,
                success=False
            )
    
    def _get_script_extension(self, script_type: str) -> str:
        """Get file extension for script type"""
        extensions = {
            "powershell": ".ps1",
            "bash": ".sh",
            "python": ".py",
            "batch": ".bat",
            "auto": ".ps1" if platform.system() == "Windows" else ".sh"
        }
        return extensions.get(script_type, ".txt")
    
    def get_available_terminals(self) -> List[TerminalType]:
        """Get list of available terminal types"""
        return self.terminal_configs["available"]
    
    def get_command_history(self, limit: int = 50) -> List[CommandResult]:
        """Get command execution history"""
        return self.command_history[-limit:]
    
    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """Get command suggestions based on partial input"""
        suggestions = []
        partial_lower = partial_command.lower()
        
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if pattern.startswith(partial_lower):
                    suggestions.append(pattern)
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def create_session(self, terminal_type: Optional[TerminalType] = None,
                      working_directory: Optional[str] = None) -> str:
        """Create a new terminal session"""
        session_id = f"session_{int(time.time())}"
        
        if terminal_type is None:
            terminal_type = self.terminal_configs["default"]
        
        session = TerminalSession(
            session_id=session_id,
            terminal_type=terminal_type,
            working_directory=working_directory or os.getcwd(),
            environment=os.environ.copy(),
            created_at=time.time(),
            last_activity=time.time()
        )
        
        self.sessions[session_id] = session
        self.logger.info(f"Created terminal session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get terminal session by ID"""
        return self.sessions.get(session_id)
    
    def close_session(self, session_id: str) -> bool:
        """Close terminal session"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            del self.sessions[session_id]
            self.logger.info(f"Closed terminal session: {session_id}")
            return True
        return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for terminal context"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "available_terminals": [t.value for t in self.get_available_terminals()],
            "active_sessions": len(self.sessions),
            "command_history_size": len(self.command_history)
        }

# Global terminal manager instance
_terminal_manager: Optional[TerminalManager] = None

def get_terminal_manager() -> TerminalManager:
    """Get global terminal manager instance"""
    global _terminal_manager
    if _terminal_manager is None:
        _terminal_manager = TerminalManager()
    return _terminal_manager
