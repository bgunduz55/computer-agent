"""
Terminal Capability Executor

Executes capabilities through terminal commands, enabling unlimited
functionality through command-line interfaces.
"""

import asyncio
import logging
import subprocess
import shlex
import os
import tempfile
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .dynamic_capability import DynamicCapability

logger = logging.getLogger(__name__)

class ExecutionResult(Enum):
    """Execution result status"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class TerminalExecutionResult:
    """Result of terminal execution"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    command: str
    error: Optional[str] = None
    parsed_output: Optional[Dict[str, Any]] = None

class TerminalCapabilityExecutor:
    """Executes capabilities through terminal commands"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.default_timeout = 30  # seconds
        self.max_timeout = 300  # 5 minutes
        
        # Security settings
        self.dangerous_commands = [
            'rm -rf', 'del /f', 'format', 'fdisk', 'mkfs', 'dd if=', 'shutdown', 'reboot',
            'halt', 'poweroff', 'init 0', 'init 6', 'systemctl poweroff', 'systemctl reboot'
        ]
        self.allowed_commands = [
            'ls', 'cat', 'grep', 'find', 'ps', 'top', 'df', 'free', 'uname', 'whoami',
            'curl', 'wget', 'ssh', 'scp', 'rsync', 'tar', 'zip', 'unzip', 'git',
            'docker', 'kubectl', 'aws', 'gcloud', 'terraform', 'echo', 'date', 'uptime'
        ]
        self.max_command_length = 1000
        self.require_confirmation = True
    
    async def initialize(self) -> bool:
        """Initialize terminal executor"""
        try:
            # Test if terminal is available
            await self._test_terminal_availability()
            
            self._is_initialized = True
            self.logger.info("Terminal capability executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize terminal executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, capability_name: str, parameters: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return capability_name == "terminal_command" and "command" in parameters
    
    async def _test_terminal_availability(self):
        """Test if terminal commands are available"""
        try:
            # Test basic command execution
            result = await self._execute_command("echo 'test'", timeout=5)
            if not result.success:
                raise Exception("Terminal not available")
        except Exception as e:
            raise Exception(f"Terminal availability test failed: {e}")
    
    async def execute(
        self, 
        capability: DynamicCapability, 
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a terminal capability"""
        if not self._is_initialized:
            return {"success": False, "error": "Terminal executor not initialized"}
        
        try:
            # Build command from template
            command = await self._build_command(capability, parameters)
            
            # Security validation
            security_check = await self._validate_command_security(command, context)
            if not security_check["safe"]:
                return {
                    "success": False,
                    "error": f"Command blocked by security policy: {security_check['reason']}",
                    "command": command,
                    "execution_time": 0.0
                }
            
            # Set working directory
            working_dir = capability.working_directory or context.get('working_directory', os.getcwd())
            
            # Set environment variables
            env_vars = {**os.environ, **capability.environment_variables, **context.get('environment', {})}
            
            # Get timeout
            timeout = parameters.get('timeout', self.default_timeout)
            timeout = min(timeout, self.max_timeout)
            
            # Execute command
            result = await self._execute_command(
                command, 
                working_directory=working_dir,
                environment=env_vars,
                timeout=timeout
            )
            
            # Parse output if parser is defined
            parsed_output = None
            if capability.output_parser and result.success:
                parsed_output = await self._parse_output(result.stdout, capability.output_parser)
            
            # Return result
            return {
                "success": result.success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.return_code,
                "execution_time": result.execution_time,
                "command": result.command,
                "error": result.error,
                "parsed_output": parsed_output
            }
            
        except Exception as e:
            self.logger.error(f"Error executing terminal capability {capability.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": capability.terminal_command or "",
                "execution_time": 0.0
            }
    
    async def _build_command(self, capability: DynamicCapability, parameters: Dict[str, Any]) -> str:
        """Build command from template and parameters"""
        try:
            if not capability.terminal_command:
                raise Exception("No terminal command defined for capability")
            
            command = capability.terminal_command
            
            # Substitute parameters
            for param_name, param_value in parameters.items():
                if param_name in capability.parameter_mapping:
                    template_param = capability.parameter_mapping[param_name]
                    
                    # Handle different parameter types
                    if isinstance(param_value, bool):
                        # Boolean parameters might be used as flags
                        if param_value and template_param.startswith('--'):
                            command = command.replace(f"{{{template_param}}}", template_param)
                        else:
                            command = command.replace(f"{{{template_param}}}", "")
                    elif isinstance(param_value, list):
                        # List parameters - join with spaces
                        value_str = " ".join(str(v) for v in param_value)
                        command = command.replace(f"{{{template_param}}}", value_str)
                    else:
                        # String parameters - escape for shell
                        escaped_value = shlex.quote(str(param_value))
                        command = command.replace(f"{{{template_param}}}", escaped_value)
            
            # Handle special options
            command = await self._apply_special_options(command, parameters)
            
            return command
            
        except Exception as e:
            self.logger.error(f"Error building command: {e}")
            raise
    
    async def _apply_special_options(self, command: str, parameters: Dict[str, Any]) -> str:
        """Apply special options to command"""
        try:
            # Handle recursive flag
            if parameters.get('recursive', False):
                if 'find' in command:
                    command = command.replace('find ', 'find ')
                elif 'grep' in command:
                    command = command.replace('grep ', 'grep -r ')
            
            # Handle case sensitivity
            if not parameters.get('case_sensitive', True):
                if 'grep' in command:
                    command = command.replace('grep ', 'grep -i ')
            
            # Handle line numbers
            if parameters.get('line_numbers', False):
                if 'grep' in command:
                    command = command.replace('grep ', 'grep -n ')
            
            # Handle file type
            if 'type' in parameters:
                file_type = parameters['type']
                if 'find' in command:
                    if file_type == 'file':
                        command += " -type f"
                    elif file_type == 'directory':
                        command += " -type d"
            
            # Handle size filter
            if 'size' in parameters:
                size = parameters['size']
                if 'find' in command:
                    command += f" -size {size}"
            
            return command
            
        except Exception as e:
            self.logger.error(f"Error applying special options: {e}")
            return command
    
    async def _execute_command(
        self, 
        command: str, 
        working_directory: str = None,
        environment: Dict[str, str] = None,
        timeout: int = None
    ) -> TerminalExecutionResult:
        """Execute a terminal command"""
        import time
        start_time = time.time()
        
        try:
            self.logger.info(f"Executing command: {command}")
            
            # Prepare environment
            env = environment or os.environ.copy()
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_directory,
                env=env
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout or self.default_timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                execution_time = time.time() - start_time
                
                return TerminalExecutionResult(
                    success=False,
                    stdout="",
                    stderr=f"Command timed out after {timeout} seconds",
                    return_code=-1,
                    execution_time=execution_time,
                    command=command,
                    error="Timeout"
                )
            
            execution_time = time.time() - start_time
            
            # Decode output
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')
            
            # Determine success
            success = process.returncode == 0
            
            return TerminalExecutionResult(
                success=success,
                stdout=stdout_str,
                stderr=stderr_str,
                return_code=process.returncode,
                execution_time=execution_time,
                command=command,
                error=stderr_str if not success else None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Error executing command '{command}': {e}")
            
            return TerminalExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                command=command,
                error=str(e)
            )
    
    async def _parse_output(self, output: str, parser_type: str) -> Optional[Dict[str, Any]]:
        """Parse command output based on parser type"""
        try:
            if parser_type == "json":
                return json.loads(output)
            elif parser_type == "lines":
                return {"lines": output.strip().split('\n')}
            elif parser_type == "table":
                lines = output.strip().split('\n')
                if len(lines) < 2:
                    return {"table": []}
                
                # Simple table parsing
                headers = lines[0].split()
                rows = []
                for line in lines[1:]:
                    if line.strip():
                        values = line.split()
                        if len(values) == len(headers):
                            rows.append(dict(zip(headers, values)))
                
                return {"table": rows}
            elif parser_type == "key_value":
                result = {}
                for line in output.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        result[key.strip()] = value.strip()
                return result
            else:
                return {"raw_output": output}
                
        except Exception as e:
            self.logger.error(f"Error parsing output: {e}")
            return {"raw_output": output, "parse_error": str(e)}
    
    async def test_command(self, command: str, timeout: int = 10) -> bool:
        """Test if a command is available"""
        try:
            result = await self._execute_command(f"which {command}", timeout=timeout)
            return result.success and result.return_code == 0
        except Exception:
            return False
    
    async def get_available_commands(self) -> List[str]:
        """Get list of available commands"""
        try:
            # Get common commands
            common_commands = [
                'ls', 'cat', 'grep', 'find', 'ps', 'top', 'df', 'free', 'uname',
                'curl', 'wget', 'ssh', 'scp', 'rsync', 'tar', 'zip', 'unzip',
                'git', 'docker', 'kubectl', 'aws', 'gcloud', 'terraform'
            ]
            
            available = []
            for cmd in common_commands:
                if await self.test_command(cmd):
                    available.append(cmd)
            
            return available
            
        except Exception as e:
            self.logger.error(f"Error getting available commands: {e}")
            return []
    
    async def _validate_command_security(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate command security"""
        try:
            # Check command length
            if len(command) > self.max_command_length:
                return {
                    "safe": False,
                    "reason": f"Command too long (max {self.max_command_length} characters)"
                }
            
            # Check for dangerous commands
            command_lower = command.lower()
            for dangerous_cmd in self.dangerous_commands:
                if dangerous_cmd.lower() in command_lower:
                    return {
                        "safe": False,
                        "reason": f"Dangerous command detected: {dangerous_cmd}"
                    }
            
            # Check for command injection attempts
            dangerous_patterns = [';', '&&', '||', '|', '`', '$', '$(', '${', '>', '>>', '<', '<<']
            for pattern in dangerous_patterns:
                if pattern in command and not self._is_safe_pattern_usage(command, pattern):
                    return {
                        "safe": False,
                        "reason": f"Potentially dangerous pattern detected: {pattern}"
                    }
            
            # Check if command is in allowed list (if strict mode)
            if hasattr(self, 'strict_mode') and self.strict_mode:
                command_base = command.split()[0] if command.split() else ""
                if command_base not in self.allowed_commands:
                    return {
                        "safe": False,
                        "reason": f"Command not in allowed list: {command_base}"
                    }
            
            # Check for user confirmation if required
            if self.require_confirmation and not context.get('user_confirmed', False):
                return {
                    "safe": False,
                    "reason": "User confirmation required for terminal commands"
                }
            
            return {"safe": True, "reason": "Command passed security validation"}
            
        except Exception as e:
            self.logger.error(f"Error validating command security: {e}")
            return {
                "safe": False,
                "reason": f"Security validation error: {e}"
            }
    
    def _is_safe_pattern_usage(self, command: str, pattern: str) -> bool:
        """Check if pattern usage is safe"""
        try:
            # Allow certain safe usages
            safe_usages = {
                ';': ['echo "test"; echo "done"'],
                '|': ['ps aux | grep python', 'ls -la | head -10'],
                '>': ['echo "test" > file.txt'],
                '>>': ['echo "test" >> file.txt']
            }
            
            if pattern in safe_usages:
                for safe_usage in safe_usages[pattern]:
                    if safe_usage in command:
                        return True
            
            # Check for quotes around potentially dangerous parts
            if pattern in [';', '&&', '||']:
                # If the pattern is inside quotes, it's likely safe
                import re
                quoted_sections = re.findall(r'"[^"]*"', command)
                for quoted in quoted_sections:
                    if pattern in quoted:
                        return True
            
            return False
            
        except Exception:
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            self._is_initialized = False
            self.logger.info("Terminal capability executor cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up terminal executor: {e}")
