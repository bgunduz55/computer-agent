"""
JARVIS Core - Main Application Controller

This module provides the main JARVIS application controller that integrates
all subsystems including voice recognition, AI integration, terminal control,
remote access, and settings management.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import signal
import sys
import os

# Core imports
from .platform import get_platform
from .platform.base_platform import BasePlatform

# Feature imports
from features.ai_integration import get_ai_manager, get_rag_system
from features.terminal_integration import get_terminal_manager, get_package_manager
from features.remote_control import get_websocket_server, get_remote_controller
from features.system_info import get_system_info_manager
from features.application_control import get_application_manager
from features.settings import get_settings_manager, SettingCategory
from plugins import get_plugin_manager
from .performance_manager import get_performance_manager
from .security_manager import get_security_manager
from .analytics_manager import get_analytics_manager

# Integration imports
from integrations.speech_engines import get_speech_manager

logger = logging.getLogger(__name__)

class JARVISCore:
    """Main JARVIS application controller"""
    
    def __init__(self):
        self.platform: Optional[BasePlatform] = None
        self.speech_manager = None
        self.ai_manager = None
        self.rag_system = None
        self.terminal_manager = None
        self.package_manager = None
        self.websocket_server = None
        self.remote_controller = None
        self.settings_manager = None
        self.system_info_manager = None
        self.application_manager = None
        self.plugin_manager = None
        self.performance_manager = None
        self.security_manager = None
        self.analytics_manager = None
        
        # State management
        self.is_running = False
        self.is_initialized = False
        self.is_listening = False
        self.is_processing = False
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        # Initialize logging
        self._setup_logging()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, "INFO", logging.INFO)
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "jarvis.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger.info("JARVIS Core logging initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self) -> bool:
        """Initialize JARVIS core and all subsystems"""
        try:
            logger.info("Initializing JARVIS Core...")
            
            # Initialize platform
            self.platform = get_platform()
            if not self.platform.initialize():
                logger.error("Failed to initialize platform")
                return False
            
            # Initialize settings manager
            self.settings_manager = get_settings_manager()
            logger.info("Settings manager initialized")
            
            # Initialize speech manager
            self.speech_manager = get_speech_manager()
            if not self.speech_manager.initialize():
                logger.error("Failed to initialize speech manager")
                return False
            logger.info("Speech manager initialized")
            
            # Initialize AI manager
            self.ai_manager = get_ai_manager()
            if not self.ai_manager.initialize():
                logger.error("Failed to initialize AI manager")
                return False
            logger.info("AI manager initialized")
            
            # Initialize RAG system
            self.rag_system = get_rag_system()
            if not await self.rag_system.initialize():
                logger.error("Failed to initialize RAG system")
                return False
            logger.info("RAG system initialized")
            
            # Initialize system info manager
            self.system_info_manager = get_system_info_manager()
            if not self.system_info_manager.initialize():
                logger.error("Failed to initialize system info manager")
                return False
            logger.info("System info manager initialized")
            
            # Initialize application manager
            self.application_manager = get_application_manager()
            if not self.application_manager.initialize():
                logger.error("Failed to initialize application manager")
                return False
            logger.info("Application manager initialized")

            # Initialize plugin manager
            self.plugin_manager = get_plugin_manager()
            if not await self.plugin_manager.initialize():
                logger.error("Failed to initialize plugin manager")
                return False
            logger.info("Plugin manager initialized")

            # Initialize performance manager
            self.performance_manager = get_performance_manager()
            if not await self.performance_manager.initialize():
                logger.error("Failed to initialize performance manager")
                return False
            logger.info("Performance manager initialized")

            # Initialize security manager
            self.security_manager = get_security_manager()
            if not await self.security_manager.initialize():
                logger.error("Failed to initialize security manager")
                return False
            logger.info("Security manager initialized")

            # Initialize analytics manager
            self.analytics_manager = get_analytics_manager()
            if not await self.analytics_manager.initialize():
                logger.error("Failed to initialize analytics manager")
                return False
            logger.info("Analytics manager initialized")
            
            # Initialize terminal manager
            self.terminal_manager = get_terminal_manager()
            if not self.terminal_manager.initialize():
                logger.error("Failed to initialize terminal manager")
                return False
            logger.info("Terminal manager initialized")
            
            # Initialize package manager
            self.package_manager = get_package_manager()
            if not await self.package_manager.initialize():
                logger.error("Failed to initialize package manager")
                return False
            logger.info("Package manager initialized")
            
            # Initialize remote control if enabled
            if self.settings_manager.remote.websocket_enabled:
                self.websocket_server = get_websocket_server()
                if not await self.websocket_server.initialize():
                    logger.error("Failed to initialize WebSocket server")
                    return False
                logger.info("WebSocket server initialized")
                
                self.remote_controller = get_remote_controller()
                if not await self.remote_controller.initialize():
                    logger.error("Failed to initialize remote controller")
                    return False
                logger.info("Remote controller initialized")
            
            # Setup event handlers
            self._setup_event_handlers()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            logger.info("JARVIS Core initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize JARVIS Core: {e}")
            return False
    
    def _setup_event_handlers(self):
        """Setup event handlers for system integration"""
        # TODO: Implement event handlers when manager classes support them
        # Voice recognition events
        # self.speech_manager.add_listener('voice_recognized', self._on_voice_recognized)
        # self.speech_manager.add_listener('voice_error', self._on_voice_error)
        
        # AI response events
        # self.ai_manager.add_listener('ai_response', self._on_ai_response)
        # self.ai_manager.add_listener('ai_error', self._on_ai_error)
        
        # Terminal events
        # self.terminal_manager.add_listener('command_completed', self._on_command_completed)
        # self.terminal_manager.add_listener('command_error', self._on_command_error)
        
        # Remote control events
        # if self.remote_controller:
        #     self.remote_controller.add_listener('remote_command', self._on_remote_command)
        #     self.remote_controller.add_listener('remote_connected', self._on_remote_connected)
        #     self.remote_controller.add_listener('remote_disconnected', self._on_remote_disconnected)
        
        # Settings events
        # self.settings_manager.add_listener('setting_changed', self._on_setting_changed)
        pass
    
    async def _start_background_tasks(self):
        """Start background tasks"""
        # Performance monitoring
        if self.settings_manager.performance.metrics_collection:
            task = asyncio.create_task(self._performance_monitor())
            self.background_tasks.append(task)
        
        # Auto backup
        if self.settings_manager.system.backup_enabled:
            task = asyncio.create_task(self._auto_backup())
            self.background_tasks.append(task)
        
        # Health check
        task = asyncio.create_task(self._health_check())
        self.background_tasks.append(task)
    
    async def start(self) -> bool:
        """Start JARVIS core services"""
        try:
            if not self.is_initialized:
                logger.error("JARVIS Core not initialized")
                return False
            
            logger.info("Starting JARVIS Core services...")
            
            # Start voice recognition if auto listen is enabled
            if self.settings_manager.voice.auto_listen:
                await self.start_listening()
            
            # Start WebSocket server if enabled
            if self.websocket_server and self.settings_manager.remote.websocket_enabled:
                await self.websocket_server.start()
                logger.info("WebSocket server started")
            
            self.is_running = True
            logger.info("JARVIS Core services started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start JARVIS Core services: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop JARVIS core services"""
        try:
            logger.info("Stopping JARVIS Core services...")
            
            # Stop listening
            if self.is_listening:
                await self.stop_listening()
            
            # Stop WebSocket server
            if self.websocket_server:
                try:
                    logger.info("Stopping WebSocket server...")
                    await asyncio.wait_for(self.websocket_server.stop(), timeout=5.0)
                    logger.info("WebSocket server stopped successfully")
                except asyncio.TimeoutError:
                    logger.warning("WebSocket server stop timeout")
                except Exception as e:
                    logger.warning(f"Error stopping WebSocket server: {e}")
                finally:
                    # Ensure WebSocket server is properly stopped
                    self.websocket_server = None
            
            # Cancel background tasks with proper cleanup
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=0.5)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass
                    except Exception as e:
                        logger.warning(f"Error cancelling background task: {e}")
            
            # Clear background tasks
            self.background_tasks.clear()
            
            self.is_running = False
            logger.info("JARVIS Core services stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop JARVIS Core services: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown JARVIS core completely"""
        try:
            logger.info("Shutting down JARVIS Core...")
            
            # Stop services first
            await self.stop()
            
            # Cleanup subsystems with error handling
            cleanup_tasks = []
            
            if self.speech_manager:
                try:
                    self.speech_manager.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up speech manager: {e}")
            
            if self.ai_manager:
                try:
                    self.ai_manager.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up AI manager: {e}")
            
            if self.rag_system:
                try:
                    await self.rag_system.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up RAG system: {e}")
            
            if self.system_info_manager:
                try:
                    self.system_info_manager.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up system info manager: {e}")
            
            if self.application_manager:
                try:
                    self.application_manager.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up application manager: {e}")

            if self.plugin_manager:
                try:
                    await self.plugin_manager.shutdown()
                except Exception as e:
                    logger.warning(f"Error shutting down plugin manager: {e}")

            if self.performance_manager:
                try:
                    await self.performance_manager.shutdown()
                except Exception as e:
                    logger.warning(f"Error shutting down performance manager: {e}")

            if self.security_manager:
                try:
                    await self.security_manager.shutdown()
                except Exception as e:
                    logger.warning(f"Error shutting down security manager: {e}")

            if self.analytics_manager:
                try:
                    await self.analytics_manager.shutdown()
                except Exception as e:
                    logger.warning(f"Error shutting down analytics manager: {e}")
            
            if self.terminal_manager:
                try:
                    self.terminal_manager.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up terminal manager: {e}")
            
            if self.package_manager:
                try:
                    self.package_manager.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up package manager: {e}")
            
            if self.websocket_server:
                try:
                    await self.websocket_server.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up WebSocket server: {e}")
            
            if self.remote_controller:
                try:
                    await self.remote_controller.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up remote controller: {e}")
            
            if self.platform:
                try:
                    self.platform.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up platform: {e}")
            
            logger.info("JARVIS Core shutdown completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to shutdown JARVIS Core: {e}")
            return False
    
    async def start_listening(self) -> bool:
        """Start voice recognition"""
        try:
            if self.is_listening:
                return True
            
            if not self.speech_manager:
                logger.error("Speech manager not initialized")
                return False
            
            await self.speech_manager.start_listening()
            self.is_listening = True
            logger.info("Voice recognition started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start voice recognition: {e}")
            return False
    
    async def stop_listening(self) -> bool:
        """Stop voice recognition"""
        try:
            if not self.is_listening:
                return True
            
            if not self.speech_manager:
                return True
            
            await self.speech_manager.stop_listening()
            self.is_listening = False
            logger.info("Voice recognition stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop voice recognition: {e}")
            return False
    
    async def process_voice_command(self, command: str) -> Optional[str]:
        """Process voice command through plugins and AI"""
        start_time = time.time()
        try:
            if self.is_processing:
                return "Already processing a command"
            
            self.is_processing = True
            logger.info(f"Processing voice command: {command}")
            
            # Validate command security
            if self.security_manager:
                is_valid = await self.security_manager.validate_command(command, "voice_user")
                if not is_valid:
                    logger.warning(f"Command blocked by security: {command}")
                    return "Command blocked for security reasons."
            
            # Track the voice command
            if self.analytics_manager:
                self.analytics_manager.track_user_action(
                    "voice_command", 
                    {"command": command[:100]},  # Only store first 100 chars for privacy
                    "voice_user"
                )
            
            # First, try to handle command through plugins
            plugin_response = None
            if self.plugin_manager:
                plugin_response = await self.plugin_manager.handle_voice_command(command)
            
            if plugin_response:
                logger.info(f"Plugin Response: {plugin_response}")
                self.speech_manager.speak_text(plugin_response)
                return plugin_response
            
            # If no plugin handled it, use AI
            ai_response = await self.ai_manager.generate_response(command)
            
            if not ai_response:
                return "Sorry, I couldn't process that command"
            
            # Check if response contains executable commands
            if self._is_executable_command(ai_response.content):
                # Execute command
                result = await self.terminal_manager.execute_command(ai_response.content)
                if result:
                    return f"Executed: {ai_response.content}\nResult: {result}"
                else:
                    return f"Failed to execute: {ai_response.content}"
            else:
                # Speak response
                self.speech_manager.speak_text(ai_response.content)
                return ai_response.content
            
        except Exception as e:
            logger.error(f"Failed to process voice command: {e}")
            if self.performance_manager:
                self.performance_manager.record_error()
            return f"Error processing command: {e}"
        finally:
            # Record response time and analytics
            response_time_ms = (time.time() - start_time) * 1000
            if self.performance_manager:
                self.performance_manager.record_response_time(response_time_ms)
            if self.analytics_manager:
                self.analytics_manager.record_metric("response_time", response_time_ms, "ms")
            self.is_processing = False
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current context for AI processing"""
        return {
            "platform": self.platform.get_platform_name() if self.platform else "unknown",
            "is_listening": self.is_listening,
            "is_processing": self.is_processing,
            "settings": self.settings_manager.get_settings_summary() if self.settings_manager else {}
        }
    
    async def update_remote_settings(self, host: str = None, port: int = None, 
                                   enabled: bool = None, **kwargs) -> bool:
        """Update remote control settings and restart WebSocket server if needed"""
        try:
            if not self.settings_manager:
                logger.error("Settings manager not initialized")
                return False
            
            # Update settings
            updated = self.settings_manager.update_remote_settings(
                host=host, port=port, enabled=enabled, **kwargs
            )
            
            if updated and self.websocket_server:
                # Check if host or port changed
                current_settings = self.settings_manager.get_remote_settings()
                if (host and host != current_settings.get('websocket_host')) or \
                   (port and port != current_settings.get('websocket_port')):
                    # Restart WebSocket server with new settings
                    logger.info("Restarting WebSocket server with new settings...")
                    await self.websocket_server.restart()
                    logger.info("WebSocket server restarted successfully")
            
            return updated
            
        except Exception as e:
            logger.error(f"Failed to update remote settings: {e}")
            return False
    
    def get_remote_settings(self) -> Dict[str, Any]:
        """Get current remote control settings"""
        if not self.settings_manager:
            return {}
        return self.settings_manager.get_remote_settings()
    
    def validate_remote_settings(self) -> List[str]:
        """Validate remote control settings"""
        if not self.settings_manager:
            return ["Settings manager not initialized"]
        return self.settings_manager.validate_remote_settings()
    
    def _is_executable_command(self, text: str) -> bool:
        """Check if text contains executable commands"""
        # Simple heuristic - can be enhanced
        executable_keywords = [
            "run", "execute", "start", "open", "launch", "install", "update",
            "git", "npm", "pip", "apt", "yum", "brew", "choco", "winget"
        ]
        return any(keyword in text.lower() for keyword in executable_keywords)
    
    # Event handlers
    def _on_voice_recognized(self, event: str, data: Dict[str, Any]):
        """Handle voice recognition events"""
        command = data.get('text', '')
        confidence = data.get('confidence', 0.0)
        
        logger.info(f"Voice recognized: {command} (confidence: {confidence})")
        
        # Process command if confidence is high enough
        if confidence >= self.settings_manager.voice.confidence_threshold:
            asyncio.create_task(self.process_voice_command(command))
        else:
            logger.warning(f"Low confidence voice recognition: {confidence}")
    
    def _on_voice_error(self, event: str, data: Dict[str, Any]):
        """Handle voice recognition errors"""
        error = data.get('error', 'Unknown error')
        logger.error(f"Voice recognition error: {error}")
    
    def _on_ai_response(self, event: str, data: Dict[str, Any]):
        """Handle AI response events"""
        response = data.get('response', '')
        provider = data.get('provider', 'unknown')
        logger.info(f"AI response from {provider}: {response}")
    
    def _on_ai_error(self, event: str, data: Dict[str, Any]):
        """Handle AI errors"""
        error = data.get('error', 'Unknown error')
        logger.error(f"AI error: {error}")
    
    def _on_command_completed(self, event: str, data: Dict[str, Any]):
        """Handle command completion events"""
        command = data.get('command', '')
        result = data.get('result', '')
        logger.info(f"Command completed: {command}")
    
    def _on_command_error(self, event: str, data: Dict[str, Any]):
        """Handle command errors"""
        command = data.get('command', '')
        error = data.get('error', 'Unknown error')
        logger.error(f"Command error: {command} - {error}")
    
    def _on_remote_command(self, event: str, data: Dict[str, Any]):
        """Handle remote commands"""
        command = data.get('command', '')
        client_id = data.get('client_id', 'unknown')
        logger.info(f"Remote command from {client_id}: {command}")
        
        # Process remote command
        asyncio.create_task(self.process_voice_command(command))
    
    def _on_remote_connected(self, event: str, data: Dict[str, Any]):
        """Handle remote client connection"""
        client_id = data.get('client_id', 'unknown')
        logger.info(f"Remote client connected: {client_id}")
    
    def _on_remote_disconnected(self, event: str, data: Dict[str, Any]):
        """Handle remote client disconnection"""
        client_id = data.get('client_id', 'unknown')
        logger.info(f"Remote client disconnected: {client_id}")
    
    def _on_setting_changed(self, event: str, data: Dict[str, Any]):
        """Handle settings changes"""
        category = data.get('category', 'unknown')
        key = data.get('key', 'unknown')
        value = data.get('value')
        logger.info(f"Setting changed: {category}.{key} = {value}")
        
        # Handle specific setting changes
        if category == 'voice' and key == 'auto_listen':
            if value and not self.is_listening:
                asyncio.create_task(self.start_listening())
            elif not value and self.is_listening:
                asyncio.create_task(self.stop_listening())
    
    # Background tasks
    async def _performance_monitor(self):
        """Monitor system performance"""
        while self.is_running:
            try:
                # Monitor memory usage
                memory_usage = self.platform.get_memory_usage()
                if memory_usage > self.settings_manager.performance.max_memory_usage:
                    logger.warning(f"High memory usage: {memory_usage}MB")
                
                # Monitor CPU usage
                cpu_usage = self.platform.get_cpu_usage()
                if cpu_usage > self.settings_manager.performance.max_cpu_usage:
                    logger.warning(f"High CPU usage: {cpu_usage}%")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _auto_backup(self):
        """Automatic backup task"""
        while self.is_running:
            try:
                await asyncio.sleep(self.settings_manager.system.backup_interval * 3600)
                
                # Create backup
                backup_path = Path("backups") / f"jarvis_backup_{int(time.time())}.json"
                backup_path.parent.mkdir(exist_ok=True)
                
                if self.settings_manager.export_settings(str(backup_path)):
                    logger.info(f"Auto backup created: {backup_path}")
                
            except Exception as e:
                logger.error(f"Auto backup error: {e}")
    
    async def _health_check(self):
        """Health check task"""
        while self.is_running:
            try:
                # Check if all subsystems are healthy
                health_status = {
                    "speech_manager": self.speech_manager is not None,
                    "ai_manager": self.ai_manager is not None,
                    "rag_system": self.rag_system is not None,
                    "terminal_manager": self.terminal_manager is not None,
                    "package_manager": self.package_manager is not None,
                    "websocket_server": self.websocket_server is not None if self.settings_manager.remote.websocket_enabled else True,
                    "remote_controller": self.remote_controller is not None if self.settings_manager.remote.websocket_enabled else True
                }
                
                unhealthy_services = [service for service, healthy in health_status.items() if not healthy]
                if unhealthy_services:
                    logger.warning(f"Unhealthy services: {unhealthy_services}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(300)
    
    # Public API methods
    def get_status(self) -> Dict[str, Any]:
        """Get current JARVIS status"""
        return {
            "is_running": self.is_running,
            "is_initialized": self.is_initialized,
            "is_listening": self.is_listening,
            "is_processing": self.is_processing,
            "platform": self.platform.get_platform_name() if self.platform else "unknown",
            "services": {
                "speech_manager": self.speech_manager is not None,
                "ai_manager": self.ai_manager is not None,
                "rag_system": self.rag_system is not None,
            "system_info_manager": self.system_info_manager is not None,
            "application_manager": self.application_manager is not None,
            "plugin_manager": self.plugin_manager is not None,
            "performance_manager": self.performance_manager is not None,
            "security_manager": self.security_manager is not None,
            "analytics_manager": self.analytics_manager is not None,
                "terminal_manager": self.terminal_manager is not None,
                "package_manager": self.package_manager is not None,
                "websocket_server": self.websocket_server is not None,
                "remote_controller": self.remote_controller is not None
            }
        }
    
    def add_event_handler(self, event: str, handler: Callable):
        """Add event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def remove_event_handler(self, event: str, handler: Callable):
        """Remove event handler"""
        if event in self.event_handlers:
            try:
                self.event_handlers[event].remove(handler)
            except ValueError:
                pass

# Global JARVIS Core instance
_jarvis_core: Optional[JARVISCore] = None

def get_jarvis_core() -> JARVISCore:
    """Get global JARVIS Core instance"""
    global _jarvis_core
    if _jarvis_core is None:
        _jarvis_core = JARVISCore()
    return _jarvis_core

async def cleanup_jarvis_core() -> None:
    """Cleanup global JARVIS Core instance"""
    global _jarvis_core
    if _jarvis_core:
        await _jarvis_core.shutdown()
        _jarvis_core = None
