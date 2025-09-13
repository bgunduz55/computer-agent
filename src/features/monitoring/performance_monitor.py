"""
Performance Monitor for JARVIS Computer Assistant

Monitors system performance, resource usage, and execution metrics.
"""

import psutil
import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import gc

@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int
    open_files: int
    thread_count: int
    process_count: int
    load_average: List[float] = field(default_factory=list)
    gc_stats: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

class PerformanceMonitor:
    """Monitors system and application performance"""
    
    def __init__(self, monitoring_interval: float = 5.0):
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitoring_task = None
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history = 1000
        self._lock = threading.Lock()
        self._start_time = time.time()
        self._last_network_stats = None
        self._last_disk_stats = None
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = await self._collect_metrics()
                self._store_metrics(metrics)
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_available_mb = memory.available / (1024 * 1024)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024 * 1024 * 1024)
        
        # Network usage
        network_sent_mb, network_recv_mb = self._get_network_usage()
        
        # Process information
        process = psutil.Process()
        active_connections = len(process.connections())
        open_files = len(process.open_files())
        thread_count = process.num_threads()
        
        # System information
        process_count = len(psutil.pids())
        load_average = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else []
        
        # Garbage collection stats
        gc_stats = {
            "collections": gc.get_count(),
            "threshold": gc.get_threshold(),
            "stats": gc.get_stats()
        }
        
        # Custom metrics
        custom_metrics = {
            "uptime": time.time() - self._start_time,
            "monitoring_interval": self.monitoring_interval
        }
        
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            active_connections=active_connections,
            open_files=open_files,
            thread_count=thread_count,
            process_count=process_count,
            load_average=list(load_average),
            gc_stats=gc_stats,
            custom_metrics=custom_metrics
        )
    
    def _get_network_usage(self) -> tuple[float, float]:
        """Get network usage since last check"""
        try:
            current_stats = psutil.net_io_counters()
            
            if self._last_network_stats is None:
                self._last_network_stats = current_stats
                return 0.0, 0.0
            
            # Calculate difference
            sent_bytes = current_stats.bytes_sent - self._last_network_stats.bytes_sent
            recv_bytes = current_stats.bytes_recv - self._last_network_stats.bytes_recv
            
            # Update last stats
            self._last_network_stats = current_stats
            
            return sent_bytes / (1024 * 1024), recv_bytes / (1024 * 1024)
        except:
            return 0.0, 0.0
    
    def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics in history"""
        with self._lock:
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history = self.metrics_history[-self.max_history:]
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get most recent performance metrics"""
        with self._lock:
            return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, limit: int = 100) -> List[PerformanceMetrics]:
        """Get recent performance metrics history"""
        with self._lock:
            return self.metrics_history[-limit:] if self.metrics_history else []
    
    def get_average_metrics(self, window_minutes: int = 5) -> Optional[PerformanceMetrics]:
        """Get average metrics over a time window"""
        with self._lock:
            if not self.metrics_history:
                return None
            
            cutoff_time = time.time() - (window_minutes * 60)
            recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return None
            
            # Calculate averages
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory_percent = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory_used = sum(m.memory_used_mb for m in recent_metrics) / len(recent_metrics)
            avg_memory_available = sum(m.memory_available_mb for m in recent_metrics) / len(recent_metrics)
            avg_disk_usage = sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics)
            avg_disk_free = sum(m.disk_free_gb for m in recent_metrics) / len(recent_metrics)
            avg_network_sent = sum(m.network_sent_mb for m in recent_metrics) / len(recent_metrics)
            avg_network_recv = sum(m.network_recv_mb for m in recent_metrics) / len(recent_metrics)
            avg_connections = sum(m.active_connections for m in recent_metrics) / len(recent_metrics)
            avg_open_files = sum(m.open_files for m in recent_metrics) / len(recent_metrics)
            avg_thread_count = sum(m.thread_count for m in recent_metrics) / len(recent_metrics)
            avg_process_count = sum(m.process_count for m in recent_metrics) / len(recent_metrics)
            
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=avg_cpu,
                memory_percent=avg_memory_percent,
                memory_used_mb=avg_memory_used,
                memory_available_mb=avg_memory_available,
                disk_usage_percent=avg_disk_usage,
                disk_free_gb=avg_disk_free,
                network_sent_mb=avg_network_sent,
                network_recv_mb=avg_network_recv,
                active_connections=int(avg_connections),
                open_files=int(avg_open_files),
                thread_count=int(avg_thread_count),
                process_count=int(avg_process_count),
                load_average=[],
                gc_stats={},
                custom_metrics={"window_minutes": window_minutes, "sample_count": len(recent_metrics)}
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        current = self.get_current_metrics()
        if not current:
            return {"status": "no_data"}
        
        # Get recent averages
        avg_5min = self.get_average_metrics(5)
        avg_15min = self.get_average_metrics(15)
        
        summary = {
            "status": "healthy",
            "current": {
                "cpu_percent": current.cpu_percent,
                "memory_percent": current.memory_percent,
                "disk_usage_percent": current.disk_usage_percent,
                "active_connections": current.active_connections,
                "thread_count": current.thread_count
            },
            "averages": {
                "5min": {
                    "cpu_percent": avg_5min.cpu_percent if avg_5min else None,
                    "memory_percent": avg_5min.memory_percent if avg_5min else None,
                    "disk_usage_percent": avg_5min.disk_usage_percent if avg_5min else None
                },
                "15min": {
                    "cpu_percent": avg_15min.cpu_percent if avg_15min else None,
                    "memory_percent": avg_15min.memory_percent if avg_15min else None,
                    "disk_usage_percent": avg_15min.disk_usage_percent if avg_15min else None
                }
            },
            "uptime": current.custom_metrics.get("uptime", 0),
            "monitoring_active": self.is_monitoring
        }
        
        # Add health status
        if current.cpu_percent > 90:
            summary["status"] = "warning"
            summary["alerts"] = ["High CPU usage"]
        
        if current.memory_percent > 90:
            summary["status"] = "warning"
            summary["alerts"] = summary.get("alerts", []) + ["High memory usage"]
        
        if current.disk_usage_percent > 90:
            summary["status"] = "warning"
            summary["alerts"] = summary.get("alerts", []) + ["High disk usage"]
        
        return summary
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        current = self.get_current_metrics()
        if not current:
            return False
        
        return (current.cpu_percent < 90 and 
                current.memory_percent < 90 and 
                current.disk_usage_percent < 90)

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
