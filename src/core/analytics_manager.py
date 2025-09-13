"""
Analytics Manager for JARVIS Computer Assistant
Handles analytics, monitoring, metrics collection, and reporting
"""

import asyncio
import logging
import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from pathlib import Path
import threading


@dataclass
class UsageMetric:
    """Usage metric data"""
    metric_type: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class UserAction:
    """User action event"""
    action_type: str
    action_data: Dict[str, Any]
    user_id: str
    session_id: str
    timestamp: datetime
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class SystemEvent:
    """System event data"""
    event_type: str
    severity: str  # info, warning, error, critical
    message: str
    component: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AnalyticsReport:
    """Analytics report data"""
    report_type: str
    title: str
    data: Dict[str, Any]
    generated_at: datetime
    period_start: datetime
    period_end: datetime


class MetricsCollector:
    """Collects and aggregates metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._metrics: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self._aggregated_metrics: Dict[str, Any] = defaultdict(list)
        self._lock = threading.Lock()
        
    def record_metric(self, metric_type: str, value: float, unit: str = "", 
                     tags: Dict[str, str] = None) -> None:
        """Record a metric"""
        try:
            with self._lock:
                metric = UsageMetric(
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    timestamp=datetime.now(),
                    tags=tags or {}
                )
                self._metrics.append(metric)
                
                # Update aggregated metrics
                key = f"{metric_type}_{unit}" if unit else metric_type
                self._aggregated_metrics[key].append({
                    'value': value,
                    'timestamp': metric.timestamp.isoformat(),
                    'tags': metric.tags
                })
                
                # Keep only last 1000 for each metric type
                if len(self._aggregated_metrics[key]) > 1000:
                    self._aggregated_metrics[key] = self._aggregated_metrics[key][-1000:]
                    
        except Exception as e:
            self.logger.error(f"Error recording metric: {e}")
    
    def get_metrics(self, metric_type: str = None, since: datetime = None) -> List[UsageMetric]:
        """Get metrics with optional filtering"""
        try:
            with self._lock:
                metrics = list(self._metrics)
                
                if metric_type:
                    metrics = [m for m in metrics if m.metric_type == metric_type]
                
                if since:
                    metrics = [m for m in metrics if m.timestamp >= since]
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return []
    
    def get_aggregated_metrics(self, metric_type: str = None) -> Dict[str, Any]:
        """Get aggregated metrics"""
        try:
            with self._lock:
                if metric_type:
                    return {k: v for k, v in self._aggregated_metrics.items() 
                           if k.startswith(metric_type)}
                return dict(self._aggregated_metrics)
                
        except Exception as e:
            self.logger.error(f"Error getting aggregated metrics: {e}")
            return {}
    
    def calculate_statistics(self, metric_type: str, period_hours: int = 24) -> Dict[str, float]:
        """Calculate statistics for a metric type"""
        try:
            since = datetime.now() - timedelta(hours=period_hours)
            metrics = self.get_metrics(metric_type, since)
            
            if not metrics:
                return {}
            
            values = [m.value for m in metrics]
            
            return {
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest': values[-1] if values else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating statistics: {e}")
            return {}


class EventTracker:
    """Tracks user actions and system events"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._user_actions: deque = deque(maxlen=5000)
        self._system_events: deque = deque(maxlen=5000)
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        
    def track_user_action(self, action_type: str, action_data: Dict[str, Any],
                         user_id: str = "default", session_id: str = "default",
                         duration_ms: float = None, success: bool = True,
                         error_message: str = None) -> None:
        """Track user action"""
        try:
            with self._lock:
                action = UserAction(
                    action_type=action_type,
                    action_data=action_data,
                    user_id=user_id,
                    session_id=session_id,
                    timestamp=datetime.now(),
                    duration_ms=duration_ms,
                    success=success,
                    error_message=error_message
                )
                self._user_actions.append(action)
                
                # Update session info
                if session_id not in self._sessions:
                    self._sessions[session_id] = {
                        'user_id': user_id,
                        'start_time': datetime.now(),
                        'last_activity': datetime.now(),
                        'action_count': 0,
                        'error_count': 0
                    }
                
                session = self._sessions[session_id]
                session['last_activity'] = datetime.now()
                session['action_count'] += 1
                if not success:
                    session['error_count'] += 1
                    
        except Exception as e:
            self.logger.error(f"Error tracking user action: {e}")
    
    def track_system_event(self, event_type: str, severity: str, message: str,
                          component: str, metadata: Dict[str, Any] = None) -> None:
        """Track system event"""
        try:
            with self._lock:
                event = SystemEvent(
                    event_type=event_type,
                    severity=severity,
                    message=message,
                    component=component,
                    timestamp=datetime.now(),
                    metadata=metadata or {}
                )
                self._system_events.append(event)
                
        except Exception as e:
            self.logger.error(f"Error tracking system event: {e}")
    
    def get_user_actions(self, user_id: str = None, session_id: str = None,
                        since: datetime = None) -> List[UserAction]:
        """Get user actions with optional filtering"""
        try:
            with self._lock:
                actions = list(self._user_actions)
                
                if user_id:
                    actions = [a for a in actions if a.user_id == user_id]
                
                if session_id:
                    actions = [a for a in actions if a.session_id == session_id]
                
                if since:
                    actions = [a for a in actions if a.timestamp >= since]
                
                return actions
                
        except Exception as e:
            self.logger.error(f"Error getting user actions: {e}")
            return []
    
    def get_system_events(self, event_type: str = None, severity: str = None,
                         component: str = None, since: datetime = None) -> List[SystemEvent]:
        """Get system events with optional filtering"""
        try:
            with self._lock:
                events = list(self._system_events)
                
                if event_type:
                    events = [e for e in events if e.event_type == event_type]
                
                if severity:
                    events = [e for e in events if e.severity == severity]
                
                if component:
                    events = [e for e in events if e.component == component]
                
                if since:
                    events = [e for e in events if e.timestamp >= since]
                
                return events
                
        except Exception as e:
            self.logger.error(f"Error getting system events: {e}")
            return []
    
    def get_session_info(self, session_id: str = None) -> Dict[str, Any]:
        """Get session information"""
        try:
            with self._lock:
                if session_id:
                    return self._sessions.get(session_id, {})
                return dict(self._sessions)
                
        except Exception as e:
            self.logger.error(f"Error getting session info: {e}")
            return {}


class DatabaseManager:
    """Manages persistent storage of analytics data"""
    
    def __init__(self, db_path: str = "data/analytics.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize database"""
        try:
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Create tables
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT,
                        timestamp DATETIME NOT NULL,
                        tags TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action_type TEXT NOT NULL,
                        action_data TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        duration_ms REAL,
                        success BOOLEAN NOT NULL,
                        error_message TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        component TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        metadata TEXT
                    )
                ''')
                
                # Create indexes
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_type_time ON metrics(metric_type, timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_actions_user_time ON user_actions(user_id, timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type_time ON system_events(event_type, timestamp)')
                
                conn.commit()
                conn.close()
                
                self._initialized = True
                self.logger.info("Analytics database initialized")
                return True
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            return False
    
    def save_metrics(self, metrics: List[UsageMetric]) -> bool:
        """Save metrics to database"""
        try:
            if not self._initialized:
                return False
                
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                for metric in metrics:
                    cursor.execute('''
                        INSERT INTO metrics (metric_type, value, unit, timestamp, tags)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        metric.metric_type,
                        metric.value,
                        metric.unit,
                        metric.timestamp.isoformat(),
                        json.dumps(metric.tags)
                    ))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
            return False
    
    def save_user_actions(self, actions: List[UserAction]) -> bool:
        """Save user actions to database"""
        try:
            if not self._initialized:
                return False
                
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                for action in actions:
                    cursor.execute('''
                        INSERT INTO user_actions (action_type, action_data, user_id, session_id, 
                                                timestamp, duration_ms, success, error_message)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        action.action_type,
                        json.dumps(action.action_data),
                        action.user_id,
                        action.session_id,
                        action.timestamp.isoformat(),
                        action.duration_ms,
                        action.success,
                        action.error_message
                    ))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving user actions: {e}")
            return False
    
    def save_system_events(self, events: List[SystemEvent]) -> bool:
        """Save system events to database"""
        try:
            if not self._initialized:
                return False
                
            with self._lock:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                for event in events:
                    cursor.execute('''
                        INSERT INTO system_events (event_type, severity, message, component, 
                                                 timestamp, metadata)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        event.event_type,
                        event.severity,
                        event.message,
                        event.component,
                        event.timestamp.isoformat(),
                        json.dumps(event.metadata)
                    ))
                
                conn.commit()
                conn.close()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving system events: {e}")
            return False


class ReportGenerator:
    """Generates analytics reports"""
    
    def __init__(self, metrics_collector: MetricsCollector, event_tracker: EventTracker):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = metrics_collector
        self.event_tracker = event_tracker
        
    def generate_usage_report(self, period_hours: int = 24) -> AnalyticsReport:
        """Generate usage report"""
        try:
            period_start = datetime.now() - timedelta(hours=period_hours)
            period_end = datetime.now()
            
            # Get user actions
            actions = self.event_tracker.get_user_actions(since=period_start)
            
            # Get metrics
            voice_commands = len([a for a in actions if a.action_type == "voice_command"])
            system_commands = len([a for a in actions if a.action_type == "system_command"])
            errors = len([a for a in actions if not a.success])
            
            # Calculate success rate
            total_actions = len(actions)
            success_rate = ((total_actions - errors) / total_actions * 100) if total_actions > 0 else 0
            
            # Get response times
            response_times = [a.duration_ms for a in actions if a.duration_ms is not None]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            data = {
                "period_hours": period_hours,
                "total_actions": total_actions,
                "voice_commands": voice_commands,
                "system_commands": system_commands,
                "errors": errors,
                "success_rate": round(success_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "actions_per_hour": round(total_actions / period_hours, 2) if period_hours > 0 else 0
            }
            
            return AnalyticsReport(
                report_type="usage",
                title=f"Usage Report - Last {period_hours} Hours",
                data=data,
                generated_at=datetime.now(),
                period_start=period_start,
                period_end=period_end
            )
            
        except Exception as e:
            self.logger.error(f"Error generating usage report: {e}")
            return AnalyticsReport(
                report_type="usage",
                title="Usage Report - Error",
                data={"error": str(e)},
                generated_at=datetime.now(),
                period_start=datetime.now(),
                period_end=datetime.now()
            )
    
    def generate_performance_report(self, period_hours: int = 24) -> AnalyticsReport:
        """Generate performance report"""
        try:
            period_start = datetime.now() - timedelta(hours=period_hours)
            period_end = datetime.now()
            
            # Get performance metrics
            cpu_stats = self.metrics_collector.calculate_statistics("cpu_percent", period_hours)
            memory_stats = self.metrics_collector.calculate_statistics("memory_percent", period_hours)
            response_stats = self.metrics_collector.calculate_statistics("response_time_ms", period_hours)
            
            data = {
                "period_hours": period_hours,
                "cpu_usage": cpu_stats,
                "memory_usage": memory_stats,
                "response_times": response_stats
            }
            
            return AnalyticsReport(
                report_type="performance",
                title=f"Performance Report - Last {period_hours} Hours",
                data=data,
                generated_at=datetime.now(),
                period_start=period_start,
                period_end=period_end
            )
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return AnalyticsReport(
                report_type="performance",
                title="Performance Report - Error",
                data={"error": str(e)},
                generated_at=datetime.now(),
                period_start=datetime.now(),
                period_end=datetime.now()
            )
    
    def generate_security_report(self, period_hours: int = 24) -> AnalyticsReport:
        """Generate security report"""
        try:
            period_start = datetime.now() - timedelta(hours=period_hours)
            period_end = datetime.now()
            
            # Get security events
            security_events = self.event_tracker.get_system_events(
                component="security", since=period_start
            )
            
            # Count by severity
            severity_counts = defaultdict(int)
            for event in security_events:
                severity_counts[event.severity] += 1
            
            # Get blocked commands
            blocked_commands = len([e for e in security_events 
                                  if e.event_type == "command_blocked"])
            
            data = {
                "period_hours": period_hours,
                "total_security_events": len(security_events),
                "severity_counts": dict(severity_counts),
                "blocked_commands": blocked_commands,
                "security_events": [asdict(e) for e in security_events[-10:]]  # Last 10 events
            }
            
            return AnalyticsReport(
                report_type="security",
                title=f"Security Report - Last {period_hours} Hours",
                data=data,
                generated_at=datetime.now(),
                period_start=period_start,
                period_end=period_end
            )
            
        except Exception as e:
            self.logger.error(f"Error generating security report: {e}")
            return AnalyticsReport(
                report_type="security",
                title="Security Report - Error",
                data={"error": str(e)},
                generated_at=datetime.now(),
                period_start=datetime.now(),
                period_end=datetime.now()
            )


class AnalyticsManager:
    """
    Main analytics management system
    Collects metrics, tracks events, generates reports, and provides analytics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_collector = MetricsCollector()
        self.event_tracker = EventTracker()
        self.database_manager = DatabaseManager()
        self.report_generator = ReportGenerator(self.metrics_collector, self.event_tracker)
        self._running = False
        self._persistence_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.persistence_interval = 300  # 5 minutes
        self.cleanup_interval = 3600  # 1 hour
        self.data_retention_days = 30
        
    async def initialize(self) -> bool:
        """Initialize analytics manager"""
        try:
            self.logger.info("Initializing analytics manager")
            
            # Initialize database
            if not self.database_manager.initialize():
                self.logger.error("Failed to initialize analytics database")
                return False
            
            # Start background tasks
            await self._start_background_tasks()
            
            self._running = True
            self.logger.info("Analytics manager initialized successfully")
            
            # Track initialization
            self.track_system_event("analytics_manager_initialized", "info", 
                                   "Analytics manager started", "analytics")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize analytics manager: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown analytics manager"""
        try:
            self.logger.info("Shutting down analytics manager")
            
            self._running = False
            
            # Stop background tasks
            if self._persistence_task:
                self._persistence_task.cancel()
                try:
                    await self._persistence_task
                except asyncio.CancelledError:
                    pass
            
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            
            # Final data persistence
            await self._persist_data()
            
            self.logger.info("Analytics manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during analytics manager shutdown: {e}")
    
    async def _start_background_tasks(self) -> None:
        """Start background tasks"""
        self._persistence_task = asyncio.create_task(self._persistence_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info("Analytics background tasks started")
    
    async def _persistence_loop(self) -> None:
        """Periodic data persistence loop"""
        while self._running:
            try:
                await self._persist_data()
                await asyncio.sleep(self.persistence_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in persistence loop: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_loop(self) -> None:
        """Periodic data cleanup loop"""
        while self._running:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)
    
    async def _persist_data(self) -> None:
        """Persist current data to database"""
        try:
            # Get current data
            metrics = self.metrics_collector.get_metrics()
            actions = self.event_tracker.get_user_actions()
            events = self.event_tracker.get_system_events()
            
            # Save to database
            if metrics:
                self.database_manager.save_metrics(metrics)
            
            if actions:
                self.database_manager.save_user_actions(actions)
            
            if events:
                self.database_manager.save_system_events(events)
            
            self.logger.debug(f"Persisted {len(metrics)} metrics, {len(actions)} actions, {len(events)} events")
            
        except Exception as e:
            self.logger.error(f"Error persisting data: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Cleanup old data beyond retention period"""
        try:
            # This would implement cleanup of old database records
            # For now, we just log the operation
            self.logger.debug("Performing data cleanup")
            
        except Exception as e:
            self.logger.error(f"Error during data cleanup: {e}")
    
    # Public API methods
    
    def record_metric(self, metric_type: str, value: float, unit: str = "", 
                     tags: Dict[str, str] = None) -> None:
        """Record a metric"""
        self.metrics_collector.record_metric(metric_type, value, unit, tags)
    
    def track_user_action(self, action_type: str, action_data: Dict[str, Any],
                         user_id: str = "default", session_id: str = "default",
                         duration_ms: float = None, success: bool = True,
                         error_message: str = None) -> None:
        """Track user action"""
        self.event_tracker.track_user_action(
            action_type, action_data, user_id, session_id,
            duration_ms, success, error_message
        )
    
    def track_system_event(self, event_type: str, severity: str, message: str,
                          component: str, metadata: Dict[str, Any] = None) -> None:
        """Track system event"""
        self.event_tracker.track_system_event(
            event_type, severity, message, component, metadata
        )
    
    def generate_report(self, report_type: str, period_hours: int = 24) -> AnalyticsReport:
        """Generate analytics report"""
        if report_type == "usage":
            return self.report_generator.generate_usage_report(period_hours)
        elif report_type == "performance":
            return self.report_generator.generate_performance_report(period_hours)
        elif report_type == "security":
            return self.report_generator.generate_security_report(period_hours)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            # Get recent data
            recent_actions = self.event_tracker.get_user_actions(
                since=datetime.now() - timedelta(hours=24)
            )
            recent_events = self.event_tracker.get_system_events(
                since=datetime.now() - timedelta(hours=24)
            )
            
            # Get session info
            sessions = self.event_tracker.get_session_info()
            
            return {
                "status": "running" if self._running else "stopped",
                "data_points": {
                    "total_metrics": len(self.metrics_collector._metrics),
                    "total_actions": len(self.event_tracker._user_actions),
                    "total_events": len(self.event_tracker._system_events),
                    "recent_actions_24h": len(recent_actions),
                    "recent_events_24h": len(recent_events),
                    "active_sessions": len(sessions)
                },
                "configuration": {
                    "persistence_interval": self.persistence_interval,
                    "cleanup_interval": self.cleanup_interval,
                    "data_retention_days": self.data_retention_days
                },
                "database_initialized": self.database_manager._initialized
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analytics summary: {e}")
            return {"status": "error", "error": str(e)}


# Global analytics manager instance
_analytics_manager: Optional[AnalyticsManager] = None


def get_analytics_manager() -> AnalyticsManager:
    """Get global analytics manager instance"""
    global _analytics_manager
    if _analytics_manager is None:
        _analytics_manager = AnalyticsManager()
    return _analytics_manager


async def cleanup_analytics_manager() -> None:
    """Cleanup global analytics manager"""
    global _analytics_manager
    if _analytics_manager is not None:
        await _analytics_manager.shutdown()
        _analytics_manager = None
