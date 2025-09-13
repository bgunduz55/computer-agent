"""
Plugin Manager for JARVIS Computer Assistant
Manages plugin lifecycle, loading, and communication
"""

import asyncio
import logging
import importlib
import importlib.util
import inspect
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
import threading
import time
from dataclasses import dataclass

from .base_plugin import BasePlugin, PluginInfo, PluginConfig, PluginType, PluginStatus


@dataclass
class PluginLoadResult:
    """Result of plugin loading operation"""
    success: bool
    plugin: Optional[BasePlugin] = None
    error: Optional[str] = None


class PluginManager:
    """
    Manages all plugins in the JARVIS system
    Handles loading, unloading, starting, stopping, and communication
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self._plugin_directories: List[Path] = []
        self._running = False
        self._lock = threading.Lock()
        self._event_handlers: Dict[str, List[callable]] = {}
        self._plugin_order: List[str] = []
        
        # Initialize plugin directories
        self._setup_plugin_directories()
        
    def _setup_plugin_directories(self) -> None:
        """Setup plugin directories"""
        # Core plugins directory
        core_plugins_dir = Path(__file__).parent / "core_plugins"
        if core_plugins_dir.exists():
            self._plugin_directories.append(core_plugins_dir)
        
        # Community plugins directory
        community_plugins_dir = Path(__file__).parent / "community_plugins"
        if community_plugins_dir.exists():
            self._plugin_directories.append(community_plugins_dir)
        
        # User plugins directory
        user_plugins_dir = Path.home() / ".jarvis" / "plugins"
        user_plugins_dir.mkdir(parents=True, exist_ok=True)
        self._plugin_directories.append(user_plugins_dir)
        
        self.logger.info(f"Plugin directories: {[str(d) for d in self._plugin_directories]}")
    
    def add_event_handler(self, event: str, handler: callable) -> None:
        """Add global event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
        self.logger.debug(f"Added global event handler for '{event}'")
    
    def remove_event_handler(self, event: str, handler: callable) -> None:
        """Remove global event handler"""
        if event in self._event_handlers:
            try:
                self._event_handlers[event].remove(handler)
                self.logger.debug(f"Removed global event handler for '{event}'")
            except ValueError:
                pass
    
    def emit_event(self, event: str, data: Any = None) -> None:
        """Emit global event"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(event, data))
                    else:
                        handler(event, data)
                except Exception as e:
                    self.logger.error(f"Error in global event handler for '{event}': {e}")
    
    async def initialize(self) -> bool:
        """Initialize plugin manager"""
        try:
            self.logger.info("Initializing plugin manager")
            
            # Discover and load plugin classes
            await self._discover_plugins()
            
            # Load enabled plugins
            await self._load_enabled_plugins()
            
            self._running = True
            self.logger.info("Plugin manager initialized successfully")
            self.emit_event("plugin_manager_initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin manager: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown plugin manager"""
        try:
            self.logger.info("Shutting down plugin manager")
            
            # Stop all running plugins
            await self._stop_all_plugins()
            
            # Unload all plugins
            await self._unload_all_plugins()
            
            self._running = False
            self.logger.info("Plugin manager shutdown complete")
            self.emit_event("plugin_manager_shutdown")
            
        except Exception as e:
            self.logger.error(f"Error during plugin manager shutdown: {e}")
    
    async def _discover_plugins(self) -> None:
        """Discover available plugin classes"""
        self.logger.info("Discovering plugins...")
        
        for plugin_dir in self._plugin_directories:
            if not plugin_dir.exists():
                continue
                
            # Look for Python files in plugin directory
            for py_file in plugin_dir.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                
                try:
                    # Import the module
                    module_name = f"plugins.{plugin_dir.name}.{py_file.stem}"
                    if module_name in sys.modules:
                        module = sys.modules[module_name]
                    else:
                        spec = importlib.util.spec_from_file_location(module_name, py_file)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                        else:
                            continue
                    
                    # Find plugin classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BasePlugin) and 
                            obj != BasePlugin and 
                            hasattr(obj, 'PLUGIN_INFO')):
                            
                            plugin_info = obj.PLUGIN_INFO
                            plugin_name = plugin_info.name
                            
                            if plugin_name not in self._plugin_classes:
                                self._plugin_classes[plugin_name] = obj
                                self.logger.info(f"Discovered plugin: {plugin_name}")
                            else:
                                self.logger.warning(f"Duplicate plugin name: {plugin_name}")
                                
                except Exception as e:
                    self.logger.error(f"Error discovering plugin in {py_file}: {e}")
                    continue
    
    async def _load_enabled_plugins(self) -> None:
        """Load all enabled plugins"""
        self.logger.info("Loading enabled plugins...")
        
        # Sort plugins by priority
        sorted_plugins = sorted(
            self._plugin_classes.items(),
            key=lambda x: getattr(x[1], 'PRIORITY', 0),
            reverse=True
        )
        
        for plugin_name, plugin_class in sorted_plugins:
            try:
                # Create plugin instance
                plugin_info = plugin_class.PLUGIN_INFO
                plugin_config = PluginConfig(
                    enabled=True,  # Default to enabled
                    auto_start=True
                )
                
                plugin = plugin_class(plugin_info, plugin_config)
                
                # Load the plugin
                success = await plugin.load()
                
                if success:
                    self._plugins[plugin_name] = plugin
                    self._plugin_order.append(plugin_name)
                    self.logger.info(f"Loaded plugin: {plugin_name}")
                    
                    # Auto-start if configured
                    if plugin_config.auto_start:
                        await plugin.start()
                else:
                    self.logger.error(f"Failed to load plugin: {plugin_name}")
                    
            except Exception as e:
                self.logger.error(f"Error loading plugin {plugin_name}: {e}")
                continue
    
    async def _stop_all_plugins(self) -> None:
        """Stop all running plugins"""
        self.logger.info("Stopping all plugins...")
        
        # Stop in reverse order
        for plugin_name in reversed(self._plugin_order):
            if plugin_name in self._plugins:
                plugin = self._plugins[plugin_name]
                if plugin.is_running:
                    await plugin.stop()
    
    async def _unload_all_plugins(self) -> None:
        """Unload all plugins"""
        self.logger.info("Unloading all plugins...")
        
        # Unload in reverse order
        for plugin_name in reversed(self._plugin_order):
            if plugin_name in self._plugins:
                plugin = self._plugins[plugin_name]
                await plugin.unload()
                del self._plugins[plugin_name]
        
        self._plugin_order.clear()
    
    async def load_plugin(self, plugin_name: str, config: PluginConfig = None) -> PluginLoadResult:
        """Load a specific plugin"""
        try:
            if plugin_name in self._plugins:
                return PluginLoadResult(
                    success=False,
                    error=f"Plugin '{plugin_name}' is already loaded"
                )
            
            if plugin_name not in self._plugin_classes:
                return PluginLoadResult(
                    success=False,
                    error=f"Plugin '{plugin_name}' not found"
                )
            
            plugin_class = self._plugin_classes[plugin_name]
            plugin_info = plugin_class.PLUGIN_INFO
            plugin_config = config or PluginConfig()
            
            plugin = plugin_class(plugin_info, plugin_config)
            success = await plugin.load()
            
            if success:
                self._plugins[plugin_name] = plugin
                self._plugin_order.append(plugin_name)
                self.logger.info(f"Loaded plugin: {plugin_name}")
                return PluginLoadResult(success=True, plugin=plugin)
            else:
                return PluginLoadResult(
                    success=False,
                    error=f"Failed to load plugin '{plugin_name}'"
                )
                
        except Exception as e:
            error_msg = f"Error loading plugin '{plugin_name}': {e}"
            self.logger.error(error_msg)
            return PluginLoadResult(success=False, error=error_msg)
    
    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        try:
            if plugin_name not in self._plugins:
                self.logger.warning(f"Plugin '{plugin_name}' is not loaded")
                return False
            
            plugin = self._plugins[plugin_name]
            
            # Stop if running
            if plugin.is_running:
                await plugin.stop()
            
            # Unload
            success = await plugin.unload()
            
            if success:
                del self._plugins[plugin_name]
                if plugin_name in self._plugin_order:
                    self._plugin_order.remove(plugin_name)
                self.logger.info(f"Unloaded plugin: {plugin_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin '{plugin_name}': {e}")
            return False
    
    async def start_plugin(self, plugin_name: str) -> bool:
        """Start a specific plugin"""
        try:
            if plugin_name not in self._plugins:
                self.logger.warning(f"Plugin '{plugin_name}' is not loaded")
                return False
            
            plugin = self._plugins[plugin_name]
            return await plugin.start()
            
        except Exception as e:
            self.logger.error(f"Error starting plugin '{plugin_name}': {e}")
            return False
    
    async def stop_plugin(self, plugin_name: str) -> bool:
        """Stop a specific plugin"""
        try:
            if plugin_name not in self._plugins:
                self.logger.warning(f"Plugin '{plugin_name}' is not loaded")
                return False
            
            plugin = self._plugins[plugin_name]
            return await plugin.stop()
            
        except Exception as e:
            self.logger.error(f"Error stopping plugin '{plugin_name}': {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a specific plugin"""
        return self._plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[BasePlugin]:
        """Get all plugins of a specific type"""
        return [
            plugin for plugin in self._plugins.values()
            if plugin.info.plugin_type == plugin_type
        ]
    
    def get_all_plugins(self) -> List[BasePlugin]:
        """Get all loaded plugins"""
        return list(self._plugins.values())
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all plugins"""
        return {
            "total_plugins": len(self._plugins),
            "running_plugins": len([p for p in self._plugins.values() if p.is_running]),
            "enabled_plugins": len([p for p in self._plugins.values() if p.status == PluginStatus.ENABLED]),
            "error_plugins": len([p for p in self._plugins.values() if p.status == PluginStatus.ERROR]),
            "plugins": {name: plugin.get_status_info() for name, plugin in self._plugins.items()}
        }
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle voice command through plugins"""
        for plugin_name in self._plugin_order:
            if plugin_name in self._plugins:
                plugin = self._plugins[plugin_name]
                if plugin.is_running:
                    try:
                        result = await plugin.handle_voice_command(command, context)
                        if result:
                            return result
                    except Exception as e:
                        self.logger.error(f"Error in plugin {plugin_name} voice command handler: {e}")
        
        return None
    
    async def handle_ai_request(self, request: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle AI request through plugins"""
        for plugin_name in self._plugin_order:
            if plugin_name in self._plugins:
                plugin = self._plugins[plugin_name]
                if plugin.is_running:
                    try:
                        result = await plugin.handle_ai_request(request, context)
                        if result:
                            return result
                    except Exception as e:
                        self.logger.error(f"Error in plugin {plugin_name} AI request handler: {e}")
        
        return None
    
    async def handle_system_event(self, event: str, data: Any = None) -> None:
        """Handle system event through plugins"""
        for plugin_name in self._plugin_order:
            if plugin_name in self._plugins:
                plugin = self._plugins[plugin_name]
                if plugin.is_running:
                    try:
                        await plugin.handle_system_event(event, data)
                    except Exception as e:
                        self.logger.error(f"Error in plugin {plugin_name} system event handler: {e}")


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


async def cleanup_plugin_manager() -> None:
    """Cleanup global plugin manager"""
    global _plugin_manager
    if _plugin_manager is not None:
        await _plugin_manager.shutdown()
        _plugin_manager = None
