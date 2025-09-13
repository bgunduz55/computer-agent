"""
System Monitor Plugin for JARVIS Computer Assistant
Provides real-time system monitoring and alerts
"""

import asyncio
import logging
import psutil
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..base_plugin import BasePlugin, PluginInfo, PluginType, PluginConfig


@dataclass
class SystemAlert:
    """System alert data"""
    type: str
    message: str
    severity: str  # low, medium, high, critical
    timestamp: datetime
    value: float
    threshold: float


class SystemMonitorPlugin(BasePlugin):
    """System monitoring plugin"""
    
    PLUGIN_INFO = PluginInfo(
        name="system_monitor",
        version="1.0.0",
        description="Real-time system monitoring and alerts",
        author="JARVIS Team",
        plugin_type=PluginType.SYSTEM,
        dependencies=[],
        config_schema={
            "type": "object",
            "properties": {
                "cpu_threshold": {"type": "number", "default": 80.0, "description": "CPU usage alert threshold (%)"},
                "memory_threshold": {"type": "number", "default": 85.0, "description": "Memory usage alert threshold (%)"},
                "disk_threshold": {"type": "number", "default": 90.0, "description": "Disk usage alert threshold (%)"},
                "temperature_threshold": {"type": "number", "default": 80.0, "description": "CPU temperature alert threshold (°C)"},
                "monitoring_interval": {"type": "number", "default": 30.0, "description": "Monitoring interval in seconds"},
                "enable_alerts": {"type": "boolean", "default": True, "description": "Enable system alerts"}
            }
        }
    )
    
    PRIORITY = 100  # High priority for system monitoring
    
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        self.temperature_threshold = 80.0
        self.monitoring_interval = 30.0
        self.enable_alerts = True
        self._monitoring_task = None
        self._alerts: List[SystemAlert] = []
        self._last_metrics = {}
        self._alert_cooldown = 300  # 5 minutes between same alerts
        
    async def _initialize(self) -> bool:
        """Initialize system monitor plugin"""
        try:
            # Load configuration
            settings = self.config.settings or {}
            self.cpu_threshold = settings.get("cpu_threshold", 80.0)
            self.memory_threshold = settings.get("memory_threshold", 85.0)
            self.disk_threshold = settings.get("disk_threshold", 90.0)
            self.temperature_threshold = settings.get("temperature_threshold", 80.0)
            self.monitoring_interval = settings.get("monitoring_interval", 30.0)
            self.enable_alerts = settings.get("enable_alerts", True)
            
            self.logger.info("System monitor plugin initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system monitor plugin: {e}")
            return False
    
    async def _cleanup(self) -> None:
        """Cleanup system monitor plugin"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self._alerts.clear()
        self.logger.info("System monitor plugin cleaned up")
    
    async def _start(self) -> bool:
        """Start system monitoring"""
        try:
            if self.enable_alerts:
                self._monitoring_task = asyncio.create_task(self._monitoring_loop())
                self.logger.info("System monitoring started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start system monitoring: {e}")
            return False
    
    async def _stop(self) -> None:
        """Stop system monitoring"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
        
        self.logger.info("System monitoring stopped")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while True:
            try:
                await self._check_system_metrics()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retry
    
    async def _check_system_metrics(self) -> None:
        """Check system metrics and generate alerts"""
        try:
            # Get current metrics
            metrics = await self.get_system_metrics()
            self._last_metrics = metrics
            
            if not self.enable_alerts:
                return
            
            # Check CPU usage
            cpu_usage = metrics.get("cpu_percent", 0)
            if cpu_usage > self.cpu_threshold:
                await self._create_alert(
                    "cpu_high",
                    f"High CPU usage: {cpu_usage:.1f}%",
                    "high" if cpu_usage > 95 else "medium",
                    cpu_usage,
                    self.cpu_threshold
                )
            
            # Check memory usage
            memory_usage = metrics.get("memory_percent", 0)
            if memory_usage > self.memory_threshold:
                await self._create_alert(
                    "memory_high",
                    f"High memory usage: {memory_usage:.1f}%",
                    "high" if memory_usage > 95 else "medium",
                    memory_usage,
                    self.memory_threshold
                )
            
            # Check disk usage
            disk_usage = metrics.get("disk_percent", 0)
            if disk_usage > self.disk_threshold:
                await self._create_alert(
                    "disk_high",
                    f"High disk usage: {disk_usage:.1f}%",
                    "high" if disk_usage > 95 else "medium",
                    disk_usage,
                    self.disk_threshold
                )
            
            # Check CPU temperature (if available)
            cpu_temp = metrics.get("cpu_temperature")
            if cpu_temp and cpu_temp > self.temperature_threshold:
                await self._create_alert(
                    "temperature_high",
                    f"High CPU temperature: {cpu_temp:.1f}°C",
                    "critical" if cpu_temp > 90 else "high",
                    cpu_temp,
                    self.temperature_threshold
                )
                
        except Exception as e:
            self.logger.error(f"Error checking system metrics: {e}")
    
    async def _create_alert(self, alert_type: str, message: str, severity: str, 
                          value: float, threshold: float) -> None:
        """Create a system alert"""
        try:
            # Check cooldown to avoid spam
            now = datetime.now()
            recent_alerts = [
                alert for alert in self._alerts
                if (alert.type == alert_type and 
                    (now - alert.timestamp).total_seconds() < self._alert_cooldown)
            ]
            
            if recent_alerts:
                return  # Skip if recent alert of same type exists
            
            # Create new alert
            alert = SystemAlert(
                type=alert_type,
                message=message,
                severity=severity,
                timestamp=now,
                value=value,
                threshold=threshold
            )
            
            self._alerts.append(alert)
            
            # Keep only last 100 alerts
            if len(self._alerts) > 100:
                self._alerts = self._alerts[-100:]
            
            # Emit alert event
            self.emit_event("system_alert", {
                "type": alert_type,
                "message": message,
                "severity": severity,
                "value": value,
                "threshold": threshold
            })
            
            self.logger.warning(f"System alert: {message}")
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            processes = len(psutil.pids())
            
            # Temperature (if available)
            cpu_temperature = None
            try:
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if 'core' in name.lower() or 'cpu' in name.lower():
                                cpu_temperature = entries[0].current if entries else None
                                break
            except Exception:
                pass  # Temperature not available on this system
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "cpu_count": cpu_count,
                "cpu_frequency": cpu_freq.current if cpu_freq else None,
                "cpu_temperature": cpu_temperature,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_percent": swap.percent,
                "disk_total": disk.total,
                "disk_used": disk.used,
                "disk_free": disk.free,
                "disk_percent": (disk.used / disk.total) * 100,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "network_packets_sent": network.packets_sent,
                "network_packets_recv": network.packets_recv,
                "process_count": processes,
                "uptime": time.time() - psutil.boot_time()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {}
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle system monitoring voice commands"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ["system", "sistem", "performance", "performans", "cpu", "memory", "ram"]):
            try:
                metrics = await self.get_system_metrics()
                return self._format_system_status(metrics)
                
            except Exception as e:
                self.logger.error(f"Error handling system command: {e}")
                return "Sorry, I couldn't get system information right now."
        
        return None
    
    def _format_system_status(self, metrics: Dict[str, Any]) -> str:
        """Format system metrics for voice response"""
        try:
            cpu_percent = metrics.get("cpu_percent", 0)
            memory_percent = metrics.get("memory_percent", 0)
            disk_percent = metrics.get("disk_percent", 0)
            process_count = metrics.get("process_count", 0)
            
            response = f"System status: CPU usage is {cpu_percent:.1f}%, "
            response += f"memory usage is {memory_percent:.1f}%, "
            response += f"disk usage is {disk_percent:.1f}%, "
            response += f"and {process_count} processes are running."
            
            # Add temperature if available
            cpu_temp = metrics.get("cpu_temperature")
            if cpu_temp:
                response += f" CPU temperature is {cpu_temp:.1f} degrees Celsius."
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error formatting system status: {e}")
            return "System information is available but couldn't be formatted properly."
    
    def get_recent_alerts(self, limit: int = 10) -> List[SystemAlert]:
        """Get recent system alerts"""
        return sorted(self._alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_alerts_by_severity(self, severity: str) -> List[SystemAlert]:
        """Get alerts by severity level"""
        return [alert for alert in self._alerts if alert.severity == severity]
    
    def clear_alerts(self) -> None:
        """Clear all alerts"""
        self._alerts.clear()
        self.logger.info("All system alerts cleared")
    
    def get_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "system status",
            "sistem durumu",
            "performance",
            "performans",
            "cpu usage",
            "memory usage",
            "ram usage",
            "disk usage",
            "system alerts",
            "sistem uyarıları"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            "system_monitoring",
            "performance_metrics",
            "alert_system",
            "resource_tracking",
            "temperature_monitoring"
        ]
