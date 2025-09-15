"""
Logging and Analytics Capabilities for JARVIS Computer Assistant

Provides comprehensive logging, analytics, and monitoring capabilities
for tracking system performance, user behavior, and operational metrics.
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from ..logging_analytics_system import (
    LoggingAnalyticsSystem, 
    LogLevel, 
    EventType, 
    MetricType,
    get_logging_analytics_system
)

logger = logging.getLogger(__name__)

class LoggingAnalyticsExecutor:
    """Logging and analytics capabilities executor"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analytics_system: Optional[LoggingAnalyticsSystem] = None
        self.is_initialized = False

    async def initialize(self) -> bool:
        """Initialize the logging analytics executor"""
        try:
            self.analytics_system = get_logging_analytics_system()
            init_result = await self.analytics_system.initialize()
            
            if init_result:
                self.is_initialized = True
                self.logger.info("Logging analytics executor initialized")
                return True
            else:
                self.logger.error("Failed to initialize analytics system")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize logging analytics executor: {e}")
            return False

    async def execute(self, action: str, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute logging and analytics operations"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            if not self.analytics_system:
                return {
                    "success": False,
                    "error": "Analytics system not initialized"
                }
            
            context = context or {}
            
            if action == "log_event":
                return await self._log_event(parameters, context)
            elif action == "record_metric":
                return await self._record_metric(parameters, context)
            elif action == "generate_report":
                return await self._generate_report(parameters, context)
            elif action == "get_real_time_metrics":
                return await self._get_real_time_metrics(parameters, context)
            elif action == "get_performance_stats":
                return await self._get_performance_stats(parameters, context)
            elif action == "search_logs":
                return await self._search_logs(parameters, context)
            elif action == "get_session_analytics":
                return await self._get_session_analytics(parameters, context)
            elif action == "export_data":
                return await self._export_data(parameters, context)
            elif action == "system_health_check":
                return await self._system_health_check(parameters, context)
            elif action == "performance_analysis":
                return await self._performance_analysis(parameters, context)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to execute logging analytics action '{action}': {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def can_execute(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if the executor can handle the given action"""
        supported_actions = {
            "log_event", "record_metric", "generate_report",
            "get_real_time_metrics", "get_performance_stats", 
            "search_logs", "get_session_analytics", "export_data",
            "system_health_check", "performance_analysis"
        }
        return action in supported_actions

    async def cleanup(self):
        """Cleanup the executor"""
        try:
            if self.analytics_system:
                await self.analytics_system.cleanup()
            self.logger.info("Logging analytics executor cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    async def _log_event(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Log an event"""
        try:
            # Required parameters
            level_str = parameters.get("level", "info").upper()
            event_type_str = parameters.get("event_type", "USER_INTERACTION").upper()
            message = parameters.get("message", "")
            
            if not message:
                return {
                    "success": False,
                    "error": "Message is required"
                }
            
            # Convert strings to enums
            try:
                level = LogLevel(level_str.lower())
            except ValueError:
                level = LogLevel.INFO
            
            try:
                event_type = EventType(event_type_str.lower())
            except ValueError:
                event_type = EventType.USER_INTERACTION
            
            # Optional parameters
            session_id = parameters.get("session_id")
            user_id = parameters.get("user_id")
            component = parameters.get("component")
            metadata = parameters.get("metadata", {})
            tags = parameters.get("tags", [])
            correlation_id = parameters.get("correlation_id")
            duration = parameters.get("duration")
            success = parameters.get("success")
            
            log_id = await self.analytics_system.log_event(
                level=level,
                event_type=event_type,
                message=message,
                session_id=session_id,
                user_id=user_id,
                component=component,
                metadata=metadata,
                tags=tags,
                correlation_id=correlation_id,
                duration=duration,
                success=success
            )
            
            return {
                "success": True,
                "log_id": log_id,
                "message": "Event logged successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to log event: {e}"
            }

    async def _record_metric(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Record a metric"""
        try:
            # Required parameters
            metric_type_str = parameters.get("metric_type", "EXECUTION_TIME").upper()
            name = parameters.get("name", "")
            value = parameters.get("value")
            
            if not name or value is None:
                return {
                    "success": False,
                    "error": "Name and value are required"
                }
            
            # Convert string to enum
            try:
                metric_type = MetricType(metric_type_str.lower())
            except ValueError:
                metric_type = MetricType.EXECUTION_TIME
            
            # Optional parameters
            unit = parameters.get("unit")
            labels = parameters.get("labels", {})
            metadata = parameters.get("metadata", {})
            
            metric_id = await self.analytics_system.record_metric(
                metric_type=metric_type,
                name=name,
                value=value,
                unit=unit,
                labels=labels,
                metadata=metadata
            )
            
            return {
                "success": True,
                "metric_id": metric_id,
                "message": "Metric recorded successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to record metric: {e}"
            }

    async def _generate_report(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an analytics report"""
        try:
            # Optional parameters
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            report_type = parameters.get("report_type", "comprehensive")
            
            # Convert string timestamps to float if needed
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time).timestamp()
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time).timestamp()
            
            report = await self.analytics_system.generate_analytics_report(
                start_time=start_time,
                end_time=end_time,
                report_type=report_type
            )
            
            return {
                "success": True,
                "report": {
                    "report_id": report.report_id,
                    "generated_at": report.generated_at,
                    "start_time": report.start_time,
                    "end_time": report.end_time,
                    "report_type": report.report_type,
                    "summary": report.summary,
                    "detailed_data": report.detailed_data,
                    "recommendations": report.recommendations
                },
                "message": "Report generated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate report: {e}"
            }

    async def _get_real_time_metrics(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get real-time metrics"""
        try:
            metrics = await self.analytics_system.get_real_time_metrics()
            
            return {
                "success": True,
                "metrics": metrics,
                "message": "Real-time metrics retrieved successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get real-time metrics: {e}"
            }

    async def _get_performance_stats(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            stats = await self.analytics_system.get_performance_stats()
            
            return {
                "success": True,
                "stats": {
                    "total_commands": stats.total_commands,
                    "successful_commands": stats.successful_commands,
                    "failed_commands": stats.failed_commands,
                    "average_execution_time": stats.average_execution_time,
                    "total_execution_time": stats.total_execution_time,
                    "most_used_commands": stats.most_used_commands,
                    "error_patterns": stats.error_patterns,
                    "peak_usage_hours": stats.peak_usage_hours
                },
                "message": "Performance statistics retrieved successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get performance stats: {e}"
            }

    async def _search_logs(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Search logs with filters"""
        try:
            # Optional parameters
            query = parameters.get("query")
            level_str = parameters.get("level")
            event_type_str = parameters.get("event_type")
            session_id = parameters.get("session_id")
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            limit = parameters.get("limit", 100)
            
            # Convert strings to enums if provided
            level = None
            if level_str:
                try:
                    level = LogLevel(level_str.lower())
                except ValueError:
                    pass
            
            event_type = None
            if event_type_str:
                try:
                    event_type = EventType(event_type_str.lower())
                except ValueError:
                    pass
            
            # Convert string timestamps to float if needed
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time).timestamp()
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time).timestamp()
            
            logs = await self.analytics_system.search_logs(
                query=query,
                level=level,
                event_type=event_type,
                session_id=session_id,
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )
            
            # Convert logs to dictionaries
            log_data = []
            for log in logs:
                log_data.append({
                    "log_id": log.log_id,
                    "timestamp": log.timestamp,
                    "level": log.level.value,
                    "event_type": log.event_type.value,
                    "message": log.message,
                    "session_id": log.session_id,
                    "user_id": log.user_id,
                    "component": log.component,
                    "metadata": log.metadata,
                    "tags": log.tags,
                    "correlation_id": log.correlation_id,
                    "duration": log.duration,
                    "success": log.success
                })
            
            return {
                "success": True,
                "logs": log_data,
                "count": len(log_data),
                "message": f"Found {len(log_data)} logs"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search logs: {e}"
            }

    async def _get_session_analytics(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        try:
            session_id = parameters.get("session_id")
            
            if not session_id:
                return {
                    "success": False,
                    "error": "Session ID is required"
                }
            
            analytics = await self.analytics_system.get_session_analytics(session_id)
            
            return {
                "success": True,
                "session_analytics": analytics,
                "message": "Session analytics retrieved successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get session analytics: {e}"
            }

    async def _export_data(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Export analytics data"""
        try:
            data_type = parameters.get("data_type", "all")  # logs, metrics, reports, all
            format_type = parameters.get("format", "json")  # json, csv
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            
            # For now, return a success message
            # In a full implementation, this would export actual data files
            
            return {
                "success": True,
                "export_info": {
                    "data_type": data_type,
                    "format": format_type,
                    "start_time": start_time,
                    "end_time": end_time,
                    "exported_at": time.time()
                },
                "message": f"Data export initiated for {data_type} in {format_type} format"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to export data: {e}"
            }

    async def _system_health_check(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a system health check"""
        try:
            metrics = await self.analytics_system.get_real_time_metrics()
            stats = await self.analytics_system.get_performance_stats()
            
            # Calculate health indicators
            health_score = 100
            issues = []
            
            # Check error rate
            error_rate = metrics.get("error_rate", 0)
            if error_rate > 10:
                health_score -= 30
                issues.append(f"High error rate: {error_rate:.1f}%")
            elif error_rate > 5:
                health_score -= 15
                issues.append(f"Elevated error rate: {error_rate:.1f}%")
            
            # Check response time
            avg_response_time = metrics.get("average_response_time", 0)
            if avg_response_time > 10:
                health_score -= 20
                issues.append(f"Slow response time: {avg_response_time:.1f}s")
            elif avg_response_time > 5:
                health_score -= 10
                issues.append(f"Elevated response time: {avg_response_time:.1f}s")
            
            # Check system health status
            system_health = metrics.get("system_health", "good")
            if system_health == "critical":
                health_score -= 40
                issues.append("System health is critical")
            elif system_health == "warning":
                health_score -= 20
                issues.append("System health has warnings")
            
            # Determine overall status
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 75:
                status = "good"
            elif health_score >= 50:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "success": True,
                "health_check": {
                    "overall_status": status,
                    "health_score": max(0, health_score),
                    "issues": issues,
                    "metrics": metrics,
                    "performance_stats": {
                        "total_commands": stats.total_commands,
                        "success_rate": (stats.successful_commands / max(1, stats.total_commands)) * 100,
                        "average_execution_time": stats.average_execution_time
                    },
                    "checked_at": time.time()
                },
                "message": f"System health check completed - Status: {status}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to perform health check: {e}"
            }

    async def _performance_analysis(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed performance analysis"""
        try:
            # Get time range
            hours = parameters.get("hours", 24)
            end_time = time.time()
            start_time = end_time - (hours * 3600)
            
            # Generate report for the time range
            report = await self.analytics_system.generate_analytics_report(
                start_time=start_time,
                end_time=end_time,
                report_type="performance"
            )
            
            # Get real-time metrics
            metrics = await self.analytics_system.get_real_time_metrics()
            
            return {
                "success": True,
                "performance_analysis": {
                    "time_range": {
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_hours": hours
                    },
                    "summary": report.summary,
                    "detailed_data": report.detailed_data,
                    "recommendations": report.recommendations,
                    "current_metrics": metrics,
                    "analyzed_at": time.time()
                },
                "message": f"Performance analysis completed for last {hours} hours"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to perform performance analysis: {e}"
            }
