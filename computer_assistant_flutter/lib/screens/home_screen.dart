import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';
import '../providers/settings_provider.dart';
import '../widgets/connection_status_widget.dart';
import '../widgets/voice_command_widget.dart';
import '../widgets/terminal_widget.dart';
import '../widgets/ai_chat_widget.dart';
import '../widgets/system_info_widget.dart';
import '../widgets/file_explorer_widget.dart';
import '../widgets/screenshot_widget.dart';
import 'settings_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('JARVIS Assistant'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: theme.colorScheme.onPrimary,
        elevation: 4,
        actions: [
          ConnectionStatusWidget(),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _showSettingsDialog(context),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(icon: Icon(Icons.mic), text: 'Voice'),
            Tab(icon: Icon(Icons.terminal), text: 'Terminal'),
            Tab(icon: Icon(Icons.chat), text: 'AI Chat'),
            Tab(icon: Icon(Icons.info), text: 'System'),
            Tab(icon: Icon(Icons.folder), text: 'Files'),
            Tab(icon: Icon(Icons.screenshot), text: 'Screen'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          const VoiceCommandWidget(),
          const TerminalWidget(),
          const AIChatWidget(),
          const SystemInfoWidget(),
          const FileExplorerWidget(),
          const ScreenshotWidget(),
        ],
      ),
      floatingActionButton: _buildFloatingActionButton(appState),
    );
  }

  Widget _buildFloatingActionButton(AppState appState) {
    if (!appState.isConnected) {
      return FloatingActionButton(
        onPressed: () => _showConnectionDialog(context),
        child: const Icon(Icons.wifi_off),
        tooltip: 'Connect to Server',
      );
    }

    if (!appState.isAuthenticated) {
      return FloatingActionButton(
        onPressed: () => _showAuthDialog(context),
        child: const Icon(Icons.lock),
        tooltip: 'Authenticate',
      );
    }

    return FloatingActionButton(
      onPressed: () => _showQuickActionsDialog(context),
      child: const Icon(Icons.add),
      tooltip: 'Quick Actions',
    );
  }

  void _showConnectionDialog(BuildContext context) {
    final settings = ref.read(settingsProvider);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Connect to Server'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: Theme.of(context).colorScheme.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Connecting to: ${settings.serverUrl}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: TextEditingController(text: settings.savedAuthToken ?? ''),
              decoration: const InputDecoration(
                labelText: 'Auth Token (Optional)',
                hintText: 'Enter authentication token',
                prefixIcon: Icon(Icons.key),
              ),
              onChanged: (value) {
                ref.read(authTokenProvider.notifier).state = value.isEmpty ? null : value;
              },
            ),
            const SizedBox(height: 8),
            Text(
              'To change server settings, go to Settings → Connection Settings',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final serverUrl = settings.serverUrl;
              final authToken = ref.read(authTokenProvider);
              final success = await ref
                  .read(appStateProvider.notifier)
                  .connect(serverUrl, authToken: authToken);
              
              if (mounted) {
                Navigator.of(context).pop();
                if (success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Connected to server')),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Failed to connect to server')),
                  );
                }
              }
            },
            child: const Text('Connect'),
          ),
        ],
      ),
    );
  }

  void _showAuthDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Authenticate'),
        content: TextField(
          decoration: const InputDecoration(
            labelText: 'Auth Token',
            hintText: 'Enter authentication token',
          ),
              onChanged: (value) {
                ref.read(authTokenProvider.notifier).state = value;
              },
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final authToken = ref.read(authTokenProvider);
              final success = await ref
                  .read(appStateProvider.notifier)
                  .authenticate(authToken ?? '');
              
              if (mounted) {
                Navigator.of(context).pop();
                if (success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Authentication successful')),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Authentication failed')),
                  );
                }
              }
            },
            child: const Text('Authenticate'),
          ),
        ],
      ),
    );
  }

  void _showQuickActionsDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Quick Actions',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              crossAxisCount: 2,
              childAspectRatio: 2,
              children: [
                _buildQuickActionButton(
                  context,
                  'System Info',
                  Icons.info,
                  () {
                    ref.read(appStateProvider.notifier).requestSystemInfo();
                    Navigator.of(context).pop();
                  },
                ),
                _buildQuickActionButton(
                  context,
                  'Screenshot',
                  Icons.screenshot,
                  () {
                    ref.read(appStateProvider.notifier).requestScreenshot();
                    Navigator.of(context).pop();
                  },
                ),
                _buildQuickActionButton(
                  context,
                  'File List',
                  Icons.folder,
                  () {
                    ref.read(appStateProvider.notifier).requestFileList('.');
                    Navigator.of(context).pop();
                  },
                ),
                _buildQuickActionButton(
                  context,
                  'Disconnect',
                  Icons.wifi_off,
                  () {
                    ref.read(appStateProvider.notifier).disconnect();
                    Navigator.of(context).pop();
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionButton(
    BuildContext context,
    String label,
    IconData icon,
    VoidCallback onPressed,
  ) {
    return Card(
      child: InkWell(
        onTap: onPressed,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 32),
            const SizedBox(height: 8),
            Text(label, textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  void _showSettingsDialog(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => const SettingsScreen(),
      ),
    );
  }
}
