"""
Advanced Logging Manager for JARVIS Computer Assistant

Provides structured logging, log rotation, and centralized log management
for production deployment.
"""

import logging
import logging.handlers
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import traceback
import threading
from contextlib import contextmanager

class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogFormat(Enum):
    """Log formats"""
    JSON = "json"
    TEXT = "text"
    STRUCTURED = "structured"

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    logger: str
    message: str
    module: str
    function: str
    line: int
    thread_id: int
    process_id: int
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    exception: Optional[str] = None
    stack_trace: Optional[str] = None

class LoggingManager:
    """Advanced logging manager with structured logging and rotation"""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 log_format: LogFormat = LogFormat.JSON,
                 log_level: LogLevel = LogLevel.INFO):
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.log_format = log_format
        self.log_level = log_level
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self._correlation_id = threading.local()
        self._user_id = threading.local()
        self._session_id = threading.local()
        self._request_id = threading.local()
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup root logger
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger with handlers"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level.value))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = self._create_formatter(LogFormat.TEXT)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "jarvis.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        file_handler.setLevel(getattr(logging, self.log_level.value))
        file_formatter = self._create_formatter(self.log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "jarvis_errors.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = self._create_formatter(self.log_format)
        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)
    
    def _create_formatter(self, format_type: LogFormat) -> logging.Formatter:
        """Create formatter based on format type"""
        if format_type == LogFormat.JSON:
            return JSONFormatter()
        elif format_type == LogFormat.STRUCTURED:
            return StructuredFormatter()
        else:
            return logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create logger with context"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        return self.loggers[name]
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current thread"""
        self._correlation_id.value = correlation_id
    
    def set_user_context(self, user_id: str, session_id: str = None, request_id: str = None):
        """Set user context for current thread"""
        self._user_id.value = user_id
        self._session_id.value = session_id
        self._request_id.value = request_id
    
    def clear_context(self):
        """Clear thread context"""
        self._correlation_id.value = None
        self._user_id.value = None
        self._session_id.value = None
        self._request_id.value = None
    
    @contextmanager
    def log_context(self, correlation_id: str = None, user_id: str = None, 
                   session_id: str = None, request_id: str = None):
        """Context manager for logging with specific context"""
        old_correlation_id = getattr(self._correlation_id, 'value', None)
        old_user_id = getattr(self._user_id, 'value', None)
        old_session_id = getattr(self._session_id, 'value', None)
        old_request_id = getattr(self._request_id, 'value', None)
        
        try:
            if correlation_id:
                self.set_correlation_id(correlation_id)
            if user_id:
                self.set_user_context(user_id, session_id, request_id)
            yield
        finally:
            self._correlation_id.value = old_correlation_id
            self._user_id.value = old_user_id
            self._session_id.value = old_session_id
            self._request_id.value = old_request_id
    
    def log_command_execution(self, command: str, success: bool, 
                            execution_time: float, steps_executed: int,
                            error: str = None, extra: Dict[str, Any] = None):
        """Log command execution with structured data"""
        logger = self.get_logger("command_execution")
        
        log_data = {
            "command": command,
            "success": success,
            "execution_time": execution_time,
            "steps_executed": steps_executed,
            "error": error,
            "extra": extra or {}
        }
        
        if success:
            logger.info(f"Command executed successfully: {command}", extra=log_data)
        else:
            logger.error(f"Command execution failed: {command}", extra=log_data)
    
    def log_capability_usage(self, capability: str, success: bool,
                           execution_time: float, parameters: Dict[str, Any] = None,
                           error: str = None):
        """Log capability usage with structured data"""
        logger = self.get_logger("capability_usage")
        
        log_data = {
            "capability": capability,
            "success": success,
            "execution_time": execution_time,
            "parameters": parameters or {},
            "error": error
        }
        
        if success:
            logger.info(f"Capability used: {capability}", extra=log_data)
        else:
            logger.error(f"Capability failed: {capability}", extra=log_data)
    
    def log_ai_interaction(self, prompt: str, response: str, model: str,
                          tokens_used: int, response_time: float, cost: float = None):
        """Log AI interaction with structured data"""
        logger = self.get_logger("ai_interaction")
        
        log_data = {
            "prompt_length": len(prompt),
            "response_length": len(response),
            "model": model,
            "tokens_used": tokens_used,
            "response_time": response_time,
            "cost": cost
        }
        
        logger.info(f"AI interaction: {model}", extra=log_data)
    
    def log_websocket_event(self, event_type: str, client_id: str, 
                          message: str = None, error: str = None):
        """Log WebSocket events with structured data"""
        logger = self.get_logger("websocket")
        
        log_data = {
            "event_type": event_type,
            "client_id": client_id,
            "message": message,
            "error": error
        }
        
        logger.info(f"WebSocket event: {event_type}", extra=log_data)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line=record.lineno,
            thread_id=record.thread,
            process_id=record.process,
            correlation_id=getattr(record, 'correlation_id', None),
            user_id=getattr(record, 'user_id', None),
            session_id=getattr(record, 'session_id', None),
            request_id=getattr(record, 'request_id', None),
            extra=getattr(record, 'extra', None),
            exception=record.exc_text,
            stack_trace=traceback.format_exc() if record.exc_info else None
        )
        
        return json.dumps(asdict(log_entry), default=str)

class StructuredFormatter(logging.Formatter):
    """Structured text formatter"""
    
    def format(self, record):
        timestamp = datetime.utcnow().isoformat()
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()
        module = record.module
        function = record.funcName
        line = record.lineno
        
        # Build structured log line
        log_parts = [
            f"[{timestamp}]",
            f"[{level}]",
            f"[{logger_name}]",
            f"[{module}.{function}:{line}]",
            message
        ]
        
        # Add extra fields
        if hasattr(record, 'extra') and record.extra:
            for key, value in record.extra.items():
                log_parts.append(f"{key}={value}")
        
        return " ".join(log_parts)

# Global logging manager instance
_logging_manager = None

def get_logging_manager() -> LoggingManager:
    """Get global logging manager instance"""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager

def setup_logging(log_dir: str = "logs", 
                 log_level: LogLevel = LogLevel.INFO,
                 log_format: LogFormat = LogFormat.JSON):
    """Setup global logging configuration"""
    global _logging_manager
    _logging_manager = LoggingManager(
        log_dir=log_dir,
        log_level=log_level,
        log_format=log_format
    )
    return _logging_manager
