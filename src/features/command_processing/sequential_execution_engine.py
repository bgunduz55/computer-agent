"""
Sequential Execution Engine

Handles sequential execution of multi-step commands with real-time
progress tracking, error recovery, and user feedback.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .command_planner import ExecutionPlan, CommandStep, StepStatus
from .execution_context import ExecutionContext, ExecutionState
from .command_orchestrator import CommandOrchestrator, OrchestrationResult
from shared.websocket_protocol import WebSocketMessage, MessageBuilder

logger = logging.getLogger(__name__)

class ExecutionStrategy(Enum):
    """Execution strategy for sequential tasks"""
    SEQUENTIAL = "sequential"      # Execute one step at a time
    PARALLEL = "parallel"          # Execute independent steps in parallel
    MIXED = "mixed"               # Mix of sequential and parallel

@dataclass
class StepExecutionResult:
    """Result of individual step execution"""
    step_name: str
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    dependencies_met: bool = True

@dataclass
class SequentialExecutionResult:
    """Result of sequential execution"""
    success: bool
    message: str
    total_execution_time: float
    steps_completed: int
    total_steps: int
    failed_steps: List[str] = field(default_factory=list)
    successful_steps: List[str] = field(default_factory=list)
    step_results: Dict[str, StepExecutionResult] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SequentialExecutionEngine:
    """Engine for sequential execution of multi-step commands"""
    
    def __init__(self):
        self.orchestrator: Optional[CommandOrchestrator] = None
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self._progress_callback: Optional[Callable] = None
        self._step_callback: Optional[Callable] = None
        self._execution_strategy = ExecutionStrategy.SEQUENTIAL
        self._max_retries = 3
        self._retry_delay = 1.0  # seconds
    
    async def initialize(self) -> bool:
        """Initialize sequential execution engine"""
        try:
            self.orchestrator = CommandOrchestrator()
            await self.orchestrator.initialize()
            
            self._is_initialized = True
            self.logger.info("Sequential execution engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize sequential execution engine: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized"""
        return self._is_initialized
    
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set progress update callback"""
        self._progress_callback = callback
    
    def set_step_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set step callback"""
        self._step_callback = callback
    
    def set_execution_strategy(self, strategy: ExecutionStrategy):
        """Set execution strategy"""
        self._execution_strategy = strategy
    
    async def execute_sequential_plan(
        self, 
        plan: ExecutionPlan, 
        context: ExecutionContext
    ) -> SequentialExecutionResult:
        """
        Execute a plan sequentially with progress tracking
        
        Args:
            plan: Execution plan to execute
            context: Execution context
            
        Returns:
            SequentialExecutionResult with execution details
        """
        if not self._is_initialized:
            return SequentialExecutionResult(
                success=False,
                message="Sequential execution engine not initialized",
                total_execution_time=0.0,
                steps_completed=0,
                total_steps=len(plan.steps),
                error="Not initialized"
            )
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting sequential execution of plan: {plan.original_command}")
            
            # Initialize context
            context.state = ExecutionState.RUNNING
            context.start_time = start_time
            
            # Send initial progress
            await self._send_progress_update(context, "Starting sequential execution...")
            
            # Execute steps based on strategy
            if self._execution_strategy == ExecutionStrategy.SEQUENTIAL:
                result = await self._execute_sequential(plan, context)
            elif self._execution_strategy == ExecutionStrategy.PARALLEL:
                result = await self._execute_parallel(plan, context)
            else:  # MIXED
                result = await self._execute_mixed(plan, context)
            
            # Finalize execution
            total_execution_time = time.time() - start_time
            context.end_time = time.time()
            
            if context.state == ExecutionState.RUNNING:
                context.mark_execution_completed()
            
            # Send final progress
            await self._send_progress_update(context, "Sequential execution completed")
            
            # Create result
            execution_result = SequentialExecutionResult(
                success=result.success,
                message=result.message,
                total_execution_time=total_execution_time,
                steps_completed=result.steps_executed,
                total_steps=len(plan.steps),
                failed_steps=context.get_failed_steps(),
                successful_steps=context.get_completed_steps(),
                step_results=self._create_step_results(context),
                error=result.error,
                metadata=result.metadata
            )
            
            self.logger.info(f"Sequential execution completed: {execution_result.success}")
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Error in sequential execution: {e}")
            context.mark_execution_failed(str(e))
            
            return SequentialExecutionResult(
                success=False,
                message=f"Sequential execution failed: {e}",
                total_execution_time=time.time() - start_time,
                steps_completed=context.get_completed_steps(),
                total_steps=len(plan.steps),
                failed_steps=context.get_failed_steps(),
                successful_steps=context.get_completed_steps(),
                error=str(e)
            )
    
    async def _execute_sequential(self, plan: ExecutionPlan, context: ExecutionContext) -> OrchestrationResult:
        """Execute steps sequentially (one after another)"""
        try:
            steps_executed = 0
            
            for step in plan.steps:
                if not context.can_continue_execution():
                    break
                
                # Check dependencies
                if not context.get_step_dependencies_met(step):
                    self.logger.warning(f"Step {step.name} dependencies not met, skipping")
                    continue
                
                # Execute step
                step_result = await self._execute_step_with_retry(step, context)
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
            
            # Create result
            return OrchestrationResult(
                success=context.state == ExecutionState.COMPLETED,
                message=self._get_result_message(context),
                execution_time=time.time() - context.start_time,
                steps_executed=steps_executed,
                total_steps=len(plan.steps),
                error=context.error,
                metadata=context.get_execution_summary()
            )
            
        except Exception as e:
            self.logger.error(f"Error in sequential execution: {e}")
            raise
    
    async def _execute_parallel(self, plan: ExecutionPlan, context: ExecutionContext) -> OrchestrationResult:
        """Execute independent steps in parallel"""
        try:
            # Group steps by dependency level
            dependency_groups = self._group_steps_by_dependencies(plan.steps)
            
            steps_executed = 0
            
            for group in dependency_groups:
                if not context.can_continue_execution():
                    break
                
                # Execute all steps in this group in parallel
                tasks = []
                for step in group:
                    if context.get_step_dependencies_met(step):
                        task = asyncio.create_task(self._execute_step_with_retry(step, context))
                        tasks.append((step, task))
                
                # Wait for all tasks in this group to complete
                for step, task in tasks:
                    try:
                        step_result = await task
                        steps_executed += 1
                        
                        if step_result.success:
                            context.mark_step_completed(step.name, step_result)
                            await self._send_step_update(context, step.name, "completed", step_result)
                        else:
                            context.mark_step_failed(step.name, step_result.error or "Unknown error")
                            await self._send_step_update(context, step.name, "failed", step_result)
                            
                            if self._should_stop_on_failure(step, plan):
                                context.mark_execution_failed(f"Step {step.name} failed: {step_result.error}")
                                break
                                
                    except Exception as e:
                        self.logger.error(f"Error executing step {step.name}: {e}")
                        context.mark_step_failed(step.name, str(e))
                        await self._send_step_update(context, step.name, "failed", None)
            
            # Create result
            return OrchestrationResult(
                success=context.state == ExecutionState.COMPLETED,
                message=self._get_result_message(context),
                execution_time=time.time() - context.start_time,
                steps_executed=steps_executed,
                total_steps=len(plan.steps),
                error=context.error,
                metadata=context.get_execution_summary()
            )
            
        except Exception as e:
            self.logger.error(f"Error in parallel execution: {e}")
            raise
    
    async def _execute_mixed(self, plan: ExecutionPlan, context: ExecutionContext) -> OrchestrationResult:
        """Execute steps using mixed strategy (sequential + parallel)"""
        try:
            # This is a simplified mixed strategy
            # In practice, this would be more sophisticated
            return await self._execute_sequential(plan, context)
            
        except Exception as e:
            self.logger.error(f"Error in mixed execution: {e}")
            raise
    
    def _group_steps_by_dependencies(self, steps: List[CommandStep]) -> List[List[CommandStep]]:
        """Group steps by dependency level for parallel execution"""
        groups = []
        remaining_steps = steps.copy()
        
        while remaining_steps:
            # Find steps with no unmet dependencies
            current_group = []
            for step in remaining_steps[:]:
                if not step.dependencies or all(
                    any(s.name == dep for s in steps if s not in remaining_steps)
                    for dep in step.dependencies
                ):
                    current_group.append(step)
                    remaining_steps.remove(step)
            
            if not current_group:
                # If no steps can be executed, add remaining steps to current group
                current_group = remaining_steps
                remaining_steps = []
            
            groups.append(current_group)
        
        return groups
    
    async def _execute_step_with_retry(
        self, 
        step: CommandStep, 
        context: ExecutionContext
    ) -> StepExecutionResult:
        """Execute a step with retry logic"""
        retry_count = 0
        last_error = None
        
        while retry_count <= self._max_retries:
            try:
                # Execute step
                result = await self._execute_single_step(step, context)
                
                if result.success:
                    return result
                else:
                    last_error = result.error
                    retry_count += 1
                    
                    if retry_count <= self._max_retries:
                        self.logger.warning(f"Step {step.name} failed, retrying ({retry_count}/{self._max_retries})")
                        await asyncio.sleep(self._retry_delay * retry_count)
                    else:
                        self.logger.error(f"Step {step.name} failed after {self._max_retries} retries")
                        return StepExecutionResult(
                            step_name=step.name,
                            success=False,
                            output={},
                            error=last_error,
                            retry_count=retry_count
                        )
                        
            except Exception as e:
                last_error = str(e)
                retry_count += 1
                
                if retry_count <= self._max_retries:
                    self.logger.warning(f"Step {step.name} failed with exception, retrying: {e}")
                    await asyncio.sleep(self._retry_delay * retry_count)
                else:
                    self.logger.error(f"Step {step.name} failed after {self._max_retries} retries: {e}")
                    return StepExecutionResult(
                        step_name=step.name,
                        success=False,
                        output={},
                        error=last_error,
                        retry_count=retry_count
                    )
        
        return StepExecutionResult(
            step_name=step.name,
            success=False,
            output={},
            error=last_error,
            retry_count=retry_count
        )
    
    async def _execute_single_step(
        self, 
        step: CommandStep, 
        context: ExecutionContext
    ) -> StepExecutionResult:
        """Execute a single step"""
        step_start_time = time.time()
        
        try:
            self.logger.info(f"Executing step: {step.name}")
            
            # Mark step as running
            context.mark_step_running(step.name)
            step.status = StepStatus.RUNNING
            
            # Send step start update
            await self._send_step_update(context, step.name, "running", None)
            
            # Execute using orchestrator
            if self.orchestrator:
                result = await self.orchestrator._execute_step(step, context)
                
                execution_time = time.time() - step_start_time
                
                if result.success:
                    return StepExecutionResult(
                        step_name=step.name,
                        success=True,
                        output=result.output,
                        execution_time=execution_time
                    )
                else:
                    return StepExecutionResult(
                        step_name=step.name,
                        success=False,
                        output=result.output,
                        error=result.error,
                        execution_time=execution_time
                    )
            else:
                raise Exception("Orchestrator not available")
                
        except Exception as e:
            execution_time = time.time() - step_start_time
            self.logger.error(f"Error executing step {step.name}: {e}")
            
            return StepExecutionResult(
                step_name=step.name,
                success=False,
                output={},
                error=str(e),
                execution_time=execution_time
            )
    
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
            return f"Sequential execution completed successfully ({completed_steps}/{total_steps} steps)"
        
        elif context.state == ExecutionState.FAILED:
            failed_steps = len(context.get_failed_steps())
            return f"Sequential execution failed ({failed_steps} steps failed)"
        
        elif context.state == ExecutionState.CANCELLED:
            return "Sequential execution was cancelled"
        
        else:
            return "Sequential execution status unknown"
    
    def _create_step_results(self, context: ExecutionContext) -> Dict[str, StepExecutionResult]:
        """Create step results from context"""
        step_results = {}
        
        for step_name, result in context.results.items():
            step_results[step_name] = StepExecutionResult(
                step_name=step_name,
                success=result.success,
                output=result.output,
                error=result.error,
                execution_time=result.execution_time
            )
        
        return step_results
    
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
        result: Optional[StepExecutionResult]
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
                self.logger.info("Sequential execution cancelled by user")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error cancelling sequential execution: {e}")
            return False
    
    async def get_execution_status(self, context: ExecutionContext) -> Dict[str, Any]:
        """Get current execution status"""
        return context.get_execution_progress()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.orchestrator:
                await self.orchestrator.cleanup()
            self._is_initialized = False
            self._progress_callback = None
            self._step_callback = None
            self.logger.info("Sequential execution engine cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up sequential execution engine: {e}")

# Global sequential execution engine instance
_sequential_execution_engine: Optional[SequentialExecutionEngine] = None

async def get_sequential_execution_engine() -> SequentialExecutionEngine:
    """Get global sequential execution engine instance"""
    global _sequential_execution_engine
    if _sequential_execution_engine is None:
        _sequential_execution_engine = SequentialExecutionEngine()
        await _sequential_execution_engine.initialize()
    return _sequential_execution_engine

async def cleanup_sequential_execution_engine():
    """Cleanup global sequential execution engine"""
    global _sequential_execution_engine
    if _sequential_execution_engine:
        await _sequential_execution_engine.cleanup()
        _sequential_execution_engine = None
