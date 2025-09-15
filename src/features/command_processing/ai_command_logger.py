"""
AI Command Logger for JARVIS Computer Assistant

Logs AI command execution, errors, and failures for analysis and improvement.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Log levels for AI commands"""
    SUCCESS = "success"
    ERROR = "error"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    INVALID = "invalid"

@dataclass
class AICommandLog:
    """AI command log entry"""
    timestamp: str
    command_id: str
    command_text: str
    command_type: str  # "quick", "intelligent", "smart"
    log_level: str
    success: bool
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    ai_response: Optional[str] = None
    capabilities_used: List[str] = None
    steps_executed: List[str] = None
    steps_failed: List[str] = None
    user_feedback: Optional[str] = None
    improvement_suggestions: List[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.capabilities_used is None:
            self.capabilities_used = []
        if self.steps_executed is None:
            self.steps_executed = []
        if self.steps_failed is None:
            self.steps_failed = []
        if self.improvement_suggestions is None:
            self.improvement_suggestions = []
        if self.context is None:
            self.context = {}

class AICommandLogger:
    """Logger for AI command execution and analysis"""
    
    def __init__(self, log_file_path: str = "data/logs/ai_commands.json"):
        self.log_file_path = log_file_path
        self.logs: List[AICommandLog] = []
        self._ensure_log_directory()
        self._load_existing_logs()
        
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
    
    def _load_existing_logs(self):
        """Load existing logs from file"""
        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logs = [AICommandLog(**log) for log in data]
                logger.info(f"Loaded {len(self.logs)} existing AI command logs")
        except Exception as e:
            logger.error(f"Failed to load existing logs: {e}")
            self.logs = []
    
    def _save_logs(self):
        """Save logs to file"""
        try:
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(log) for log in self.logs], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save logs: {e}")
    
    def log_command(self, 
                   command_id: str,
                   command_text: str,
                   command_type: str,
                   success: bool,
                   log_level: LogLevel = LogLevel.SUCCESS,
                   error_message: Optional[str] = None,
                   execution_time: Optional[float] = None,
                   ai_response: Optional[str] = None,
                   capabilities_used: List[str] = None,
                   steps_executed: List[str] = None,
                   steps_failed: List[str] = None,
                   user_feedback: Optional[str] = None,
                   improvement_suggestions: List[str] = None,
                   context: Dict[str, Any] = None) -> None:
        """Log an AI command execution"""
        
        log_entry = AICommandLog(
            timestamp=datetime.now().isoformat(),
            command_id=command_id,
            command_text=command_text,
            command_type=command_type,
            log_level=log_level.value,
            success=success,
            error_message=error_message,
            execution_time=execution_time,
            ai_response=ai_response,
            capabilities_used=capabilities_used or [],
            steps_executed=steps_executed or [],
            steps_failed=steps_failed or [],
            user_feedback=user_feedback,
            improvement_suggestions=improvement_suggestions or [],
            context=context or {}
        )
        
        self.logs.append(log_entry)
        self._save_logs()
        
        # Also log to standard logger
        if success:
            logger.info(f"AI Command SUCCESS: {command_text[:50]}...")
        else:
            logger.error(f"AI Command FAILED: {command_text[:50]}... - {error_message}")
    
    def get_failed_commands(self, limit: int = 100) -> List[AICommandLog]:
        """Get failed commands for analysis"""
        failed = [log for log in self.logs if not log.success]
        return failed[-limit:] if limit else failed
    
    def get_error_patterns(self) -> Dict[str, int]:
        """Analyze error patterns"""
        error_patterns = {}
        for log in self.logs:
            if not log.success and log.error_message:
                # Extract error type from message
                error_type = log.error_message.split(':')[0] if ':' in log.error_message else log.error_message
                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
        return error_patterns
    
    def get_capability_failures(self) -> Dict[str, int]:
        """Analyze capability failure patterns"""
        capability_failures = {}
        for log in self.logs:
            if not log.success:
                for capability in log.capabilities_used:
                    capability_failures[capability] = capability_failures.get(capability, 0) + 1
        return capability_failures
    
    def get_improvement_suggestions(self) -> List[str]:
        """Get all improvement suggestions"""
        suggestions = []
        for log in self.logs:
            suggestions.extend(log.improvement_suggestions)
        return list(set(suggestions))  # Remove duplicates
    
    def generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        total_commands = len(self.logs)
        successful_commands = len([log for log in self.logs if log.success])
        failed_commands = total_commands - successful_commands
        
        success_rate = (successful_commands / total_commands * 100) if total_commands > 0 else 0
        
        return {
            "summary": {
                "total_commands": total_commands,
                "successful_commands": successful_commands,
                "failed_commands": failed_commands,
                "success_rate": round(success_rate, 2)
            },
            "error_patterns": self.get_error_patterns(),
            "capability_failures": self.get_capability_failures(),
            "improvement_suggestions": self.get_improvement_suggestions(),
            "recent_failures": [asdict(log) for log in self.get_failed_commands(10)]
        }
    
    def export_analysis(self, output_file: str = "data/logs/ai_analysis_report.json"):
        """Export analysis report to file"""
        try:
            report = self.generate_analysis_report()
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Analysis report exported to {output_file}")
        except Exception as e:
            logger.error(f"Failed to export analysis: {e}")

# Global logger instance
_ai_logger = None

def get_ai_logger() -> AICommandLogger:
    """Get global AI logger instance"""
    global _ai_logger
    if _ai_logger is None:
        _ai_logger = AICommandLogger()
    return _ai_logger

def log_ai_command(command_id: str, command_text: str, command_type: str, 
                  success: bool, **kwargs) -> None:
    """Convenience function to log AI commands"""
    logger = get_ai_logger()
    logger.log_command(command_id, command_text, command_type, success, **kwargs)
