"""
Web Automation Executor

High-level web automation executor that provides easy-to-use methods
for common web operations like clicking, typing, form filling, etc.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

from .browser_engine import BrowserEngine, BrowserType, BrowserConfig, BrowserBackend
from .element_finder import ElementFinder, ElementType, FindStrategy

logger = logging.getLogger(__name__)

@dataclass
class AutomationResult:
    """Result of automation operation"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0

class WebAutomationExecutor:
    """High-level web automation executor"""
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig(
            browser_type=BrowserType.CHROME,
            backend=BrowserBackend.SELENIUM,
            headless=False
        )
        self.browser_engine = BrowserEngine(self.config)
        self.element_finder = ElementFinder(self.browser_engine)
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the automation executor"""
        try:
            success = await self.browser_engine.initialize()
            if success:
                self._is_initialized = True
                self.logger.info("Web automation executor initialized successfully")
            return success
        except Exception as e:
            self.logger.error(f"Failed to initialize web automation executor: {e}")
            return False
    
    async def navigate_to(self, url: str) -> AutomationResult:
        """Navigate to URL"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            success = await self.browser_engine.navigate_to(url)
            if success:
                return AutomationResult(
                    success=True,
                    message=f"Successfully navigated to {url}",
                    data={"url": url},
                    execution_time=time.time() - start_time
                )
            else:
                return AutomationResult(
                    success=False,
                    message=f"Failed to navigate to {url}",
                    error="Navigation failed",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return AutomationResult(
                success=False,
                message=f"Error navigating to {url}",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def click_element(self, 
                           locator: str, 
                           strategy: FindStrategy = FindStrategy.CSS_SELECTOR,
                           element_type: ElementType = ElementType.BUTTON) -> AutomationResult:
        """Click on an element"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            # Find element
            element = await self.element_finder.find_element(locator, strategy, element_type)
            if not element:
                return AutomationResult(
                    success=False,
                    message=f"Element not found: {locator}",
                    error="Element not found",
                    execution_time=time.time() - start_time
                )
            
            # Click element
            if self.config.backend == BrowserBackend.SELENIUM:
                element.click()
            else:  # Playwright
                await element.click()
            
            return AutomationResult(
                success=True,
                message=f"Successfully clicked element: {locator}",
                data={"locator": locator, "strategy": strategy.value},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AutomationResult(
                success=False,
                message=f"Error clicking element {locator}",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def type_text(self, 
                       locator: str, 
                       text: str,
                       strategy: FindStrategy = FindStrategy.CSS_SELECTOR,
                       element_type: ElementType = ElementType.INPUT,
                       clear_first: bool = True) -> AutomationResult:
        """Type text into an element"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            # Find element
            element = await self.element_finder.find_element(locator, strategy, element_type)
            if not element:
                return AutomationResult(
                    success=False,
                    message=f"Element not found: {locator}",
                    error="Element not found",
                    execution_time=time.time() - start_time
                )
            
            # Clear and type text
            if self.config.backend == BrowserBackend.SELENIUM:
                if clear_first:
                    element.clear()
                element.send_keys(text)
            else:  # Playwright
                if clear_first:
                    await element.fill("")
                await element.type(text)
            
            return AutomationResult(
                success=True,
                message=f"Successfully typed text into element: {locator}",
                data={"locator": locator, "text": text, "strategy": strategy.value},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AutomationResult(
                success=False,
                message=f"Error typing text into element {locator}",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def get_text(self, 
                      locator: str, 
                      strategy: FindStrategy = FindStrategy.CSS_SELECTOR,
                      element_type: ElementType = ElementType.TEXT) -> AutomationResult:
        """Get text from an element"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            # Find element
            element = await self.element_finder.find_element(locator, strategy, element_type)
            if not element:
                return AutomationResult(
                    success=False,
                    message=f"Element not found: {locator}",
                    error="Element not found",
                    execution_time=time.time() - start_time
                )
            
            # Get text
            if self.config.backend == BrowserBackend.SELENIUM:
                text = element.text
            else:  # Playwright
                text = await element.text_content()
            
            return AutomationResult(
                success=True,
                message=f"Successfully retrieved text from element: {locator}",
                data={"locator": locator, "text": text, "strategy": strategy.value},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AutomationResult(
                success=False,
                message=f"Error getting text from element {locator}",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def get_attribute(self, 
                           locator: str, 
                           attribute: str,
                           strategy: FindStrategy = FindStrategy.CSS_SELECTOR,
                           element_type: ElementType = ElementType.UNKNOWN) -> AutomationResult:
        """Get attribute value from an element"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            # Find element
            element = await self.element_finder.find_element(locator, strategy, element_type)
            if not element:
                return AutomationResult(
                    success=False,
                    message=f"Element not found: {locator}",
                    error="Element not found",
                    execution_time=time.time() - start_time
                )
            
            # Get attribute
            if self.config.backend == BrowserBackend.SELENIUM:
                value = element.get_attribute(attribute)
            else:  # Playwright
                value = await element.get_attribute(attribute)
            
            return AutomationResult(
                success=True,
                message=f"Successfully retrieved attribute {attribute} from element: {locator}",
                data={"locator": locator, "attribute": attribute, "value": value, "strategy": strategy.value},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AutomationResult(
                success=False,
                message=f"Error getting attribute {attribute} from element {locator}",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def wait_for_element(self, 
                              locator: str, 
                              strategy: FindStrategy = FindStrategy.CSS_SELECTOR,
                              timeout: int = 10) -> AutomationResult:
        """Wait for element to be present"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            success = await self.element_finder.wait_for_element(locator, strategy, timeout)
            if success:
                return AutomationResult(
                    success=True,
                    message=f"Element found: {locator}",
                    data={"locator": locator, "strategy": strategy.value},
                    execution_time=time.time() - start_time
                )
            else:
                return AutomationResult(
                    success=False,
                    message=f"Element not found within timeout: {locator}",
                    error="Timeout",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return AutomationResult(
                success=False,
                message=f"Error waiting for element {locator}",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def wait_for_element_visible(self, 
                                     locator: str, 
                                     strategy: FindStrategy = FindStrategy.CSS_SELECTOR,
                                     timeout: int = 10) -> AutomationResult:
        """Wait for element to be visible"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            success = await self.element_finder.wait_for_element_visible(locator, strategy, timeout)
            if success:
                return AutomationResult(
                    success=True,
                    message=f"Element visible: {locator}",
                    data={"locator": locator, "strategy": strategy.value},
                    execution_time=time.time() - start_time
                )
            else:
                return AutomationResult(
                    success=False,
                    message=f"Element not visible within timeout: {locator}",
                    error="Timeout",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return AutomationResult(
                success=False,
                message=f"Error waiting for element visibility {locator}",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def take_screenshot(self, path: Optional[str] = None) -> AutomationResult:
        """Take screenshot of current page"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            screenshot_path = await self.browser_engine.take_screenshot(path)
            if screenshot_path:
                return AutomationResult(
                    success=True,
                    message="Screenshot taken successfully",
                    data={"screenshot_path": screenshot_path},
                    execution_time=time.time() - start_time
                )
            else:
                return AutomationResult(
                    success=False,
                    message="Failed to take screenshot",
                    error="Screenshot failed",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return AutomationResult(
                success=False,
                message="Error taking screenshot",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def execute_javascript(self, script: str) -> AutomationResult:
        """Execute JavaScript on current page"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            result = await self.browser_engine.execute_javascript(script)
            return AutomationResult(
                success=True,
                message="JavaScript executed successfully",
                data={"script": script, "result": result},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AutomationResult(
                success=False,
                message="Error executing JavaScript",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def get_page_info(self) -> AutomationResult:
        """Get current page information"""
        start_time = time.time()
        try:
            if not self._is_initialized:
                return AutomationResult(
                    success=False,
                    message="Automation executor not initialized",
                    error="Not initialized",
                    execution_time=time.time() - start_time
                )
            
            title = await self.browser_engine.get_page_title()
            url = await self.browser_engine.get_page_url()
            
            return AutomationResult(
                success=True,
                message="Page information retrieved successfully",
                data={"title": title, "url": url},
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return AutomationResult(
                success=False,
                message="Error getting page information",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def cleanup(self):
        """Cleanup automation resources"""
        try:
            await self.browser_engine.cleanup()
            self._is_initialized = False
            self.logger.info("Web automation executor cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def is_initialized(self) -> bool:
        """Check if automation executor is initialized"""
        return self._is_initialized

