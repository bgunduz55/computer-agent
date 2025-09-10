import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';
import '../models/websocket_message.dart';

class TerminalWidget extends ConsumerStatefulWidget {
  const TerminalWidget({super.key});

  @override
  ConsumerState<TerminalWidget> createState() => _TerminalWidgetState();
}

class _TerminalWidgetState extends ConsumerState<TerminalWidget> {
  final TextEditingController _commandController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  String _currentDirectory = '.';
  String _selectedTerminal = 'powershell';

  @override
  void dispose() {
    _commandController.dispose();
    _scrollController.dispose();
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
          // Terminal Header
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Icon(Icons.terminal, color: theme.colorScheme.primary),
                      const SizedBox(width: 8),
                      Text(
                        'Terminal',
                        style: theme.textTheme.titleLarge,
                      ),
                      const Spacer(),
                      DropdownButton<String>(
                        value: _selectedTerminal,
                        items: const [
                          DropdownMenuItem(value: 'powershell', child: Text('PowerShell')),
                          DropdownMenuItem(value: 'cmd', child: Text('CMD')),
                          DropdownMenuItem(value: 'bash', child: Text('Bash')),
                          DropdownMenuItem(value: 'wsl', child: Text('WSL')),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _selectedTerminal = value ?? 'powershell';
                          });
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Current Directory: $_currentDirectory',
                    style: theme.textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Terminal Output
          Expanded(
            child: Card(
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.black,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ListView.builder(
                  controller: _scrollController,
                  itemCount: appState.terminalOutput.length,
                  itemBuilder: (context, index) {
                    final response = appState.terminalOutput[index];
                    return _buildTerminalOutput(response);
                  },
                ),
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Command Input
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _commandController,
                          decoration: InputDecoration(
                            labelText: 'Enter command',
                            hintText: 'Type your terminal command...',
                            prefixText: '$_selectedTerminal> ',
                            border: const OutlineInputBorder(),
                          ),
                          onSubmitted: (value) => _executeCommand(value),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        onPressed: () => _executeCommand(_commandController.text),
                        icon: const Icon(Icons.send),
                        style: IconButton.styleFrom(
                          backgroundColor: theme.colorScheme.primary,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      ElevatedButton.icon(
                        onPressed: _clearOutput,
                        icon: const Icon(Icons.clear),
                        label: const Text('Clear'),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton.icon(
                        onPressed: _showCommandHistory,
                        icon: const Icon(Icons.history),
                        label: const Text('History'),
                      ),
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

  Widget _buildTerminalOutput(TerminalResponse response) {
    final theme = Theme.of(context);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Command
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
                color: Colors.blue.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              '> ${response.command}',
              style: const TextStyle(
                color: Colors.blue,
                fontWeight: FontWeight.bold,
                fontFamily: 'monospace',
              ),
            ),
          ),
          
          const SizedBox(height: 4),
          
          // Output
          if (response.output.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.green.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                response.output,
                style: const TextStyle(
                  color: Colors.green,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          
          // Error
          if (response.error.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.red.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                response.error,
                style: const TextStyle(
                  color: Colors.red,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          
          // Status
          Row(
            children: [
              Icon(
                response.success ? Icons.check_circle : Icons.error,
                size: 16,
                color: response.success ? Colors.green : Colors.red,
              ),
              const SizedBox(width: 4),
              Text(
                'Exit Code: ${response.exitCode}',
                style: const TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                  fontFamily: 'monospace',
                ),
              ),
              const Spacer(),
              Text(
                '${response.executionTime.toStringAsFixed(2)}s',
                style: const TextStyle(
                  color: Colors.grey,
                  fontSize: 12,
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _executeCommand(String command) async {
    if (command.trim().isEmpty) return;
    
    _commandController.clear();
    
    // Add to command history
    _addToHistory(command);
    
    // Send command to server
    await ref.read(appStateProvider.notifier).sendTerminalCommand(command);
    
    // Scroll to bottom
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _addToHistory(String command) {
    // This would be implemented with a proper history storage
    // For now, we'll just show a snackbar
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Command added to history: $command'),
        duration: const Duration(seconds: 1),
      ),
    );
  }

  void _clearOutput() {
    ref.read(appStateProvider.notifier).clearTerminalOutput();
  }

  void _showCommandHistory() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Command History',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Text('Command history will be implemented here'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Close'),
            ),
          ],
        ),
      ),
    );
  }
}
