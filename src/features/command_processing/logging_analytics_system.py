"""
Advanced Logging and Analytics System for JARVIS Computer Assistant

This module provides comprehensive logging, analytics, and monitoring capabilities
for remote operations, command execution, and system performance.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Set, Callable, Union
from enum import Enum
from pathlib import Path
import statistics
import hashlib

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Log levels for analytics"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class EventType(Enum):
    """Types of events to track"""
    COMMAND_EXECUTION = "command_execution"
    AI_PROCESSING = "ai_processing"
    BROWSER_AUTOMATION = "browser_automation"
    FILE_OPERATION = "file_operation"
    SYSTEM_OPERATION = "system_operation"
    USER_INTERACTION = "user_interaction"
    ERROR_EVENT = "error_event"
    PERFORMANCE_METRIC = "performance_metric"
    SECURITY_EVENT = "security_event"
    REMOTE_CONTROL = "remote_control"

class MetricType(Enum):
    """Types of metrics to collect"""
    EXECUTION_TIME = "execution_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_PERFORMANCE = "system_performance"
    NETWORK_LATENCY = "network_latency"
    THROUGHPUT = "throughput"

@dataclass
class LogEntry:
    """Single log entry"""
    log_id: str
    timestamp: float
    level: LogLevel
    event_type: EventType
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    component: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    correlation_id: Optional[str] = None
    duration: Optional[float] = None
    success: Optional[bool] = None

@dataclass
class MetricData:
    """Metric data point"""
    metric_id: str
    timestamp: float
    metric_type: MetricType
    name: str
    value: Union[int, float, str, bool]
    unit: Optional[str] = None
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsReport:
    """Analytics report"""
    report_id: str
    generated_at: float
    start_time: float
    end_time: float
    report_type: str
    summary: Dict[str, Any]
    detailed_data: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)

@dataclass
class PerformanceStats:
    """Performance statistics"""
    total_commands: int = 0
    successful_commands: int = 0
    failed_commands: int = 0
    average_execution_time: float = 0.0
    total_execution_time: float = 0.0
    most_used_commands: List[tuple] = field(default_factory=list)
    error_patterns: List[tuple] = field(default_factory=list)
    peak_usage_hours: List[int] = field(default_factory=list)

class LoggingAnalyticsSystem:
    """Advanced logging and analytics system"""
    
    def __init__(self, log_directory: str = "data/logs", analytics_directory: str = "data/analytics"):
        self.log_directory = Path(log_directory)
        self.analytics_directory = Path(analytics_directory)
        self.logger = logging.getLogger(__name__)
        
        # In-memory storage for recent data
        self.log_buffer: List[LogEntry] = []
        self.metric_buffer: List[MetricData] = []
        self.max_buffer_size = 1000
        
        # Analytics data
        self.performance_stats = PerformanceStats()
        self.session_analytics: Dict[str, Dict[str, Any]] = {}
        self.real_time_metrics: Dict[str, Any] = {}
        
        # Configuration
        self.auto_save_interval = 300  # 5 minutes
        self.retention_days = 30
        self.is_initialized = False
        
        # Create directories
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.analytics_directory.mkdir(parents=True, exist_ok=True)
        
        # Background tasks
        self._auto_save_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._analytics_task: Optional[asyncio.Task] = None

    async def initialize(self) -> bool:
        """Initialize the logging and analytics system"""
        try:
            # Load existing data
            await self._load_performance_stats()
            
            # Start background tasks
            self._auto_save_task = asyncio.create_task(self._auto_save_worker())
            self._cleanup_task = asyncio.create_task(self._cleanup_worker())
            self._analytics_task = asyncio.create_task(self._analytics_worker())
            
            self.is_initialized = True
            self.logger.info("Logging and analytics system initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize logging and analytics system: {e}")
            return False

    async def cleanup(self):
        """Cleanup the logging and analytics system"""
        try:
            # Save all data
            await self._save_all_data()
            
            # Cancel background tasks
            if self._auto_save_task:
                self._auto_save_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()
            if self._analytics_task:
                self._analytics_task.cancel()
            
            self.logger.info("Logging and analytics system cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def log_event(self, 
                       level: LogLevel,
                       event_type: EventType,
                       message: str,
                       session_id: Optional[str] = None,
                       user_id: Optional[str] = None,
                       component: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       tags: Optional[List[str]] = None,
                       correlation_id: Optional[str] = None,
                       duration: Optional[float] = None,
                       success: Optional[bool] = None) -> str:
        """Log an event"""
        try:
            log_entry = LogEntry(
                log_id=str(uuid.uuid4()),
                timestamp=time.time(),
                level=level,
                event_type=event_type,
                message=message,
                session_id=session_id,
                user_id=user_id,
                component=component,
                metadata=metadata or {},
                tags=tags or [],
                correlation_id=correlation_id,
                duration=duration,
                success=success
            )
            
            # Add to buffer
            self.log_buffer.append(log_entry)
            
            # Trim buffer if needed
            if len(self.log_buffer) > self.max_buffer_size:
                self.log_buffer = self.log_buffer[-self.max_buffer_size:]
            
            # Update real-time metrics
            await self._update_real_time_metrics(log_entry)
            
            # Update performance stats
            if event_type == EventType.COMMAND_EXECUTION:
                await self._update_performance_stats(log_entry)
            
            return log_entry.log_id
            
        except Exception as e:
            self.logger.error(f"Failed to log event: {e}")
            return ""

    async def record_metric(self,
                           metric_type: MetricType,
                           name: str,
                           value: Union[int, float, str, bool],
                           unit: Optional[str] = None,
                           labels: Optional[Dict[str, str]] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Record a metric"""
        try:
            metric = MetricData(
                metric_id=str(uuid.uuid4()),
                timestamp=time.time(),
                metric_type=metric_type,
                name=name,
                value=value,
                unit=unit,
                labels=labels or {},
                metadata=metadata or {}
            )
            
            # Add to buffer
            self.metric_buffer.append(metric)
            
            # Trim buffer if needed
            if len(self.metric_buffer) > self.max_buffer_size:
                self.metric_buffer = self.metric_buffer[-self.max_buffer_size:]
            
            return metric.metric_id
            
        except Exception as e:
            self.logger.error(f"Failed to record metric: {e}")
            return ""

    async def generate_analytics_report(self,
                                      start_time: Optional[float] = None,
                                      end_time: Optional[float] = None,
                                      report_type: str = "comprehensive") -> AnalyticsReport:
        """Generate an analytics report"""
        try:
            now = time.time()
            start_time = start_time or (now - 86400)  # Last 24 hours
            end_time = end_time or now
            
            # Filter data by time range
            relevant_logs = [
                log for log in self.log_buffer
                if start_time <= log.timestamp <= end_time
            ]
            
            relevant_metrics = [
                metric for metric in self.metric_buffer
                if start_time <= metric.timestamp <= end_time
            ]
            
            # Generate summary
            summary = await self._generate_summary(relevant_logs, relevant_metrics)
            
            # Generate detailed data
            detailed_data = await self._generate_detailed_data(relevant_logs, relevant_metrics)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(summary, detailed_data)
            
            report = AnalyticsReport(
                report_id=str(uuid.uuid4()),
                generated_at=now,
                start_time=start_time,
                end_time=end_time,
                report_type=report_type,
                summary=summary,
                detailed_data=detailed_data,
                recommendations=recommendations
            )
            
            # Save report
            await self._save_report(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate analytics report: {e}")
            return AnalyticsReport(
                report_id="error",
                generated_at=time.time(),
                start_time=start_time or time.time(),
                end_time=end_time or time.time(),
                report_type=report_type,
                summary={"error": str(e)},
                detailed_data={}
            )

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics"""
        return self.real_time_metrics.copy()

    async def get_performance_stats(self) -> PerformanceStats:
        """Get performance statistics"""
        return self.performance_stats

    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        return self.session_analytics.get(session_id, {})

    async def search_logs(self,
                         query: Optional[str] = None,
                         level: Optional[LogLevel] = None,
                         event_type: Optional[EventType] = None,
                         session_id: Optional[str] = None,
                         start_time: Optional[float] = None,
                         end_time: Optional[float] = None,
                         limit: int = 100) -> List[LogEntry]:
        """Search logs with filters"""
        try:
            filtered_logs = []
            
            for log in self.log_buffer:
                # Apply filters
                if level and log.level != level:
                    continue
                if event_type and log.event_type != event_type:
                    continue
                if session_id and log.session_id != session_id:
                    continue
                if start_time and log.timestamp < start_time:
                    continue
                if end_time and log.timestamp > end_time:
                    continue
                if query and query.lower() not in log.message.lower():
                    continue
                
                filtered_logs.append(log)
            
            # Sort by timestamp (newest first)
            filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
            
            return filtered_logs[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to search logs: {e}")
            return []

    async def _update_real_time_metrics(self, log_entry: LogEntry):
        """Update real-time metrics"""
        try:
            now = time.time()
            
            # Initialize if needed
            if "last_update" not in self.real_time_metrics:
                self.real_time_metrics = {
                    "last_update": now,
                    "events_per_minute": 0,
                    "current_active_sessions": [],
                    "error_rate": 0.0,
                    "average_response_time": 0.0,
                    "system_health": "good"
                }
            
            # Update metrics
            self.real_time_metrics["last_update"] = now
            
            # Count events in last minute
            recent_logs = [
                log for log in self.log_buffer
                if (now - log.timestamp) <= 60  # Last minute
            ]
            self.real_time_metrics["events_per_minute"] = len(recent_logs)
            
            # Active sessions
            if log_entry.session_id:
                if "current_active_sessions" not in self.real_time_metrics:
                    self.real_time_metrics["current_active_sessions"] = []
                if log_entry.session_id not in self.real_time_metrics["current_active_sessions"]:
                    self.real_time_metrics["current_active_sessions"].append(log_entry.session_id)
            
            # Error rate in last hour
            hour_ago = now - 3600
            recent_hour_logs = [
                log for log in self.log_buffer
                if log.timestamp >= hour_ago
            ]
            error_logs = [
                log for log in recent_hour_logs
                if log.level in [LogLevel.ERROR, LogLevel.CRITICAL] or log.success is False
            ]
            
            if recent_hour_logs:
                self.real_time_metrics["error_rate"] = len(error_logs) / len(recent_hour_logs) * 100
            
            # Average response time
            recent_duration_logs = [
                log for log in recent_hour_logs
                if log.duration is not None
            ]
            if recent_duration_logs:
                durations = [log.duration for log in recent_duration_logs]
                self.real_time_metrics["average_response_time"] = statistics.mean(durations)
            
            # System health assessment
            error_rate = self.real_time_metrics["error_rate"]
            if error_rate > 10:
                self.real_time_metrics["system_health"] = "critical"
            elif error_rate > 5:
                self.real_time_metrics["system_health"] = "warning"
            else:
                self.real_time_metrics["system_health"] = "good"
            
            # Ensure current_active_sessions is a list for JSON serialization
            if "current_active_sessions" not in self.real_time_metrics:
                self.real_time_metrics["current_active_sessions"] = []
            
        except Exception as e:
            self.logger.error(f"Failed to update real-time metrics: {e}")

    async def _update_performance_stats(self, log_entry: LogEntry):
        """Update performance statistics"""
        try:
            self.performance_stats.total_commands += 1
            
            if log_entry.success is True:
                self.performance_stats.successful_commands += 1
            elif log_entry.success is False:
                self.performance_stats.failed_commands += 1
            
            if log_entry.duration:
                self.performance_stats.total_execution_time += log_entry.duration
                self.performance_stats.average_execution_time = (
                    self.performance_stats.total_execution_time / 
                    self.performance_stats.total_commands
                )
            
        except Exception as e:
            self.logger.error(f"Failed to update performance stats: {e}")

    async def _generate_summary(self, logs: List[LogEntry], metrics: List[MetricData]) -> Dict[str, Any]:
        """Generate summary data"""
        try:
            summary = {
                "total_events": len(logs),
                "total_metrics": len(metrics),
                "event_breakdown": {},
                "level_breakdown": {},
                "success_rate": 0.0,
                "average_duration": 0.0,
                "unique_sessions": 0,
                "unique_users": 0
            }
            
            # Event type breakdown
            for log in logs:
                event_type = log.event_type.value
                summary["event_breakdown"][event_type] = summary["event_breakdown"].get(event_type, 0) + 1
            
            # Log level breakdown
            for log in logs:
                level = log.level.value
                summary["level_breakdown"][level] = summary["level_breakdown"].get(level, 0) + 1
            
            # Success rate
            success_logs = [log for log in logs if log.success is True]
            failed_logs = [log for log in logs if log.success is False]
            total_with_success = len(success_logs) + len(failed_logs)
            
            if total_with_success > 0:
                summary["success_rate"] = len(success_logs) / total_with_success * 100
            
            # Average duration
            duration_logs = [log for log in logs if log.duration is not None]
            if duration_logs:
                durations = [log.duration for log in duration_logs]
                summary["average_duration"] = statistics.mean(durations)
            
            # Unique sessions and users
            sessions = {log.session_id for log in logs if log.session_id}
            users = {log.user_id for log in logs if log.user_id}
            summary["unique_sessions"] = len(sessions)
            summary["unique_users"] = len(users)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            return {"error": str(e)}

    async def _generate_detailed_data(self, logs: List[LogEntry], metrics: List[MetricData]) -> Dict[str, Any]:
        """Generate detailed analytics data"""
        try:
            detailed_data = {
                "hourly_activity": {},
                "command_patterns": {},
                "error_analysis": {},
                "performance_trends": {},
                "user_behavior": {},
                "resource_usage": {}
            }
            
            # Hourly activity
            for log in logs:
                hour = datetime.fromtimestamp(log.timestamp).hour
                detailed_data["hourly_activity"][hour] = detailed_data["hourly_activity"].get(hour, 0) + 1
            
            # Command patterns
            command_logs = [log for log in logs if log.event_type == EventType.COMMAND_EXECUTION]
            for log in command_logs:
                command = log.metadata.get("command", "unknown")
                detailed_data["command_patterns"][command] = detailed_data["command_patterns"].get(command, 0) + 1
            
            # Error analysis
            error_logs = [log for log in logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
            for log in error_logs:
                component = log.component or "unknown"
                if component not in detailed_data["error_analysis"]:
                    detailed_data["error_analysis"][component] = {
                        "count": 0,
                        "messages": []
                    }
                detailed_data["error_analysis"][component]["count"] += 1
                detailed_data["error_analysis"][component]["messages"].append(log.message)
            
            return detailed_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate detailed data: {e}")
            return {"error": str(e)}

    async def _generate_recommendations(self, summary: Dict[str, Any], detailed_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analytics"""
        try:
            recommendations = []
            
            # Error rate recommendations
            error_rate = summary.get("success_rate", 100)
            if error_rate < 90:
                recommendations.append("High error rate detected. Consider reviewing command validation and error handling.")
            
            # Performance recommendations
            avg_duration = summary.get("average_duration", 0)
            if avg_duration > 5:
                recommendations.append("Average command execution time is high. Consider optimizing frequently used commands.")
            
            # Usage pattern recommendations
            hourly_activity = detailed_data.get("hourly_activity", {})
            if hourly_activity:
                peak_hour = max(hourly_activity.items(), key=lambda x: x[1])
                recommendations.append(f"Peak usage detected at hour {peak_hour[0]}. Consider scaling resources during this time.")
            
            # Error pattern recommendations
            error_analysis = detailed_data.get("error_analysis", {})
            if error_analysis:
                most_errors = max(error_analysis.items(), key=lambda x: x[1]["count"])
                recommendations.append(f"Component '{most_errors[0]}' has the highest error count. Consider debugging this component.")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            return ["Error generating recommendations"]

    async def _save_report(self, report: AnalyticsReport):
        """Save analytics report to disk"""
        try:
            report_file = self.analytics_directory / f"report_{report.report_id}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")

    async def _load_performance_stats(self):
        """Load performance statistics from disk"""
        try:
            stats_file = self.analytics_directory / "performance_stats.json"
            
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for key, value in data.items():
                    if hasattr(self.performance_stats, key):
                        setattr(self.performance_stats, key, value)
            
        except Exception as e:
            self.logger.error(f"Failed to load performance stats: {e}")

    async def _save_all_data(self):
        """Save all data to disk"""
        try:
            # Save performance stats
            stats_file = self.analytics_directory / "performance_stats.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.performance_stats), f, indent=2, default=str)
            
            # Save recent logs
            logs_file = self.log_directory / f"logs_{int(time.time())}.json"
            with open(logs_file, 'w', encoding='utf-8') as f:
                logs_data = [asdict(log) for log in self.log_buffer]
                json.dump(logs_data, f, indent=2, default=str)
            
            # Save recent metrics
            metrics_file = self.analytics_directory / f"metrics_{int(time.time())}.json"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                metrics_data = [asdict(metric) for metric in self.metric_buffer]
                json.dump(metrics_data, f, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")

    async def _auto_save_worker(self):
        """Background worker for auto-saving data"""
        while True:
            try:
                await asyncio.sleep(self.auto_save_interval)
                await self._save_all_data()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Auto-save worker error: {e}")

    async def _cleanup_worker(self):
        """Background worker for cleaning up old data"""
        while True:
            try:
                await asyncio.sleep(86400)  # Daily cleanup
                
                cutoff_time = time.time() - (self.retention_days * 86400)
                
                # Clean up log files
                for log_file in self.log_directory.glob("logs_*.json"):
                    if log_file.stat().st_mtime < cutoff_time:
                        log_file.unlink()
                
                # Clean up metric files
                for metric_file in self.analytics_directory.glob("metrics_*.json"):
                    if metric_file.stat().st_mtime < cutoff_time:
                        metric_file.unlink()
                
                # Clean up report files
                for report_file in self.analytics_directory.glob("report_*.json"):
                    if report_file.stat().st_mtime < cutoff_time:
                        report_file.unlink()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup worker error: {e}")

    async def _analytics_worker(self):
        """Background worker for periodic analytics processing"""
        while True:
            try:
                await asyncio.sleep(3600)  # Hourly analytics
                
                # Generate hourly report
                await self.generate_analytics_report(
                    start_time=time.time() - 3600,
                    report_type="hourly"
                )
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Analytics worker error: {e}")


# Global instance
_logging_analytics_system: Optional[LoggingAnalyticsSystem] = None

def get_logging_analytics_system() -> LoggingAnalyticsSystem:
    """Get the global logging and analytics system instance"""
    global _logging_analytics_system
    if _logging_analytics_system is None:
        _logging_analytics_system = LoggingAnalyticsSystem()
    return _logging_analytics_system
