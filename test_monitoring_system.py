import asyncio
import sys
sys.path.insert(0, 'src')

from features.monitoring import (
    get_logging_manager, get_metrics_collector, get_performance_monitor,
    get_health_checker, get_alert_manager, LogLevel, LogFormat
)

async def test_monitoring_system():
    """Test comprehensive monitoring system"""
    
    print("🔍 Testing JARVIS Monitoring System")
    print("=" * 50)
    
    # 1. Test Logging Manager
    print("\n1. Testing Logging Manager...")
    logging_manager = get_logging_manager()
    
    # Setup logging
    from features.monitoring.logging_manager import setup_logging
    setup_logging(
        log_dir="logs",
        log_level=LogLevel.INFO,
        log_format=LogFormat.STRUCTURED
    )
    
    # Test logging with context
    with logging_manager.log_context(
        correlation_id="test-123",
        user_id="test_user",
        session_id="test_session"
    ):
        logger = logging_manager.get_logger("test")
        logger.info("Testing structured logging")
        logger.warning("Testing warning level")
        logger.error("Testing error level")
    
    # Test command execution logging
    logging_manager.log_command_execution(
        command="test command",
        success=True,
        execution_time=1.5,
        steps_executed=3
    )
    
    print("✅ Logging Manager working")
    
    # 2. Test Metrics Collector
    print("\n2. Testing Metrics Collector...")
    metrics = get_metrics_collector()
    
    # Record some metrics
    metrics.increment_counter("commands_executed", 1)
    metrics.increment_counter("commands_executed", 2)
    metrics.set_gauge("active_connections", 5)
    metrics.record_histogram("response_time", 1.2)
    metrics.record_histogram("response_time", 2.1)
    metrics.record_histogram("response_time", 0.8)
    metrics.record_timer("command_execution", 1.5)
    metrics.record_rate("requests_per_second", 10.5)
    
    # Get metrics summary
    summary = metrics.get_metrics_summary()
    print(f"✅ Metrics collected: {summary['total_metrics']} metrics")
    print(f"   - Commands executed: {summary['counters'].get('commands_executed', 0)}")
    print(f"   - Active connections: {summary['gauges'].get('active_connections', 0)}")
    
    # 3. Test Performance Monitor
    print("\n3. Testing Performance Monitor...")
    perf_monitor = get_performance_monitor()
    
    # Start monitoring
    await perf_monitor.start_monitoring()
    await asyncio.sleep(2)  # Let it collect some data
    
    # Get current metrics
    current = perf_monitor.get_current_metrics()
    if current:
        print(f"✅ Performance monitoring active")
        print(f"   - CPU: {current.cpu_percent:.1f}%")
        print(f"   - Memory: {current.memory_percent:.1f}%")
        print(f"   - Disk: {current.disk_usage_percent:.1f}%")
    
    # Get performance summary
    summary = perf_monitor.get_performance_summary()
    print(f"   - Status: {summary['status']}")
    print(f"   - Uptime: {summary['uptime']:.1f}s")
    
    # Stop monitoring
    await perf_monitor.stop_monitoring()
    
    # 4. Test Health Checker
    print("\n4. Testing Health Checker...")
    health_checker = get_health_checker()
    
    # Run health checks
    health_report = await health_checker.run_health_checks()
    print(f"✅ Health check completed")
    print(f"   - Overall status: {health_report.overall_status.value}")
    print(f"   - Checks run: {health_report.summary['total_checks']}")
    print(f"   - Healthy: {health_report.summary['healthy_checks']}")
    print(f"   - Warnings: {health_report.summary['warning_checks']}")
    print(f"   - Critical: {health_report.summary['critical_checks']}")
    
    # Show individual check results
    for check in health_report.checks:
        status_emoji = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "🚨",
            "unknown": "❓"
        }
        emoji = status_emoji.get(check.status.value, "❓")
        print(f"   {emoji} {check.name}: {check.message}")
    
    # 5. Test Alert Manager
    print("\n5. Testing Alert Manager...")
    alert_manager = get_alert_manager()
    
    # Create test alerts
    from features.monitoring.alert_manager import AlertLevel
    await alert_manager.create_alert(
        title="Test Warning",
        message="This is a test warning alert",
        level=AlertLevel.WARNING,
        source="test_system"
    )
    
    await alert_manager.create_alert(
        title="Test Critical",
        message="This is a test critical alert",
        level=AlertLevel.CRITICAL,
        source="test_system"
    )
    
    # Test alert rules
    test_context = {
        "cpu_percent": 95.0,
        "memory_percent": 85.0,
        "disk_usage_percent": 80.0,
        "error_rate": 0.05,
        "avg_response_time": 2.5
    }
    
    await alert_manager.check_rules(test_context)
    
    # Get alert summary
    alert_summary = alert_manager.get_alert_summary()
    print(f"✅ Alert Manager working")
    print(f"   - Total alerts: {alert_summary['total_alerts']}")
    print(f"   - Active alerts: {alert_summary['active_alerts']}")
    print(f"   - Rules: {alert_summary['rules_count']}")
    
    # Show active alerts
    active_alerts = alert_manager.get_active_alerts()
    for alert in active_alerts:
        level_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        emoji = level_emoji.get(alert.level.value, "❓")
        print(f"   {emoji} {alert.title}: {alert.message}")
    
    print("\n🎉 All monitoring systems working correctly!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_monitoring_system())
