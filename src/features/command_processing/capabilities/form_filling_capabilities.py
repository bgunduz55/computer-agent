"""
Form Filling Capabilities for JARVIS Computer Assistant

Provides advanced form filling, text manipulation, and automation capabilities.
"""

import asyncio
import logging
import time
import platform
import re
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FormFieldType(Enum):
    """Types of form fields"""
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    PHONE = "phone"
    DATE = "date"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FILE = "file"

class TextManipulationType(Enum):
    """Types of text manipulation operations"""
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    TITLE_CASE = "title_case"
    SENTENCE_CASE = "sentence_case"
    REMOVE_SPACES = "remove_spaces"
    REMOVE_SPECIAL_CHARS = "remove_special_chars"
    FORMAT_PHONE = "format_phone"
    FORMAT_EMAIL = "format_email"
    CLEAN_TEXT = "clean_text"
    EXTRACT_NUMBERS = "extract_numbers"
    EXTRACT_EMAILS = "extract_emails"
    EXTRACT_URLS = "extract_urls"

@dataclass
class FormField:
    """Form field definition"""
    name: str
    field_type: FormFieldType
    value: str
    required: bool = True
    placeholder: Optional[str] = None
    validation_pattern: Optional[str] = None
    options: Optional[List[str]] = None  # For select fields

@dataclass
class FormData:
    """Form data structure"""
    fields: List[FormField]
    form_name: Optional[str] = None
    form_url: Optional[str] = None
    submit_button_text: Optional[str] = None

@dataclass
class TextManipulationResult:
    """Result of text manipulation operation"""
    success: bool
    original_text: str
    manipulated_text: str
    operation: TextManipulationType
    execution_time: float
    error: Optional[str] = None

@dataclass
class FormFillingResult:
    """Result of form filling operation"""
    success: bool
    fields_filled: int
    total_fields: int
    execution_time: float
    errors: List[str] = None
    filled_data: Dict[str, str] = None

class TextManipulationEngine:
    """Engine for text manipulation operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def manipulate_text(self, text: str, operation: TextManipulationType, 
                            parameters: Dict[str, Any] = None) -> TextManipulationResult:
        """Manipulate text based on operation type"""
        start_time = time.time()
        
        try:
            if operation == TextManipulationType.UPPERCASE:
                result_text = text.upper()
            elif operation == TextManipulationType.LOWERCASE:
                result_text = text.lower()
            elif operation == TextManipulationType.TITLE_CASE:
                result_text = text.title()
            elif operation == TextManipulationType.SENTENCE_CASE:
                result_text = self._sentence_case(text)
            elif operation == TextManipulationType.REMOVE_SPACES:
                result_text = text.replace(" ", "")
            elif operation == TextManipulationType.REMOVE_SPECIAL_CHARS:
                result_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
            elif operation == TextManipulationType.FORMAT_PHONE:
                result_text = self._format_phone(text)
            elif operation == TextManipulationType.FORMAT_EMAIL:
                result_text = self._format_email(text)
            elif operation == TextManipulationType.CLEAN_TEXT:
                result_text = self._clean_text(text)
            elif operation == TextManipulationType.EXTRACT_NUMBERS:
                result_text = self._extract_numbers(text)
            elif operation == TextManipulationType.EXTRACT_EMAILS:
                result_text = self._extract_emails(text)
            elif operation == TextManipulationType.EXTRACT_URLS:
                result_text = self._extract_urls(text)
            else:
                result_text = text
            
            execution_time = time.time() - start_time
            return TextManipulationResult(
                success=True,
                original_text=text,
                manipulated_text=result_text,
                operation=operation,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TextManipulationResult(
                success=False,
                original_text=text,
                manipulated_text="",
                operation=operation,
                execution_time=execution_time,
                error=str(e)
            )
    
    def _sentence_case(self, text: str) -> str:
        """Convert text to sentence case"""
        sentences = re.split(r'[.!?]+', text)
        result = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                result.append(sentence[0].upper() + sentence[1:].lower())
        return '. '.join(result) + '.'
    
    def _format_phone(self, text: str) -> str:
        """Format phone number"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', text)
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return text
    
    def _format_email(self, text: str) -> str:
        """Format email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.match(email_pattern, text):
            return text.lower().strip()
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra spaces and normalizing"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        return text
    
    def _extract_numbers(self, text: str) -> str:
        """Extract numbers from text"""
        numbers = re.findall(r'\d+', text)
        return ', '.join(numbers)
    
    def _extract_emails(self, text: str) -> str:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return ', '.join(emails)
    
    def _extract_urls(self, text: str) -> str:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return ', '.join(urls)

class FormFillingExecutor:
    """Executes form filling operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.platform = platform.system().lower()
        self.text_manipulation_engine = TextManipulationEngine()
        
    async def initialize(self) -> bool:
        """Initialize form filling executor"""
        try:
            self._is_initialized = True
            self.logger.info("Form filling executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize form filling executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("form_data" in parameters or 
                "text_manipulation" in parameters or
                "fill_field" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute form filling capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Form filling executor not initialized"}
            
            # Text manipulation
            if "text_manipulation" in parameters:
                return await self._execute_text_manipulation(parameters, context)
            
            # Form filling
            elif "form_data" in parameters:
                return await self._execute_form_filling(parameters, context)
            
            # Single field filling
            elif "fill_field" in parameters:
                return await self._execute_field_filling(parameters, context)
            
            else:
                return {"success": False, "error": "No valid operation specified"}
                
        except Exception as e:
            self.logger.error(f"Error executing form filling capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_text_manipulation(self, parameters: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text manipulation operation"""
        try:
            text = parameters.get("text", "")
            operation_str = parameters.get("text_manipulation", "")
            
            if not text:
                return {"success": False, "error": "No text provided"}
            
            try:
                operation = TextManipulationType(operation_str)
            except ValueError:
                return {"success": False, "error": f"Invalid operation: {operation_str}"}
            
            result = await self.text_manipulation_engine.manipulate_text(
                text, operation, parameters
            )
            
            return {
                "success": result.success,
                "original_text": result.original_text,
                "manipulated_text": result.manipulated_text,
                "operation": result.operation.value,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_form_filling(self, parameters: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute form filling operation"""
        try:
            form_data_dict = parameters.get("form_data", {})
            form_data = self._parse_form_data(form_data_dict)
            
            if not form_data or not form_data.fields:
                return {"success": False, "error": "No form data provided"}
            
            result = await self._fill_form(form_data, context)
            
            return {
                "success": result.success,
                "fields_filled": result.fields_filled,
                "total_fields": result.total_fields,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "filled_data": result.filled_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_field_filling(self, parameters: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single field filling operation"""
        try:
            field_name = parameters.get("field_name", "")
            field_value = parameters.get("field_value", "")
            field_type = parameters.get("field_type", "text")
            
            if not field_name or not field_value:
                return {"success": False, "error": "Field name and value required"}
            
            # Create a single field form
            field = FormField(
                name=field_name,
                field_type=FormFieldType(field_type),
                value=field_value
            )
            
            form_data = FormData(fields=[field])
            result = await self._fill_form(form_data, context)
            
            return {
                "success": result.success,
                "field_filled": field_name,
                "field_value": field_value,
                "execution_time": result.execution_time,
                "error": result.errors[0] if result.errors else None
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_form_data(self, form_data_dict: Dict[str, Any]) -> FormData:
        """Parse form data from dictionary"""
        try:
            fields = []
            for field_dict in form_data_dict.get("fields", []):
                field = FormField(
                    name=field_dict.get("name", ""),
                    field_type=FormFieldType(field_dict.get("type", "text")),
                    value=field_dict.get("value", ""),
                    required=field_dict.get("required", True),
                    placeholder=field_dict.get("placeholder"),
                    validation_pattern=field_dict.get("validation_pattern"),
                    options=field_dict.get("options")
                )
                fields.append(field)
            
            return FormData(
                fields=fields,
                form_name=form_data_dict.get("form_name"),
                form_url=form_data_dict.get("form_url"),
                submit_button_text=form_data_dict.get("submit_button_text")
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing form data: {e}")
            return FormData(fields=[])
    
    async def _fill_form(self, form_data: FormData, context: Dict[str, Any]) -> FormFillingResult:
        """Fill form with provided data"""
        start_time = time.time()
        filled_data = {}
        errors = []
        fields_filled = 0
        
        try:
            for field in form_data.fields:
                try:
                    # Validate field value
                    if field.required and not field.value:
                        errors.append(f"Required field '{field.name}' is empty")
                        continue
                    
                    # Apply text manipulation if needed
                    processed_value = await self._process_field_value(field)
                    
                    # Fill the field (simulate for now - would integrate with browser automation)
                    filled_data[field.name] = processed_value
                    fields_filled += 1
                    
                    # Add small delay between fields
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    errors.append(f"Error filling field '{field.name}': {str(e)}")
            
            execution_time = time.time() - start_time
            return FormFillingResult(
                success=len(errors) == 0,
                fields_filled=fields_filled,
                total_fields=len(form_data.fields),
                execution_time=execution_time,
                errors=errors,
                filled_data=filled_data
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return FormFillingResult(
                success=False,
                fields_filled=fields_filled,
                total_fields=len(form_data.fields),
                execution_time=execution_time,
                errors=[str(e)],
                filled_data=filled_data
            )
    
    async def _process_field_value(self, field: FormField) -> str:
        """Process field value based on field type"""
        value = field.value
        
        # Apply field-specific processing
        if field.field_type == FormFieldType.EMAIL:
            # Format email
            result = await self.text_manipulation_engine.manipulate_text(
                value, TextManipulationType.FORMAT_EMAIL
            )
            value = result.manipulated_text
            
        elif field.field_type == FormFieldType.PHONE:
            # Format phone number
            result = await self.text_manipulation_engine.manipulate_text(
                value, TextManipulationType.FORMAT_PHONE
            )
            value = result.manipulated_text
            
        elif field.field_type == FormFieldType.TEXT:
            # Clean text
            result = await self.text_manipulation_engine.manipulate_text(
                value, TextManipulationType.CLEAN_TEXT
            )
            value = result.manipulated_text
        
        # Apply validation if pattern provided
        if field.validation_pattern:
            if not re.match(field.validation_pattern, value):
                raise ValueError(f"Field '{field.name}' does not match validation pattern")
        
        return value

class AdvancedTextInputExecutor:
    """Advanced text input executor with enhanced capabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.platform = platform.system().lower()
        self.form_filling_executor = FormFillingExecutor()
        self.text_manipulation_engine = TextManipulationEngine()
        
    async def initialize(self) -> bool:
        """Initialize advanced text input executor"""
        try:
            if not await self.form_filling_executor.initialize():
                return False
            
            self._is_initialized = True
            self.logger.info("Advanced text input executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize advanced text input executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("advanced_text_input" in parameters or
                "smart_typing" in parameters or
                "text_automation" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute advanced text input capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Advanced text input executor not initialized"}
            
            operation = parameters.get("operation", "type_text")
            
            if operation == "type_text":
                return await self._execute_smart_typing(parameters, context)
            elif operation == "fill_form":
                return await self._execute_form_filling(parameters, context)
            elif operation == "manipulate_text":
                return await self._execute_text_manipulation(parameters, context)
            elif operation == "auto_complete":
                return await self._execute_auto_complete(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing advanced text input capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_smart_typing(self, parameters: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute smart typing with context awareness"""
        try:
            text = parameters.get("text", "")
            typing_speed = parameters.get("typing_speed", "normal")
            auto_format = parameters.get("auto_format", True)
            
            if not text:
                return {"success": False, "error": "No text provided"}
            
            # Apply auto-formatting if enabled
            if auto_format:
                # Clean and format text
                clean_result = await self.text_manipulation_engine.manipulate_text(
                    text, TextManipulationType.CLEAN_TEXT
                )
                text = clean_result.manipulated_text
            
            # Simulate typing with appropriate speed
            typing_delay = self._get_typing_delay(typing_speed)
            
            # Type text character by character with delay
            for char in text:
                # Here we would integrate with actual typing mechanism
                await asyncio.sleep(typing_delay)
            
            return {
                "success": True,
                "text_typed": text,
                "typing_speed": typing_speed,
                "characters_typed": len(text),
                "execution_time": len(text) * typing_delay
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_form_filling(self, parameters: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute form filling using the form filling executor"""
        return await self.form_filling_executor.execute(parameters, context)
    
    async def _execute_text_manipulation(self, parameters: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text manipulation using the form filling executor"""
        return await self.form_filling_executor.execute(parameters, context)
    
    async def _execute_auto_complete(self, parameters: Dict[str, Any], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute auto-completion based on context"""
        try:
            partial_text = parameters.get("partial_text", "")
            context_hints = parameters.get("context_hints", [])
            
            if not partial_text:
                return {"success": False, "error": "No partial text provided"}
            
            # Simple auto-completion logic (would be enhanced with AI)
            suggestions = self._generate_suggestions(partial_text, context_hints)
            
            return {
                "success": True,
                "partial_text": partial_text,
                "suggestions": suggestions,
                "best_suggestion": suggestions[0] if suggestions else ""
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_typing_delay(self, speed: str) -> float:
        """Get typing delay based on speed setting"""
        delays = {
            "slow": 0.2,
            "normal": 0.05,
            "fast": 0.01,
            "instant": 0.0
        }
        return delays.get(speed, 0.05)
    
    def _generate_suggestions(self, partial_text: str, context_hints: List[str]) -> List[str]:
        """Generate auto-completion suggestions"""
        suggestions = []
        
        # Add context-based suggestions
        for hint in context_hints:
            if hint.lower().startswith(partial_text.lower()):
                suggestions.append(hint)
        
        # Add common completions
        common_completions = [
            "hello", "world", "test", "example", "sample",
            "email", "phone", "address", "name", "date"
        ]
        
        for completion in common_completions:
            if completion.lower().startswith(partial_text.lower()):
                suggestions.append(completion)
        
        return suggestions[:5]  # Return top 5 suggestions

