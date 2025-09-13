"""
Simple Terminal Executor for JARVIS Computer Assistant

A simplified terminal executor that works with the capability system.
"""

import asyncio
import logging
import subprocess
import shlex
import os
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TerminalResult:
    """Result of terminal execution"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    command: str
    error: Optional[str] = None

class SimpleTerminalExecutor:
    """Simple terminal executor for capability system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.default_timeout = 30  # seconds
        self.max_timeout = 300  # 5 minutes
        
    async def initialize(self) -> bool:
        """Initialize terminal executor"""
        try:
            # Test basic command execution
            await self._test_terminal_availability()
            self._is_initialized = True
            self.logger.info("Simple terminal executor initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize simple terminal executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return "command" in parameters
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute terminal command"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Terminal executor not initialized"}
            
            command = parameters.get("command", "")
            if not command:
                return {"success": False, "error": "No command provided"}
            
            # Security validation
            if not self._is_command_safe(command):
                return {
                    "success": False,
                    "error": f"Command blocked by security policy: {command}",
                    "security_violation": True
                }
            
            # Execute command
            result = await self._execute_command(command, parameters.get("timeout", self.default_timeout))
            
            return {
                "success": result.success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.return_code,
                "execution_time": result.execution_time,
                "command": result.command,
                "error": result.error
            }
            
        except Exception as e:
            self.logger.error(f"Error executing terminal command: {e}")
            return {"success": False, "error": str(e)}
    
    async def _test_terminal_availability(self):
        """Test if terminal commands are available"""
        try:
            # Test basic command execution
            result = await self._execute_command("echo 'test'", 5)
            if not result.success:
                raise Exception(f"Terminal test failed: {result.error}")
        except Exception as e:
            self.logger.warning(f"Terminal availability test failed: {e}")
            # Don't fail initialization, just warn
    
    async def _execute_command(self, command: str, timeout: float) -> TerminalResult:
        """Execute a terminal command"""
        start_time = time.time()
        
        try:
            # Parse command
            if isinstance(command, str):
                # Split command into parts for subprocess
                if os.name == 'nt':  # Windows
                    # Use shell=True for Windows
                    process = await asyncio.create_subprocess_shell(
                        command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=os.getcwd()
                    )
                else:  # Unix-like
                    # Use shell=False for better security on Unix
                    cmd_parts = shlex.split(command)
                    process = await asyncio.create_subprocess_exec(
                        *cmd_parts,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=os.getcwd()
                    )
            else:
                raise ValueError("Command must be a string")
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                execution_time = time.time() - start_time
                return TerminalResult(
                    success=False,
                    stdout="",
                    stderr="",
                    return_code=-1,
                    execution_time=execution_time,
                    command=command,
                    error=f"Command timed out after {timeout} seconds"
                )
            
            execution_time = time.time() - start_time
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace').strip()
            stderr_text = stderr.decode('utf-8', errors='replace').strip()
            
            success = process.returncode == 0
            
            return TerminalResult(
                success=success,
                stdout=stdout_text,
                stderr=stderr_text,
                return_code=process.returncode,
                execution_time=execution_time,
                command=command,
                error=None if success else f"Command failed with return code {process.returncode}"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TerminalResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                execution_time=execution_time,
                command=command,
                error=str(e)
            )
    
    def _is_command_safe(self, command: str) -> bool:
        """Check if command is safe to execute"""
        # Dangerous commands to block
        dangerous_commands = [
            'rm -rf /',
            'rm -rf ~',
            'rm -rf *',
            'format',
            'fdisk',
            'mkfs',
            'dd if=/dev/zero',
            'shutdown',
            'reboot',
            'halt',
            'poweroff',
            'init 0',
            'init 6',
            'del /f /s /q',
            'rd /s /q',
            'format c:',
            'format d:',
            'format e:',
            'format f:',
            'format g:',
            'format h:',
            'format i:',
            'format j:',
            'format k:',
            'format l:',
            'format m:',
            'format n:',
            'format o:',
            'format p:',
            'format q:',
            'format r:',
            'format s:',
            'format t:',
            'format u:',
            'format v:',
            'format w:',
            'format x:',
            'format y:',
            'format z:',
        ]
        
        command_lower = command.lower().strip()
        
        # Check for dangerous commands
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            'rm -rf',
            'del /f /s',
            'rd /s',
            'format ',
            'fdisk',
            'mkfs',
            'dd if=',
            'shutdown',
            'reboot',
            'halt',
            'poweroff',
            'init 0',
            'init 6',
        ]
        
        for pattern in suspicious_patterns:
            if pattern in command_lower:
                return False
        
        return True
