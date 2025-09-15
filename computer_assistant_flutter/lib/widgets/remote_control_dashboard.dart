/// Advanced Remote Control Dashboard
/// 
/// System information, file browser, and application launcher
/// Integrates with backend T013 (Remote Control) and T015 (Analytics)

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/backend_integration_models.dart';
import '../services/websocket_service.dart';
import '../shared/websocket_protocol.dart';

class RemoteControlDashboard extends StatefulWidget {
  final bool showSystemInfo;
  final bool showFileBrowser;
  final bool showAppLauncher;
  final bool showQuickActions;

  const RemoteControlDashboard({
    Key? key,
    this.showSystemInfo = true,
    this.showFileBrowser = true,
    this.showAppLauncher = true,
    this.showQuickActions = true,
  }) : super(key: key);

  @override
  State<RemoteControlDashboard> createState() => _RemoteControlDashboardState();
}

class _RemoteControlDashboardState extends State<RemoteControlDashboard>
    with TickerProviderStateMixin {
  final WebSocketService _webSocketService = WebSocketService();
  final TextEditingController _pathController = TextEditingController();
  final ScrollController _fileScrollController = ScrollController();
  
  Map<String, dynamic> _systemInfo = {};
  List<Map<String, dynamic>> _fileList = [];
  List<Map<String, dynamic>> _applications = [];
  List<Map<String, dynamic>> _quickActions = [];
  
  String _currentPath = '/';
  bool _isLoadingSystemInfo = false;
  bool _isLoadingFiles = false;
  bool _isLoadingApplications = false;
  
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
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
        case MessageType.systemResponse:
          _handleSystemInfo(message);
          break;
        case MessageType.fileResponse:
          _handleFileList(message);
          break;
        case MessageType.capabilityResponse:
          _handleApplications(message);
          break;
        case MessageType.screenshotResponse:
          _handleScreenshot(message);
          break;
        default:
          break;
      }
    }
  }

  void _handleSystemInfo(WebSocketMessage message) {
    setState(() {
      _systemInfo = message.data;
      _isLoadingSystemInfo = false;
    });
  }

  void _handleFileList(WebSocketMessage message) {
    setState(() {
      _fileList = (message.data['files'] as List<dynamic>)
          .map((item) => Map<String, dynamic>.from(item))
          .toList();
      _isLoadingFiles = false;
    });
  }

  void _handleApplications(WebSocketMessage message) {
    setState(() {
      _applications = (message.data['applications'] as List<dynamic>)
          .map((item) => Map<String, dynamic>.from(item))
          .toList();
      _isLoadingApplications = false;
    });
  }

  void _handleScreenshot(WebSocketMessage message) {
    // Handle screenshot response
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Screenshot captured')),
    );
  }

  void _loadInitialData() {
    _loadSystemInfo();
    _loadFileList(_currentPath);
    _loadApplications();
    _loadQuickActions();
  }

  void _loadSystemInfo() {
    setState(() {
      _isLoadingSystemInfo = true;
    });
    _webSocketService.requestSystemInfo();
  }

  void _loadFileList(String path) {
    setState(() {
      _isLoadingFiles = true;
      _currentPath = path;
      _pathController.text = path;
    });
    _webSocketService.requestFileList(path);
  }

  void _loadApplications() {
    setState(() {
      _isLoadingApplications = true;
    });
    _webSocketService.requestCapabilities();
  }

  void _loadQuickActions() {
    setState(() {
      _quickActions = [
        {
          'name': 'Take Screenshot',
          'icon': Icons.screenshot,
          'action': 'screenshot',
          'color': Colors.blue,
        },
        {
          'name': 'Open Terminal',
          'icon': Icons.terminal,
          'action': 'terminal',
          'color': Colors.green,
        },
        {
          'name': 'File Explorer',
          'icon': Icons.folder,
          'action': 'file_explorer',
          'color': Colors.orange,
        },
        {
          'name': 'System Monitor',
          'icon': Icons.monitor,
          'action': 'system_monitor',
          'color': Colors.purple,
        },
        {
          'name': 'Web Browser',
          'icon': Icons.web,
          'action': 'web_browser',
          'color': Colors.cyan,
        },
        {
          'name': 'Text Editor',
          'icon': Icons.edit,
          'action': 'text_editor',
          'color': Colors.indigo,
        },
      ];
    });
  }

  void _executeQuickAction(Map<String, dynamic> action) {
    switch (action['action']) {
      case 'screenshot':
        _webSocketService.requestScreenshot();
        break;
      case 'terminal':
        _webSocketService.sendTerminalCommand('start');
        break;
      case 'file_explorer':
        _loadFileList(_currentPath);
        break;
      case 'system_monitor':
        _loadSystemInfo();
        break;
      case 'web_browser':
        _webSocketService.sendSystemControl('open_browser');
        break;
      case 'text_editor':
        _webSocketService.sendSystemControl('open_text_editor');
        break;
    }
  }

  void _navigateToPath(String path) {
    _loadFileList(path);
  }

  void _navigateUp() {
    final parentPath = _currentPath.split('/').where((s) => s.isNotEmpty).toList();
    if (parentPath.isNotEmpty) {
      parentPath.removeLast();
      final newPath = parentPath.isEmpty ? '/' : '/${parentPath.join('/')}';
      _navigateToPath(newPath);
    }
  }

  void _launchApplication(Map<String, dynamic> app) {
    _webSocketService.sendSystemControl('launch_app', params: {
      'name': app['name'],
      'path': app['path'],
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _pathController.dispose();
    _fileScrollController.dispose();
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
                _buildSystemInfoTab(),
                _buildFileBrowserTab(),
                _buildAppLauncherTab(),
                _buildQuickActionsTab(),
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
              const Icon(Icons.dashboard),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Remote Control Dashboard',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              IconButton(
                onPressed: _loadInitialData,
                icon: const Icon(Icons.refresh),
                tooltip: 'Refresh All',
              ),
            ],
          ),
          const SizedBox(height: 16),
          TabBar(
            controller: _tabController,
            isScrollable: true,
            tabs: const [
              Tab(icon: Icon(Icons.info), text: 'System'),
              Tab(icon: Icon(Icons.folder), text: 'Files'),
              Tab(icon: Icon(Icons.apps), text: 'Apps'),
              Tab(icon: Icon(Icons.flash_on), text: 'Quick'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSystemInfoTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: _isLoadingSystemInfo
          ? const Center(child: CircularProgressIndicator())
          : _systemInfo.isEmpty
              ? const Center(child: Text('No system information available'))
              : ListView(
                  children: [
                    _buildSystemInfoCard('Operating System', [
                      _systemInfo['os_name'] ?? 'Unknown',
                      _systemInfo['os_version'] ?? 'Unknown',
                      _systemInfo['os_arch'] ?? 'Unknown',
                    ]),
                    _buildSystemInfoCard('Hardware', [
                      'CPU: ${_systemInfo['cpu_count'] ?? 'Unknown'} cores',
                      'RAM: ${_systemInfo['memory_total'] ?? 'Unknown'} MB',
                      'Disk: ${_systemInfo['disk_total'] ?? 'Unknown'} GB',
                    ]),
                    _buildSystemInfoCard('Network', [
                      'Hostname: ${_systemInfo['hostname'] ?? 'Unknown'}',
                      'IP: ${_systemInfo['ip_address'] ?? 'Unknown'}',
                      'Status: ${_systemInfo['network_status'] ?? 'Unknown'}',
                    ]),
                    _buildSystemInfoCard('Performance', [
                      'CPU Usage: ${_systemInfo['cpu_usage'] ?? 'Unknown'}%',
                      'Memory Usage: ${_systemInfo['memory_usage'] ?? 'Unknown'}%',
                      'Disk Usage: ${_systemInfo['disk_usage'] ?? 'Unknown'}%',
                    ]),
                  ],
                ),
    );
  }

  Widget _buildSystemInfoCard(String title, List<String> items) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            ...items.map((item) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 2.0),
                  child: Text(
                    item,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                )),
          ],
        ),
      ),
    );
  }

  Widget _buildFileBrowserTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          _buildPathNavigator(),
          const SizedBox(height: 16),
          Expanded(
            child: _isLoadingFiles
                ? const Center(child: CircularProgressIndicator())
                : _fileList.isEmpty
                    ? const Center(child: Text('No files found'))
                    : ListView.builder(
                        controller: _fileScrollController,
                        itemCount: _fileList.length,
                        itemBuilder: (context, index) {
                          final file = _fileList[index];
                          return _buildFileItem(file);
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildPathNavigator() {
    return Row(
      children: [
        IconButton(
          onPressed: _currentPath != '/' ? _navigateUp : null,
          icon: const Icon(Icons.arrow_upward),
          tooltip: 'Go Up',
        ),
        Expanded(
          child: TextField(
            controller: _pathController,
            decoration: const InputDecoration(
              labelText: 'Current Path',
              border: OutlineInputBorder(),
              contentPadding: EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 8,
              ),
            ),
            onSubmitted: _navigateToPath,
          ),
        ),
        IconButton(
          onPressed: () => _navigateToPath(_pathController.text),
          icon: const Icon(Icons.search),
          tooltip: 'Navigate',
        ),
      ],
    );
  }

  Widget _buildFileItem(Map<String, dynamic> file) {
    final isDirectory = file['type'] == 'directory';
    final name = file['name'] as String;
    final size = file['size'] as int?;
    final modified = file['modified'] as String?;
    
    return Card(
      margin: const EdgeInsets.only(bottom: 8.0),
      child: ListTile(
        leading: Icon(
          isDirectory ? Icons.folder : Icons.insert_drive_file,
          color: isDirectory ? Colors.blue : Colors.grey[600],
        ),
        title: Text(name),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (size != null && !isDirectory)
              Text('${_formatFileSize(size)}'),
            if (modified != null)
              Text(
                'Modified: ${_formatDate(modified)}',
                style: Theme.of(context).textTheme.bodySmall,
              ),
          ],
        ),
        trailing: isDirectory
            ? IconButton(
                onPressed: () => _navigateToPath('$_currentPath/$name'),
                icon: const Icon(Icons.arrow_forward),
                tooltip: 'Open Directory',
              )
            : IconButton(
                onPressed: () => _openFile(file),
                icon: const Icon(Icons.open_in_new),
                tooltip: 'Open File',
              ),
        onTap: isDirectory
            ? () => _navigateToPath('$_currentPath/$name')
            : () => _openFile(file),
      ),
    );
  }

  Widget _buildAppLauncherTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: _isLoadingApplications
          ? const Center(child: CircularProgressIndicator())
          : _applications.isEmpty
              ? const Center(child: Text('No applications available'))
              : GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    childAspectRatio: 1.2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                  ),
                  itemCount: _applications.length,
                  itemBuilder: (context, index) {
                    final app = _applications[index];
                    return _buildAppCard(app);
                  },
                ),
    );
  }

  Widget _buildAppCard(Map<String, dynamic> app) {
    return Card(
      child: InkWell(
        onTap: () => _launchApplication(app),
        borderRadius: BorderRadius.circular(8.0),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.apps,
                size: 48,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(height: 8),
              Text(
                app['name'] ?? 'Unknown App',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Text(
                app['category'] ?? 'Application',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionsTab() {
    return Container(
      padding: const EdgeInsets.all(16.0),
      child: GridView.builder(
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 1.2,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
        ),
        itemCount: _quickActions.length,
        itemBuilder: (context, index) {
          final action = _quickActions[index];
          return _buildQuickActionCard(action);
        },
      ),
    );
  }

  Widget _buildQuickActionCard(Map<String, dynamic> action) {
    return Card(
      child: InkWell(
        onTap: () => _executeQuickAction(action),
        borderRadius: BorderRadius.circular(8.0),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                action['icon'] as IconData,
                size: 48,
                color: action['color'] as Color,
              ),
              const SizedBox(height: 8),
              Text(
                action['name'] as String,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _openFile(Map<String, dynamic> file) {
    _webSocketService.sendSystemControl('open_file', params: {
      'path': '$_currentPath/${file['name']}',
      'type': file['type'],
    });
  }

  String _formatFileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateString;
    }
  }
}
