/// Error Recovery and Learning UI
/// 
/// Error display with suggestions and learning progress
/// Integrates with backend T006 (Error Recovery and Learning)

import 'package:flutter/material.dart';
import '../models/backend_integration_models.dart';
import '../services/websocket_service.dart';
import '../shared/websocket_protocol.dart';

class ErrorRecoveryLearningUI extends StatefulWidget {
  final String? sessionId;
  final bool showErrors;
  final bool showRecovery;
  final bool showLearning;
  final bool showSuggestions;

  const ErrorRecoveryLearningUI({
    Key? key,
    this.sessionId,
    this.showErrors = true,
    this.showRecovery = true,
    this.showLearning = true,
    this.showSuggestions = true,
  }) : super(key: key);

  @override
  State<ErrorRecoveryLearningUI> createState() => _ErrorRecoveryLearningUIState();
}

class _ErrorRecoveryLearningUIState extends State<ErrorRecoveryLearningUI>
    with TickerProviderStateMixin {
  final WebSocketService _webSocketService = WebSocketService();
  final ScrollController _errorScrollController = ScrollController();
  final TextEditingController _searchController = TextEditingController();
  
  List<ErrorLogEntry> _errorLogs = [];
  List<Map<String, dynamic>> _recoverySuggestions = [];
  List<Map<String, dynamic>> _learningProgress = [];
  Map<String, dynamic> _learningStats = {};
  
  bool _isLoadingErrors = false;
  bool _isLoadingRecovery = false;
  bool _isLoadingLearning = false;
  bool _showResolvedErrors = false;
  
  late TabController _tabController;
  late AnimationController _errorAnimationController;
  late AnimationController _learningAnimationController;
  late Animation<double> _errorAnimation;
  late Animation<double> _learningAnimation;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _setupAnimations();
    _setupWebSocketListeners();
    _loadErrorData();
  }

  void _setupAnimations() {
    _errorAnimationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _learningAnimationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    _errorAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _errorAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _learningAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _learningAnimationController,
      curve: Curves.easeInOut,
    ));
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
        case MessageType.errorLog:
          _handleErrorLog(message);
          break;
        case MessageType.errorRecovery:
          _handleRecoveryResponse(message);
          break;
        case MessageType.learningUpdate:
          _handleLearningUpdate(message);
          break;
        case MessageType.learningResponse:
          _handleLearningResponse(message);
          break;
        default:
          break;
      }
    }
  }

  void _handleErrorLog(WebSocketMessage message) {
    final error = ErrorLogEntry.fromJson(message.data);
    
    setState(() {
      _errorLogs.add(error);
    });
    
    _errorAnimationController.forward();
    _generateRecoverySuggestions(error);
  }

  void _handleRecoveryResponse(WebSocketMessage message) {
    final success = message.data['success'] as bool;
    final suggestion = message.data['suggestion'] as String;
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(success ? 'Recovery successful: $suggestion' : 'Recovery failed'),
        backgroundColor: success ? Colors.green : Colors.red,
      ),
    );
  }

  void _handleLearningUpdate(WebSocketMessage message) {
    final progress = message.data['progress'] as Map<String, dynamic>;
    
    setState(() {
      _learningProgress.add(progress);
    });
    
    _learningAnimationController.forward();
  }

  void _handleLearningResponse(WebSocketMessage message) {
    setState(() {
      _learningStats = message.data;
      _isLoadingLearning = false;
    });
  }

  void _loadErrorData() {
    _loadErrors();
    _loadLearningStats();
  }

  void _loadErrors() {
    setState(() {
      _isLoadingErrors = true;
    });
    
    // Simulate loading errors
    Future.delayed(const Duration(seconds: 1), () {
      setState(() {
        _isLoadingErrors = false;
      });
    });
  }

  void _loadLearningStats() {
    setState(() {
      _isLoadingLearning = true;
    });
    
    _webSocketService.sendSystemControl('get_learning_stats');
  }

  void _generateRecoverySuggestions(ErrorLogEntry error) {
    final suggestions = <Map<String, dynamic>>[];
    
    // Generate suggestions based on error type
    switch (error.errorType) {
      case 'FileNotFoundError':
        suggestions.add({
          'type': 'file',
          'title': 'Create Missing File',
          'description': 'Create the missing file and retry',
          'action': 'create_file',
          'icon': Icons.create_new_folder,
          'color': Colors.blue,
        });
        break;
      case 'PermissionDeniedError':
        suggestions.add({
          'type': 'permission',
          'title': 'Elevate Privileges',
          'description': 'Run with elevated privileges',
          'action': 'elevate_privileges',
          'icon': Icons.admin_panel_settings,
          'color': Colors.orange,
        });
        break;
      case 'ConnectionError':
        suggestions.add({
          'type': 'network',
          'title': 'Check Connection',
          'description': 'Verify network connectivity',
          'action': 'check_connection',
          'icon': Icons.network_check,
          'color': Colors.red,
        });
        break;
      default:
        suggestions.add({
          'type': 'general',
          'title': 'General Recovery',
          'description': 'Attempt general error recovery',
          'action': 'general_recovery',
          'icon': Icons.refresh,
          'color': Colors.grey,
        });
    }
    
    setState(() {
      _recoverySuggestions = suggestions;
    });
  }

  void _executeRecoverySuggestion(Map<String, dynamic> suggestion) {
    _webSocketService.sendSystemControl('error_recovery', params: {
      'suggestion': suggestion['action'],
      'error_id': _errorLogs.isNotEmpty ? _errorLogs.last.errorId : null,
    });
  }

  void _resolveError(ErrorLogEntry error, String resolution) {
    _webSocketService.sendSystemControl('resolve_error', params: {
      'error_id': error.errorId,
      'resolution': resolution,
    });
    
    setState(() {
      error = ErrorLogEntry(
        errorId: error.errorId,
        timestamp: error.timestamp,
        errorType: error.errorType,
        message: error.message,
        severity: error.severity,
        category: error.category,
        context: error.context,
        isResolved: true,
        resolutionNotes: resolution,
        recoveryAttempted: error.recoveryAttempted,
        recoverySuccess: error.recoverySuccess,
        recoveryMessage: error.recoveryMessage,
      );
    });
  }

  void _searchErrors(String query) {
    setState(() {
      _errorLogs = _errorLogs.where((error) {
        return error.message.toLowerCase().contains(query.toLowerCase()) ||
               error.errorType.toLowerCase().contains(query.toLowerCase());
      }).toList();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _errorAnimationController.dispose();
    _learningAnimationController.dispose();
    _errorScrollController.dispose();
    _searchController.dispose();
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
                _buildErrorsTab(),
                _buildRecoveryTab(),
                _buildLearningTab(),
                _buildSuggestionsTab(),
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
              const Icon(Icons.bug_report),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Error Recovery & Learning',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              IconButton(
                onPressed: _loadErrorData,
                icon: const Icon(Icons.refresh),
                tooltip: 'Refresh Data',
              ),
            ],
          ),
          const SizedBox(height: 16),
          TabBar(
            controller: _tabController,
            isScrollable: true,
            tabs: const [
              Tab(icon: Icon(Icons.error), text: 'Errors'),
              Tab(icon: Icon(Icons.healing), text: 'Recovery'),
              Tab(icon: Icon(Icons.school), text: 'Learning'),
              Tab(icon: Icon(Icons.lightbulb), text: 'Suggestions'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildErrorsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          _buildErrorFilters(),
          const SizedBox(height: 16),
          Expanded(
            child: _isLoadingErrors
                ? const Center(child: CircularProgressIndicator())
                : _errorLogs.isEmpty
                    ? const Center(child: Text('No errors found'))
                    : ListView.builder(
                        controller: _errorScrollController,
                        itemCount: _errorLogs.length,
                        itemBuilder: (context, index) {
                          final error = _errorLogs[index];
                          return _buildErrorCard(error);
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorFilters() {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _searchController,
            decoration: const InputDecoration(
              labelText: 'Search Errors',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.search),
            ),
            onChanged: _searchErrors,
          ),
        ),
        const SizedBox(width: 12),
        Switch(
          value: _showResolvedErrors,
          onChanged: (value) {
            setState(() {
              _showResolvedErrors = value;
            });
          },
        ),
        const Text('Show Resolved'),
      ],
    );
  }

  Widget _buildErrorCard(ErrorLogEntry error) {
    if (!_showResolvedErrors && error.isResolved) {
      return const SizedBox.shrink();
    }
    
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      color: error.isResolved ? Colors.green[50] : _getSeverityColor(error.severity).withOpacity(0.1),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getSeverityColor(error.severity),
          child: Icon(
            _getSeverityIcon(error.severity),
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(
          error.errorType,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(error.message),
            const SizedBox(height: 4),
            Row(
              children: [
                Chip(
                  label: Text(error.severity.name.toUpperCase()),
                  backgroundColor: _getSeverityColor(error.severity),
                  labelStyle: const TextStyle(color: Colors.white, fontSize: 10),
                ),
                const SizedBox(width: 8),
                Chip(
                  label: Text(error.category.name.toUpperCase()),
                  backgroundColor: Colors.grey[300],
                  labelStyle: const TextStyle(fontSize: 10),
                ),
              ],
            ),
          ],
        ),
        trailing: PopupMenuButton(
          itemBuilder: (context) => [
            PopupMenuItem(
              value: 'recover',
              child: const Text('Attempt Recovery'),
            ),
            PopupMenuItem(
              value: 'resolve',
              child: const Text('Mark as Resolved'),
            ),
            PopupMenuItem(
              value: 'details',
              child: const Text('View Details'),
            ),
          ],
          onSelected: (value) {
            switch (value) {
              case 'recover':
                _executeRecoverySuggestion(_recoverySuggestions.isNotEmpty 
                    ? _recoverySuggestions.first 
                    : {'action': 'general_recovery'});
                break;
              case 'resolve':
                _showResolveDialog(error);
                break;
              case 'details':
                _showErrorDetails(error);
                break;
            }
          },
        ),
      ),
    );
  }

  Widget _buildRecoveryTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Recovery Suggestions',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_recoverySuggestions.isEmpty) ...[
            Text(
              'No recovery suggestions available',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ] else ...[
            Expanded(
              child: ListView.builder(
                itemCount: _recoverySuggestions.length,
                itemBuilder: (context, index) {
                  final suggestion = _recoverySuggestions[index];
                  return _buildRecoverySuggestionCard(suggestion);
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildRecoverySuggestionCard(Map<String, dynamic> suggestion) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: suggestion['color'] as Color,
          child: Icon(
            suggestion['icon'] as IconData,
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(suggestion['title'] as String),
        subtitle: Text(suggestion['description'] as String),
        trailing: ElevatedButton(
          onPressed: () => _executeRecoverySuggestion(suggestion),
          child: const Text('Execute'),
        ),
      ),
    );
  }

  Widget _buildLearningTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Learning Progress',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_isLoadingLearning) ...[
            const Center(child: CircularProgressIndicator()),
          ] else if (_learningStats.isEmpty) ...[
            Text(
              'No learning data available',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ] else ...[
            _buildLearningStatsCard(),
            const SizedBox(height: 16),
            Expanded(
              child: _buildLearningProgressList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildLearningStatsCard() {
    return Card(
      color: Colors.purple[50],
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.school,
                  color: Colors.purple[700],
                ),
                const SizedBox(width: 8),
                Text(
                  'Learning Statistics',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: Colors.purple[700],
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Errors Learned',
                    _learningStats['errors_learned']?.toString() ?? '0',
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Recovery Success',
                    '${_learningStats['recovery_success_rate']?.toString() ?? '0'}%',
                    Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Learning Rules',
                    _learningStats['learning_rules']?.toString() ?? '0',
                    Colors.orange,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Accuracy',
                    '${_learningStats['accuracy']?.toString() ?? '0'}%',
                    Colors.purple,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
            color: color,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildLearningProgressList() {
    return ListView.builder(
      itemCount: _learningProgress.length,
      itemBuilder: (context, index) {
        final progress = _learningProgress[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 8.0),
          child: ListTile(
            leading: const CircleAvatar(
              backgroundColor: Colors.purple,
              child: Icon(Icons.trending_up, color: Colors.white),
            ),
            title: Text(progress['title'] ?? 'Learning Update'),
            subtitle: Text(progress['description'] ?? ''),
            trailing: Text(
              _formatTimestamp(DateTime.fromMillisecondsSinceEpoch(
                (progress['timestamp'] as num).toInt() * 1000,
              )),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSuggestionsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Smart Suggestions',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Based on error patterns and learning data',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView(
              children: [
                _buildSuggestionCard(
                  'Enable Auto-Recovery',
                  'Automatically attempt recovery for common errors',
                  Icons.auto_fix_high,
                  Colors.blue,
                ),
                _buildSuggestionCard(
                  'Improve Error Logging',
                  'Enhance error logging for better analysis',
                  Icons.analytics,
                  Colors.green,
                ),
                _buildSuggestionCard(
                  'Update Learning Rules',
                  'Add new learning rules based on recent errors',
                  Icons.rule,
                  Colors.orange,
                ),
                _buildSuggestionCard(
                  'Optimize Performance',
                  'Optimize system performance to reduce errors',
                  Icons.speed,
                  Colors.purple,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionCard(String title, String description, IconData icon, Color color) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color,
          child: Icon(icon, color: Colors.white),
        ),
        title: Text(title),
        subtitle: Text(description),
        trailing: IconButton(
          onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('Applied suggestion: $title')),
            );
          },
          icon: const Icon(Icons.check),
        ),
      ),
    );
  }

  void _showResolveDialog(ErrorLogEntry error) {
    final controller = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Resolve Error'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Resolution Notes',
            border: OutlineInputBorder(),
          ),
          maxLines: 3,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              _resolveError(error, controller.text);
              Navigator.pop(context);
            },
            child: const Text('Resolve'),
          ),
        ],
      ),
    );
  }

  void _showErrorDetails(ErrorLogEntry error) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(error.errorType),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Message: ${error.message}'),
              const SizedBox(height: 8),
              Text('Severity: ${error.severity.name}'),
              const SizedBox(height: 8),
              Text('Category: ${error.category.name}'),
              const SizedBox(height: 8),
              Text('Timestamp: ${_formatTimestamp(error.timestamp)}'),
              if (error.context.isNotEmpty) ...[
                const SizedBox(height: 8),
                const Text('Context:'),
                Text(error.context.toString()),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Color _getSeverityColor(ErrorSeverity severity) {
    switch (severity) {
      case ErrorSeverity.low:
        return Colors.green;
      case ErrorSeverity.medium:
        return Colors.orange;
      case ErrorSeverity.high:
        return Colors.red;
      case ErrorSeverity.critical:
        return Colors.purple;
    }
  }

  IconData _getSeverityIcon(ErrorSeverity severity) {
    switch (severity) {
      case ErrorSeverity.low:
        return Icons.info;
      case ErrorSeverity.medium:
        return Icons.warning;
      case ErrorSeverity.high:
        return Icons.error;
      case ErrorSeverity.critical:
        return Icons.dangerous;
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
