import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/command_service.dart';
import '../providers/app_provider.dart';
import '../widgets/command_input_widget.dart';
import '../widgets/command_history_widget.dart';
import '../widgets/quick_commands_widget.dart';

class CommandScreen extends StatefulWidget {
  const CommandScreen({Key? key}) : super(key: key);

  @override
  State<CommandScreen> createState() => _CommandScreenState();
}

class _CommandScreenState extends State<CommandScreen> with TickerProviderStateMixin {
  late TabController _tabController;
  final CommandService _commandService = CommandService();
  final TextEditingController _commandController = TextEditingController();
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _commandService.initialize();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _commandController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('JARVIS Commands'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.mic), text: 'Voice'),
            Tab(icon: Icon(Icons.keyboard), text: 'Type'),
            Tab(icon: Icon(Icons.history), text: 'History'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildVoiceTab(),
          _buildTypeTab(),
          _buildHistoryTab(),
        ],
      ),
    );
  }

  Widget _buildVoiceTab() {
    return Consumer<AppState>(
      builder: (context, appState, child) {
        return Column(
          children: [
            // Connection status
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: appState.isConnected ? Colors.green.shade100 : Colors.red.shade100,
              child: Row(
                children: [
                  Icon(
                    appState.isConnected ? Icons.wifi : Icons.wifi_off,
                    color: appState.isConnected ? Colors.green : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    appState.isConnected ? 'Connected to JARVIS' : 'Disconnected from JARVIS',
                    style: TextStyle(
                      color: appState.isConnected ? Colors.green.shade800 : Colors.red.shade800,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            
            // Voice command input
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Quick commands
                    const QuickCommandsWidget(),
                    
                    const SizedBox(height: 20),
                    
                    // Voice command input
                    CommandInputWidget(
                      controller: _commandController,
                      onSend: _sendVoiceCommand,
                      hintText: 'Say something to JARVIS...',
                      enabled: appState.isConnected,
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Voice recognition status
                    if (appState.isProcessing)
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade100,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.mic, color: Colors.blue),
                            const SizedBox(width: 8),
                            const Text('Listening...'),
                            const SizedBox(width: 8),
                            const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildTypeTab() {
    return Consumer<AppState>(
      builder: (context, appState, child) {
        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              // Typing command input
              CommandInputWidget(
                controller: _commandController,
                onSend: _sendTypingCommand,
                hintText: 'Type what you want JARVIS to type...',
                enabled: appState.isConnected,
                icon: Icons.keyboard,
              ),
              
              const SizedBox(height: 20),
              
              // Typing examples
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Typing Examples:',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      _buildExampleChip('yaz Merhaba dünya'),
                      _buildExampleChip('yaz Hello World'),
                      _buildExampleChip('yaz Bu bir test mesajıdır'),
                      _buildExampleChip('enter'),
                      _buildExampleChip('tab'),
                      _buildExampleChip('ctrl+c'),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHistoryTab() {
    return const CommandHistoryWidget();
  }

  Widget _buildExampleChip(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: InkWell(
        onTap: () {
          _commandController.text = text;
          _sendTypingCommand(text);
        },
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.grey.shade200,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(text),
        ),
      ),
    );
  }

  void _sendVoiceCommand(String command) {
    if (command.trim().isEmpty) return;
    
    _commandService.sendVoiceCommand(command);
    _commandController.clear();
  }

  void _sendTypingCommand(String text) {
    if (text.trim().isEmpty) return;
    
    _commandService.sendTypingCommand(text);
    _commandController.clear();
  }
}
