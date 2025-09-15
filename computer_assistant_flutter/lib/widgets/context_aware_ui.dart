/// Context-Aware UI Updates
/// 
/// Dynamic UI based on execution context and memory
/// Integrates with backend T005 (Context-Aware Execution)

import 'package:flutter/material.dart';
import '../models/backend_integration_models.dart';
import '../services/websocket_service.dart';
import '../shared/websocket_protocol.dart';

class ContextAwareUI extends StatefulWidget {
  final String? sessionId;
  final bool showContext;
  final bool showMemory;
  final bool showSuggestions;
  final bool showAdaptiveUI;

  const ContextAwareUI({
    Key? key,
    this.sessionId,
    this.showContext = true,
    this.showMemory = true,
    this.showSuggestions = true,
    this.showAdaptiveUI = true,
  }) : super(key: key);

  @override
  State<ContextAwareUI> createState() => _ContextAwareUIState();
}

class _ContextAwareUIState extends State<ContextAwareUI>
    with TickerProviderStateMixin {
  final WebSocketService _webSocketService = WebSocketService();
  final ScrollController _memoryScrollController = ScrollController();
  
  ExecutionContext? _currentContext;
  List<MemoryEntry> _memoryEntries = [];
  List<Map<String, dynamic>> _suggestions = [];
  Map<String, dynamic> _uiState = {};
  
  bool _isLoadingContext = false;
  bool _isLoadingMemory = false;
  bool _isAdaptiveMode = true;
  
  late AnimationController _contextAnimationController;
  late AnimationController _suggestionAnimationController;
  late Animation<double> _contextAnimation;
  late Animation<double> _suggestionAnimation;

  @override
  void initState() {
    super.initState();
    _setupAnimations();
    _setupWebSocketListeners();
    _loadContextData();
  }

  void _setupAnimations() {
    _contextAnimationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _suggestionAnimationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    _contextAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _contextAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _suggestionAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _suggestionAnimationController,
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
        case MessageType.contextResponse:
          _handleContextResponse(message);
          break;
        case MessageType.memoryRetrieve:
          _handleMemoryResponse(message);
          break;
        case MessageType.memorySearch:
          _handleMemorySearchResponse(message);
          break;
        default:
          break;
      }
    }
  }

  void _handleContextResponse(WebSocketMessage message) {
    final context = ExecutionContext.fromJson(message.data['context']);
    
    setState(() {
      _currentContext = context;
      _isLoadingContext = false;
    });
    
    _contextAnimationController.forward();
    _generateSuggestions();
  }

  void _handleMemoryResponse(WebSocketMessage message) {
    final memory = MemoryEntry.fromJson(message.data['memory']);
    
    setState(() {
      _memoryEntries.add(memory);
      _isLoadingMemory = false;
    });
  }

  void _handleMemorySearchResponse(WebSocketMessage message) {
    final entries = (message.data['entries'] as List<dynamic>)
        .map((item) => MemoryEntry.fromJson(item))
        .toList();
    
    setState(() {
      _memoryEntries = entries;
      _isLoadingMemory = false;
    });
  }

  void _loadContextData() {
    if (widget.sessionId != null) {
      _loadContext();
      _loadMemory();
    }
  }

  void _loadContext() {
    setState(() {
      _isLoadingContext = true;
    });
    
    _webSocketService.updateExecutionContext(widget.sessionId!, {});
  }

  void _loadMemory() {
    setState(() {
      _isLoadingMemory = true;
    });
    
    _webSocketService.searchMemoryEntries(
      widget.sessionId!,
      limit: 20,
    );
  }

  void _generateSuggestions() {
    if (_currentContext == null) return;
    
    final suggestions = <Map<String, dynamic>>[];
    
    // Generate context-based suggestions
    if (_currentContext!.commandSequence.isNotEmpty) {
      suggestions.add({
        'type': 'command',
        'title': 'Continue Command Sequence',
        'description': 'Execute next command in sequence',
        'action': 'continue_sequence',
        'icon': Icons.play_arrow,
        'color': Colors.blue,
      });
    }
    
    if (_currentContext!.variables.isNotEmpty) {
      suggestions.add({
        'type': 'variable',
        'title': 'View Variables',
        'description': 'Check current execution variables',
        'action': 'view_variables',
        'icon': Icons.code,
        'color': Colors.green,
      });
    }
    
    if (_currentContext!.status == 'error') {
      suggestions.add({
        'type': 'error',
        'title': 'Error Recovery',
        'description': 'Attempt to recover from error',
        'action': 'error_recovery',
        'icon': Icons.error_outline,
        'color': Colors.red,
      });
    }
    
    // Generate memory-based suggestions
    final recentMemory = _memoryEntries.take(5).toList();
    for (final entry in recentMemory) {
      if (entry.contextType == ContextType.userPreference) {
        suggestions.add({
          'type': 'preference',
          'title': 'Apply Preference',
          'description': 'Use saved user preference',
          'action': 'apply_preference',
          'data': entry.value,
          'icon': Icons.settings,
          'color': Colors.purple,
        });
      }
    }
    
    setState(() {
      _suggestions = suggestions;
    });
    
    _suggestionAnimationController.forward();
  }

  void _executeSuggestion(Map<String, dynamic> suggestion) {
    switch (suggestion['action']) {
      case 'continue_sequence':
        _continueCommandSequence();
        break;
      case 'view_variables':
        _showVariablesDialog();
        break;
      case 'error_recovery':
        _attemptErrorRecovery();
        break;
      case 'apply_preference':
        _applyPreference(suggestion['data']);
        break;
    }
  }

  void _continueCommandSequence() {
    if (_currentContext?.commandSequence.isNotEmpty == true) {
      final nextCommand = _currentContext!.commandSequence.first;
      _webSocketService.sendCommand(nextCommand);
    }
  }

  void _showVariablesDialog() {
    showDialog(
      context: context,
      builder: (context) => _VariablesDialog(
        variables: _currentContext?.variables ?? {},
      ),
    );
  }

  void _attemptErrorRecovery() {
    _webSocketService.sendSystemControl('error_recovery');
  }

  void _applyPreference(dynamic preference) {
    _webSocketService.updateExecutionContext(
      widget.sessionId!,
      {'preference': preference},
    );
  }

  void _storeMemoryEntry(String key, dynamic value, ContextType type) {
    _webSocketService.storeMemoryEntry(
      widget.sessionId!,
      key,
      value,
      contextType: type.name,
    );
  }

  void _searchMemory(String query) {
    _webSocketService.searchMemoryEntries(
      widget.sessionId!,
      query: query,
    );
  }

  @override
  void dispose() {
    _contextAnimationController.dispose();
    _suggestionAnimationController.dispose();
    _memoryScrollController.dispose();
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
            Icons.psychology,
            color: _isAdaptiveMode ? Colors.purple : Colors.grey,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Context-Aware UI',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (_currentContext != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    'Session: ${_currentContext!.sessionId.substring(0, 8)}...',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ],
            ),
          ),
          Switch(
            value: _isAdaptiveMode,
            onChanged: (value) {
              setState(() {
                _isAdaptiveMode = value;
              });
            },
            activeColor: Colors.purple,
          ),
          const SizedBox(width: 8),
          Text(
            _isAdaptiveMode ? 'Adaptive' : 'Static',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return Column(
      children: [
        if (widget.showContext) _buildContextSection(),
        if (widget.showMemory) _buildMemorySection(),
        if (widget.showSuggestions) _buildSuggestionsSection(),
        if (widget.showAdaptiveUI) _buildAdaptiveUISection(),
      ],
    );
  }

  Widget _buildContextSection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
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
          if (_isLoadingContext) ...[
            const Center(child: CircularProgressIndicator()),
          ] else if (_currentContext == null) ...[
            Text(
              'No context available',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ] else ...[
            AnimatedBuilder(
              animation: _contextAnimation,
              builder: (context, child) {
                return Opacity(
                  opacity: _contextAnimation.value,
                  child: _buildContextCard(_currentContext!),
                );
              },
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildContextCard(ExecutionContext execContext) {
    return Card(
      color: Colors.blue[50],
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: Colors.blue[700],
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Status: ${execContext.status.toUpperCase()}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.blue[700],
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (execContext.currentStep != null && execContext.totalSteps != null) ...[
              Text(
                'Step ${execContext.currentStep}/${execContext.totalSteps}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 4),
            ],
            if (execContext.commandSequence.isNotEmpty) ...[
              Text(
                'Commands: ${execContext.commandSequence.length}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 4),
            ],
            if (execContext.variables.isNotEmpty) ...[
              Text(
                'Variables: ${execContext.variables.length}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildMemorySection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Memory Entries',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              IconButton(
                onPressed: _loadMemory,
                icon: const Icon(Icons.refresh, size: 16),
                tooltip: 'Refresh Memory',
              ),
            ],
          ),
          const SizedBox(height: 8),
          if (_isLoadingMemory) ...[
            const Center(child: CircularProgressIndicator()),
          ] else if (_memoryEntries.isEmpty) ...[
            Text(
              'No memory entries available',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ] else ...[
            Container(
              height: 150,
              child: ListView.builder(
                controller: _memoryScrollController,
                itemCount: _memoryEntries.length,
                itemBuilder: (context, index) {
                  final entry = _memoryEntries[index];
                  return _buildMemoryEntryCard(entry);
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMemoryEntryCard(MemoryEntry entry) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getContextTypeColor(entry.contextType),
          child: Icon(
            _getContextTypeIcon(entry.contextType),
            color: Colors.white,
            size: 16,
          ),
        ),
        title: Text(
          entry.key,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(
          '${entry.contextType.name} • ${entry.priority.name}',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        trailing: Text(
          _formatTimestamp(entry.timestamp),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
          ),
        ),
      ),
    );
  }

  Widget _buildSuggestionsSection() {
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
          if (_suggestions.isEmpty) ...[
            Text(
              'No suggestions available',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ] else ...[
            AnimatedBuilder(
              animation: _suggestionAnimation,
              builder: (context, child) {
                return Opacity(
                  opacity: _suggestionAnimation.value,
                  child: Container(
                    height: 120,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _suggestions.length,
                      itemBuilder: (context, index) {
                        final suggestion = _suggestions[index];
                        return _buildSuggestionCard(suggestion);
                      },
                    ),
                  ),
                );
              },
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSuggestionCard(Map<String, dynamic> suggestion) {
    return Container(
      width: 200,
      margin: const EdgeInsets.only(right: 8.0),
      child: Card(
        child: InkWell(
          onTap: () => _executeSuggestion(suggestion),
          borderRadius: BorderRadius.circular(8.0),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      suggestion['icon'] as IconData,
                      color: suggestion['color'] as Color,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        suggestion['title'] as String,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  suggestion['description'] as String,
                  style: Theme.of(context).textTheme.bodySmall,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAdaptiveUISection() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Adaptive UI Controls',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _storeMemoryEntry(
                    'ui_preference',
                    'dark_mode',
                    ContextType.userPreference,
                  ),
                  icon: const Icon(Icons.dark_mode),
                  label: const Text('Dark Mode'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () => _storeMemoryEntry(
                    'ui_preference',
                    'light_mode',
                    ContextType.userPreference,
                  ),
                  icon: const Icon(Icons.light_mode),
                  label: const Text('Light Mode'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getContextTypeColor(ContextType type) {
    switch (type) {
      case ContextType.userPreference:
        return Colors.purple;
      case ContextType.systemState:
        return Colors.blue;
      case ContextType.executionHistory:
        return Colors.green;
      case ContextType.environment:
        return Colors.orange;
      case ContextType.temporary:
        return Colors.grey;
    }
  }

  IconData _getContextTypeIcon(ContextType type) {
    switch (type) {
      case ContextType.userPreference:
        return Icons.settings;
      case ContextType.systemState:
        return Icons.computer;
      case ContextType.executionHistory:
        return Icons.history;
      case ContextType.environment:
        return Icons.settings;
      case ContextType.temporary:
        return Icons.timer;
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

class _VariablesDialog extends StatelessWidget {
  final Map<String, dynamic> variables;

  const _VariablesDialog({
    required this.variables,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Execution Variables'),
      content: Container(
        width: double.maxFinite,
        child: ListView.builder(
          shrinkWrap: true,
          itemCount: variables.length,
          itemBuilder: (context, index) {
            final key = variables.keys.elementAt(index);
            final value = variables[key];
            return ListTile(
              title: Text(key),
              subtitle: Text(value.toString()),
            );
          },
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Close'),
        ),
      ],
    );
  }
}
