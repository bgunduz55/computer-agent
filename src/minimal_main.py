#!/usr/bin/env python3
"""
Minimal JARVIS Backend - Stable Version
Only essential capabilities to prevent loops
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MinimalJARVIS:
    """Minimal JARVIS implementation with only essential features"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
    async def initialize(self):
        """Initialize minimal JARVIS"""
        try:
            self.logger.info("Initializing Minimal JARVIS...")
            
            # Only initialize essential components
            await self._initialize_platform()
            await self._initialize_websocket_server()
            
            self.is_running = True
            self.logger.info("Minimal JARVIS initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Minimal JARVIS: {e}")
            raise
    
    async def _initialize_platform(self):
        """Initialize platform detection"""
        try:
            import platform
            system = platform.system()
            self.logger.info(f"Platform detected: {system}")
        except Exception as e:
            self.logger.error(f"Platform initialization failed: {e}")
    
    async def _initialize_websocket_server(self):
        """Initialize WebSocket server for Flutter communication"""
        try:
            from features.remote_control.websocket_server import WebSocketServer
            self.websocket_server = WebSocketServer()
            await self.websocket_server.start()
            self.logger.info("WebSocket server started")
        except Exception as e:
            self.logger.error(f"WebSocket server initialization failed: {e}")
    
    async def run(self):
        """Run minimal JARVIS"""
        try:
            await self.initialize()
            
            if self.is_running:
                self.logger.info("Minimal JARVIS is running...")
                
                # Keep running until interrupted
                while self.is_running:
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown minimal JARVIS"""
        try:
            self.logger.info("Shutting down Minimal JARVIS...")
            self.is_running = False
            
            if hasattr(self, 'websocket_server'):
                await self.websocket_server.stop()
                self.logger.info("WebSocket server stopped")
                
            self.logger.info("Minimal JARVIS shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

async def main():
    """Main entry point"""
    jarvis = MinimalJARVIS()
    await jarvis.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
