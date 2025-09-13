"""
Health Checker for JARVIS Computer Assistant

Provides comprehensive health checking for all system components.
"""

import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str
    response_time: float
    timestamp: float
    details: Dict[str, Any] = None

@dataclass
class HealthReport:
    """Overall health report"""
    overall_status: HealthStatus
    timestamp: float
    checks: List[HealthCheck]
    summary: Dict[str, Any]

class HealthChecker:
    """Comprehensive health checker for JARVIS components"""
    
    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.check_timeout = 30.0
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default health checks"""
        self.register_check("system_resources", self._check_system_resources)
        self.register_check("disk_space", self._check_disk_space)
        self.register_check("memory_usage", self._check_memory_usage)
        self.register_check("cpu_usage", self._check_cpu_usage)
        self.register_check("network_connectivity", self._check_network_connectivity)
        self.register_check("process_health", self._check_process_health)
    
    def register_check(self, name: str, check_function: Callable):
        """Register a health check function"""
        self.checks[name] = check_function
    
    async def run_health_checks(self) -> HealthReport:
        """Run all registered health checks"""
        start_time = time.time()
        checks = []
        
        # Run checks in parallel
        tasks = []
        for name, check_func in self.checks.items():
            task = asyncio.create_task(self._run_single_check(name, check_func))
            tasks.append(task)
        
        # Wait for all checks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                check_name = list(self.checks.keys())[i]
                checks.append(HealthCheck(
                    name=check_name,
                    status=HealthStatus.CRITICAL,
                    message=f"Check failed with exception: {str(result)}",
                    response_time=0.0,
                    timestamp=time.time()
                ))
            else:
                checks.append(result)
        
        # Determine overall status
        overall_status = self._determine_overall_status(checks)
        
        # Create summary
        summary = {
            "total_checks": len(checks),
            "healthy_checks": len([c for c in checks if c.status == HealthStatus.HEALTHY]),
            "warning_checks": len([c for c in checks if c.status == HealthStatus.WARNING]),
            "critical_checks": len([c for c in checks if c.status == HealthStatus.CRITICAL]),
            "unknown_checks": len([c for c in checks if c.status == HealthStatus.UNKNOWN]),
            "total_response_time": sum(c.response_time for c in checks),
            "timestamp": time.time()
        }
        
        return HealthReport(
            overall_status=overall_status,
            timestamp=time.time(),
            checks=checks,
            summary=summary
        )
    
    async def _run_single_check(self, name: str, check_function: Callable) -> HealthCheck:
        """Run a single health check with timeout"""
        start_time = time.time()
        
        try:
            # Run check with timeout
            result = await asyncio.wait_for(
                check_function(),
                timeout=self.check_timeout
            )
            
            response_time = time.time() - start_time
            
            if isinstance(result, HealthCheck):
                result.response_time = response_time
                result.timestamp = time.time()
                return result
            else:
                # Convert simple result to HealthCheck
                return HealthCheck(
                    name=name,
                    status=result.get("status", HealthStatus.UNKNOWN),
                    message=result.get("message", "Check completed"),
                    response_time=response_time,
                    timestamp=time.time(),
                    details=result.get("details", {})
                )
                
        except asyncio.TimeoutError:
            return HealthCheck(
                name=name,
                status=HealthStatus.CRITICAL,
                message=f"Check timed out after {self.check_timeout} seconds",
                response_time=time.time() - start_time,
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheck(
                name=name,
                status=HealthStatus.CRITICAL,
                message=f"Check failed with exception: {str(e)}",
                response_time=time.time() - start_time,
                timestamp=time.time()
            )
    
    def _determine_overall_status(self, checks: List[HealthCheck]) -> HealthStatus:
        """Determine overall health status from individual checks"""
        if not checks:
            return HealthStatus.UNKNOWN
        
        # Check for critical status
        if any(c.status == HealthStatus.CRITICAL for c in checks):
            return HealthStatus.CRITICAL
        
        # Check for warning status
        if any(c.status == HealthStatus.WARNING for c in checks):
            return HealthStatus.WARNING
        
        # Check for unknown status
        if any(c.status == HealthStatus.UNKNOWN for c in checks):
            return HealthStatus.WARNING
        
        return HealthStatus.HEALTHY
    
    async def _check_system_resources(self) -> HealthCheck:
        """Check overall system resources"""
        try:
            # Get system info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status
            status = HealthStatus.HEALTHY
            issues = []
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            elif cpu_percent > 80:
                status = HealthStatus.WARNING
                issues.append(f"Elevated CPU usage: {cpu_percent:.1f}%")
            
            if memory.percent > 90:
                status = HealthStatus.CRITICAL
                issues.append(f"High memory usage: {memory.percent:.1f}%")
            elif memory.percent > 80:
                status = HealthStatus.WARNING
                issues.append(f"Elevated memory usage: {memory.percent:.1f}%")
            
            if disk.percent > 95:
                status = HealthStatus.CRITICAL
                issues.append(f"Critical disk usage: {disk.percent:.1f}%")
            elif disk.percent > 85:
                status = HealthStatus.WARNING
                issues.append(f"High disk usage: {disk.percent:.1f}%")
            
            message = "System resources are healthy"
            if issues:
                message = "; ".join(issues)
            
            return HealthCheck(
                name="system_resources",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=time.time(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3)
                }
            )
        except Exception as e:
            return HealthCheck(
                name="system_resources",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check system resources: {str(e)}",
                response_time=0.0,
                timestamp=time.time()
            )
    
    async def _check_disk_space(self) -> HealthCheck:
        """Check disk space availability"""
        try:
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024**3)
            total_gb = disk.total / (1024**3)
            usage_percent = (disk.used / disk.total) * 100
            
            if usage_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical disk space: {free_gb:.1f}GB free ({usage_percent:.1f}% used)"
            elif usage_percent > 85:
                status = HealthStatus.WARNING
                message = f"Low disk space: {free_gb:.1f}GB free ({usage_percent:.1f}% used)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space OK: {free_gb:.1f}GB free ({usage_percent:.1f}% used)"
            
            return HealthCheck(
                name="disk_space",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=time.time(),
                details={
                    "free_gb": free_gb,
                    "total_gb": total_gb,
                    "usage_percent": usage_percent
                }
            )
        except Exception as e:
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check disk space: {str(e)}",
                response_time=0.0,
                timestamp=time.time()
            )
    
    async def _check_memory_usage(self) -> HealthCheck:
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            total_gb = memory.total / (1024**3)
            
            if memory.percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {available_gb:.1f}GB available ({memory.percent:.1f}% used)"
            elif memory.percent > 85:
                status = HealthStatus.WARNING
                message = f"High memory usage: {available_gb:.1f}GB available ({memory.percent:.1f}% used)"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage OK: {available_gb:.1f}GB available ({memory.percent:.1f}% used)"
            
            return HealthCheck(
                name="memory_usage",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=time.time(),
                details={
                    "available_gb": available_gb,
                    "total_gb": total_gb,
                    "usage_percent": memory.percent
                }
            )
        except Exception as e:
            return HealthCheck(
                name="memory_usage",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check memory usage: {str(e)}",
                response_time=0.0,
                timestamp=time.time()
            )
    
    async def _check_cpu_usage(self) -> HealthCheck:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=2)
            cpu_count = psutil.cpu_count()
            
            if cpu_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent > 85:
                status = HealthStatus.WARNING
                message = f"High CPU usage: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage OK: {cpu_percent:.1f}%"
            
            return HealthCheck(
                name="cpu_usage",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=time.time(),
                details={
                    "cpu_percent": cpu_percent,
                    "cpu_count": cpu_count
                }
            )
        except Exception as e:
            return HealthCheck(
                name="cpu_usage",
                status=HealthStatus.CRITICAL,
                message=f"Failed to check CPU usage: {str(e)}",
                response_time=0.0,
                timestamp=time.time()
            )
    
    async def _check_network_connectivity(self) -> HealthCheck:
        """Check network connectivity"""
        try:
            import socket
            
            # Test DNS resolution
            socket.gethostbyname("google.com")
            
            # Test basic connectivity
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("8.8.8.8", 53))
            sock.close()
            
            if result == 0:
                status = HealthStatus.HEALTHY
                message = "Network connectivity OK"
            else:
                status = HealthStatus.WARNING
                message = "Network connectivity issues detected"
            
            return HealthCheck(
                name="network_connectivity",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=time.time(),
                details={"connectivity_test": "passed" if result == 0 else "failed"}
            )
        except Exception as e:
            return HealthCheck(
                name="network_connectivity",
                status=HealthStatus.WARNING,
                message=f"Network connectivity check failed: {str(e)}",
                response_time=0.0,
                timestamp=time.time()
            )
    
    async def _check_process_health(self) -> HealthCheck:
        """Check process health"""
        try:
            process = psutil.Process()
            
            # Check if process is responsive
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            num_threads = process.num_threads()
            num_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            
            status = HealthStatus.HEALTHY
            issues = []
            
            if num_threads > 1000:
                status = HealthStatus.WARNING
                issues.append(f"High thread count: {num_threads}")
            
            if num_fds > 1000:
                status = HealthStatus.WARNING
                issues.append(f"High file descriptor count: {num_fds}")
            
            message = "Process health OK"
            if issues:
                message = "; ".join(issues)
            
            return HealthCheck(
                name="process_health",
                status=status,
                message=message,
                response_time=0.0,
                timestamp=time.time(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_info.rss / (1024 * 1024),
                    "thread_count": num_threads,
                    "file_descriptors": num_fds
                }
            )
        except Exception as e:
            return HealthCheck(
                name="process_health",
                status=HealthStatus.CRITICAL,
                message=f"Process health check failed: {str(e)}",
                response_time=0.0,
                timestamp=time.time()
            )

# Global health checker instance
_health_checker = None

def get_health_checker() -> HealthChecker:
    """Get global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker
