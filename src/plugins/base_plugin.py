"""
Base Plugin Interface for JARVIS Computer Assistant
Defines the standard interface that all plugins must implement
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import asyncio
import threading
import time


class PluginType(Enum):
    """Plugin types for categorization"""
    VOICE = "voice"
    AI = "ai"
    SYSTEM = "system"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    ENTERTAINMENT = "entertainment"
    UTILITY = "utility"
    INTEGRATION = "integration"


class PluginStatus(Enum):
    """Plugin status states"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    LOADING = "loading"
    ERROR = "error"
    UNLOADED = "unloaded"


@dataclass
class PluginInfo:
    """Plugin information metadata"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str]
    config_schema: Optional[Dict[str, Any]] = None
    min_jarvis_version: str = "1.0.0"
    max_jarvis_version: Optional[str] = None


@dataclass
class PluginConfig:
    """Plugin configuration"""
    enabled: bool = True
    settings: Dict[str, Any] = None
    auto_start: bool = True
    priority: int = 0
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}


class BasePlugin(ABC):
    """
    Base class for all JARVIS plugins
    Provides standard interface and common functionality
    """
    
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        self.info = plugin_info
        self.config = config or PluginConfig()
        self.status = PluginStatus.UNLOADED
        self.logger = logging.getLogger(f"plugin.{self.info.name}")
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._lock = threading.Lock()
        self._start_time: Optional[float] = None
        self._error_count = 0
        self._last_error: Optional[str] = None
        
    @property
    def is_running(self) -> bool:
        """Check if plugin is currently running"""
        return self._running and self.status == PluginStatus.ENABLED
    
    @property
    def uptime(self) -> float:
        """Get plugin uptime in seconds"""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time
    
    @property
    def error_count(self) -> int:
        """Get total error count"""
        return self._error_count
    
    @property
    def last_error(self) -> Optional[str]:
        """Get last error message"""
        return self._last_error
    
    def add_event_handler(self, event: str, handler: Callable) -> None:
        """Add event handler for plugin events"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        self.logger.debug(f"Added event handler for '{event}'")
    
    def remove_event_handler(self, event: str, handler: Callable) -> None:
        """Remove event handler"""
        if event in self._event_handlers:
            try:
                self._event_handlers[event].remove(handler)
                self.logger.debug(f"Removed event handler for '{event}'")
            except ValueError:
                pass
    
    def emit_event(self, event: str, data: Any = None) -> None:
        """Emit event to all registered handlers"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(event, data))
                    else:
                        handler(event, data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for '{event}': {e}")
    
    async def load(self) -> bool:
        """Load the plugin (async initialization)"""
        try:
            with self._lock:
                if self.status != PluginStatus.UNLOADED:
                    return False
                
                self.status = PluginStatus.LOADING
                self.logger.info(f"Loading plugin: {self.info.name}")
                
                # Initialize plugin
                success = await self._initialize()
                
                if success:
                    self.status = PluginStatus.ENABLED
                    self.logger.info(f"Plugin loaded successfully: {self.info.name}")
                    self.emit_event("plugin_loaded", {"plugin": self.info.name})
                else:
                    self.status = PluginStatus.ERROR
                    self.logger.error(f"Failed to load plugin: {self.info.name}")
                    self.emit_event("plugin_load_failed", {"plugin": self.info.name})
                
                return success
                
        except Exception as e:
            self.status = PluginStatus.ERROR
            self._error_count += 1
            self._last_error = str(e)
            self.logger.error(f"Error loading plugin {self.info.name}: {e}")
            self.emit_event("plugin_error", {"plugin": self.info.name, "error": str(e)})
            return False
    
    async def unload(self) -> bool:
        """Unload the plugin (cleanup)"""
        try:
            with self._lock:
                if self.status == PluginStatus.UNLOADED:
                    return True
                
                self.logger.info(f"Unloading plugin: {self.info.name}")
                
                # Stop if running
                if self._running:
                    await self.stop()
                
                # Cleanup plugin
                await self._cleanup()
                
                self.status = PluginStatus.UNLOADED
                self.logger.info(f"Plugin unloaded: {self.info.name}")
                self.emit_event("plugin_unloaded", {"plugin": self.info.name})
                
                return True
                
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self.logger.error(f"Error unloading plugin {self.info.name}: {e}")
            self.emit_event("plugin_error", {"plugin": self.info.name, "error": str(e)})
            return False
    
    async def start(self) -> bool:
        """Start the plugin"""
        try:
            with self._lock:
                if self.status != PluginStatus.ENABLED or self._running:
                    return False
                
                self.logger.info(f"Starting plugin: {self.info.name}")
                
                # Start plugin
                success = await self._start()
                
                if success:
                    self._running = True
                    self._start_time = time.time()
                    self.logger.info(f"Plugin started: {self.info.name}")
                    self.emit_event("plugin_started", {"plugin": self.info.name})
                else:
                    self.logger.error(f"Failed to start plugin: {self.info.name}")
                    self.emit_event("plugin_start_failed", {"plugin": self.info.name})
                
                return success
                
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self.logger.error(f"Error starting plugin {self.info.name}: {e}")
            self.emit_event("plugin_error", {"plugin": self.info.name, "error": str(e)})
            return False
    
    async def stop(self) -> bool:
        """Stop the plugin"""
        try:
            with self._lock:
                if not self._running:
                    return True
                
                self.logger.info(f"Stopping plugin: {self.info.name}")
                
                # Stop plugin
                await self._stop()
                
                self._running = False
                self._start_time = None
                self.logger.info(f"Plugin stopped: {self.info.name}")
                self.emit_event("plugin_stopped", {"plugin": self.info.name})
                
                return True
                
        except Exception as e:
            self._error_count += 1
            self._last_error = str(e)
            self.logger.error(f"Error stopping plugin {self.info.name}: {e}")
            self.emit_event("plugin_error", {"plugin": self.info.name, "error": str(e)})
            return False
    
    def enable(self) -> bool:
        """Enable the plugin"""
        if self.status == PluginStatus.DISABLED:
            self.status = PluginStatus.ENABLED
            self.logger.info(f"Plugin enabled: {self.info.name}")
            self.emit_event("plugin_enabled", {"plugin": self.info.name})
            return True
        return False
    
    def disable(self) -> bool:
        """Disable the plugin"""
        if self.status == PluginStatus.ENABLED:
            self.status = PluginStatus.DISABLED
            self.logger.info(f"Plugin disabled: {self.info.name}")
            self.emit_event("plugin_disabled", {"plugin": self.info.name})
            return True
        return False
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get comprehensive plugin status information"""
        return {
            "name": self.info.name,
            "version": self.info.version,
            "status": self.status.value,
            "running": self._running,
            "uptime": self.uptime,
            "error_count": self._error_count,
            "last_error": self._last_error,
            "enabled": self.config.enabled,
            "priority": self.config.priority,
            "plugin_type": self.info.plugin_type.value
        }
    
    # Abstract methods that must be implemented by plugins
    
    @abstractmethod
    async def _initialize(self) -> bool:
        """Initialize the plugin (implement in subclass)"""
        pass
    
    @abstractmethod
    async def _cleanup(self) -> None:
        """Cleanup plugin resources (implement in subclass)"""
        pass
    
    @abstractmethod
    async def _start(self) -> bool:
        """Start the plugin (implement in subclass)"""
        pass
    
    @abstractmethod
    async def _stop(self) -> None:
        """Stop the plugin (implement in subclass)"""
        pass
    
    # Optional methods that can be overridden
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle voice commands (override if needed)"""
        return None
    
    async def handle_ai_request(self, request: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle AI requests (override if needed)"""
        return None
    
    async def handle_system_event(self, event: str, data: Any = None) -> None:
        """Handle system events (override if needed)"""
        pass
    
    def get_commands(self) -> List[str]:
        """Get list of supported commands (override if needed)"""
        return []
    
    def get_capabilities(self) -> List[str]:
        """Get list of plugin capabilities (override if needed)"""
        return []
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate plugin configuration (override if needed)"""
        return []
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema (override if needed)"""
        return self.info.config_schema or {}
