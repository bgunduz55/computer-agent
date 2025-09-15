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
    YOUTUBE = "youtube"
    WHATSAPP = "whatsapp"
    BROWSER = "browser"
    TEXT_INPUT = "text_input"
    FORM_FILLING = "form_filling"
    TEXT_MANIPULATION = "text_manipulation"
    TYPING_AUTOMATION = "typing_automation"
    DOCUMENT_PROCESSING = "document_processing"
    FILE_ORGANIZATION = "file_organization"
    APPLICATION_AUTOMATION = "application_automation"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    PROGRESS_TRACKING = "progress_tracking"
    FEEDBACK_SYSTEM = "feedback_system"
    ADVANCED_TERMINAL = "advanced_terminal"
    MOBILE_MONITORING = "mobile_monitoring"
    REMOTE_CONTROL = "remote_control"
    TERMINAL_SESSION_MANAGEMENT = "terminal_session_management"
    LOGGING_ANALYTICS = "logging_analytics"

@dataclass
class ParameterInfo:
    """Parameter information for capabilities"""
    name: str
    description: str
    required: bool
    type: str = "string"
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
    keywords: List[str] = field(default_factory=list)
    
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
            "enabled": self.enabled,
            "keywords": self.keywords
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
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CapabilityManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_is_initialized'):
            self.capabilities: Dict[str, Capability] = {}
            self.executors: Dict[str, BaseCapabilityExecutor] = {}
            self.logger = logging.getLogger(__name__)
            self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize capability manager"""
        if self._is_initialized:
            return True
            
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
        
        # Advanced web capabilities
        await self._register_advanced_web_capabilities()
        
        # Text input capabilities - CORE
        await self._register_text_input_capabilities()
        
        # Enhanced text input capabilities - RE-ENABLED
        await self._register_enhanced_text_input_capabilities()
        
        # Advanced file operations capabilities
        await self._register_advanced_file_operations_capabilities()
        
        # Application control capabilities
        await self._register_application_control_capabilities()
        
        # Progress tracking and feedback capabilities
        await self._register_progress_feedback_capabilities()
        
        # Advanced terminal capabilities
        await self._register_advanced_terminal_capabilities()
        
        # Mobile monitoring capabilities
        await self._register_mobile_monitoring_capabilities()
        
        # Remote control capabilities
        await self._register_remote_control_capabilities()
        
        # Terminal session management capabilities
        await self._register_terminal_session_capabilities()
        await self._register_logging_analytics_capabilities()
    
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
        
        # Text input capabilities moved to _register_text_input_capabilities
        
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
        # Initialize the executor
        await self.executors["keyboard_control"].initialize()
    
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
            required_parameters=["application_name"],
            optional_parameters=["arguments"],
            parameter_info={
                "application_name": ParameterInfo(
                    name="application_name",
                    type="string",
                    required=True,
                    description="Application name (e.g., notepad, chrome, calculator)"
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
        self.executors["app_open"] = ApplicationLauncherExecutor()
        
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
    
    async def _register_advanced_web_capabilities(self):
        """Register advanced web automation capabilities"""
        # Try to import optional automation capabilities
        try:
            from .capabilities.youtube_automation import YouTubeAutomationExecutor
            youtube_available = True
        except ImportError as e:
            self.logger.warning(f"YouTube automation not available: {e}")
            youtube_available = False
            
        try:
            from .capabilities.whatsapp_automation import WhatsAppAutomationExecutor
            whatsapp_available = True
        except ImportError as e:
            self.logger.warning(f"WhatsApp automation not available: {e}")
            whatsapp_available = False
        
        # YouTube automation capability
        youtube_cap = Capability(
            name="youtube_automation",
            description="Advanced YouTube automation including video search, selection, and playback",
            capability_type=CapabilityType.YOUTUBE,
            required_parameters=["action"],
            optional_parameters=["query", "video_url", "playlist_url"],
            parameter_info={
                "action": ParameterInfo(
                    name="action",
                    type="string",
                    required=True,
                    description="YouTube action to perform",
                    allowed_values=["search", "play_video", "play_playlist", "get_recommendations", "get_video_info"]
                ),
                "query": ParameterInfo(
                    name="query",
                    type="string",
                    required=False,
                    description="Search query for videos"
                ),
                "video_url": ParameterInfo(
                    name="video_url",
                    type="string",
                    required=False,
                    description="YouTube video URL to play"
                ),
                "playlist_url": ParameterInfo(
                    name="playlist_url",
                    type="string",
                    required=False,
                    description="YouTube playlist URL to play"
                )
            }
        )
        await self.register_capability(youtube_cap)
        if youtube_available:
            self.executors["youtube_automation"] = YouTubeAutomationExecutor()
        else:
            self.logger.warning("YouTube automation executor not available")
        
        # WhatsApp automation capability
        whatsapp_cap = Capability(
            name="whatsapp_automation",
            description="Advanced WhatsApp Web automation including messaging, group management, and file sharing",
            capability_type=CapabilityType.WHATSAPP,
            required_parameters=["action"],
            optional_parameters=["contact", "message", "file_path", "group_name", "members"],
            parameter_info={
                "action": ParameterInfo(
                    name="action",
                    type="string",
                    required=True,
                    description="WhatsApp action to perform",
                    allowed_values=["send_message", "send_file", "create_group", "add_to_group", "get_contacts", "get_messages"]
                ),
                "contact": ParameterInfo(
                    name="contact",
                    type="string",
                    required=False,
                    description="Contact name or phone number"
                ),
                "message": ParameterInfo(
                    name="message",
                    type="string",
                    required=False,
                    description="Message text to send"
                ),
                "file_path": ParameterInfo(
                    name="file_path",
                    type="string",
                    required=False,
                    description="Path to file to send"
                ),
                "group_name": ParameterInfo(
                    name="group_name",
                    type="string",
                    required=False,
                    description="Name of the group to create or modify"
                ),
                "members": ParameterInfo(
                    name="members",
                    type="list",
                    required=False,
                    description="List of member names to add to group"
                )
            }
        )
        await self.register_capability(whatsapp_cap)
        if whatsapp_available:
            self.executors["whatsapp_automation"] = WhatsAppAutomationExecutor()
        else:
            self.logger.warning("WhatsApp automation executor not available")
    
    async def _register_text_input_capabilities(self):
        """Register basic text input capabilities"""
        from .capabilities.text_input_capabilities import TextInputExecutor
        
        # Text input capability - RE-ENABLED
        text_input_cap = Capability(
            name="text_input",
            description="Type text using keyboard input",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=["text"],
            optional_parameters=["method"],
            parameter_info={
                "text": ParameterInfo(
                    name="text",
                    description="Text to type",
                    type="string",
                    required=True
                ),
                "method": ParameterInfo(
                    name="method",
                    description="Typing method (type_text, paste, etc.)",
                    type="string",
                    required=False,
                    default_value="type_text"
                )
            },
            keywords=["type", "write", "input", "text"]
        )
        await self.register_capability(text_input_cap)
        self.executors["text_input"] = TextInputExecutor()
        # Initialize the executor
        await self.executors["text_input"].initialize()
        
        # Text generation and typing capability - SIMPLIFIED (no AI)
        text_generation_cap = Capability(
            name="generate_and_type",
            description="Generate text and type it (simplified version)",
            capability_type=CapabilityType.SYSTEM,
            required_parameters=["prompt"],
            optional_parameters=["method"],
            parameter_info={
                "prompt": ParameterInfo(
                    name="prompt",
                    description="Prompt for text generation",
                    type="string",
                    required=True
                ),
                "method": ParameterInfo(
                    name="method",
                    description="Typing method (type_text, paste, etc.)",
                    type="string",
                    required=False,
                    default_value="type_text"
                )
            },
            keywords=["generate", "ai", "write", "type"]
        )
        await self.register_capability(text_generation_cap)
        # Use simple text input executor for both
        self.executors["generate_and_type"] = TextInputExecutor()
        # Initialize the executor
        await self.executors["generate_and_type"].initialize()

    async def _register_enhanced_text_input_capabilities(self):
        """Register enhanced text input and automation capabilities"""
        from .capabilities.form_filling_capabilities import (
            FormFillingExecutor, AdvancedTextInputExecutor
        )
        from .capabilities.text_manipulation_capabilities import TextManipulationExecutor
        from .capabilities.typing_automation_capabilities import TypingAutomationExecutor
        
        # Form filling capability
        form_filling_cap = Capability(
            name="form_filling",
            description="Fill forms with data including validation and formatting",
            capability_type=CapabilityType.FORM_FILLING,
            required_parameters=["form_data"],
            optional_parameters=["auto_format", "validate_fields"],
            parameter_info={
                "form_data": ParameterInfo(
                    name="form_data",
                    type="object",
                    required=True,
                    description="Form data structure with fields and values"
                ),
                "auto_format": ParameterInfo(
                    name="auto_format",
                    type="boolean",
                    required=False,
                    description="Automatically format field values",
                    default_value=True
                ),
                "validate_fields": ParameterInfo(
                    name="validate_fields",
                    type="boolean",
                    required=False,
                    description="Validate field values before filling",
                    default_value=True
                )
            }
        )
        await self.register_capability(form_filling_cap)
        self.executors["form_filling"] = FormFillingExecutor()
        
        # Text manipulation capability
        text_manipulation_cap = Capability(
            name="text_manipulation",
            description="Manipulate and process text with various operations",
            capability_type=CapabilityType.TEXT_MANIPULATION,
            required_parameters=["text", "operation"],
            optional_parameters=["format_type", "search_term", "search_type", "extraction_type"],
            parameter_info={
                "text": ParameterInfo(
                    name="text",
                    type="string",
                    required=True,
                    description="Text to manipulate"
                ),
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Operation to perform",
                    allowed_values=["format", "search", "extract"]
                ),
                "format_type": ParameterInfo(
                    name="format_type",
                    type="string",
                    required=False,
                    description="Format type for formatting operation",
                    allowed_values=["markdown", "html", "json", "xml", "csv", "yaml", "plain_text"]
                ),
                "search_term": ParameterInfo(
                    name="search_term",
                    type="string",
                    required=False,
                    description="Search term for search operation"
                ),
                "search_type": ParameterInfo(
                    name="search_type",
                    type="string",
                    required=False,
                    description="Type of search to perform",
                    allowed_values=["exact_match", "regex", "fuzzy", "case_insensitive", "word_boundary"]
                ),
                "extraction_type": ParameterInfo(
                    name="extraction_type",
                    type="string",
                    required=False,
                    description="Type of data to extract",
                    allowed_values=["emails", "phones", "urls", "dates", "numbers", "names", "addresses"]
                )
            }
        )
        await self.register_capability(text_manipulation_cap)
        self.executors["text_manipulation"] = TextManipulationExecutor()
        
        # Advanced text input capability
        advanced_text_input_cap = Capability(
            name="advanced_text_input",
            description="Advanced text input with smart typing and context awareness",
            capability_type=CapabilityType.TEXT_INPUT,
            required_parameters=["text", "operation"],
            optional_parameters=["typing_mode", "auto_format", "typing_speed"],
            parameter_info={
                "text": ParameterInfo(
                    name="text",
                    type="string",
                    required=True,
                    description="Text to input"
                ),
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Operation to perform",
                    allowed_values=["type_text", "fill_form", "manipulate_text", "auto_complete"]
                ),
                "typing_mode": ParameterInfo(
                    name="typing_mode",
                    type="string",
                    required=False,
                    description="Typing mode for text input",
                    allowed_values=["normal", "fast", "slow", "human_like", "instant"],
                    default_value="normal"
                ),
                "auto_format": ParameterInfo(
                    name="auto_format",
                    type="boolean",
                    required=False,
                    description="Automatically format text before typing",
                    default_value=True
                ),
                "typing_speed": ParameterInfo(
                    name="typing_speed",
                    type="string",
                    required=False,
                    description="Typing speed setting",
                    allowed_values=["slow", "normal", "fast", "instant"],
                    default_value="normal"
                )
            }
        )
        await self.register_capability(advanced_text_input_cap)
        self.executors["advanced_text_input"] = AdvancedTextInputExecutor()
        
        # Typing automation capability
        typing_automation_cap = Capability(
            name="typing_automation",
            description="Advanced typing automation with macro recording and smart typing",
            capability_type=CapabilityType.TYPING_AUTOMATION,
            required_parameters=["operation"],
            optional_parameters=["text", "mode", "macro_name", "macro_type"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Automation operation to perform",
                    allowed_values=["type_text", "execute_macro", "start_recording", "stop_recording", "list_macros"]
                ),
                "text": ParameterInfo(
                    name="text",
                    type="string",
                    required=False,
                    description="Text to type"
                ),
                "mode": ParameterInfo(
                    name="mode",
                    type="string",
                    required=False,
                    description="Typing mode",
                    allowed_values=["normal", "fast", "slow", "human_like", "instant"],
                    default_value="normal"
                ),
                "macro_name": ParameterInfo(
                    name="macro_name",
                    type="string",
                    required=False,
                    description="Name of macro to execute or record"
                ),
                "macro_type": ParameterInfo(
                    name="macro_type",
                    type="string",
                    required=False,
                    description="Type of macro to record",
                    allowed_values=["text", "keyboard_shortcut", "mouse_action", "combined"],
                    default_value="text"
                )
            }
        )
        await self.register_capability(typing_automation_cap)
        self.executors["typing_automation"] = TypingAutomationExecutor()
    
    async def _register_advanced_file_operations_capabilities(self):
        """Register advanced file operations capabilities"""
        from .capabilities.document_processor import DocumentProcessorExecutor
        from .capabilities.file_organizer import FileOrganizerExecutor
        
        # Document processing capability
        document_processing_cap = Capability(
            name="document_processing",
            description="Advanced document creation, processing, and template management",
            capability_type=CapabilityType.DOCUMENT_PROCESSING,
            required_parameters=["operation"],
            optional_parameters=["title", "content", "document_type", "format_type", "template_name", "placeholders"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Document processing operation to perform",
                    allowed_values=["create_document", "process_document", "create_from_template", "list_templates"]
                ),
                "title": ParameterInfo(
                    name="title",
                    type="string",
                    required=False,
                    description="Document title"
                ),
                "content": ParameterInfo(
                    name="content",
                    type="string",
                    required=False,
                    description="Document content"
                ),
                "document_type": ParameterInfo(
                    name="document_type",
                    type="string",
                    required=False,
                    description="Type of document to create",
                    allowed_values=["text", "markdown", "html", "json", "xml", "csv", "yaml"],
                    default_value="text"
                ),
                "format_type": ParameterInfo(
                    name="format_type",
                    type="string",
                    required=False,
                    description="Format type for document",
                    allowed_values=["plain", "formatted", "structured", "template"],
                    default_value="formatted"
                ),
                "template_name": ParameterInfo(
                    name="template_name",
                    type="string",
                    required=False,
                    description="Name of template to use"
                ),
                "placeholders": ParameterInfo(
                    name="placeholders",
                    type="object",
                    required=False,
                    description="Placeholder values for template"
                )
            }
        )
        await self.register_capability(document_processing_cap)
        self.executors["document_processing"] = DocumentProcessorExecutor()
        
        # File organization capability
        file_organization_cap = Capability(
            name="file_organization",
            description="Advanced file organization, batch operations, and duplicate detection",
            capability_type=CapabilityType.FILE_ORGANIZATION,
            required_parameters=["operation"],
            optional_parameters=["source_directory", "target_directory", "rule_type", "pattern", "file_paths", "operations"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="File organization operation to perform",
                    allowed_values=["organize_files", "batch_operations", "find_duplicates"]
                ),
                "source_directory": ParameterInfo(
                    name="source_directory",
                    type="string",
                    required=False,
                    description="Source directory for organization"
                ),
                "target_directory": ParameterInfo(
                    name="target_directory",
                    type="string",
                    required=False,
                    description="Target directory for organization"
                ),
                "rule_type": ParameterInfo(
                    name="rule_type",
                    type="string",
                    required=False,
                    description="Organization rule type",
                    allowed_values=["by_extension", "by_date", "by_size", "by_name", "by_type", "by_pattern", "by_duplicate"],
                    default_value="by_type"
                ),
                "pattern": ParameterInfo(
                    name="pattern",
                    type="string",
                    required=False,
                    description="File pattern for organization",
                    default_value="*"
                ),
                "file_paths": ParameterInfo(
                    name="file_paths",
                    type="array",
                    required=False,
                    description="List of file paths for batch operations"
                ),
                "operations": ParameterInfo(
                    name="operations",
                    type="array",
                    required=False,
                    description="List of operations to perform",
                    allowed_values=["rename", "copy", "move", "delete", "compress"]
                )
            }
        )
        await self.register_capability(file_organization_cap)
        self.executors["file_organization"] = FileOrganizerExecutor()
    
    async def _register_application_control_capabilities(self):
        """Register application control capabilities"""
        from .capabilities.application_automation import ApplicationAutomationExecutor
        from .capabilities.workflow_orchestrator import WorkflowOrchestratorExecutor
        
        # Application automation capability
        application_automation_cap = Capability(
            name="application_automation",
            description="Advanced application control, launching, and automation",
            capability_type=CapabilityType.APPLICATION_AUTOMATION,
            required_parameters=["operation"],
            optional_parameters=["app_name", "app_path", "arguments", "key", "text", "workflow_name", "force"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Application automation operation to perform",
                    allowed_values=["launch_application", "close_application", "send_key", "send_text", "take_screenshot", "execute_workflow", "list_applications"]
                ),
                "app_name": ParameterInfo(
                    name="app_name",
                    type="string",
                    required=False,
                    description="Name of the application"
                ),
                "app_path": ParameterInfo(
                    name="app_path",
                    type="string",
                    required=False,
                    description="Path to the application executable"
                ),
                "arguments": ParameterInfo(
                    name="arguments",
                    type="array",
                    required=False,
                    description="Command line arguments for the application"
                ),
                "key": ParameterInfo(
                    name="key",
                    type="string",
                    required=False,
                    description="Key to send to the application"
                ),
                "text": ParameterInfo(
                    name="text",
                    type="string",
                    required=False,
                    description="Text to send to the application"
                ),
                "workflow_name": ParameterInfo(
                    name="workflow_name",
                    type="string",
                    required=False,
                    description="Name of the workflow to execute"
                ),
                "force": ParameterInfo(
                    name="force",
                    type="boolean",
                    required=False,
                    description="Force close application",
                    default_value=False
                )
            }
        )
        await self.register_capability(application_automation_cap)
        self.executors["application_automation"] = ApplicationAutomationExecutor()
        
        # Workflow orchestration capability
        workflow_orchestration_cap = Capability(
            name="workflow_orchestration",
            description="Advanced workflow orchestration and cross-application automation",
            capability_type=CapabilityType.WORKFLOW_ORCHESTRATION,
            required_parameters=["operation"],
            optional_parameters=["workflow_name", "name", "description", "steps", "triggers", "conditions", "timeout", "retry_count", "execution_id", "context"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Workflow orchestration operation to perform",
                    allowed_values=["execute_workflow", "create_workflow", "list_workflows", "get_execution_status", "cancel_execution"]
                ),
                "workflow_name": ParameterInfo(
                    name="workflow_name",
                    type="string",
                    required=False,
                    description="Name of the workflow to execute"
                ),
                "name": ParameterInfo(
                    name="name",
                    type="string",
                    required=False,
                    description="Name of the workflow to create"
                ),
                "description": ParameterInfo(
                    name="description",
                    type="string",
                    required=False,
                    description="Description of the workflow"
                ),
                "steps": ParameterInfo(
                    name="steps",
                    type="array",
                    required=False,
                    description="Steps of the workflow"
                ),
                "triggers": ParameterInfo(
                    name="triggers",
                    type="array",
                    required=False,
                    description="Triggers for the workflow",
                    allowed_values=["manual", "scheduled", "event", "condition"]
                ),
                "conditions": ParameterInfo(
                    name="conditions",
                    type="array",
                    required=False,
                    description="Conditions for the workflow"
                ),
                "timeout": ParameterInfo(
                    name="timeout",
                    type="integer",
                    required=False,
                    description="Timeout for workflow execution in seconds",
                    default_value=300
                ),
                "retry_count": ParameterInfo(
                    name="retry_count",
                    type="integer",
                    required=False,
                    description="Number of retries for failed steps",
                    default_value=3
                ),
                "execution_id": ParameterInfo(
                    name="execution_id",
                    type="string",
                    required=False,
                    description="ID of the workflow execution"
                ),
                "context": ParameterInfo(
                    name="context",
                    type="object",
                    required=False,
                    description="Context variables for workflow execution"
                )
            }
        )
        await self.register_capability(workflow_orchestration_cap)
        self.executors["workflow_orchestration"] = WorkflowOrchestratorExecutor()
    
    async def _register_progress_feedback_capabilities(self):
        """Register progress tracking and feedback capabilities"""
        from .progress_tracker import ProgressTrackerExecutor
        from .feedback_system import FeedbackSystemExecutor
        
        # Progress tracking capability
        progress_tracking_cap = Capability(
            name="progress_tracking",
            description="Real-time progress tracking and execution monitoring",
            capability_type=CapabilityType.PROGRESS_TRACKING,
            required_parameters=["operation"],
            optional_parameters=["execution_id", "command", "total_steps", "status", "message", "step_id", "name", "description", "progress_percentage", "error_message", "data", "status_filter", "limit"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Progress tracking operation to perform",
                    allowed_values=["start_execution", "update_status", "add_step", "start_step", "complete_step", "fail_step", "update_progress", "add_message", "add_error", "get_execution_status", "list_executions", "get_recent_events"]
                ),
                "execution_id": ParameterInfo(
                    name="execution_id",
                    type="string",
                    required=False,
                    description="Execution ID for tracking"
                ),
                "command": ParameterInfo(
                    name="command",
                    type="string",
                    required=False,
                    description="Command being executed"
                ),
                "total_steps": ParameterInfo(
                    name="total_steps",
                    type="integer",
                    required=False,
                    description="Total number of steps in execution",
                    default_value=0
                ),
                "status": ParameterInfo(
                    name="status",
                    type="string",
                    required=False,
                    description="Execution status",
                    allowed_values=["pending", "running", "completed", "failed", "cancelled", "paused"]
                ),
                "message": ParameterInfo(
                    name="message",
                    type="string",
                    required=False,
                    description="Status or progress message"
                ),
                "step_id": ParameterInfo(
                    name="step_id",
                    type="string",
                    required=False,
                    description="Step ID for step operations"
                ),
                "name": ParameterInfo(
                    name="name",
                    type="string",
                    required=False,
                    description="Step name"
                ),
                "description": ParameterInfo(
                    name="description",
                    type="string",
                    required=False,
                    description="Step description"
                ),
                "progress_percentage": ParameterInfo(
                    name="progress_percentage",
                    type="number",
                    required=False,
                    description="Progress percentage (0-100)"
                ),
                "error_message": ParameterInfo(
                    name="error_message",
                    type="string",
                    required=False,
                    description="Error message for failed operations"
                ),
                "data": ParameterInfo(
                    name="data",
                    type="object",
                    required=False,
                    description="Additional data for operations"
                ),
                "status_filter": ParameterInfo(
                    name="status_filter",
                    type="string",
                    required=False,
                    description="Filter executions by status",
                    allowed_values=["pending", "running", "completed", "failed", "cancelled", "paused"]
                ),
                "limit": ParameterInfo(
                    name="limit",
                    type="integer",
                    required=False,
                    description="Limit for recent events",
                    default_value=100
                )
            }
        )
        await self.register_capability(progress_tracking_cap)
        self.executors["progress_tracking"] = ProgressTrackerExecutor()
        
        # Feedback system capability
        feedback_system_cap = Capability(
            name="feedback_system",
            description="Real-time feedback collection, analysis, and response generation",
            capability_type=CapabilityType.FEEDBACK_SYSTEM,
            required_parameters=["operation"],
            optional_parameters=["execution_id", "feedback_type", "priority", "message", "user_input", "context", "feedback_id", "status_filter", "feedback_type_filter"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Feedback system operation to perform",
                    allowed_values=["create_feedback", "process_feedback", "get_feedback", "list_feedbacks", "get_feedback_summary"]
                ),
                "execution_id": ParameterInfo(
                    name="execution_id",
                    type="string",
                    required=False,
                    description="Execution ID for feedback"
                ),
                "feedback_type": ParameterInfo(
                    name="feedback_type",
                    type="string",
                    required=False,
                    description="Type of feedback",
                    allowed_values=["success", "error", "warning", "info", "question", "confirmation", "suggestion"]
                ),
                "priority": ParameterInfo(
                    name="priority",
                    type="string",
                    required=False,
                    description="Feedback priority",
                    allowed_values=["low", "medium", "high", "critical"],
                    default_value="medium"
                ),
                "message": ParameterInfo(
                    name="message",
                    type="string",
                    required=False,
                    description="Feedback message"
                ),
                "user_input": ParameterInfo(
                    name="user_input",
                    type="string",
                    required=False,
                    description="User input for feedback"
                ),
                "context": ParameterInfo(
                    name="context",
                    type="object",
                    required=False,
                    description="Additional context for feedback"
                ),
                "feedback_id": ParameterInfo(
                    name="feedback_id",
                    type="string",
                    required=False,
                    description="Feedback ID for operations"
                ),
                "status_filter": ParameterInfo(
                    name="status_filter",
                    type="string",
                    required=False,
                    description="Filter feedbacks by status",
                    allowed_values=["pending", "processing", "resolved", "ignored", "escalated"]
                ),
                "feedback_type_filter": ParameterInfo(
                    name="feedback_type_filter",
                    type="string",
                    required=False,
                    description="Filter feedbacks by type",
                    allowed_values=["success", "error", "warning", "info", "question", "confirmation", "suggestion"]
                )
            }
        )
        await self.register_capability(feedback_system_cap)
        self.executors["feedback_system"] = FeedbackSystemExecutor()
    
    async def _register_advanced_terminal_capabilities(self):
        """Register advanced terminal capabilities"""
        from .capabilities.advanced_terminal_capabilities import AdvancedTerminalExecutor
        
        # Advanced terminal capability
        advanced_terminal_cap = Capability(
            name="advanced_terminal",
            description="Advanced terminal integration with real-time monitoring, session management, and command chaining",
            capability_type=CapabilityType.ADVANCED_TERMINAL,
            required_parameters=["operation"],
            optional_parameters=["command", "session_id", "terminal_type", "working_directory", "timeout", "chain_id", "commands", "chain_type", "stop_on_error", "monitor_id", "execution_id", "name", "limit"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Advanced terminal operation to perform",
                    allowed_values=["execute_command", "execute_command_chain", "create_session", "get_session_info", "close_session", "list_sessions", "monitor_session", "stop_monitoring", "get_execution_status", "cancel_execution", "get_command_history", "create_command_chain", "list_command_chains", "get_system_info"]
                ),
                "command": ParameterInfo(
                    name="command",
                    type="string",
                    required=False,
                    description="Command to execute"
                ),
                "session_id": ParameterInfo(
                    name="session_id",
                    type="string",
                    required=False,
                    description="Terminal session ID"
                ),
                "terminal_type": ParameterInfo(
                    name="terminal_type",
                    type="string",
                    required=False,
                    description="Type of terminal to use",
                    allowed_values=["powershell", "cmd", "bash", "zsh", "fish", "wsl"]
                ),
                "working_directory": ParameterInfo(
                    name="working_directory",
                    type="string",
                    required=False,
                    description="Working directory for command execution"
                ),
                "timeout": ParameterInfo(
                    name="timeout",
                    type="integer",
                    required=False,
                    description="Command timeout in seconds",
                    default_value=30
                ),
                "chain_id": ParameterInfo(
                    name="chain_id",
                    type="string",
                    required=False,
                    description="Command chain ID"
                ),
                "commands": ParameterInfo(
                    name="commands",
                    type="array",
                    required=False,
                    description="List of commands to execute"
                ),
                "chain_type": ParameterInfo(
                    name="chain_type",
                    type="string",
                    required=False,
                    description="Type of command chain execution",
                    allowed_values=["sequential", "parallel", "conditional", "pipeline"],
                    default_value="sequential"
                ),
                "stop_on_error": ParameterInfo(
                    name="stop_on_error",
                    type="boolean",
                    required=False,
                    description="Stop execution on first error",
                    default_value=True
                ),
                "monitor_id": ParameterInfo(
                    name="monitor_id",
                    type="string",
                    required=False,
                    description="Monitor ID for session monitoring"
                ),
                "execution_id": ParameterInfo(
                    name="execution_id",
                    type="string",
                    required=False,
                    description="Execution ID for status tracking"
                ),
                "name": ParameterInfo(
                    name="name",
                    type="string",
                    required=False,
                    description="Name for command chain"
                ),
                "limit": ParameterInfo(
                    name="limit",
                    type="integer",
                    required=False,
                    description="Limit for command history",
                    default_value=50
                )
            }
        )
        await self.register_capability(advanced_terminal_cap)
        self.executors["advanced_terminal"] = AdvancedTerminalExecutor()
    
    async def _register_mobile_monitoring_capabilities(self):
        """Register mobile monitoring capabilities"""
        from .capabilities.mobile_monitoring_capabilities import MobileMonitoringExecutor
        
        # Mobile monitoring capability
        mobile_monitoring_cap = Capability(
            name="mobile_monitoring",
            description="Real-time mobile monitoring and status updates for mobile applications",
            capability_type=CapabilityType.MOBILE_MONITORING,
            required_parameters=["operation"],
            optional_parameters=["host", "port", "execution_id", "command", "metadata", "progress", "message", "output", "error", "context", "level", "operation", "file_path", "status", "app_name", "event", "event_type", "data", "priority", "requires_ack"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Mobile monitoring operation to perform",
                    allowed_values=["start_monitoring", "stop_monitoring", "track_command_start", "track_command_progress", "track_command_completed", "track_command_failed", "send_log_message", "send_error", "send_terminal_output", "send_file_operation", "send_application_event", "get_connection_status", "get_execution_status", "get_stats", "send_custom_event"]
                ),
                "host": ParameterInfo(
                    name="host",
                    type="string",
                    required=False,
                    description="WebSocket server host",
                    default_value="localhost"
                ),
                "port": ParameterInfo(
                    name="port",
                    type="integer",
                    required=False,
                    description="WebSocket server port",
                    default_value=8765
                ),
                "execution_id": ParameterInfo(
                    name="execution_id",
                    type="string",
                    required=False,
                    description="Command execution ID for tracking"
                ),
                "command": ParameterInfo(
                    name="command",
                    type="string",
                    required=False,
                    description="Command being executed"
                ),
                "metadata": ParameterInfo(
                    name="metadata",
                    type="object",
                    required=False,
                    description="Additional metadata for tracking"
                ),
                "progress": ParameterInfo(
                    name="progress",
                    type="number",
                    required=False,
                    description="Command progress percentage (0-100)"
                ),
                "message": ParameterInfo(
                    name="message",
                    type="string",
                    required=False,
                    description="Progress or log message"
                ),
                "output": ParameterInfo(
                    name="output",
                    type="string",
                    required=False,
                    description="Command output or terminal output"
                ),
                "error": ParameterInfo(
                    name="error",
                    type="string",
                    required=False,
                    description="Error message"
                ),
                "context": ParameterInfo(
                    name="context",
                    type="object",
                    required=False,
                    description="Error context information"
                ),
                "level": ParameterInfo(
                    name="level",
                    type="string",
                    required=False,
                    description="Log level",
                    allowed_values=["debug", "info", "warning", "error", "critical"],
                    default_value="info"
                ),
                "file_path": ParameterInfo(
                    name="file_path",
                    type="string",
                    required=False,
                    description="File path for file operations"
                ),
                "status": ParameterInfo(
                    name="status",
                    type="string",
                    required=False,
                    description="Status for file operations"
                ),
                "app_name": ParameterInfo(
                    name="app_name",
                    type="string",
                    required=False,
                    description="Application name for application events"
                ),
                "event": ParameterInfo(
                    name="event",
                    type="string",
                    required=False,
                    description="Event type for application events"
                ),
                "event_type": ParameterInfo(
                    name="event_type",
                    type="string",
                    required=False,
                    description="Custom event type",
                    allowed_values=["command_started", "command_progress", "command_completed", "command_failed", "system_status", "log_message", "error_occurred", "session_update", "terminal_output", "file_operation", "application_event"]
                ),
                "data": ParameterInfo(
                    name="data",
                    type="object",
                    required=False,
                    description="Custom event data"
                ),
                "priority": ParameterInfo(
                    name="priority",
                    type="integer",
                    required=False,
                    description="Event priority (1=low, 2=medium, 3=high, 4=critical)",
                    default_value=1
                ),
                "requires_ack": ParameterInfo(
                    name="requires_ack",
                    type="boolean",
                    required=False,
                    description="Whether event requires acknowledgment",
                    default_value=False
                )
            }
        )
        await self.register_capability(mobile_monitoring_cap)
        self.executors["mobile_monitoring"] = MobileMonitoringExecutor()
    
    async def _register_remote_control_capabilities(self):
        """Register remote control capabilities"""
        from .capabilities.remote_control_capabilities import RemoteControlExecutor
        
        # Remote control capability
        remote_control_cap = Capability(
            name="remote_control",
            description="Remote computer control interface for mobile applications",
            capability_type=CapabilityType.REMOTE_CONTROL,
            required_parameters=["operation"],
            optional_parameters=["host", "port", "connection_id", "command_id", "command_type", "action", "parameters", "message_type", "data", "user_filter"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Remote control operation to perform",
                    allowed_values=["start_interface", "stop_interface", "get_connection_status", "get_command_status", "get_stats", "send_remote_command", "broadcast_message", "get_active_connections", "disconnect_client"]
                ),
                "host": ParameterInfo(
                    name="host",
                    type="string",
                    required=False,
                    description="WebSocket server host",
                    default_value="localhost"
                ),
                "port": ParameterInfo(
                    name="port",
                    type="integer",
                    required=False,
                    description="WebSocket server port",
                    default_value=8767
                ),
                "connection_id": ParameterInfo(
                    name="connection_id",
                    type="string",
                    required=False,
                    description="Connection ID for operations"
                ),
                "command_id": ParameterInfo(
                    name="command_id",
                    type="string",
                    required=False,
                    description="Command ID for status operations"
                ),
                "command_type": ParameterInfo(
                    name="command_type",
                    type="string",
                    required=False,
                    description="Type of command to send",
                    allowed_values=["system_control", "file_operation", "application_control", "terminal_command", "browser_automation", "text_input", "media_control", "monitoring", "custom"]
                ),
                "action": ParameterInfo(
                    name="action",
                    type="string",
                    required=False,
                    description="Action to perform"
                ),
                "parameters": ParameterInfo(
                    name="parameters",
                    type="object",
                    required=False,
                    description="Command parameters"
                ),
                "message_type": ParameterInfo(
                    name="message_type",
                    type="string",
                    required=False,
                    description="Type of broadcast message",
                    default_value="broadcast"
                ),
                "data": ParameterInfo(
                    name="data",
                    type="object",
                    required=False,
                    description="Message data"
                ),
                "user_filter": ParameterInfo(
                    name="user_filter",
                    type="string",
                    required=False,
                    description="User ID filter for broadcast messages"
                )
            }
        )
        await self.register_capability(remote_control_cap)
        self.executors["remote_control"] = RemoteControlExecutor()
    
    async def _register_terminal_session_capabilities(self):
        """Register terminal session management capabilities"""
        from .capabilities.terminal_session_capabilities import TerminalSessionExecutor
        
        # Terminal session management capability
        terminal_session_cap = Capability(
            name="terminal_session_management",
            description="Persistent terminal session management with history and context preservation",
            capability_type=CapabilityType.TERMINAL_SESSION_MANAGEMENT,
            required_parameters=["operation"],
            optional_parameters=["session_id", "name", "session_type", "terminal_type", "working_directory", "description", "tags", "parent_session_id", "command", "timeout", "status_filter", "session_type_filter", "tag_filter", "context_updates", "limit", "query", "group_name", "session_ids"],
            parameter_info={
                "operation": ParameterInfo(
                    name="operation",
                    type="string",
                    required=True,
                    description="Terminal session management operation to perform",
                    allowed_values=["create_session", "activate_session", "suspend_session", "terminate_session", "execute_command", "get_session_info", "list_sessions", "update_context", "get_history", "search_history", "create_group", "execute_in_group", "get_stats"]
                ),
                "session_id": ParameterInfo(
                    name="session_id",
                    type="string",
                    required=False,
                    description="Terminal session ID"
                ),
                "name": ParameterInfo(
                    name="name",
                    type="string",
                    required=False,
                    description="Session name"
                ),
                "session_type": ParameterInfo(
                    name="session_type",
                    type="string",
                    required=False,
                    description="Type of session",
                    allowed_values=["interactive", "batch", "script", "monitoring", "debug"],
                    default_value="interactive"
                ),
                "terminal_type": ParameterInfo(
                    name="terminal_type",
                    type="string",
                    required=False,
                    description="Type of terminal",
                    allowed_values=["powershell", "cmd", "bash", "zsh", "fish", "wsl"]
                ),
                "working_directory": ParameterInfo(
                    name="working_directory",
                    type="string",
                    required=False,
                    description="Working directory for session"
                ),
                "description": ParameterInfo(
                    name="description",
                    type="string",
                    required=False,
                    description="Session description"
                ),
                "tags": ParameterInfo(
                    name="tags",
                    type="array",
                    required=False,
                    description="Session tags"
                ),
                "parent_session_id": ParameterInfo(
                    name="parent_session_id",
                    type="string",
                    required=False,
                    description="Parent session ID for nested sessions"
                ),
                "command": ParameterInfo(
                    name="command",
                    type="string",
                    required=False,
                    description="Command to execute"
                ),
                "timeout": ParameterInfo(
                    name="timeout",
                    type="integer",
                    required=False,
                    description="Command timeout in seconds",
                    default_value=30
                ),
                "status_filter": ParameterInfo(
                    name="status_filter",
                    type="string",
                    required=False,
                    description="Filter sessions by status",
                    allowed_values=["active", "inactive", "suspended", "terminated", "error"]
                ),
                "session_type_filter": ParameterInfo(
                    name="session_type_filter",
                    type="string",
                    required=False,
                    description="Filter sessions by type",
                    allowed_values=["interactive", "batch", "script", "monitoring", "debug"]
                ),
                "tag_filter": ParameterInfo(
                    name="tag_filter",
                    type="string",
                    required=False,
                    description="Filter sessions by tag"
                ),
                "context_updates": ParameterInfo(
                    name="context_updates",
                    type="object",
                    required=False,
                    description="Context updates to apply"
                ),
                "limit": ParameterInfo(
                    name="limit",
                    type="integer",
                    required=False,
                    description="Limit for history results",
                    default_value=100
                ),
                "query": ParameterInfo(
                    name="query",
                    type="string",
                    required=False,
                    description="Search query for history"
                ),
                "group_name": ParameterInfo(
                    name="group_name",
                    type="string",
                    required=False,
                    description="Name for session group"
                ),
                "session_ids": ParameterInfo(
                    name="session_ids",
                    type="array",
                    required=False,
                    description="Session IDs for group"
                )
            }
        )
        await self.register_capability(terminal_session_cap)
        self.executors["terminal_session_management"] = TerminalSessionExecutor()
    
    async def _register_logging_analytics_capabilities(self):
        """Register logging and analytics capabilities"""
        try:
            from .capabilities.logging_analytics_capabilities import LoggingAnalyticsExecutor
            
            executor = LoggingAnalyticsExecutor()
            await executor.initialize()
            
            # Logging and analytics capability
            logging_analytics_cap = Capability(
                name="logging_analytics",
                description="Comprehensive logging, analytics, and monitoring capabilities",
                capability_type=CapabilityType.LOGGING_ANALYTICS,
                required_parameters=["action"],
                optional_parameters=["level", "event_type", "message", "session_id", "user_id", "component", "metadata", "tags", "duration", "success", "metric_type", "name", "value", "unit", "labels", "start_time", "end_time", "report_type", "query", "limit", "data_type", "format", "hours"],
                parameter_info={
                    "action": ParameterInfo(
                        name="action",
                        type="string",
                        required=True,
                        description="Logging and analytics action to perform",
                        allowed_values=["log_event", "record_metric", "generate_report", "get_real_time_metrics", "get_performance_stats", "search_logs", "get_session_analytics", "export_data", "system_health_check", "performance_analysis"]
                    ),
                    "level": ParameterInfo(
                        name="level",
                        type="string",
                        required=False,
                        description="Log level",
                        allowed_values=["debug", "info", "warning", "error", "critical"],
                        default_value="info"
                    ),
                    "event_type": ParameterInfo(
                        name="event_type",
                        type="string",
                        required=False,
                        description="Type of event to log",
                        allowed_values=["command_execution", "ai_processing", "browser_automation", "file_operation", "system_operation", "user_interaction", "error_event", "performance_metric", "security_event", "remote_control"],
                        default_value="user_interaction"
                    ),
                    "message": ParameterInfo(
                        name="message",
                        type="string",
                        required=False,
                        description="Log message content"
                    ),
                    "session_id": ParameterInfo(
                        name="session_id",
                        type="string",
                        required=False,
                        description="Session identifier"
                    ),
                    "user_id": ParameterInfo(
                        name="user_id",
                        type="string",
                        required=False,
                        description="User identifier"
                    ),
                    "component": ParameterInfo(
                        name="component",
                        type="string",
                        required=False,
                        description="Component name"
                    ),
                    "metadata": ParameterInfo(
                        name="metadata",
                        type="object",
                        required=False,
                        description="Additional metadata"
                    ),
                    "tags": ParameterInfo(
                        name="tags",
                        type="array",
                        required=False,
                        description="Event tags"
                    ),
                    "duration": ParameterInfo(
                        name="duration",
                        type="number",
                        required=False,
                        description="Execution duration in seconds"
                    ),
                    "success": ParameterInfo(
                        name="success",
                        type="boolean",
                        required=False,
                        description="Operation success status"
                    ),
                    "metric_type": ParameterInfo(
                        name="metric_type",
                        type="string",
                        required=False,
                        description="Type of metric",
                        allowed_values=["execution_time", "success_rate", "error_rate", "resource_usage", "user_engagement", "system_performance", "network_latency", "throughput"],
                        default_value="execution_time"
                    ),
                    "name": ParameterInfo(
                        name="name",
                        type="string",
                        required=False,
                        description="Metric or query name"
                    ),
                    "value": ParameterInfo(
                        name="value",
                        type="any",
                        required=False,
                        description="Metric value"
                    ),
                    "unit": ParameterInfo(
                        name="unit",
                        type="string",
                        required=False,
                        description="Measurement unit"
                    ),
                    "labels": ParameterInfo(
                        name="labels",
                        type="object",
                        required=False,
                        description="Metric labels"
                    ),
                    "start_time": ParameterInfo(
                        name="start_time",
                        type="string",
                        required=False,
                        description="Start time for reports/queries"
                    ),
                    "end_time": ParameterInfo(
                        name="end_time",
                        type="string",
                        required=False,
                        description="End time for reports/queries"
                    ),
                    "report_type": ParameterInfo(
                        name="report_type",
                        type="string",
                        required=False,
                        description="Type of report to generate",
                        default_value="comprehensive"
                    ),
                    "query": ParameterInfo(
                        name="query",
                        type="string",
                        required=False,
                        description="Search query"
                    ),
                    "limit": ParameterInfo(
                        name="limit",
                        type="number",
                        required=False,
                        description="Limit for search results",
                        default_value=100
                    ),
                    "data_type": ParameterInfo(
                        name="data_type",
                        type="string",
                        required=False,
                        description="Type of data to export",
                        allowed_values=["logs", "metrics", "reports", "all"],
                        default_value="all"
                    ),
                    "format": ParameterInfo(
                        name="format",
                        type="string",
                        required=False,
                        description="Export format",
                        allowed_values=["json", "csv"],
                        default_value="json"
                    ),
                    "hours": ParameterInfo(
                        name="hours",
                        type="number",
                        required=False,
                        description="Time range in hours for analysis",
                        default_value=24
                    )
                }
            )
            await self.register_capability(logging_analytics_cap)
            self.executors["logging_analytics"] = executor
            
            self.logger.info("Logging and analytics capabilities registered successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to register logging analytics capabilities: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Cleanup all executors
            for executor in self.executors.values():
                if hasattr(executor, 'cleanup'):
                    await executor.cleanup()
            
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
    elif not _capability_manager._is_initialized:
        await _capability_manager.initialize()
    return _capability_manager

async def cleanup_capability_manager():
    """Cleanup global capability manager"""
    global _capability_manager
    if _capability_manager:
        await _capability_manager.cleanup()
        _capability_manager = None
