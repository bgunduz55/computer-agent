"""
Intelligent Command Decomposition Engine

AI-powered command decomposition that breaks complex user requests
into sequential, executable steps with dependency management.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..ai_integration import AIProviderManager, AIRequest, AIResponse, AIProviderType
from .command_planner import CommandStep, ExecutionPlan
from .capability_system import CapabilityManager, CapabilityType

logger = logging.getLogger(__name__)

class DecompositionStrategy(Enum):
    """Command decomposition strategies"""
    SEQUENTIAL = "sequential"      # Steps must be executed in order
    PARALLEL = "parallel"          # Steps can be executed simultaneously
    CONDITIONAL = "conditional"    # Steps depend on conditions
    ITERATIVE = "iterative"        # Steps repeat based on conditions

class StepDependency(Enum):
    """Step dependency types"""
    REQUIRES = "requires"          # Step requires another step to complete
    BLOCKS = "blocks"              # Step blocks another step
    OPTIONAL = "optional"          # Step is optional for completion
    ALTERNATIVE = "alternative"    # Step is alternative to another

@dataclass
class DecomposedStep:
    """A decomposed command step with enhanced metadata"""
    step_id: str
    description: str
    capability_name: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    dependency_type: StepDependency
    estimated_duration: float
    priority: int
    can_parallelize: bool
    retry_count: int = 0
    max_retries: int = 3
    success_criteria: Optional[Dict[str, Any]] = None
    rollback_action: Optional[str] = None

@dataclass
class DecompositionResult:
    """Result of command decomposition"""
    success: bool
    original_command: str
    decomposed_steps: List[DecomposedStep]
    strategy: DecompositionStrategy
    total_estimated_duration: float
    complexity_score: float
    confidence_score: float
    error: Optional[str] = None
    suggestions: List[str] = None

class IntelligentCommandDecompositionEngine:
    """AI-powered command decomposition engine"""
    
    def __init__(self, ai_manager: AIProviderManager, capability_manager: CapabilityManager):
        self.ai_manager = ai_manager
        self.capability_manager = capability_manager
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        
        # Decomposition patterns and rules
        self.decomposition_patterns = self._load_decomposition_patterns()
        self.capability_mappings = self._load_capability_mappings()
    
    async def initialize(self) -> bool:
        """Initialize the decomposition engine"""
        try:
            if not self.capability_manager.is_initialized():
                await self.capability_manager.initialize()
            
            self._is_initialized = True
            self.logger.info("Intelligent command decomposition engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize decomposition engine: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized"""
        return self._is_initialized
    
    async def decompose_command(
        self, 
        command: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> DecompositionResult:
        """Decompose a complex command into executable steps"""
        try:
            if not self._is_initialized:
                return DecompositionResult(
                    success=False,
                    original_command=command,
                    decomposed_steps=[],
                    strategy=DecompositionStrategy.SEQUENTIAL,
                    total_estimated_duration=0.0,
                    complexity_score=0.0,
                    confidence_score=0.0,
                    error="Decomposition engine not initialized"
                )
            
            self.logger.info(f"Decomposing command: {command}")
            
            # Step 1: Analyze command complexity and intent
            analysis = await self._analyze_command_intent(command, context)
            
            # Step 2: Generate AI-powered decomposition
            ai_decomposition = await self._generate_ai_decomposition(command, analysis, context)
            
            # Step 3: Validate and refine decomposition
            refined_decomposition = await self._validate_and_refine_decomposition(
                command, ai_decomposition, analysis
            )
            
            # Step 4: Create execution plan
            execution_plan = await self._create_execution_plan(refined_decomposition, analysis)
            
            return DecompositionResult(
                success=True,
                original_command=command,
                decomposed_steps=execution_plan.steps,
                strategy=execution_plan.strategy,
                total_estimated_duration=execution_plan.total_estimated_duration,
                complexity_score=analysis.complexity_score,
                confidence_score=analysis.confidence_score,
                suggestions=analysis.suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error decomposing command: {e}")
            return DecompositionResult(
                success=False,
                original_command=command,
                decomposed_steps=[],
                strategy=DecompositionStrategy.SEQUENTIAL,
                total_estimated_duration=0.0,
                complexity_score=0.0,
                confidence_score=0.0,
                error=str(e)
            )
    
    async def _analyze_command_intent(
        self, 
        command: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze command intent and complexity"""
        try:
            # Detect language
            is_turkish = any(char in command for char in 'çğıöşüÇĞIÖŞÜ')
            language = "Turkish" if is_turkish else "English"
            
            # Analyze complexity indicators
            complexity_indicators = self._analyze_complexity_indicators(command)
            
            # Detect intent patterns
            intent_patterns = self._detect_intent_patterns(command, language)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(command, complexity_indicators)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(command, complexity_indicators, language)
            
            return {
                "language": language,
                "complexity_indicators": complexity_indicators,
                "intent_patterns": intent_patterns,
                "complexity_score": complexity_score,
                "confidence_score": 0.8,  # Will be refined by AI
                "suggestions": suggestions,
                "context": context or {}
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing command intent: {e}")
            return {
                "language": "English",
                "complexity_indicators": [],
                "intent_patterns": [],
                "complexity_score": 0.5,
                "confidence_score": 0.5,
                "suggestions": [],
                "context": context or {}
            }
    
    def _analyze_complexity_indicators(self, command: str) -> List[str]:
        """Analyze command for complexity indicators"""
        indicators = []
        command_lower = command.lower()
        
        # Sequential indicators
        sequential_words = [
            'then', 'after', 'next', 'also', 'and', 'while', 'during',
            'sonra', 'ardından', 'sonraki', 'ayrıca', 've', 'iken', 'sırasında'
        ]
        
        if any(word in command_lower for word in sequential_words):
            indicators.append("sequential")
        
        # Conditional indicators
        conditional_words = [
            'if', 'when', 'unless', 'provided', 'eğer', 'ne zaman', 'sadece'
        ]
        
        if any(word in command_lower for word in conditional_words):
            indicators.append("conditional")
        
        # Multi-object indicators
        multi_object_words = [
            'both', 'multiple', 'several', 'her ikisi', 'birden fazla', 'birkaç'
        ]
        
        if any(word in command_lower for word in multi_object_words):
            indicators.append("multi_object")
        
        # File operations
        file_words = [
            'file', 'dosya', 'document', 'belge', 'folder', 'klasör'
        ]
        
        if any(word in command_lower for word in file_words):
            indicators.append("file_operations")
        
        # Web operations
        web_words = [
            'website', 'web sitesi', 'browser', 'tarayıcı', 'search', 'ara'
        ]
        
        if any(word in command_lower for word in web_words):
            indicators.append("web_operations")
        
        return indicators
    
    def _detect_intent_patterns(self, command: str, language: str) -> List[str]:
        """Detect intent patterns in command"""
        patterns = []
        command_lower = command.lower()
        
        # YouTube patterns
        youtube_patterns = [
            'youtube', 'müzik', 'müziği', 'şarkı', 'video', 'oynat', 'play'
        ]
        
        if any(pattern in command_lower for pattern in youtube_patterns):
            patterns.append("youtube_operation")
        
        # WhatsApp patterns
        whatsapp_patterns = [
            'whatsapp', 'mesaj', 'gönder', 'send', 'message'
        ]
        
        if any(pattern in command_lower for pattern in whatsapp_patterns):
            patterns.append("whatsapp_operation")
        
        # File creation patterns
        file_creation_patterns = [
            'create', 'oluştur', 'make', 'yap', 'new', 'yeni'
        ]
        
        if any(pattern in command_lower for pattern in file_creation_patterns):
            patterns.append("file_creation")
        
        # Search patterns
        search_patterns = [
            'search', 'ara', 'find', 'bul', 'look', 'bak'
        ]
        
        if any(pattern in command_lower for pattern in search_patterns):
            patterns.append("search_operation")
        
        return patterns
    
    def _calculate_complexity_score(self, command: str, indicators: List[str]) -> float:
        """Calculate command complexity score"""
        base_score = 0.1
        
        # Word count factor
        word_count = len(command.split())
        if word_count > 15:
            base_score += 0.3
        elif word_count > 10:
            base_score += 0.2
        elif word_count > 5:
            base_score += 0.1
        
        # Indicator factors
        indicator_weights = {
            "sequential": 0.2,
            "conditional": 0.3,
            "multi_object": 0.2,
            "file_operations": 0.15,
            "web_operations": 0.15
        }
        
        for indicator in indicators:
            base_score += indicator_weights.get(indicator, 0.1)
        
        return min(base_score, 1.0)
    
    def _generate_suggestions(self, command: str, indicators: List[str], language: str) -> List[str]:
        """Generate suggestions for command improvement"""
        suggestions = []
        
        if "sequential" in indicators:
            if language == "Turkish":
                suggestions.append("Komutunuzu daha basit adımlara bölebilirsiniz")
            else:
                suggestions.append("You can break your command into simpler steps")
        
        if "conditional" in indicators:
            if language == "Turkish":
                suggestions.append("Koşullu işlemler için daha açık ifadeler kullanın")
            else:
                suggestions.append("Use clearer expressions for conditional operations")
        
        if len(command.split()) > 20:
            if language == "Turkish":
                suggestions.append("Komutunuzu daha kısa cümleler halinde ifade edin")
            else:
                suggestions.append("Express your command in shorter sentences")
        
        return suggestions
    
    async def _generate_ai_decomposition(
        self, 
        command: str, 
        analysis: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate AI-powered command decomposition"""
        try:
            # Get available capabilities
            capabilities = await self.capability_manager.get_all_capabilities()
            capability_info = [cap.to_dict() for cap in capabilities]
            
            # Create AI prompt for decomposition
            prompt = self._create_decomposition_prompt(command, analysis, capability_info, context)
            
            # Generate AI response
            response = await self.ai_manager.generate_response(prompt)
            
            # Parse AI response
            decomposition = self._parse_ai_decomposition_response(response.content, command)
            
            return decomposition
            
        except Exception as e:
            self.logger.error(f"Error generating AI decomposition: {e}")
            return {"steps": [], "strategy": "sequential", "error": str(e)}
    
    def _create_decomposition_prompt(
        self, 
        command: str, 
        analysis: Dict[str, Any], 
        capabilities: List[Dict[str, Any]], 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Create AI prompt for command decomposition"""
        language = analysis.get("language", "English")
        complexity_score = analysis.get("complexity_score", 0.5)
        intent_patterns = analysis.get("intent_patterns", [])
        
        # Filter relevant capabilities
        relevant_capabilities = self._filter_relevant_capabilities(capabilities, intent_patterns)
        
        prompt = f"""You are an expert command decomposition AI. Decompose this {language} command into executable steps:

COMMAND: "{command}"

ANALYSIS:
- Language: {language}
- Complexity Score: {complexity_score}
- Intent Patterns: {', '.join(intent_patterns)}
- Context: {context or 'None'}

AVAILABLE CAPABILITIES:
{self._format_capabilities_for_prompt(relevant_capabilities)}

DECOMPOSITION RULES:
1. Break complex commands into logical, sequential steps
2. Each step should use exactly one capability
3. Consider dependencies between steps
4. Provide realistic duration estimates
5. Include error handling and rollback actions
6. Mark steps that can run in parallel
7. Use clear, descriptive step names

OUTPUT FORMAT (JSON only):
{{
    "strategy": "sequential|parallel|conditional|iterative",
    "steps": [
        {{
            "step_id": "step_1",
            "description": "Clear description of what this step does",
            "capability_name": "exact_capability_name",
            "parameters": {{"param": "value"}},
            "dependencies": [],
            "dependency_type": "requires|blocks|optional|alternative",
            "estimated_duration": 5.0,
            "priority": 1,
            "can_parallelize": false,
            "max_retries": 3,
            "success_criteria": {{"type": "element_present", "selector": "selector"}},
            "rollback_action": "action_to_undo_this_step"
        }}
    ],
    "total_estimated_duration": 15.0,
    "confidence_score": 0.9
}}"""
        
        return prompt
    
    def _filter_relevant_capabilities(
        self, 
        capabilities: List[Dict[str, Any]], 
        intent_patterns: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter capabilities relevant to intent patterns"""
        relevant = []
        
        for cap in capabilities:
            cap_name = cap.get("name", "").lower()
            cap_type = cap.get("capability_type", "").lower()
            
            # Check if capability matches intent patterns
            if "youtube_operation" in intent_patterns and "youtube" in cap_name:
                relevant.append(cap)
            elif "whatsapp_operation" in intent_patterns and "whatsapp" in cap_name:
                relevant.append(cap)
            elif "file_creation" in intent_patterns and "file" in cap_name:
                relevant.append(cap)
            elif "search_operation" in intent_patterns and ("web" in cap_name or "search" in cap_name):
                relevant.append(cap)
            elif cap_type in ["system", "productivity", "application"]:
                relevant.append(cap)
        
        return relevant[:20]  # Limit to first 20 relevant capabilities
    
    def _format_capabilities_for_prompt(self, capabilities: List[Dict[str, Any]]) -> str:
        """Format capabilities for AI prompt"""
        if not capabilities:
            return "No relevant capabilities found"
        
        formatted = []
        for cap in capabilities:
            name = cap.get("name", "Unknown")
            description = cap.get("description", "No description")
            cap_type = cap.get("capability_type", "unknown")
            
            formatted.append(f"- {name} ({cap_type}): {description}")
            
            # Add parameter info
            param_info = cap.get("parameter_info", {})
            if param_info:
                params = []
                for param_name, param_data in param_info.items():
                    param_type = param_data.get("type", "string")
                    required = param_data.get("required", False)
                    req_text = "required" if required else "optional"
                    params.append(f"{param_name} ({param_type}, {req_text})")
                
                if params:
                    formatted.append(f"  Parameters: {', '.join(params)}")
        
        return "\n".join(formatted)
    
    def _parse_ai_decomposition_response(self, response: str, original_command: str) -> Dict[str, Any]:
        """Parse AI decomposition response"""
        try:
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in AI response")
            
            decomposition_data = json.loads(json_match.group())
            
            # Validate and clean the data
            steps = []
            for step_data in decomposition_data.get("steps", []):
                step = DecomposedStep(
                    step_id=step_data.get("step_id", ""),
                    description=step_data.get("description", ""),
                    capability_name=step_data.get("capability_name", ""),
                    parameters=step_data.get("parameters", {}),
                    dependencies=step_data.get("dependencies", []),
                    dependency_type=StepDependency(step_data.get("dependency_type", "requires")),
                    estimated_duration=float(step_data.get("estimated_duration", 5.0)),
                    priority=int(step_data.get("priority", 1)),
                    can_parallelize=bool(step_data.get("can_parallelize", False)),
                    max_retries=int(step_data.get("max_retries", 3)),
                    success_criteria=step_data.get("success_criteria"),
                    rollback_action=step_data.get("rollback_action")
                )
                steps.append(step)
            
            return {
                "steps": steps,
                "strategy": DecompositionStrategy(decomposition_data.get("strategy", "sequential")),
                "total_estimated_duration": float(decomposition_data.get("total_estimated_duration", 0.0)),
                "confidence_score": float(decomposition_data.get("confidence_score", 0.8))
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing AI decomposition response: {e}")
            return {
                "steps": [],
                "strategy": DecompositionStrategy.SEQUENTIAL,
                "total_estimated_duration": 0.0,
                "confidence_score": 0.5,
                "error": str(e)
            }
    
    async def _validate_and_refine_decomposition(
        self, 
        command: str, 
        decomposition: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and refine the decomposition"""
        try:
            steps = decomposition.get("steps", [])
            validated_steps = []
            
            for step in steps:
                # Validate capability exists
                capability = await self.capability_manager.get_capability(step.capability_name)
                if not capability:
                    self.logger.warning(f"Capability not found: {step.capability_name}")
                    continue
                
                # Validate parameters
                validated_params = self._validate_step_parameters(step, capability)
                step.parameters = validated_params
                
                # Add validation metadata
                step.success_criteria = step.success_criteria or self._generate_success_criteria(step)
                step.rollback_action = step.rollback_action or self._generate_rollback_action(step)
                
                validated_steps.append(step)
            
            return {
                "steps": validated_steps,
                "strategy": decomposition.get("strategy", DecompositionStrategy.SEQUENTIAL),
                "total_estimated_duration": sum(step.estimated_duration for step in validated_steps),
                "confidence_score": decomposition.get("confidence_score", 0.8)
            }
            
        except Exception as e:
            self.logger.error(f"Error validating decomposition: {e}")
            return decomposition
    
    def _validate_step_parameters(self, step: DecomposedStep, capability: Any) -> Dict[str, Any]:
        """Validate step parameters against capability requirements"""
        validated_params = {}
        param_info = capability.parameter_info
        
        for param_name, param_value in step.parameters.items():
            if param_name in param_info:
                param_spec = param_info[param_name]
                
                # Type validation
                if param_spec.type == "integer" and isinstance(param_value, str):
                    try:
                        validated_params[param_name] = int(param_value)
                    except ValueError:
                        validated_params[param_name] = param_spec.default_value
                elif param_spec.type == "float" and isinstance(param_value, str):
                    try:
                        validated_params[param_name] = float(param_value)
                    except ValueError:
                        validated_params[param_name] = param_spec.default_value
                else:
                    validated_params[param_name] = param_value
            else:
                validated_params[param_name] = param_value
        
        return validated_params
    
    def _generate_success_criteria(self, step: DecomposedStep) -> Dict[str, Any]:
        """Generate success criteria for a step"""
        if "youtube" in step.capability_name.lower():
            return {"type": "element_present", "selector": "video"}
        elif "whatsapp" in step.capability_name.lower():
            return {"type": "element_present", "selector": "div[data-testid='conversation-panel-messages']"}
        elif "web" in step.capability_name.lower():
            return {"type": "page_loaded", "timeout": 5}
        else:
            return {"type": "execution_complete", "timeout": step.estimated_duration}
    
    def _generate_rollback_action(self, step: DecomposedStep) -> str:
        """Generate rollback action for a step"""
        if "create" in step.description.lower():
            return "delete_created_item"
        elif "open" in step.description.lower():
            return "close_opened_item"
        elif "send" in step.description.lower():
            return "undo_sent_item"
        else:
            return "revert_changes"
    
    async def _create_execution_plan(
        self, 
        decomposition: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> ExecutionPlan:
        """Create execution plan from decomposition"""
        try:
            steps = decomposition.get("steps", [])
            strategy = decomposition.get("strategy", DecompositionStrategy.SEQUENTIAL)
            total_duration = decomposition.get("total_estimated_duration", 0.0)
            
            # Convert DecomposedStep to CommandStep
            command_steps = []
            for step in steps:
                command_step = CommandStep(
                    name=step.step_id,
                    description=step.description,
                    capability_name=step.capability_name,
                    parameters=step.parameters,
                    dependencies=step.dependencies,
                    estimated_duration=step.estimated_duration
                )
                command_steps.append(command_step)
            
            return ExecutionPlan(
                original_command=analysis.get("original_command", ""),
                steps=command_steps,
                total_estimated_duration=total_duration,
                complexity=strategy.value
            )
            
        except Exception as e:
            self.logger.error(f"Error creating execution plan: {e}")
            return ExecutionPlan(
                original_command="",
                steps=[],
                total_estimated_duration=0.0,
                complexity="simple"
            )
    
    def _load_decomposition_patterns(self) -> Dict[str, Any]:
        """Load decomposition patterns and rules"""
        return {
            "youtube_patterns": [
                "search.*play", "find.*video", "youtube.*music"
            ],
            "whatsapp_patterns": [
                "send.*message", "whatsapp.*group", "message.*contact"
            ],
            "file_patterns": [
                "create.*file", "write.*document", "save.*text"
            ],
            "web_patterns": [
                "open.*website", "search.*google", "browser.*navigate"
            ]
        }
    
    def _load_capability_mappings(self) -> Dict[str, List[str]]:
        """Load capability mappings for different intents"""
        return {
            "youtube_operation": ["youtube_automation", "web_automation"],
            "whatsapp_operation": ["whatsapp_automation"],
            "file_creation": ["file_create", "text_input"],
            "search_operation": ["web_search", "youtube_automation"],
            "system_control": ["system_shutdown", "volume_control", "brightness_control"]
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            self._is_initialized = False
            self.logger.info("Command decomposition engine cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

