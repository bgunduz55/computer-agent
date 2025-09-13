"""
Keyboard Control Capabilities for JARVIS Computer Assistant

Provides keyboard control and shortcut capabilities.
"""

import asyncio
import logging
import time
import platform
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class KeyType(Enum):
    """Types of keyboard keys"""
    SPECIAL = "special"  # Enter, Space, Tab, Arrow keys, etc.
    MODIFIER = "modifier"  # Ctrl, Alt, Shift, Win
    FUNCTION = "function"  # F1-F12
    ALPHANUMERIC = "alphanumeric"  # Letters, numbers, symbols

@dataclass
class KeyboardAction:
    """Keyboard action definition"""
    key: str
    action_type: str  # "press", "release", "tap", "hold"
    duration: float = 0.1  # For hold actions
    modifiers: List[str] = None  # Ctrl, Alt, Shift, Win

@dataclass
class KeyboardResult:
    """Result of keyboard action"""
    success: bool
    action_performed: str
    method_used: str
    execution_time: float
    error: Optional[str] = None

class KeyboardControlExecutor:
    """Executes keyboard control operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.platform = platform.system().lower()
        
        # Key mappings
        self.key_mappings = {
            # Special keys
            "enter": {"windows": "enter", "linux": "Return"},
            "space": {"windows": "space", "linux": "space"},
            "tab": {"windows": "tab", "linux": "Tab"},
            "escape": {"windows": "esc", "linux": "Escape"},
            "backspace": {"windows": "backspace", "linux": "BackSpace"},
            "delete": {"windows": "delete", "linux": "Delete"},
            
            # Arrow keys
            "up": {"windows": "up", "linux": "Up"},
            "down": {"windows": "down", "linux": "Down"},
            "left": {"windows": "left", "linux": "Left"},
            "right": {"windows": "right", "linux": "Right"},
            
            # Function keys
            "f1": {"windows": "f1", "linux": "F1"},
            "f2": {"windows": "f2", "linux": "F2"},
            "f3": {"windows": "f3", "linux": "F3"},
            "f4": {"windows": "f4", "linux": "F4"},
            "f5": {"windows": "f5", "linux": "F5"},
            "f6": {"windows": "f6", "linux": "F6"},
            "f7": {"windows": "f7", "linux": "F7"},
            "f8": {"windows": "f8", "linux": "F8"},
            "f9": {"windows": "f9", "linux": "F9"},
            "f10": {"windows": "f10", "linux": "F10"},
            "f11": {"windows": "f11", "linux": "F11"},
            "f12": {"windows": "f12", "linux": "F12"},
            
            # Modifier keys
            "ctrl": {"windows": "ctrl", "linux": "Control_L"},
            "alt": {"windows": "alt", "linux": "Alt_L"},
            "shift": {"windows": "shift", "linux": "Shift_L"},
            "win": {"windows": "win", "linux": "Super_L"},
        }
        
    async def initialize(self) -> bool:
        """Initialize keyboard control executor"""
        try:
            # Test keyboard control capability
            if self.platform == "windows":
                await self._test_windows_keyboard()
            else:
                await self._test_linux_keyboard()
            
            self._is_initialized = True
            self.logger.info("Keyboard control executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize keyboard control executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return "key" in parameters or "keys" in parameters
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute keyboard control capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Keyboard control executor not initialized"}
            
            # Single key press
            if "key" in parameters:
                key = parameters["key"]
                action = parameters.get("action", "tap")
                duration = parameters.get("duration", 0.1)
                modifiers = parameters.get("modifiers", [])
                
                result = await self._press_key(key, action, duration, modifiers)
                
            # Multiple keys (shortcut)
            elif "keys" in parameters:
                keys = parameters["keys"]
                action = parameters.get("action", "tap")
                duration = parameters.get("duration", 0.1)
                
                result = await self._press_keys(keys, action, duration)
            
            else:
                return {"success": False, "error": "No key or keys provided"}
            
            return {
                "success": result.success,
                "action_performed": result.action_performed,
                "method_used": result.method_used,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            self.logger.error(f"Error executing keyboard control capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _press_key(self, key: str, action: str, duration: float, modifiers: List[str]) -> KeyboardResult:
        """Press a single key"""
        start_time = time.time()
        
        try:
            if self.platform == "windows":
                result = await self._press_key_windows(key, action, duration, modifiers)
            else:
                result = await self._press_key_linux(key, action, duration, modifiers)
            
            execution_time = time.time() - start_time
            return KeyboardResult(
                success=result.success,
                action_performed=f"{action} {key}",
                method_used=result.method_used,
                execution_time=execution_time,
                error=result.error
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return KeyboardResult(
                success=False,
                action_performed="",
                method_used="unknown",
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _press_keys(self, keys: List[str], action: str, duration: float) -> KeyboardResult:
        """Press multiple keys (shortcut)"""
        start_time = time.time()
        
        try:
            if self.platform == "windows":
                result = await self._press_keys_windows(keys, action, duration)
            else:
                result = await self._press_keys_linux(keys, action, duration)
            
            execution_time = time.time() - start_time
            return KeyboardResult(
                success=result.success,
                action_performed=f"{action} {'+'.join(keys)}",
                method_used=result.method_used,
                execution_time=execution_time,
                error=result.error
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return KeyboardResult(
                success=False,
                action_performed="",
                method_used="unknown",
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _press_key_windows(self, key: str, action: str, duration: float, modifiers: List[str]) -> KeyboardResult:
        """Press key on Windows"""
        try:
            # Try pyautogui first
            try:
                import pyautogui
                
                # Handle modifiers
                if modifiers:
                    pyautogui.hotkey(*modifiers, key)
                else:
                    if action == "tap":
                        pyautogui.press(key)
                    elif action == "hold":
                        pyautogui.keyDown(key)
                        await asyncio.sleep(duration)
                        pyautogui.keyUp(key)
                    elif action == "press":
                        pyautogui.keyDown(key)
                    elif action == "release":
                        pyautogui.keyUp(key)
                
                return KeyboardResult(
                    success=True,
                    action_performed=f"{action} {key}",
                    method_used="pyautogui",
                    execution_time=0,
                    error=None
                )
            except ImportError:
                pass
            
            # Fallback to PowerShell
            return await self._press_key_powershell(key, action, duration, modifiers)
            
        except Exception as e:
            return KeyboardResult(
                success=False,
                action_performed="",
                method_used="windows",
                execution_time=0,
                error=str(e)
            )
    
    async def _press_key_linux(self, key: str, action: str, duration: float, modifiers: List[str]) -> KeyboardResult:
        """Press key on Linux"""
        try:
            import subprocess
            
            # Map key to xdotool format
            mapped_key = self.key_mappings.get(key.lower(), {}).get("linux", key)
            
            if modifiers:
                # Handle modifiers
                mod_keys = [self.key_mappings.get(mod.lower(), {}).get("linux", mod) for mod in modifiers]
                cmd = ["xdotool", "key", f"{'+'.join(mod_keys)}+{mapped_key}"]
            else:
                if action == "tap":
                    cmd = ["xdotool", "key", mapped_key]
                elif action == "hold":
                    cmd = ["xdotool", "keydown", mapped_key]
                    # Note: xdotool doesn't have built-in hold duration, we'll simulate
                elif action == "press":
                    cmd = ["xdotool", "keydown", mapped_key]
                elif action == "release":
                    cmd = ["xdotool", "keyup", mapped_key]
                else:
                    cmd = ["xdotool", "key", mapped_key]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return KeyboardResult(
                    success=True,
                    action_performed=f"{action} {key}",
                    method_used="xdotool",
                    execution_time=0,
                    error=None
                )
            else:
                return KeyboardResult(
                    success=False,
                    action_performed="",
                    method_used="xdotool",
                    execution_time=0,
                    error=f"xdotool failed: {result.stderr}"
                )
                
        except Exception as e:
            return KeyboardResult(
                success=False,
                action_performed="",
                method_used="linux",
                execution_time=0,
                error=str(e)
            )
    
    async def _press_key_powershell(self, key: str, action: str, duration: float, modifiers: List[str]) -> KeyboardResult:
        """Press key using PowerShell on Windows"""
        try:
            import subprocess
            
            # Map key to PowerShell format
            mapped_key = self.key_mappings.get(key.lower(), {}).get("windows", key)
            
            # Create PowerShell script
            if modifiers:
                mod_keys = [self.key_mappings.get(mod.lower(), {}).get("windows", mod) for mod in modifiers]
                ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("{{{'+'.join(mod_keys)}+{mapped_key}}}")
'''
            else:
                if action == "tap":
                    ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("{{{mapped_key}}}")
'''
                elif action == "hold":
                    ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("{{{mapped_key}}}+")
Start-Sleep -Milliseconds {int(duration * 1000)}
[System.Windows.Forms.SendKeys]::SendKeys::SendWait("{{{mapped_key}}}-")
'''
                else:
                    ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("{{{mapped_key}}}")
'''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return KeyboardResult(
                    success=True,
                    action_performed=f"{action} {key}",
                    method_used="powershell",
                    execution_time=0,
                    error=None
                )
            else:
                return KeyboardResult(
                    success=False,
                    action_performed="",
                    method_used="powershell",
                    execution_time=0,
                    error=f"PowerShell failed: {result.stderr}"
                )
                
        except Exception as e:
            return KeyboardResult(
                success=False,
                action_performed="",
                method_used="powershell",
                execution_time=0,
                error=str(e)
            )
    
    async def _press_keys_windows(self, keys: List[str], action: str, duration: float) -> KeyboardResult:
        """Press multiple keys on Windows"""
        try:
            import pyautogui
            
            if action == "tap":
                pyautogui.hotkey(*keys)
            else:
                # For hold/press actions, press all keys down then up
                for key in keys:
                    pyautogui.keyDown(key)
                await asyncio.sleep(duration)
                for key in reversed(keys):
                    pyautogui.keyUp(key)
            
            return KeyboardResult(
                success=True,
                action_performed=f"{action} {'+'.join(keys)}",
                method_used="pyautogui",
                execution_time=0,
                error=None
            )
            
        except Exception as e:
            return KeyboardResult(
                success=False,
                action_performed="",
                method_used="pyautogui",
                execution_time=0,
                error=str(e)
            )
    
    async def _press_keys_linux(self, keys: List[str], action: str, duration: float) -> KeyboardResult:
        """Press multiple keys on Linux"""
        try:
            import subprocess
            
            # Map keys to xdotool format
            mapped_keys = [self.key_mappings.get(key.lower(), {}).get("linux", key) for key in keys]
            
            if action == "tap":
                cmd = ["xdotool", "key", "+".join(mapped_keys)]
            else:
                # For hold actions, we'll need to simulate
                cmd = ["xdotool", "key", "+".join(mapped_keys)]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return KeyboardResult(
                    success=True,
                    action_performed=f"{action} {'+'.join(keys)}",
                    method_used="xdotool",
                    execution_time=0,
                    error=None
                )
            else:
                return KeyboardResult(
                    success=False,
                    action_performed="",
                    method_used="xdotool",
                    execution_time=0,
                    error=f"xdotool failed: {result.stderr}"
                )
                
        except Exception as e:
            return KeyboardResult(
                success=False,
                action_performed="",
                method_used="linux",
                execution_time=0,
                error=str(e)
            )
    
    async def _test_windows_keyboard(self):
        """Test Windows keyboard control capability"""
        try:
            # Test PowerShell method
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise Exception(f"PowerShell keyboard test failed: {result.stderr}")
                
        except Exception as e:
            self.logger.warning(f"Windows keyboard test failed: {e}")
            # Don't fail initialization, just warn
    
    async def _test_linux_keyboard(self):
        """Test Linux keyboard control capability"""
        try:
            import subprocess
            result = subprocess.run(
                ["which", "xdotool"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise Exception("xdotool not found")
                
        except Exception as e:
            self.logger.warning(f"Linux keyboard test failed: {e}")
            # Don't fail initialization, just warn
