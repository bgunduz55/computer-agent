/// Progress Tracking and Feedback System
/// 
/// Real-time progress tracking and user feedback collection
/// Integrates with backend T010 (Progress Tracking) and T010 (Feedback System)

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/backend_integration_models.dart';
import '../services/websocket_service.dart';
import '../shared/websocket_protocol.dart';

class ProgressFeedbackSystem extends StatefulWidget {
  final String? sessionId;
  final bool showProgress;
  final bool showFeedback;
  final bool showHistory;
  final bool showAnalytics;

  const ProgressFeedbackSystem({
    Key? key,
    this.sessionId,
    this.showProgress = true,
    this.showFeedback = true,
    this.showHistory = true,
    this.showAnalytics = true,
  }) : super(key: key);

  @override
  State<ProgressFeedbackSystem> createState() => _ProgressFeedbackSystemState();
}

class _ProgressFeedbackSystemState extends State<ProgressFeedbackSystem>
    with TickerProviderStateMixin {
  final WebSocketService _webSocketService = WebSocketService();
  final ScrollController _historyScrollController = ScrollController();
  final TextEditingController _feedbackController = TextEditingController();
  
  List<ProgressUpdate> _progressUpdates = [];
  List<FeedbackSubmission> _feedbackSubmissions = [];
  Map<String, dynamic> _currentExecution = {};
  Map<String, dynamic> _feedbackAnalytics = {};
  
  bool _isTracking = false;
  bool _isSubmittingFeedback = false;
  bool _showFeedbackForm = false;
  
  late AnimationController _progressAnimationController;
  late AnimationController _pulseAnimationController;
  late Animation<double> _progressAnimation;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
    _setupWebSocketListeners();
    _startTracking();
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
        case MessageType.feedbackResponse:
          _handleFeedbackResponse(message);
          break;
        case MessageType.analyticsResponse:
          _handleFeedbackAnalytics(message);
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
      _currentExecution = {
        'execution_id': progressUpdate.executionId,
        'status': progressUpdate.status,
        'progress': progressUpdate.progress,
        'message': progressUpdate.message,
      };
      
      // Animate progress
      _progressAnimationController.animateTo(progressUpdate.progress);
      
      // Auto-scroll to latest update
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_historyScrollController.hasClients) {
          _historyScrollController.animateTo(
            _historyScrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    });
  }

  void _handleFeedbackResponse(WebSocketMessage message) {
    setState(() {
      _isSubmittingFeedback = false;
    });
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Feedback submitted successfully')),
    );
  }

  void _handleFeedbackAnalytics(WebSocketMessage message) {
    setState(() {
      _feedbackAnalytics = message.data;
    });
  }

  void _startTracking() {
    setState(() {
      _isTracking = true;
    });
    
    if (widget.sessionId != null) {
      _webSocketService.requestProgressTracking(widget.sessionId!);
    }
  }

  void _stopTracking() {
    setState(() {
      _isTracking = false;
    });
  }

  void _submitFeedback(int rating, String? comment) {
    if (_currentExecution['execution_id'] == null) return;
    
    setState(() {
      _isSubmittingFeedback = true;
    });
    
    final feedback = FeedbackSubmission(
      executionId: _currentExecution['execution_id'],
      rating: rating,
      comment: comment,
      timestamp: DateTime.now(),
    );
    
    _webSocketService.sendFeedback(_currentExecution['execution_id'], feedback.toJson());
    
    setState(() {
      _feedbackSubmissions.add(feedback);
      _showFeedbackForm = false;
      _feedbackController.clear();
    });
  }

  void _showFeedbackDialog() {
    showDialog(
      context: context,
      builder: (context) => _FeedbackDialog(
        onFeedbackSubmitted: _submitFeedback,
        isSubmitting: _isSubmittingFeedback,
      ),
    );
  }

  void _clearHistory() {
    setState(() {
      _progressUpdates.clear();
      _feedbackSubmissions.clear();
      _currentExecution.clear();
    });
  }

  @override
  void dispose() {
    _progressAnimationController.dispose();
    _pulseAnimationController.dispose();
    _historyScrollController.dispose();
    _feedbackController.dispose();
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
            child: _buildContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        children: [
          Icon(
            Icons.track_changes,
            color: _isTracking ? Colors.green : Colors.grey,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Progress & Feedback',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (_currentExecution.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Text(
                    _currentExecution['message'] ?? 'No active execution',
                    style: Theme.of(context).textTheme.bodySmall,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ],
            ),
          ),
          if (_currentExecution.isNotEmpty) ...[
            const SizedBox(width: 12),
            AnimatedBuilder(
              animation: _pulseAnimation,
              builder: (context, child) {
                return Transform.scale(
                  scale: _isTracking ? _pulseAnimation.value : 1.0,
                  child: Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _getStatusColor(_currentExecution['status'] ?? ''),
                    ),
                  ),
                );
              },
            ),
          ],
          const SizedBox(width: 12),
          IconButton(
            onPressed: _showFeedbackDialog,
            icon: const Icon(Icons.feedback),
            tooltip: 'Submit Feedback',
          ),
          IconButton(
            onPressed: _clearHistory,
            icon: const Icon(Icons.clear),
            tooltip: 'Clear History',
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return Column(
      children: [
        if (widget.showProgress) _buildProgressSection(),
        if (widget.showFeedback) _buildFeedbackSection(),
        if (widget.showHistory) _buildHistorySection(),
        if (widget.showAnalytics) _buildAnalyticsSection(),
      ],
    );
  }

  Widget _buildProgressSection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Current Progress',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              if (_currentExecution.isNotEmpty)
                Text(
                  '${(_currentExecution['progress'] * 100).toStringAsFixed(1)}%',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: _getStatusColor(_currentExecution['status'] ?? ''),
                    fontWeight: FontWeight.bold,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          if (_currentExecution.isNotEmpty) ...[
            AnimatedBuilder(
              animation: _progressAnimation,
              builder: (context, child) {
                return LinearProgressIndicator(
                  value: _currentExecution['progress'],
                  backgroundColor: Colors.grey[300],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getStatusColor(_currentExecution['status'] ?? ''),
                  ),
                );
              },
            ),
            const SizedBox(height: 8),
            Text(
              _currentExecution['status']?.toUpperCase() ?? '',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: _getStatusColor(_currentExecution['status'] ?? ''),
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

  Widget _buildFeedbackSection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Recent Feedback',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_feedbackSubmissions.isEmpty) ...[
            Text(
              'No feedback submitted yet',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ] else ...[
            Container(
              height: 100,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: _feedbackSubmissions.length,
                itemBuilder: (context, index) {
                  final feedback = _feedbackSubmissions[index];
                  return _buildFeedbackCard(feedback);
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildFeedbackCard(FeedbackSubmission feedback) {
    return Container(
      width: 200,
      margin: const EdgeInsets.only(right: 8.0),
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(8.0),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              ...List.generate(5, (index) {
                return Icon(
                  Icons.star,
                  size: 16,
                  color: index < feedback.rating ? Colors.orange : Colors.grey,
                );
              }),
            ],
          ),
          const SizedBox(height: 8),
          if (feedback.comment != null) ...[
            Text(
              feedback.comment!,
              style: Theme.of(context).textTheme.bodySmall,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
          ],
          Text(
            _formatTimestamp(feedback.timestamp),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
          ),
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
            Text(
              'Progress History',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: _progressUpdates.isEmpty
                  ? const Center(
                      child: Text('No progress updates yet'),
                    )
                  : ListView.builder(
                      controller: _historyScrollController,
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

  Widget _buildAnalyticsSection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Feedback Analytics',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_feedbackAnalytics.isEmpty) ...[
            Text(
              'No analytics data available',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ] else ...[
            Row(
              children: [
                Expanded(
                  child: _buildAnalyticsItem(
                    'Total Feedback',
                    _feedbackAnalytics['total_feedback']?.toString() ?? '0',
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildAnalyticsItem(
                    'Average Rating',
                    _feedbackAnalytics['average_rating']?.toString() ?? '0.0',
                    Colors.green,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAnalyticsItem(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8.0),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: color,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Colors.grey[600],
            ),
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

class _FeedbackDialog extends StatefulWidget {
  final Function(int, String?) onFeedbackSubmitted;
  final bool isSubmitting;

  const _FeedbackDialog({
    required this.onFeedbackSubmitted,
    required this.isSubmitting,
  });

  @override
  State<_FeedbackDialog> createState() => _FeedbackDialogState();
}

class _FeedbackDialogState extends State<_FeedbackDialog> {
  int _rating = 0;
  final TextEditingController _commentController = TextEditingController();

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Submit Feedback'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'How would you rate this execution?',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(5, (index) {
              return IconButton(
                onPressed: () {
                  setState(() {
                    _rating = index + 1;
                  });
                },
                icon: Icon(
                  Icons.star,
                  color: index < _rating ? Colors.orange : Colors.grey,
                  size: 32,
                ),
              );
            }),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _commentController,
            decoration: const InputDecoration(
              labelText: 'Comments (optional)',
              border: OutlineInputBorder(),
              hintText: 'Share your thoughts...',
            ),
            maxLines: 3,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: widget.isSubmitting ? null : () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: widget.isSubmitting || _rating == 0
              ? null
              : () {
                  widget.onFeedbackSubmitted(_rating, _commentController.text.isEmpty ? null : _commentController.text);
                  Navigator.pop(context);
                },
          child: widget.isSubmitting
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Submit'),
        ),
      ],
    );
  }
}
