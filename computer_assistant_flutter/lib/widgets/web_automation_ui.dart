/// Advanced Web Automation UI
/// 
/// Web automation control panel and browser session management
/// Integrates with backend T002, T003 (Advanced Web Automation)

import 'package:flutter/material.dart';
import '../models/backend_integration_models.dart';
import '../services/websocket_service.dart';
import '../shared/websocket_protocol.dart';

class WebAutomationUI extends StatefulWidget {
  final String? sessionId;
  final bool showBrowser;
  final bool showAutomation;
  final bool showScreenshots;
  final bool showHistory;

  const WebAutomationUI({
    Key? key,
    this.sessionId,
    this.showBrowser = true,
    this.showAutomation = true,
    this.showScreenshots = true,
    this.showHistory = true,
  }) : super(key: key);

  @override
  State<WebAutomationUI> createState() => _WebAutomationUIState();
}

class _WebAutomationUIState extends State<WebAutomationUI>
    with TickerProviderStateMixin {
  final WebSocketService _webSocketService = WebSocketService();
  final ScrollController _historyScrollController = ScrollController();
  final TextEditingController _urlController = TextEditingController();
  final TextEditingController _searchController = TextEditingController();
  
  List<WebAutomationAction> _automationActions = [];
  List<Map<String, dynamic>> _browserSessions = [];
  List<Map<String, dynamic>> _screenshots = [];
  Map<String, dynamic> _currentSession = {};
  
  bool _isLoadingAutomation = false;
  bool _isLoadingScreenshots = false;
  bool _isAutomationRunning = false;
  bool _showBrowserControls = false;
  
  late TabController _tabController;
  late AnimationController _automationAnimationController;
  late AnimationController _screenshotAnimationController;
  late Animation<double> _automationAnimation;
  late Animation<double> _screenshotAnimation;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _setupAnimations();
    _setupWebSocketListeners();
    _loadAutomationData();
  }

  void _setupAnimations() {
    _automationAnimationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    
    _screenshotAnimationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    _automationAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _automationAnimationController,
      curve: Curves.easeInOut,
    ));
    
    _screenshotAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _screenshotAnimationController,
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
        case MessageType.webAutomationResponse:
          _handleAutomationResponse(message);
          break;
        case MessageType.webAutomationProgress:
          _handleAutomationProgress(message);
          break;
        case MessageType.webAutomationComplete:
          _handleAutomationComplete(message);
          break;
        case MessageType.webAutomationScreenshot:
          _handleScreenshotResponse(message);
          break;
        default:
          break;
      }
    }
  }

  void _handleAutomationResponse(WebSocketMessage message) {
    final action = WebAutomationAction.fromJson(message.data);
    
    setState(() {
      _automationActions.add(action);
      _isLoadingAutomation = false;
    });
    
    _automationAnimationController.forward();
  }

  void _handleAutomationProgress(WebSocketMessage message) {
    final progress = message.data['progress'] as double;
    final status = message.data['status'] as String;
    
    setState(() {
      _isAutomationRunning = true;
    });
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Automation progress: ${(progress * 100).toInt()}% - $status')),
    );
  }

  void _handleAutomationComplete(WebSocketMessage message) {
    final success = message.data['success'] as bool;
    final result = message.data['result'] as String?;
    
    setState(() {
      _isAutomationRunning = false;
    });
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(success ? 'Automation completed: $result' : 'Automation failed'),
        backgroundColor: success ? Colors.green : Colors.red,
      ),
    );
  }

  void _handleScreenshotResponse(WebSocketMessage message) {
    final screenshot = {
      'id': message.data['screenshot_id'],
      'url': message.data['screenshot_url'],
      'timestamp': DateTime.now(),
      'session_id': message.data['session_id'],
    };
    
    setState(() {
      _screenshots.add(screenshot);
      _isLoadingScreenshots = false;
    });
    
    _screenshotAnimationController.forward();
  }

  void _loadAutomationData() {
    _loadBrowserSessions();
    _loadScreenshots();
  }

  void _loadBrowserSessions() {
    // Simulate loading browser sessions
    setState(() {
      _browserSessions = [
        {
          'id': 'session_1',
          'name': 'Main Browser',
          'url': 'https://www.google.com',
          'status': 'active',
          'tabs': 3,
        },
        {
          'id': 'session_2',
          'name': 'Development',
          'url': 'https://github.com',
          'status': 'inactive',
          'tabs': 1,
        },
      ];
    });
  }

  void _loadScreenshots() {
    setState(() {
      _isLoadingScreenshots = true;
    });
    
    // Simulate loading screenshots
    Future.delayed(const Duration(seconds: 1), () {
      setState(() {
        _isLoadingScreenshots = false;
      });
    });
  }

  void _startAutomation(String action, Map<String, dynamic> parameters) {
    setState(() {
      _isLoadingAutomation = true;
    });
    
    _webSocketService.startWebAutomation(action, parameters);
  }

  void _takeScreenshot() {
    setState(() {
      _isLoadingScreenshots = true;
    });
    
    _webSocketService.requestScreenshot();
  }

  void _navigateToUrl(String url) {
    _startAutomation('navigate', {'url': url});
  }

  void _searchOnPage(String query) {
    _startAutomation('search', {'query': query});
  }

  void _clickElement(String selector) {
    _startAutomation('click', {'selector': selector});
  }

  void _fillForm(String selector, String value) {
    _startAutomation('fill_form', {'selector': selector, 'value': value});
  }

  void _scrollPage(String direction) {
    _startAutomation('scroll', {'direction': direction});
  }

  void _executeJavaScript(String script) {
    _startAutomation('execute_script', {'script': script});
  }

  void _showAutomationDialog() {
    showDialog(
      context: context,
      builder: (context) => _AutomationDialog(
        onAutomationStarted: _startAutomation,
      ),
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    _automationAnimationController.dispose();
    _screenshotAnimationController.dispose();
    _historyScrollController.dispose();
    _urlController.dispose();
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
                _buildBrowserTab(),
                _buildAutomationTab(),
                _buildScreenshotsTab(),
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
              const Icon(Icons.web),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Web Automation',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              if (_isAutomationRunning) ...[
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
                const SizedBox(width: 8),
              ],
              IconButton(
                onPressed: _takeScreenshot,
                icon: const Icon(Icons.camera_alt),
                tooltip: 'Take Screenshot',
              ),
              IconButton(
                onPressed: _showAutomationDialog,
                icon: const Icon(Icons.play_arrow),
                tooltip: 'Start Automation',
              ),
            ],
          ),
          const SizedBox(height: 16),
          TabBar(
            controller: _tabController,
            isScrollable: true,
            tabs: const [
              Tab(icon: Icon(Icons.browser_updated), text: 'Browser'),
              Tab(icon: Icon(Icons.smart_toy), text: 'Automation'),
              Tab(icon: Icon(Icons.camera), text: 'Screenshots'),
              Tab(icon: Icon(Icons.history), text: 'History'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildBrowserTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          _buildBrowserControls(),
          const SizedBox(height: 16),
          Expanded(
            child: _buildBrowserSessions(),
          ),
        ],
      ),
    );
  }

  Widget _buildBrowserControls() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Browser Controls',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _urlController,
                    decoration: const InputDecoration(
                      labelText: 'URL',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.link),
                    ),
                    onSubmitted: _navigateToUrl,
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _navigateToUrl(_urlController.text),
                  child: const Text('Go'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: const InputDecoration(
                      labelText: 'Search',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.search),
                    ),
                    onSubmitted: _searchOnPage,
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _searchOnPage(_searchController.text),
                  child: const Text('Search'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _scrollPage('up'),
                    icon: const Icon(Icons.keyboard_arrow_up),
                    label: const Text('Scroll Up'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _scrollPage('down'),
                    icon: const Icon(Icons.keyboard_arrow_down),
                    label: const Text('Scroll Down'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBrowserSessions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Browser Sessions',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Expanded(
          child: _browserSessions.isEmpty
              ? const Center(child: Text('No browser sessions available'))
              : ListView.builder(
                  itemCount: _browserSessions.length,
                  itemBuilder: (context, index) {
                    final session = _browserSessions[index];
                    return _buildBrowserSessionCard(session);
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildBrowserSessionCard(Map<String, dynamic> session) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getSessionStatusColor(session['status']),
          child: Icon(
            Icons.browser_updated,
            color: Colors.white,
          ),
        ),
        title: Text(session['name']),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(session['url']),
            Text('${session['tabs']} tabs • ${session['status']}'),
          ],
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              onPressed: () => _navigateToUrl(session['url']),
              icon: const Icon(Icons.open_in_new),
              tooltip: 'Open Session',
            ),
            IconButton(
              onPressed: () => _takeScreenshot(),
              icon: const Icon(Icons.camera_alt),
              tooltip: 'Take Screenshot',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAutomationTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Automation Actions',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_isLoadingAutomation) ...[
            const Center(child: CircularProgressIndicator()),
          ] else if (_automationActions.isEmpty) ...[
            const Center(child: Text('No automation actions yet')),
          ] else ...[
            Expanded(
              child: ListView.builder(
                itemCount: _automationActions.length,
                itemBuilder: (context, index) {
                  final action = _automationActions[index];
                  return _buildAutomationActionCard(action);
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildAutomationActionCard(WebAutomationAction action) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getActionStatusColor(action.status),
          child: Icon(
            _getActionIcon(action.action),
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(action.action),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Status: ${action.status}'),
            if (action.result != null) Text('Result: ${action.result}'),
          ],
        ),
        trailing: Text(
          _formatTimestamp(action.timestamp),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
          ),
        ),
      ),
    );
  }

  Widget _buildScreenshotsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Screenshots',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: _takeScreenshot,
                icon: const Icon(Icons.camera_alt),
                label: const Text('Take Screenshot'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          if (_isLoadingScreenshots) ...[
            const Center(child: CircularProgressIndicator()),
          ] else if (_screenshots.isEmpty) ...[
            const Center(child: Text('No screenshots available')),
          ] else ...[
            Expanded(
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 1.2,
                  crossAxisSpacing: 8,
                  mainAxisSpacing: 8,
                ),
                itemCount: _screenshots.length,
                itemBuilder: (context, index) {
                  final screenshot = _screenshots[index];
                  return _buildScreenshotCard(screenshot);
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildScreenshotCard(Map<String, dynamic> screenshot) {
    return Card(
      child: InkWell(
        onTap: () => _showScreenshotDialog(screenshot),
        borderRadius: BorderRadius.circular(8.0),
        child: Column(
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(8.0),
                  ),
                ),
                child: const Icon(
                  Icons.image,
                  size: 48,
                  color: Colors.grey,
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Text(
                _formatTimestamp(screenshot['timestamp']),
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Automation History',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: _automationActions.isEmpty
                ? const Center(child: Text('No automation history'))
                : ListView.builder(
                    controller: _historyScrollController,
                    itemCount: _automationActions.length,
                    itemBuilder: (context, index) {
                      final action = _automationActions[index];
                      return _buildHistoryItem(action);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryItem(WebAutomationAction action) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: Icon(
          _getActionIcon(action.action),
          color: _getActionStatusColor(action.status),
        ),
        title: Text(action.action),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Status: ${action.status}'),
            if (action.result != null) Text('Result: ${action.result}'),
            Text(
              _formatTimestamp(action.timestamp),
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
        trailing: PopupMenuButton(
          itemBuilder: (context) => [
            PopupMenuItem(
              value: 'repeat',
              child: const Text('Repeat Action'),
            ),
            PopupMenuItem(
              value: 'details',
              child: const Text('View Details'),
            ),
          ],
          onSelected: (value) {
            switch (value) {
              case 'repeat':
                _startAutomation(action.action, action.parameters);
                break;
              case 'details':
                _showActionDetails(action);
                break;
            }
          },
        ),
      ),
    );
  }

  void _showScreenshotDialog(Map<String, dynamic> screenshot) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Screenshot'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(8.0),
              ),
              child: const Icon(
                Icons.image,
                size: 64,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 16),
            Text('Taken: ${_formatTimestamp(screenshot['timestamp'])}'),
          ],
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

  void _showActionDetails(WebAutomationAction action) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(action.action),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Status: ${action.status}'),
              const SizedBox(height: 8),
              Text('Timestamp: ${_formatTimestamp(action.timestamp)}'),
              if (action.result != null) ...[
                const SizedBox(height: 8),
                Text('Result: ${action.result}'),
              ],
              if (action.parameters.isNotEmpty) ...[
                const SizedBox(height: 8),
                const Text('Parameters:'),
                Text(action.parameters.toString()),
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

  Color _getSessionStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'active':
        return Colors.green;
      case 'inactive':
        return Colors.grey;
      case 'error':
        return Colors.red;
      default:
        return Colors.blue;
    }
  }

  Color _getActionStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'success':
        return Colors.green;
      case 'running':
        return Colors.blue;
      case 'error':
        return Colors.red;
      case 'pending':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  IconData _getActionIcon(String action) {
    switch (action.toLowerCase()) {
      case 'navigate':
        return Icons.navigation;
      case 'click':
        return Icons.touch_app;
      case 'search':
        return Icons.search;
      case 'fill_form':
        return Icons.edit;
      case 'scroll':
        return Icons.swipe;
      case 'execute_script':
        return Icons.code;
      default:
        return Icons.smart_toy;
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

class _AutomationDialog extends StatefulWidget {
  final Function(String, Map<String, dynamic>) onAutomationStarted;

  const _AutomationDialog({
    required this.onAutomationStarted,
  });

  @override
  State<_AutomationDialog> createState() => _AutomationDialogState();
}

class _AutomationDialogState extends State<_AutomationDialog> {
  final _formKey = GlobalKey<FormState>();
  final _actionController = TextEditingController();
  final _parametersController = TextEditingController();
  
  String _selectedAction = 'navigate';

  @override
  void dispose() {
    _actionController.dispose();
    _parametersController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Start Automation'),
      content: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            DropdownButtonFormField<String>(
              value: _selectedAction,
              decoration: const InputDecoration(
                labelText: 'Action Type',
                border: OutlineInputBorder(),
              ),
              items: [
                'navigate',
                'click',
                'search',
                'fill_form',
                'scroll',
                'execute_script',
              ].map((action) {
                return DropdownMenuItem(
                  value: action,
                  child: Text(action.replaceAll('_', ' ').toUpperCase()),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedAction = value!;
                });
              },
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _actionController,
              decoration: const InputDecoration(
                labelText: 'Action Details',
                border: OutlineInputBorder(),
                hintText: 'e.g., URL, selector, query...',
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _parametersController,
              decoration: const InputDecoration(
                labelText: 'Parameters (JSON)',
                border: OutlineInputBorder(),
                hintText: '{"key": "value"}',
              ),
              maxLines: 3,
            ),
          ],
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
              final parameters = <String, dynamic>{
                'action': _actionController.text,
              };
              
              try {
                if (_parametersController.text.isNotEmpty) {
                  parameters.addAll(
                    Map<String, dynamic>.from(
                      // In a real app, you'd parse JSON here
                      {'custom': _parametersController.text},
                    ),
                  );
                }
              } catch (e) {
                // Handle JSON parsing error
              }
              
              widget.onAutomationStarted(_selectedAction, parameters);
              Navigator.pop(context);
            }
          },
          child: const Text('Start'),
        ),
      ],
    );
  }
}
