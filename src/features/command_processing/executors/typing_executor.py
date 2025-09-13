"""
Typing Command Executor
Handles typing and keyboard input commands
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
import platform
import time

from ..command_classifier import CommandCategory
from ..nlp_engine import ProcessedCommand, IntentType
from ..command_executor import BaseExecutor, CommandResult, ExecutionStatus

logger = logging.getLogger(__name__)


class KeyboardController:
    """Cross-platform keyboard controller"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
        self._controller = None
        self._initialize_controller()
    
    def _initialize_controller(self) -> None:
        """Initialize platform-specific keyboard controller"""
        try:
            if self.platform == "windows":
                self._controller = WindowsKeyboardController()
            elif self.platform == "linux":
                self._controller = LinuxKeyboardController()
            else:
                self.logger.warning(f"Unsupported platform: {self.platform}")
                self._controller = None
        except Exception as e:
            self.logger.error(f"Failed to initialize keyboard controller: {e}")
            self._controller = None
    
    async def type_text(self, text: str, delay: float = 0.01) -> bool:
        """Type text with specified delay between characters"""
        if not self._controller:
            self.logger.error("Keyboard controller not available")
            return False
        
        try:
            await self._controller.type_text(text, delay)
            return True
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
            return False
    
    async def press_key(self, key: str) -> bool:
        """Press a single key"""
        if not self._controller:
            self.logger.error("Keyboard controller not available")
            return False
        
        try:
            await self._controller.press_key(key)
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key {key}: {e}")
            return False
    
    async def press_key_combination(self, keys: List[str]) -> bool:
        """Press a combination of keys"""
        if not self._controller:
            self.logger.error("Keyboard controller not available")
            return False
        
        try:
            await self._controller.press_key_combination(keys)
            return True
        except Exception as e:
            self.logger.error(f"Error pressing key combination {keys}: {e}")
            return False


class WindowsKeyboardController:
    """Windows-specific keyboard controller"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            import pyautogui
            import win32api
            import win32con
            self.pyautogui = pyautogui
            self.win32api = win32api
            self.win32con = win32con
            self._available = True
        except ImportError as e:
            self.logger.error(f"Required libraries not available: {e}")
            self._available = False
    
    async def type_text(self, text: str, delay: float = 0.01) -> None:
        """Type text on Windows"""
        if not self._available:
            raise RuntimeError("Windows keyboard controller not available")
        
        # Process text for special characters
        processed_text = self._process_text(text)
        
        # Type each character with delay
        for char in processed_text:
            if char == '\n':
                self.pyautogui.press('enter')
            elif char == '\t':
                self.pyautogui.press('tab')
            else:
                self.pyautogui.write(char)
            
            await asyncio.sleep(delay)
    
    async def press_key(self, key: str) -> None:
        """Press a key on Windows"""
        if not self._available:
            raise RuntimeError("Windows keyboard controller not available")
        
        key_mapping = {
            'enter': 'enter',
            'tab': 'tab',
            'space': 'space',
            'backspace': 'backspace',
            'delete': 'delete',
            'ctrl': 'ctrl',
            'alt': 'alt',
            'shift': 'shift',
            'esc': 'esc',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
            'home': 'home',
            'end': 'end',
            'pageup': 'pageup',
            'pagedown': 'pagedown'
        }
        
        mapped_key = key_mapping.get(key.lower(), key)
        self.pyautogui.press(mapped_key)
    
    async def press_key_combination(self, keys: List[str]) -> None:
        """Press key combination on Windows"""
        if not self._available:
            raise RuntimeError("Windows keyboard controller not available")
        
        # Map keys
        key_mapping = {
            'ctrl': 'ctrl',
            'alt': 'alt',
            'shift': 'shift',
            'win': 'win'
        }
        
        mapped_keys = [key_mapping.get(key.lower(), key) for key in keys]
        
        # Press all keys together
        self.pyautogui.hotkey(*mapped_keys)
    
    def _process_text(self, text: str) -> str:
        """Process text for special characters"""
        # Handle Turkish characters
        replacements = {
            'ç': 'c',
            'ğ': 'g',
            'ı': 'i',
            'ö': 'o',
            'ş': 's',
            'ü': 'u',
            'Ç': 'C',
            'Ğ': 'G',
            'İ': 'I',
            'Ö': 'O',
            'Ş': 'S',
            'Ü': 'U'
        }
        
        processed = text
        for turkish, english in replacements.items():
            processed = processed.replace(turkish, english)
        
        return processed


class LinuxKeyboardController:
    """Linux-specific keyboard controller"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            from pynput import keyboard
            self.keyboard = keyboard.Controller()
            self._available = True
        except ImportError as e:
            self.logger.error(f"Required libraries not available: {e}")
            self._available = False
    
    async def type_text(self, text: str, delay: float = 0.01) -> None:
        """Type text on Linux"""
        if not self._available:
            raise RuntimeError("Linux keyboard controller not available")
        
        # Process text for special characters
        processed_text = self._process_text(text)
        
        # Type each character with delay
        for char in processed_text:
            if char == '\n':
                self.keyboard.press(keyboard.Key.enter)
                self.keyboard.release(keyboard.Key.enter)
            elif char == '\t':
                self.keyboard.press(keyboard.Key.tab)
                self.keyboard.release(keyboard.Key.tab)
            else:
                self.keyboard.type(char)
            
            await asyncio.sleep(delay)
    
    async def press_key(self, key: str) -> None:
        """Press a key on Linux"""
        if not self._available:
            raise RuntimeError("Linux keyboard controller not available")
        
        key_mapping = {
            'enter': keyboard.Key.enter,
            'tab': keyboard.Key.tab,
            'space': keyboard.Key.space,
            'backspace': keyboard.Key.backspace,
            'delete': keyboard.Key.delete,
            'ctrl': keyboard.Key.ctrl,
            'alt': keyboard.Key.alt,
            'shift': keyboard.Key.shift,
            'esc': keyboard.Key.esc,
            'up': keyboard.Key.up,
            'down': keyboard.Key.down,
            'left': keyboard.Key.left,
            'right': keyboard.Key.right,
            'home': keyboard.Key.home,
            'end': keyboard.Key.end,
            'pageup': keyboard.Key.page_up,
            'pagedown': keyboard.Key.page_down
        }
        
        mapped_key = key_mapping.get(key.lower())
        if mapped_key:
            self.keyboard.press(mapped_key)
            self.keyboard.release(mapped_key)
        else:
            # Try to type the key as a character
            self.keyboard.type(key)
    
    async def press_key_combination(self, keys: List[str]) -> None:
        """Press key combination on Linux"""
        if not self._available:
            raise RuntimeError("Linux keyboard controller not available")
        
        # Map keys
        key_mapping = {
            'ctrl': keyboard.Key.ctrl,
            'alt': keyboard.Key.alt,
            'shift': keyboard.Key.shift,
            'win': keyboard.Key.cmd
        }
        
        # Press all keys together
        for key in keys:
            mapped_key = key_mapping.get(key.lower())
            if mapped_key:
                self.keyboard.press(mapped_key)
        
        # Release all keys
        for key in reversed(keys):
            mapped_key = key_mapping.get(key.lower())
            if mapped_key:
                self.keyboard.release(mapped_key)
    
    def _process_text(self, text: str) -> str:
        """Process text for special characters"""
        # Handle Turkish characters
        replacements = {
            'ç': 'c',
            'ğ': 'g',
            'ı': 'i',
            'ö': 'o',
            'ş': 's',
            'ü': 'u',
            'Ç': 'C',
            'Ğ': 'G',
            'İ': 'I',
            'Ö': 'O',
            'Ş': 'S',
            'Ü': 'U'
        }
        
        processed = text
        for turkish, english in replacements.items():
            processed = processed.replace(turkish, english)
        
        return processed


class TypingExecutor(BaseExecutor):
    """Executor for typing and keyboard commands"""
    
    def __init__(self):
        super().__init__()
        self.keyboard_controller = KeyboardController()
        self._is_running = False
    
    def can_handle(self, command: ProcessedCommand) -> bool:
        """Check if this executor can handle the command"""
        return command.category == CommandCategory.TYPING
    
    async def execute(self, command: ProcessedCommand) -> CommandResult:
        """Execute typing command"""
        try:
            self._is_running = True
            self.logger.info(f"Executing typing command: {command.action}")
            
            if command.action == "type_text":
                return await self._execute_type_text(command)
            elif command.action == "press_key":
                return await self._execute_press_key(command)
            elif command.action == "key_combination":
                return await self._execute_key_combination(command)
            else:
                return self._create_result(
                    success=False,
                    message=f"Unknown typing action: {command.action}",
                    status=ExecutionStatus.FAILED
                )
        
        except Exception as e:
            self.logger.error(f"Error executing typing command: {e}")
            return self._create_result(
                success=False,
                message=f"Error executing typing command: {e}",
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
        finally:
            self._is_running = False
    
    async def _execute_type_text(self, command: ProcessedCommand) -> CommandResult:
        """Execute type text command"""
        text = command.parameters.get('text', '')
        if not text:
            return self._create_result(
                success=False,
                message="No text provided for typing",
                status=ExecutionStatus.FAILED
            )
        
        # Get typing delay from parameters
        delay = command.parameters.get('delay', 0.01)
        
        # Type the text
        success = await self.keyboard_controller.type_text(text, delay)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}",
                data={"text": text, "length": len(text)}
            )
        else:
            return self._create_result(
                success=False,
                message="Failed to type text",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_press_key(self, command: ProcessedCommand) -> CommandResult:
        """Execute press key command"""
        key = command.parameters.get('key', '')
        if not key:
            return self._create_result(
                success=False,
                message="No key provided for pressing",
                status=ExecutionStatus.FAILED
            )
        
        # Press the key
        success = await self.keyboard_controller.press_key(key)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Pressed key: {key}",
                data={"key": key}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to press key: {key}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_key_combination(self, command: ProcessedCommand) -> CommandResult:
        """Execute key combination command"""
        keys = command.parameters.get('keys', [])
        if not keys:
            return self._create_result(
                success=False,
                message="No keys provided for combination",
                status=ExecutionStatus.FAILED
            )
        
        # Press key combination
        success = await self.keyboard_controller.press_key_combination(keys)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Pressed key combination: {'+'.join(keys)}",
                data={"keys": keys}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to press key combination: {'+'.join(keys)}",
                status=ExecutionStatus.FAILED
            )
    
    def cleanup(self) -> None:
        """Cleanup executor resources"""
        self._is_running = False
        self.logger.info("Typing executor cleaned up")
