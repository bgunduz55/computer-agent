import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:speech_to_text/speech_to_text.dart';
// import 'package:permission_handler/permission_handler.dart';
import '../providers/app_provider.dart';
import '../utils/error_handler.dart';

class VoiceCommandWidget extends ConsumerStatefulWidget {
  const VoiceCommandWidget({super.key});

  @override
  ConsumerState<VoiceCommandWidget> createState() => _VoiceCommandWidgetState();
}

class _VoiceCommandWidgetState extends ConsumerState<VoiceCommandWidget> {
  final TextEditingController _commandController = TextEditingController();
  // final SpeechToText _speechToText = SpeechToText();
  
  bool _isProcessing = false;
  bool _isListening = false;
  bool _speechEnabled = false;
  String _lastWords = '';
  String _lastError = '';
  String _lastStatus = '';

  @override
  void initState() {
    super.initState();
    _initSpeech();
    _initTts();
  }

  @override
  void dispose() {
    _commandController.dispose();
    // _speechToText.cancel();
    super.dispose();
  }

  Future<void> _initSpeech() async {
    // Voice recognition will be enabled when dependencies are properly installed
    // For now, use text input to send commands to JARVIS server
    setState(() {
      _speechEnabled = true;
      _lastStatus = 'Text input mode - Type commands to send to JARVIS server';
    });
  }

  Future<void> _initTts() async {
    // TTS will be handled by the Python server
    ErrorHandler.logInfo('VoiceCommandWidget', 'TTS handled by JARVIS server');
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: SingleChildScrollView(
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
                      const SizedBox(width: 8),
                      // Voice Recognition Button
                      ElevatedButton.icon(
                        onPressed: _isListening ? _stopListening : _startListening,
                        icon: Icon(_isListening ? Icons.stop : Icons.mic),
                        label: Text(_isListening ? 'Stop' : 'Voice'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _isListening 
                              ? Theme.of(context).colorScheme.error
                              : Theme.of(context).colorScheme.primary,
                          foregroundColor: _isListening 
                              ? Theme.of(context).colorScheme.onError
                              : Theme.of(context).colorScheme.onPrimary,
                        ),
                      ),
                      const SizedBox(width: 8),
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
          
          // Voice Recognition Status
          if (_lastStatus.isNotEmpty || _lastError.isNotEmpty) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          _isListening ? Icons.mic : Icons.mic_off,
                          color: _isListening 
                              ? Colors.green 
                              : Theme.of(context).colorScheme.primary,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Voice Recognition Status',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (_lastStatus.isNotEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: _isListening 
                              ? Colors.green.withOpacity(0.1)
                              : theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: _isListening 
                                ? Colors.green 
                                : theme.colorScheme.outline,
                          ),
                        ),
                        child: Text(
                          _lastStatus,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: _isListening ? Colors.green : null,
                          ),
                        ),
                      ),
                    
                    // Server Notifications
                    if (appState.lastVoiceResponse?.isNotEmpty == true)
                      Container(
                        width: double.infinity,
                        margin: const EdgeInsets.only(top: 8),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: theme.colorScheme.primary,
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  Icons.smart_toy,
                                  size: 20,
                                  color: theme.colorScheme.primary,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'JARVIS Response',
                                  style: theme.textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: theme.colorScheme.primary,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              appState.lastVoiceResponse ?? '',
                              style: theme.textTheme.bodyMedium?.copyWith(
                                color: theme.colorScheme.onPrimaryContainer,
                              ),
                            ),
                          ],
                        ),
                      ),
                    if (_lastError.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.red.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.red),
                        ),
                        child: Text(
                          _lastError,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: Colors.red,
                          ),
                        ),
                      ),
                    ],
                    
                    // Show last voice response
                    if (appState.lastVoiceResponse != null && appState.lastVoiceResponse!.isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primaryContainer.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: theme.colorScheme.primary.withOpacity(0.3),
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  Icons.smart_toy,
                                  color: theme.colorScheme.primary,
                                  size: 16,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'JARVIS Response',
                                  style: theme.textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: theme.colorScheme.primary,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              appState.lastVoiceResponse!,
                              style: theme.textTheme.bodyMedium?.copyWith(
                                color: theme.colorScheme.onSurface,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
          
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
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      ErrorHandler.handleError(
        context,
        e,
        title: 'Voice Command Error',
        customMessage: 'Failed to send voice command: $command',
        onRetry: () => _sendCommand(),
      );
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

  Future<void> _startListening() async {
    if (!_speechEnabled) {
      await _initSpeech();
      if (!_speechEnabled) return;
    }

    setState(() {
      _isListening = true;
      _lastWords = '';
      _lastError = '';
    });

    // Voice recognition will be enabled when dependencies are properly installed
    // For now, show instruction to use text input
    setState(() {
      _lastStatus = 'Voice recognition will be available when dependencies are installed. Use text input below.';
      _isListening = false;
    });
  }

  Future<void> _stopListening() async {
    setState(() {
      _isListening = false;
    });
    // await _speechToText.stop();
  }

}