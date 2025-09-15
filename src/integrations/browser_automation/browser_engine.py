"""
Browser Engine

Cross-platform browser automation engine supporting Chrome, Firefox, Edge
with both Selenium and Playwright backends.
"""

import asyncio
import logging
import platform
import subprocess
import tempfile
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class BrowserType(Enum):
    """Supported browser types"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"

class BrowserBackend(Enum):
    """Browser automation backends"""
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"

@dataclass
class BrowserConfig:
    """Browser configuration"""
    browser_type: BrowserType
    backend: BrowserBackend
    headless: bool = False
    window_size: tuple = (1920, 1080)
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    download_directory: Optional[str] = None
    disable_images: bool = False
    disable_javascript: bool = False
    incognito: bool = False
    timeout: int = 30

class BrowserEngine:
    """Cross-platform browser automation engine"""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._driver = None
        self._page = None
        self._is_initialized = False
        self._temp_dirs = []
        
    async def initialize(self) -> bool:
        """Initialize browser engine"""
        try:
            self.logger.info(f"Initializing browser engine: {self.config.browser_type.value} with {self.config.backend.value}")
            
            if self.config.backend == BrowserBackend.SELENIUM:
                return await self._initialize_selenium()
            elif self.config.backend == BrowserBackend.PLAYWRIGHT:
                return await self._initialize_playwright()
            else:
                raise ValueError(f"Unsupported backend: {self.config.backend}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize browser engine: {e}")
            return False
    
    async def _initialize_selenium(self) -> bool:
        """Initialize Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.firefox.options import Options as FirefoxOptions
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Create options based on browser type
            if self.config.browser_type == BrowserType.CHROME:
                options = ChromeOptions()
                if self.config.headless:
                    options.add_argument("--headless")
                if self.config.incognito:
                    options.add_argument("--incognito")
                if self.config.disable_images:
                    options.add_argument("--disable-images")
                if self.config.disable_javascript:
                    options.add_argument("--disable-javascript")
                if self.config.user_agent:
                    options.add_argument(f"--user-agent={self.config.user_agent}")
                if self.config.proxy:
                    options.add_argument(f"--proxy-server={self.config.proxy}")
                if self.config.download_directory:
                    prefs = {"download.default_directory": self.config.download_directory}
                    options.add_experimental_option("prefs", prefs)
                
                options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                
                # Find Chrome executable
                chrome_path = self._find_chrome_executable()
                if chrome_path:
                    options.binary_location = chrome_path
                
                self._driver = webdriver.Chrome(options=options)
                
            elif self.config.browser_type == BrowserType.FIREFOX:
                options = FirefoxOptions()
                if self.config.headless:
                    options.add_argument("--headless")
                if self.config.incognito:
                    options.add_argument("--private")
                if self.config.disable_images:
                    options.set_preference("permissions.default.image", 2)
                if self.config.disable_javascript:
                    options.set_preference("javascript.enabled", False)
                if self.config.user_agent:
                    options.set_preference("general.useragent.override", self.config.user_agent)
                if self.config.proxy:
                    options.set_preference("network.proxy.type", 1)
                    options.set_preference("network.proxy.http", self.config.proxy.split(":")[0])
                    options.set_preference("network.proxy.http_port", int(self.config.proxy.split(":")[1]))
                
                self._driver = webdriver.Firefox(options=options)
                
            elif self.config.browser_type == BrowserType.EDGE:
                options = EdgeOptions()
                if self.config.headless:
                    options.add_argument("--headless")
                if self.config.incognito:
                    options.add_argument("--inprivate")
                if self.config.disable_images:
                    options.add_argument("--disable-images")
                if self.config.disable_javascript:
                    options.add_argument("--disable-javascript")
                if self.config.user_agent:
                    options.add_argument(f"--user-agent={self.config.user_agent}")
                if self.config.proxy:
                    options.add_argument(f"--proxy-server={self.config.proxy}")
                
                self._driver = webdriver.Edge(options=options)
            
            else:
                raise ValueError(f"Unsupported browser type for Selenium: {self.config.browser_type}")
            
            # Set timeouts
            self._driver.set_page_load_timeout(self.config.timeout)
            self._driver.implicitly_wait(10)
            
            self._is_initialized = True
            self.logger.info("Selenium WebDriver initialized successfully")
            return True
            
        except ImportError:
            self.logger.error("Selenium not installed. Please install: pip install selenium")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            return False
    
    async def _initialize_playwright(self) -> bool:
        """Initialize Playwright browser"""
        try:
            from playwright.async_api import async_playwright
            
            self._playwright = await async_playwright().start()
            
            # Select browser type
            if self.config.browser_type == BrowserType.CHROME:
                browser = await self._playwright.chromium.launch(
                    headless=self.config.headless,
                    args=[
                        f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}",
                        "--no-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                )
            elif self.config.browser_type == BrowserType.FIREFOX:
                browser = await self._playwright.firefox.launch(
                    headless=self.config.headless,
                    args=[f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}"]
                )
            elif self.config.browser_type == BrowserType.EDGE:
                browser = await self._playwright.chromium.launch(
                    headless=self.config.headless,
                    channel="msedge",
                    args=[f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}"]
                )
            else:
                raise ValueError(f"Unsupported browser type for Playwright: {self.config.browser_type}")
            
            # Create context with options
            context_options = {}
            if self.config.user_agent:
                context_options["user_agent"] = self.config.user_agent
            if self.config.proxy:
                context_options["proxy"] = {"server": self.config.proxy}
            if self.config.incognito:
                context_options["ignore_https_errors"] = True
            
            context = await browser.new_context(**context_options)
            
            # Create page
            self._page = await context.new_page()
            
            # Set viewport
            await self._page.set_viewport_size({
                "width": self.config.window_size[0],
                "height": self.config.window_size[1]
            })
            
            # Set timeouts
            self._page.set_default_timeout(self.config.timeout * 1000)
            
            self._is_initialized = True
            self.logger.info("Playwright browser initialized successfully")
            return True
            
        except ImportError:
            self.logger.error("Playwright not installed. Please install: pip install playwright")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Playwright: {e}")
            return False
    
    def _find_chrome_executable(self) -> Optional[str]:
        """Find Chrome executable path"""
        possible_paths = []
        
        if platform.system() == "Windows":
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(
                    platform.node()
                )
            ]
        elif platform.system() == "Linux":
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/snap/bin/chromium"
            ]
        elif platform.system() == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return None
    
    async def navigate_to(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            if not self._is_initialized:
                raise RuntimeError("Browser not initialized")
            
            if self.config.backend == BrowserBackend.SELENIUM:
                self._driver.get(url)
            else:  # Playwright
                await self._page.goto(url)
            
            self.logger.info(f"Navigated to: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    async def get_page_title(self) -> str:
        """Get current page title"""
        try:
            if not self._is_initialized:
                raise RuntimeError("Browser not initialized")
            
            if self.config.backend == BrowserBackend.SELENIUM:
                return self._driver.title
            else:  # Playwright
                return await self._page.title()
                
        except Exception as e:
            self.logger.error(f"Failed to get page title: {e}")
            return ""
    
    async def get_page_url(self) -> str:
        """Get current page URL"""
        try:
            if not self._is_initialized:
                raise RuntimeError("Browser not initialized")
            
            if self.config.backend == BrowserBackend.SELENIUM:
                return self._driver.current_url
            else:  # Playwright
                return self._page.url
                
        except Exception as e:
            self.logger.error(f"Failed to get page URL: {e}")
            return ""
    
    async def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take screenshot of current page"""
        try:
            if not self._is_initialized:
                raise RuntimeError("Browser not initialized")
            
            if not path:
                temp_dir = tempfile.mkdtemp()
                self._temp_dirs.append(temp_dir)
                path = Path(temp_dir) / f"screenshot_{int(time.time())}.png"
            
            if self.config.backend == BrowserBackend.SELENIUM:
                self._driver.save_screenshot(str(path))
            else:  # Playwright
                await self._page.screenshot(path=str(path))
            
            self.logger.info(f"Screenshot saved to: {path}")
            return str(path)
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    async def execute_javascript(self, script: str) -> Any:
        """Execute JavaScript on current page"""
        try:
            if not self._is_initialized:
                raise RuntimeError("Browser not initialized")
            
            if self.config.backend == BrowserBackend.SELENIUM:
                return self._driver.execute_script(script)
            else:  # Playwright
                return await self._page.evaluate(script)
                
        except Exception as e:
            self.logger.error(f"Failed to execute JavaScript: {e}")
            return None
    
    async def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for element to be present"""
        try:
            if not self._is_initialized:
                raise RuntimeError("Browser not initialized")
            
            if self.config.backend == BrowserBackend.SELENIUM:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(self._driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            else:  # Playwright
                await self._page.wait_for_selector(selector, timeout=timeout * 1000)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to wait for element {selector}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup browser resources"""
        try:
            if self._driver:
                self._driver.quit()
                self._driver = None
            
            if hasattr(self, '_page') and self._page:
                await self._page.close()
                self._page = None
            
            if hasattr(self, '_playwright') and self._playwright:
                await self._playwright.stop()
                self._playwright = None
            
            # Clean up temp directories
            for temp_dir in self._temp_dirs:
                try:
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
            
            self._is_initialized = False
            self.logger.info("Browser engine cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def is_initialized(self) -> bool:
        """Check if browser is initialized"""
        return self._is_initialized
    
    def get_driver(self):
        """Get Selenium WebDriver (if using Selenium backend)"""
        return self._driver
    
    def get_page(self):
        """Get Playwright Page (if using Playwright backend)"""
        return self._page

