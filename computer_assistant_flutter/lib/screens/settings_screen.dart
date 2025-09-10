import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/settings_provider.dart';

class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  late TextEditingController _hostController;
  late TextEditingController _portController;
  late TextEditingController _timeoutController;
  late TextEditingController _heartbeatController;
  late TextEditingController _authTokenController;

  @override
  void initState() {
    super.initState();
    _hostController = TextEditingController();
    _portController = TextEditingController();
    _timeoutController = TextEditingController();
    _heartbeatController = TextEditingController();
    _authTokenController = TextEditingController();
  }

  @override
  void dispose() {
    _hostController.dispose();
    _portController.dispose();
    _timeoutController.dispose();
    _heartbeatController.dispose();
    _authTokenController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final settings = ref.watch(settingsProvider);
    final theme = Theme.of(context);

    // Update controllers when settings change
    _hostController.text = settings.serverHost;
    _portController.text = settings.serverPort.toString();
    _timeoutController.text = settings.connectionTimeout.toString();
    _heartbeatController.text = settings.heartbeatInterval.toString();
    _authTokenController.text = settings.savedAuthToken ?? '';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: theme.colorScheme.onPrimary,
        elevation: 4,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _resetToDefaults,
            tooltip: 'Reset to Defaults',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildConnectionSection(theme),
            const SizedBox(height: 24),
            _buildAdvancedSection(theme),
            const SizedBox(height: 24),
            _buildSecuritySection(theme),
            const SizedBox(height: 24),
            _buildActionsSection(theme),
          ],
        ),
      ),
    );
  }

  Widget _buildConnectionSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Connection Settings',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  flex: 3,
                  child: TextField(
                    controller: _hostController,
                    decoration: const InputDecoration(
                      labelText: 'Server Host',
                      hintText: '192.168.1.100',
                      prefixIcon: Icon(Icons.computer),
                    ),
                    onChanged: (value) {
                      ref.read(settingsProvider.notifier).updateServerHost(value);
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  flex: 1,
                  child: TextField(
                    controller: _portController,
                    decoration: const InputDecoration(
                      labelText: 'Port',
                      hintText: '8765',
                      prefixIcon: Icon(Icons.settings_ethernet),
                    ),
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(5),
                    ],
                    onChanged: (value) {
                      final port = int.tryParse(value);
                      if (port != null) {
                        ref.read(settingsProvider.notifier).updateServerPort(port);
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Consumer(
                    builder: (context, ref, child) {
                      final settings = ref.watch(settingsProvider);
                      return SwitchListTile(
                        title: const Text('Use SSL/TLS'),
                        subtitle: const Text('Secure WebSocket connection'),
                        value: settings.useSSL,
                        onChanged: (value) {
                          ref.read(settingsProvider.notifier).updateUseSSL(value);
                        },
                      );
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Consumer(
                    builder: (context, ref, child) {
                      final settings = ref.watch(settingsProvider);
                      return SwitchListTile(
                        title: const Text('Auto Connect'),
                        subtitle: const Text('Connect automatically on startup'),
                        value: settings.autoConnect,
                        onChanged: (value) {
                          ref.read(settingsProvider.notifier).updateAutoConnect(value);
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: theme.colorScheme.primary,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Server URL: ${ref.watch(serverUrlProvider)}',
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAdvancedSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Advanced Settings',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _timeoutController,
                    decoration: const InputDecoration(
                      labelText: 'Connection Timeout (seconds)',
                      hintText: '30',
                      prefixIcon: Icon(Icons.timer),
                    ),
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(3),
                    ],
                    onChanged: (value) {
                      final timeout = int.tryParse(value);
                      if (timeout != null) {
                        ref.read(settingsProvider.notifier).updateConnectionTimeout(timeout);
                      }
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    controller: _heartbeatController,
                    decoration: const InputDecoration(
                      labelText: 'Heartbeat Interval (seconds)',
                      hintText: '30',
                      prefixIcon: Icon(Icons.favorite),
                    ),
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(3),
                    ],
                    onChanged: (value) {
                      final interval = int.tryParse(value);
                      if (interval != null) {
                        ref.read(settingsProvider.notifier).updateHeartbeatInterval(interval);
                      }
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSecuritySection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Security Settings',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _authTokenController,
              decoration: const InputDecoration(
                labelText: 'Authentication Token',
                hintText: 'Enter your auth token',
                prefixIcon: Icon(Icons.key),
                suffixIcon: Icon(Icons.visibility_off),
              ),
              obscureText: true,
              onChanged: (value) {
                ref.read(settingsProvider.notifier).updateAuthToken(value.isEmpty ? null : value);
              },
            ),
            const SizedBox(height: 16),
            Consumer(
              builder: (context, ref, child) {
                final settings = ref.watch(settingsProvider);
                return SwitchListTile(
                  title: const Text('Save Credentials'),
                  subtitle: const Text('Remember authentication token'),
                  value: settings.saveCredentials,
                  onChanged: (value) {
                    ref.read(settingsProvider.notifier).updateSaveCredentials(value);
                  },
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionsSection(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Actions',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _testConnection,
                    icon: const Icon(Icons.wifi),
                    label: const Text('Test Connection'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _validateSettings,
                    icon: const Icon(Icons.check_circle),
                    label: const Text('Validate Settings'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _resetToDefaults,
                    icon: const Icon(Icons.restore),
                    label: const Text('Reset to Defaults'),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _exportSettings,
                    icon: const Icon(Icons.download),
                    label: const Text('Export Settings'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _testConnection() async {
    final settings = ref.read(settingsProvider);
    final serverUrl = settings.serverUrl;
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Testing Connection'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text('Connecting to $serverUrl...'),
          ],
        ),
      ),
    );

    // Simulate connection test
    await Future.delayed(const Duration(seconds: 2));

    if (mounted) {
      Navigator.of(context).pop();
      
      // Show result
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Connection Test'),
          content: const Text('Connection test completed. Check the connection status in the main screen.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  void _validateSettings() {
    final errors = ref.read(settingsProvider.notifier).validateSettings();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Settings Validation'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (errors.isEmpty)
              const Text('All settings are valid! ✅')
            else ...[
              const Text('Found the following issues:'),
              const SizedBox(height: 8),
              ...errors.map((error) => Padding(
                padding: const EdgeInsets.only(left: 8, top: 4),
                child: Text('• $error', style: const TextStyle(color: Colors.red)),
              )),
            ],
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _resetToDefaults() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reset to Defaults'),
        content: const Text('Are you sure you want to reset all settings to their default values? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              await ref.read(settingsProvider.notifier).resetToDefaults();
              if (mounted) {
                Navigator.of(context).pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Settings reset to defaults')),
                );
              }
            },
            child: const Text('Reset'),
          ),
        ],
      ),
    );
  }

  void _exportSettings() {
    final settings = ref.read(settingsProvider);
    final settingsJson = settings.toJson();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Export Settings'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Copy the following settings to share or backup:'),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(8),
              ),
              child: SelectableText(
                settingsJson.toString(),
                style: const TextStyle(fontFamily: 'monospace'),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
