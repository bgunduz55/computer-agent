"""
Metrics Collector for JARVIS Computer Assistant

Collects and aggregates various metrics for monitoring and observability.
"""

import time
import threading
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
import asyncio

class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"

@dataclass
class MetricValue:
    """A metric value with metadata"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class MetricSnapshot:
    """A snapshot of metrics at a point in time"""
    timestamp: float
    metrics: Dict[str, Any]
    summary: Dict[str, Any]

class MetricsCollector:
    """Collects and aggregates metrics for monitoring"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.rates: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._start_time = time.time()
    
    def increment_counter(self, name: str, value: float = 1.0, 
                        tags: Dict[str, str] = None, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        with self._lock:
            self.counters[name] += value
            self._record_metric(MetricValue(
                name=name,
                value=self.counters[name],
                metric_type=MetricType.COUNTER,
                timestamp=time.time(),
                tags=tags or {},
                labels=labels or {}
            ))
    
    def set_gauge(self, name: str, value: float, 
                 tags: Dict[str, str] = None, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        with self._lock:
            self.gauges[name] = value
            self._record_metric(MetricValue(
                name=name,
                value=value,
                metric_type=MetricType.GAUGE,
                timestamp=time.time(),
                tags=tags or {},
                labels=labels or {}
            ))
    
    def record_histogram(self, name: str, value: float,
                        tags: Dict[str, str] = None, labels: Dict[str, str] = None):
        """Record a histogram value"""
        with self._lock:
            self.histograms[name].append(value)
            # Keep only recent values
            if len(self.histograms[name]) > self.max_history:
                self.histograms[name] = self.histograms[name][-self.max_history:]
            
            self._record_metric(MetricValue(
                name=name,
                value=value,
                metric_type=MetricType.HISTOGRAM,
                timestamp=time.time(),
                tags=tags or {},
                labels=labels or {}
            ))
    
    def record_timer(self, name: str, duration: float,
                    tags: Dict[str, str] = None, labels: Dict[str, str] = None):
        """Record a timer duration"""
        with self._lock:
            self.timers[name].append(duration)
            # Keep only recent values
            if len(self.timers[name]) > self.max_history:
                self.timers[name] = self.timers[name][-self.max_history:]
            
            self._record_metric(MetricValue(
                name=name,
                value=duration,
                metric_type=MetricType.TIMER,
                timestamp=time.time(),
                tags=tags or {},
                labels=labels or {}
            ))
    
    def record_rate(self, name: str, value: float,
                   tags: Dict[str, str] = None, labels: Dict[str, str] = None):
        """Record a rate metric"""
        with self._lock:
            self.rates[name].append(value)
            # Keep only recent values
            if len(self.rates[name]) > self.max_history:
                self.rates[name] = self.rates[name][-self.max_history:]
            
            self._record_metric(MetricValue(
                name=name,
                value=value,
                metric_type=MetricType.RATE,
                timestamp=time.time(),
                tags=tags or {},
                labels=labels or {}
            ))
    
    def _record_metric(self, metric: MetricValue):
        """Record a metric value"""
        self.metrics[metric.name].append(metric)
    
    def get_counter(self, name: str) -> float:
        """Get counter value"""
        with self._lock:
            return self.counters.get(name, 0.0)
    
    def get_gauge(self, name: str) -> float:
        """Get gauge value"""
        with self._lock:
            return self.gauges.get(name, 0.0)
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics"""
        with self._lock:
            values = self.histograms.get(name, [])
            if not values:
                return {}
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "median": sorted(values)[len(values) // 2],
                "p95": sorted(values)[int(len(values) * 0.95)],
                "p99": sorted(values)[int(len(values) * 0.99)]
            }
    
    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """Get timer statistics"""
        with self._lock:
            values = self.timers.get(name, [])
            if not values:
                return {}
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "median": sorted(values)[len(values) // 2],
                "p95": sorted(values)[int(len(values) * 0.95)],
                "p99": sorted(values)[int(len(values) * 0.99)]
            }
    
    def get_rate_stats(self, name: str, window_seconds: int = 60) -> Dict[str, float]:
        """Get rate statistics for a time window"""
        with self._lock:
            values = self.rates.get(name, [])
            if not values:
                return {}
            
            # Filter values within time window
            cutoff_time = time.time() - window_seconds
            recent_values = [v for v in values if v >= cutoff_time]
            
            if not recent_values:
                return {"count": 0, "rate": 0.0}
            
            return {
                "count": len(recent_values),
                "rate": len(recent_values) / window_seconds,
                "total": sum(recent_values)
            }
    
    def get_snapshot(self) -> MetricSnapshot:
        """Get current metrics snapshot"""
        with self._lock:
            snapshot = {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {name: self.get_histogram_stats(name) for name in self.histograms},
                "timers": {name: self.get_timer_stats(name) for name in self.timers},
                "rates": {name: self.get_rate_stats(name) for name in self.rates}
            }
            
            # Calculate summary
            summary = {
                "total_metrics": len(self.metrics),
                "uptime": time.time() - self._start_time,
                "timestamp": time.time()
            }
            
            return MetricSnapshot(
                timestamp=time.time(),
                metrics=snapshot,
                summary=summary
            )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics"""
        snapshot = self.get_snapshot()
        return {
            "timestamp": snapshot.timestamp,
            "uptime": snapshot.summary["uptime"],
            "total_metrics": snapshot.summary["total_metrics"],
            "counters": snapshot.metrics["counters"],
            "gauges": snapshot.metrics["gauges"],
            "histograms": snapshot.metrics["histograms"],
            "timers": snapshot.metrics["timers"],
            "rates": snapshot.metrics["rates"]
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format"""
        summary = self.get_metrics_summary()
        
        if format == "json":
            return json.dumps(summary, indent=2)
        elif format == "prometheus":
            return self._export_prometheus(summary)
        else:
            return str(summary)
    
    def _export_prometheus(self, summary: Dict[str, Any]) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Add metadata
        lines.append(f"# HELP jarvis_uptime_seconds Total uptime in seconds")
        lines.append(f"# TYPE jarvis_uptime_seconds gauge")
        lines.append(f"jarvis_uptime_seconds {summary['uptime']}")
        
        # Export counters
        for name, value in summary["counters"].items():
            lines.append(f"# HELP jarvis_counter_{name} Counter metric")
            lines.append(f"# TYPE jarvis_counter_{name} counter")
            lines.append(f"jarvis_counter_{name} {value}")
        
        # Export gauges
        for name, value in summary["gauges"].items():
            lines.append(f"# HELP jarvis_gauge_{name} Gauge metric")
            lines.append(f"# TYPE jarvis_gauge_{name} gauge")
            lines.append(f"jarvis_gauge_{name} {value}")
        
        return "\n".join(lines)
    
    def reset_metrics(self):
        """Reset all metrics"""
        with self._lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.timers.clear()
            self.rates.clear()
            self.metrics.clear()
            self._start_time = time.time()

# Global metrics collector instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
