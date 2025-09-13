"""
System Information Manager - Provides system and real-time information to AI
"""

import asyncio
import logging
import platform
import psutil
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

from core.platform import get_platform


@dataclass
class SystemTime:
    """System time information"""
    local_time: str
    utc_time: str
    timezone_name: str
    timestamp: float
    formatted_date: str
    formatted_time: str
    day_of_week: str
    is_dst: bool


@dataclass
class SystemInfo:
    """System information"""
    platform: str
    platform_version: str
    architecture: str
    processor: str
    hostname: str
    username: str
    python_version: str
    uptime_seconds: float
    uptime_formatted: str


@dataclass
class PerformanceInfo:
    """System performance information"""
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    disk_total_gb: float
    process_count: int
    boot_time: str


@dataclass
class NetworkInfo:
    """Network information"""
    network_interfaces: List[Dict[str, Any]]
    active_connections: int
    bytes_sent: int
    bytes_received: int


class SystemInfoManager:
    """Manages system information and real-time data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform_manager = get_platform()
        self._initialized = False
        self._cache = {}
        self._cache_timeout = 5.0  # Cache for 5 seconds
        
    def initialize(self) -> bool:
        """Initialize system info manager"""
        try:
            self.logger.info("System info manager initialized successfully")
            self._initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize system info manager: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup system info manager"""
        self._cache.clear()
        self._initialized = False
        self.logger.info("System info manager cleaned up")
    
    def get_current_time(self) -> SystemTime:
        """Get current system time information"""
        try:
            now = datetime.now()
            utc_now = datetime.now(timezone.utc)
            
            return SystemTime(
                local_time=now.strftime("%H:%M:%S"),
                utc_time=utc_now.strftime("%H:%M:%S UTC"),
                timezone_name=str(now.astimezone().tzinfo),
                timestamp=time.time(),
                formatted_date=now.strftime("%Y-%m-%d"),
                formatted_time=now.strftime("%I:%M:%S %p"),
                day_of_week=now.strftime("%A"),
                is_dst=bool(time.daylight and time.localtime().tm_isdst)
            )
        except Exception as e:
            self.logger.error(f"Failed to get current time: {e}")
            return SystemTime(
                local_time="Unknown",
                utc_time="Unknown",
                timezone_name="Unknown",
                timestamp=0.0,
                formatted_date="Unknown",
                formatted_time="Unknown",
                day_of_week="Unknown",
                is_dst=False
            )
    
    def get_system_info(self) -> SystemInfo:
        """Get system information"""
        cache_key = "system_info"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_formatted = self._format_uptime(uptime_seconds)
            
            # Get processor info with better error handling
            try:
                processor = platform.processor()
                if not processor or processor == "":
                    # Try to get CPU info from psutil
                    try:
                        import psutil
                        cpu_info = psutil.cpu_freq()
                        if cpu_info:
                            processor = f"CPU @ {cpu_info.max:.0f}MHz"
                        else:
                            processor = "Unknown CPU"
                    except:
                        processor = "Unknown CPU"
            except Exception:
                processor = "Unknown CPU"
            
            # Get hostname with fallback
            try:
                hostname = platform.node()
                if not hostname or hostname == "":
                    hostname = "Unknown"
            except Exception:
                hostname = "Unknown"
            
            # Get username with fallback
            try:
                username = Path.home().name
                if not username or username == "":
                    import getpass
                    username = getpass.getuser()
            except Exception:
                username = "Unknown"
            
            info = SystemInfo(
                platform=platform.system(),
                platform_version=platform.version(),
                architecture=platform.architecture()[0],
                processor=processor,
                hostname=hostname,
                username=username,
                python_version=platform.python_version(),
                uptime_seconds=uptime_seconds,
                uptime_formatted=uptime_formatted
            )
            
            self._cache[cache_key] = info
            self._cache[f"{cache_key}_time"] = time.time()
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return SystemInfo(
                platform="Unknown",
                platform_version="Unknown", 
                architecture="Unknown",
                processor="Unknown",
                hostname="Unknown",
                username="Unknown",
                python_version="Unknown",
                uptime_seconds=0.0,
                uptime_formatted="Unknown"
            )
    
    def get_performance_info(self) -> PerformanceInfo:
        """Get system performance information"""
        cache_key = "performance_info"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        
        try:
            memory = psutil.virtual_memory()
            
            # Get disk usage - handle different platforms
            try:
                if platform.system() == "Windows":
                    disk = psutil.disk_usage('C:')
                else:
                    disk = psutil.disk_usage('/')
            except Exception as e:
                self.logger.warning(f"Failed to get disk usage: {e}")
                disk = type('DiskUsage', (), {
                    'percent': 0.0,
                    'free': 0,
                    'total': 0
                })()
            
            boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            
            info = PerformanceInfo(
                cpu_percent=psutil.cpu_percent(interval=1),
                memory_percent=memory.percent,
                memory_available_gb=round(memory.available / (1024**3), 2),
                memory_total_gb=round(memory.total / (1024**3), 2),
                disk_usage_percent=disk.percent,
                disk_free_gb=round(disk.free / (1024**3), 2),
                disk_total_gb=round(disk.total / (1024**3), 2),
                process_count=len(psutil.pids()),
                boot_time=boot_time
            )
            
            self._cache[cache_key] = info
            self._cache[f"{cache_key}_time"] = time.time()
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get performance info: {e}")
            return PerformanceInfo(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_gb=0.0,
                memory_total_gb=0.0,
                disk_usage_percent=0.0,
                disk_free_gb=0.0,
                disk_total_gb=0.0,
                process_count=0,
                boot_time="Unknown"
            )
    
    def get_network_info(self) -> NetworkInfo:
        """Get network information"""
        cache_key = "network_info"
        if self._is_cached(cache_key):
            return self._cache[cache_key]
        
        try:
            interfaces = []
            try:
                for interface, addrs in psutil.net_if_addrs().items():
                    interface_info = {
                        "name": interface,
                        "addresses": []
                    }
                    for addr in addrs:
                        interface_info["addresses"].append({
                            "family": str(addr.family),
                            "address": addr.address or "Unknown",
                            "netmask": getattr(addr, 'netmask', None),
                            "broadcast": getattr(addr, 'broadcast', None)
                        })
                    interfaces.append(interface_info)
            except Exception as e:
                self.logger.warning(f"Failed to get network interfaces: {e}")
                interfaces = []
            
            try:
                net_io = psutil.net_io_counters()
                bytes_sent = net_io.bytes_sent if net_io else 0
                bytes_received = net_io.bytes_recv if net_io else 0
            except Exception as e:
                self.logger.warning(f"Failed to get network I/O counters: {e}")
                bytes_sent = 0
                bytes_received = 0
            
            try:
                active_connections = len(psutil.net_connections())
            except Exception as e:
                self.logger.warning(f"Failed to get active connections: {e}")
                active_connections = 0
            
            info = NetworkInfo(
                network_interfaces=interfaces,
                active_connections=active_connections,
                bytes_sent=bytes_sent,
                bytes_received=bytes_received
            )
            
            self._cache[cache_key] = info
            self._cache[f"{cache_key}_time"] = time.time()
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get network info: {e}")
            return NetworkInfo(
                network_interfaces=[],
                active_connections=0,
                bytes_sent=0,
                bytes_received=0
            )
    
    def get_comprehensive_system_context(self) -> Dict[str, Any]:
        """Get comprehensive system context for AI"""
        try:
            time_info = self.get_current_time()
            system_info = self.get_system_info()
            performance_info = self.get_performance_info()
            
            return {
                "current_time": asdict(time_info),
                "system": asdict(system_info),
                "performance": asdict(performance_info),
                "context_generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive system context: {e}")
            return {}
    
    def get_time_context_for_ai(self) -> str:
        """Get formatted time context for AI responses"""
        try:
            time_info = self.get_current_time()
            return f"Current time: {time_info.formatted_time} on {time_info.day_of_week}, {time_info.formatted_date} ({time_info.timezone_name})"
        except Exception as e:
            self.logger.error(f"Failed to get time context for AI: {e}")
            return "Current time information is not available"
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached and not expired"""
        if key not in self._cache:
            return False
        
        cache_time_key = f"{key}_time"
        if cache_time_key not in self._cache:
            return False
        
        return (time.time() - self._cache[cache_time_key]) < self._cache_timeout
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """Format uptime in human readable format"""
        try:
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            if days > 0:
                return f"{days} days, {hours} hours, {minutes} minutes"
            elif hours > 0:
                return f"{hours} hours, {minutes} minutes"
            else:
                return f"{minutes} minutes"
        except Exception:
            return "Unknown"


# Global instance
_system_info_manager: Optional[SystemInfoManager] = None


def get_system_info_manager() -> SystemInfoManager:
    """Get global system info manager instance"""
    global _system_info_manager
    if _system_info_manager is None:
        _system_info_manager = SystemInfoManager()
    return _system_info_manager


def cleanup_system_info_manager() -> None:
    """Cleanup global system info manager instance"""
    global _system_info_manager
    if _system_info_manager:
        _system_info_manager.cleanup()
        _system_info_manager = None
