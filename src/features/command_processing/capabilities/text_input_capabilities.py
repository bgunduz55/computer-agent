"""
Text Input Capabilities for JARVIS Computer Assistant

Provides text input and typing capabilities through various methods.
"""

import asyncio
import logging
import time
import platform
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TextInputResult:
    """Result of text input operation"""
    success: bool
    text_entered: str
    method_used: str
    execution_time: float
    error: Optional[str] = None

class TextInputExecutor:
    """Executes text input operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.platform = platform.system().lower()
        
    async def initialize(self) -> bool:
        """Initialize text input executor"""
        try:
            # Test text input capability
            if self.platform == "windows":
                await self._test_windows_text_input()
            else:
                await self._test_linux_text_input()
            
            self._is_initialized = True
            self.logger.info("Text input executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize text input executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return "text" in parameters
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text input capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Text input executor not initialized"}
            
            text = parameters.get("text", "")
            if not text:
                return {"success": False, "error": "No text provided"}
            
            # Execute text input
            result = await self._type_text(text, parameters)
            
            return {
                "success": result.success,
                "text_entered": result.text_entered,
                "method_used": result.method_used,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            self.logger.error(f"Error executing text input capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _type_text(self, text: str, parameters: Dict[str, Any]) -> TextInputResult:
        """Type text using keyboard simulation"""
        start_time = time.time()
        
        try:
            if self.platform == "windows":
                result = await self._type_text_windows(text, parameters)
            else:
                result = await self._type_text_linux(text, parameters)
            
            execution_time = time.time() - start_time
            return TextInputResult(
                success=result.success,
                text_entered=text,
                method_used=result.method_used,
                execution_time=execution_time,
                error=result.error
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TextInputResult(
                success=False,
                text_entered="",
                method_used="unknown",
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _write_text(self, text: str, parameters: Dict[str, Any]) -> TextInputResult:
        """Write text to active application"""
        return await self._type_text(text, parameters)
    
    async def _type_text_windows(self, text: str, parameters: Dict[str, Any]) -> TextInputResult:
        """Type text on Windows using PowerShell (supports Turkish characters) or pyautogui"""
        try:
            # Try PowerShell first (supports Turkish characters)
            try:
                result = await self._type_text_powershell(text, parameters)
                if result.success:
                    return result
            except Exception as e:
                self.logger.warning(f"PowerShell method failed: {e}")
            
            # Fallback to pyautogui (limited Turkish support)
            try:
                import pyautogui
                # Convert Turkish characters to closest ASCII equivalents
                ascii_text = self._convert_turkish_to_ascii(text)
                pyautogui.write(ascii_text)
                return TextInputResult(
                    success=True,
                    text_entered=ascii_text,
                    method_used="pyautogui_ascii",
                    execution_time=0,
                    error=None
                )
            except ImportError:
                pass
            
            return TextInputResult(
                success=False,
                text_entered="",
                method_used="windows",
                execution_time=0,
                error="No text input method available"
            )
            
        except Exception as e:
            return TextInputResult(
                success=False,
                text_entered="",
                method_used="windows",
                execution_time=0,
                error=str(e)
            )
    
    async def _type_text_linux(self, text: str, parameters: Dict[str, Any]) -> TextInputResult:
        """Type text on Linux using xdotool or similar"""
        try:
            # Try xdotool
            import subprocess
            result = subprocess.run(
                ["xdotool", "type", text],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return TextInputResult(
                    success=True,
                    text_entered=text,
                    method_used="xdotool",
                    execution_time=0,
                    error=None
                )
            else:
                return TextInputResult(
                    success=False,
                    text_entered="",
                    method_used="xdotool",
                    execution_time=0,
                    error=f"xdotool failed: {result.stderr}"
                )
                
        except Exception as e:
            return TextInputResult(
                success=False,
                text_entered="",
                method_used="linux",
                execution_time=0,
                error=str(e)
            )
    
    async def _type_text_powershell(self, text: str, parameters: Dict[str, Any]) -> TextInputResult:
        """Type text using PowerShell on Windows (supports Turkish characters)"""
        try:
            import subprocess
            import json
            
            # Create a temporary file with the text to avoid escaping issues
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
                f.write(text)
                temp_file = f.name
            
            try:
                # Create PowerShell script that reads from file and types it
                ps_script = f'''
Add-Type -AssemblyName System.Windows.Forms
$text = Get-Content -Path "{temp_file}" -Encoding UTF8 -Raw
[System.Windows.Forms.SendKeys]::SendWait($text)
'''
                
                result = subprocess.run(
                    ["powershell", "-Command", ps_script],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    encoding='utf-8'
                )
                
                if result.returncode == 0:
                    return TextInputResult(
                        success=True,
                        text_entered=text,
                        method_used="powershell_utf8",
                        execution_time=0,
                        error=None
                    )
                else:
                    return TextInputResult(
                        success=False,
                        text_entered="",
                        method_used="powershell_utf8",
                        execution_time=0,
                        error=f"PowerShell failed: {result.stderr}"
                    )
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                
        except Exception as e:
            return TextInputResult(
                success=False,
                text_entered="",
                method_used="powershell_utf8",
                execution_time=0,
                error=str(e)
            )
    
    async def _test_windows_text_input(self):
        """Test Windows text input capability"""
        try:
            # Test PowerShell method without actual text input
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise Exception(f"PowerShell text input test failed: {result.stderr}")
                
        except Exception as e:
            self.logger.warning(f"Windows text input test failed: {e}")
            # Don't fail initialization, just warn
    
    async def _test_linux_text_input(self):
        """Test Linux text input capability"""
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
            self.logger.warning(f"Linux text input test failed: {e}")
            # Don't fail initialization, just warn
    
    def _convert_turkish_to_ascii(self, text: str) -> str:
        """Convert Turkish characters to ASCII equivalents for pyautogui fallback"""
        turkish_to_ascii = {
            'ç': 'c', 'Ç': 'C',
            'ğ': 'g', 'Ğ': 'G',
            'ı': 'i', 'İ': 'I',
            'ö': 'o', 'Ö': 'O',
            'ş': 's', 'Ş': 'S',
            'ü': 'u', 'Ü': 'U'
        }
        
        converted_text = text
        for turkish, ascii_char in turkish_to_ascii.items():
            converted_text = converted_text.replace(turkish, ascii_char)
        
        return converted_text

class TextGenerationExecutor:
    """Generates text using AI and then types it"""
    
    def __init__(self, ai_manager=None):
        self.logger = logging.getLogger(__name__)
        self.ai_manager = ai_manager
        self.text_input_executor = TextInputExecutor()
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize text generation executor"""
        try:
            if not await self.text_input_executor.initialize():
                return False
            
            self._is_initialized = True
            self.logger.info("Text generation executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize text generation executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return "prompt" in parameters
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text generation and typing capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Text generation executor not initialized"}
            
            prompt = parameters.get("prompt", "")
            if not prompt:
                return {"success": False, "error": "No prompt provided"}
            
            # Generate text using AI
            if self.ai_manager:
                ai_response = await self.ai_manager.generate_response(prompt)
                if ai_response and ai_response.content:
                    generated_text = ai_response.content.strip()
                else:
                    return {"success": False, "error": "Failed to generate text with AI"}
            else:
                # Fallback: simple text generation
                generated_text = f"Generated text for: {prompt}"
            
            # Type the generated text
            type_result = await self.text_input_executor._type_text(generated_text, {})
            
            return {
                "success": type_result.success,
                "text_entered": type_result.text_entered,
                "method_used": f"ai_generation + {type_result.method_used}",
                "execution_time": type_result.execution_time,
                "error": type_result.error,
                "generated_text": generated_text
            }
            
        except Exception as e:
            self.logger.error(f"Error executing text generation capability: {e}")
            return {"success": False, "error": str(e)}
