/// Command Execution Monitoring Widget
/// 
/// Real-time display of command execution with multi-step progress tracking
/// Integrates with backend T010 (Progress Tracking) and T005 (Context-Aware Execution)

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/backend_integration_models.dart';
import '../services/websocket_service.dart';
import '../providers/app_provider.dart';
import '../shared/websocket_protocol.dart';

class CommandExecutionMonitor extends StatefulWidget {
  final String? sessionId;
  final bool showHistory;
  final bool showContext;
  final bool showFeedback;

  const CommandExecutionMonitor({
    Key? key,
    this.sessionId,
    this.showHistory = true,
    this.showContext = true,
    this.showFeedback = true,
  }) : super(key: key);

  @override
  State<CommandExecutionMonitor> createState() => _CommandExecutionMonitorState();
}

class _CommandExecutionMonitorState extends State<CommandExecutionMonitor>
    with TickerProviderStateMixin {
  final WebSocketService _webSocketService = WebSocketService();
  final ScrollController _scrollController = ScrollController();
  
  List<ProgressUpdate> _progressUpdates = [];
  List<ExecutionContext> _executionContexts = [];
  List<FeedbackSubmission> _feedbackSubmissions = [];
  Map<String, List<TerminalCommand>> _commandHistory = {};
  
  String? _currentExecutionId;
  bool _isMonitoring = false;
  bool _isExpanded = false;
  
  late AnimationController _progressAnimationController;
  late AnimationController _pulseAnimationController;
  late Animation<double> _progressAnimation;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
    _setupWebSocketListeners();
    _startMonitoring();
  }

  void _setupAnimations() {
    _progressAnimationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    _pulseAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _progressAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _progressAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _pulseAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _pulseAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _pulseAnimationController.repeat(reverse: true);
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
        case MessageType.progressStart:
        case MessageType.progressUpdate:
        case MessageType.progressComplete:
        case MessageType.progressError:
          _handleProgressMessage(message);
          break;
        case MessageType.contextResponse:
          _handleContextMessage(message);
          break;
        case MessageType.feedbackResponse:
          _handleFeedbackMessage(message);
          break;
        case MessageType.terminalSessionOutput:
          _handleTerminalOutput(message);
          break;
        default:
          break;
      }
    }
  }

  void _handleProgressMessage(WebSocketMessage message) {
    final progressUpdate = ProgressUpdate.fromJson(message.data);
    
    setState(() {
      _progressUpdates.add(progressUpdate);
      _currentExecutionId = progressUpdate.executionId;
      
      // Animate progress
      _progressAnimationController.animateTo(progressUpdate.progress);
      
      // Auto-scroll to latest update
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    });
  }

  void _handleContextMessage(WebSocketMessage message) {
    final context = ExecutionContext.fromJson(message.data['context']);
    
    setState(() {
      _executionContexts.add(context);
    });
  }

  void _handleFeedbackMessage(WebSocketMessage message) {
    final feedback = FeedbackSubmission.fromJson(message.data['feedback']);
    
    setState(() {
      _feedbackSubmissions.add(feedback);
    });
  }

  void _handleTerminalOutput(WebSocketMessage message) {
    final command = TerminalCommand.fromJson(message.data);
    
    setState(() {
      if (!_commandHistory.containsKey(command.sessionId)) {
        _commandHistory[command.sessionId] = [];
      }
      _commandHistory[command.sessionId]!.add(command);
    });
  }

  void _startMonitoring() {
    setState(() {
      _isMonitoring = true;
    });
    
    // Request progress tracking for current session
    if (widget.sessionId != null) {
      _webSocketService.requestProgressTracking(widget.sessionId!);
    }
  }

  void _stopMonitoring() {
    setState(() {
      _isMonitoring = false;
    });
  }

  void _clearHistory() {
    setState(() {
      _progressUpdates.clear();
      _executionContexts.clear();
      _feedbackSubmissions.clear();
      _commandHistory.clear();
    });
  }

  void _submitFeedback(int rating, String? comment) {
    if (_currentExecutionId != null) {
      final feedback = FeedbackSubmission(
        executionId: _currentExecutionId!,
        rating: rating,
        comment: comment,
        timestamp: DateTime.now(),
      );
      
      _webSocketService.sendFeedback(_currentExecutionId!, feedback.toJson());
    }
  }

  @override
  void dispose() {
    _progressAnimationController.dispose();
    _pulseAnimationController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(8.0),
      child: Column(
        children: [
          _buildHeader(),
          if (_isExpanded) _buildExpandedContent(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    final latestProgress = _progressUpdates.isNotEmpty 
        ? _progressUpdates.last 
        : null;
    
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        children: [
          Icon(
            Icons.monitor_heart,
            color: _isMonitoring ? Colors.green : Colors.grey,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Command Execution Monitor',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (latestProgress != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    latestProgress.message,
                    style: Theme.of(context).textTheme.bodySmall,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ],
            ),
          ),
          if (latestProgress != null) ...[
            const SizedBox(width: 12),
            AnimatedBuilder(
              animation: _pulseAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: _isMonitoring ? _pulseAnimation.value : 1.0,
                  child: Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _getStatusColor(latestProgress.status),
                    ),
                  ),
                );
              },
            ),
          ],
          const SizedBox(width: 12),
          IconButton(
            icon: Icon(_isExpanded ? Icons.expand_less : Icons.expand_more),
            onPressed: () {
              setState(() {
                _isExpanded = !_isExpanded;
              });
            },
          ),
        ],
      ),
    );
  }

  Widget _buildExpandedContent() {
    return Container(
      height: 400,
      child: Column(
        children: [
          _buildProgressSection(),
          if (widget.showContext) _buildContextSection(),
          if (widget.showHistory) _buildHistorySection(),
          if (widget.showFeedback) _buildFeedbackSection(),
        ],
      ),
    );
  }

  Widget _buildProgressSection() {
    final latestProgress = _progressUpdates.isNotEmpty 
        ? _progressUpdates.last 
        : null;
    
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Progress',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              if (latestProgress != null)
                Text(
                  '${(latestProgress.progress * 100).toStringAsFixed(1)}%',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: _getStatusColor(latestProgress.status),
                    fontWeight: FontWeight.bold,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          if (latestProgress != null) ...[
            AnimatedBuilder(
              animation: _progressAnimation,
              builder: (context, child) {
                return LinearProgressIndicator(
                  value: latestProgress.progress,
                  backgroundColor: Colors.grey[300],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getStatusColor(latestProgress.status),
                  ),
                );
              },
            ),
            const SizedBox(height: 8),
            Text(
              latestProgress.status.toUpperCase(),
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: _getStatusColor(latestProgress.status),
                fontWeight: FontWeight.bold,
              ),
            ),
          ] else ...[
            LinearProgressIndicator(
              value: 0.0,
              backgroundColor: Colors.grey[300],
            ),
            const SizedBox(height: 8),
            Text(
              'No active execution',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildContextSection() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Execution Context',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_executionContexts.isNotEmpty) ...[
            Container(
              height: 100,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: _executionContexts.length,
                itemBuilder: (context, index) {
                  final execContext = _executionContexts[index];
                  return Container(
                    width: 200,
                    margin: const EdgeInsets.only(right: 8.0),
                    padding: const EdgeInsets.all(8.0),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey[300]!),
                      borderRadius: BorderRadius.circular(8.0),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Session: ${execContext.sessionId.substring(0, 8)}...',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Status: ${execContext.status}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        if (execContext.currentStep != null && execContext.totalSteps != null)
                          Text(
                            'Step: ${execContext.currentStep}/${execContext.totalSteps}',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ] else ...[
            Text(
              'No context available',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildHistorySection() {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'Execution History',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                TextButton.icon(
                  onPressed: _clearHistory,
                  icon: const Icon(Icons.clear, size: 16),
                  label: const Text('Clear'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                itemCount: _progressUpdates.length,
                itemBuilder: (context, index) {
                  final update = _progressUpdates[index];
                  return _buildProgressUpdateItem(update);
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressUpdateItem(ProgressUpdate update) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8.0),
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        border: Border.all(color: _getStatusColor(update.status)),
        borderRadius: BorderRadius.circular(8.0),
        color: _getStatusColor(update.status).withOpacity(0.1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                _getStatusIcon(update.status),
                size: 16,
                color: _getStatusColor(update.status),
              ),
              const SizedBox(width: 8),
              Text(
                update.status.toUpperCase(),
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: _getStatusColor(update.status),
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Text(
                '${(update.progress * 100).toStringAsFixed(1)}%',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            update.message,
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 4),
          Text(
            _formatTimestamp(update.timestamp),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackSection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Feedback',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: List.generate(5, (index) {
              return IconButton(
                onPressed: () => _submitFeedback(index + 1, null),
                icon: Icon(
                  Icons.star,
                  color: index < 3 ? Colors.orange : Colors.grey,
                ),
              );
            }),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'running':
      case 'active':
        return Colors.blue;
      case 'completed':
      case 'success':
        return Colors.green;
      case 'error':
      case 'failed':
        return Colors.red;
      case 'pending':
      case 'waiting':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'running':
      case 'active':
        return Icons.play_arrow;
      case 'completed':
      case 'success':
        return Icons.check_circle;
      case 'error':
      case 'failed':
        return Icons.error;
      case 'pending':
      case 'waiting':
        return Icons.pause;
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
