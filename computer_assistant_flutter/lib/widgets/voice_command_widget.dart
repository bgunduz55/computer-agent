import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';

class VoiceCommandWidget extends ConsumerStatefulWidget {
  const VoiceCommandWidget({super.key});

  @override
  ConsumerState<VoiceCommandWidget> createState() => _VoiceCommandWidgetState();
}

class _VoiceCommandWidgetState extends ConsumerState<VoiceCommandWidget> {
  final TextEditingController _commandController = TextEditingController();
  bool _isProcessing = false;

  @override
  void dispose() {
    _commandController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Voice Command Header
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        Icons.mic,
                        color: theme.colorScheme.primary,
                        size: 24,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Voice Commands',
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Send voice commands to JARVIS remotely',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Command Input
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Send Command',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _commandController,
                    decoration: InputDecoration(
                      labelText: 'Enter your command',
                      hintText: 'e.g., "What time is it?", "Open browser", "Close current tab"',
                      prefixIcon: const Icon(Icons.keyboard_voice),
                      suffixIcon: _commandController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                _commandController.clear();
                                setState(() {});
                              },
                            )
                          : null,
                      border: const OutlineInputBorder(),
                    ),
                    maxLines: 3,
                    onChanged: (value) {
                      setState(() {});
                    },
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _isProcessing || !appState.isConnected
                              ? null
                              : _sendCommand,
                          icon: _isProcessing
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Icon(Icons.send),
                          label: Text(_isProcessing ? 'Sending...' : 'Send Command'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      OutlinedButton.icon(
                        onPressed: _isProcessing ? null : _clearCommand,
                        icon: const Icon(Icons.clear_all),
                        label: const Text('Clear'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Command History
          if (appState.currentVoiceCommand != null) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.history,
                          color: theme.colorScheme.primary,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Last Command',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        appState.currentVoiceCommand!,
                        style: theme.textTheme.bodyMedium,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
          
          const SizedBox(height: 16),
          
          // Quick Commands
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Quick Commands',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _buildQuickCommandChip('What time is it?', theme),
                      _buildQuickCommandChip('Open browser', theme),
                      _buildQuickCommandChip('Close current tab', theme),
                      _buildQuickCommandChip('List running apps', theme),
                      _buildQuickCommandChip('Take screenshot', theme),
                      _buildQuickCommandChip('System info', theme),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickCommandChip(String command, ThemeData theme) {
    return ActionChip(
      label: Text(command),
      onPressed: () {
        _commandController.text = command;
        setState(() {});
        _sendCommand();
      },
      avatar: const Icon(Icons.arrow_forward, size: 16),
    );
  }

  Future<void> _sendCommand() async {
    final command = _commandController.text.trim();
    if (command.isEmpty) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      await ref.read(appStateProvider.notifier).sendVoiceCommand(command);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Command sent: $command'),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to send command: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
    }
  }

  void _clearCommand() {
    _commandController.clear();
    setState(() {});
  }
}