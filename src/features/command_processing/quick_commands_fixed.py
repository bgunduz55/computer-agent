"""
Quick Commands Handler - Fixed Version
Handles quick command execution with proper indentation
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QuickCommandType(Enum):
    SYSTEM = "system"
    FILE = "file"
    WEB = "web"
    AI = "ai"

@dataclass
class QuickCommand:
    name: str
    description: str
    command_type: QuickCommandType
    handler: callable
    keywords: List[str]
    parameters: List[str] = None

class QuickCommandsHandler:
    """Handles quick command execution"""
    
    def __init__(self, capability_manager):
        self.capability_manager = capability_manager
        self.commands: Dict[str, QuickCommand] = {}
        self._register_quick_commands()
    
    def _register_quick_commands(self):
        """Register all quick commands"""
        try:
            # System commands
            self.register_command(QuickCommand(
                name="show_system_info",
                description="Show system information",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_system_info,
                keywords=["system", "info", "status", "stats"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="list_files",
                description="List files in current directory",
                command_type=QuickCommandType.FILE,
                handler=self._handle_list_files,
                keywords=["list", "files", "ls", "dir", "show files"],
                parameters=["directory"]
            ))
        
            self.register_command(QuickCommand(
                name="show_processes",
                description="Show running processes",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_show_processes,
                keywords=["processes", "ps", "tasks", "running"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="show_memory",
                description="Show memory usage",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_show_memory,
                keywords=["memory", "ram", "usage"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="show_disk",
                description="Show disk usage",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_show_disk,
                keywords=["disk", "space", "storage"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="show_network",
                description="Show network information",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_show_network,
                keywords=["network", "net", "ip", "connection"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="show_time",
                description="Show current time",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_show_time,
                keywords=["time", "date", "clock"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="show_uptime",
                description="Show system uptime",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_show_uptime,
                keywords=["uptime", "up", "running time"],
                parameters=[]
            ))
        
            # Text input commands - SAFE VERSION (no actual typing)
            self.register_command(QuickCommand(
                name="type_text",
                description="Type text using keyboard (simulation only)",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_type_text_safe,
                keywords=["yaz", "type", "write", "yazı", "metin"],
                parameters=["text"]
            ))
        
            self.register_command(QuickCommand(
                name="generate_and_type",
                description="Generate text with AI and type it (simulation only)",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_generate_and_type_safe,
                keywords=["yaz", "generate", "ai write", "kod yaz", "metin yaz", "hadi kod yazalım", "hadi kod yaz", "kod yazalım"],
                parameters=["prompt"]
            ))
        
            # Keyboard control commands
            self.register_command(QuickCommand(
                name="key_enter",
                description="Press Enter key",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_key_enter,
                keywords=["enter", "gir", "bas", "key enter"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="key_space",
                description="Press Space key",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_key_space,
                keywords=["space", "boşluk", "key space"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="key_tab",
                description="Press Tab key",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_key_tab,
                keywords=["tab", "key tab"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="key_escape",
                description="Press Escape key",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_key_escape,
                keywords=["escape", "esc", "key escape"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="key_backspace",
                description="Press Backspace key",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_key_backspace,
                keywords=["backspace", "sil", "key backspace"],
                parameters=[]
            ))
        
            self.register_command(QuickCommand(
                name="key_arrow",
                description="Press arrow key",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_key_arrow,
                keywords=["arrow", "ok", "up", "down", "left", "right", "key arrow"],
                parameters=["direction"]
            ))
        
        except Exception as e:
            logger.error(f"Failed to register quick commands: {e}")
            raise
    
    def register_command(self, command: QuickCommand):
        """Register a quick command"""
        try:
            self.commands[command.name] = command
            logger.info(f"Registered quick command: {command.name}")
        except Exception as e:
            logger.error(f"Failed to register quick command {command.name}: {e}")
            raise
    
    async def process_command(self, command_text: str) -> Dict[str, Any]:
        """Process a command using quick commands"""
        command_lower = command_text.lower().strip()
        
        # Find matching quick command
        for command in self.commands.values():
            if any(keyword in command_lower for keyword in command.keywords):
                try:
                    result = await command.handler(command_text, {})
                    return {
                        "success": True,
                        "message": result.get("message", "Command executed"),
                        "data": result.get("data", {}),
                        "command_type": "quick",
                        "command_name": command.name
                    }
                except Exception as e:
                    logger.error(f"Error executing quick command {command.name}: {e}")
                    return {
                        "success": False,
                        "message": f"Error executing {command.name}",
                        "error": str(e),
                        "command_type": "quick",
                        "command_name": command.name
                    }
        
        # No quick command found
        return {
            "success": False,
            "message": "No quick command found",
            "command_type": "quick"
        }
    
    # Handler methods
    async def _handle_system_info(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system info command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("system_info", {}, {})
                if result.success:
                    return {"message": "System information retrieved", "data": {"output": result.output}}
                else:
                    return {"message": f"Failed to get system info: {result.error}"}
            else:
                return {"message": "System info capability not available"}
        except Exception as e:
            return {"message": f"Error getting system info: {e}"}
    
    async def _handle_list_files(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list files command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("file_list", {"directory": "."}, {})
                if result.success:
                    return {"message": "Files listed", "data": {"output": result.output}}
                else:
                    return {"message": f"Failed to list files: {result.error}"}
            else:
                return {"message": "File list capability not available"}
        except Exception as e:
            return {"message": f"Error listing files: {e}"}
    
    async def _handle_show_processes(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle show processes command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("terminal_command", {"command": "tasklist" if hasattr(self, '_is_windows') else "ps aux"}, {})
                if result.success:
                    return {"message": "Processes listed", "data": {"output": result.output}}
                else:
                    return {"message": f"Failed to list processes: {result.error}"}
            else:
                return {"message": "Terminal capability not available"}
        except Exception as e:
            return {"message": f"Error listing processes: {e}"}
    
    async def _handle_show_memory(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle show memory command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("terminal_command", {"command": "wmic memorychip get capacity,speed" if hasattr(self, '_is_windows') else "free -h"}, {})
                if result.success:
                    return {"message": "Memory info retrieved", "data": {"output": result.output}}
                else:
                    return {"message": f"Failed to get memory info: {result.error}"}
            else:
                return {"message": "Terminal capability not available"}
        except Exception as e:
            return {"message": f"Error getting memory info: {e}"}
    
    async def _handle_show_disk(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle show disk command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("terminal_command", {"command": "wmic logicaldisk get size,freespace,caption" if hasattr(self, '_is_windows') else "df -h"}, {})
                if result.success:
                    return {"message": "Disk info retrieved", "data": {"output": result.output}}
                else:
                    return {"message": f"Failed to get disk info: {result.error}"}
            else:
                return {"message": "Terminal capability not available"}
        except Exception as e:
            return {"message": f"Error getting disk info: {e}"}
    
    async def _handle_show_network(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle show network command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("terminal_command", {"command": "ipconfig" if hasattr(self, '_is_windows') else "ifconfig"}, {})
                if result.success:
                    return {"message": "Network info retrieved", "data": {"output": result.output}}
                else:
                    return {"message": f"Failed to get network info: {result.error}"}
            else:
                return {"message": "Terminal capability not available"}
        except Exception as e:
            return {"message": f"Error getting network info: {e}"}
    
    async def _handle_show_time(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle show time command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("terminal_command", {"command": "time /t" if hasattr(self, '_is_windows') else "date"}, {})
                if result.success:
                    return {"message": "Time retrieved", "data": {"output": result.output}}
                else:
                    return {"message": f"Failed to get time: {result.error}"}
            else:
                return {"message": "Terminal capability not available"}
        except Exception as e:
            return {"message": f"Error getting time: {e}"}
    
    async def _handle_show_uptime(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle show uptime command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("terminal_command", {"command": "systeminfo | findstr \"System Boot Time\"" if hasattr(self, '_is_windows') else "uptime"}, {})
                if result.success:
                    return {"message": "Uptime retrieved", "data": {"output": result.output}}
                else:
                    return {"message": f"Failed to get uptime: {result.error}"}
            else:
                return {"message": "Terminal capability not available"}
        except Exception as e:
            return {"message": f"Error getting uptime: {e}"}
    
    async def _handle_type_text_safe(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle type text command (safe simulation only)"""
        try:
            # Extract text from command
            words = command.split()
            
            # Find text after "yaz" or "type" keyword
            text_start = 0
            for i, word in enumerate(words):
                if word.lower() in ["yaz", "type", "write", "yazı", "metin"]:
                    text_start = i + 1
                    break
            
            if text_start >= len(words):
                return {"message": "No text provided to type"}
            
            text_to_type = " ".join(words[text_start:])
            
            # Simulate typing (no actual keyboard input)
            return {
                "message": f"Simulated typing: '{text_to_type}' (Safe mode - no actual keyboard input)",
                "data": {"output": f"Would type: {text_to_type}"}
            }
                
        except Exception as e:
            return {"message": f"Error in type text simulation: {e}"}
    
    async def _handle_generate_and_type_safe(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate and type command (safe simulation only)"""
        try:
            # Extract prompt from command
            words = command.lower().split()
            
            # Find prompt after keywords
            prompt_start = 0
            for i, word in enumerate(words):
                if word in ["yaz", "generate", "ai", "kod", "metin"]:
                    prompt_start = i + 1
                    break
            
            if prompt_start >= len(words):
                return {"message": "No prompt provided for text generation"}
            
            prompt = " ".join(words[prompt_start:])
            
            # Simulate AI generation and typing (no actual AI or keyboard input)
            return {
                "message": f"Simulated AI generation and typing: '{prompt}' (Safe mode - no actual AI or keyboard input)",
                "data": {"output": f"Would generate and type: {prompt}"}
            }
                
        except Exception as e:
            return {"message": f"Error in generate and type simulation: {e}"}
    
    # Keyboard handlers
    async def _handle_key_enter(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key enter command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"action": "press_key", "key": "enter"}, {})
                if result.success:
                    return {"message": "Enter key pressed", "data": {"action_performed": result.output}}
                else:
                    return {"message": f"Failed to press Enter: {result.error}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing Enter: {e}"}
    
    async def _handle_key_space(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key space command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"action": "press_key", "key": "space"}, {})
                if result.success:
                    return {"message": "Space key pressed", "data": {"action_performed": result.output}}
                else:
                    return {"message": f"Failed to press Space: {result.error}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing Space: {e}"}
    
    async def _handle_key_tab(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key tab command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"action": "press_key", "key": "tab"}, {})
                if result.success:
                    return {"message": "Tab key pressed", "data": {"action_performed": result.output}}
                else:
                    return {"message": f"Failed to press Tab: {result.error}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing Tab: {e}"}
    
    async def _handle_key_escape(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key escape command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"action": "press_key", "key": "escape"}, {})
                if result.success:
                    return {"message": "Escape key pressed", "data": {"action_performed": result.output}}
                else:
                    return {"message": f"Failed to press Escape: {result.error}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing Escape: {e}"}
    
    async def _handle_key_backspace(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key backspace command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"action": "press_key", "key": "backspace"}, {})
                if result.success:
                    return {"message": "Backspace key pressed", "data": {"action_performed": result.output}}
                else:
                    return {"message": f"Failed to press Backspace: {result.error}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing Backspace: {e}"}
    
    async def _handle_key_arrow(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key arrow command"""
        try:
            # Extract direction from command
            words = command.lower().split()
            direction = "up"  # default
            for word in words:
                if word in ["up", "down", "left", "right"]:
                    direction = word
                    break
            
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"action": "press_key", "key": f"arrow_{direction}"}, {})
                if result.success:
                    return {"message": f"{direction.capitalize()} arrow key pressed", "data": {"action_performed": result.output}}
                else:
                    return {"message": f"Failed to press {direction} arrow: {result.error}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing {direction} arrow: {e}"}
    
    def get_available_commands(self) -> List[Dict[str, Any]]:
        """Get list of available quick commands"""
        return [
            {
                "name": cmd.name,
                "description": cmd.description,
                "keywords": cmd.keywords,
                "type": cmd.command_type.value
            }
            for cmd in self.commands.values()
        ]

# Global quick commands handler instance
_quick_commands_handler = None

def get_quick_commands_handler(capability_manager=None) -> QuickCommandsHandler:
    """Get global quick commands handler instance"""
    global _quick_commands_handler
    if _quick_commands_handler is None and capability_manager:
        _quick_commands_handler = QuickCommandsHandler(capability_manager)
    return _quick_commands_handler
