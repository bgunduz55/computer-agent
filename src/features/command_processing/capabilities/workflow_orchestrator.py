"""
Workflow Orchestrator for JARVIS Computer Assistant

Provides advanced workflow orchestration and cross-application automation.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowTrigger(Enum):
    """Workflow trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    CONDITION = "condition"

@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    name: str
    description: str
    version: str
    steps: List[Dict[str, Any]]
    triggers: List[WorkflowTrigger]
    conditions: List[Dict[str, Any]]
    timeout: int = 300  # 5 minutes default
    retry_count: int = 3
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str
    workflow_name: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_step: int = 0
    total_steps: int = 0
    error_message: Optional[str] = None
    context: Dict[str, Any] = None

@dataclass
class StepExecution:
    """Step execution instance"""
    step_id: str
    execution_id: str
    status: StepStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Dict[str, Any] = None

class WorkflowEngine:
    """Main workflow execution engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_executions: Dict[str, List[StepExecution]] = {}
        self.execution_counter = 0
        
    def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register a workflow"""
        try:
            workflow.created_at = datetime.now()
            workflow.updated_at = datetime.now()
            self.workflows[workflow.name] = workflow
            self.logger.info(f"Registered workflow: {workflow.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error registering workflow {workflow.name}: {e}")
            return False
    
    def get_workflow(self, name: str) -> Optional[WorkflowDefinition]:
        """Get workflow by name"""
        return self.workflows.get(name)
    
    def list_workflows(self) -> List[WorkflowDefinition]:
        """List all workflows"""
        return list(self.workflows.values())
    
    async def execute_workflow(self, workflow_name: str, 
                             context: Dict[str, Any] = None) -> str:
        """Execute a workflow and return execution ID"""
        try:
            workflow = self.get_workflow(workflow_name)
            if not workflow:
                raise ValueError(f"Workflow not found: {workflow_name}")
            
            # Create execution instance
            execution_id = f"exec_{self.execution_counter}_{int(time.time())}"
            self.execution_counter += 1
            
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_name=workflow_name,
                status=WorkflowStatus.PENDING,
                started_at=datetime.now(),
                total_steps=len(workflow.steps),
                context=context or {}
            )
            
            self.executions[execution_id] = execution
            self.step_executions[execution_id] = []
            
            # Start execution in background
            asyncio.create_task(self._execute_workflow_async(execution_id))
            
            return execution_id
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_name}: {e}")
            raise
    
    async def _execute_workflow_async(self, execution_id: str):
        """Execute workflow asynchronously"""
        try:
            execution = self.executions[execution_id]
            workflow = self.get_workflow(execution.workflow_name)
            
            if not workflow:
                execution.status = WorkflowStatus.FAILED
                execution.error_message = "Workflow not found"
                return
            
            execution.status = WorkflowStatus.RUNNING
            
            # Execute each step
            for i, step_def in enumerate(workflow.steps):
                execution.current_step = i + 1
                
                # Create step execution
                step_execution = StepExecution(
                    step_id=step_def.get("id", f"step_{i+1}"),
                    execution_id=execution_id,
                    status=StepStatus.PENDING,
                    started_at=datetime.now()
                )
                
                self.step_executions[execution_id].append(step_execution)
                
                try:
                    # Execute step
                    await self._execute_step(step_execution, step_def, execution.context)
                    
                    if step_execution.status == StepStatus.FAILED:
                        # Check if we should retry
                        if step_execution.step_id in [s.step_id for s in self.step_executions[execution_id] if s.status == StepStatus.FAILED]:
                            retry_count = len([s for s in self.step_executions[execution_id] if s.step_id == step_execution.step_id and s.status == StepStatus.FAILED])
                            if retry_count < workflow.retry_count:
                                # Retry step
                                await asyncio.sleep(1.0)
                                step_execution.status = StepStatus.PENDING
                                await self._execute_step(step_execution, step_def, execution.context)
                        
                        if step_execution.status == StepStatus.FAILED:
                            execution.status = WorkflowStatus.FAILED
                            execution.error_message = f"Step {step_execution.step_id} failed: {step_execution.error_message}"
                            return
                    
                    # Check timeout
                    if (datetime.now() - execution.started_at).total_seconds() > workflow.timeout:
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = "Workflow timeout"
                        return
                    
                except Exception as e:
                    step_execution.status = StepStatus.FAILED
                    step_execution.error_message = str(e)
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = f"Step {step_execution.step_id} error: {e}"
                    return
            
            # Workflow completed successfully
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            self.logger.error(f"Error executing workflow {execution_id}: {e}")
    
    async def _execute_step(self, step_execution: StepExecution, 
                          step_def: Dict[str, Any], context: Dict[str, Any]):
        """Execute a single step"""
        try:
            step_execution.status = StepStatus.RUNNING
            
            step_type = step_def.get("type", "action")
            
            if step_type == "action":
                await self._execute_action_step(step_execution, step_def, context)
            elif step_type == "condition":
                await self._execute_condition_step(step_execution, step_def, context)
            elif step_type == "loop":
                await self._execute_loop_step(step_execution, step_def, context)
            elif step_type == "delay":
                await self._execute_delay_step(step_execution, step_def, context)
            else:
                step_execution.status = StepStatus.FAILED
                step_execution.error_message = f"Unknown step type: {step_type}"
                return
            
            step_execution.completed_at = datetime.now()
            
        except Exception as e:
            step_execution.status = StepStatus.FAILED
            step_execution.error_message = str(e)
            step_execution.completed_at = datetime.now()
    
    async def _execute_action_step(self, step_execution: StepExecution, 
                                 step_def: Dict[str, Any], context: Dict[str, Any]):
        """Execute action step"""
        try:
            action = step_def.get("action", "")
            parameters = step_def.get("parameters", {})
            
            # Merge context with parameters
            merged_params = {**context, **parameters}
            
            if action == "launch_application":
                # This would integrate with ApplicationController
                app_name = merged_params.get("app_name", "")
                app_path = merged_params.get("app_path", "")
                arguments = merged_params.get("arguments", [])
                
                # Simulate application launch
                await asyncio.sleep(0.5)
                
                step_execution.result_data = {
                    "action": "launch_application",
                    "app_name": app_name,
                    "success": True
                }
                
            elif action == "send_text":
                text = merged_params.get("text", "")
                app_name = merged_params.get("app_name", "")
                
                # Simulate text sending
                await asyncio.sleep(0.2)
                
                step_execution.result_data = {
                    "action": "send_text",
                    "text": text,
                    "app_name": app_name,
                    "success": True
                }
                
            elif action == "send_key":
                key = merged_params.get("key", "")
                app_name = merged_params.get("app_name", "")
                
                # Simulate key sending
                await asyncio.sleep(0.1)
                
                step_execution.result_data = {
                    "action": "send_key",
                    "key": key,
                    "app_name": app_name,
                    "success": True
                }
                
            else:
                step_execution.status = StepStatus.FAILED
                step_execution.error_message = f"Unknown action: {action}"
                return
            
            step_execution.status = StepStatus.COMPLETED
            
        except Exception as e:
            step_execution.status = StepStatus.FAILED
            step_execution.error_message = str(e)
    
    async def _execute_condition_step(self, step_execution: StepExecution, 
                                    step_def: Dict[str, Any], context: Dict[str, Any]):
        """Execute condition step"""
        try:
            condition = step_def.get("condition", "")
            true_steps = step_def.get("true_steps", [])
            false_steps = step_def.get("false_steps", [])
            
            # Evaluate condition
            condition_result = self._evaluate_condition(condition, context)
            
            if condition_result:
                # Execute true steps
                for true_step in true_steps:
                    await self._execute_step(step_execution, true_step, context)
            else:
                # Execute false steps
                for false_step in false_steps:
                    await self._execute_step(step_execution, false_step, context)
            
            step_execution.status = StepStatus.COMPLETED
            step_execution.result_data = {"condition_result": condition_result}
            
        except Exception as e:
            step_execution.status = StepStatus.FAILED
            step_execution.error_message = str(e)
    
    async def _execute_loop_step(self, step_execution: StepExecution, 
                               step_def: Dict[str, Any], context: Dict[str, Any]):
        """Execute loop step"""
        try:
            loop_count = step_def.get("count", 1)
            loop_steps = step_def.get("steps", [])
            
            for i in range(loop_count):
                # Update context with loop index
                loop_context = {**context, "loop_index": i}
                
                # Execute loop steps
                for loop_step in loop_steps:
                    await self._execute_step(step_execution, loop_step, loop_context)
            
            step_execution.status = StepStatus.COMPLETED
            step_execution.result_data = {"loop_count": loop_count}
            
        except Exception as e:
            step_execution.status = StepStatus.FAILED
            step_execution.error_message = str(e)
    
    async def _execute_delay_step(self, step_execution: StepExecution, 
                                step_def: Dict[str, Any], context: Dict[str, Any]):
        """Execute delay step"""
        try:
            delay = step_def.get("delay", 1.0)
            
            await asyncio.sleep(delay)
            
            step_execution.status = StepStatus.COMPLETED
            step_execution.result_data = {"delay": delay}
            
        except Exception as e:
            step_execution.status = StepStatus.FAILED
            step_execution.error_message = str(e)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate condition string"""
        try:
            # Simple condition evaluation
            # This could be enhanced with a proper expression evaluator
            if "==" in condition:
                left, right = condition.split("==", 1)
                left = left.strip()
                right = right.strip()
                
                # Get value from context
                left_value = context.get(left, left)
                right_value = context.get(right, right)
                
                return str(left_value) == str(right_value)
            
            elif "!=" in condition:
                left, right = condition.split("!=", 1)
                left = left.strip()
                right = right.strip()
                
                left_value = context.get(left, left)
                right_value = context.get(right, right)
                
                return str(left_value) != str(right_value)
            
            elif ">" in condition:
                left, right = condition.split(">", 1)
                left = left.strip()
                right = right.strip()
                
                left_value = context.get(left, left)
                right_value = context.get(right, right)
                
                try:
                    return float(left_value) > float(right_value)
                except ValueError:
                    return str(left_value) > str(right_value)
            
            elif "<" in condition:
                left, right = condition.split("<", 1)
                left = left.strip()
                right = right.strip()
                
                left_value = context.get(left, left)
                right_value = context.get(right, right)
                
                try:
                    return float(left_value) < float(right_value)
                except ValueError:
                    return str(left_value) < str(right_value)
            
            else:
                # Simple boolean check
                return context.get(condition, False)
                
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution status"""
        return self.executions.get(execution_id)
    
    def get_step_executions(self, execution_id: str) -> List[StepExecution]:
        """Get step executions for an execution"""
        return self.step_executions.get(execution_id, [])
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel workflow execution"""
        try:
            execution = self.executions.get(execution_id)
            if not execution:
                return False
            
            if execution.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
                execution.status = WorkflowStatus.CANCELLED
                execution.completed_at = datetime.now()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling execution {execution_id}: {e}")
            return False
    
    def list_executions(self) -> List[WorkflowExecution]:
        """List all executions"""
        return list(self.executions.values())
    
    def cleanup_completed_executions(self, older_than_hours: int = 24):
        """Cleanup completed executions older than specified hours"""
        try:
            cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
            
            to_remove = []
            for execution_id, execution in self.executions.items():
                if (execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED] and
                    execution.completed_at and
                    execution.completed_at.timestamp() < cutoff_time):
                    to_remove.append(execution_id)
            
            for execution_id in to_remove:
                del self.executions[execution_id]
                if execution_id in self.step_executions:
                    del self.step_executions[execution_id]
            
            self.logger.info(f"Cleaned up {len(to_remove)} completed executions")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up executions: {e}")

class WorkflowOrchestratorExecutor:
    """Executor for workflow orchestration operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.engine = WorkflowEngine()
        self._load_default_workflows()
    
    async def initialize(self) -> bool:
        """Initialize workflow orchestrator executor"""
        try:
            self._is_initialized = True
            self.logger.info("Workflow orchestrator executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize workflow orchestrator executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("workflow_orchestration" in parameters or
                "execute_workflow" in parameters or
                "create_workflow" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow orchestration capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Workflow orchestrator executor not initialized"}
            
            operation = parameters.get("operation", "execute_workflow")
            
            if operation == "execute_workflow":
                return await self._execute_workflow(parameters, context)
            elif operation == "create_workflow":
                return await self._create_workflow(parameters, context)
            elif operation == "list_workflows":
                return await self._list_workflows(parameters, context)
            elif operation == "get_execution_status":
                return await self._get_execution_status(parameters, context)
            elif operation == "cancel_execution":
                return await self._cancel_execution(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing workflow orchestration capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_workflow(self, parameters: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow operation"""
        try:
            workflow_name = parameters.get("workflow_name", "")
            execution_context = parameters.get("context", {})
            
            if not workflow_name:
                return {"success": False, "error": "Workflow name required"}
            
            execution_id = await self.engine.execute_workflow(workflow_name, execution_context)
            
            return {
                "success": True,
                "execution_id": execution_id,
                "workflow_name": workflow_name,
                "message": f"Workflow {workflow_name} started with execution ID {execution_id}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_workflow(self, parameters: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow operation"""
        try:
            name = parameters.get("name", "")
            description = parameters.get("description", "")
            steps = parameters.get("steps", [])
            triggers = parameters.get("triggers", [WorkflowTrigger.MANUAL])
            conditions = parameters.get("conditions", [])
            timeout = parameters.get("timeout", 300)
            retry_count = parameters.get("retry_count", 3)
            
            if not name or not steps:
                return {"success": False, "error": "Workflow name and steps required"}
            
            workflow = WorkflowDefinition(
                name=name,
                description=description,
                version="1.0",
                steps=steps,
                triggers=triggers,
                conditions=conditions,
                timeout=timeout,
                retry_count=retry_count
            )
            
            success = self.engine.register_workflow(workflow)
            
            return {
                "success": success,
                "workflow_name": name,
                "message": f"Workflow {name} {'created' if success else 'failed to create'}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_workflows(self, parameters: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """List workflows operation"""
        try:
            workflows = self.engine.list_workflows()
            
            workflow_list = []
            for workflow in workflows:
                workflow_list.append({
                    "name": workflow.name,
                    "description": workflow.description,
                    "version": workflow.version,
                    "steps_count": len(workflow.steps),
                    "triggers": [t.value for t in workflow.triggers],
                    "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                    "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None
                })
            
            return {
                "success": True,
                "workflows": workflow_list,
                "total_workflows": len(workflow_list)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_execution_status(self, parameters: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Get execution status operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            
            if not execution_id:
                return {"success": False, "error": "Execution ID required"}
            
            execution = self.engine.get_execution_status(execution_id)
            if not execution:
                return {"success": False, "error": "Execution not found"}
            
            step_executions = self.engine.get_step_executions(execution_id)
            
            return {
                "success": True,
                "execution": {
                    "execution_id": execution.execution_id,
                    "workflow_name": execution.workflow_name,
                    "status": execution.status.value,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "current_step": execution.current_step,
                    "total_steps": execution.total_steps,
                    "error_message": execution.error_message
                },
                "step_executions": [
                    {
                        "step_id": step.step_id,
                        "status": step.status.value,
                        "started_at": step.started_at.isoformat(),
                        "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                        "error_message": step.error_message,
                        "result_data": step.result_data
                    }
                    for step in step_executions
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _cancel_execution(self, parameters: Dict[str, Any], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel execution operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            
            if not execution_id:
                return {"success": False, "error": "Execution ID required"}
            
            success = await self.engine.cancel_execution(execution_id)
            
            return {
                "success": success,
                "execution_id": execution_id,
                "message": f"Execution {execution_id} {'cancelled' if success else 'failed to cancel'}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _load_default_workflows(self):
        """Load default workflows"""
        # Document creation workflow
        document_workflow = WorkflowDefinition(
            name="document_creation",
            description="Create and format a document",
            version="1.0",
            steps=[
                {
                    "id": "launch_editor",
                    "type": "action",
                    "action": "launch_application",
                    "parameters": {"app_name": "notepad"}
                },
                {
                    "id": "delay_1",
                    "type": "delay",
                    "delay": 2.0
                },
                {
                    "id": "type_title",
                    "type": "action",
                    "action": "send_text",
                    "parameters": {"text": "Document Title\n\n"}
                },
                {
                    "id": "type_content",
                    "type": "action",
                    "action": "send_text",
                    "parameters": {"text": "This is the document content.\n"}
                },
                {
                    "id": "save_document",
                    "type": "action",
                    "action": "send_key",
                    "parameters": {"key": "ctrl+s"}
                }
            ],
            triggers=[WorkflowTrigger.MANUAL],
            conditions=[],
            timeout=60,
            retry_count=2
        )
        
        self.engine.register_workflow(document_workflow)
        
        # Web automation workflow
        web_workflow = WorkflowDefinition(
            name="web_automation",
            description="Automate web browsing tasks",
            version="1.0",
            steps=[
                {
                    "id": "launch_browser",
                    "type": "action",
                    "action": "launch_application",
                    "parameters": {"app_name": "chrome"}
                },
                {
                    "id": "delay_1",
                    "type": "delay",
                    "delay": 3.0
                },
                {
                    "id": "focus_address_bar",
                    "type": "action",
                    "action": "send_key",
                    "parameters": {"key": "ctrl+l"}
                },
                {
                    "id": "type_url",
                    "type": "action",
                    "action": "send_text",
                    "parameters": {"text": "https://www.google.com"}
                },
                {
                    "id": "navigate",
                    "type": "action",
                    "action": "send_key",
                    "parameters": {"key": "enter"}
                }
            ],
            triggers=[WorkflowTrigger.MANUAL],
            conditions=[],
            timeout=120,
            retry_count=3
        )
        
        self.engine.register_workflow(web_workflow)

