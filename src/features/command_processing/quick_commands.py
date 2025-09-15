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
        
            # Text input commands - REAL VERSION (actual typing)
            self.register_command(QuickCommand(
                name="type_text",
                description="Type text using keyboard",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_type_text_real,
                keywords=["yaz", "type", "write", "yazı", "metin"],
                parameters=["text"]
            ))
        
            self.register_command(QuickCommand(
                name="generate_and_type",
                description="Generate text with AI and type it",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_generate_and_type_real,
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
            
            # General key command - handles any key
            self.register_command(QuickCommand(
                name="key_any",
                description="Press any key",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_key_any,
                keywords=["key", "tuş", "bas", "press"],
                parameters=["key_name"]
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
            
            # System control commands
            self.register_command(QuickCommand(
                name="shutdown",
                description="Shutdown computer",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_shutdown,
                keywords=["shutdown", "kapat", "kapatma", "kapatma"],
                parameters=[]
            ))
            
            self.register_command(QuickCommand(
                name="restart",
                description="Restart computer",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_restart,
                keywords=["restart", "yeniden", "reboot", "yeniden başlat"],
                parameters=[]
            ))
            
            # Volume control commands
            self.register_command(QuickCommand(
                name="volume_up",
                description="Increase volume",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_volume_up,
                keywords=["volume up", "ses artır", "ses artir", "ses yükselt"],
                parameters=[]
            ))
            
            self.register_command(QuickCommand(
                name="volume_down",
                description="Decrease volume",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_volume_down,
                keywords=["volume down", "ses azalt", "ses düşür", "ses dusur"],
                parameters=[]
            ))
            
            # File operations
            self.register_command(QuickCommand(
                name="create_file",
                description="Create a text file",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_create_file,
                keywords=["create file", "dosya oluştur", "dosya olustur", "yeni dosya"],
                parameters=["filename", "content"]
            ))
            
            # Web operations
            self.register_command(QuickCommand(
                name="open_google",
                description="Open Google in browser",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_open_google,
                keywords=["open google", "google aç", "google ac", "google"],
                parameters=[]
            ))
            
            self.register_command(QuickCommand(
                name="search_web",
                description="Search the web",
                command_type=QuickCommandType.SYSTEM,
                handler=self._handle_search_web,
                keywords=["search", "ara", "web search", "web ara"],
                parameters=["query"]
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
        
        # Find matching quick command with priority order
        # Priority: exact matches first, then partial matches
        matched_commands = []
        
        for command in self.commands.values():
            for keyword in command.keywords:
                # Check for exact word match at start of command
                if command_lower.startswith(keyword + " "):
                    matched_commands.append((command, 100, keyword))  # Highest priority
                # Check for exact word match anywhere
                elif f" {keyword} " in f" {command_lower} ":
                    matched_commands.append((command, 80, keyword))  # High priority
                # Check for partial match at start
                elif command_lower.startswith(keyword):
                    matched_commands.append((command, 60, keyword))  # Medium priority
                # Check for partial match anywhere
                elif keyword in command_lower:
                    matched_commands.append((command, 40, keyword))  # Low priority
        
        # Sort by priority (highest first)
        matched_commands.sort(key=lambda x: x[1], reverse=True)
        
        # Execute the highest priority command
        if matched_commands:
            command, priority, matched_keyword = matched_commands[0]
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
    
    async def _handle_type_text_real(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle type text command (real typing)"""
        try:
            # Extract text from command - handle Turkish characters properly
            command_lower = command.lower()
            
            # Find text after "yaz" or "type" keyword
            text_start = 0
            keywords = ["yaz", "type", "write", "yazı", "metin"]
            
            for keyword in keywords:
                if keyword in command_lower:
                    # Find the position after the keyword
                    keyword_pos = command_lower.find(keyword)
                    text_start = keyword_pos + len(keyword)
                    break
            
            if text_start == 0:
                return {"message": "No 'yaz' keyword found in command"}
            
            # Extract text after keyword, handling spaces and special characters
            text_to_type = command[text_start:].strip()
            
            if not text_to_type:
                return {"message": "No text provided to type"}
            
            # Use real text input capability
            if self.capability_manager:
                result = await self.capability_manager.execute_capability(
                    "text_input", 
                    {"text": text_to_type, "method": "type_text"}, 
                    {}
                )
                if result.get("success", False):
                    return {
                        "message": f"Typed: '{text_to_type}'",
                        "data": {"output": result.get("output", "Text typed successfully")}
                    }
                else:
                    return {"message": f"Failed to type text: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Text input capability not available"}
                
        except Exception as e:
            return {"message": f"Error in type text: {e}"}
    
    async def _handle_generate_and_type_real(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generate and type command (real AI generation and typing)"""
        try:
            # Extract prompt from command - handle Turkish characters properly
            command_lower = command.lower()
            
            # Find prompt after keywords
            text_start = 0
            keywords = ["yaz", "generate", "ai write", "kod yaz", "metin yaz", "hadi kod yazalım", "hadi kod yaz", "kod yazalım"]
            
            for keyword in keywords:
                if keyword in command_lower:
                    # Find the position after the keyword
                    keyword_pos = command_lower.find(keyword)
                    text_start = keyword_pos + len(keyword)
                    break
            
            if text_start == 0:
                return {"message": "No valid keyword found in command"}
            
            # Extract prompt after keyword, handling spaces and special characters
            prompt = command[text_start:].strip()
            
            if not prompt:
                return {"message": "No prompt provided for text generation"}
            
            # Use real AI generation and typing capability
            if self.capability_manager:
                result = await self.capability_manager.execute_capability(
                    "generate_and_type", 
                    {"prompt": prompt, "method": "type_text"}, 
                    {}
                )
                if result.get("success", False):
                    return {
                        "message": f"Generated and typed: '{prompt}'",
                        "data": {"output": result.get("output", "Text generated and typed successfully")}
                    }
                else:
                    return {"message": f"Failed to generate and type: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "AI generation capability not available"}
                
        except Exception as e:
            return {"message": f"Error in generate and type: {e}"}
    
    # Keyboard handlers
    async def _handle_key_enter(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key enter command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"key": "enter", "action": "tap"}, {})
                if result.get("success", False):
                    return {"message": "Enter key pressed", "data": {"action_performed": result.get("output", "Key pressed successfully")}}
                else:
                    return {"message": f"Failed to press Enter: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing Enter: {e}"}
    
    async def _handle_key_space(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key space command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"key": "space", "action": "tap"}, {})
                if result.get("success", False):
                    return {"message": "Space key pressed", "data": {"action_performed": result.get("output", "Key pressed successfully")}}
                else:
                    return {"message": f"Failed to press Space: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing Space: {e}"}
    
    async def _handle_key_any(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle any key command - extract key from command"""
        try:
            # Extract key from command
            words = command.lower().split()
            key_name = None
            
            # Look for key names in the command
            key_mappings = {
                "enter": "enter", "return": "enter", "gir": "enter",
                "space": "space", "boşluk": "space", "bosluk": "space",
                "tab": "tab", "sekme": "tab",
                "escape": "escape", "esc": "escape", "çıkış": "escape", "cikis": "escape",
                "backspace": "backspace", "sil": "backspace", "geri": "backspace",
                "up": "up", "yukarı": "up", "yukari": "up",
                "down": "down", "aşağı": "down", "asagi": "down",
                "left": "left", "sol": "left",
                "right": "right", "sağ": "right", "sag": "right",
                "ctrl": "ctrl", "control": "ctrl",
                "alt": "alt", "alternate": "alt",
                "shift": "shift", "üst": "shift", "ust": "shift",
                "win": "win", "windows": "win", "pencere": "win"
            }
            
            for word in words:
                if word in key_mappings:
                    key_name = key_mappings[word]
                    break
            
            if not key_name:
                return {"message": f"No valid key found in command: {command}. Available keys: enter, space, tab, escape, backspace, up, down, left, right, ctrl, alt, shift, win"}
            
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"key": key_name, "action": "tap"}, {})
                if result.get("success", False):
                    return {"message": f"{key_name.title()} key pressed", "data": {"action_performed": result.get("output", "Key pressed successfully")}}
                else:
                    return {"message": f"Failed to press {key_name}: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing key: {e}"}
    
    async def _handle_key_tab(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle key tab command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("keyboard_control", {"action": "press_key", "key": "tab"}, {})
                if result.get("success", False):
                    return {"message": "Tab key pressed", "data": {"action_performed": result.get("output", "Key pressed successfully")}}
                else:
                    return {"message": f"Failed to press Tab: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Keyboard control capability not available"}
        except Exception as e:
            return {"message": f"Error pressing Tab: {e}"}
    
    # System control handlers
    async def _handle_shutdown(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle shutdown command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("system_shutdown", {}, {})
                if result.get("success", False):
                    return {"message": "Computer shutdown initiated", "data": {"action_performed": result.get("output", "Shutdown successful")}}
                else:
                    return {"message": f"Failed to shutdown: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "System control capability not available"}
        except Exception as e:
            return {"message": f"Error shutting down: {e}"}
    
    async def _handle_restart(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle restart command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("system_restart", {}, {})
                if result.get("success", False):
                    return {"message": "Computer restart initiated", "data": {"action_performed": result.get("output", "Restart successful")}}
                else:
                    return {"message": f"Failed to restart: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "System control capability not available"}
        except Exception as e:
            return {"message": f"Error restarting: {e}"}
    
    async def _handle_volume_up(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle volume up command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("system_volume", {"action": "increase"}, {})
                if result.get("success", False):
                    return {"message": "Volume increased", "data": {"action_performed": result.get("output", "Volume up successful")}}
                else:
                    return {"message": f"Failed to increase volume: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Volume control capability not available"}
        except Exception as e:
            return {"message": f"Error increasing volume: {e}"}
    
    async def _handle_volume_down(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle volume down command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("system_volume", {"action": "decrease"}, {})
                if result.get("success", False):
                    return {"message": "Volume decreased", "data": {"action_performed": result.get("output", "Volume down successful")}}
                else:
                    return {"message": f"Failed to decrease volume: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Volume control capability not available"}
        except Exception as e:
            return {"message": f"Error decreasing volume: {e}"}
    
    async def _handle_create_file(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create file command"""
        try:
            # Extract filename and content from command
            words = command.split()
            filename = None
            content = ""
            
            # Look for filename patterns
            for i, word in enumerate(words):
                if word.lower() in ["file", "dosya"] and i + 1 < len(words):
                    filename = words[i + 1]
                    if not filename.endswith('.txt'):
                        filename += '.txt'
                    break
            
            if not filename:
                filename = "new_file.txt"
            
            # Extract content (everything after filename)
            if "file" in words or "dosya" in words:
                file_index = words.index("file") if "file" in words else words.index("dosya")
                if file_index + 2 < len(words):
                    content = " ".join(words[file_index + 2:])
            
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("file_create_text", {"filename": filename, "content": content}, {})
                if result.get("success", False):
                    return {"message": f"File '{filename}' created successfully", "data": {"action_performed": result.get("output", "File created")}}
                else:
                    return {"message": f"Failed to create file: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "File creation capability not available"}
        except Exception as e:
            return {"message": f"Error creating file: {e}"}
    
    async def _handle_open_google(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle open Google command"""
        try:
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("web_open_url", {"url": "https://www.google.com"}, {})
                if result.get("success", False):
                    return {"message": "Google opened in browser", "data": {"action_performed": result.get("output", "Google opened")}}
                else:
                    return {"message": f"Failed to open Google: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Web capability not available"}
        except Exception as e:
            return {"message": f"Error opening Google: {e}"}
    
    async def _handle_search_web(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web search command"""
        try:
            # Extract search query from command
            words = command.split()
            query = ""
            
            # Look for search keywords
            search_keywords = ["search", "ara", "web search", "web ara"]
            for keyword in search_keywords:
                if keyword in command.lower():
                    keyword_index = command.lower().find(keyword)
                    query = command[keyword_index + len(keyword):].strip()
                    break
            
            if not query:
                query = " ".join(words[1:])  # Use everything after first word
            
            if self.capability_manager:
                result = await self.capability_manager.execute_capability("web_search", {"query": query}, {})
                if result.get("success", False):
                    return {"message": f"Web search for '{query}' completed", "data": {"action_performed": result.get("output", "Search completed")}}
                else:
                    return {"message": f"Failed to search web: {result.get('error', 'Unknown error')}"}
            else:
                return {"message": "Web search capability not available"}
        except Exception as e:
            return {"message": f"Error searching web: {e}"}
    
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
