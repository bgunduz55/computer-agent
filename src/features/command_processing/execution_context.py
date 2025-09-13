"""
Execution Context

Manages the execution context for multi-step commands including
variable storage, step dependencies, and error handling.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from .command_planner import ExecutionPlan, CommandStep, StepStatus

logger = logging.getLogger(__name__)

class ExecutionState(Enum):
    """Execution state"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ExecutionResult:
    """Result of step execution"""
    step_name: str
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ExecutionContext:
    """Context for command execution"""
    original_command: str
    plan: ExecutionPlan
    client_id: Optional[str] = None
    state: ExecutionState = ExecutionState.PENDING
    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, ExecutionResult] = field(default_factory=dict)
    current_step: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "original_command": self.original_command,
            "plan": self.plan.to_dict(),
            "client_id": self.client_id,
            "state": self.state.value,
            "variables": self.variables,
            "results": {
                name: {
                    "step_name": result.step_name,
                    "success": result.success,
                    "output": result.output,
                    "error": result.error,
                    "execution_time": result.execution_time,
                    "metadata": result.metadata
                }
                for name, result in self.results.items()
            },
            "current_step": self.current_step,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error": self.error,
            "metadata": self.metadata
        }
    
    def set_variable(self, name: str, value: Any):
        """Set a variable in the context"""
        self.variables[name] = value
        logger.debug(f"Set variable {name} = {value}")
    
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a variable from the context"""
        return self.variables.get(name, default)
    
    def has_variable(self, name: str) -> bool:
        """Check if variable exists"""
        return name in self.variables
    
    def set_result(self, step_name: str, result: ExecutionResult):
        """Set execution result for a step"""
        self.results[step_name] = result
        logger.debug(f"Set result for step {step_name}: success={result.success}")
    
    def get_result(self, step_name: str) -> Optional[ExecutionResult]:
        """Get execution result for a step"""
        return self.results.get(step_name)
    
    def get_completed_steps(self) -> List[str]:
        """Get list of completed step names"""
        return [
            name for name, result in self.results.items()
            if result.success
        ]
    
    def get_failed_steps(self) -> List[str]:
        """Get list of failed step names"""
        return [
            name for name, result in self.results.items()
            if not result.success
        ]
    
    def is_step_completed(self, step_name: str) -> bool:
        """Check if step is completed"""
        result = self.get_result(step_name)
        return result is not None and result.success
    
    def is_step_failed(self, step_name: str) -> bool:
        """Check if step failed"""
        result = self.get_result(step_name)
        return result is not None and not result.success
    
    def get_step_dependencies_met(self, step: CommandStep) -> bool:
        """Check if all dependencies for a step are met"""
        for dep_name in step.dependencies:
            if not self.is_step_completed(dep_name):
                return False
        return True
    
    def get_ready_steps(self) -> List[CommandStep]:
        """Get steps that are ready to execute"""
        ready_steps = []
        
        for step in self.plan.steps:
            if step.status == StepStatus.PENDING and self.get_step_dependencies_met(step):
                ready_steps.append(step)
        
        return ready_steps
    
    def get_execution_progress(self) -> Dict[str, Any]:
        """Get execution progress information"""
        total_steps = len(self.plan.steps)
        completed_steps = len(self.get_completed_steps())
        failed_steps = len(self.get_failed_steps())
        
        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "progress_percentage": progress_percentage,
            "current_step": self.current_step,
            "state": self.state.value,
            "execution_time": time.time() - self.start_time if self.start_time else 0
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary"""
        return {
            "original_command": self.original_command,
            "state": self.state.value,
            "total_steps": len(self.plan.steps),
            "completed_steps": len(self.get_completed_steps()),
            "failed_steps": len(self.get_failed_steps()),
            "execution_time": (self.end_time - self.start_time) if self.end_time and self.start_time else 0,
            "error": self.error,
            "results": {
                name: {
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "error": result.error
                }
                for name, result in self.results.items()
            }
        }
    
    def mark_step_running(self, step_name: str):
        """Mark a step as running"""
        self.current_step = step_name
        self.state = ExecutionState.RUNNING
        
        # Update step status in plan
        for step in self.plan.steps:
            if step.name == step_name:
                step.status = StepStatus.RUNNING
                step.start_time = time.time()
                break
        
        logger.info(f"Marked step as running: {step_name}")
    
    def mark_step_completed(self, step_name: str, result: ExecutionResult):
        """Mark a step as completed"""
        self.set_result(step_name, result)
        
        # Update step status in plan
        for step in self.plan.steps:
            if step.name == step_name:
                step.status = StepStatus.COMPLETED
                step.end_time = time.time()
                break
        
        logger.info(f"Marked step as completed: {step_name}")
    
    def mark_step_failed(self, step_name: str, error: str):
        """Mark a step as failed"""
        result = ExecutionResult(
            step_name=step_name,
            success=False,
            output={},
            error=error,
            execution_time=0.0
        )
        self.set_result(step_name, result)
        
        # Update step status in plan
        for step in self.plan.steps:
            if step.name == step_name:
                step.status = StepStatus.FAILED
                step.error = error
                step.end_time = time.time()
                break
        
        logger.error(f"Marked step as failed: {step_name} - {error}")
    
    def mark_execution_completed(self):
        """Mark execution as completed"""
        self.state = ExecutionState.COMPLETED
        self.end_time = time.time()
        self.current_step = None
        logger.info("Marked execution as completed")
    
    def mark_execution_failed(self, error: str):
        """Mark execution as failed"""
        self.state = ExecutionState.FAILED
        self.end_time = time.time()
        self.error = error
        self.current_step = None
        logger.error(f"Marked execution as failed: {error}")
    
    def mark_execution_cancelled(self):
        """Mark execution as cancelled"""
        self.state = ExecutionState.CANCELLED
        self.end_time = time.time()
        self.current_step = None
        logger.info("Marked execution as cancelled")
    
    def can_continue_execution(self) -> bool:
        """Check if execution can continue"""
        return self.state in [ExecutionState.PENDING, ExecutionState.RUNNING]
    
    def should_stop_execution(self) -> bool:
        """Check if execution should stop"""
        return self.state in [ExecutionState.FAILED, ExecutionState.CANCELLED, ExecutionState.COMPLETED]
    
    def get_remaining_steps(self) -> List[CommandStep]:
        """Get remaining steps to execute"""
        return [
            step for step in self.plan.steps
            if step.status == StepStatus.PENDING
        ]
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_time = (self.end_time - self.start_time) if self.end_time and self.start_time else 0
        successful_steps = len(self.get_completed_steps())
        failed_steps = len(self.get_failed_steps())
        
        return {
            "total_execution_time": total_time,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "success_rate": (successful_steps / (successful_steps + failed_steps) * 100) if (successful_steps + failed_steps) > 0 else 0,
            "average_step_time": total_time / len(self.plan.steps) if len(self.plan.steps) > 0 else 0
        }
