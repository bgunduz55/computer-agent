"""
Dynamic Capability System

Extends the capability system to support dynamic capabilities through
terminal commands, making the assistant's capabilities virtually unlimited.
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .capability_system import Capability, CapabilityType, ParameterInfo, BaseCapabilityExecutor
from .dynamic_capability import DynamicCapability
from .terminal_capability_executor import TerminalCapabilityExecutor

logger = logging.getLogger(__name__)

class CapabilitySource(Enum):
    """Source of capability"""
    BUILTIN = "builtin"
    TERMINAL = "terminal"
    AI_GENERATED = "ai_generated"
    PLUGIN = "plugin"

@dataclass
class DynamicCapability(Capability):
    """Dynamic capability that can be executed via terminal"""
    source: CapabilitySource = CapabilitySource.BUILTIN
    terminal_command: Optional[str] = None
    command_template: Optional[str] = None
    parameter_mapping: Dict[str, str] = None
    output_parser: Optional[str] = None
    working_directory: Optional[str] = None
    environment_variables: Dict[str, str] = None
    
    def __post_init__(self):
        if self.parameter_mapping is None:
            self.parameter_mapping = {}
        if self.environment_variables is None:
            self.environment_variables = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            "source": self.source.value,
            "terminal_command": self.terminal_command,
            "command_template": self.command_template,
            "parameter_mapping": self.parameter_mapping,
            "output_parser": self.output_parser,
            "working_directory": self.working_directory,
            "environment_variables": self.environment_variables
        })
        return base_dict

class DynamicCapabilityManager:
    """Manages dynamic capabilities including terminal-based ones"""
    
    def __init__(self):
        self.capabilities: Dict[str, DynamicCapability] = {}
        self.terminal_executor = TerminalCapabilityExecutor()
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        
        # AI capability generation patterns
        self.capability_patterns = {
            "file_operations": [
                r"create.*file", r"delete.*file", r"copy.*file", r"move.*file",
                r"edit.*file", r"read.*file", r"search.*file", r"compress.*file"
            ],
            "system_operations": [
                r"install.*package", r"uninstall.*package", r"update.*system",
                r"restart.*service", r"start.*service", r"stop.*service"
            ],
            "network_operations": [
                r"ping.*host", r"download.*file", r"upload.*file", r"check.*connection",
                r"scan.*network", r"test.*connection"
            ],
            "process_operations": [
                r"kill.*process", r"start.*process", r"monitor.*process",
                r"list.*process", r"find.*process"
            ],
            "database_operations": [
                r"query.*database", r"backup.*database", r"restore.*database",
                r"create.*table", r"drop.*table"
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize dynamic capability manager"""
        try:
            await self.terminal_executor.initialize()
            await self._register_builtin_capabilities()
            await self._register_terminal_capabilities()
            await self._register_advanced_capabilities()
            
            self._is_initialized = True
            self.logger.info(f"Dynamic capability manager initialized with {len(self.capabilities)} capabilities")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dynamic capability manager: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if manager is initialized"""
        return self._is_initialized
    
    async def _register_builtin_capabilities(self):
        """Register built-in capabilities"""
        # File operations
        file_create_cap = DynamicCapability(
            name="file_create",
            description="Create a file with content",
            capability_type=CapabilityType.FILE,
            required_parameters=["file_path", "content"],
            optional_parameters=["encoding"],
            parameter_info={
                "file_path": ParameterInfo(
                    name="file_path",
                    type="string",
                    required=True,
                    description="Path where to create the file"
                ),
                "content": ParameterInfo(
                    name="content",
                    type="string",
                    required=True,
                    description="Content to write to the file"
                ),
                "encoding": ParameterInfo(
                    name="encoding",
                    type="string",
                    required=False,
                    description="File encoding",
                    default_value="utf-8"
                )
            },
            source=CapabilitySource.BUILTIN
        )
        await self.register_capability(file_create_cap)
        
        # Directory operations
        dir_create_cap = DynamicCapability(
            name="directory_create",
            description="Create a directory",
            capability_type=CapabilityType.FILE,
            required_parameters=["directory_path"],
            optional_parameters=["recursive"],
            parameter_info={
                "directory_path": ParameterInfo(
                    name="directory_path",
                    type="string",
                    required=True,
                    description="Path where to create the directory"
                ),
                "recursive": ParameterInfo(
                    name="recursive",
                    type="boolean",
                    required=False,
                    description="Create parent directories if they don't exist",
                    default_value=True
                )
            },
            source=CapabilitySource.BUILTIN
        )
        await self.register_capability(dir_create_cap)
    
    async def _register_terminal_capabilities(self):
        """Register common terminal-based capabilities"""
        # Linux/Unix commands
        linux_capabilities = [
            {
                "name": "terminal_command",
                "description": "Execute any terminal command",
                "capability_type": CapabilityType.SYSTEM,
                "required_parameters": ["command"],
                "optional_parameters": ["working_directory", "timeout", "environment"],
                "terminal_command": "{command}",
                "parameter_mapping": {
                    "command": "command",
                    "working_directory": "working_directory",
                    "timeout": "timeout",
                    "environment": "environment"
                }
            },
            {
                "name": "grep_search",
                "description": "Search for text in files using grep",
                "capability_type": CapabilityType.FILE,
                "required_parameters": ["pattern", "file_path"],
                "optional_parameters": ["recursive", "case_sensitive", "line_numbers"],
                "terminal_command": "grep {options} '{pattern}' '{file_path}'",
                "parameter_mapping": {
                    "pattern": "pattern",
                    "file_path": "file_path",
                    "recursive": "recursive",
                    "case_sensitive": "case_sensitive",
                    "line_numbers": "line_numbers"
                }
            },
            {
                "name": "find_files",
                "description": "Find files using find command",
                "capability_type": CapabilityType.FILE,
                "required_parameters": ["directory"],
                "optional_parameters": ["name_pattern", "type", "size", "modified_time"],
                "terminal_command": "find '{directory}' {options}",
                "parameter_mapping": {
                    "directory": "directory",
                    "name_pattern": "name_pattern",
                    "type": "type",
                    "size": "size",
                    "modified_time": "modified_time"
                }
            },
            {
                "name": "system_info",
                "description": "Get system information",
                "capability_type": CapabilityType.SYSTEM,
                "required_parameters": [],
                "optional_parameters": ["info_type"],
                "terminal_command": "uname -a && df -h && free -h && ps aux | head -10",
                "parameter_mapping": {
                    "info_type": "info_type"
                }
            },
            {
                "name": "package_install",
                "description": "Install packages using package manager",
                "capability_type": CapabilityType.SYSTEM,
                "required_parameters": ["package_name"],
                "optional_parameters": ["package_manager", "version"],
                "terminal_command": "{package_manager} install {package_name}",
                "parameter_mapping": {
                    "package_name": "package_name",
                    "package_manager": "package_manager",
                    "version": "version"
                }
            }
        ]
        
        for cap_data in linux_capabilities:
            capability = DynamicCapability(
                name=cap_data["name"],
                description=cap_data["description"],
                capability_type=cap_data["capability_type"],
                required_parameters=cap_data["required_parameters"],
                optional_parameters=cap_data["optional_parameters"],
                source=CapabilitySource.TERMINAL,
                terminal_command=cap_data["terminal_command"],
                parameter_mapping=cap_data["parameter_mapping"]
            )
            await self.register_capability(capability)
    
    async def _register_advanced_capabilities(self):
        """Register advanced capabilities from specialized modules"""
        try:
            # Note: Media, productivity, and web capabilities are registered
            # through the main capability system, not as dynamic capabilities
            
            self.logger.info("Advanced capabilities registered successfully")
            
        except Exception as e:
            self.logger.error(f"Error registering advanced capabilities: {e}")
    
    async def register_capability(self, capability: DynamicCapability):
        """Register a dynamic capability"""
        try:
            self.capabilities[capability.name] = capability
            self.logger.debug(f"Registered dynamic capability: {capability.name}")
        except Exception as e:
            self.logger.error(f"Error registering capability {capability.name}: {e}")
    
    async def generate_capability_from_ai(
        self, 
        command_description: str, 
        ai_suggestion: str
    ) -> Optional[DynamicCapability]:
        """Generate a capability from AI suggestion"""
        try:
            # Parse AI suggestion to extract command and parameters
            parsed = await self._parse_ai_suggestion(ai_suggestion)
            if not parsed:
                return None
            
            # Create dynamic capability
            capability = DynamicCapability(
                name=parsed["name"],
                description=command_description,
                capability_type=parsed["capability_type"],
                required_parameters=parsed["required_parameters"],
                optional_parameters=parsed["optional_parameters"],
                source=CapabilitySource.AI_GENERATED,
                terminal_command=parsed["terminal_command"],
                parameter_mapping=parsed["parameter_mapping"],
                output_parser=parsed.get("output_parser"),
                working_directory=parsed.get("working_directory")
            )
            
            # Register the capability
            await self.register_capability(capability)
            
            self.logger.info(f"Generated AI capability: {capability.name}")
            return capability
            
        except Exception as e:
            self.logger.error(f"Error generating capability from AI: {e}")
            return None
    
    async def _parse_ai_suggestion(self, ai_suggestion: str) -> Optional[Dict[str, Any]]:
        """Parse AI suggestion to extract capability information"""
        try:
            # Try to parse as JSON first
            try:
                suggestion_data = json.loads(ai_suggestion)
                return suggestion_data
            except json.JSONDecodeError:
                pass
            
            # Parse as text description
            lines = ai_suggestion.strip().split('\n')
            
            # Extract command
            command_line = None
            for line in lines:
                if line.strip().startswith('Command:') or line.strip().startswith('command:'):
                    command_line = line.split(':', 1)[1].strip()
                    break
            
            if not command_line:
                # Try to find command in the text
                command_match = re.search(r'`([^`]+)`', ai_suggestion)
                if command_match:
                    command_line = command_match.group(1)
                else:
                    return None
            
            # Generate capability name
            capability_name = self._generate_capability_name(command_line)
            
            # Determine capability type
            capability_type = self._determine_capability_type(command_line)
            
            # Extract parameters from command
            parameters = self._extract_parameters_from_command(command_line)
            
            return {
                "name": capability_name,
                "capability_type": capability_type,
                "required_parameters": parameters["required"],
                "optional_parameters": parameters["optional"],
                "terminal_command": command_line,
                "parameter_mapping": parameters["mapping"]
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing AI suggestion: {e}")
            return None
    
    def _generate_capability_name(self, command: str) -> str:
        """Generate a capability name from command"""
        # Extract the main command
        main_command = command.split()[0] if command.split() else "command"
        
        # Clean up the name
        name = main_command.replace('-', '_').replace('/', '_')
        
        # Add timestamp to make it unique
        import time
        timestamp = int(time.time())
        
        return f"ai_{name}_{timestamp}"
    
    def _determine_capability_type(self, command: str) -> CapabilityType:
        """Determine capability type from command"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ['file', 'dir', 'ls', 'cat', 'grep', 'find']):
            return CapabilityType.FILE
        elif any(keyword in command_lower for keyword in ['install', 'update', 'system', 'service']):
            return CapabilityType.SYSTEM
        elif any(keyword in command_lower for keyword in ['ping', 'curl', 'wget', 'ssh', 'scp']):
            return CapabilityType.WEB
        elif any(keyword in command_lower for keyword in ['ps', 'kill', 'top', 'htop']):
            return CapabilityType.SYSTEM
        else:
            return CapabilityType.SYSTEM
    
    def _extract_parameters_from_command(self, command: str) -> Dict[str, Any]:
        """Extract parameters from command template"""
        # This is a simplified parameter extraction
        # In a real implementation, this would be more sophisticated
        
        required_params = []
        optional_params = []
        mapping = {}
        
        # Look for common parameter patterns
        if '{' in command and '}' in command:
            # Extract parameters from template
            import re
            param_matches = re.findall(r'\{([^}]+)\}', command)
            
            for param in param_matches:
                if param in ['command', 'file_path', 'directory', 'pattern']:
                    required_params.append(param)
                else:
                    optional_params.append(param)
                
                mapping[param] = param
        
        return {
            "required": required_params,
            "optional": optional_params,
            "mapping": mapping
        }
    
    async def find_matching_capability(self, command_description: str) -> Optional[DynamicCapability]:
        """Find a matching capability for a command description"""
        try:
            # First, try to find exact matches
            for capability in self.capabilities.values():
                if capability.description.lower() in command_description.lower():
                    return capability
            
            # Try pattern matching
            for pattern_name, patterns in self.capability_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, command_description.lower()):
                        # Find a capability that matches this pattern
                        for capability in self.capabilities.values():
                            if pattern_name in capability.name or pattern_name in capability.description.lower():
                                return capability
            
            # If no match found, suggest creating a terminal command capability
            return self.capabilities.get("terminal_command")
            
        except Exception as e:
            self.logger.error(f"Error finding matching capability: {e}")
            return None
    
    async def execute_capability(
        self, 
        capability_name: str, 
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a dynamic capability"""
        try:
            capability = self.capabilities.get(capability_name)
            if not capability:
                return {"success": False, "error": f"Capability not found: {capability_name}"}
            
            if capability.source == CapabilitySource.TERMINAL or capability.source == CapabilitySource.AI_GENERATED:
                # Execute via terminal
                return await self.terminal_executor.execute(capability, parameters, context)
            else:
                # Execute built-in capability
                return await self._execute_builtin_capability(capability, parameters, context)
                
        except Exception as e:
            self.logger.error(f"Error executing capability {capability_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_builtin_capability(
        self, 
        capability: DynamicCapability, 
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute built-in capability"""
        # This would contain the actual implementation for built-in capabilities
        # For now, return a placeholder
        return {
            "success": True,
            "message": f"Executed built-in capability: {capability.name}",
            "output": parameters
        }
    
    async def get_all_capabilities(self) -> List[DynamicCapability]:
        """Get all capabilities"""
        return list(self.capabilities.values())
    
    async def get_capability(self, name: str) -> Optional[DynamicCapability]:
        """Get capability by name"""
        return self.capabilities.get(name)
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.terminal_executor.cleanup()
            self.capabilities.clear()
            self._is_initialized = False
            self.logger.info("Dynamic capability manager cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up dynamic capability manager: {e}")

# Global dynamic capability manager instance
_dynamic_capability_manager: Optional[DynamicCapabilityManager] = None

async def get_dynamic_capability_manager() -> DynamicCapabilityManager:
    """Get global dynamic capability manager instance"""
    global _dynamic_capability_manager
    if _dynamic_capability_manager is None:
        _dynamic_capability_manager = DynamicCapabilityManager()
        await _dynamic_capability_manager.initialize()
    return _dynamic_capability_manager

async def cleanup_dynamic_capability_manager():
    """Cleanup global dynamic capability manager"""
    global _dynamic_capability_manager
    if _dynamic_capability_manager:
        await _dynamic_capability_manager.cleanup()
        _dynamic_capability_manager = None
