"""
Real-time Feedback System for JARVIS Computer Assistant

Provides user feedback collection, analysis, and response generation.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

class FeedbackJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for feedback system"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._seen = set()
    
    def default(self, obj):
        # Handle circular references
        if id(obj) in self._seen:
            return f"<circular reference to {type(obj).__name__}>"
        
        if hasattr(obj, '__dict__'):
            self._seen.add(id(obj))
            try:
                result = obj.__dict__
                return result
            finally:
                self._seen.discard(id(obj))
        elif hasattr(obj, 'items'):  # Handle mappingproxy and dict-like objects
            return dict(obj)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            return list(obj)
        elif callable(obj):  # Handle functions and methods
            return str(obj)
        return super().default(obj)
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    """Feedback types"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    QUESTION = "question"
    CONFIRMATION = "confirmation"
    SUGGESTION = "suggestion"

class FeedbackPriority(Enum):
    """Feedback priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FeedbackStatus(Enum):
    """Feedback status"""
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    IGNORED = "ignored"
    ESCALATED = "escalated"

@dataclass
class Feedback:
    """Feedback data structure"""
    feedback_id: str
    execution_id: str
    feedback_type: FeedbackType
    priority: FeedbackPriority
    status: FeedbackStatus
    message: str
    user_input: Optional[str] = None
    response: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeedbackRule:
    """Feedback processing rule"""
    rule_id: str
    name: str
    condition: str
    action: str
    priority: FeedbackPriority
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class FeedbackTemplate:
    """Feedback response template"""
    template_id: str
    name: str
    feedback_type: FeedbackType
    template: str
    variables: List[str] = field(default_factory=list)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)

class FeedbackAnalyzer:
    """Analyzes feedback and generates responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates: Dict[str, FeedbackTemplate] = {}
        self.rules: List[FeedbackRule] = []
        self._load_default_templates()
        self._load_default_rules()
    
    def _load_default_templates(self):
        """Load default feedback templates"""
        templates = [
            FeedbackTemplate(
                template_id="success_generic",
                name="Generic Success",
                feedback_type=FeedbackType.SUCCESS,
                template="✅ {message}",
                variables=["message"]
            ),
            FeedbackTemplate(
                template_id="error_generic",
                name="Generic Error",
                feedback_type=FeedbackType.ERROR,
                template="❌ Error: {message}",
                variables=["message"]
            ),
            FeedbackTemplate(
                template_id="warning_generic",
                name="Generic Warning",
                feedback_type=FeedbackType.WARNING,
                template="⚠️ Warning: {message}",
                variables=["message"]
            ),
            FeedbackTemplate(
                template_id="info_generic",
                name="Generic Info",
                feedback_type=FeedbackType.INFO,
                template="ℹ️ {message}",
                variables=["message"]
            ),
            FeedbackTemplate(
                template_id="question_generic",
                name="Generic Question",
                feedback_type=FeedbackType.QUESTION,
                template="❓ {message}",
                variables=["message"]
            ),
            FeedbackTemplate(
                template_id="confirmation_generic",
                name="Generic Confirmation",
                feedback_type=FeedbackType.CONFIRMATION,
                template="✅ {message}",
                variables=["message"]
            ),
            FeedbackTemplate(
                template_id="suggestion_generic",
                name="Generic Suggestion",
                feedback_type=FeedbackType.SUGGESTION,
                template="💡 Suggestion: {message}",
                variables=["message"]
            )
        ]
        
        for template in templates:
            self.templates[template.template_id] = template
    
    def _load_default_rules(self):
        """Load default feedback processing rules"""
        rules = [
            FeedbackRule(
                rule_id="error_escalation",
                name="Error Escalation",
                condition="feedback_type == 'error' and priority == 'critical'",
                action="escalate",
                priority=FeedbackPriority.HIGH
            ),
            FeedbackRule(
                rule_id="success_acknowledgment",
                name="Success Acknowledgment",
                condition="feedback_type == 'success'",
                action="acknowledge",
                priority=FeedbackPriority.LOW
            ),
            FeedbackRule(
                rule_id="question_response",
                name="Question Response",
                condition="feedback_type == 'question'",
                action="respond",
                priority=FeedbackPriority.MEDIUM
            )
        ]
        
        self.rules.extend(rules)
    
    def analyze_feedback(self, feedback: Feedback) -> Dict[str, Any]:
        """Analyze feedback and generate response"""
        try:
            # Find matching template
            template = self._find_template(feedback.feedback_type)
            
            # Generate response using template
            response = self._generate_response(template, feedback)
            
            # Apply processing rules
            actions = self._apply_rules(feedback)
            
            return {
                "response": response,
                "actions": actions,
                "template_used": template.template_id if template else None,
                "rules_applied": [rule.rule_id for rule in actions]
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing feedback: {e}")
            return {
                "response": f"Error processing feedback: {e}",
                "actions": [],
                "template_used": None,
                "rules_applied": []
            }
    
    def _find_template(self, feedback_type: FeedbackType) -> Optional[FeedbackTemplate]:
        """Find template for feedback type"""
        for template in self.templates.values():
            if template.feedback_type == feedback_type and template.enabled:
                return template
        return None
    
    def _generate_response(self, template: Optional[FeedbackTemplate], 
                         feedback: Feedback) -> str:
        """Generate response using template"""
        if not template:
            return feedback.message
        
        try:
            response = template.template
            
            # Replace variables
            for variable in template.variables:
                if variable == "message":
                    response = response.replace("{message}", feedback.message)
                elif variable == "execution_id":
                    response = response.replace("{execution_id}", feedback.execution_id)
                elif variable == "feedback_type":
                    response = response.replace("{feedback_type}", feedback.feedback_type.value)
                elif variable == "priority":
                    response = response.replace("{priority}", feedback.priority.value)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return feedback.message
    
    def _apply_rules(self, feedback: Feedback) -> List[FeedbackRule]:
        """Apply processing rules to feedback"""
        applied_rules = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                if self._evaluate_condition(rule.condition, feedback):
                    applied_rules.append(rule)
            except Exception as e:
                self.logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        return applied_rules
    
    def _evaluate_condition(self, condition: str, feedback: Feedback) -> bool:
        """Evaluate rule condition"""
        try:
            # Simple condition evaluation
            # This could be enhanced with a proper expression evaluator
            if "feedback_type == 'error'" in condition:
                if feedback.feedback_type != FeedbackType.ERROR:
                    return False
            elif "feedback_type == 'success'" in condition:
                if feedback.feedback_type != FeedbackType.SUCCESS:
                    return False
            elif "feedback_type == 'warning'" in condition:
                if feedback.feedback_type != FeedbackType.WARNING:
                    return False
            elif "feedback_type == 'question'" in condition:
                if feedback.feedback_type != FeedbackType.QUESTION:
                    return False
            
            if "priority == 'critical'" in condition:
                if feedback.priority != FeedbackPriority.CRITICAL:
                    return False
            elif "priority == 'high'" in condition:
                if feedback.priority != FeedbackPriority.HIGH:
                    return False
            elif "priority == 'medium'" in condition:
                if feedback.priority != FeedbackPriority.MEDIUM:
                    return False
            elif "priority == 'low'" in condition:
                if feedback.priority != FeedbackPriority.LOW:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

class FeedbackSystem:
    """Main feedback system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feedbacks: Dict[str, Feedback] = {}
        self.analyzer = FeedbackAnalyzer()
        self.subscribers: Set[Callable[[Feedback], None]] = set()
        self.feedback_history: List[Feedback] = []
        self.max_history_size = 1000
    
    def subscribe(self, callback: Callable[[Feedback], None]) -> str:
        """Subscribe to feedback events"""
        self.subscribers.add(callback)
        return f"subscriber_{len(self.subscribers)}"
    
    def unsubscribe(self, callback: Callable[[Feedback], None]):
        """Unsubscribe from feedback events"""
        self.subscribers.discard(callback)
    
    async def _notify_subscribers(self, feedback: Feedback):
        """Notify all subscribers of feedback"""
        for callback in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(feedback)
                else:
                    callback(feedback)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {e}")
    
    def create_feedback(self, execution_id: str, feedback_type: FeedbackType,
                       priority: FeedbackPriority, message: str,
                       user_input: str = None, context: Dict[str, Any] = None) -> str:
        """Create new feedback"""
        feedback_id = str(uuid.uuid4())
        
        feedback = Feedback(
            feedback_id=feedback_id,
            execution_id=execution_id,
            feedback_type=feedback_type,
            priority=priority,
            status=FeedbackStatus.PENDING,
            message=message,
            user_input=user_input,
            context=context or {}
        )
        
        self.feedbacks[feedback_id] = feedback
        self.feedback_history.append(feedback)
        self._trim_history()
        
        # Notify subscribers
        asyncio.create_task(self._notify_subscribers(feedback))
        
        return feedback_id
    
    def process_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """Process feedback and generate response"""
        if feedback_id not in self.feedbacks:
            return {"success": False, "error": "Feedback not found"}
        
        feedback = self.feedbacks[feedback_id]
        feedback.status = FeedbackStatus.PROCESSING
        
        # Analyze feedback
        analysis = self.analyzer.analyze_feedback(feedback)
        
        # Update feedback with response
        feedback.response = analysis["response"]
        feedback.status = FeedbackStatus.RESOLVED
        feedback.resolved_at = datetime.now()
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "response": analysis["response"],
            "actions": analysis["actions"],
            "template_used": analysis["template_used"],
            "rules_applied": analysis["rules_applied"]
        }
    
    def get_feedback(self, feedback_id: str) -> Optional[Feedback]:
        """Get feedback by ID"""
        return self.feedbacks.get(feedback_id)
    
    def list_feedbacks(self, status_filter: Optional[FeedbackStatus] = None,
                      feedback_type_filter: Optional[FeedbackType] = None) -> List[Dict[str, Any]]:
        """List feedbacks with optional filters"""
        feedbacks = []
        
        for feedback in self.feedbacks.values():
            if status_filter and feedback.status != status_filter:
                continue
            if feedback_type_filter and feedback.feedback_type != feedback_type_filter:
                continue
            
            feedbacks.append({
                "feedback_id": feedback.feedback_id,
                "execution_id": feedback.execution_id,
                "feedback_type": feedback.feedback_type.value,
                "priority": feedback.priority.value,
                "status": feedback.status.value,
                "message": feedback.message,
                "user_input": feedback.user_input,
                "response": feedback.response,
                "created_at": feedback.created_at.isoformat(),
                "resolved_at": feedback.resolved_at.isoformat() if feedback.resolved_at else None,
                "context": feedback.context
            })
        
        return feedbacks
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get feedback summary statistics"""
        total_feedbacks = len(self.feedbacks)
        
        status_counts = {}
        type_counts = {}
        priority_counts = {}
        
        for feedback in self.feedbacks.values():
            # Count by status
            status = feedback.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by type
            feedback_type = feedback.feedback_type.value
            type_counts[feedback_type] = type_counts.get(feedback_type, 0) + 1
            
            # Count by priority
            priority = feedback.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "total_feedbacks": total_feedbacks,
            "status_counts": status_counts,
            "type_counts": type_counts,
            "priority_counts": priority_counts
        }
    
    def cleanup_old_feedbacks(self, older_than_hours: int = 24):
        """Cleanup old resolved feedbacks"""
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
        
        to_remove = []
        for feedback_id, feedback in self.feedbacks.items():
            if (feedback.status == FeedbackStatus.RESOLVED and
                feedback.resolved_at and
                feedback.resolved_at.timestamp() < cutoff_time):
                to_remove.append(feedback_id)
        
        for feedback_id in to_remove:
            del self.feedbacks[feedback_id]
        
        self.logger.info(f"Cleaned up {len(to_remove)} old feedbacks")
    
    def _trim_history(self):
        """Trim feedback history to max size"""
        if len(self.feedback_history) > self.max_history_size:
            self.feedback_history = self.feedback_history[-self.max_history_size:]

class FeedbackSystemExecutor:
    """Executor for feedback system operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.feedback_system = FeedbackSystem()
    
    async def initialize(self) -> bool:
        """Initialize feedback system executor"""
        try:
            self._is_initialized = True
            self.logger.info("Feedback system executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize feedback system executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("feedback_system" in parameters or
                "create_feedback" in parameters or
                "process_feedback" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute feedback system capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Feedback system executor not initialized"}
            
            operation = parameters.get("operation", "create_feedback")
            
            if operation == "create_feedback":
                return await self._execute_create_feedback(parameters, context)
            elif operation == "process_feedback":
                return await self._execute_process_feedback(parameters, context)
            elif operation == "get_feedback":
                return await self._execute_get_feedback(parameters, context)
            elif operation == "list_feedbacks":
                return await self._execute_list_feedbacks(parameters, context)
            elif operation == "get_feedback_summary":
                return await self._execute_get_feedback_summary(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing feedback system capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_create_feedback(self, parameters: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create feedback operation"""
        try:
            execution_id = parameters.get("execution_id", "")
            feedback_type_str = parameters.get("feedback_type", "")
            priority_str = parameters.get("priority", "medium")
            message = parameters.get("message", "")
            user_input = parameters.get("user_input")
            context_data = parameters.get("context", {})
            
            if not execution_id or not feedback_type_str or not message:
                return {"success": False, "error": "Execution ID, feedback type, and message required"}
            
            try:
                feedback_type = FeedbackType(feedback_type_str)
                priority = FeedbackPriority(priority_str)
            except ValueError as e:
                return {"success": False, "error": f"Invalid type or priority: {e}"}
            
            feedback_id = self.feedback_system.create_feedback(
                execution_id, feedback_type, priority, message, user_input, context_data
            )
            
            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": f"Feedback created: {feedback_id}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_process_feedback(self, parameters: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute process feedback operation"""
        try:
            feedback_id = parameters.get("feedback_id", "")
            
            if not feedback_id:
                return {"success": False, "error": "Feedback ID required"}
            
            result = self.feedback_system.process_feedback(feedback_id)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_get_feedback(self, parameters: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get feedback operation"""
        try:
            feedback_id = parameters.get("feedback_id", "")
            
            if not feedback_id:
                return {"success": False, "error": "Feedback ID required"}
            
            feedback = self.feedback_system.get_feedback(feedback_id)
            
            if not feedback:
                return {"success": False, "error": "Feedback not found"}
            
            return {
                "success": True,
                "feedback": {
                    "feedback_id": feedback.feedback_id,
                    "execution_id": feedback.execution_id,
                    "feedback_type": feedback.feedback_type.value,
                    "priority": feedback.priority.value,
                    "status": feedback.status.value,
                    "message": feedback.message,
                    "user_input": feedback.user_input,
                    "response": feedback.response,
                    "created_at": feedback.created_at.isoformat(),
                    "resolved_at": feedback.resolved_at.isoformat() if feedback.resolved_at else None,
                    "context": feedback.context
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_list_feedbacks(self, parameters: Dict[str, Any], 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute list feedbacks operation"""
        try:
            status_filter = parameters.get("status_filter")
            feedback_type_filter = parameters.get("feedback_type_filter")
            
            status = None
            if status_filter:
                try:
                    status = FeedbackStatus(status_filter)
                except ValueError:
                    return {"success": False, "error": f"Invalid status filter: {status_filter}"}
            
            feedback_type = None
            if feedback_type_filter:
                try:
                    feedback_type = FeedbackType(feedback_type_filter)
                except ValueError:
                    return {"success": False, "error": f"Invalid feedback type filter: {feedback_type_filter}"}
            
            feedbacks = self.feedback_system.list_feedbacks(status, feedback_type)
            
            return {
                "success": True,
                "feedbacks": feedbacks,
                "total_feedbacks": len(feedbacks)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_get_feedback_summary(self, parameters: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get feedback summary operation"""
        try:
            summary = self.feedback_system.get_feedback_summary()
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
