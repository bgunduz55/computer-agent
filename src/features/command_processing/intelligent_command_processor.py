"""
Intelligent Command Processor

AI-powered command processing system that understands complex, multi-step commands
and executes them using the assistant's capabilities.
"""

import asyncio
import logging
import platform
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from ..ai_integration import AIProviderManager, AIRequest, AIResponse, AIProviderType
from .command_planner import CommandPlanner, CommandStep, ExecutionPlan
from .capability_system import CapabilityManager, Capability
from .dynamic_capability_system import DynamicCapabilityManager, DynamicCapability
from .execution_context import ExecutionContext
from .command_orchestrator import CommandOrchestrator
from .sequential_execution_engine import SequentialExecutionEngine, ExecutionStrategy
from .command_decomposition_engine import IntelligentCommandDecompositionEngine, DecompositionStrategy
from .context_aware_execution import ContextAwareExecutionManager, ContextType, ContextPriority
from .error_recovery_learning import ErrorRecoveryLearningSystem, ErrorSeverity, ErrorCategory
from shared.websocket_protocol import WebSocketMessage, MessageBuilder

logger = logging.getLogger(__name__)

class CommandComplexity(Enum):
    """Command complexity levels"""
    SIMPLE = "simple"      # Single action
    MODERATE = "moderate"  # 2-3 steps
    COMPLEX = "complex"    # 4+ steps with dependencies

@dataclass
class IntelligentCommandResult:
    """Result of intelligent command processing"""
    success: bool
    message: str
    execution_time: float
    steps_executed: int
    total_steps: int
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class IntelligentCommandProcessor:
    """AI-powered intelligent command processor"""
    
    def __init__(self, ai_manager: AIProviderManager, capability_manager: CapabilityManager):
        self.ai_manager = ai_manager
        self.capability_manager = capability_manager
        self.dynamic_capability_manager: Optional[DynamicCapabilityManager] = None
        self.command_planner = CommandPlanner(capability_manager)
        self.decomposition_engine = IntelligentCommandDecompositionEngine(ai_manager, capability_manager)
        self.context_manager: Optional[ContextAwareExecutionManager] = None
        self.learning_system: Optional[ErrorRecoveryLearningSystem] = None
        self.orchestrator = CommandOrchestrator()
        self.sequential_engine: Optional[SequentialExecutionEngine] = None
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the intelligent command processor"""
        try:
            # AI manager initialization is handled in constructor
            pass
            
            if not self.capability_manager.is_initialized():
                await self.capability_manager.initialize()
            
            # Initialize dynamic capability manager
            from .dynamic_capability_system import get_dynamic_capability_manager
            from .sequential_execution_engine import get_sequential_execution_engine
            
            self.dynamic_capability_manager = await get_dynamic_capability_manager()
            self.sequential_engine = await get_sequential_execution_engine()
            
            await self.command_planner.initialize()
            await self.decomposition_engine.initialize()
            
            # Initialize context manager
            from .context_aware_execution import get_context_manager
            self.context_manager = get_context_manager()
            
            # Initialize learning system
            from .error_recovery_learning import get_error_recovery_system
            self.learning_system = get_error_recovery_system()
            
            await self.orchestrator.initialize()
            
            self._is_initialized = True
            self.logger.info("Intelligent command processor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize intelligent command processor: {e}")
            return False
    
    async def process_intelligent_command(
        self, 
        command: str, 
        context: Optional[Dict[str, Any]] = None,
        client_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> IntelligentCommandResult:
        """
        Process an intelligent command using AI with context awareness
        
        Args:
            command: The voice command to process
            context: Additional context information
            client_id: Client ID for progress updates
            session_id: Session ID for context persistence
            
        Returns:
            IntelligentCommandResult with execution details
        """
        if not self._is_initialized:
            return IntelligentCommandResult(
                success=False,
                message="Intelligent command processor not initialized",
                execution_time=0.0,
                steps_executed=0,
                total_steps=0,
                error="Not initialized"
            )
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing intelligent command: {command}")
            
            # Step 1: Get or create execution context
            execution_context = await self._get_or_create_execution_context(
                session_id, client_id, command, context
            )
            
            # Step 2: Analyze command complexity with context
            complexity = await self._analyze_command_complexity(command)
            self.logger.info(f"Command complexity: {complexity.value}")
            
            # Step 3: Generate AI context with capabilities and memory
            ai_context = await self._generate_ai_context_with_memory(command, context, execution_context)
            
            # Step 4: Process command with AI
            ai_response = await self._process_with_ai(command, ai_context)
            
            if ai_response.metadata and ai_response.metadata.get("error"):
                return IntelligentCommandResult(
                    success=False,
                    message="AI processing failed",
                    execution_time=time.time() - start_time,
                    steps_executed=0,
                    total_steps=0,
                    error=ai_response.metadata.get("error")
                )
            
            # Step 5: Use intelligent decomposition engine for complex commands
            if complexity == CommandComplexity.COMPLEX:
                decomposition_result = await self.decomposition_engine.decompose_command(command, context)
                if decomposition_result.success:
                    execution_plan = await self._create_execution_plan_from_decomposition(decomposition_result)
                else:
                    # Fallback to AI response parsing
                    execution_plan = await self._parse_ai_response(ai_response, command)
            else:
                # For simple/moderate commands, use AI response parsing
                execution_plan = await self._parse_ai_response(ai_response, command)
            
            if not execution_plan:
                return IntelligentCommandResult(
                    success=False,
                    message="Failed to create execution plan",
                    execution_time=time.time() - start_time,
                    steps_executed=0,
                    total_steps=0,
                    error="Invalid AI response format"
                )
            
            # Step 6: Execute the plan with context awareness
            execution_result = await self._execute_plan_with_context(
                execution_plan, 
                command, 
                client_id,
                execution_context
            )
            
            execution_time = time.time() - start_time
            
            return IntelligentCommandResult(
                success=execution_result.success,
                message=execution_result.message,
                execution_time=execution_time,
                steps_executed=execution_result.steps_executed,
                total_steps=execution_result.total_steps,
                error=execution_result.error,
                metadata=execution_result.metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error processing intelligent command: {e}")
            
            # Record error for learning
            if self.learning_system:
                error_id = await self.learning_system.record_error(
                    error=e,
                    context={
                        "command": command,
                        "session_id": session_id,
                        "client_id": client_id,
                        "context": context
                    },
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.AI_PROCESSING
                )
                
                # Attempt recovery
                if error_id:
                    recovery_success, recovery_message = await self.learning_system.attempt_recovery(
                        error_id, 
                        {
                            "command": command,
                            "session_id": session_id,
                            "client_id": client_id
                        }
                    )
                    
                    if recovery_success:
                        self.logger.info(f"Error recovery successful: {recovery_message}")
                        # Continue with recovered execution
                        return await self.process_intelligent_command(command, context, client_id, session_id)
            
            # Enhanced error handling with recovery suggestions
            error_message = self._create_error_message(e, command)
            recovery_suggestions = self._get_recovery_suggestions(e, command)
            
            return IntelligentCommandResult(
                success=False,
                message=error_message,
                execution_time=time.time() - start_time,
                steps_executed=0,
                total_steps=0,
                error=str(e),
                metadata={
                    "error_type": type(e).__name__,
                    "recovery_suggestions": recovery_suggestions,
                    "command_complexity": "unknown",
                    "error_id": error_id if 'error_id' in locals() else None
                }
            )
    
    async def _analyze_command_complexity(self, command: str) -> CommandComplexity:
        """Analyze the complexity of the command with enhanced intelligence"""
        command_lower = command.lower()
        
        # Enhanced complexity analysis
        complexity_score = 0
        
        # 1. Sequential indicators (Turkish & English)
        sequential_keywords = [
            'then', 'after', 'next', 'also', 'and', 'while', 'during', 'first', 'second', 'finally',
            'sonra', 'ardından', 'sonraki', 'ayrıca', 've', 'iken', 'sırasında', 'önce', 'sonra', 'sonunda'
        ]
        complexity_score += sum(1 for keyword in sequential_keywords if keyword in command_lower) * 2
        
        # 2. Action verbs (multi-step indicators)
        action_verbs = [
            'open', 'create', 'write', 'save', 'close', 'send', 'search', 'play', 'find', 'download',
            'aç', 'oluştur', 'yaz', 'kaydet', 'kapat', 'gönder', 'ara', 'oynat', 'bul', 'indir'
        ]
        complexity_score += sum(1 for verb in action_verbs if verb in command_lower)
        
        # 3. Conditional statements
        conditional_keywords = [
            'if', 'when', 'unless', 'provided', 'eğer', 'ne zaman', 'sadece', 'şartıyla'
        ]
        complexity_score += sum(1 for keyword in conditional_keywords if keyword in command_lower) * 3
        
        # 4. Multi-object operations
        multi_object_patterns = [
            'and then', 've sonra', 'also', 'ayrıca', 'both', 'her ikisi', 'multiple', 'birden fazla'
        ]
        complexity_score += sum(1 for pattern in multi_object_patterns if pattern in command_lower) * 2
        
        # 5. File operations (usually multi-step)
        file_operations = [
            'file', 'dosya', 'document', 'belge', 'folder', 'klasör', 'directory', 'dizin'
        ]
        if any(op in command_lower for op in file_operations):
            complexity_score += 2
        
        # 6. Web operations (usually multi-step)
        web_operations = [
            'website', 'web sitesi', 'browser', 'tarayıcı', 'url', 'link', 'bağlantı'
        ]
        if any(op in command_lower for op in web_operations):
            complexity_score += 2
        
        # 7. Command length factor
        word_count = len(command.split())
        if word_count > 10:
            complexity_score += 2
        elif word_count > 5:
            complexity_score += 1
        
        # 8. Special complexity patterns
        special_patterns = [
            'create.*and.*write', 'oluştur.*ve.*yaz', 'open.*and.*search', 'aç.*ve.*ara',
            'find.*and.*play', 'bul.*ve.*oynat', 'download.*and.*open', 'indir.*ve.*aç'
        ]
        import re
        for pattern in special_patterns:
            if re.search(pattern, command_lower):
                complexity_score += 3
        
        # Determine complexity level
        if complexity_score >= 8:
            return CommandComplexity.COMPLEX
        elif complexity_score >= 4:
            return CommandComplexity.MODERATE
        else:
            return CommandComplexity.SIMPLE
    
    async def _generate_ai_context(self, command: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI context with capabilities and system state"""
        try:
            # Get available capabilities (both built-in and dynamic)
            builtin_capabilities = await self.capability_manager.get_all_capabilities()
            dynamic_capabilities = []
            
            if self.dynamic_capability_manager:
                dynamic_capabilities = await self.dynamic_capability_manager.get_all_capabilities()
            
            # Combine capabilities
            all_capabilities = [cap.to_dict() for cap in builtin_capabilities]
            all_capabilities.extend([cap.to_dict() for cap in dynamic_capabilities])
            
            # Get system state
            system_state = await self._get_system_state()
            
            # Get available terminal commands
            available_commands = []
            if self.dynamic_capability_manager:
                from .terminal_capability_executor import TerminalCapabilityExecutor
                terminal_executor = TerminalCapabilityExecutor()
                await terminal_executor.initialize()
                available_commands = await terminal_executor.get_available_commands()
                await terminal_executor.cleanup()
            
            # Build context
            ai_context = {
                "command": command,
                "capabilities": all_capabilities,
                "system_state": system_state,
                "available_commands": available_commands,
                "user_context": context or {},
                "timestamp": time.time()
            }
            
            return ai_context
            
        except Exception as e:
            self.logger.error(f"Error generating AI context: {e}")
            return {"command": command, "capabilities": [], "system_state": {}, "available_commands": []}
    
    async def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        try:
            # This would integrate with system info manager
            return {
                "platform": "windows",  # or detect actual platform
                "available_apps": [],  # Get from application manager
                "current_directory": "",  # Get from file manager
                "running_processes": [],  # Get from process manager
                "network_status": "connected"
            }
        except Exception as e:
            self.logger.error(f"Error getting system state: {e}")
            return {}
    
    async def _process_with_ai(self, command: str, context: Dict[str, Any]) -> AIResponse:
        """Process command with AI"""
        try:
            # Create AI prompt
            prompt = self._create_ai_prompt(command, context)
            
            # Log the prompt for debugging
            self.logger.info("=" * 80)
            self.logger.info("🤖 AI PROMPT SENT TO LLM:")
            self.logger.info("=" * 80)
            self.logger.info(prompt)
            self.logger.info("=" * 80)
            
            # Generate AI response using string prompt
            response = await self.ai_manager.generate_response(prompt)
            
            # Log the response for debugging
            self.logger.info("🤖 AI RESPONSE RECEIVED:")
            self.logger.info("=" * 80)
            self.logger.info(response.content)
            self.logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing with AI: {e}")
            return AIResponse(
                content="",
                model="",
                provider=AIProviderType.OPENAI,
                tokens_used=0,
                cost=0.0,
                response_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _create_ai_prompt(self, command: str, context: Dict[str, Any]) -> str:
        """Create enhanced AI prompt for command processing"""
        capabilities = context.get("capabilities", [])
        system_state = context.get("system_state", {})
        available_commands = context.get("available_commands", [])
        
        # Detect language
        is_turkish = any(char in command for char in 'çğıöşüÇĞIÖŞÜ')
        language = "Turkish" if is_turkish else "English"
        
        # Create detailed capability mapping
        capability_map = self._create_capability_map(capabilities)
        
        # Create system context
        system_context = self._create_system_context(system_state, available_commands)
        
        # Create examples based on language
        examples = self._create_examples(language)
        
        prompt = f"""You are JARVIS - an advanced AI computer assistant with Iron Man-level intelligence. 

USER COMMAND ({language}): "{command}"

SYSTEM CONTEXT:
{system_context}

AVAILABLE CAPABILITIES:
{capability_map}

INTELLIGENT PROCESSING RULES:
1. ANALYZE the command for multi-step operations
2. BREAK DOWN complex commands into logical sequential steps
3. CHOOSE the most appropriate capability for each step
4. CONSIDER dependencies between steps
5. PROVIDE detailed step descriptions
6. ESTIMATE realistic execution times

MULTI-STEP EXAMPLES:
{examples}

OUTPUT FORMAT - Return ONLY this JSON:
{{
    "analysis": {{
        "intent": "Detailed description of what user wants to accomplish",
        "complexity": "simple|moderate|complex",
        "language": "{language}",
        "requires_confirmation": false,
        "estimated_risk": "low|medium|high"
    }},
    "execution_plan": {{
        "steps": [
            {{
                "step_id": "step_1",
                "description": "Clear description of what this step accomplishes",
                "capability": "exact_capability_name",
                "parameters": {{"param": "value"}},
                "dependencies": [],
                "estimated_duration": 5,
                "can_parallelize": false
            }},
            {{
                "step_id": "step_2", 
                "description": "Next step description",
                "capability": "exact_capability_name",
                "parameters": {{"param": "value"}},
                "dependencies": ["step_1"],
                "estimated_duration": 3,
                "can_parallelize": false
            }}
        ],
        "total_steps": 2,
        "estimated_duration": 8,
        "parallel_steps": 0,
        "requires_user_input": false
    }}
}}"""
        return prompt
    
    def _create_capability_map(self, capabilities: List[Dict[str, Any]]) -> str:
        """Create detailed capability mapping for AI prompt"""
        if not capabilities:
            return "No capabilities available"
        
        # Group capabilities by category
        categories = {
            "Web Operations": [],
            "File Management": [],
            "System Control": [],
            "Text Input": [],
            "Application Control": [],
            "Terminal Commands": [],
            "Other": []
        }
        
        for cap in capabilities:
            name = cap.get('name', 'Unknown')
            description = cap.get('description', 'No description')
            parameters = cap.get('parameters', {})
            
            # Categorize capabilities
            if any(keyword in name.lower() for keyword in ['web', 'browser', 'url', 'search', 'youtube']):
                categories["Web Operations"].append((name, description, parameters))
            elif any(keyword in name.lower() for keyword in ['file', 'directory', 'folder', 'create', 'delete', 'copy']):
                categories["File Management"].append((name, description, parameters))
            elif any(keyword in name.lower() for keyword in ['system', 'shutdown', 'restart', 'volume', 'brightness']):
                categories["System Control"].append((name, description, parameters))
            elif any(keyword in name.lower() for keyword in ['text', 'input', 'type', 'keyboard']):
                categories["Text Input"].append((name, description, parameters))
            elif any(keyword in name.lower() for keyword in ['app', 'application', 'launch', 'open']):
                categories["Application Control"].append((name, description, parameters))
            elif any(keyword in name.lower() for keyword in ['terminal', 'command', 'execute']):
                categories["Terminal Commands"].append((name, description, parameters))
            else:
                categories["Other"].append((name, description, parameters))
        
        # Format each category
        formatted = []
        for category, caps in categories.items():
            if caps:
                formatted.append(f"\n{category}:")
                for name, description, parameters in caps:
                    formatted.append(f"  • {name}: {description}")
                    if parameters:
                        param_list = ', '.join([f"{k}: {v}" for k, v in parameters.items()])
                        formatted.append(f"    Parameters: {param_list}")
        
        return "\n".join(formatted)
    
    def _create_system_context(self, system_state: Dict[str, Any], available_commands: List[str]) -> str:
        """Create system context for AI prompt"""
        context_parts = []
        
        # Platform information
        platform = system_state.get('platform', 'unknown')
        context_parts.append(f"Platform: {platform}")
        
        # Available applications
        apps = system_state.get('available_apps', [])
        if apps:
            context_parts.append(f"Available Applications: {', '.join(apps[:10])}")
        
        # Current directory
        current_dir = system_state.get('current_directory', '')
        if current_dir:
            context_parts.append(f"Current Directory: {current_dir}")
        
        # Running processes
        processes = system_state.get('running_processes', [])
        if processes:
            context_parts.append(f"Running Processes: {len(processes)} active")
        
        # Network status
        network = system_state.get('network_status', 'unknown')
        context_parts.append(f"Network Status: {network}")
        
        # Available terminal commands
        if available_commands:
            context_parts.append(f"Available Terminal Commands: {', '.join(available_commands[:15])}")
        
        return "\n".join(context_parts) if context_parts else "No system context available"
    
    def _create_examples(self, language: str) -> str:
        """Create multi-step examples based on language"""
        if language == "Turkish":
            return """
TÜRKÇE ÖRNEKLER:
1. "YouTube'da müzik bul ve aç" → 2 adım:
   - Step 1: YouTube'da arama yap
   - Step 2: Bulunan videoyu aç

2. "Dosya oluştur, içine yaz ve kaydet" → 3 adım:
   - Step 1: Yeni dosya oluştur
   - Step 2: İçine metin yaz
   - Step 3: Dosyayı kaydet

3. "Chrome aç, Google'a git ve Python ara" → 3 adım:
   - Step 1: Chrome tarayıcısını aç
   - Step 2: Google'a git
   - Step 3: Python ara
"""
        else:
            return """
ENGLISH EXAMPLES:
1. "Find music on YouTube and play it" → 2 steps:
   - Step 1: Search YouTube for music
   - Step 2: Play the found video

2. "Create a file, write to it and save" → 3 steps:
   - Step 1: Create new file
   - Step 2: Write text to file
   - Step 3: Save the file

3. "Open Chrome, go to Google and search Python" → 3 steps:
   - Step 1: Open Chrome browser
   - Step 2: Navigate to Google
   - Step 3: Search for Python
"""
    
    def _format_capabilities(self, capabilities: List[Dict[str, Any]]) -> str:
        """Format capabilities for AI prompt (legacy method)"""
        if not capabilities:
            return "No capabilities available"
        
        formatted = []
        for cap in capabilities:
            formatted.append(f"- {cap.get('name', 'Unknown')}: {cap.get('description', 'No description')}")
            if cap.get('parameters'):
                formatted.append(f"  Parameters: {', '.join(cap['parameters'].keys())}")
        
        return "\n".join(formatted)
    
    def _format_system_state(self, system_state: Dict[str, Any]) -> str:
        """Format system state for AI prompt"""
        if not system_state:
            return "No system state available"
        
        formatted = []
        for key, value in system_state.items():
            if isinstance(value, list):
                formatted.append(f"- {key}: {len(value)} items")
            else:
                formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted)
    
    async def _parse_ai_response(self, ai_response: AIResponse, original_command: str) -> Optional[ExecutionPlan]:
        """Parse AI response into execution plan with fallback to terminal commands"""
        try:
            import json
            import re
            
            # Extract and clean JSON from AI response
            response_text = ai_response.content.strip()
            response_text = self._clean_ai_response(response_text)
            
            # Try multiple JSON extraction methods
            json_text = self._extract_json_from_response(response_text)
            
            if not json_text:
                self.logger.warning("No valid JSON found in AI response, creating terminal command fallback")
                return self._create_terminal_fallback_plan(original_command)
            
            # Parse JSON with error handling
            try:
                plan_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON decode error: {e}, trying to fix JSON")
                json_text = self._fix_json_syntax(json_text)
                if json_text:
                    plan_data = json.loads(json_text)
                else:
                    raise e
            
            # Create execution plan from new JSON format
            execution_plan_data = plan_data.get("execution_plan", {})
            analysis_data = plan_data.get("analysis", {})
            
            steps = []
            for step_data in execution_plan_data.get("steps", []):
                step = CommandStep(
                    name=step_data.get("step_id", ""),
                    description=step_data.get("description", ""),
                    capability_name=step_data.get("capability", ""),
                    parameters=step_data.get("parameters", {}),
                    dependencies=[],  # Will be handled by orchestrator
                    estimated_duration=5  # Default duration
                )
                steps.append(step)
            
            plan = ExecutionPlan(
                original_command=original_command,
                steps=steps,
                total_estimated_duration=execution_plan_data.get("estimated_duration", 30),
                complexity=analysis_data.get("complexity", "simple")
            )
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")
            # Fallback: Create a simple terminal command plan
            return self._create_terminal_fallback_plan(original_command)
    
    def _clean_ai_response(self, response_text: str) -> str:
        """Clean AI response text"""
        import re
        
        # Remove <think> tags and content
        response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        
        # Remove extra whitespace
        response_text = response_text.strip()
        
        return response_text
    
    def _extract_json_from_response(self, response_text: str) -> Optional[str]:
        """Extract JSON from AI response using multiple methods"""
        import json
        import re
        
        # Method 1: Direct JSON
        if response_text.startswith('{') and response_text.endswith('}'):
            try:
                json.loads(response_text)
                return response_text
            except:
                pass
        
        # Method 2: Find JSON block with better parsing
        start = response_text.find('{')
        if start != -1:
            # Find the matching closing brace
            brace_count = 0
            end = start
            for i, char in enumerate(response_text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if end > start:
                json_text = response_text[start:end]
                try:
                    json.loads(json_text)
                    return json_text
                except:
                    pass
        
        # Method 3: Find JSON array
        start = response_text.find('[')
        if start != -1:
            bracket_count = 0
            end = start
            for i, char in enumerate(response_text[start:], start):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end = i + 1
                        break
            
            if end > start:
                json_text = response_text[start:end]
                try:
                    json.loads(json_text)
                    return json_text
                except:
                    pass
        
        # Method 4: Regex pattern matching
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)
        for match in matches:
            try:
                json.loads(match)
                return match
            except:
                continue
        
        return None
    
    def _fix_json_syntax(self, json_text: str) -> Optional[str]:
        """Try to fix common JSON syntax errors"""
        try:
            # Fix common issues
            json_text = json_text.replace("'", '"')  # Single quotes to double quotes
            json_text = re.sub(r'(\w+):', r'"\1":', json_text)  # Add quotes to keys
            json_text = json_text.replace('True', 'true')
            json_text = json_text.replace('False', 'false')
            json_text = json_text.replace('None', 'null')
            
            # Try to parse
            json.loads(json_text)
            return json_text
        except:
            return None
    
    def _create_terminal_fallback_plan(self, command: str) -> ExecutionPlan:
        """Create a fallback plan using terminal commands"""
        command_lower = command.lower()
        steps = []

        # YouTube commands
        if any(word in command_lower for word in ['youtube', 'müzik', 'müziği', 'şarkı', 'video']):
            search_query = command.replace('youtube', '').replace('müziği', '').replace('müzik', '').replace('şarkı', '').replace('video', '').strip()
            if search_query:
                steps.append(CommandStep(
                    name="youtube_search",
                    description=f"Search YouTube for: {search_query}",
                    capability_name="terminal_command",
                    parameters={"command": f"start chrome \"https://www.youtube.com/results?search_query={search_query}\""},
                    dependencies=[],
                    estimated_duration=5
                ))

        # Google search commands
        elif any(word in command_lower for word in ['google', 'ara', 'search']):
            search_query = command.replace('google', '').replace('ara', '').replace('search', '').strip()
            if search_query:
                steps.append(CommandStep(
                    name="google_search",
                    description=f"Search Google for: {search_query}",
                    capability_name="terminal_command",
                    parameters={"command": f"start chrome \"https://www.google.com/search?q={search_query}\""},
                    dependencies=[],
                    estimated_duration=5
                ))
            else:
                steps.append(CommandStep(
                    name="open_google",
                    description="Open Google homepage",
                    capability_name="terminal_command",
                    parameters={"command": "start chrome https://www.google.com"},
                    dependencies=[],
                    estimated_duration=3
                ))

        # YouTube commands
        elif any(word in command_lower for word in ['youtube', 'müzik', 'muzik', 'video', 'şarkı', 'sarki']):
            # Extract search term from command
            search_terms = []
            for word in command_lower.split():
                if word not in ['youtube', 'müzik', 'muzik', 'video', 'şarkı', 'sarki', 'aç', 'ac', 'bul', 'ara', 'oynat', 'play']:
                    search_terms.append(word)
            
            search_query = " ".join(search_terms) if search_terms else "music"
            youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
            
            if platform.system().lower() == "windows":
                steps.append(CommandStep(
                    name="youtube_search",
                    description=f"Search YouTube for: {search_query}",
                    capability_name="terminal_command",
                    parameters={"command": f'start "" "{youtube_url}"'},
                    dependencies=[],
                    estimated_duration=5
                ))
            else:
                steps.append(CommandStep(
                    name="youtube_search",
                    description=f"Search YouTube for: {search_query}",
                    capability_name="terminal_command",
                    parameters={"command": f'xdg-open "{youtube_url}"'},
                    dependencies=[],
                    estimated_duration=5
                ))

        # Application commands
        elif any(word in command_lower for word in ['not defteri', 'notepad', 'hesap makinesi', 'calculator', 'paint', 'chrome', 'firefox']):
            if 'not defteri' in command_lower or 'notepad' in command_lower:
                steps.append(CommandStep(
                    name="open_notepad",
                    description="Open Notepad",
                    capability_name="terminal_command",
                    parameters={"command": "notepad"},
                    dependencies=[],
                    estimated_duration=3
                ))
            elif 'hesap makinesi' in command_lower or 'calculator' in command_lower:
                steps.append(CommandStep(
                    name="open_calculator",
                    description="Open Calculator",
                    capability_name="terminal_command",
                    parameters={"command": "calc"},
                    dependencies=[],
                    estimated_duration=3
                ))
            elif 'chrome' in command_lower:
                if platform.system().lower() == "windows":
                    steps.append(CommandStep(
                        name="open_chrome",
                        description="Open Chrome browser",
                        capability_name="terminal_command",
                        parameters={"command": 'start "" chrome'},
                        dependencies=[],
                        estimated_duration=3
                    ))
                else:
                    steps.append(CommandStep(
                        name="open_chrome",
                        description="Open Chrome browser",
                        capability_name="terminal_command",
                        parameters={"command": "google-chrome"},
                        dependencies=[],
                        estimated_duration=3
                    ))
            elif 'firefox' in command_lower:
                if platform.system().lower() == "windows":
                    steps.append(CommandStep(
                        name="open_firefox",
                        description="Open Firefox browser",
                        capability_name="terminal_command",
                        parameters={"command": 'start "" firefox'},
                        dependencies=[],
                        estimated_duration=3
                    ))
                else:
                    steps.append(CommandStep(
                        name="open_firefox",
                        description="Open Firefox browser",
                        capability_name="terminal_command",
                        parameters={"command": "firefox"},
                        dependencies=[],
                        estimated_duration=3
                    ))

        # System info commands
        elif any(word in command_lower for word in ['sistem', 'bilgi', 'info', 'göster']):
            steps.append(CommandStep(
                name="system_info",
                description="Show system information",
                capability_name="terminal_command",
                parameters={"command": "systeminfo"},
                dependencies=[],
                estimated_duration=5
            ))

        # File commands
        elif any(word in command_lower for word in ['dosya', 'file', 'listele', 'göster']):
            steps.append(CommandStep(
                name="list_files",
                description="List files in current directory",
                capability_name="terminal_command",
                parameters={"command": "dir"},
                dependencies=[],
                estimated_duration=3
            ))

        # Default fallback
        else:
            # Use Windows-compatible echo command
            if platform.system().lower() == "windows":
                echo_cmd = f"echo. Command: {command}"
            else:
                echo_cmd = f"echo 'Command: {command}'"
            
            steps.append(CommandStep(
                name="echo_command",
                description=f"Echo command: {command}",
                capability_name="terminal_command",
                parameters={"command": echo_cmd},
                dependencies=[],
                estimated_duration=2
            ))

        return ExecutionPlan(
            original_command=command,
            steps=steps,
            total_estimated_duration=sum(step.estimated_duration for step in steps),
            complexity="simple"
        )
    
    async def _execute_plan_sequential(
        self, 
        plan: ExecutionPlan, 
        original_command: str,
        client_id: Optional[str] = None
    ) -> IntelligentCommandResult:
        """Execute the execution plan sequentially"""
        try:
            # Create execution context
            context = ExecutionContext(
                original_command=original_command,
                plan=plan,
                client_id=client_id
            )
            
            # Set up progress callbacks
            if self.sequential_engine:
                self.sequential_engine.set_progress_callback(self._progress_callback)
                self.sequential_engine.set_step_callback(self._step_callback)
                
                # Execute using sequential engine
                result = await self.sequential_engine.execute_sequential_plan(plan, context)
                
                return IntelligentCommandResult(
                    success=result.success,
                    message=result.message,
                    execution_time=result.total_execution_time,
                    steps_executed=result.steps_completed,
                    total_steps=result.total_steps,
                    error=result.error,
                    metadata=result.metadata
                )
            else:
                # Fallback to orchestrator
                result = await self.orchestrator.execute_plan(plan, context)
                
                return IntelligentCommandResult(
                    success=result.success,
                    message=result.message,
                    execution_time=result.execution_time,
                    steps_executed=result.steps_executed,
                    total_steps=result.total_steps,
                    error=result.error,
                    metadata=result.metadata
                )
            
        except Exception as e:
            self.logger.error(f"Error executing plan sequentially: {e}")
            return IntelligentCommandResult(
                success=False,
                message=f"Error executing plan: {e}",
                execution_time=0.0,
                steps_executed=0,
                total_steps=len(plan.steps),
                error=str(e)
            )
    
    async def _execute_plan(
        self, 
        plan: ExecutionPlan, 
        original_command: str,
        client_id: Optional[str] = None
    ) -> IntelligentCommandResult:
        """Execute the execution plan (legacy method)"""
        try:
            # Create execution context
            context = ExecutionContext(
                original_command=original_command,
                plan=plan,
                client_id=client_id
            )
            
            # Execute using orchestrator
            result = await self.orchestrator.execute_plan(plan, context)
            
            return IntelligentCommandResult(
                success=result.success,
                message=result.message,
                execution_time=result.execution_time,
                steps_executed=result.steps_executed,
                total_steps=result.total_steps,
                error=result.error,
                metadata=result.metadata
            )
            
        except Exception as e:
            self.logger.error(f"Error executing plan: {e}")
            return IntelligentCommandResult(
                success=False,
                message=f"Error executing plan: {e}",
                execution_time=0.0,
                steps_executed=0,
                total_steps=len(plan.steps),
                error=str(e)
            )
    
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set progress update callback"""
        self._progress_callback = callback
    
    def set_step_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set step update callback"""
        self._step_callback = callback
    
    def _progress_callback(self, message: WebSocketMessage):
        """Enhanced progress callback with detailed logging"""
        try:
            self.logger.info(f"Progress Update: {message.data}")
            # Send progress update to connected clients
            if hasattr(self, '_progress_callback_handler'):
                self._progress_callback_handler(message)
        except Exception as e:
            self.logger.error(f"Error in progress callback: {e}")
    
    def _step_callback(self, message: WebSocketMessage):
        """Enhanced step callback with detailed logging"""
        try:
            step_data = message.data
            step_name = step_data.get('step_name', 'Unknown')
            step_status = step_data.get('step_status', 'Unknown')
            step_progress = step_data.get('step_progress', 0.0)
            
            self.logger.info(f"Step Update: {step_name} - {step_status} ({step_progress:.1f}%)")
            
            # Send step update to connected clients
            if hasattr(self, '_step_callback_handler'):
                self._step_callback_handler(message)
        except Exception as e:
            self.logger.error(f"Error in step callback: {e}")
    
    def set_progress_callback_handler(self, handler: Callable[[WebSocketMessage], None]):
        """Set custom progress callback handler"""
        self._progress_callback_handler = handler
    
    def set_step_callback_handler(self, handler: Callable[[WebSocketMessage], None]):
        """Set custom step callback handler"""
        self._step_callback_handler = handler
    
    def _create_error_message(self, error: Exception, command: str) -> str:
        """Create user-friendly error message"""
        error_type = type(error).__name__
        
        # Detect language
        is_turkish = any(char in command for char in 'çğıöşüÇĞIÖŞÜ')
        
        if is_turkish:
            error_messages = {
                'ConnectionError': 'Bağlantı hatası oluştu. Lütfen internet bağlantınızı kontrol edin.',
                'TimeoutError': 'İşlem zaman aşımına uğradı. Lütfen tekrar deneyin.',
                'ValueError': 'Geçersiz değer hatası. Lütfen komutu daha açık şekilde ifade edin.',
                'KeyError': 'Eksik parametre hatası. Lütfen gerekli bilgileri sağlayın.',
                'FileNotFoundError': 'Dosya bulunamadı. Lütfen dosya yolunu kontrol edin.',
                'PermissionError': 'İzin hatası. Lütfen gerekli izinleri kontrol edin.',
                'ImportError': 'Modül yükleme hatası. Sistem yapılandırmasını kontrol edin.'
            }
        else:
            error_messages = {
                'ConnectionError': 'Connection error occurred. Please check your internet connection.',
                'TimeoutError': 'Operation timed out. Please try again.',
                'ValueError': 'Invalid value error. Please express the command more clearly.',
                'KeyError': 'Missing parameter error. Please provide required information.',
                'FileNotFoundError': 'File not found. Please check the file path.',
                'PermissionError': 'Permission error. Please check required permissions.',
                'ImportError': 'Module loading error. Please check system configuration.'
            }
        
        base_message = error_messages.get(error_type, 
            'Bir hata oluştu. Lütfen tekrar deneyin.' if is_turkish 
            else 'An error occurred. Please try again.')
        
        return f"{base_message} (Hata: {str(error)})"
    
    def _get_recovery_suggestions(self, error: Exception, command: str) -> List[str]:
        """Get recovery suggestions based on error type and command"""
        suggestions = []
        error_type = type(error).__name__
        
        # Detect language
        is_turkish = any(char in command for char in 'çğıöşüÇĞIÖŞÜ')
        
        if error_type == 'ConnectionError':
            if is_turkish:
                suggestions = [
                    "İnternet bağlantınızı kontrol edin",
                    "Sunucu ayarlarını kontrol edin",
                    "Güvenlik duvarı ayarlarını kontrol edin"
                ]
            else:
                suggestions = [
                    "Check your internet connection",
                    "Verify server settings",
                    "Check firewall settings"
                ]
        elif error_type == 'TimeoutError':
            if is_turkish:
                suggestions = [
                    "Komutu daha basit hale getirin",
                    "Daha kısa süreli işlemler deneyin",
                    "Sistem kaynaklarını kontrol edin"
                ]
            else:
                suggestions = [
                    "Simplify the command",
                    "Try shorter operations",
                    "Check system resources"
                ]
        elif error_type == 'ValueError':
            if is_turkish:
                suggestions = [
                    "Komutu daha açık şekilde ifade edin",
                    "Eksik parametreleri belirtin",
                    "Örnek komut formatını kullanın"
                ]
            else:
                suggestions = [
                    "Express the command more clearly",
                    "Specify missing parameters",
                    "Use example command format"
                ]
        else:
            if is_turkish:
                suggestions = [
                    "Komutu yeniden formüle edin",
                    "Sistem durumunu kontrol edin",
                    "Yardım için 'yardım' yazın"
                ]
            else:
                suggestions = [
                    "Reformulate the command",
                    "Check system status",
                    "Type 'help' for assistance"
                ]
        
        return suggestions
    
    async def _create_execution_plan_from_decomposition(self, decomposition_result) -> Optional[ExecutionPlan]:
        """Create execution plan from decomposition result"""
        try:
            steps = []
            for decomposed_step in decomposition_result.decomposed_steps:
                command_step = CommandStep(
                    name=decomposed_step.step_id,
                    description=decomposed_step.description,
                    capability_name=decomposed_step.capability_name,
                    parameters=decomposed_step.parameters,
                    dependencies=decomposed_step.dependencies,
                    estimated_duration=decomposed_step.estimated_duration
                )
                steps.append(command_step)
            
            return ExecutionPlan(
                original_command=decomposition_result.original_command,
                steps=steps,
                total_estimated_duration=decomposition_result.total_estimated_duration,
                complexity=decomposition_result.strategy.value
            )
            
        except Exception as e:
            self.logger.error(f"Error creating execution plan from decomposition: {e}")
            return None
    
    async def _get_or_create_execution_context(
        self, 
        session_id: Optional[str], 
        client_id: Optional[str], 
        command: str, 
        context: Optional[Dict[str, Any]]
    ):
        """Get or create execution context with memory"""
        try:
            if not self.context_manager:
                return None
            
            # Use session_id or generate one
            if not session_id:
                session_id = f"session_{int(time.time())}_{client_id or 'anonymous'}"
            
            # Get existing context or create new one
            execution_context = await self.context_manager.get_execution_context(session_id)
            
            if not execution_context:
                execution_context = await self.context_manager.create_execution_context(
                    session_id=session_id,
                    user_id=context.get("user_id") if context else None,
                    command_sequence=[command]
                )
            else:
                # Update command sequence
                execution_context.command_sequence.append(command)
                await self.context_manager.update_execution_context(
                    session_id, 
                    {"command_sequence": execution_context.command_sequence}
                )
            
            # Store command in memory
            await self.context_manager.store_memory_entry(
                session_id=session_id,
                key=f"command_{len(execution_context.command_sequence)}",
                value=command,
                context_type=ContextType.EXECUTION_HISTORY,
                priority=ContextPriority.HIGH,
                tags=["command", "user_input"]
            )
            
            return execution_context
            
        except Exception as e:
            self.logger.error(f"Error getting/creating execution context: {e}")
            return None
    
    async def _generate_ai_context_with_memory(
        self, 
        command: str, 
        context: Optional[Dict[str, Any]], 
        execution_context
    ) -> Dict[str, Any]:
        """Generate AI context with memory and capabilities"""
        try:
            # Get base context
            base_context = await self._generate_ai_context(command, context)
            
            # Add memory context if available
            if execution_context and self.context_manager:
                memory_context = await self._get_memory_context(execution_context.session_id)
                base_context["memory"] = memory_context
                base_context["session_id"] = execution_context.session_id
                base_context["command_history"] = execution_context.command_sequence[-5:]  # Last 5 commands
                base_context["current_step"] = execution_context.current_step
                base_context["total_steps"] = execution_context.total_steps
            
            return base_context
            
        except Exception as e:
            self.logger.error(f"Error generating AI context with memory: {e}")
            return await self._generate_ai_context(command, context)
    
    async def _get_memory_context(self, session_id: str) -> Dict[str, Any]:
        """Get relevant memory context for AI"""
        try:
            if not self.context_manager:
                return {}
            
            # Get recent memory entries
            recent_entries = await self.context_manager.search_memory_entries(
                session_id=session_id,
                priority=ContextPriority.HIGH
            )
            
            # Get user preferences
            preferences = await self.context_manager.search_memory_entries(
                session_id=session_id,
                context_type=ContextType.USER_PREFERENCE
            )
            
            # Get system state
            system_state = await self.context_manager.search_memory_entries(
                session_id=session_id,
                context_type=ContextType.SYSTEM_STATE
            )
            
            memory_context = {
                "recent_commands": [entry.value for entry in recent_entries[:3]],
                "user_preferences": {entry.key: entry.value for entry in preferences},
                "system_state": {entry.key: entry.value for entry in system_state},
                "context_summary": await self.context_manager.get_context_summary(session_id)
            }
            
            return memory_context
            
        except Exception as e:
            self.logger.error(f"Error getting memory context: {e}")
            return {}
    
    async def _execute_plan_with_context(
        self, 
        plan, 
        original_command: str,
        client_id: Optional[str],
        execution_context
    ) -> IntelligentCommandResult:
        """Execute plan with context awareness"""
        try:
            if not execution_context or not self.context_manager:
                # Fallback to regular execution
                return await self._execute_plan_sequential(plan, original_command, client_id)
            
            # Update execution context
            await self.context_manager.update_execution_context(
                execution_context.session_id,
                {
                    "current_step": 0,
                    "total_steps": len(plan.steps)
                }
            )
            
            # Store execution plan in memory
            await self.context_manager.store_memory_entry(
                session_id=execution_context.session_id,
                key=f"execution_plan_{int(time.time())}",
                value={
                    "original_command": original_command,
                    "steps": [step.__dict__ for step in plan.steps],
                    "total_duration": plan.total_estimated_duration
                },
                context_type=ContextType.EXECUTION_HISTORY,
                priority=ContextPriority.MEDIUM,
                tags=["execution_plan", "command_sequence"]
            )
            
            # Execute with progress tracking
            result = await self._execute_plan_sequential(plan, original_command, client_id)
            
            # Store execution result in memory
            await self.context_manager.store_memory_entry(
                session_id=execution_context.session_id,
                key=f"execution_result_{int(time.time())}",
                value={
                    "success": result.success,
                    "message": result.message,
                    "execution_time": result.execution_time,
                    "steps_executed": result.steps_executed,
                    "error": result.error
                },
                context_type=ContextType.EXECUTION_HISTORY,
                priority=ContextPriority.MEDIUM,
                tags=["execution_result", "command_sequence"]
            )
            
            # Update context with final state
            await self.context_manager.update_execution_context(
                execution_context.session_id,
                {
                    "current_step": result.steps_executed,
                    "last_command": original_command,
                    "last_execution_time": time.time()
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing plan with context: {e}")
            # Fallback to regular execution
            return await self._execute_plan_sequential(plan, original_command, client_id)
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.sequential_engine:
                await self.sequential_engine.cleanup()
            await self.decomposition_engine.cleanup()
            if self.context_manager:
                await self.context_manager.cleanup()
            if self.learning_system:
                await self.learning_system.cleanup()
            await self.orchestrator.cleanup()
            await self.command_planner.cleanup()
            self._is_initialized = False
            self.logger.info("Intelligent command processor cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up intelligent command processor: {e}")
