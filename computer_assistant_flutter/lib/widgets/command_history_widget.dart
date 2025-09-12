import 'package:flutter/material.dart';
import '../services/command_service.dart';

class CommandHistoryWidget extends StatefulWidget {
  const CommandHistoryWidget({Key? key}) : super(key: key);

  @override
  State<CommandHistoryWidget> createState() => _CommandHistoryWidgetState();
}

class _CommandHistoryWidgetState extends State<CommandHistoryWidget> {
  final CommandService _commandService = CommandService();
  String _selectedFilter = 'All';

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Header with filter and clear button
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Filter dropdown
              Expanded(
                child: DropdownButton<String>(
                  value: _selectedFilter,
                  isExpanded: true,
                  items: const [
                    DropdownMenuItem(value: 'All', child: Text('All Commands')),
                    DropdownMenuItem(value: 'Completed', child: Text('Completed')),
                    DropdownMenuItem(value: 'Failed', child: Text('Failed')),
                    DropdownMenuItem(value: 'Sending', child: Text('Sending')),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _selectedFilter = value!;
                    });
                  },
                ),
              ),
              
              const SizedBox(width: 16),
              
              // Clear button
              IconButton(
                onPressed: _clearHistory,
                icon: const Icon(Icons.clear_all),
                tooltip: 'Clear History',
              ),
            ],
          ),
        ),
        
        // Statistics
        _buildStatistics(),
        
        // Command list
        Expanded(
          child: _buildCommandList(),
        ),
      ],
    );
  }

  Widget _buildStatistics() {
    final stats = _commandService.getStatistics();
    
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildStatItem('Total', stats['total'].toString(), Colors.blue),
            _buildStatItem('Completed', stats['completed'].toString(), Colors.green),
            _buildStatItem('Failed', stats['failed'].toString(), Colors.red),
            _buildStatItem('Success Rate', '${(stats['success_rate'] * 100).toStringAsFixed(1)}%', Colors.orange),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey.shade600,
          ),
        ),
      ],
    );
  }

  Widget _buildCommandList() {
    final commands = _commandService.commandHistory;
    final filteredCommands = _filterCommands(commands);
    
    if (filteredCommands.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No commands yet',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
            Text(
              'Send some commands to see them here',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: filteredCommands.length,
      itemBuilder: (context, index) {
        final command = filteredCommands[index];
        return _buildCommandItem(command);
      },
    );
  }

  List<CommandHistory> _filterCommands(List<CommandHistory> commands) {
    switch (_selectedFilter) {
      case 'Completed':
        return commands.where((c) => c.status == CommandStatus.completed).toList();
      case 'Failed':
        return commands.where((c) => c.status == CommandStatus.failed).toList();
      case 'Sending':
        return commands.where((c) => c.status == CommandStatus.sending).toList();
      default:
        return commands;
    }
  }

  Widget _buildCommandItem(CommandHistory command) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: _buildCommandIcon(command),
        title: Text(
          command.command,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_getCommandTypeText(command.type)),
            if (command.response != null)
              Text(
                'Response: ${command.response}',
                style: TextStyle(color: Colors.green.shade700),
              ),
            if (command.error != null)
              Text(
                'Error: ${command.error}',
                style: TextStyle(color: Colors.red.shade700),
              ),
            if (command.executionTime != null)
              Text(
                'Execution time: ${command.executionTime!.toStringAsFixed(2)}s',
                style: TextStyle(color: Colors.grey.shade600),
              ),
          ],
        ),
        trailing: _buildStatusChip(command.status),
        isThreeLine: true,
      ),
    );
  }

  Widget _buildCommandIcon(CommandHistory command) {
    IconData iconData;
    Color iconColor;
    
    switch (command.type) {
      case CommandType.voice:
        iconData = Icons.mic;
        iconColor = Colors.blue;
        break;
      case CommandType.typing:
        iconData = Icons.keyboard;
        iconColor = Colors.orange;
        break;
      case CommandType.application:
        iconData = Icons.apps;
        iconColor = Colors.purple;
        break;
      case CommandType.browser:
        iconData = Icons.web;
        iconColor = Colors.green;
        break;
      case CommandType.system:
        iconData = Icons.settings;
        iconColor = Colors.red;
        break;
      case CommandType.media:
        iconData = Icons.play_circle;
        iconColor = Colors.pink;
        break;
      case CommandType.file:
        iconData = Icons.folder;
        iconColor = Colors.brown;
        break;
      case CommandType.custom:
        iconData = Icons.code;
        iconColor = Colors.grey;
        break;
    }
    
    return CircleAvatar(
      backgroundColor: iconColor.withOpacity(0.1),
      child: Icon(iconData, color: iconColor),
    );
  }

  Widget _buildStatusChip(CommandStatus status) {
    Color color;
    String text;
    
    switch (status) {
      case CommandStatus.sending:
        color = Colors.orange;
        text = 'Sending';
        break;
      case CommandStatus.completed:
        color = Colors.green;
        text = 'Completed';
        break;
      case CommandStatus.failed:
        color = Colors.red;
        text = 'Failed';
        break;
    }
    
    return Chip(
      label: Text(
        text,
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
      backgroundColor: color,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }

  String _getCommandTypeText(CommandType type) {
    switch (type) {
      case CommandType.voice:
        return 'Voice Command';
      case CommandType.typing:
        return 'Typing Command';
      case CommandType.application:
        return 'Application Control';
      case CommandType.browser:
        return 'Browser Control';
      case CommandType.system:
        return 'System Control';
      case CommandType.media:
        return 'Media Control';
      case CommandType.file:
        return 'File Operation';
      case CommandType.custom:
        return 'Custom Command';
    }
  }

  void _clearHistory() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear History'),
        content: const Text('Are you sure you want to clear all command history?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              _commandService.clearHistory();
              Navigator.pop(context);
              setState(() {});
            },
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }
}
