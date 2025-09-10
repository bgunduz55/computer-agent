"""
Performance Manager for JARVIS Computer Assistant
Handles performance monitoring, optimization, and resource management
"""

import asyncio
import logging
import psutil
import threading
import time
import weakref
import gc
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque, defaultdict


@dataclass
class PerformanceMetrics:
    """Performance metrics data"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    active_threads: int
    open_files: int
    network_io_sent: int
    network_io_recv: int
    disk_io_read: int
    disk_io_write: int
    response_time_ms: float = 0.0


@dataclass
class OptimizationResult:
    """Optimization operation result"""
    operation: str
    success: bool
    improvement: float
    description: str
    timestamp: datetime


class PerformanceOptimizer:
    """Performance optimization engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._object_cache = weakref.WeakValueDictionary()
        self._memory_pools = defaultdict(list)
        self._gc_threshold = 0.85  # Trigger GC at 85% memory usage
        
    async def optimize_memory(self) -> OptimizationResult:
        """Optimize memory usage"""
        try:
            start_time = time.time()
            memory_before = psutil.virtual_memory().percent
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear unused object pools
            cleared_pools = 0
            for pool_type, pool in self._memory_pools.items():
                if len(pool) > 100:  # Keep max 100 objects per pool
                    excess = len(pool) - 100
                    del pool[:excess]
                    cleared_pools += excess
            
            # Clear weak references
            self._object_cache.clear()
            
            memory_after = psutil.virtual_memory().percent
            improvement = memory_before - memory_after
            duration = (time.time() - start_time) * 1000
            
            result = OptimizationResult(
                operation="memory_optimization",
                success=True,
                improvement=improvement,
                description=f"Collected {collected} objects, cleared {cleared_pools} pooled objects in {duration:.1f}ms",
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Memory optimization: {result.description}")
            return result
            
        except Exception as e:
            self.logger.error(f"Memory optimization failed: {e}")
            return OptimizationResult(
                operation="memory_optimization",
                success=False,
                improvement=0.0,
                description=f"Failed: {e}",
                timestamp=datetime.now()
            )
    
    async def optimize_cpu(self) -> OptimizationResult:
        """Optimize CPU usage"""
        try:
            start_time = time.time()
            
            # Adjust process priority
            current_process = psutil.Process()
            original_nice = current_process.nice()
            
            # Lower priority slightly to be more system-friendly
            if original_nice < 5:
                current_process.nice(original_nice + 1)
            
            # Optimize asyncio event loop
            loop = asyncio.get_event_loop()
            if hasattr(loop, 'slow_callback_duration'):
                loop.slow_callback_duration = 0.1  # 100ms threshold
            
            duration = (time.time() - start_time) * 1000
            
            result = OptimizationResult(
                operation="cpu_optimization",
                success=True,
                improvement=1.0,  # Relative improvement
                description=f"Adjusted process priority and event loop settings in {duration:.1f}ms",
                timestamp=datetime.now()
            )
            
            self.logger.info(f"CPU optimization: {result.description}")
            return result
            
        except Exception as e:
            self.logger.error(f"CPU optimization failed: {e}")
            return OptimizationResult(
                operation="cpu_optimization",
                success=False,
                improvement=0.0,
                description=f"Failed: {e}",
                timestamp=datetime.now()
            )
    
    async def optimize_io(self) -> OptimizationResult:
        """Optimize I/O operations"""
        try:
            start_time = time.time()
            optimizations = []
            
            # Check and optimize file descriptors
            current_process = psutil.Process()
            open_files = len(current_process.open_files())
            
            if open_files > 50:
                optimizations.append(f"Warning: {open_files} open files")
            
            # Optimize asyncio I/O
            loop = asyncio.get_event_loop()
            if hasattr(loop, '_ready'):
                ready_count = len(loop._ready)
                if ready_count > 100:
                    optimizations.append(f"High asyncio queue: {ready_count}")
            
            duration = (time.time() - start_time) * 1000
            
            result = OptimizationResult(
                operation="io_optimization",
                success=True,
                improvement=0.5,
                description=f"I/O analysis completed in {duration:.1f}ms. {'; '.join(optimizations) if optimizations else 'No issues found'}",
                timestamp=datetime.now()
            )
            
            self.logger.info(f"I/O optimization: {result.description}")
            return result
            
        except Exception as e:
            self.logger.error(f"I/O optimization failed: {e}")
            return OptimizationResult(
                operation="io_optimization",
                success=False,
                improvement=0.0,
                description=f"Failed: {e}",
                timestamp=datetime.now()
            )
    
    def get_object_from_cache(self, key: str) -> Optional[Any]:
        """Get object from weak reference cache"""
        return self._object_cache.get(key)
    
    def cache_object(self, key: str, obj: Any) -> None:
        """Cache object with weak reference"""
        self._object_cache[key] = obj
    
    def get_pooled_object(self, pool_type: str) -> Optional[Any]:
        """Get object from memory pool"""
        pool = self._memory_pools[pool_type]
        return pool.pop() if pool else None
    
    def return_to_pool(self, pool_type: str, obj: Any) -> None:
        """Return object to memory pool"""
        pool = self._memory_pools[pool_type]
        if len(pool) < 100:  # Limit pool size
            pool.append(obj)


class PerformanceManager:
    """
    Main performance management system
    Monitors performance, triggers optimizations, and manages resources
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimizer = PerformanceOptimizer()
        self._metrics_history: deque = deque(maxlen=1000)  # Keep last 1000 metrics
        self._optimization_history: List[OptimizationResult] = []
        self._monitoring_task: Optional[asyncio.Task] = None
        self._optimization_task: Optional[asyncio.Task] = None
        self._running = False
        self._lock = threading.Lock()
        
        # Configuration
        self.monitoring_interval = 30.0  # 30 seconds
        self.optimization_interval = 300.0  # 5 minutes
        self.auto_optimize = True
        self.cpu_threshold = 80.0  # %
        self.memory_threshold = 85.0  # %
        
        # Performance tracking
        self._response_times: deque = deque(maxlen=100)
        self._error_count = 0
        self._last_optimization = None
        
    async def initialize(self) -> bool:
        """Initialize performance manager"""
        try:
            self.logger.info("Initializing performance manager")
            
            # Start monitoring
            await self.start_monitoring()
            
            # Start optimization loop if enabled
            if self.auto_optimize:
                await self.start_optimization_loop()
            
            self._running = True
            self.logger.info("Performance manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance manager: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown performance manager"""
        try:
            self.logger.info("Shutting down performance manager")
            
            self._running = False
            
            # Stop monitoring
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Stop optimization
            if self._optimization_task:
                self._optimization_task.cancel()
                try:
                    await self._optimization_task
                except asyncio.CancelledError:
                    pass
            
            self.logger.info("Performance manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during performance manager shutdown: {e}")
    
    async def start_monitoring(self) -> None:
        """Start performance monitoring"""
        if not self._monitoring_task or self._monitoring_task.done():
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            self.logger.info("Performance monitoring started")
    
    async def start_optimization_loop(self) -> None:
        """Start automatic optimization loop"""
        if not self._optimization_task or self._optimization_task.done():
            self._optimization_task = asyncio.create_task(self._optimization_loop())
            self.logger.info("Automatic optimization started")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self._running:
            try:
                metrics = await self.collect_metrics()
                self._metrics_history.append(metrics)
                
                # Check for performance issues
                await self._check_performance_thresholds(metrics)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _optimization_loop(self) -> None:
        """Automatic optimization loop"""
        while self._running:
            try:
                if self.auto_optimize:
                    await self.run_optimization()
                
                await asyncio.sleep(self.optimization_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(30)
    
    async def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Process metrics
            current_process = psutil.Process()
            process_memory = current_process.memory_info()
            
            # Network I/O
            network_io = psutil.net_io_counters()
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            
            # Thread count
            thread_count = threading.active_count()
            
            # Open files
            try:
                open_files = len(current_process.open_files())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                open_files = 0
            
            # Average response time
            avg_response_time = 0.0
            if self._response_times:
                avg_response_time = sum(self._response_times) / len(self._response_times)
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=process_memory.rss / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                active_threads=thread_count,
                open_files=open_files,
                network_io_sent=network_io.bytes_sent if network_io else 0,
                network_io_recv=network_io.bytes_recv if network_io else 0,
                disk_io_read=disk_io.read_bytes if disk_io else 0,
                disk_io_write=disk_io.write_bytes if disk_io else 0,
                response_time_ms=avg_response_time
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0,
                memory_percent=0,
                memory_used_mb=0,
                memory_available_mb=0,
                active_threads=0,
                open_files=0,
                network_io_sent=0,
                network_io_recv=0,
                disk_io_read=0,
                disk_io_write=0
            )
    
    async def _check_performance_thresholds(self, metrics: PerformanceMetrics) -> None:
        """Check if performance thresholds are exceeded"""
        issues = []
        
        if metrics.cpu_percent > self.cpu_threshold:
            issues.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > self.memory_threshold:
            issues.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.active_threads > 50:
            issues.append(f"High thread count: {metrics.active_threads}")
        
        if metrics.open_files > 100:
            issues.append(f"Many open files: {metrics.open_files}")
        
        if issues:
            self.logger.warning(f"Performance issues detected: {'; '.join(issues)}")
            
            # Trigger immediate optimization if auto_optimize is enabled
            if self.auto_optimize:
                await self.run_optimization()
    
    async def run_optimization(self) -> List[OptimizationResult]:
        """Run performance optimization"""
        try:
            with self._lock:
                self.logger.info("Running performance optimization")
                results = []
                
                # Memory optimization
                memory_result = await self.optimizer.optimize_memory()
                results.append(memory_result)
                
                # CPU optimization
                cpu_result = await self.optimizer.optimize_cpu()
                results.append(cpu_result)
                
                # I/O optimization
                io_result = await self.optimizer.optimize_io()
                results.append(io_result)
                
                # Store results
                self._optimization_history.extend(results)
                
                # Keep only last 100 optimizations
                if len(self._optimization_history) > 100:
                    self._optimization_history = self._optimization_history[-100:]
                
                self._last_optimization = datetime.now()
                
                # Log summary
                successful = sum(1 for r in results if r.success)
                total_improvement = sum(r.improvement for r in results)
                
                self.logger.info(f"Optimization complete: {successful}/{len(results)} successful, total improvement: {total_improvement:.2f}")
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error during optimization: {e}")
            return []
    
    def record_response_time(self, response_time_ms: float) -> None:
        """Record a response time measurement"""
        self._response_times.append(response_time_ms)
    
    def record_error(self) -> None:
        """Record an error occurrence"""
        self._error_count += 1
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            current_metrics = None
            if self._metrics_history:
                current_metrics = self._metrics_history[-1]
            
            # Calculate averages
            if len(self._metrics_history) > 1:
                recent_metrics = list(self._metrics_history)[-10:]  # Last 10 measurements
                avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
                avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
                avg_response_time = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
            else:
                avg_cpu = current_metrics.cpu_percent if current_metrics else 0
                avg_memory = current_metrics.memory_percent if current_metrics else 0
                avg_response_time = current_metrics.response_time_ms if current_metrics else 0
            
            return {
                "status": "running" if self._running else "stopped",
                "current_metrics": {
                    "cpu_percent": current_metrics.cpu_percent if current_metrics else 0,
                    "memory_percent": current_metrics.memory_percent if current_metrics else 0,
                    "memory_used_mb": current_metrics.memory_used_mb if current_metrics else 0,
                    "active_threads": current_metrics.active_threads if current_metrics else 0,
                    "open_files": current_metrics.open_files if current_metrics else 0,
                    "response_time_ms": current_metrics.response_time_ms if current_metrics else 0
                },
                "averages": {
                    "cpu_percent": avg_cpu,
                    "memory_percent": avg_memory,
                    "response_time_ms": avg_response_time
                },
                "totals": {
                    "metrics_collected": len(self._metrics_history),
                    "optimizations_run": len(self._optimization_history),
                    "errors_recorded": self._error_count
                },
                "last_optimization": self._last_optimization.isoformat() if self._last_optimization else None,
                "auto_optimize": self.auto_optimize,
                "monitoring_interval": self.monitoring_interval,
                "optimization_interval": self.optimization_interval
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {"status": "error", "error": str(e)}


# Global performance manager instance
_performance_manager: Optional[PerformanceManager] = None


def get_performance_manager() -> PerformanceManager:
    """Get global performance manager instance"""
    global _performance_manager
    if _performance_manager is None:
        _performance_manager = PerformanceManager()
    return _performance_manager


async def cleanup_performance_manager() -> None:
    """Cleanup global performance manager"""
    global _performance_manager
    if _performance_manager is not None:
        await _performance_manager.shutdown()
        _performance_manager = None
