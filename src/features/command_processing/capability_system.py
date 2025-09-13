"""
Capability System

Manages and provides access to all assistant capabilities including
system control, media, productivity, and web capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class CapabilityType(Enum):
    """Types of capabilities"""
    SYSTEM = "system"
    MEDIA = "media"
    PRODUCTIVITY = "productivity"
    WEB = "web"
    FILE = "file"
    APPLICATION = "application"

@dataclass
class ParameterInfo:
    """Parameter information for capabilities"""
    name: str
    type: str
    required: bool
    description: str
    default_value: Any = None
    allowed_values: Optional[List[Any]] = None

@dataclass
class Capability:
    """Represents a single capability"""
    name: str
    description: str
    capability_type: CapabilityType
    required_parameters: List[str] = field(default_factory=list)
    optional_parameters: List[str] = field(default_factory=list)
    parameter_info: Dict[str, ParameterInfo] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    executor: Optional[Callable] = None
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.capability_type.value,
            "required_parameters": self.required_parameters,
            "optional_parameters": self.optional_parameters,
            "parameter_info": {
                name: {
                    "type": info.type,
                    "required": info.required,
                    "description": info.description,
                    "default_value": info.default_value,
                    "allowed_values": info.allowed_values
                }
                for name, info in self.parameter_info.items()
            },
            "dependencies": self.dependencies,
            "enabled": self.enabled
        }
    
    def get_parameter_info(self, param_name: str) -> Optional[Dict[str, Any]]:
        """Get parameter information"""
        return self.parameter_info.get(param_name)

class BaseCapabilityExecutor(ABC):
    """Base class for capability executors"""
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the capability"""
        pass
    
    @abstractmethod
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if capability can be executed"""
        pass

class CapabilityManager:
    """Manages all assistant capabilities"""
    
    def __init__(self):
        self.capabilities: Dict[str, Capability] = {}
        self.executors: Dict[str, BaseCapabilityExecutor] = {}
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize capability manager"""
        try:
            await self._register_core_capabilities()
            
            # Initialize all executors
            for name, executor in self.executors.items():
                if hasattr(executor, 'initialize'):
                    await executor.initialize()
                    self.logger.info(f"Initialized executor: {name}")
            
            self._is_initialized = True
            self.logger.info(f"Capability manager initialized with {len(self.capabilities)} capabilities")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize capability manager: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if manager is initialized"""
        return self._is_initialized
    
    async def _register_core_capabilities(self):
        """Register core capabilities"""
        # System capabilities
        await self._register_system_capabilities()
        
        # Media capabilities
        await self._register_media_capabilities()
        
        # Productivity capabilities
        await self._register_productivity_capabilities()
        
        # Web capabilities
        await self._register_web_capabilities()
        
        # File capabilities
        await self._register_file_capabilities()
        
        # Application capabilities
        await self._register_application_capabilities()
    
    async def _register_system_capabilities(self):
        """Register system control capabilities"""
        from .capabilities.system_capabilities import (
            SystemShutdownExecutor, VolumeControlExecutor, 
            BrightnessControlExecutor, SystemInfoExecutor
        )
        from .simple_terminal_executor import SimpleTerminalExecutor
        from .capabilities.text_input_capabilities import TextInputExecutor, TextGenerationExecutor
        from .capabilities.keyboard_control_capabilities import KeyboardControlExecutor
        
        # Shutdown capability
        shutdown_cap = Capability(
            name="system_shutdown",
            description="Shutdown the computer",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=[],
            optional_parameters=["delay"],
            parameter_info={
                "delay": ParameterInfo(
                    name="delay",
                    type="integer",
                    required=False,
                    description="Delay in seconds before shutdown",
                    default_value=0
                )
            }
        )
        await self.register_capability(shutdown_cap)
        self.executors["system_shutdown"] = SystemShutdownExecutor()
        
        # Restart capability
        restart_cap = Capability(
            name="system_restart",
            description="Restart the computer",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=[],
            optional_parameters=["delay"],
            parameter_info={
                "delay": ParameterInfo(
                    name="delay",
                    type="integer",
                    required=False,
                    description="Delay in seconds before restart",
                    default_value=0
                )
            }
        )
        await self.register_capability(restart_cap)
        self.executors["system_restart"] = SystemShutdownExecutor()
        
        # Volume control
        volume_cap = Capability(
            name="system_volume",
            description="Control system volume",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=["action"],
            optional_parameters=["level"],
            parameter_info={
                "action": ParameterInfo(
                    name="action",
                    type="string",
                    required=True,
                    description="Volume action (set, increase, decrease, mute, unmute)",
                    allowed_values=["set", "increase", "decrease", "mute", "unmute"]
                ),
                "level": ParameterInfo(
                    name="level",
                    type="integer",
                    required=False,
                    description="Volume level (0-100)",
                    default_value=50
                )
            }
        )
        await self.register_capability(volume_cap)
        self.executors["system_volume"] = VolumeControlExecutor()
        
        # System information
        system_info_cap = Capability(
            name="system_info",
            description="Get system information",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=[],
            optional_parameters=["info_type"],
            parameter_info={
                "info_type": ParameterInfo(
                    name="info_type",
                    type="string",
                    required=False,
                    description="Type of system information to retrieve",
                    default_value="all"
                )
            }
        )
        await self.register_capability(system_info_cap)
        self.executors["system_info"] = SystemInfoExecutor()
        
        # Terminal command capability
        terminal_command_cap = Capability(
            name="terminal_command",
            description="Execute terminal/shell commands",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=["command"],
            optional_parameters=["timeout", "working_directory"],
            parameter_info={
                "command": ParameterInfo(
                    name="command",
                    type="string",
                    required=True,
                    description="Terminal command to execute"
                ),
                "timeout": ParameterInfo(
                    name="timeout",
                    type="integer",
                    required=False,
                    description="Command timeout in seconds",
                    default_value=30
                ),
                "working_directory": ParameterInfo(
                    name="working_directory",
                    type="string",
                    required=False,
                    description="Working directory for command execution"
                )
            }
        )
        await self.register_capability(terminal_command_cap)
        self.executors["terminal_command"] = SimpleTerminalExecutor()
        
        # Text input capability
        text_input_cap = Capability(
            name="text_input",
            description="Type text using keyboard simulation",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=["text"],
            optional_parameters=["delay", "method"],
            parameter_info={
                "text": ParameterInfo(
                    name="text",
                    type="string",
                    required=True,
                    description="Text to type"
                ),
                "delay": ParameterInfo(
                    name="delay",
                    type="float",
                    required=False,
                    description="Delay between keystrokes in seconds",
                    default_value=0.01
                ),
                "method": ParameterInfo(
                    name="method",
                    type="string",
                    required=False,
                    description="Input method to use",
                    default_value="auto"
                )
            }
        )
        await self.register_capability(text_input_cap)
        self.executors["text_input"] = TextInputExecutor()
        
        # Text generation and typing capability
        text_generation_cap = Capability(
            name="generate_and_type",
            description="Generate text using AI and type it",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=["prompt"],
            optional_parameters=["ai_model", "max_length"],
            parameter_info={
                "prompt": ParameterInfo(
                    name="prompt",
                    type="string",
                    required=True,
                    description="Prompt for text generation"
                ),
                "ai_model": ParameterInfo(
                    name="ai_model",
                    type="string",
                    required=False,
                    description="AI model to use for generation"
                ),
                "max_length": ParameterInfo(
                    name="max_length",
                    type="integer",
                    required=False,
                    description="Maximum length of generated text",
                    default_value=500
                )
            }
        )
        await self.register_capability(text_generation_cap)
        # Get AI manager for text generation
        from features.ai_integration import get_ai_manager
        ai_manager = get_ai_manager()
        self.executors["generate_and_type"] = TextGenerationExecutor(ai_manager)
        
        # Keyboard control capability
        keyboard_control_cap = Capability(
            name="keyboard_control",
            description="Control keyboard input - press keys, shortcuts",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=["key"],
            optional_parameters=["action", "duration", "modifiers", "keys"],
            parameter_info={
                "key": ParameterInfo(
                    name="key",
                    type="string",
                    required=True,
                    description="Key to press (enter, space, tab, arrow keys, etc.)"
                ),
                "action": ParameterInfo(
                    name="action",
                    type="string",
                    required=False,
                    description="Action type: tap, hold, press, release",
                    default_value="tap"
                ),
                "duration": ParameterInfo(
                    name="duration",
                    type="float",
                    required=False,
                    description="Duration for hold actions in seconds",
                    default_value=0.1
                ),
                "modifiers": ParameterInfo(
                    name="modifiers",
                    type="array",
                    required=False,
                    description="Modifier keys: ctrl, alt, shift, win",
                    default_value=[]
                ),
                "keys": ParameterInfo(
                    name="keys",
                    type="array",
                    required=False,
                    description="Multiple keys for shortcuts"
                )
            }
        )
        await self.register_capability(keyboard_control_cap)
        self.executors["keyboard_control"] = KeyboardControlExecutor()
    
    async def _register_media_capabilities(self):
        """Register media control capabilities"""
        from .capabilities.media_capabilities import (
            MusicPlaybackExecutor, VideoPlaybackExecutor, 
            BrowserControlExecutor, YouTubeControlExecutor, MediaFileExecutor
        )
        
        # Play music
        play_music_cap = Capability(
            name="media_play_music",
            description="Play music",
            capability_type=CapabilityType.MEDIA,
            required_parameters=[],
            optional_parameters=["song", "artist", "playlist"],
            parameter_info={
                "song": ParameterInfo(
                    name="song",
                    type="string",
                    required=False,
                    description="Song name to play"
                ),
                "artist": ParameterInfo(
                    name="artist",
                    type="string",
                    required=False,
                    description="Artist name"
                ),
                "playlist": ParameterInfo(
                    name="playlist",
                    type="string",
                    required=False,
                    description="Playlist name"
                )
            }
        )
        await self.register_capability(play_music_cap)
        
        # Control playback
        playback_cap = Capability(
            name="media_playback_control",
            description="Control media playback",
            capability_type=CapabilityType.MEDIA,
            required_parameters=["action"],
            optional_parameters=[],
            parameter_info={
                "action": ParameterInfo(
                    name="action",
                    type="string",
                    required=True,
                    description="Playback action",
                    allowed_values=["play", "pause", "stop", "next", "previous", "seek"]
                )
            }
        )
        await self.register_capability(playback_cap)
        self.executors["media_play_music"] = MusicPlaybackExecutor()
        self.executors["media_playback_control"] = MusicPlaybackExecutor()
    
    async def _register_productivity_capabilities(self):
        """Register productivity capabilities"""
        from .capabilities.productivity_capabilities import (
            TextEditorExecutor, FileManagerExecutor, 
            NoteTakingExecutor, ApplicationLauncherExecutor
        )
        
        # Open application
        open_app_cap = Capability(
            name="app_open",
            description="Open an application",
            capability_type=CapabilityType.APPLICATION,
            required_parameters=["application"],
            optional_parameters=["arguments"],
            parameter_info={
                "application": ParameterInfo(
                    name="application",
                    type="string",
                    required=True,
                    description="Application name or path"
                ),
                "arguments": ParameterInfo(
                    name="arguments",
                    type="list",
                    required=False,
                    description="Command line arguments",
                    default_value=[]
                )
            }
        )
        await self.register_capability(open_app_cap)
        
        # Create text file
        create_file_cap = Capability(
            name="file_create_text",
            description="Create a text file",
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
            }
        )
        await self.register_capability(create_file_cap)
        self.executors["app_open"] = ApplicationLauncherExecutor()
        self.executors["file_create_text"] = TextEditorExecutor()
    
    async def _register_web_capabilities(self):
        """Register web capabilities"""
        from .capabilities.web_capabilities import (
            WebSearchExecutor, WebNavigationExecutor, 
            DataExtractionExecutor, FormAutomationExecutor, YouTubeExecutor
        )
        
        # Open URL
        open_url_cap = Capability(
            name="web_open_url",
            description="Open a URL in browser",
            capability_type=CapabilityType.WEB,
            required_parameters=["url"],
            optional_parameters=["browser"],
            parameter_info={
                "url": ParameterInfo(
                    name="url",
                    type="string",
                    required=True,
                    description="URL to open"
                ),
                "browser": ParameterInfo(
                    name="browser",
                    type="string",
                    required=False,
                    description="Browser to use",
                    default_value="default"
                )
            }
        )
        await self.register_capability(open_url_cap)
        
        # Search web
        search_web_cap = Capability(
            name="web_search",
            description="Search the web",
            capability_type=CapabilityType.WEB,
            required_parameters=["query"],
            optional_parameters=["engine"],
            parameter_info={
                "query": ParameterInfo(
                    name="query",
                    type="string",
                    required=True,
                    description="Search query"
                ),
                "engine": ParameterInfo(
                    name="engine",
                    type="string",
                    required=False,
                    description="Search engine",
                    default_value="google"
                )
            }
        )
        await self.register_capability(search_web_cap)
        
        # YouTube capability
        youtube_cap = Capability(
            name="youtube_search",
            description="Search and play YouTube videos",
            capability_type=CapabilityType.WEB,
            required_parameters=["query"],
            optional_parameters=["action", "video_id", "playlist_id"],
            parameter_info={
                "query": ParameterInfo(
                    name="query",
                    type="string",
                    required=True,
                    description="Search query or video/channel name"
                ),
                "action": ParameterInfo(
                    name="action",
                    type="string",
                    required=False,
                    description="Action type: search, play_video, play_playlist, open_channel",
                    default_value="search"
                ),
                "video_id": ParameterInfo(
                    name="video_id",
                    type="string",
                    required=False,
                    description="YouTube video ID"
                ),
                "playlist_id": ParameterInfo(
                    name="playlist_id",
                    type="string",
                    required=False,
                    description="YouTube playlist ID"
                )
            }
        )
        await self.register_capability(youtube_cap)
        
        self.executors["web_open_url"] = WebNavigationExecutor()
        self.executors["web_search"] = WebSearchExecutor()
        self.executors["youtube_search"] = YouTubeExecutor()
    
    async def _register_file_capabilities(self):
        """Register file management capabilities"""
        from .capabilities.productivity_capabilities import FileManagerExecutor
        
        # List files
        list_files_cap = Capability(
            name="file_list",
            description="List files in directory",
            capability_type=CapabilityType.FILE,
            required_parameters=["directory"],
            optional_parameters=["pattern", "recursive"],
            parameter_info={
                "directory": ParameterInfo(
                    name="directory",
                    type="string",
                    required=True,
                    description="Directory path"
                ),
                "pattern": ParameterInfo(
                    name="pattern",
                    type="string",
                    required=False,
                    description="File pattern filter"
                ),
                "recursive": ParameterInfo(
                    name="recursive",
                    type="boolean",
                    required=False,
                    description="Search recursively",
                    default_value=False
                )
            }
        )
        await self.register_capability(list_files_cap)
        self.executors["file_list"] = FileManagerExecutor()
    
    async def _register_application_capabilities(self):
        """Register application control capabilities"""
        from .capabilities.productivity_capabilities import ApplicationLauncherExecutor
        
        # Close application
        close_app_cap = Capability(
            name="app_close",
            description="Close an application",
            capability_type=CapabilityType.APPLICATION,
            required_parameters=["application"],
            optional_parameters=["force"],
            parameter_info={
                "application": ParameterInfo(
                    name="application",
                    type="string",
                    required=True,
                    description="Application name or process name"
                ),
                "force": ParameterInfo(
                    name="force",
                    type="boolean",
                    required=False,
                    description="Force close the application",
                    default_value=False
                )
            }
        )
        await self.register_capability(close_app_cap)
        self.executors["app_close"] = ApplicationLauncherExecutor()
    
    async def register_capability(self, capability: Capability):
        """Register a capability"""
        try:
            self.capabilities[capability.name] = capability
            self.logger.debug(f"Registered capability: {capability.name}")
        except Exception as e:
            self.logger.error(f"Error registering capability {capability.name}: {e}")
    
    async def register_executor(self, capability_name: str, executor: BaseCapabilityExecutor):
        """Register an executor for a capability"""
        try:
            if capability_name in self.capabilities:
                self.executors[capability_name] = executor
                self.capabilities[capability_name].executor = executor.execute
                self.logger.debug(f"Registered executor for capability: {capability_name}")
            else:
                self.logger.error(f"Cannot register executor: capability {capability_name} not found")
        except Exception as e:
            self.logger.error(f"Error registering executor for {capability_name}: {e}")
    
    async def get_capability(self, name: str) -> Optional[Capability]:
        """Get a capability by name"""
        return self.capabilities.get(name)
    
    async def get_all_capabilities(self) -> List[Capability]:
        """Get all capabilities"""
        return list(self.capabilities.values())
    
    async def get_capabilities_by_type(self, capability_type: CapabilityType) -> List[Capability]:
        """Get capabilities by type"""
        return [
            cap for cap in self.capabilities.values() 
            if cap.capability_type == capability_type
        ]
    
    async def get_enabled_capabilities(self) -> List[Capability]:
        """Get enabled capabilities"""
        return [cap for cap in self.capabilities.values() if cap.enabled]
    
    async def execute_capability(
        self, 
        capability_name: str, 
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a capability"""
        try:
            capability = await self.get_capability(capability_name)
            if not capability:
                return {"success": False, "error": f"Capability not found: {capability_name}"}
            
            if not capability.enabled:
                return {"success": False, "error": f"Capability disabled: {capability_name}"}
            
            executor = self.executors.get(capability_name)
            if not executor:
                return {"success": False, "error": f"No executor for capability: {capability_name}"}
            
            if not executor.can_execute(parameters, context):
                return {"success": False, "error": f"Cannot execute capability: {capability_name}"}
            
            result = await executor.execute(parameters, context)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing capability {capability_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_capability_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get capability information"""
        capability = await self.get_capability(name)
        if capability:
            return capability.to_dict()
        return None
    
    async def get_all_capabilities_info(self) -> List[Dict[str, Any]]:
        """Get all capabilities information"""
        return [cap.to_dict() for cap in self.capabilities.values()]
    
    async def enable_capability(self, name: str) -> bool:
        """Enable a capability"""
        try:
            capability = await self.get_capability(name)
            if capability:
                capability.enabled = True
                self.logger.info(f"Enabled capability: {name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error enabling capability {name}: {e}")
            return False
    
    async def disable_capability(self, name: str) -> bool:
        """Disable a capability"""
        try:
            capability = await self.get_capability(name)
            if capability:
                capability.enabled = False
                self.logger.info(f"Disabled capability: {name}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error disabling capability {name}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            self.capabilities.clear()
            self.executors.clear()
            self._is_initialized = False
            self.logger.info("Capability manager cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up capability manager: {e}")

# Global capability manager instance
_capability_manager: Optional[CapabilityManager] = None

async def get_capability_manager() -> CapabilityManager:
    """Get global capability manager instance"""
    global _capability_manager
    if _capability_manager is None:
        _capability_manager = CapabilityManager()
        await _capability_manager.initialize()
    return _capability_manager

async def cleanup_capability_manager():
    """Cleanup global capability manager"""
    global _capability_manager
    if _capability_manager:
        await _capability_manager.cleanup()
        _capability_manager = None
