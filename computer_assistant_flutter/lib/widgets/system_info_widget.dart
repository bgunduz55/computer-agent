import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';
import '../models/websocket_message.dart';

class SystemInfoWidget extends ConsumerWidget {
  const SystemInfoWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // System Info Header
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Icon(Icons.info, color: theme.colorScheme.primary),
                      const SizedBox(width: 8),
                      Text(
                        'System Information',
                        style: theme.textTheme.titleLarge,
                      ),
                      const Spacer(),
                      ElevatedButton.icon(
                        onPressed: () {
                          ref.read(appStateProvider.notifier).requestSystemInfo();
                        },
                        icon: const Icon(Icons.refresh),
                        label: const Text('Refresh'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // System Info Content
          Expanded(
            child: appState.systemInfo != null
                ? _buildSystemInfoContent(appState.systemInfo!, theme)
                : _buildNoDataContent(theme),
          ),
        ],
      ),
    );
  }

  Widget _buildSystemInfoContent(SystemInfo systemInfo, ThemeData theme) {
    return ListView(
      children: [
        // Platform Information
        _buildInfoCard(
          'Platform Information',
          Icons.computer,
          [
            _buildInfoRow('Platform', systemInfo.platform),
            _buildInfoRow('Version', systemInfo.platformVersion),
            _buildInfoRow('Architecture', systemInfo.architecture),
            _buildInfoRow('Processor', systemInfo.processor),
            _buildInfoRow('Python Version', systemInfo.pythonVersion),
          ],
          theme,
        ),
        
        const SizedBox(height: 16),
        
        // Terminal Information
        _buildInfoCard(
          'Terminal Information',
          Icons.terminal,
          [
            _buildInfoRow('Available Terminals', systemInfo.availableTerminals.join(', ')),
            _buildInfoRow('Active Sessions', systemInfo.activeSessions.toString()),
            _buildInfoRow('Command History Size', systemInfo.commandHistorySize.toString()),
          ],
          theme,
        ),
        
        const SizedBox(height: 16),
        
        // Quick Actions
        _buildQuickActionsCard(theme),
      ],
    );
  }

  Widget _buildNoDataContent(ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.info_outline,
            size: 64,
            color: theme.colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No System Information Available',
            style: theme.textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'Tap the refresh button to load system information',
            style: theme.textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildInfoCard(
    String title,
    IconData icon,
    List<Widget> children,
    ThemeData theme,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: theme.textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionsCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.speed, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  'Quick Actions',
                  style: theme.textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildActionButton(
                  'Get System Info',
                  Icons.info,
                  () {
                    // Already handled by refresh button
                  },
                  theme,
                ),
                _buildActionButton(
                  'Check Status',
                  Icons.check_circle,
                  () {
                    // Implement status check
                  },
                  theme,
                ),
                _buildActionButton(
                  'View Logs',
                  Icons.list_alt,
                  () {
                    // Implement log viewer
                  },
                  theme,
                ),
                _buildActionButton(
                  'Restart Service',
                  Icons.restart_alt,
                  () {
                    // Implement service restart
                  },
                  theme,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    VoidCallback onPressed,
    ThemeData theme,
  ) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 16),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
    );
  }
}
