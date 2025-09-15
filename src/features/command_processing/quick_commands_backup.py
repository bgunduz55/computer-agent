"""
Quick Commands Handler for JARVIS Computer Assistant

Provides fast execution of common commands without AI processing.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QuickCommandType(Enum):
    """Types of quick commands"""
    SYSTEM = "system"
    MEDIA = "media"
    FILE = "file"
    WEB = "web"
    TERMINAL = "terminal"

@dataclass
class QuickCommand:
    """Quick command definition"""
    name: str
    description: str
    command_type: QuickCommandType
    handler: Callable
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
        
        # Text input commands
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
    
    async def _handle_system_info(self, command: str) -> Dict[str, Any]:
        """Handle system info command"""
        result = await self.capability_manager.execute_capability(
            "system_info",
            {"info_type": "all"},
            {}
        )
        
        if result["success"]:
            data = result.get("data", {})
            message = f"System: {data.get('platform', 'Unknown')} {data.get('version', '')}"
            return {"message": message, "data": data}
        else:
            return {"message": f"Failed to get system info: {result.get('error', 'Unknown error')}"}
    
    async def _handle_list_files(self, command: str) -> Dict[str, Any]:
        """Handle list files command"""
        # Extract directory from command if specified
        words = command.split()
        directory = "."
        for i, word in enumerate(words):
            if word.lower() in ["in", "from", "at"] and i + 1 < len(words):
                directory = words[i + 1]
                break
        
        result = await self.capability_manager.execute_capability(
            "terminal_command",
            {"command": f"ls -la {directory}"},
            {}
        )
        
        if result["success"]:
            return {"message": f"Files in {directory}", "data": {"output": result.get("output", "")}}
        else:
            return {"message": f"Failed to list files: {result.get('error', 'Unknown error')}"}
    
    async def _handle_show_processes(self, command: str) -> Dict[str, Any]:
        """Handle show processes command"""
        result = await self.capability_manager.execute_capability(
            "terminal_command",
            {"command": "ps aux | head -20"},
            {}
        )
        
        if result["success"]:
            return {"message": "Running processes", "data": {"output": result.get("output", "")}}
        else:
            return {"message": f"Failed to show processes: {result.get('error', 'Unknown error')}"}
    
    async def _handle_show_memory(self, command: str) -> Dict[str, Any]:
        """Handle show memory command"""
        result = await self.capability_manager.execute_capability(
            "terminal_command",
            {"command": "free -h"},
            {}
        )
        
        if result["success"]:
            return {"message": "Memory usage", "data": {"output": result.get("output", "")}}
        else:
            return {"message": f"Failed to show memory: {result.get('error', 'Unknown error')}"}
    
    async def _handle_show_disk(self, command: str) -> Dict[str, Any]:
        """Handle show disk command"""
        result = await self.capability_manager.execute_capability(
            "terminal_command",
            {"command": "df -h"},
            {}
        )
        
        if result["success"]:
            return {"message": "Disk usage", "data": {"output": result.get("output", "")}}
        else:
            return {"message": f"Failed to show disk usage: {result.get('error', 'Unknown error')}"}
    
    async def _handle_show_network(self, command: str) -> Dict[str, Any]:
        """Handle show network command"""
        result = await self.capability_manager.execute_capability(
            "terminal_command",
            {"command": "ip addr show"},
            {}
        )
        
        if result["success"]:
            return {"message": "Network information", "data": {"output": result.get("output", "")}}
        else:
            return {"message": f"Failed to show network info: {result.get('error', 'Unknown error')}"}
    
    async def _handle_show_time(self, command: str) -> Dict[str, Any]:
        """Handle show time command"""
        result = await self.capability_manager.execute_capability(
            "terminal_command",
            {"command": "date"},
            {}
        )
        
        if result["success"]:
            return {"message": "Current time", "data": {"output": result.get("output", "")}}
        else:
            return {"message": f"Failed to show time: {result.get('error', 'Unknown error')}"}
    
    async def _handle_show_uptime(self, command: str) -> Dict[str, Any]:
        """Handle show uptime command"""
        result = await self.capability_manager.execute_capability(
            "terminal_command",
            {"command": "uptime"},
            {}
        )
        
        if result["success"]:
            return {"message": "System uptime", "data": {"output": result.get("output", "")}}
        else:
            return {"message": f"Failed to show uptime: {result.get('error', 'Unknown error')}"}
    
    async def _handle_type_text(self, command: str) -> Dict[str, Any]:
        """Handle type text command"""
        # Extract text from command
        words = command.split()
        if len(words) < 2:
            return {"message": "No text provided to type"}
        
        # Find text after "yaz" or "type" keyword
        text_start = 0
        for i, word in enumerate(words):
            if word.lower() in ["yaz", "type", "write", "yazı", "metin"]:
                text_start = i + 1
                break
        
        if text_start >= len(words):
            return {"message": "No text provided to type"}
        
        text_to_type = " ".join(words[text_start:])
        
        result = await self.capability_manager.execute_capability(
            "text_input",
            {"text": text_to_type},
            {}
        )
        
        if result["success"]:
            return {"message": f"Typed: {text_to_type}", "data": {"text_entered": result.get("text_entered", "")}}
        else:
            return {"message": f"Failed to type text: {result.get('error', 'Unknown error')}"}
    
    async def _handle_generate_and_type(self, command: str) -> Dict[str, Any]:
        """Handle generate and type command"""
        # Extract prompt from command
        words = command.split()
        if len(words) < 2:
            return {"message": "No prompt provided for generation"}
        
        # Find prompt after keywords
        prompt_start = 0
        for i, word in enumerate(words):
            if word.lower() in ["yaz", "generate", "kod", "metin", "hadi"]:
                prompt_start = i + 1
                break
        
        if prompt_start >= len(words):
            return {"message": "No prompt provided for generation"}
        
        prompt = " ".join(words[prompt_start:])
        
        # Eğer prompt boşsa, varsayılan kod üretme promptu kullan
        if not prompt.strip():
            prompt = "Write a simple Python function that demonstrates basic programming concepts"
        
        result = await self.capability_manager.execute_capability(
            "generate_and_type",
            {"prompt": prompt},
            {}
        )
        
        if result["success"]:
            return {"message": f"Generated and typed: {prompt}", "data": {"text_entered": result.get("text_entered", "")}}
        else:
            return {"message": f"Failed to generate and type: {result.get('error', 'Unknown error')}"}
    
    async def _handle_key_enter(self, command: str) -> Dict[str, Any]:
        """Handle key enter command"""
        result = await self.capability_manager.execute_capability(
            "keyboard_control",
            {"key": "enter", "action": "tap"},
            {}
        )
        
        if result["success"]:
            return {"message": "Enter key pressed", "data": {"action_performed": result.get("action_performed", "")}}
        else:
            return {"message": f"Failed to press Enter: {result.get('error', 'Unknown error')}"}
    
    async def _handle_key_space(self, command: str) -> Dict[str, Any]:
        """Handle key space command"""
        result = await self.capability_manager.execute_capability(
            "keyboard_control",
            {"key": "space", "action": "tap"},
            {}
        )
        
        if result["success"]:
            return {"message": "Space key pressed", "data": {"action_performed": result.get("action_performed", "")}}
        else:
            return {"message": f"Failed to press Space: {result.get('error', 'Unknown error')}"}
    
    async def _handle_key_tab(self, command: str) -> Dict[str, Any]:
        """Handle key tab command"""
        result = await self.capability_manager.execute_capability(
            "keyboard_control",
            {"key": "tab", "action": "tap"},
            {}
        )
        
        if result["success"]:
            return {"message": "Tab key pressed", "data": {"action_performed": result.get("action_performed", "")}}
        else:
            return {"message": f"Failed to press Tab: {result.get('error', 'Unknown error')}"}
    
    async def _handle_key_escape(self, command: str) -> Dict[str, Any]:
        """Handle key escape command"""
        result = await self.capability_manager.execute_capability(
            "keyboard_control",
            {"key": "escape", "action": "tap"},
            {}
        )
        
        if result["success"]:
            return {"message": "Escape key pressed", "data": {"action_performed": result.get("action_performed", "")}}
        else:
            return {"message": f"Failed to press Escape: {result.get('error', 'Unknown error')}"}
    
    async def _handle_key_backspace(self, command: str) -> Dict[str, Any]:
        """Handle key backspace command"""
        result = await self.capability_manager.execute_capability(
            "keyboard_control",
            {"key": "backspace", "action": "tap"},
            {}
        )
        
        if result["success"]:
            return {"message": "Backspace key pressed", "data": {"action_performed": result.get("action_performed", "")}}
        else:
            return {"message": f"Failed to press Backspace: {result.get('error', 'Unknown error')}"}
    
    async def _handle_key_arrow(self, command: str) -> Dict[str, Any]:
        """Handle key arrow command"""
        # Extract direction from command
        words = command.split()
        direction = "up"  # default
        
        for word in words:
            if word.lower() in ["up", "yukarı", "yukari"]:
                direction = "up"
                break
            elif word.lower() in ["down", "aşağı", "asagi"]:
                direction = "down"
                break
            elif word.lower() in ["left", "sol"]:
                direction = "left"
                break
            elif word.lower() in ["right", "sağ", "sag"]:
                direction = "right"
                break
        
        result = await self.capability_manager.execute_capability(
            "keyboard_control",
            {"key": direction, "action": "tap"},
            {}
        )
        
        if result["success"]:
            return {"message": f"{direction.capitalize()} arrow key pressed", "data": {"action_performed": result.get("action_performed", "")}}
        else:
            return {"message": f"Failed to press {direction} arrow: {result.get('error', 'Unknown error')}"}
    
    
    async def _handle_generate_and_type(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate and type command"""
        try:
            # Extract prompt from command
            prompt = command.replace("yaz", "").replace("generate", "").replace("ai write", "").replace("kod yaz", "").replace("metin yaz", "").replace("hadi kod yazalım", "").replace("hadi kod yaz", "").replace("kod yazalım", "").strip()
            if not prompt:
                prompt = "Write some code"
            
            # Use AI to generate text
            if self.capability_manager:
                # First generate text with AI
                ai_result = await self.capability_manager.execute_capability(
                    "ai_generation", 
                    {"prompt": prompt, "max_length": 500},
                    {}
                )
                
                if ai_result.get("success"):
                    generated_text = ai_result.get("output", "")
                    
                    # Then type the generated text
                    type_result = await self.capability_manager.execute_capability(
                        "text_input", 
                        {"text": generated_text, "method": "type_text"},
                        {}
                    )
                    
                    if type_result.get("success"):
                        return {
                            "message": f"Generated and typed: '{generated_text[:100]}{'...' if len(generated_text) > 100 else ''}'",
                            "data": {"output": generated_text}
                        }
                    else:
                        return {"message": f"Generated text but failed to type: {type_result.get('error', 'Unknown error')}"}
                else:
                    return {"message": f"Failed to generate text: {ai_result.get('error', 'Unknown error')}"}
            else:
                return {"message": "AI generation capability not available"}
                
        except Exception as e:
            logger.error(f"Error in generate and type handler: {e}")
            return {"message": f"Error generating and typing: {str(e)}"}
    
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
