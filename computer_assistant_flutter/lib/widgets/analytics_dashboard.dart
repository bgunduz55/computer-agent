/// Analytics and Monitoring Dashboard
/// 
/// Real-time metrics display and performance analytics
/// Integrates with backend T015 (Analytics and Logging)

import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../models/backend_integration_models.dart';
import '../services/websocket_service.dart';
import '../shared/websocket_protocol.dart';

class AnalyticsDashboard extends StatefulWidget {
  final bool showMetrics;
  final bool showCharts;
  final bool showLogs;
  final bool showReports;

  const AnalyticsDashboard({
    Key? key,
    this.showMetrics = true,
    this.showCharts = true,
    this.showLogs = true,
    this.showReports = true,
  }) : super(key: key);

  @override
  State<AnalyticsDashboard> createState() => _AnalyticsDashboardState();
}

class _AnalyticsDashboardState extends State<AnalyticsDashboard>
    with TickerProviderStateMixin {
  final WebSocketService _webSocketService = WebSocketService();
  final ScrollController _logScrollController = ScrollController();
  
  List<AnalyticsMetrics> _metrics = [];
  List<LogEvent> _logs = [];
  Map<String, dynamic> _realTimeMetrics = {};
  Map<String, dynamic> _performanceData = {};
  
  bool _isLoadingMetrics = false;
  bool _isLoadingLogs = false;
  bool _isRealTimeMode = false;
  
  late TabController _tabController;
  late AnimationController _refreshAnimationController;
  late Animation<double> _refreshAnimation;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _refreshAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    _refreshAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _refreshAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _setupWebSocketListeners();
    _loadInitialData();
  }

  void _setupWebSocketListeners() {
    _webSocketService.messageStream.listen((message) {
      if (mounted) {
        _handleWebSocketMessage(message);
      }
    });
  }

  void _handleWebSocketMessage(dynamic message) {
    if (message is WebSocketMessage) {
      switch (message.type) {
        case MessageType.analyticsResponse:
          _handleAnalyticsResponse(message);
          break;
        case MessageType.analyticsMetrics:
          _handleRealTimeMetrics(message);
          break;
        case MessageType.logResponse:
          _handleLogResponse(message);
          break;
        case MessageType.metricsResponse:
          _handleMetricsResponse(message);
          break;
        default:
          break;
      }
    }
  }

  void _handleAnalyticsResponse(WebSocketMessage message) {
    setState(() {
      _metrics = (message.data['metrics'] as List<dynamic>)
          .map((item) => AnalyticsMetrics.fromJson(item))
          .toList();
      _isLoadingMetrics = false;
    });
  }

  void _handleRealTimeMetrics(WebSocketMessage message) {
    setState(() {
      _realTimeMetrics = message.data;
    });
  }

  void _handleLogResponse(WebSocketMessage message) {
    setState(() {
      _logs = (message.data['logs'] as List<dynamic>)
          .map((item) => LogEvent.fromJson(item))
          .toList();
      _isLoadingLogs = false;
    });
  }

  void _handleMetricsResponse(WebSocketMessage message) {
    setState(() {
      _performanceData = message.data;
    });
  }

  void _loadInitialData() {
    _loadAnalytics();
    _loadLogs();
    _startRealTimeMode();
  }

  void _loadAnalytics() {
    setState(() {
      _isLoadingMetrics = true;
    });
    _webSocketService.requestAnalytics();
  }

  void _loadLogs() {
    setState(() {
      _isLoadingLogs = true;
    });
    _webSocketService.logEvent('info', 'user_action', 'Analytics dashboard loaded');
  }

  void _startRealTimeMode() {
    setState(() {
      _isRealTimeMode = true;
    });
    _webSocketService.requestRealTimeMetrics();
    
    // Request real-time metrics every 5 seconds
    Future.delayed(const Duration(seconds: 5), () {
      if (_isRealTimeMode && mounted) {
        _webSocketService.requestRealTimeMetrics();
      }
    });
  }

  void _stopRealTimeMode() {
    setState(() {
      _isRealTimeMode = false;
    });
  }

  void _refreshData() {
    _refreshAnimationController.forward().then((_) {
      _refreshAnimationController.reset();
    });
    
    _loadAnalytics();
    _loadLogs();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _refreshAnimationController.dispose();
    _logScrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Column(
        children: [
          _buildHeader(),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildMetricsTab(),
                _buildChartsTab(),
                _buildLogsTab(),
                _buildReportsTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Row(
            children: [
              const Icon(Icons.analytics),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Analytics Dashboard',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              AnimatedBuilder(
                animation: _refreshAnimation,
                builder: (context, child) {
                  return Transform.rotate(
                    angle: _refreshAnimation.value * 2 * 3.14159,
                    child: IconButton(
                      onPressed: _refreshData,
                      icon: const Icon(Icons.refresh),
                      tooltip: 'Refresh Data',
                    ),
                  );
                },
              ),
              Switch(
                value: _isRealTimeMode,
                onChanged: (value) {
                  if (value) {
                    _startRealTimeMode();
                  } else {
                    _stopRealTimeMode();
                  }
                },
                activeColor: Colors.green,
              ),
              const SizedBox(width: 8),
              Text(
                _isRealTimeMode ? 'Live' : 'Static',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
          const SizedBox(height: 16),
          TabBar(
            controller: _tabController,
            isScrollable: true,
            tabs: const [
              Tab(icon: Icon(Icons.speed), text: 'Metrics'),
              Tab(icon: Icon(Icons.show_chart), text: 'Charts'),
              Tab(icon: Icon(Icons.list_alt), text: 'Logs'),
              Tab(icon: Icon(Icons.assessment), text: 'Reports'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: _isLoadingMetrics
          ? const Center(child: CircularProgressIndicator())
          : _metrics.isEmpty
              ? const Center(child: Text('No metrics available'))
              : Column(
                  children: [
                    _buildRealTimeMetricsCard(),
                    const SizedBox(height: 16),
                    Expanded(
                      child: ListView.builder(
                        itemCount: _metrics.length,
                        itemBuilder: (context, index) {
                          final metric = _metrics[index];
                          return _buildMetricCard(metric);
                        },
                      ),
                    ),
                  ],
                ),
    );
  }

  Widget _buildRealTimeMetricsCard() {
    return Card(
      color: Colors.blue[50],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.trending_up,
                  color: Colors.blue[700],
                ),
                const SizedBox(width: 8),
                Text(
                  'Real-time Metrics',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue[700],
                  ),
                ),
                const Spacer(),
                if (_isRealTimeMode)
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.green,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            if (_realTimeMetrics.isNotEmpty) ...[
              Row(
                children: [
                  Expanded(
                    child: _buildMetricItem(
                      'Active Sessions',
                      _realTimeMetrics['active_sessions']?.toString() ?? '0',
                      Colors.green,
                    ),
                  ),
                  Expanded(
                    child: _buildMetricItem(
                      'Commands/Min',
                      _realTimeMetrics['commands_per_minute']?.toString() ?? '0',
                      Colors.blue,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricItem(
                      'CPU Usage',
                      '${_realTimeMetrics['cpu_usage']?.toString() ?? '0'}%',
                      Colors.orange,
                    ),
                  ),
                  Expanded(
                    child: _buildMetricItem(
                      'Memory Usage',
                      '${_realTimeMetrics['memory_usage']?.toString() ?? '0'}%',
                      Colors.purple,
                    ),
                  ),
                ],
              ),
            ] else ...[
              const Text('No real-time data available'),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildMetricItem(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricCard(AnalyticsMetrics metric) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getMetricColor(metric.metricType),
          child: Icon(
            _getMetricIcon(metric.metricType),
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(metric.name),
        subtitle: Text('${metric.value} ${metric.unit ?? ''}'),
        trailing: Text(
          _formatTimestamp(metric.timestamp),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
          ),
        ),
      ),
    );
  }

  Widget _buildChartsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Expanded(
            child: _buildPerformanceChart(),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: _buildUsageChart(),
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceChart() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Performance Metrics',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(show: true),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true),
                    ),
                    topTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  borderData: FlBorderData(show: true),
                  lineBarsData: [
                    LineChartBarData(
                      spots: _generateChartData(),
                      isCurved: true,
                      color: Colors.blue,
                      barWidth: 3,
                      dotData: FlDotData(show: false),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUsageChart() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Resource Usage',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: PieChart(
                PieChartData(
                  sections: [
                    PieChartSectionData(
                      value: 40,
                      title: 'CPU',
                      color: Colors.blue,
                    ),
                    PieChartSectionData(
                      value: 30,
                      title: 'Memory',
                      color: Colors.green,
                    ),
                    PieChartSectionData(
                      value: 20,
                      title: 'Disk',
                      color: Colors.orange,
                    ),
                    PieChartSectionData(
                      value: 10,
                      title: 'Network',
                      color: Colors.purple,
                    ),
                  ],
                  sectionsSpace: 2,
                  centerSpaceRadius: 40,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLogsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'System Logs',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              TextButton.icon(
                onPressed: _loadLogs,
                icon: const Icon(Icons.refresh, size: 16),
                label: const Text('Refresh'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: _isLoadingLogs
                ? const Center(child: CircularProgressIndicator())
                : _logs.isEmpty
                    ? const Center(child: Text('No logs available'))
                    : ListView.builder(
                        controller: _logScrollController,
                        itemCount: _logs.length,
                        itemBuilder: (context, index) {
                          final log = _logs[index];
                          return _buildLogItem(log);
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildLogItem(LogEvent log) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getLogLevelColor(log.level),
          child: Icon(
            _getLogLevelIcon(log.level),
            color: Colors.white,
            size: 16,
          ),
        ),
        title: Text(log.message),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${log.eventType} • ${log.component ?? 'System'}'),
            Text(
              _formatTimestamp(log.timestamp),
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
        trailing: Text(
          log.level.toUpperCase(),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: _getLogLevelColor(log.level),
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  Widget _buildReportsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          _buildReportCard(
            'Performance Report',
            'System performance over the last 24 hours',
            Icons.assessment,
            Colors.blue,
          ),
          const SizedBox(height: 16),
          _buildReportCard(
            'Usage Statistics',
            'Command usage and user activity patterns',
            Icons.analytics,
            Colors.green,
          ),
          const SizedBox(height: 16),
          _buildReportCard(
            'Error Analysis',
            'Error patterns and recovery suggestions',
            Icons.bug_report,
            Colors.red,
          ),
        ],
      ),
    );
  }

  Widget _buildReportCard(String title, String description, IconData icon, Color color) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color,
          child: Icon(icon, color: Colors.white),
        ),
        title: Text(title),
        subtitle: Text(description),
        trailing: const Icon(Icons.arrow_forward),
        onTap: () {
          // Generate and show report
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Generating $title...')),
          );
        },
      ),
    );
  }

  List<FlSpot> _generateChartData() {
    // Generate sample chart data
    return List.generate(10, (index) {
      return FlSpot(index.toDouble(), (index * 10 + 20).toDouble());
    });
  }

  Color _getMetricColor(String metricType) {
    switch (metricType.toLowerCase()) {
      case 'performance':
        return Colors.blue;
      case 'usage':
        return Colors.green;
      case 'error':
        return Colors.red;
      case 'custom':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  IconData _getMetricIcon(String metricType) {
    switch (metricType.toLowerCase()) {
      case 'performance':
        return Icons.speed;
      case 'usage':
        return Icons.analytics;
      case 'error':
        return Icons.error;
      case 'custom':
        return Icons.tune;
      default:
        return Icons.info;
    }
  }

  Color _getLogLevelColor(String level) {
    switch (level.toLowerCase()) {
      case 'error':
        return Colors.red;
      case 'warning':
        return Colors.orange;
      case 'info':
        return Colors.blue;
      case 'debug':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }

  IconData _getLogLevelIcon(String level) {
    switch (level.toLowerCase()) {
      case 'error':
        return Icons.error;
      case 'warning':
        return Icons.warning;
      case 'info':
        return Icons.info;
      case 'debug':
        return Icons.bug_report;
      default:
        return Icons.help;
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inSeconds < 60) {
      return '${difference.inSeconds}s ago';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inDays}d ago';
    }
  }
}
