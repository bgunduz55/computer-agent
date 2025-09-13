"""
Alert Manager for JARVIS Computer Assistant

Manages alerts, notifications, and alerting rules for monitoring.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Alert definition"""
    id: str
    title: str
    message: str
    level: AlertLevel
    source: str
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None
    metadata: Dict[str, Any] = None
    tags: List[str] = None

@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    condition: Callable
    level: AlertLevel
    message_template: str
    cooldown_seconds: int = 300  # 5 minutes default
    enabled: bool = True
    tags: List[str] = None

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.rules: Dict[str, AlertRule] = {}
        self.notification_handlers: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        self._last_alert_times: Dict[str, float] = {}
        self._alert_counter = 0
    
    def register_rule(self, rule: AlertRule):
        """Register an alert rule"""
        self.rules[rule.name] = rule
        self.logger.info(f"Registered alert rule: {rule.name}")
    
    def add_notification_handler(self, handler: Callable):
        """Add a notification handler"""
        self.notification_handlers.append(handler)
        self.logger.info(f"Added notification handler: {handler.__name__}")
    
    async def create_alert(self, title: str, message: str, level: AlertLevel,
                          source: str, metadata: Dict[str, Any] = None,
                          tags: List[str] = None) -> Alert:
        """Create a new alert"""
        alert_id = f"alert_{self._alert_counter}_{int(time.time())}"
        self._alert_counter += 1
        
        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            level=level,
            source=source,
            timestamp=time.time(),
            metadata=metadata or {},
            tags=tags or []
        )
        
        self.alerts[alert_id] = alert
        
        # Send notifications
        await self._send_notifications(alert)
        
        self.logger.info(f"Created alert: {alert_id} - {title}")
        return alert
    
    async def resolve_alert(self, alert_id: str, resolution_message: str = None):
        """Resolve an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = time.time()
            
            if resolution_message:
                alert.message += f" | Resolution: {resolution_message}"
            
            self.logger.info(f"Resolved alert: {alert_id}")
            
            # Send resolution notification
            await self._send_notifications(alert, is_resolution=True)
    
    async def check_rules(self, context: Dict[str, Any]):
        """Check all alert rules against current context"""
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown
            last_alert_time = self._last_alert_times.get(rule_name, 0)
            if time.time() - last_alert_time < rule.cooldown_seconds:
                continue
            
            try:
                # Check condition
                if rule.condition(context):
                    # Create alert
                    message = rule.message_template.format(**context)
                    alert = await self.create_alert(
                        title=f"Rule triggered: {rule_name}",
                        message=message,
                        level=rule.level,
                        source="alert_rule",
                        metadata={"rule_name": rule_name},
                        tags=rule.tags or []
                    )
                    
                    # Update last alert time
                    self._last_alert_times[rule_name] = time.time()
                    
            except Exception as e:
                self.logger.error(f"Error checking rule {rule_name}: {e}")
    
    async def _send_notifications(self, alert: Alert, is_resolution: bool = False):
        """Send notifications for an alert"""
        for handler in self.notification_handlers:
            try:
                await handler(alert, is_resolution)
            except Exception as e:
                self.logger.error(f"Error in notification handler {handler.__name__}: {e}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts.values() if alert.level == level]
    
    def get_alerts_by_source(self, source: str) -> List[Alert]:
        """Get alerts by source"""
        return [alert for alert in self.alerts.values() if alert.source == source]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        resolved_alerts = total_alerts - active_alerts
        
        alerts_by_level = {}
        for level in AlertLevel:
            alerts_by_level[level.value] = len(self.get_alerts_by_level(level))
        
        alerts_by_source = {}
        for alert in self.alerts.values():
            source = alert.source
            alerts_by_source[source] = alerts_by_source.get(source, 0) + 1
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "alerts_by_level": alerts_by_level,
            "alerts_by_source": alerts_by_source,
            "rules_count": len(self.rules),
            "notification_handlers": len(self.notification_handlers)
        }
    
    def cleanup_old_alerts(self, max_age_days: int = 30):
        """Clean up old resolved alerts"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        
        alerts_to_remove = []
        for alert_id, alert in self.alerts.items():
            if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_time:
                alerts_to_remove.append(alert_id)
        
        for alert_id in alerts_to_remove:
            del self.alerts[alert_id]
        
        self.logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")
    
    def setup_default_rules(self):
        """Setup default alert rules"""
        # High CPU usage rule
        self.register_rule(AlertRule(
            name="high_cpu_usage",
            condition=lambda ctx: ctx.get("cpu_percent", 0) > 90,
            level=AlertLevel.CRITICAL,
            message_template="High CPU usage detected: {cpu_percent:.1f}%",
            cooldown_seconds=300,
            tags=["cpu", "performance"]
        ))
        
        # High memory usage rule
        self.register_rule(AlertRule(
            name="high_memory_usage",
            condition=lambda ctx: ctx.get("memory_percent", 0) > 90,
            level=AlertLevel.CRITICAL,
            message_template="High memory usage detected: {memory_percent:.1f}%",
            cooldown_seconds=300,
            tags=["memory", "performance"]
        ))
        
        # Low disk space rule
        self.register_rule(AlertRule(
            name="low_disk_space",
            condition=lambda ctx: ctx.get("disk_usage_percent", 0) > 95,
            level=AlertLevel.CRITICAL,
            message_template="Low disk space: {disk_usage_percent:.1f}% used",
            cooldown_seconds=600,
            tags=["disk", "storage"]
        ))
        
        # High error rate rule
        self.register_rule(AlertRule(
            name="high_error_rate",
            condition=lambda ctx: ctx.get("error_rate", 0) > 0.1,
            level=AlertLevel.WARNING,
            message_template="High error rate detected: {error_rate:.2f}%",
            cooldown_seconds=300,
            tags=["errors", "reliability"]
        ))
        
        # Long response time rule
        self.register_rule(AlertRule(
            name="long_response_time",
            condition=lambda ctx: ctx.get("avg_response_time", 0) > 5.0,
            level=AlertLevel.WARNING,
            message_template="Long response time: {avg_response_time:.2f}s",
            cooldown_seconds=300,
            tags=["performance", "response_time"]
        ))

# Default notification handlers
async def console_notification_handler(alert: Alert, is_resolution: bool = False):
    """Console notification handler"""
    status = "RESOLVED" if is_resolution else "ALERT"
    level_emoji = {
        AlertLevel.INFO: "ℹ️",
        AlertLevel.WARNING: "⚠️",
        AlertLevel.ERROR: "❌",
        AlertLevel.CRITICAL: "🚨"
    }
    
    emoji = level_emoji.get(alert.level, "❓")
    print(f"{emoji} [{status}] {alert.title}: {alert.message}")

async def log_notification_handler(alert: Alert, is_resolution: bool = False):
    """Log notification handler"""
    logger = logging.getLogger("alerts")
    
    if is_resolution:
        logger.info(f"Alert resolved: {alert.title}")
    else:
        if alert.level == AlertLevel.CRITICAL:
            logger.critical(f"Critical alert: {alert.title} - {alert.message}")
        elif alert.level == AlertLevel.ERROR:
            logger.error(f"Error alert: {alert.title} - {alert.message}")
        elif alert.level == AlertLevel.WARNING:
            logger.warning(f"Warning alert: {alert.title} - {alert.message}")
        else:
            logger.info(f"Info alert: {alert.title} - {alert.message}")

# Global alert manager instance
_alert_manager = None

def get_alert_manager() -> AlertManager:
    """Get global alert manager instance"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
        _alert_manager.setup_default_rules()
        _alert_manager.add_notification_handler(console_notification_handler)
        _alert_manager.add_notification_handler(log_notification_handler)
    return _alert_manager
