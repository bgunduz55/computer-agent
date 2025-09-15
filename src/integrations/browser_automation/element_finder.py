"""
Element Finder

Advanced element finding strategies for web automation
with support for multiple locator types and fallback mechanisms.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ElementType(Enum):
    """Element types for identification"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    IMAGE = "image"
    TEXT = "text"
    CONTAINER = "container"
    FORM = "form"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    UNKNOWN = "unknown"

class FindStrategy(Enum):
    """Element finding strategies"""
    CSS_SELECTOR = "css_selector"
    XPATH = "xpath"
    ID = "id"
    CLASS_NAME = "class_name"
    TAG_NAME = "tag_name"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"
    NAME = "name"
    TEXT_CONTENT = "text_content"
    ATTRIBUTE = "attribute"

@dataclass
class ElementInfo:
    """Element information"""
    element_type: ElementType
    locator: str
    strategy: FindStrategy
    text: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    is_visible: bool = True
    is_enabled: bool = True
    is_displayed: bool = True

class ElementFinder:
    """Advanced element finder with multiple strategies"""
    
    def __init__(self, browser_engine):
        self.browser_engine = browser_engine
        self.logger = logging.getLogger(__name__)
    
    async def find_element(self, 
                          locator: str, 
                          strategy: FindStrategy = FindStrategy.CSS_SELECTOR,
                          element_type: ElementType = ElementType.UNKNOWN,
                          timeout: int = 10) -> Optional[Any]:
        """Find element using specified strategy"""
        try:
            if not self.browser_engine.is_initialized():
                raise RuntimeError("Browser not initialized")
            
            if self.browser_engine.config.backend.value == "selenium":
                return await self._find_element_selenium(locator, strategy, timeout)
            else:  # Playwright
                return await self._find_element_playwright(locator, strategy, timeout)
                
        except Exception as e:
            self.logger.error(f"Failed to find element {locator}: {e}")
            return None
    
    async def _find_element_selenium(self, locator: str, strategy: FindStrategy, timeout: int) -> Optional[Any]:
        """Find element using Selenium"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = self.browser_engine.get_driver()
            wait = WebDriverWait(driver, timeout)
            
            # Map strategy to Selenium By
            by_mapping = {
                FindStrategy.CSS_SELECTOR: By.CSS_SELECTOR,
                FindStrategy.XPATH: By.XPATH,
                FindStrategy.ID: By.ID,
                FindStrategy.CLASS_NAME: By.CLASS_NAME,
                FindStrategy.TAG_NAME: By.TAG_NAME,
                FindStrategy.LINK_TEXT: By.LINK_TEXT,
                FindStrategy.PARTIAL_LINK_TEXT: By.PARTIAL_LINK_TEXT,
                FindStrategy.NAME: By.NAME
            }
            
            by = by_mapping.get(strategy, By.CSS_SELECTOR)
            
            # Wait for element to be present
            element = wait.until(EC.presence_of_element_located((by, locator)))
            
            return element
            
        except Exception as e:
            self.logger.error(f"Selenium element finding failed: {e}")
            return None
    
    async def _find_element_playwright(self, locator: str, strategy: FindStrategy, timeout: int) -> Optional[Any]:
        """Find element using Playwright"""
        try:
            page = self.browser_engine.get_page()
            
            # Map strategy to Playwright selector
            if strategy == FindStrategy.CSS_SELECTOR:
                selector = locator
            elif strategy == FindStrategy.XPATH:
                selector = f"xpath={locator}"
            elif strategy == FindStrategy.ID:
                selector = f"#{locator}"
            elif strategy == FindStrategy.CLASS_NAME:
                selector = f".{locator}"
            elif strategy == FindStrategy.TAG_NAME:
                selector = locator
            elif strategy == FindStrategy.LINK_TEXT:
                selector = f"text={locator}"
            elif strategy == FindStrategy.PARTIAL_LINK_TEXT:
                selector = f"text={locator}"
            elif strategy == FindStrategy.NAME:
                selector = f"[name='{locator}']"
            else:
                selector = locator
            
            # Wait for element
            element = await page.wait_for_selector(selector, timeout=timeout * 1000)
            
            return element
            
        except Exception as e:
            self.logger.error(f"Playwright element finding failed: {e}")
            return None
    
    async def find_elements(self, 
                           locator: str, 
                           strategy: FindStrategy = FindStrategy.CSS_SELECTOR,
                           timeout: int = 10) -> List[Any]:
        """Find multiple elements using specified strategy"""
        try:
            if not self.browser_engine.is_initialized():
                raise RuntimeError("Browser not initialized")
            
            if self.browser_engine.config.backend.value == "selenium":
                return await self._find_elements_selenium(locator, strategy, timeout)
            else:  # Playwright
                return await self._find_elements_playwright(locator, strategy, timeout)
                
        except Exception as e:
            self.logger.error(f"Failed to find elements {locator}: {e}")
            return []
    
    async def _find_elements_selenium(self, locator: str, strategy: FindStrategy, timeout: int) -> List[Any]:
        """Find elements using Selenium"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = self.browser_engine.get_driver()
            wait = WebDriverWait(driver, timeout)
            
            # Map strategy to Selenium By
            by_mapping = {
                FindStrategy.CSS_SELECTOR: By.CSS_SELECTOR,
                FindStrategy.XPATH: By.XPATH,
                FindStrategy.ID: By.ID,
                FindStrategy.CLASS_NAME: By.CLASS_NAME,
                FindStrategy.TAG_NAME: By.TAG_NAME,
                FindStrategy.LINK_TEXT: By.LINK_TEXT,
                FindStrategy.PARTIAL_LINK_TEXT: By.PARTIAL_LINK_TEXT,
                FindStrategy.NAME: By.NAME
            }
            
            by = by_mapping.get(strategy, By.CSS_SELECTOR)
            
            # Wait for at least one element to be present
            wait.until(EC.presence_of_element_located((by, locator)))
            
            # Find all elements
            elements = driver.find_elements(by, locator)
            
            return elements
            
        except Exception as e:
            self.logger.error(f"Selenium elements finding failed: {e}")
            return []
    
    async def _find_elements_playwright(self, locator: str, strategy: FindStrategy, timeout: int) -> List[Any]:
        """Find elements using Playwright"""
        try:
            page = self.browser_engine.get_page()
            
            # Map strategy to Playwright selector
            if strategy == FindStrategy.CSS_SELECTOR:
                selector = locator
            elif strategy == FindStrategy.XPATH:
                selector = f"xpath={locator}"
            elif strategy == FindStrategy.ID:
                selector = f"#{locator}"
            elif strategy == FindStrategy.CLASS_NAME:
                selector = f".{locator}"
            elif strategy == FindStrategy.TAG_NAME:
                selector = locator
            elif strategy == FindStrategy.LINK_TEXT:
                selector = f"text={locator}"
            elif strategy == FindStrategy.PARTIAL_LINK_TEXT:
                selector = f"text={locator}"
            elif strategy == FindStrategy.NAME:
                selector = f"[name='{locator}']"
            else:
                selector = locator
            
            # Wait for at least one element
            await page.wait_for_selector(selector, timeout=timeout * 1000)
            
            # Find all elements
            elements = await page.query_selector_all(selector)
            
            return elements
            
        except Exception as e:
            self.logger.error(f"Playwright elements finding failed: {e}")
            return []
    
    async def find_element_by_text(self, text: str, element_type: ElementType = ElementType.UNKNOWN) -> Optional[Any]:
        """Find element by text content"""
        try:
            # Try different strategies
            strategies = [
                (f"text()='{text}'", FindStrategy.XPATH),
                (f"//*[contains(text(), '{text}')]", FindStrategy.XPATH),
                (f"text={text}", FindStrategy.LINK_TEXT),
                (f"text={text}", FindStrategy.PARTIAL_LINK_TEXT)
            ]
            
            for locator, strategy in strategies:
                element = await self.find_element(locator, strategy, element_type)
                if element:
                    return element
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find element by text '{text}': {e}")
            return None
    
    async def find_element_by_attribute(self, attribute: str, value: str, element_type: ElementType = ElementType.UNKNOWN) -> Optional[Any]:
        """Find element by attribute value"""
        try:
            locator = f"[{attribute}='{value}']"
            return await self.find_element(locator, FindStrategy.CSS_SELECTOR, element_type)
            
        except Exception as e:
            self.logger.error(f"Failed to find element by attribute {attribute}='{value}': {e}")
            return None
    
    async def get_element_info(self, element: Any) -> ElementInfo:
        """Get detailed information about an element"""
        try:
            if self.browser_engine.config.backend.value == "selenium":
                return await self._get_element_info_selenium(element)
            else:  # Playwright
                return await self._get_element_info_playwright(element)
                
        except Exception as e:
            self.logger.error(f"Failed to get element info: {e}")
            return ElementInfo(
                element_type=ElementType.UNKNOWN,
                locator="",
                strategy=FindStrategy.CSS_SELECTOR
            )
    
    async def _get_element_info_selenium(self, element: Any) -> ElementInfo:
        """Get element info for Selenium element"""
        try:
            tag_name = element.tag_name.lower()
            element_type = self._map_tag_to_type(tag_name)
            
            # Get text content
            text = element.text if hasattr(element, 'text') else None
            
            # Get attributes
            attributes = {}
            if hasattr(element, 'get_attribute'):
                common_attrs = ['id', 'class', 'name', 'type', 'value', 'href', 'src', 'alt', 'title']
                for attr in common_attrs:
                    value = element.get_attribute(attr)
                    if value:
                        attributes[attr] = value
            
            # Check visibility and enabled state
            is_visible = element.is_displayed() if hasattr(element, 'is_displayed') else True
            is_enabled = element.is_enabled() if hasattr(element, 'is_enabled') else True
            
            return ElementInfo(
                element_type=element_type,
                locator=tag_name,
                strategy=FindStrategy.TAG_NAME,
                text=text,
                attributes=attributes,
                is_visible=is_visible,
                is_enabled=is_enabled,
                is_displayed=is_visible
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get Selenium element info: {e}")
            return ElementInfo(
                element_type=ElementType.UNKNOWN,
                locator="",
                strategy=FindStrategy.CSS_SELECTOR
            )
    
    async def _get_element_info_playwright(self, element: Any) -> ElementInfo:
        """Get element info for Playwright element"""
        try:
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            element_type = self._map_tag_to_type(tag_name)
            
            # Get text content
            text = await element.text_content()
            
            # Get attributes
            attributes = {}
            common_attrs = ['id', 'class', 'name', 'type', 'value', 'href', 'src', 'alt', 'title']
            for attr in common_attrs:
                value = await element.get_attribute(attr)
                if value:
                    attributes[attr] = value
            
            # Check visibility and enabled state
            is_visible = await element.is_visible()
            is_enabled = await element.is_enabled()
            
            return ElementInfo(
                element_type=element_type,
                locator=tag_name,
                strategy=FindStrategy.TAG_NAME,
                text=text,
                attributes=attributes,
                is_visible=is_visible,
                is_enabled=is_enabled,
                is_displayed=is_visible
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get Playwright element info: {e}")
            return ElementInfo(
                element_type=ElementType.UNKNOWN,
                locator="",
                strategy=FindStrategy.CSS_SELECTOR
            )
    
    def _map_tag_to_type(self, tag_name: str) -> ElementType:
        """Map HTML tag name to ElementType"""
        mapping = {
            'button': ElementType.BUTTON,
            'input': ElementType.INPUT,
            'a': ElementType.LINK,
            'img': ElementType.IMAGE,
            'p': ElementType.TEXT,
            'div': ElementType.CONTAINER,
            'span': ElementType.TEXT,
            'form': ElementType.FORM,
            'select': ElementType.SELECT,
            'textarea': ElementType.INPUT
        }
        
        return mapping.get(tag_name, ElementType.UNKNOWN)
    
    async def wait_for_element_visible(self, locator: str, strategy: FindStrategy = FindStrategy.CSS_SELECTOR, timeout: int = 10) -> bool:
        """Wait for element to be visible"""
        try:
            if not self.browser_engine.is_initialized():
                return False
            
            if self.browser_engine.config.backend.value == "selenium":
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                driver = self.browser_engine.get_driver()
                wait = WebDriverWait(driver, timeout)
                
                by_mapping = {
                    FindStrategy.CSS_SELECTOR: By.CSS_SELECTOR,
                    FindStrategy.XPATH: By.XPATH,
                    FindStrategy.ID: By.ID,
                    FindStrategy.CLASS_NAME: By.CLASS_NAME,
                    FindStrategy.TAG_NAME: By.TAG_NAME,
                    FindStrategy.LINK_TEXT: By.LINK_TEXT,
                    FindStrategy.PARTIAL_LINK_TEXT: By.PARTIAL_LINK_TEXT,
                    FindStrategy.NAME: By.NAME
                }
                
                by = by_mapping.get(strategy, By.CSS_SELECTOR)
                wait.until(EC.visibility_of_element_located((by, locator)))
                
            else:  # Playwright
                page = self.browser_engine.get_page()
                await page.wait_for_selector(locator, state="visible", timeout=timeout * 1000)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to wait for element visibility {locator}: {e}")
            return False

