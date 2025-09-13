"""
Command Planner

Plans and optimizes multi-step command execution by analyzing dependencies
and creating optimal execution order.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .capability_system import CapabilityManager, Capability

logger = logging.getLogger(__name__)

class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class CommandStep:
    """Individual command step"""
    name: str
    description: str
    capability_name: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    estimated_duration: int  # seconds
    status: StepStatus = StepStatus.PENDING
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "capability_name": self.capability_name,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration,
            "status": self.status.value,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time
        }

@dataclass
class ExecutionPlan:
    """Complete execution plan for a command"""
    original_command: str
    steps: List[CommandStep]
    total_estimated_duration: int
    complexity: str
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            import time
            self.created_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "original_command": self.original_command,
            "steps": [step.to_dict() for step in self.steps],
            "total_estimated_duration": self.total_estimated_duration,
            "complexity": self.complexity,
            "created_at": self.created_at
        }

class CommandPlanner:
    """Plans and optimizes command execution"""
    
    def __init__(self, capability_manager: CapabilityManager):
        self.capability_manager = capability_manager
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the command planner"""
        try:
            if not self.capability_manager.is_initialized():
                await self.capability_manager.initialize()
            
            self._is_initialized = True
            self.logger.info("Command planner initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize command planner: {e}")
            return False
    
    async def create_execution_plan(
        self, 
        command: str, 
        steps_data: List[Dict[str, Any]]
    ) -> Optional[ExecutionPlan]:
        """
        Create an execution plan from command steps
        
        Args:
            command: Original command
            steps_data: List of step data from AI
            
        Returns:
            ExecutionPlan or None if invalid
        """
        if not self._is_initialized:
            self.logger.error("Command planner not initialized")
            return None
        
        try:
            # Validate and create steps
            steps = []
            for step_data in steps_data:
                step = await self._create_step(step_data)
                if step:
                    steps.append(step)
                else:
                    self.logger.error(f"Failed to create step: {step_data}")
                    return None
            
            # Validate dependencies
            if not self._validate_dependencies(steps):
                self.logger.error("Invalid dependencies in execution plan")
                return None
            
            # Optimize execution order
            optimized_steps = await self._optimize_execution_order(steps)
            
            # Calculate total duration
            total_duration = sum(step.estimated_duration for step in optimized_steps)
            
            # Determine complexity
            complexity = self._determine_complexity(len(optimized_steps), total_duration)
            
            plan = ExecutionPlan(
                original_command=command,
                steps=optimized_steps,
                total_estimated_duration=total_duration,
                complexity=complexity
            )
            
            self.logger.info(f"Created execution plan with {len(optimized_steps)} steps")
            return plan
            
        except Exception as e:
            self.logger.error(f"Error creating execution plan: {e}")
            return None
    
    async def _create_step(self, step_data: Dict[str, Any]) -> Optional[CommandStep]:
        """Create a CommandStep from step data"""
        try:
            # Validate required fields
            required_fields = ["name", "description", "capability_name"]
            for field in required_fields:
                if field not in step_data:
                    self.logger.error(f"Missing required field: {field}")
                    return None
            
            # Validate capability exists
            capability = await self.capability_manager.get_capability(step_data["capability_name"])
            if not capability:
                self.logger.error(f"Capability not found: {step_data['capability_name']}")
                return None
            
            # Validate parameters
            if not self._validate_parameters(step_data.get("parameters", {}), capability):
                self.logger.error(f"Invalid parameters for capability: {step_data['capability_name']}")
                return None
            
            # Create step
            step = CommandStep(
                name=step_data["name"],
                description=step_data["description"],
                capability_name=step_data["capability_name"],
                parameters=step_data.get("parameters", {}),
                dependencies=step_data.get("dependencies", []),
                estimated_duration=step_data.get("estimated_duration", 5)
            )
            
            return step
            
        except Exception as e:
            self.logger.error(f"Error creating step: {e}")
            return None
    
    def _validate_parameters(self, parameters: Dict[str, Any], capability: Capability) -> bool:
        """Validate parameters against capability requirements"""
        try:
            # Get capability parameter requirements
            required_params = capability.required_parameters
            optional_params = capability.optional_parameters
            
            # Check required parameters
            for param_name in required_params:
                if param_name not in parameters:
                    self.logger.error(f"Missing required parameter: {param_name}")
                    return False
            
            # Check parameter types (basic validation)
            for param_name, param_value in parameters.items():
                if param_name in required_params or param_name in optional_params:
                    param_info = capability.get_parameter_info(param_name)
                    if param_info and not self._validate_parameter_type(param_value, param_info.get("type")):
                        self.logger.error(f"Invalid parameter type for {param_name}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating parameters: {e}")
            return False
    
    def _validate_parameter_type(self, value: Any, expected_type: str) -> bool:
        """Validate parameter type"""
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "float":
            return isinstance(value, (int, float))
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "list":
            return isinstance(value, list)
        elif expected_type == "dict":
            return isinstance(value, dict)
        else:
            return True  # Unknown type, assume valid
    
    def _validate_dependencies(self, steps: List[CommandStep]) -> bool:
        """Validate step dependencies"""
        try:
            step_names = {step.name for step in steps}
            
            for step in steps:
                for dependency in step.dependencies:
                    if dependency not in step_names:
                        self.logger.error(f"Invalid dependency: {dependency} not found in steps")
                        return False
            
            # Check for circular dependencies
            if self._has_circular_dependencies(steps):
                self.logger.error("Circular dependencies detected")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating dependencies: {e}")
            return False
    
    def _has_circular_dependencies(self, steps: List[CommandStep]) -> bool:
        """Check for circular dependencies using DFS"""
        try:
            step_map = {step.name: step for step in steps}
            visited = set()
            rec_stack = set()
            
            def has_cycle(step_name: str) -> bool:
                if step_name in rec_stack:
                    return True
                if step_name in visited:
                    return False
                
                visited.add(step_name)
                rec_stack.add(step_name)
                
                step = step_map.get(step_name)
                if step:
                    for dep in step.dependencies:
                        if has_cycle(dep):
                            return True
                
                rec_stack.remove(step_name)
                return False
            
            for step in steps:
                if step.name not in visited:
                    if has_cycle(step.name):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking circular dependencies: {e}")
            return True  # Assume circular if error
    
    async def _optimize_execution_order(self, steps: List[CommandStep]) -> List[CommandStep]:
        """Optimize execution order using topological sort"""
        try:
            # Create dependency graph
            step_map = {step.name: step for step in steps}
            in_degree = {step.name: 0 for step in steps}
            graph = {step.name: [] for step in steps}
            
            for step in steps:
                for dep in step.dependencies:
                    graph[dep].append(step.name)
                    in_degree[step.name] += 1
            
            # Topological sort
            queue = [step_name for step_name, degree in in_degree.items() if degree == 0]
            result = []
            
            while queue:
                # Sort by estimated duration for better parallelization
                queue.sort(key=lambda x: step_map[x].estimated_duration)
                
                current = queue.pop(0)
                result.append(step_map[current])
                
                for neighbor in graph[current]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            if len(result) != len(steps):
                self.logger.warning("Some steps could not be ordered (circular dependencies)")
                # Add remaining steps
                remaining = [step for step in steps if step not in result]
                result.extend(remaining)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error optimizing execution order: {e}")
            return steps  # Return original order if optimization fails
    
    def _determine_complexity(self, step_count: int, total_duration: int) -> str:
        """Determine plan complexity"""
        if step_count <= 1:
            return "simple"
        elif step_count <= 3 and total_duration <= 30:
            return "moderate"
        else:
            return "complex"
    
    async def get_ready_steps(self, steps: List[CommandStep]) -> List[CommandStep]:
        """Get steps that are ready to execute"""
        ready_steps = []
        
        for step in steps:
            if step.status != StepStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            dependencies_completed = True
            for dep_name in step.dependencies:
                dep_step = next((s for s in steps if s.name == dep_name), None)
                if not dep_step or dep_step.status != StepStatus.COMPLETED:
                    dependencies_completed = False
                    break
            
            if dependencies_completed:
                step.status = StepStatus.READY
                ready_steps.append(step)
        
        return ready_steps
    
    async def update_step_status(
        self, 
        steps: List[CommandStep], 
        step_name: str, 
        status: StepStatus,
        error: Optional[str] = None
    ) -> bool:
        """Update step status"""
        try:
            step = next((s for s in steps if s.name == step_name), None)
            if not step:
                self.logger.error(f"Step not found: {step_name}")
                return False
            
            step.status = status
            if error:
                step.error = error
            
            if status == StepStatus.RUNNING:
                import time
                step.start_time = time.time()
            elif status in [StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED]:
                import time
                step.end_time = time.time()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating step status: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            self._is_initialized = False
            self.logger.info("Command planner cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up command planner: {e}")
