"""
Error Recovery and Learning System for JARVIS Computer Assistant

This module implements a system for logging errors, analyzing them,
and suggesting recovery strategies, contributing to the assistant's self-improvement.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severity levels for errors"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categories for errors"""
    AI_PROCESSING = "ai_processing"
    CAPABILITY_EXECUTION = "capability_execution"
    SYSTEM_INTEGRATION = "system_integration"
    USER_INPUT = "user_input"
    NETWORK = "network"
    UNKNOWN = "unknown"

@dataclass
class ErrorLogEntry:
    """Represents a single error log entry"""
    error_id: str
    timestamp: float
    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: Dict[str, Any] = field(default_factory=dict)
    is_resolved: bool = False
    resolution_notes: Optional[str] = None
    recovery_attempted: bool = False
    recovery_success: Optional[bool] = None
    recovery_message: Optional[str] = None

@dataclass
class LearningRule:
    """Represents a learning rule for error recovery"""
    rule_id: str
    name: str
    condition: str  # e.g., "error_type == 'FileNotFoundError' and 'create' in command"
    action: str     # e.g., "suggest_create_file"
    priority: int
    enabled: bool = True
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

class ErrorRecoveryLearningSystem:
    """Manages error logging, recovery, and learning"""
    
    def __init__(self, ai_manager=None):
        self.ai_manager = ai_manager
        self.error_logs: Dict[str, ErrorLogEntry] = {}
        self.learning_rules: List[LearningRule] = []
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False

    async def initialize(self) -> bool:
        """Initialize the error recovery learning system"""
        try:
            # Load default learning rules
            await self._load_default_rules()
            
            self._is_initialized = True
            self.logger.info("Error recovery learning system initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize error recovery learning system: {e}")
            return False

    async def record_error(self, 
                          error: Exception, 
                          context: Dict[str, Any], 
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                          category: ErrorCategory = ErrorCategory.UNKNOWN) -> str:
        """Record an error for learning and recovery"""
        try:
            error_id = str(uuid.uuid4())
            
            error_entry = ErrorLogEntry(
                error_id=error_id,
                timestamp=time.time(),
                error_type=type(error).__name__,
                message=str(error),
                severity=severity,
                category=category,
                context=context
            )
            
            self.error_logs[error_id] = error_entry
            self.logger.warning(f"Recorded error {error_id}: {error}")
            
            # Attempt automatic recovery
            recovery_success, recovery_message = await self.attempt_recovery(error_id, context)
            error_entry.recovery_attempted = True
            error_entry.recovery_success = recovery_success
            error_entry.recovery_message = recovery_message
            
            return error_id
            
        except Exception as e:
            self.logger.error(f"Failed to record error: {e}")
            return ""

    async def attempt_recovery(self, error_id: str, current_context: Dict[str, Any]) -> Tuple[bool, str]:
        """Attempt to recover from an error"""
        try:
            error_entry = self.error_logs.get(error_id)
            if not error_entry:
                return False, "Error entry not found"
            
            # Find applicable learning rules
            applicable_rules = []
            for rule in self.learning_rules:
                if rule.enabled and self._evaluate_rule_condition(rule, error_entry, current_context):
                    applicable_rules.append(rule)
            
            # Sort by priority (higher priority first)
            applicable_rules.sort(key=lambda x: x.priority, reverse=True)
            
            # Execute recovery actions
            for rule in applicable_rules:
                recovery_success, recovery_message = await self._execute_recovery_action(
                    rule, error_entry, current_context
                )
                if recovery_success:
                    return True, recovery_message
            
            return False, "No applicable recovery actions found"
            
        except Exception as e:
            self.logger.error(f"Failed to attempt recovery: {e}")
            return False, f"Recovery failed: {e}"

    async def generate_codebase_task(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Generate a codebase improvement task based on error analysis"""
        try:
            error_entry = self.error_logs.get(error_id)
            if not error_entry:
                return None
            
            # Analyze error patterns
            similar_errors = await self._find_similar_errors(error_entry)
            
            # Generate improvement suggestions
            suggestions = await self._generate_improvement_suggestions(error_entry, similar_errors)
            
            if suggestions:
                task = {
                    "task_id": str(uuid.uuid4()),
                    "error_id": error_id,
                    "priority": error_entry.severity.value,
                    "category": error_entry.category.value,
                    "suggestions": suggestions,
                    "created_at": time.time(),
                    "status": "pending"
                }
                
                self.logger.info(f"Generated codebase task for error {error_id}")
                return task
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to generate codebase task: {e}")
            return None

    async def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and patterns"""
        try:
            total_errors = len(self.error_logs)
            resolved_errors = sum(1 for error in self.error_logs.values() if error.is_resolved)
            
            # Count by severity
            severity_counts = {}
            for error in self.error_logs.values():
                severity = error.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count by category
            category_counts = {}
            for error in self.error_logs.values():
                category = error.category.value
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by error type
            error_type_counts = {}
            for error in self.error_logs.values():
                error_type = error.error_type
                error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
            
            return {
                "total_errors": total_errors,
                "resolved_errors": resolved_errors,
                "resolution_rate": (resolved_errors / total_errors * 100) if total_errors > 0 else 0,
                "severity_breakdown": severity_counts,
                "category_breakdown": category_counts,
                "error_type_breakdown": error_type_counts,
                "learning_rules_count": len(self.learning_rules),
                "active_rules_count": sum(1 for rule in self.learning_rules if rule.enabled)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get error statistics: {e}")
            return {}

    async def cleanup(self):
        """Cleanup the error recovery learning system"""
        try:
            # Archive old resolved errors (older than 30 days)
            cutoff_time = time.time() - (30 * 24 * 3600)
            self.error_logs = {
                error_id: error for error_id, error in self.error_logs.items()
                if not error.is_resolved or error.timestamp > cutoff_time
            }
            
            self.logger.info("Error recovery learning system cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def _load_default_rules(self):
        """Load default learning rules"""
        try:
            default_rules = [
                LearningRule(
                    rule_id="file_not_found_create",
                    name="File Not Found - Suggest Creation",
                    condition="error_type == 'FileNotFoundError' and 'create' in str(context.get('command', '')).lower()",
                    action="suggest_create_file",
                    priority=8
                ),
                LearningRule(
                    rule_id="permission_denied_elevate",
                    name="Permission Denied - Suggest Elevation",
                    condition="error_type == 'PermissionError'",
                    action="suggest_elevate_permissions",
                    priority=7
                ),
                LearningRule(
                    rule_id="network_timeout_retry",
                    name="Network Timeout - Suggest Retry",
                    condition="'timeout' in str(error).lower() and 'network' in str(context.get('component', '')).lower()",
                    action="suggest_retry_with_backoff",
                    priority=6
                ),
                LearningRule(
                    rule_id="ai_processing_fallback",
                    name="AI Processing Error - Suggest Fallback",
                    condition="category == 'AI_PROCESSING' and severity == 'HIGH'",
                    action="suggest_fallback_processing",
                    priority=9
                ),
                LearningRule(
                    rule_id="capability_not_found_suggest",
                    name="Capability Not Found - Suggest Alternative",
                    condition="error_type == 'CapabilityNotFoundError'",
                    action="suggest_alternative_capability",
                    priority=5
                )
            ]
            
            self.learning_rules.extend(default_rules)
            self.logger.info(f"Loaded {len(default_rules)} default learning rules")
            
        except Exception as e:
            self.logger.error(f"Failed to load default rules: {e}")

    def _evaluate_rule_condition(self, rule: LearningRule, error_entry: ErrorLogEntry, context: Dict[str, Any]) -> bool:
        """Evaluate if a rule condition matches the error and context"""
        try:
            # Simple condition evaluation (in a real implementation, this would be more sophisticated)
            condition = rule.condition.lower()
            
            # Check error type
            if "error_type" in condition:
                error_type_check = f"error_type == '{error_entry.error_type}'"
                if error_type_check.lower() not in condition:
                    return False
            
            # Check category
            if "category" in condition:
                category_check = f"category == '{error_entry.category.value}'"
                if category_check.lower() not in condition:
                    return False
            
            # Check severity
            if "severity" in condition:
                severity_check = f"severity == '{error_entry.severity.value}'"
                if severity_check.lower() not in condition:
                    return False
            
            # Check context
            if "context" in condition:
                for key, value in context.items():
                    if f"'{value}'" in condition and key in condition:
                        return True
            
            return True  # Default to true for simple conditions
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate rule condition: {e}")
            return False

    async def _execute_recovery_action(self, rule: LearningRule, error_entry: ErrorLogEntry, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Execute a recovery action based on the rule"""
        try:
            action = rule.action.lower()
            
            if action == "suggest_create_file":
                return True, "Consider creating the missing file or checking the file path"
            
            elif action == "suggest_elevate_permissions":
                return True, "Try running with elevated permissions or check file/directory permissions"
            
            elif action == "suggest_retry_with_backoff":
                return True, "Retry the operation with exponential backoff"
            
            elif action == "suggest_fallback_processing":
                return True, "Use fallback processing method or alternative AI provider"
            
            elif action == "suggest_alternative_capability":
                return True, "Try using an alternative capability or check available capabilities"
            
            else:
                return False, f"Unknown recovery action: {action}"
                
        except Exception as e:
            self.logger.error(f"Failed to execute recovery action: {e}")
            return False, f"Recovery action failed: {e}"

    async def _find_similar_errors(self, error_entry: ErrorLogEntry) -> List[ErrorLogEntry]:
        """Find similar errors for pattern analysis"""
        try:
            similar_errors = []
            
            for error in self.error_logs.values():
                if error.error_id == error_entry.error_id:
                    continue
                
                # Check for similar error types
                if error.error_type == error_entry.error_type:
                    similar_errors.append(error)
                
                # Check for similar categories
                elif error.category == error_entry.category:
                    similar_errors.append(error)
            
            return similar_errors[:10]  # Return top 10 similar errors
            
        except Exception as e:
            self.logger.error(f"Failed to find similar errors: {e}")
            return []

    async def _generate_improvement_suggestions(self, error_entry: ErrorLogEntry, similar_errors: List[ErrorLogEntry]) -> List[str]:
        """Generate improvement suggestions based on error analysis"""
        try:
            suggestions = []
            
            # Analyze error frequency
            if len(similar_errors) > 5:
                suggestions.append(f"Consider implementing better error handling for {error_entry.error_type}")
            
            # Analyze error category
            if error_entry.category == ErrorCategory.AI_PROCESSING:
                suggestions.append("Review AI provider configuration and fallback mechanisms")
            
            elif error_entry.category == ErrorCategory.CAPABILITY_EXECUTION:
                suggestions.append("Check capability availability and parameter validation")
            
            elif error_entry.category == ErrorCategory.SYSTEM_INTEGRATION:
                suggestions.append("Verify system dependencies and platform compatibility")
            
            # Analyze severity
            if error_entry.severity == ErrorSeverity.CRITICAL:
                suggestions.append("Implement critical error monitoring and alerting")
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate improvement suggestions: {e}")
            return []


# Global instance
_error_recovery_system: Optional[ErrorRecoveryLearningSystem] = None

def get_error_recovery_system() -> ErrorRecoveryLearningSystem:
    """Get the global error recovery learning system instance"""
    global _error_recovery_system
    if _error_recovery_system is None:
        _error_recovery_system = ErrorRecoveryLearningSystem()
    return _error_recovery_system
