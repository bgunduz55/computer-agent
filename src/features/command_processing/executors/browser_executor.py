"""
Browser Command Executor
Handles browser control commands (open URL, search, tab management)
"""

import asyncio
import logging
import webbrowser
import subprocess
from typing import Dict, Any, Optional, List
import platform
import time
import urllib.parse

from ..command_classifier import CommandCategory
from ..nlp_engine import ProcessedCommand, IntentType
from ..command_executor import BaseExecutor, CommandResult, ExecutionStatus

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
        self._browser_configs = self._setup_browser_configs()
        self._search_engines = self._setup_search_engines()
    
    def _setup_browser_configs(self) -> Dict[str, Dict[str, str]]:
        """Setup browser configurations for different platforms"""
        if self.platform == "windows":
            return {
                "chrome": {
                    "executable": "chrome.exe",
                    "command": "start chrome",
                    "new_tab_flag": "--new-tab"
                },
                "firefox": {
                    "executable": "firefox.exe",
                    "command": "start firefox",
                    "new_tab_flag": "-new-tab"
                },
                "edge": {
                    "executable": "msedge.exe",
                    "command": "start msedge",
                    "new_tab_flag": "--new-tab"
                }
            }
        elif self.platform == "linux":
            return {
                "chrome": {
                    "executable": "google-chrome",
                    "command": "google-chrome",
                    "new_tab_flag": "--new-tab"
                },
                "firefox": {
                    "executable": "firefox",
                    "command": "firefox",
                    "new_tab_flag": "-new-tab"
                },
                "chromium": {
                    "executable": "chromium-browser",
                    "command": "chromium-browser",
                    "new_tab_flag": "--new-tab"
                }
            }
        else:
            return {}
    
    def _setup_search_engines(self) -> Dict[str, str]:
        """Setup search engine URLs"""
        return {
            "google": "https://www.google.com/search?q={}",
            "youtube": "https://www.youtube.com/results?search_query={}",
            "github": "https://github.com/search?q={}",
            "stackoverflow": "https://stackoverflow.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "wikipedia": "https://en.wikipedia.org/wiki/{}"
        }
    
    def get_default_browser(self) -> str:
        """Get default browser for the platform"""
        if self.platform == "windows":
            return "chrome"  # Default to Chrome on Windows
        elif self.platform == "linux":
            return "chrome"  # Default to Chrome on Linux
        else:
            return "chrome"
    
    def get_browser_config(self, browser_name: str) -> Optional[Dict[str, str]]:
        """Get browser configuration"""
        return self._browser_configs.get(browser_name.lower())
    
    def get_search_url(self, query: str, engine: str = "google") -> str:
        """Get search URL for query and engine"""
        search_template = self._search_engines.get(engine.lower(), self._search_engines["google"])
        encoded_query = urllib.parse.quote_plus(query)
        return search_template.format(encoded_query)
    
    async def open_url(self, url: str, browser: str = None, new_tab: bool = True) -> bool:
        """Open URL in browser"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            browser = browser or self.get_default_browser()
            browser_config = self.get_browser_config(browser)
            
            if not browser_config:
                self.logger.error(f"Unknown browser: {browser}")
                return False
            
            if new_tab:
                # Use browser-specific new tab command
                if self.platform == "windows":
                    command = f"{browser_config['command']} {browser_config['new_tab_flag']} {url}"
                    subprocess.Popen(command, shell=True)
                else:
                    command = [browser_config['executable'], browser_config['new_tab_flag'], url]
                    subprocess.Popen(command)
            else:
                # Use webbrowser module for default behavior
                webbrowser.open(url)
            
            self.logger.info(f"Opened URL: {url} in {browser}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening URL {url}: {e}")
            return False
    
    async def search(self, query: str, engine: str = "google", browser: str = None) -> bool:
        """Search using specified engine"""
        try:
            search_url = self.get_search_url(query, engine)
            return await self.open_url(search_url, browser, new_tab=True)
            
        except Exception as e:
            self.logger.error(f"Error searching '{query}' with {engine}: {e}")
            return False
    
    async def open_new_tab(self, browser: str = None) -> bool:
        """Open new tab in browser"""
        try:
            browser = browser or self.get_default_browser()
            browser_config = self.get_browser_config(browser)
            
            if not browser_config:
                self.logger.error(f"Unknown browser: {browser}")
                return False
            
            if self.platform == "windows":
                command = f"{browser_config['command']} {browser_config['new_tab_flag']}"
                subprocess.Popen(command, shell=True)
            else:
                command = [browser_config['executable'], browser_config['new_tab_flag']]
                subprocess.Popen(command)
            
            self.logger.info(f"Opened new tab in {browser}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening new tab in {browser}: {e}")
            return False
    
    async def close_current_tab(self, browser: str = None) -> bool:
        """Close current tab in browser"""
        try:
            # This is a simplified implementation
            # In a real implementation, you would use browser automation tools like Selenium
            # For now, we'll use keyboard shortcuts
            
            if self.platform == "windows":
                import pyautogui
                pyautogui.hotkey('ctrl', 'w')
            else:
                import subprocess
                subprocess.run(['xdotool', 'key', 'ctrl+w'])
            
            self.logger.info("Closed current tab")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing current tab: {e}")
            return False
    
    def get_available_browsers(self) -> List[str]:
        """Get list of available browsers"""
        available = []
        
        for browser_name, config in self._browser_configs.items():
            try:
                if self.platform == "windows":
                    # Check if executable exists in PATH
                    result = subprocess.run(['where', config['executable']], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        available.append(browser_name)
                else:
                    # Check if executable exists in PATH
                    result = subprocess.run(['which', config['executable']], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        available.append(browser_name)
            except Exception:
                continue
        
        return available


class BrowserExecutor(BaseExecutor):
    """Executor for browser control commands"""
    
    def __init__(self):
        super().__init__()
        self.browser_manager = BrowserManager()
        self._is_running = False
    
    def can_handle(self, command: ProcessedCommand) -> bool:
        """Check if this executor can handle the command"""
        return command.category == CommandCategory.BROWSER
    
    async def execute(self, command: ProcessedCommand) -> CommandResult:
        """Execute browser command"""
        try:
            self._is_running = True
            self.logger.info(f"Executing browser command: {command.action}")
            
            if command.action == "open_url":
                return await self._execute_open_url(command)
            elif command.action == "search":
                return await self._execute_search(command)
            elif command.action == "new_tab":
                return await self._execute_new_tab(command)
            elif command.action == "close_tab":
                return await self._execute_close_tab(command)
            elif command.action == "list_browsers":
                return await self._execute_list_browsers(command)
            else:
                return self._create_result(
                    success=False,
                    message=f"Unknown browser action: {command.action}",
                    status=ExecutionStatus.FAILED
                )
        
        except Exception as e:
            self.logger.error(f"Error executing browser command: {e}")
            return self._create_result(
                success=False,
                message=f"Error executing browser command: {e}",
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
        finally:
            self._is_running = False
    
    async def _execute_open_url(self, command: ProcessedCommand) -> CommandResult:
        """Execute open URL command"""
        url = command.parameters.get('url', '')
        if not url:
            return self._create_result(
                success=False,
                message="No URL provided",
                status=ExecutionStatus.FAILED
            )
        
        browser = command.parameters.get('browser', self.browser_manager.get_default_browser())
        new_tab = command.parameters.get('new_tab', True)
        
        success = await self.browser_manager.open_url(url, browser, new_tab)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Opened URL: {url}",
                data={"url": url, "browser": browser, "new_tab": new_tab}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to open URL: {url}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_search(self, command: ProcessedCommand) -> CommandResult:
        """Execute search command"""
        query = command.parameters.get('query', '')
        if not query:
            return self._create_result(
                success=False,
                message="No search query provided",
                status=ExecutionStatus.FAILED
            )
        
        engine = command.parameters.get('engine', 'google')
        browser = command.parameters.get('browser', self.browser_manager.get_default_browser())
        
        success = await self.browser_manager.search(query, engine, browser)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Searched '{query}' on {engine}",
                data={"query": query, "engine": engine, "browser": browser}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to search '{query}' on {engine}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_new_tab(self, command: ProcessedCommand) -> CommandResult:
        """Execute new tab command"""
        browser = command.parameters.get('browser', self.browser_manager.get_default_browser())
        
        success = await self.browser_manager.open_new_tab(browser)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Opened new tab in {browser}",
                data={"browser": browser}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to open new tab in {browser}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_close_tab(self, command: ProcessedCommand) -> CommandResult:
        """Execute close tab command"""
        browser = command.parameters.get('browser', self.browser_manager.get_default_browser())
        
        success = await self.browser_manager.close_current_tab(browser)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Closed current tab in {browser}",
                data={"browser": browser}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to close current tab in {browser}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_list_browsers(self, command: ProcessedCommand) -> CommandResult:
        """Execute list browsers command"""
        try:
            available_browsers = self.browser_manager.get_available_browsers()
            
            return self._create_result(
                success=True,
                message=f"Found {len(available_browsers)} available browsers",
                data={"browsers": available_browsers, "count": len(available_browsers)}
            )
        
        except Exception as e:
            self.logger.error(f"Error listing browsers: {e}")
            return self._create_result(
                success=False,
                message=f"Error listing browsers: {e}",
                status=ExecutionStatus.FAILED
            )
    
    def cleanup(self) -> None:
        """Cleanup executor resources"""
        self._is_running = False
        self.logger.info("Browser executor cleaned up")
