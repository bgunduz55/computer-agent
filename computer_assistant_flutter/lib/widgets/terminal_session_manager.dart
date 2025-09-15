/// Terminal Session Management Widget
/// 
/// Interactive terminal session creation and management
/// Integrates with backend T014 (Terminal Session Management)

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/backend_integration_models.dart';
import '../services/websocket_service.dart';
import '../shared/websocket_protocol.dart';

class TerminalSessionManager extends StatefulWidget {
  final bool showSessions;
  final bool showHistory;
  final bool showGroups;

  const TerminalSessionManager({
    Key? key,
    this.showSessions = true,
    this.showHistory = true,
    this.showGroups = true,
  }) : super(key: key);

  @override
  State<TerminalSessionManager> createState() => _TerminalSessionManagerState();
}

class _TerminalSessionManagerState extends State<TerminalSessionManager>
    with TickerProviderStateMixin {
  final WebSocketService _webSocketService = WebSocketService();
  final TextEditingController _commandController = TextEditingController();
  final ScrollController _outputScrollController = ScrollController();
  
  List<TerminalSession> _sessions = [];
  Map<String, List<TerminalCommand>> _sessionHistory = {};
  Map<String, String> _sessionOutputs = {};
  
  TerminalSession? _selectedSession;
  bool _isCreatingSession = false;
  bool _isExecutingCommand = false;
  
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _setupWebSocketListeners();
    _loadSessions();
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
        case MessageType.terminalSessionResponse:
          _handleSessionResponse(message);
          break;
        case MessageType.terminalSessionOutput:
          _handleSessionOutput(message);
          break;
        case MessageType.terminalSessionHistory:
          _handleSessionHistory(message);
          break;
        case MessageType.terminalSessionList:
          _handleSessionList(message);
          break;
        default:
          break;
      }
    }
  }

  void _handleSessionResponse(WebSocketMessage message) {
    final session = TerminalSession.fromJson(message.data['session']);
    
    setState(() {
      _sessions.add(session);
      _isCreatingSession = false;
    });
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Session "${session.name}" created successfully')),
    );
  }

  void _handleSessionOutput(WebSocketMessage message) {
    final command = TerminalCommand.fromJson(message.data);
    
    setState(() {
      if (!_sessionHistory.containsKey(command.sessionId)) {
        _sessionHistory[command.sessionId] = [];
      }
      _sessionHistory[command.sessionId]!.add(command);
      
      // Update session output
      _sessionOutputs[command.sessionId] = command.output ?? '';
      
      // Auto-scroll to bottom
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_outputScrollController.hasClients) {
          _outputScrollController.animateTo(
            _outputScrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    });
  }

  void _handleSessionHistory(WebSocketMessage message) {
    final history = (message.data['history'] as List<dynamic>)
        .map((item) => TerminalCommand.fromJson(item))
        .toList();
    
    setState(() {
      _sessionHistory[message.data['session_id']] = history;
    });
  }

  void _handleSessionList(WebSocketMessage message) {
    final sessions = (message.data['sessions'] as List<dynamic>)
        .map((item) => TerminalSession.fromJson(item))
        .toList();
    
    setState(() {
      _sessions = sessions;
    });
  }

  void _loadSessions() {
    _webSocketService.listTerminalSessions();
  }

  void _createSession() {
    showDialog(
      context: context,
      builder: (context) => _CreateSessionDialog(
        onSessionCreated: (sessionData) {
          setState(() {
            _isCreatingSession = true;
          });
          
          _webSocketService.createTerminalSession(
            name: sessionData['name'],
            sessionType: sessionData['sessionType'],
            terminalType: sessionData['terminalType'],
            workingDirectory: sessionData['workingDirectory'],
            description: sessionData['description'],
            tags: sessionData['tags'],
          );
        },
      ),
    );
  }

  void _selectSession(TerminalSession session) {
    setState(() {
      _selectedSession = session;
    });
    
    // Load session history
    _webSocketService.getTerminalSessionHistory(session.sessionId);
  }

  void _executeCommand(String command) {
    if (_selectedSession == null || command.trim().isEmpty) return;
    
    setState(() {
      _isExecutingCommand = true;
    });
    
    _webSocketService.executeTerminalSessionCommand(
      _selectedSession!.sessionId,
      command,
    );
    
    _commandController.clear();
  }

  void _deleteSession(TerminalSession session) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Session'),
        content: Text('Are you sure you want to delete "${session.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _sessions.remove(session);
                if (_selectedSession?.sessionId == session.sessionId) {
                  _selectedSession = null;
                }
              });
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    _commandController.dispose();
    _outputScrollController.dispose();
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
                _buildSessionsTab(),
                _buildTerminalTab(),
                _buildHistoryTab(),
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
              const Icon(Icons.terminal),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Terminal Session Manager',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              IconButton(
                onPressed: _createSession,
                icon: const Icon(Icons.add),
                tooltip: 'Create New Session',
              ),
              IconButton(
                onPressed: _loadSessions,
                icon: const Icon(Icons.refresh),
                tooltip: 'Refresh Sessions',
              ),
            ],
          ),
          const SizedBox(height: 16),
          TabBar(
            controller: _tabController,
            tabs: const [
              Tab(icon: Icon(Icons.list), text: 'Sessions'),
              Tab(icon: Icon(Icons.terminal), text: 'Terminal'),
              Tab(icon: Icon(Icons.history), text: 'History'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSessionsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Active Sessions (${_sessions.length})',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: _sessions.isEmpty
                ? _buildEmptySessions()
                : ListView.builder(
                    itemCount: _sessions.length,
                    itemBuilder: (context, index) {
                      final session = _sessions[index];
                      return _buildSessionCard(session);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptySessions() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.terminal,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No Terminal Sessions',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Create a new session to get started',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _createSession,
            icon: const Icon(Icons.add),
            label: const Text('Create Session'),
          ),
        ],
      ),
    );
  }

  Widget _buildSessionCard(TerminalSession session) {
    final isSelected = _selectedSession?.sessionId == session.sessionId;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      color: isSelected ? Theme.of(context).primaryColor.withOpacity(0.1) : null,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getSessionStatusColor(session.status),
          child: Icon(
            _getSessionStatusIcon(session.status),
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(
          session.name,
          style: TextStyle(
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${session.sessionType.name} • ${session.terminalType}'),
            if (session.workingDirectory != null)
              Text(
                session.workingDirectory!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              onPressed: () => _selectSession(session),
              icon: const Icon(Icons.open_in_new),
              tooltip: 'Open Session',
            ),
            IconButton(
              onPressed: () => _deleteSession(session),
              icon: const Icon(Icons.delete),
              tooltip: 'Delete Session',
            ),
          ],
        ),
        onTap: () => _selectSession(session),
      ),
    );
  }

  Widget _buildTerminalTab() {
    if (_selectedSession == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.terminal,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'No Session Selected',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Select a session from the Sessions tab',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        _buildTerminalHeader(),
        Expanded(
          child: _buildTerminalOutput(),
        ),
        _buildTerminalInput(),
      ],
    );
  }

  Widget _buildTerminalHeader() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        border: Border(
          bottom: BorderSide(color: Colors.grey[300]!),
        ),
      ),
      child: Row(
        children: [
          Icon(
            Icons.terminal,
            color: _getSessionStatusColor(_selectedSession!.status),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _selectedSession!.name,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  '${_selectedSession!.sessionType.name} • ${_selectedSession!.status}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          if (_isExecutingCommand)
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
        ],
      ),
    );
  }

  Widget _buildTerminalOutput() {
    final output = _sessionOutputs[_selectedSession!.sessionId] ?? '';
    
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8.0),
      ),
      child: SingleChildScrollView(
        controller: _outputScrollController,
        child: Text(
          output.isEmpty ? 'Terminal output will appear here...' : output,
          style: const TextStyle(
            fontFamily: 'monospace',
            color: Colors.green,
            fontSize: 12,
          ),
        ),
      ),
    );
  }

  Widget _buildTerminalInput() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        border: Border(
          top: BorderSide(color: Colors.grey[300]!),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _commandController,
              decoration: const InputDecoration(
                hintText: 'Enter command...',
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 8,
                ),
              ),
              onSubmitted: _executeCommand,
              enabled: !_isExecutingCommand,
            ),
          ),
          const SizedBox(width: 12),
          ElevatedButton(
            onPressed: _isExecutingCommand
                ? null
                : () => _executeCommand(_commandController.text),
            child: const Text('Execute'),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryTab() {
    if (_selectedSession == null) {
      return const Center(
        child: Text('Select a session to view history'),
      );
    }

    final history = _sessionHistory[_selectedSession!.sessionId] ?? [];
    
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Command History (${history.length})',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: history.isEmpty
                ? const Center(
                    child: Text('No commands executed yet'),
                  )
                : ListView.builder(
                    itemCount: history.length,
                    itemBuilder: (context, index) {
                      final command = history[index];
                      return _buildHistoryItem(command);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryItem(TerminalCommand command) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ExpansionTile(
        title: Text(
          command.command,
          style: const TextStyle(fontFamily: 'monospace'),
        ),
        subtitle: Text(
          'Exit code: ${command.exitCode ?? 'N/A'} • Duration: ${command.duration ?? 'N/A'}ms',
        ),
        children: [
          if (command.output != null) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8.0),
              ),
              child: Text(
                command.output!,
                style: const TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 12,
                ),
              ),
            ),
          ],
          if (command.error != null) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: Colors.red[50],
                borderRadius: BorderRadius.circular(8.0),
              ),
              child: Text(
                command.error!,
                style: TextStyle(
                  fontFamily: 'monospace',
                  fontSize: 12,
                  color: Colors.red[700],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Color _getSessionStatusColor(TerminalSessionStatus status) {
    switch (status) {
      case TerminalSessionStatus.active:
        return Colors.green;
      case TerminalSessionStatus.inactive:
        return Colors.grey;
      case TerminalSessionStatus.suspended:
        return Colors.orange;
      case TerminalSessionStatus.terminated:
        return Colors.red;
      case TerminalSessionStatus.error:
        return Colors.red;
    }
  }

  IconData _getSessionStatusIcon(TerminalSessionStatus status) {
    switch (status) {
      case TerminalSessionStatus.active:
        return Icons.play_arrow;
      case TerminalSessionStatus.inactive:
        return Icons.pause;
      case TerminalSessionStatus.suspended:
        return Icons.pause_circle;
      case TerminalSessionStatus.terminated:
        return Icons.stop;
      case TerminalSessionStatus.error:
        return Icons.error;
    }
  }
}

class _CreateSessionDialog extends StatefulWidget {
  final Function(Map<String, dynamic>) onSessionCreated;

  const _CreateSessionDialog({
    required this.onSessionCreated,
  });

  @override
  State<_CreateSessionDialog> createState() => _CreateSessionDialogState();
}

class _CreateSessionDialogState extends State<_CreateSessionDialog> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _workingDirectoryController = TextEditingController();
  
  TerminalSessionType _selectedSessionType = TerminalSessionType.interactive;
  String _selectedTerminalType = 'bash';
  List<String> _tags = [];

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _workingDirectoryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create Terminal Session'),
      content: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Session Name',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a session name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<TerminalSessionType>(
                value: _selectedSessionType,
                decoration: const InputDecoration(
                  labelText: 'Session Type',
                  border: OutlineInputBorder(),
                ),
                items: TerminalSessionType.values.map((type) {
                  return DropdownMenuItem(
                    value: type,
                    child: Text(type.name.toUpperCase()),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedSessionType = value!;
                  });
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedTerminalType,
                decoration: const InputDecoration(
                  labelText: 'Terminal Type',
                  border: OutlineInputBorder(),
                ),
                items: ['bash', 'powershell', 'cmd', 'zsh', 'fish'].map((type) {
                  return DropdownMenuItem(
                    value: type,
                    child: Text(type.toUpperCase()),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() {
                    _selectedTerminalType = value!;
                  });
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _workingDirectoryController,
                decoration: const InputDecoration(
                  labelText: 'Working Directory (optional)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description (optional)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 2,
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            if (_formKey.currentState!.validate()) {
              widget.onSessionCreated({
                'name': _nameController.text,
                'sessionType': _selectedSessionType.name,
                'terminalType': _selectedTerminalType,
                'workingDirectory': _workingDirectoryController.text.isEmpty
                    ? null
                    : _workingDirectoryController.text,
                'description': _descriptionController.text.isEmpty
                    ? null
                    : _descriptionController.text,
                'tags': _tags,
              });
              Navigator.pop(context);
            }
          },
          child: const Text('Create'),
        ),
      ],
    );
  }
}
