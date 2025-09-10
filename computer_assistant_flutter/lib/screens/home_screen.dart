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
import '../widgets/rag_widget.dart';
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
    _tabController = TabController(length: 7, vsync: this);
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
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.smart_toy,
                color: theme.colorScheme.onPrimaryContainer,
                size: 20,
              ),
            ),
            const SizedBox(width: 8),
            const Expanded(
              child: Text(
                'JARVIS Assistant',
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        actions: [
          ConnectionStatusWidget(),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _showSettingsDialog(context),
            tooltip: 'Settings',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabAlignment: TabAlignment.start,
          indicatorSize: TabBarIndicatorSize.tab,
          tabs: const [
            Tab(
              icon: Icon(Icons.mic_rounded),
              text: 'Voice',
              height: 60,
            ),
            Tab(
              icon: Icon(Icons.terminal_rounded),
              text: 'Terminal',
              height: 60,
            ),
            Tab(
              icon: Icon(Icons.chat_rounded),
              text: 'AI Chat',
              height: 60,
            ),
            Tab(
              icon: Icon(Icons.search_rounded),
              text: 'RAG',
              height: 60,
            ),
            Tab(
              icon: Icon(Icons.info_rounded),
              text: 'System',
              height: 60,
            ),
            Tab(
              icon: Icon(Icons.folder_rounded),
              text: 'Files',
              height: 60,
            ),
            Tab(
              icon: Icon(Icons.screenshot_rounded),
              text: 'Screen',
              height: 60,
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          const VoiceCommandWidget(),
          const TerminalWidget(),
          const AIChatWidget(),
          const RAGWidget(),
          const SystemInfoWidget(),
          const FileExplorerWidget(),
          const ScreenshotWidget(),
        ],
      ),
      floatingActionButton: _buildFloatingActionButton(appState),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
    );
  }

  Widget _buildFloatingActionButton(AppState appState) {
    final theme = Theme.of(context);
    
    if (!appState.isConnected) {
      return FloatingActionButton.extended(
        onPressed: () => _showConnectionDialog(context),
        icon: const Icon(Icons.wifi_off_rounded),
        label: const Text('Connect'),
        tooltip: 'Connect to Server',
        backgroundColor: theme.colorScheme.errorContainer,
        foregroundColor: theme.colorScheme.onErrorContainer,
      );
    }

    if (!appState.isAuthenticated) {
      return FloatingActionButton.extended(
        onPressed: () => _showAuthDialog(context),
        icon: const Icon(Icons.lock_rounded),
        label: const Text('Auth'),
        tooltip: 'Authenticate',
        backgroundColor: theme.colorScheme.secondaryContainer,
        foregroundColor: theme.colorScheme.onSecondaryContainer,
      );
    }

    return FloatingActionButton.extended(
      onPressed: () => _showQuickActionsDialog(context),
      icon: const Icon(Icons.add_rounded),
      label: const Text('Actions'),
      tooltip: 'Quick Actions',
    );
  }

  void _showConnectionDialog(BuildContext context) {
    final settings = ref.read(settingsProvider);
    final theme = Theme.of(context);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.wifi_rounded,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(width: 8),
            const Text('Connect to Server'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: theme.colorScheme.outline.withValues(alpha: 0.2),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline_rounded,
                    color: theme.colorScheme.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Connecting to: ${settings.serverUrl}',
                      style: theme.textTheme.bodyMedium,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: TextEditingController(text: settings.savedAuthToken ?? ''),
              decoration: InputDecoration(
                labelText: 'Auth Token (Optional)',
                hintText: 'Enter authentication token',
                prefixIcon: const Icon(Icons.key_rounded),
                filled: true,
              ),
              onChanged: (value) {
                ref.read(authTokenProvider.notifier).state = value.isEmpty ? null : value;
              },
            ),
            const SizedBox(height: 12),
            Text(
              'To change server settings, go to Settings → Connection Settings',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
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
                    SnackBar(
                      content: const Text('Connected to server'),
                      backgroundColor: theme.colorScheme.primaryContainer,
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Failed to connect to server'),
                      backgroundColor: theme.colorScheme.errorContainer,
                      behavior: SnackBarBehavior.floating,
                    ),
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
    final theme = Theme.of(context);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.lock_rounded,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(width: 8),
            const Text('Authenticate'),
          ],
        ),
        content: TextField(
          decoration: const InputDecoration(
            labelText: 'Auth Token',
            hintText: 'Enter authentication token',
            prefixIcon: Icon(Icons.key_rounded),
            filled: true,
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
          FilledButton(
            onPressed: () async {
              final authToken = ref.read(authTokenProvider);
              final success = await ref
                  .read(appStateProvider.notifier)
                  .authenticate(authToken ?? '');
              
              if (mounted) {
                Navigator.of(context).pop();
                if (success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Authentication successful'),
                      backgroundColor: theme.colorScheme.primaryContainer,
                      behavior: SnackBarBehavior.floating,
                    ),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Authentication failed'),
                      backgroundColor: theme.colorScheme.errorContainer,
                      behavior: SnackBarBehavior.floating,
                    ),
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
    final theme = Theme.of(context);
    
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: theme.colorScheme.outline.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Icon(
                  Icons.flash_on_rounded,
                  color: theme.colorScheme.primary,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  'Quick Actions',
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            GridView.count(
              shrinkWrap: true,
              crossAxisCount: 2,
              childAspectRatio: 1.2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              children: [
                _buildQuickActionButton(
                  context,
                  'System Info',
                  Icons.info_rounded,
                  () {
                    ref.read(appStateProvider.notifier).requestSystemInfo();
                    Navigator.of(context).pop();
                  },
                ),
                _buildQuickActionButton(
                  context,
                  'Screenshot',
                  Icons.screenshot_rounded,
                  () {
                    ref.read(appStateProvider.notifier).requestScreenshot();
                    Navigator.of(context).pop();
                  },
                ),
                _buildQuickActionButton(
                  context,
                  'File List',
                  Icons.folder_rounded,
                  () {
                    ref.read(appStateProvider.notifier).requestFileList('.');
                    Navigator.of(context).pop();
                  },
                ),
                _buildQuickActionButton(
                  context,
                  'Disconnect',
                  Icons.wifi_off_rounded,
                  () {
                    ref.read(appStateProvider.notifier).disconnect();
                    Navigator.of(context).pop();
                  },
                ),
              ],
            ),
            const SizedBox(height: 20),
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
    final theme = Theme.of(context);
    
    return Card(
      elevation: 0,
      color: theme.colorScheme.surfaceContainerHighest,
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: theme.colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  size: 24,
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                label,
                textAlign: TextAlign.center,
                style: theme.textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
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
