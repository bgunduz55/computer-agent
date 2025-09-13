"""
Intelligent Command Processor

AI-powered command processing system that understands complex, multi-step commands
and executes them using the assistant's capabilities.
"""

import asyncio
import logging
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
        client_id: Optional[str] = None
    ) -> IntelligentCommandResult:
        """
        Process an intelligent command using AI
        
        Args:
            command: The voice command to process
            context: Additional context information
            client_id: Client ID for progress updates
            
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
            
            # Step 1: Analyze command complexity
            complexity = await self._analyze_command_complexity(command)
            self.logger.info(f"Command complexity: {complexity.value}")
            
            # Step 2: Generate AI context with capabilities
            ai_context = await self._generate_ai_context(command, context)
            
            # Step 3: Process command with AI
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
            
            # Step 4: Parse AI response into execution plan
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
            
            # Step 5: Execute the plan sequentially
            execution_result = await self._execute_plan_sequential(
                execution_plan, 
                command, 
                client_id
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
            return IntelligentCommandResult(
                success=False,
                message=f"Error processing command: {e}",
                execution_time=time.time() - start_time,
                steps_executed=0,
                total_steps=0,
                error=str(e)
            )
    
    async def _analyze_command_complexity(self, command: str) -> CommandComplexity:
        """Analyze the complexity of the command"""
        # Simple heuristic based on command length and keywords
        complex_keywords = [
            'then', 'after', 'next', 'also', 'and', 'while', 'during',
            'sonra', 'ardından', 'sonraki', 'ayrıca', 've', 'iken', 'sırasında'
        ]
        
        multi_step_indicators = [
            'open', 'create', 'write', 'save', 'close', 'send', 'search', 'play',
            'aç', 'oluştur', 'yaz', 'kaydet', 'kapat', 'gönder', 'ara', 'oynat'
        ]
        
        command_lower = command.lower()
        
        # Count complex keywords
        complex_count = sum(1 for keyword in complex_keywords if keyword in command_lower)
        
        # Count multi-step indicators
        step_count = sum(1 for indicator in multi_step_indicators if indicator in command_lower)
        
        if complex_count >= 2 or step_count >= 4:
            return CommandComplexity.COMPLEX
        elif complex_count >= 1 or step_count >= 2:
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
        """Create AI prompt for command processing"""
        capabilities = context.get("capabilities", [])
        system_state = context.get("system_state", {})
        available_commands = context.get("available_commands", [])
        
        # Detect language
        is_turkish = any(char in command for char in 'çğıöşüÇĞIÖŞÜ')
        language = "Turkish" if is_turkish else "English"
        
        prompt = f"""
You are JARVIS, an intelligent computer assistant. The user command is in {language}:

"{command}"

Available capabilities:
{self._format_capabilities(capabilities)}

System: {system_state.get('platform', 'unknown')}

IMPORTANT: You must respond with ONLY valid JSON. No thinking, no explanations, no <think> tags.

For YouTube commands, use "web_open_url" with YouTube search URL.
For browser commands, use "web_open_url" with the URL.
For complex tasks, break them into steps.

Return this EXACT JSON format:
{{
    "analysis": {{
        "intent": "What user wants to accomplish",
        "complexity": "simple|moderate|complex"
    }},
    "execution_plan": {{
        "steps": [
            {{
                "step_id": "step_1",
                "description": "What this step does",
                "capability": "capability_name",
                "parameters": {{"param": "value"}}
            }}
        ],
        "total_steps": 1,
        "estimated_duration": 10
    }}
}}

CRITICAL: Return ONLY valid JSON. No other text, no thinking, no explanations.
"""
        return prompt
    
    def _format_capabilities(self, capabilities: List[Dict[str, Any]]) -> str:
        """Format capabilities for AI prompt"""
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
        
        # Method 1: Direct JSON
        if response_text.startswith('{') and response_text.endswith('}'):
            try:
                json.loads(response_text)
                return response_text
            except:
                pass
        
        # Method 2: Find JSON block
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            json_text = response_text[start:end]
            try:
                json.loads(json_text)
                return json_text
            except:
                pass
        
        # Method 3: Find JSON array
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end > start:
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
        # Simple command mapping for common operations
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['list', 'show', 'ls', 'dir']):
            terminal_command = "ls -la"
        elif any(word in command_lower for word in ['find', 'search', 'grep']):
            terminal_command = f"find . -name '*{command.split()[-1]}*' 2>/dev/null"
        elif any(word in command_lower for word in ['process', 'ps', 'task']):
            terminal_command = "ps aux"
        elif any(word in command_lower for word in ['memory', 'ram', 'free']):
            terminal_command = "free -h"
        elif any(word in command_lower for word in ['disk', 'space', 'df']):
            terminal_command = "df -h"
        elif any(word in command_lower for word in ['network', 'net', 'ip']):
            terminal_command = "ip addr show"
        elif any(word in command_lower for word in ['date', 'time']):
            terminal_command = "date"
        elif any(word in command_lower for word in ['uptime', 'up']):
            terminal_command = "uptime"
        else:
            # Generic terminal command
            terminal_command = command
        
        step = CommandStep(
            name="terminal_execution",
            description=f"Execute terminal command: {terminal_command}",
            capability_name="terminal_command",
            parameters={"command": terminal_command},
            dependencies=[],
            estimated_duration=5
        )
        
        return ExecutionPlan(
            original_command=command,
            steps=[step],
            total_estimated_duration=10,
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
        """Default progress callback"""
        pass
    
    def _step_callback(self, message: WebSocketMessage):
        """Default step callback"""
        pass
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.sequential_engine:
                await self.sequential_engine.cleanup()
            await self.orchestrator.cleanup()
            await self.command_planner.cleanup()
            self._is_initialized = False
            self.logger.info("Intelligent command processor cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up intelligent command processor: {e}")
