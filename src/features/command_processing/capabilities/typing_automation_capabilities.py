"""
Typing Automation Capabilities for JARVIS Computer Assistant

Provides advanced typing automation, macro recording, and text input capabilities.
"""

import asyncio
import logging
import time
import platform
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TypingMode(Enum):
    """Types of typing modes"""
    NORMAL = "normal"
    FAST = "fast"
    SLOW = "slow"
    HUMAN_LIKE = "human_like"
    INSTANT = "instant"

class MacroType(Enum):
    """Types of macros"""
    TEXT = "text"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    MOUSE_ACTION = "mouse_action"
    COMBINED = "combined"

@dataclass
class TypingMacro:
    """Typing macro definition"""
    name: str
    macro_type: MacroType
    actions: List[Dict[str, Any]]
    description: Optional[str] = None
    created_at: Optional[float] = None
    last_used: Optional[float] = None

@dataclass
class TypingResult:
    """Result of typing operation"""
    success: bool
    text_typed: str
    characters_typed: int
    typing_mode: TypingMode
    execution_time: float
    error: Optional[str] = None

@dataclass
class MacroResult:
    """Result of macro execution"""
    success: bool
    macro_name: str
    actions_executed: int
    execution_time: float
    error: Optional[str] = None

class TypingSpeedController:
    """Controls typing speed and human-like behavior"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_delays = {
            TypingMode.INSTANT: 0.0,
            TypingMode.FAST: 0.01,
            TypingMode.NORMAL: 0.05,
            TypingMode.SLOW: 0.2,
            TypingMode.HUMAN_LIKE: 0.1
        }
    
    def get_typing_delay(self, mode: TypingMode, character: str = None) -> float:
        """Get typing delay based on mode and character"""
        base_delay = self.base_delays.get(mode, 0.05)
        
        if mode == TypingMode.HUMAN_LIKE and character:
            # Add human-like variation
            import random
            variation = random.uniform(0.8, 1.2)
            
            # Different delays for different character types
            if character.isalpha():
                delay_multiplier = 1.0
            elif character.isdigit():
                delay_multiplier = 0.9
            elif character in '.,!?;:':
                delay_multiplier = 1.2
            elif character == ' ':
                delay_multiplier = 0.8
            else:
                delay_multiplier = 1.1
            
            return base_delay * variation * delay_multiplier
        
        return base_delay

class MacroRecorder:
    """Records and manages typing macros"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.macros: Dict[str, TypingMacro] = {}
        self.is_recording = False
        self.current_macro_actions: List[Dict[str, Any]] = []
        self.recording_start_time: Optional[float] = None
    
    def start_recording(self, macro_name: str, macro_type: MacroType) -> bool:
        """Start recording a new macro"""
        try:
            if self.is_recording:
                self.logger.warning("Already recording a macro")
                return False
            
            self.is_recording = True
            self.current_macro_actions = []
            self.recording_start_time = time.time()
            
            self.logger.info(f"Started recording macro: {macro_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting macro recording: {e}")
            return False
    
    def stop_recording(self) -> Optional[TypingMacro]:
        """Stop recording and return the macro"""
        try:
            if not self.is_recording:
                self.logger.warning("Not currently recording")
                return None
            
            self.is_recording = False
            
            if not self.current_macro_actions:
                self.logger.warning("No actions recorded")
                return None
            
            # Create macro from recorded actions
            macro = TypingMacro(
                name=f"macro_{int(time.time())}",
                macro_type=MacroType.TEXT,  # Default type
                actions=self.current_macro_actions.copy(),
                created_at=time.time()
            )
            
            self.macros[macro.name] = macro
            self.current_macro_actions = []
            self.recording_start_time = None
            
            self.logger.info(f"Stopped recording macro: {macro.name}")
            return macro
            
        except Exception as e:
            self.logger.error(f"Error stopping macro recording: {e}")
            return None
    
    def add_action(self, action: Dict[str, Any]) -> bool:
        """Add an action to the current macro"""
        try:
            if not self.is_recording:
                return False
            
            action["timestamp"] = time.time() - (self.recording_start_time or 0)
            self.current_macro_actions.append(action)
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding action to macro: {e}")
            return False
    
    def save_macro(self, macro: TypingMacro) -> bool:
        """Save a macro"""
        try:
            self.macros[macro.name] = macro
            self.logger.info(f"Saved macro: {macro.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving macro: {e}")
            return False
    
    def get_macro(self, name: str) -> Optional[TypingMacro]:
        """Get a macro by name"""
        return self.macros.get(name)
    
    def list_macros(self) -> List[TypingMacro]:
        """List all macros"""
        return list(self.macros.values())
    
    def delete_macro(self, name: str) -> bool:
        """Delete a macro"""
        try:
            if name in self.macros:
                del self.macros[name]
                self.logger.info(f"Deleted macro: {name}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting macro: {e}")
            return False

class SmartTypingEngine:
    """Engine for smart typing with context awareness"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.speed_controller = TypingSpeedController()
        self.macro_recorder = MacroRecorder()
        self.platform = platform.system().lower()
        
    async def type_text(self, text: str, mode: TypingMode = TypingMode.NORMAL, 
                       parameters: Dict[str, Any] = None) -> TypingResult:
        """Type text with specified mode"""
        start_time = time.time()
        
        try:
            if not text:
                return TypingResult(
                    success=False,
                    text_typed="",
                    characters_typed=0,
                    typing_mode=mode,
                    execution_time=0,
                    error="No text provided"
                )
            
            # Type text character by character
            for i, character in enumerate(text):
                # Get delay for this character
                delay = self.speed_controller.get_typing_delay(mode, character)
                
                # Type the character (simulate for now)
                await self._type_character(character, parameters)
                
                # Add delay between characters
                if delay > 0:
                    await asyncio.sleep(delay)
            
            execution_time = time.time() - start_time
            return TypingResult(
                success=True,
                text_typed=text,
                characters_typed=len(text),
                typing_mode=mode,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TypingResult(
                success=False,
                text_typed="",
                characters_typed=0,
                typing_mode=mode,
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _type_character(self, character: str, parameters: Dict[str, Any] = None):
        """Type a single character"""
        # This would integrate with the actual typing mechanism
        # For now, we'll just log the character
        self.logger.debug(f"Typing character: {character}")
        
        # Record action if recording
        if self.macro_recorder.is_recording:
            self.macro_recorder.add_action({
                "type": "type_character",
                "character": character
            })
    
    async def execute_macro(self, macro_name: str, parameters: Dict[str, Any] = None) -> MacroResult:
        """Execute a typing macro"""
        start_time = time.time()
        
        try:
            macro = self.macro_recorder.get_macro(macro_name)
            if not macro:
                return MacroResult(
                    success=False,
                    macro_name=macro_name,
                    actions_executed=0,
                    execution_time=0,
                    error=f"Macro '{macro_name}' not found"
                )
            
            actions_executed = 0
            
            for action in macro.actions:
                try:
                    await self._execute_action(action, parameters)
                    actions_executed += 1
                    
                    # Add delay between actions if specified
                    if "delay" in action:
                        await asyncio.sleep(action["delay"])
                    
                except Exception as e:
                    self.logger.error(f"Error executing action: {e}")
            
            # Update last used time
            macro.last_used = time.time()
            
            execution_time = time.time() - start_time
            return MacroResult(
                success=True,
                macro_name=macro_name,
                actions_executed=actions_executed,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return MacroResult(
                success=False,
                macro_name=macro_name,
                actions_executed=0,
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _execute_action(self, action: Dict[str, Any], parameters: Dict[str, Any] = None):
        """Execute a single macro action"""
        action_type = action.get("type", "")
        
        if action_type == "type_character":
            character = action.get("character", "")
            await self._type_character(character, parameters)
        
        elif action_type == "type_text":
            text = action.get("text", "")
            mode = TypingMode(action.get("mode", "normal"))
            await self.type_text(text, mode, parameters)
        
        elif action_type == "key_press":
            key = action.get("key", "")
            # This would integrate with keyboard control
            self.logger.debug(f"Pressing key: {key}")
        
        elif action_type == "delay":
            delay = action.get("delay", 0)
            await asyncio.sleep(delay)
        
        else:
            self.logger.warning(f"Unknown action type: {action_type}")

class TypingAutomationExecutor:
    """Executes typing automation operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.smart_typing_engine = SmartTypingEngine()
        
    async def initialize(self) -> bool:
        """Initialize typing automation executor"""
        try:
            self._is_initialized = True
            self.logger.info("Typing automation executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize typing automation executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("typing_automation" in parameters or
                "smart_typing" in parameters or
                "macro_execution" in parameters or
                "macro_recording" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute typing automation capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Typing automation executor not initialized"}
            
            operation = parameters.get("operation", "type_text")
            
            if operation == "type_text":
                return await self._execute_smart_typing(parameters, context)
            elif operation == "execute_macro":
                return await self._execute_macro(parameters, context)
            elif operation == "start_recording":
                return await self._start_recording(parameters, context)
            elif operation == "stop_recording":
                return await self._stop_recording(parameters, context)
            elif operation == "list_macros":
                return await self._list_macros(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing typing automation capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_smart_typing(self, parameters: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute smart typing operation"""
        try:
            text = parameters.get("text", "")
            mode_str = parameters.get("mode", "normal")
            
            if not text:
                return {"success": False, "error": "No text provided"}
            
            try:
                mode = TypingMode(mode_str)
            except ValueError:
                return {"success": False, "error": f"Invalid typing mode: {mode_str}"}
            
            result = await self.smart_typing_engine.type_text(text, mode, parameters)
            
            return {
                "success": result.success,
                "text_typed": result.text_typed,
                "characters_typed": result.characters_typed,
                "typing_mode": result.typing_mode.value,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_macro(self, parameters: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute macro operation"""
        try:
            macro_name = parameters.get("macro_name", "")
            
            if not macro_name:
                return {"success": False, "error": "Macro name required"}
            
            result = await self.smart_typing_engine.execute_macro(macro_name, parameters)
            
            return {
                "success": result.success,
                "macro_name": result.macro_name,
                "actions_executed": result.actions_executed,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start_recording(self, parameters: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Start macro recording"""
        try:
            macro_name = parameters.get("macro_name", f"macro_{int(time.time())}")
            macro_type_str = parameters.get("macro_type", "text")
            
            try:
                macro_type = MacroType(macro_type_str)
            except ValueError:
                return {"success": False, "error": f"Invalid macro type: {macro_type_str}"}
            
            success = self.smart_typing_engine.macro_recorder.start_recording(macro_name, macro_type)
            
            return {
                "success": success,
                "macro_name": macro_name,
                "recording": success
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stop_recording(self, parameters: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Stop macro recording"""
        try:
            macro = self.smart_typing_engine.macro_recorder.stop_recording()
            
            if macro:
                return {
                    "success": True,
                    "macro_name": macro.name,
                    "actions_recorded": len(macro.actions),
                    "recording": False
                }
            else:
                return {
                    "success": False,
                    "error": "No macro was being recorded"
                }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_macros(self, parameters: Dict[str, Any], 
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """List available macros"""
        try:
            macros = self.smart_typing_engine.macro_recorder.list_macros()
            
            macro_list = []
            for macro in macros:
                macro_list.append({
                    "name": macro.name,
                    "type": macro.macro_type.value,
                    "actions_count": len(macro.actions),
                    "description": macro.description,
                    "created_at": macro.created_at,
                    "last_used": macro.last_used
                })
            
            return {
                "success": True,
                "macros": macro_list,
                "total_macros": len(macro_list)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

