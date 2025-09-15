"""
Browser Automation Integration

Provides cross-platform browser automation capabilities using Selenium and Playwright
for complex web interactions, form filling, and data extraction.
"""

from .browser_engine import BrowserEngine, BrowserType, BrowserConfig
from .web_automation_executor import WebAutomationExecutor
from .element_finder import ElementFinder, ElementType, FindStrategy

__all__ = [
    'BrowserEngine',
    'BrowserType', 
    'BrowserConfig',
    'WebAutomationExecutor',
    'ElementFinder',
    'ElementType',
    'FindStrategy'
]

