"""
Application Control Manager - Manages running applications and browser control
"""

import asyncio
import logging
import psutil
import subprocess
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import platform
import json

try:
    import pyautogui
    import pygetwindow as gw
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


@dataclass
class ApplicationInfo:
    """Information about a running application"""
    name: str
    pid: int
    memory_usage: float
    cpu_percent: float
    window_title: str
    executable_path: str
    is_browser: bool
    browser_type: Optional[str] = None


@dataclass
class BrowserTab:
    """Information about a browser tab"""
    title: str
    url: str
    is_active: bool
    tab_id: Optional[str] = None


class ApplicationManager:
    """Manages running applications and browser control"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._browser_drivers: Dict[str, Any] = {}
        self._known_browsers = {
            'chrome': ['chrome.exe', 'google-chrome', 'chromium-browser'],
            'firefox': ['firefox.exe', 'firefox'],
            'edge': ['msedge.exe', 'microsoft-edge'],
            'safari': ['safari.exe', 'safari']
        }
        
    def initialize(self) -> bool:
        """Initialize application manager"""
        try:
            self.logger.info("Application manager initialized successfully")
            self._initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize application manager: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup application manager"""
        try:
            # Close all browser drivers
            for browser_type, driver in self._browser_drivers.items():
                try:
                    driver.quit()
                except Exception as e:
                    self.logger.warning(f"Failed to close {browser_type} driver: {e}")
            
            self._browser_drivers.clear()
            self._initialized = False
            self.logger.info("Application manager cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup application manager: {e}")
    
    def get_running_applications(self) -> List[ApplicationInfo]:
        """Get list of running applications"""
        try:
            applications = []
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'exe']):
                try:
                    proc_info = proc.info
                    if not proc_info['exe']:
                        continue
                    
                    # Get window title if possible
                    window_title = self._get_window_title(proc_info['pid'])
                    
                    # Check if it's a browser
                    is_browser, browser_type = self._is_browser(proc_info['name'])
                    
                    app_info = ApplicationInfo(
                        name=proc_info['name'],
                        pid=proc_info['pid'],
                        memory_usage=proc_info['memory_info'].rss / (1024 * 1024),  # MB
                        cpu_percent=proc_info['cpu_percent'] or 0.0,
                        window_title=window_title,
                        executable_path=proc_info['exe'],
                        is_browser=is_browser,
                        browser_type=browser_type
                    )
                    
                    applications.append(app_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return applications
        except Exception as e:
            self.logger.error(f"Failed to get running applications: {e}")
            return []
    
    def get_browser_applications(self) -> List[ApplicationInfo]:
        """Get list of running browser applications"""
        applications = self.get_running_applications()
        return [app for app in applications if app.is_browser]
    
    def find_application(self, name_pattern: str) -> List[ApplicationInfo]:
        """Find applications matching name pattern"""
        applications = self.get_running_applications()
        return [app for app in applications if name_pattern.lower() in app.name.lower()]
    
    def close_application(self, pid: int) -> bool:
        """Close application by PID"""
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            # Wait for process to terminate
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # Force kill if it doesn't terminate
                process.kill()
                process.wait(timeout=2)
            
            self.logger.info(f"Application with PID {pid} closed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to close application with PID {pid}: {e}")
            return False
    
    def close_application_by_name(self, name_pattern: str) -> bool:
        """Close application by name pattern"""
        applications = self.find_application(name_pattern)
        if not applications:
            self.logger.warning(f"No applications found matching '{name_pattern}'")
            return False
        
        success = True
        for app in applications:
            if not self.close_application(app.pid):
                success = False
        
        return success
    
    def get_browser_tabs(self, browser_type: str = "chrome") -> List[BrowserTab]:
        """Get browser tabs (requires selenium)"""
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available for browser control")
            return []
        
        try:
            driver = self._get_browser_driver(browser_type)
            if not driver:
                return []
            
            tabs = []
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                tab = BrowserTab(
                    title=driver.title,
                    url=driver.current_url,
                    is_active=handle == driver.current_window_handle,
                    tab_id=handle
                )
                tabs.append(tab)
            
            return tabs
        except Exception as e:
            self.logger.error(f"Failed to get browser tabs: {e}")
            return []
    
    def close_current_tab(self, browser_type: str = "chrome") -> bool:
        """Close current browser tab"""
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available for browser control")
            return False
        
        try:
            driver = self._get_browser_driver(browser_type)
            if not driver:
                return False
            
            if len(driver.window_handles) > 1:
                driver.close()
                # Switch to remaining tab
                driver.switch_to.window(driver.window_handles[0])
                self.logger.info("Current browser tab closed")
                return True
            else:
                self.logger.warning("Cannot close the last browser tab")
                return False
        except Exception as e:
            self.logger.error(f"Failed to close current tab: {e}")
            return False
    
    def open_url(self, url: str, browser_type: str = "chrome", new_tab: bool = True) -> bool:
        """Open URL in browser"""
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available for browser control")
            return False
        
        try:
            driver = self._get_browser_driver(browser_type)
            if not driver:
                return False
            
            if new_tab:
                # Open new tab
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
            
            driver.get(url)
            self.logger.info(f"Opened URL: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open URL {url}: {e}")
            return False
    
    def search_in_browser(self, query: str, browser_type: str = "chrome") -> bool:
        """Search query in browser"""
        if not SELENIUM_AVAILABLE:
            self.logger.warning("Selenium not available for browser control")
            return False
        
        try:
            driver = self._get_browser_driver(browser_type)
            if not driver:
                return False
            
            # Try to find search box
            search_selectors = [
                "input[name='q']",  # Google
                "input[type='search']",
                "input[placeholder*='search']",
                "input[placeholder*='Search']",
                "#search",
                ".search-input"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if search_box:
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                self.logger.info(f"Searched for: {query}")
                return True
            else:
                # Fallback: search in address bar
                address_bar = driver.find_element(By.TAG_NAME, "body")
                address_bar.send_keys(Keys.CONTROL + "l")  # Focus address bar
                time.sleep(0.5)
                address_bar.send_keys(f"https://www.google.com/search?q={query}")
                address_bar.send_keys(Keys.RETURN)
                self.logger.info(f"Searched for: {query} (fallback)")
                return True
        except Exception as e:
            self.logger.error(f"Failed to search in browser: {e}")
            return False
    
    def _get_browser_driver(self, browser_type: str):
        """Get or create browser driver"""
        if browser_type in self._browser_drivers:
            return self._browser_drivers[browser_type]
        
        if not SELENIUM_AVAILABLE:
            return None
        
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            
            if browser_type.lower() == "chrome":
                driver = webdriver.Chrome(options=options)
            elif browser_type.lower() == "firefox":
                driver = webdriver.Firefox()
            elif browser_type.lower() == "edge":
                driver = webdriver.Edge()
            else:
                self.logger.error(f"Unsupported browser type: {browser_type}")
                return None
            
            self._browser_drivers[browser_type] = driver
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create {browser_type} driver: {e}")
            return None
    
    def _get_window_title(self, pid: int) -> str:
        """Get window title for process"""
        try:
            if PYAUTOGUI_AVAILABLE:
                windows = gw.getWindowsWithTitle("")
                for window in windows:
                    if hasattr(window, '_hWnd'):
                        try:
                            # This is a simplified approach - in practice you'd need
                            # more sophisticated window-to-process mapping
                            return window.title
                        except:
                            continue
        except Exception:
            pass
        return "Unknown"
    
    def _is_browser(self, process_name: str) -> Tuple[bool, Optional[str]]:
        """Check if process is a browser"""
        for browser_type, names in self._known_browsers.items():
            for name in names:
                if name.lower() in process_name.lower():
                    return True, browser_type
        return False, None
    
    def get_application_summary(self) -> Dict[str, Any]:
        """Get summary of running applications"""
        try:
            applications = self.get_running_applications()
            browsers = self.get_browser_applications()
            
            return {
                "total_applications": len(applications),
                "browser_applications": len(browsers),
                "browsers": [{"name": app.name, "type": app.browser_type, "pid": app.pid} for app in browsers],
                "top_memory_usage": sorted(applications, key=lambda x: x.memory_usage, reverse=True)[:5],
                "top_cpu_usage": sorted(applications, key=lambda x: x.cpu_percent, reverse=True)[:5]
            }
        except Exception as e:
            self.logger.error(f"Failed to get application summary: {e}")
            return {}


# Global instance
_application_manager: Optional[ApplicationManager] = None


def get_application_manager() -> ApplicationManager:
    """Get global application manager instance"""
    global _application_manager
    if _application_manager is None:
        _application_manager = ApplicationManager()
    return _application_manager


def cleanup_application_manager() -> None:
    """Cleanup global application manager instance"""
    global _application_manager
    if _application_manager:
        _application_manager.cleanup()
        _application_manager = None
