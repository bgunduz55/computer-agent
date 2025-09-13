"""
Command Orchestrator

Orchestrates the execution of multi-step commands with progress tracking,
error handling, and real-time status updates.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

from .command_planner import ExecutionPlan, CommandStep, StepStatus
from .execution_context import ExecutionContext, ExecutionResult, ExecutionState
from .capability_system import CapabilityManager
from shared.websocket_protocol import WebSocketMessage, MessageBuilder

logger = logging.getLogger(__name__)

@dataclass
class OrchestrationResult:
    """Result of command orchestration"""
    success: bool
    message: str
    execution_time: float
    steps_executed: int
    total_steps: int
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CommandOrchestrator:
    """Orchestrates multi-step command execution"""
    
    def __init__(self):
        self.capability_manager: Optional[CapabilityManager] = None
        self.dynamic_capability_manager = None
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self._progress_callback: Optional[Callable] = None
        self._step_callback: Optional[Callable] = None
    
    async def initialize(self) -> bool:
        """Initialize the orchestrator"""
        try:
            from .capability_system import get_capability_manager
            from .dynamic_capability_system import get_dynamic_capability_manager
            
            self.capability_manager = await get_capability_manager()
            self.dynamic_capability_manager = await get_dynamic_capability_manager()
            
            self._is_initialized = True
            self.logger.info("Command orchestrator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize command orchestrator: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if orchestrator is initialized"""
        return self._is_initialized
    
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set progress update callback"""
        self._progress_callback = callback
    
    def set_step_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set step update callback"""
        self._step_callback = callback
    
    async def execute_plan(
        self, 
        plan: ExecutionPlan, 
        context: ExecutionContext
    ) -> OrchestrationResult:
        """
        Execute a command plan
        
        Args:
            plan: Execution plan
            context: Execution context
            
        Returns:
            OrchestrationResult with execution details
        """
        if not self._is_initialized:
            return OrchestrationResult(
                success=False,
                message="Command orchestrator not initialized",
                execution_time=0.0,
                steps_executed=0,
                total_steps=len(plan.steps),
                error="Not initialized"
            )
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting execution of plan: {plan.original_command}")
            
            # Initialize context
            context.state = ExecutionState.RUNNING
            context.start_time = start_time
            
            # Send initial progress
            await self._send_progress_update(context, "Starting execution...")
            
            # Execute steps
            steps_executed = 0
            for step in plan.steps:
                if not context.can_continue_execution():
                    break
                
                # Check if step is ready
                if not context.get_step_dependencies_met(step):
                    self.logger.warning(f"Step {step.name} dependencies not met, skipping")
                    continue
                
                # Execute step
                step_result = await self._execute_step(step, context)
                steps_executed += 1
                
                if step_result.success:
                    context.mark_step_completed(step.name, step_result)
                    await self._send_step_update(context, step.name, "completed", step_result)
                else:
                    context.mark_step_failed(step.name, step_result.error or "Unknown error")
                    await self._send_step_update(context, step.name, "failed", step_result)
                    
                    # Check if we should continue or stop
                    if self._should_stop_on_failure(step, plan):
                        context.mark_execution_failed(f"Step {step.name} failed: {step_result.error}")
                        break
            
            # Finalize execution
            execution_time = time.time() - start_time
            context.end_time = time.time()
            
            if context.state == ExecutionState.RUNNING:
                context.mark_execution_completed()
            
            # Send final progress
            await self._send_progress_update(context, "Execution completed")
            
            # Create result
            result = OrchestrationResult(
                success=context.state == ExecutionState.COMPLETED,
                message=self._get_result_message(context),
                execution_time=execution_time,
                steps_executed=steps_executed,
                total_steps=len(plan.steps),
                error=context.error,
                metadata=context.get_execution_summary()
            )
            
            self.logger.info(f"Plan execution completed: {result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing plan: {e}")
            context.mark_execution_failed(str(e))
            
            return OrchestrationResult(
                success=False,
                message=f"Error executing plan: {e}",
                execution_time=time.time() - start_time,
                steps_executed=context.get_completed_steps(),
                total_steps=len(plan.steps),
                error=str(e)
            )
    
    async def _execute_step(self, step: CommandStep, context: ExecutionContext) -> ExecutionResult:
        """Execute a single step"""
        step_start_time = time.time()
        
        try:
            self.logger.info(f"Executing step: {step.name}")
            
            # Mark step as running
            context.mark_step_running(step.name)
            step.status = StepStatus.RUNNING
            
            # Send step start update
            await self._send_step_update(context, step.name, "running", None)
            
            # Execute capability
            if not self.capability_manager:
                raise Exception("Capability manager not available")
            
            # Prepare parameters with variable substitution
            parameters = self._substitute_variables(step.parameters, context)
            
            # Try built-in capability first, then dynamic capability
            capability_result = None
            
            # Check if it's a built-in capability
            builtin_capability = await self.capability_manager.get_capability(step.capability_name)
            if builtin_capability:
                capability_result = await self.capability_manager.execute_capability(
                    step.capability_name,
                    parameters,
                    context.variables
                )
            elif self.dynamic_capability_manager:
                # Try dynamic capability
                dynamic_capability = await self.dynamic_capability_manager.get_capability(step.capability_name)
                if dynamic_capability:
                    capability_result = await self.dynamic_capability_manager.execute_capability(
                        step.capability_name,
                        parameters,
                        context.variables
                    )
            
            if capability_result is None:
                raise Exception(f"Capability not found: {step.capability_name}")
            
            # Create execution result
            execution_time = time.time() - step_start_time
            
            if capability_result.get("success", False):
                result = ExecutionResult(
                    step_name=step.name,
                    success=True,
                    output=capability_result,
                    execution_time=execution_time,
                    metadata={"capability": step.capability_name}
                )
                
                # Store step output in context variables
                self._store_step_output(step, capability_result, context)
                
                self.logger.info(f"Step {step.name} completed successfully")
            else:
                result = ExecutionResult(
                    step_name=step.name,
                    success=False,
                    output=capability_result,
                    error=capability_result.get("error", "Unknown error"),
                    execution_time=execution_time,
                    metadata={"capability": step.capability_name}
                )
                
                self.logger.error(f"Step {step.name} failed: {result.error}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - step_start_time
            self.logger.error(f"Error executing step {step.name}: {e}")
            
            return ExecutionResult(
                step_name=step.name,
                success=False,
                output={},
                error=str(e),
                execution_time=execution_time
            )
    
    def _substitute_variables(self, parameters: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Substitute variables in parameters"""
        substituted = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Variable substitution
                var_name = value[2:-1]
                substituted[key] = context.get_variable(var_name, value)
            else:
                substituted[key] = value
        
        return substituted
    
    def _store_step_output(self, step: CommandStep, output: Dict[str, Any], context: ExecutionContext):
        """Store step output in context variables"""
        # Store common output variables
        if "result" in output:
            context.set_variable(f"{step.name}_result", output["result"])
        
        if "data" in output:
            context.set_variable(f"{step.name}_data", output["data"])
        
        # Store step-specific variables
        for key, value in output.items():
            if key not in ["success", "error"]:
                context.set_variable(f"{step.name}_{key}", value)
    
    def _should_stop_on_failure(self, step: CommandStep, plan: ExecutionPlan) -> bool:
        """Determine if execution should stop on step failure"""
        # For now, stop on any failure
        # This could be made configurable per step or plan
        return True
    
    def _get_result_message(self, context: ExecutionContext) -> str:
        """Get result message based on execution state"""
        if context.state == ExecutionState.COMPLETED:
            completed_steps = len(context.get_completed_steps())
            total_steps = len(context.plan.steps)
            return f"Command completed successfully ({completed_steps}/{total_steps} steps)"
        
        elif context.state == ExecutionState.FAILED:
            failed_steps = len(context.get_failed_steps())
            return f"Command failed ({failed_steps} steps failed)"
        
        elif context.state == ExecutionState.CANCELLED:
            return "Command was cancelled"
        
        else:
            return "Command execution status unknown"
    
    async def _send_progress_update(self, context: ExecutionContext, status: str):
        """Send progress update"""
        try:
            if not context.client_id:
                return
            
            progress_info = context.get_execution_progress()
            
            # Create progress message
            message = MessageBuilder.create_intelligent_command_progress(
                progress=progress_info["progress_percentage"],
                status=status,
                current_step=context.current_step or "",
                steps=[
                    {
                        "name": step.name,
                        "description": step.description,
                        "status": step.status.value,
                        "isCompleted": step.status == StepStatus.COMPLETED,
                        "isCurrent": step.name == context.current_step,
                        "hasError": step.status == StepStatus.FAILED,
                        "errorMessage": step.error
                    }
                    for step in context.plan.steps
                ],
                client_id=context.client_id
            )
            
            # Send via callback if available
            if self._progress_callback:
                self._progress_callback(message)
            
        except Exception as e:
            self.logger.error(f"Error sending progress update: {e}")
    
    async def _send_step_update(
        self, 
        context: ExecutionContext, 
        step_name: str, 
        step_status: str, 
        result: Optional[ExecutionResult]
    ):
        """Send step update"""
        try:
            if not context.client_id:
                return
            
            # Create step message
            message = MessageBuilder.create_intelligent_command_step(
                step_name=step_name,
                step_status=step_status,
                step_progress=100 if step_status == "completed" else 0,
                client_id=context.client_id
            )
            
            # Send via callback if available
            if self._step_callback:
                self._step_callback(message)
            
        except Exception as e:
            self.logger.error(f"Error sending step update: {e}")
    
    async def cancel_execution(self, context: ExecutionContext) -> bool:
        """Cancel ongoing execution"""
        try:
            if context.state == ExecutionState.RUNNING:
                context.mark_execution_cancelled()
                self.logger.info("Execution cancelled by user")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error cancelling execution: {e}")
            return False
    
    async def get_execution_status(self, context: ExecutionContext) -> Dict[str, Any]:
        """Get current execution status"""
        return context.get_execution_progress()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            self._is_initialized = False
            self._progress_callback = None
            self._step_callback = None
            self.logger.info("Command orchestrator cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up command orchestrator: {e}")
