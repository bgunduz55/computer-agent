#!/usr/bin/env python3
"""
JARVIS Computer Assistant - Main Application

This is the main entry point for the JARVIS Computer Assistant application.
It initializes and runs all subsystems including voice recognition, AI integration,
terminal control, remote access, and settings management.
"""

import asyncio
import logging
import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.jarvis_core import get_jarvis_core, cleanup_jarvis_core
from features.settings import get_settings_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class JARVISApplication:
    """Main JARVIS application class"""
    
    def __init__(self):
        self.jarvis_core = None
        self.settings_manager = None
        self.is_running = False
    
    async def initialize(self) -> bool:
        """Initialize JARVIS application"""
        try:
            logger.info("Initializing JARVIS Computer Assistant...")
            
            # Initialize settings manager
            self.settings_manager = get_settings_manager()
            
            # Initialize JARVIS core
            self.jarvis_core = get_jarvis_core()
            if not await self.jarvis_core.initialize():
                logger.error("Failed to initialize JARVIS Core")
                return False
            
            logger.info("JARVIS Computer Assistant initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize JARVIS application: {e}")
            return False
    
    async def run(self) -> bool:
        """Run JARVIS application"""
        try:
            if not self.jarvis_core:
                logger.error("JARVIS Core not initialized")
                return False
            
            logger.info("Starting JARVIS Computer Assistant...")
            
            # Start JARVIS core
            if not await self.jarvis_core.start():
                logger.error("Failed to start JARVIS Core")
                return False
            
            self.is_running = True
            logger.info("JARVIS Computer Assistant is running!")
            logger.info("Press Ctrl+C to stop")
            
            # Keep running until interrupted
            try:
                while self.is_running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                self.is_running = False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to run JARVIS application: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown JARVIS application"""
        try:
            logger.info("Shutting down JARVIS Computer Assistant...")
            
            self.is_running = False
            
            if self.jarvis_core:
                try:
                    await asyncio.wait_for(self.jarvis_core.shutdown(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("JARVIS core shutdown timeout")
                except Exception as e:
                    logger.warning(f"Error during JARVIS core shutdown: {e}")
            
            logger.info("JARVIS Computer Assistant shutdown completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to shutdown JARVIS application: {e}")
            return False

def print_banner():
    """Print JARVIS banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🤖 JARVIS Computer Assistant v1.0.0                      ║
    ║                                                              ║
    ║    🎯 Intelligent Voice-Controlled Computer Assistant        ║
    ║    🗣️  Advanced Voice Recognition & AI Integration          ║
    ║    🖥️  Cross-Platform Terminal Control                      ║
    ║    📱 Remote Control via Mobile App                         ║
    ║    ⚙️  Comprehensive Settings Management                    ║
    ║                                                              ║
    ║    🚀 Ready to assist you with your computing needs!        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_help():
    """Print help information"""
    help_text = """
    JARVIS Computer Assistant - Help
    
    Usage: python main.py [options]
    
    Options:
        -h, --help              Show this help message
        -v, --version           Show version information
        -c, --config <file>     Use custom configuration file
        -d, --debug             Enable debug logging
        -q, --quiet             Enable quiet mode (minimal output)
        --no-voice              Disable voice recognition
        --no-remote             Disable remote control
        --no-ai                 Disable AI integration
        --settings              Open settings UI
        --test                  Run in test mode
    
    Examples:
        python main.py                          # Start JARVIS normally
        python main.py --debug                  # Start with debug logging
        python main.py --no-voice               # Start without voice recognition
        python main.py --settings               # Open settings UI
        python main.py --test                   # Run in test mode
    
    For more information, visit: https://github.com/your-repo/jarvis-assistant
    """
    print(help_text)

def print_version():
    """Print version information"""
    version_info = """
    JARVIS Computer Assistant v1.0.0
    
    Built with:
    - Python 3.8+
    - Cross-platform support (Windows 11, Linux)
    - Advanced voice recognition
    - Multiple AI providers (Ollama, OpenAI, Gemini, OpenRouter)
    - RAG (Retrieval Augmented Generation)
    - Terminal integration
    - Remote control via WebSocket
    - Flutter mobile app
    - Comprehensive settings management
    
    Copyright (c) 2024 JARVIS Computer Assistant
    """
    print(version_info)

async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="JARVIS Computer Assistant - Intelligent Voice-Controlled Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("-v", "--version", action="store_true", help="Show version information")
    parser.add_argument("-c", "--config", type=str, help="Use custom configuration file")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("-q", "--quiet", action="store_true", help="Enable quiet mode")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice recognition")
    parser.add_argument("--no-remote", action="store_true", help="Disable remote control")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI integration")
    parser.add_argument("--settings", action="store_true", help="Open settings UI")
    parser.add_argument("--gui", action="store_true", help="Run with GUI")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    
    args = parser.parse_args()
    
    # Handle special arguments
    if args.version:
        print_version()
        return 0
    
    # Setup logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Print banner
    if not args.quiet:
        print_banner()
    
    # Handle settings UI
    if args.settings:
        try:
            from features.settings import show_settings
            show_settings()
            return 0
        except Exception as e:
            logger.error(f"Failed to open settings UI: {e}")
            return 1
    
    # Handle GUI mode
    if args.gui:
        try:
            from gui.main_window import JARVISMainWindow
            app = JARVISMainWindow()
            app.run()
            return 0
        except Exception as e:
            logger.error(f"Failed to start GUI: {e}")
            return 1
    
    # Create application
    app = JARVISApplication()
    
    try:
        # Initialize application
        if not await app.initialize():
            logger.error("Failed to initialize JARVIS application")
            return 1
        
        # Handle test mode
        if args.test:
            logger.info("Running in test mode...")
            # Run basic tests
            status = app.jarvis_core.get_status()
            logger.info(f"JARVIS Status: {status}")
            return 0
        
        # Run application
        if not await app.run():
            logger.error("Failed to run JARVIS application")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    finally:
        # Shutdown application
        await app.shutdown()

def run_sync():
    """Run the application synchronously"""
    try:
        return asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted")
        return 0
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_sync())