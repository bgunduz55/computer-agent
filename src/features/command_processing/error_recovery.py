"""
Error Recovery and Rollback System

Implements comprehensive error recovery mechanisms for intelligent command execution,
including automatic retry, rollback capabilities, and alternative execution paths.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RecoveryStrategy(Enum):
    """Error recovery strategies"""
    RETRY = "retry"
    ROLLBACK = "rollback"
    ALTERNATIVE = "alternative"
    SKIP = "skip"
    ABORT = "abort"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RecoveryAction:
    """A recovery action to be executed"""
    strategy: RecoveryStrategy
    description: str
    action: Callable
    max_attempts: int = 3
    delay: float = 1.0
    backoff_multiplier: float = 2.0
    timeout: float = 30.0

@dataclass
class ExecutionStep:
    """A step in command execution"""
    step_id: str
    name: str
    capability: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    rollback_action: Optional[Callable] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0

@dataclass
class ExecutionContext:
    """Context for command execution"""
    command_id: str
    steps: List[ExecutionStep]
    variables: Dict[str, Any]
    rollback_stack: List[Callable]
    recovery_actions: List[RecoveryAction]
    max_retries: int = 3
    timeout: float = 300.0

class ErrorRecoveryManager:
    """Manages error recovery and rollback for command execution"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recovery_strategies: Dict[ErrorSeverity, List[RecoveryAction]] = {}
        self.rollback_handlers: Dict[str, Callable] = {}
        self._initialize_default_strategies()
    
    def _initialize_default_strategies(self):
        """Initialize default recovery strategies"""
        # Low severity errors - simple retry
        self.recovery_strategies[ErrorSeverity.LOW] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry with exponential backoff",
                action=self._retry_with_backoff,
                max_attempts=3,
                delay=1.0,
                backoff_multiplier=2.0
            )
        ]
        
        # Medium severity errors - retry with alternative
        self.recovery_strategies[ErrorSeverity.MEDIUM] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry with exponential backoff",
                action=self._retry_with_backoff,
                max_attempts=2,
                delay=2.0,
                backoff_multiplier=2.0
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.ALTERNATIVE,
                description="Try alternative execution method",
                action=self._try_alternative_method,
                max_attempts=1
            )
        ]
        
        # High severity errors - rollback and retry
        self.recovery_strategies[ErrorSeverity.HIGH] = [
            RecoveryAction(
                strategy=RecoveryStrategy.ROLLBACK,
                description="Rollback and retry",
                action=self._rollback_and_retry,
                max_attempts=2
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.ALTERNATIVE,
                description="Try alternative execution method",
                action=self._try_alternative_method,
                max_attempts=1
            )
        ]
        
        # Critical severity errors - abort
        self.recovery_strategies[ErrorSeverity.CRITICAL] = [
            RecoveryAction(
                strategy=RecoveryStrategy.ABORT,
                description="Abort execution and rollback all changes",
                action=self._abort_execution,
                max_attempts=1
            )
        ]
    
    async def handle_execution_error(
        self, 
        step: ExecutionStep, 
        error: Exception, 
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle execution errors with recovery strategies"""
        try:
            # Determine error severity
            severity = self._classify_error_severity(error, step)
            
            # Get recovery strategies for this severity
            strategies = self.recovery_strategies.get(severity, [])
            
            if not strategies:
                return {
                    "success": False,
                    "error": f"No recovery strategies available for {severity.value} severity error",
                    "severity": severity.value
                }
            
            # Try each recovery strategy
            for strategy in strategies:
                try:
                    self.logger.info(f"Trying recovery strategy: {strategy.description}")
                    
                    result = await strategy.action(step, error, context, strategy)
                    
                    if result.get("success", False):
                        self.logger.info(f"Recovery successful with strategy: {strategy.description}")
                        return result
                    
                except Exception as recovery_error:
                    self.logger.error(f"Recovery strategy failed: {strategy.description}, error: {recovery_error}")
                    continue
            
            # All recovery strategies failed
            return {
                "success": False,
                "error": f"All recovery strategies failed for step {step.step_id}",
                "severity": severity.value,
                "original_error": str(error)
            }
            
        except Exception as e:
            self.logger.error(f"Error in error recovery manager: {e}")
            return {
                "success": False,
                "error": f"Error recovery manager failed: {e}",
                "original_error": str(error)
            }
    
    def _classify_error_severity(self, error: Exception, step: ExecutionStep) -> ErrorSeverity:
        """Classify error severity based on error type and context"""
        error_str = str(error).lower()
        
        # Critical errors - system-level failures
        if any(keyword in error_str for keyword in [
            "permission denied", "access denied", "unauthorized", 
            "disk full", "out of memory", "system error"
        ]):
            return ErrorSeverity.CRITICAL
        
        # High severity errors - capability failures
        if any(keyword in error_str for keyword in [
            "capability not found", "executor failed", "timeout", 
            "connection failed", "service unavailable"
        ]):
            return ErrorSeverity.HIGH
        
        # Medium severity errors - parameter or configuration issues
        if any(keyword in error_str for keyword in [
            "invalid parameter", "missing parameter", "validation failed",
            "configuration error", "format error"
        ]):
            return ErrorSeverity.MEDIUM
        
        # Low severity errors - temporary issues
        return ErrorSeverity.LOW
    
    async def _retry_with_backoff(
        self, 
        step: ExecutionStep, 
        error: Exception, 
        context: ExecutionContext, 
        strategy: RecoveryAction
    ) -> Dict[str, Any]:
        """Retry execution with exponential backoff"""
        try:
            if step.retry_count >= strategy.max_attempts:
                return {
                    "success": False,
                    "error": f"Max retry attempts ({strategy.max_attempts}) exceeded"
                }
            
            # Calculate delay with exponential backoff
            delay = strategy.delay * (strategy.backoff_multiplier ** step.retry_count)
            
            self.logger.info(f"Retrying step {step.step_id} in {delay} seconds (attempt {step.retry_count + 1})")
            
            # Wait before retry
            await asyncio.sleep(delay)
            
            # Update retry count
            step.retry_count += 1
            
            # Mark step as retrying
            step.status = "retrying"
            
            return {
                "success": True,
                "action": "retry",
                "delay": delay,
                "retry_count": step.retry_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Retry with backoff failed: {e}"
            }
    
    async def _try_alternative_method(
        self, 
        step: ExecutionStep, 
        error: Exception, 
        context: ExecutionContext, 
        strategy: RecoveryAction
    ) -> Dict[str, Any]:
        """Try alternative execution method"""
        try:
            # Look for alternative capabilities
            alternative_capabilities = self._find_alternative_capabilities(step.capability)
            
            if not alternative_capabilities:
                return {
                    "success": False,
                    "error": "No alternative capabilities found"
                }
            
            # Try each alternative capability
            for alt_capability in alternative_capabilities:
                try:
                    self.logger.info(f"Trying alternative capability: {alt_capability}")
                    
                    # Update step with alternative capability
                    step.capability = alt_capability
                    step.status = "retrying"
                    
                    return {
                        "success": True,
                        "action": "alternative",
                        "alternative_capability": alt_capability
                    }
                    
                except Exception as alt_error:
                    self.logger.warning(f"Alternative capability {alt_capability} failed: {alt_error}")
                    continue
            
            return {
                "success": False,
                "error": "All alternative capabilities failed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Alternative method failed: {e}"
            }
    
    async def _rollback_and_retry(
        self, 
        step: ExecutionStep, 
        error: Exception, 
        context: ExecutionContext, 
        strategy: RecoveryAction
    ) -> Dict[str, Any]:
        """Rollback changes and retry"""
        try:
            # Execute rollback actions
            rollback_success = await self._execute_rollback(step, context)
            
            if not rollback_success:
                return {
                    "success": False,
                    "error": "Rollback failed"
                }
            
            # Reset step status
            step.status = "pending"
            step.error = None
            step.retry_count += 1
            
            return {
                "success": True,
                "action": "rollback_retry",
                "rollback_success": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Rollback and retry failed: {e}"
            }
    
    async def _abort_execution(
        self, 
        step: ExecutionStep, 
        error: Exception, 
        context: ExecutionContext, 
        strategy: RecoveryAction
    ) -> Dict[str, Any]:
        """Abort execution and rollback all changes"""
        try:
            # Execute full rollback
            full_rollback_success = await self._execute_full_rollback(context)
            
            return {
                "success": True,
                "action": "abort",
                "full_rollback_success": full_rollback_success,
                "abort_reason": str(error)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Abort execution failed: {e}"
            }
    
    def _find_alternative_capabilities(self, capability: str) -> List[str]:
        """Find alternative capabilities for a given capability"""
        alternatives = {
            "system_shutdown": ["system_restart"],
            "volume_control": ["media_volume_control"],
            "web_search": ["web_duckduckgo_search"],
            "browser_open_url": ["web_open_url"],
            "file_create_text": ["text_create_file"],
            "app_open": ["application_launch"]
        }
        
        return alternatives.get(capability, [])
    
    async def _execute_rollback(self, step: ExecutionStep, context: ExecutionContext) -> bool:
        """Execute rollback for a specific step"""
        try:
            if step.rollback_action:
                await step.rollback_action(step, context)
                self.logger.info(f"Rollback executed for step {step.step_id}")
                return True
            else:
                self.logger.warning(f"No rollback action defined for step {step.step_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Rollback failed for step {step.step_id}: {e}")
            return False
    
    async def _execute_full_rollback(self, context: ExecutionContext) -> bool:
        """Execute full rollback for all completed steps"""
        try:
            rollback_success = True
            
            # Execute rollback actions in reverse order
            for step in reversed(context.steps):
                if step.status == "completed" and step.rollback_action:
                    try:
                        await step.rollback_action(step, context)
                        self.logger.info(f"Rollback executed for step {step.step_id}")
                    except Exception as e:
                        self.logger.error(f"Rollback failed for step {step.step_id}: {e}")
                        rollback_success = False
            
            return rollback_success
            
        except Exception as e:
            self.logger.error(f"Full rollback failed: {e}")
            return False
    
    def register_rollback_handler(self, capability: str, handler: Callable):
        """Register a rollback handler for a capability"""
        self.rollback_handlers[capability] = handler
        self.logger.info(f"Registered rollback handler for capability: {capability}")
    
    def register_recovery_strategy(
        self, 
        severity: ErrorSeverity, 
        strategy: RecoveryAction
    ):
        """Register a custom recovery strategy"""
        if severity not in self.recovery_strategies:
            self.recovery_strategies[severity] = []
        
        self.recovery_strategies[severity].append(strategy)
        self.logger.info(f"Registered recovery strategy for {severity.value} severity: {strategy.description}")

# Global error recovery manager instance
_error_recovery_manager: Optional[ErrorRecoveryManager] = None

def get_error_recovery_manager() -> ErrorRecoveryManager:
    """Get global error recovery manager instance"""
    global _error_recovery_manager
    if _error_recovery_manager is None:
        _error_recovery_manager = ErrorRecoveryManager()
    return _error_recovery_manager

# Export main classes
__all__ = [
    'ErrorRecoveryManager',
    'RecoveryStrategy',
    'ErrorSeverity',
    'RecoveryAction',
    'ExecutionStep',
    'ExecutionContext',
    'get_error_recovery_manager'
]
