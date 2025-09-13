import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';
import '../widgets/voice_button.dart';
import '../widgets/intelligent_command_button.dart';
import '../widgets/command_progress_indicator.dart';
import '../widgets/connection_status.dart';
import '../widgets/quick_commands.dart';
import '../widgets/command_history.dart';
import '../widgets/smart_suggestions.dart';
import '../widgets/settings_panel.dart';
import '../widgets/notification_banner.dart';

class RefactoredHomeScreen extends ConsumerStatefulWidget {
  const RefactoredHomeScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<RefactoredHomeScreen> createState() => _RefactoredHomeScreenState();
}

class _RefactoredHomeScreenState extends ConsumerState<RefactoredHomeScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  bool _showSettings = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    
    // Otomatik bağlantı - sadece bir kez
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _autoConnect();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _autoConnect() async {
    final appState = ref.read(appStateProvider);
    if (!appState.isConnected) {
      // Varsayılan sunucu URL'si
      const serverUrl = "ws://100.109.80.8:8765";
      await ref.read(appStateProvider.notifier).connect(serverUrl);
    }
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);
    
    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text(
          '🤖 JARVIS Computer Assistant',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
        backgroundColor: Colors.blue.shade50,
        elevation: 0,
        actions: [
          // Bağlantı durumu
          ConnectionStatus(
            isConnected: appState.isConnected,
            onReconnect: () {
              _autoConnect();
            },
          ),
          const SizedBox(width: 8),
          
          // Ayarlar butonu
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              setState(() {
                _showSettings = !_showSettings;
              });
            },
          ),
          const SizedBox(width: 16),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.blue.shade800,
          unselectedLabelColor: Colors.grey.shade600,
          indicatorColor: Colors.blue.shade800,
          tabs: const [
            Tab(
              icon: Icon(Icons.mic),
              text: 'Voice',
            ),
            Tab(
              icon: Icon(Icons.smart_toy),
              text: 'Smart',
            ),
            Tab(
              icon: Icon(Icons.history),
              text: 'History',
            ),
          ],
        ),
      ),
      body: Stack(
        children: [
          // Ana içerik
          TabBarView(
            controller: _tabController,
            children: [
              _buildVoiceTab(appState),
              _buildSmartTab(appState),
              _buildHistoryTab(appState),
            ],
          ),
          
          // Notification banner
          const Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: NotificationBanner(),
          ),
          
          // Ayarlar paneli
          if (_showSettings)
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              child: Container(
                color: Colors.black54,
                child: Center(
                  child: Container(
                    margin: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: SettingsPanel(
                      onClose: () {
                        setState(() {
                          _showSettings = false;
                        });
                      },
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildVoiceTab(AppState appState) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // Ana sesli komut alanı
          Container(
            width: double.infinity,
            constraints: const BoxConstraints(minHeight: 400),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.shade300,
                  blurRadius: 10,
                  offset: const Offset(0, 5),
                ),
              ],
            ),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Bağlantı durumu
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: appState.isConnected 
                          ? Colors.green.shade100 
                          : Colors.red.shade100,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          appState.isConnected ? Icons.wifi : Icons.wifi_off,
                          color: appState.isConnected ? Colors.green : Colors.red,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          appState.isConnected 
                              ? 'Connected to JARVIS' 
                              : 'Disconnected',
                          style: TextStyle(
                            color: appState.isConnected 
                                ? Colors.green.shade800 
                                : Colors.red.shade800,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 40),
                  
                  // Hızlı komut butonu (mikrofon)
                  VoiceButton(
                    onCommandRecognized: (command) {
                      _handleQuickCommand(command);
                    },
                    onStartListening: () {
                      // Dinleme başladı
                    },
                    onStopListening: () {
                      // Dinleme bitti
                    },
                    enabled: appState.isConnected,
                  ),
                  
                  const SizedBox(height: 30),
                  
                  // Akıllı komut butonu
                  IntelligentCommandButton(
                    onCommandRecognized: (command) {
                      _handleIntelligentCommand(command);
                    },
                    onStartListening: () {
                      // Dinleme başladı
                    },
                    onStopListening: () {
                      // Dinleme bitti
                    },
                    enabled: appState.isConnected,
                    isProcessing: appState.isIntelligentCommandProcessing,
                    currentStep: appState.currentStep ?? '',
                    progress: appState.intelligentCommandProgress,
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Hızlı komut durumu
                  if (appState.isProcessing)
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Processing quick command...',
                            style: TextStyle(
                              color: Colors.blue.shade800,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  
                  // Akıllı komut progress indicator
                  if (appState.isIntelligentCommandProcessing && appState.commandSteps != null)
                    CommandProgressIndicator(
                      steps: appState.commandSteps!
                          .map((step) => CommandStep(
                                name: step['name'] ?? '',
                                description: step['description'] ?? '',
                                isCompleted: step['isCompleted'] ?? false,
                                isCurrent: step['isCurrent'] ?? false,
                                hasError: step['hasError'] ?? false,
                                errorMessage: step['errorMessage'],
                              ))
                          .toList(),
                      currentStep: appState.currentStep != null ? 0 : 0,
                      status: appState.intelligentCommandStatus ?? '',
                      isError: false,
                      progress: appState.intelligentCommandProgress.toDouble(),
                    ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Hızlı komutlar
          QuickCommands(
            onCommandSelected: (command) {
              _handleCommand(command);
            },
            enabled: appState.isConnected,
          ),
        ],
      ),
    );
  }

  Widget _buildSmartTab(AppState appState) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // AI önerileri
          SmartSuggestions(
            onSuggestionSelected: (suggestion) {
              _handleCommand(suggestion);
            },
            enabled: appState.isConnected,
          ),
          
          const SizedBox(height: 20),
          
          // Hızlı komutlar
          QuickCommands(
            onCommandSelected: (command) {
              _handleCommand(command);
            },
            enabled: appState.isConnected,
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryTab(AppState appState) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: CommandHistory(
        onCommandSelected: (command) {
          _handleCommand(command);
        },
        enabled: appState.isConnected,
      ),
    );
  }

  void _handleCommand(String command) {
    if (command.trim().isEmpty) return;
    
    // Komutu gönder
    ref.read(appStateProvider.notifier).sendCommand(command);
  }

  void _handleQuickCommand(String command) {
    if (command.trim().isEmpty) return;
    
    // Hızlı komutu gönder
    ref.read(appStateProvider.notifier).sendQuickCommand(command);
  }

  void _handleIntelligentCommand(String command) {
    if (command.trim().isEmpty) return;
    
    // Akıllı komutu gönder
    ref.read(appStateProvider.notifier).sendIntelligentCommand(command);
  }
}
