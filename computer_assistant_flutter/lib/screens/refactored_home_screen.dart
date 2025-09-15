import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';
import '../shared/websocket_protocol.dart';
import '../widgets/voice_button.dart';
import '../widgets/intelligent_command_button.dart';
import '../widgets/command_progress_indicator.dart';
import '../widgets/connection_status.dart';
import '../widgets/quick_commands.dart';
import '../widgets/command_history.dart';
import '../widgets/smart_suggestions.dart';
import '../widgets/settings_panel.dart';
import '../widgets/notification_banner.dart';
// Backend integration widgets
import '../widgets/terminal_session_manager.dart';

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
    _tabController = TabController(length: 5, vsync: this);
    
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
          isScrollable: false,
          tabs: const [
            Tab(
              icon: Icon(Icons.mic),
              text: 'Sesli Komut',
            ),
            Tab(
              icon: Icon(Icons.smart_toy),
              text: 'Akıllı Komut',
            ),
            Tab(
              icon: Icon(Icons.terminal),
              text: 'Terminal',
            ),
            Tab(
              icon: Icon(Icons.dashboard),
              text: 'Kontrol',
            ),
            Tab(
              icon: Icon(Icons.settings),
              text: 'Ayarlar',
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
              _buildTerminalTab(appState),
              _buildControlTab(appState),
              _buildSettingsTab(appState),
            ],
          ),
          
          // Backend mesaj bildirimleri
          _buildBackendNotifications(),
          
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

  // New backend integration tabs
  Widget _buildTerminalTab(AppState appState) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Başlık
          Text(
            'Terminal Kontrolü',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade800,
            ),
          ),
          const SizedBox(height: 16),
          
          // Komut geçmişi
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Komut Geçmişi',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  CommandHistory(
                    onCommandSelected: (command) {
                      _handleCommand(command);
                    },
                    enabled: appState.isConnected,
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Terminal oturumları
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Terminal Oturumları',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const TerminalSessionManager(),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControlTab(AppState appState) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Başlık
          Text(
            'Sistem Kontrolü',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade800,
            ),
          ),
          const SizedBox(height: 16),
          
          // Sistem bilgileri
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Sistem Bilgileri',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (appState.systemInfo != null) ...[
                    _buildSystemInfoItem('İşletim Sistemi', appState.systemInfo!.os),
                    _buildSystemInfoItem('İşlemci', appState.systemInfo!.processor),
                    _buildSystemInfoItem('Bellek', '${(appState.systemInfo!.totalMemory / 1024 / 1024 / 1024).toStringAsFixed(1)} GB'),
                    _buildSystemInfoItem('Disk Kullanımı', '${appState.systemInfo!.diskUsage.toStringAsFixed(1)}%'),
                  ] else ...[
                    const Text('Sistem bilgileri yükleniyor...'),
                    const SizedBox(height: 8),
                    ElevatedButton(
                      onPressed: () {
                        ref.read(appStateProvider.notifier).requestSystemInfo();
                      },
                      child: const Text('Sistem Bilgilerini Yükle'),
                    ),
                  ],
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Hızlı komutlar
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hızlı Komutlar',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  QuickCommands(
                    onCommandSelected: (command) {
                      _handleQuickCommand(command);
                    },
                    enabled: appState.isConnected,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSystemInfoItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
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
              style: TextStyle(color: Colors.grey.shade700),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsTab(AppState appState) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Başlık
          Text(
            'Ayarlar',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Colors.blue.shade800,
            ),
          ),
          const SizedBox(height: 16),
          
          // Bağlantı ayarları
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Bağlantı Ayarları',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Icon(
                        appState.isConnected ? Icons.wifi : Icons.wifi_off,
                        color: appState.isConnected ? Colors.green : Colors.red,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        appState.isConnected ? 'Bağlı' : 'Bağlantı Yok',
                        style: TextStyle(
                          color: appState.isConnected ? Colors.green : Colors.red,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const Spacer(),
                      ElevatedButton(
                        onPressed: () {
                          if (appState.isConnected) {
                            ref.read(appStateProvider.notifier).disconnect();
                          } else {
                            _autoConnect();
                          }
                        },
                        child: Text(appState.isConnected ? 'Bağlantıyı Kes' : 'Bağlan'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Uygulama bilgileri
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Uygulama Bilgileri',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildInfoItem('Uygulama Adı', 'JARVIS Computer Assistant'),
                  _buildInfoItem('Versiyon', '1.0.0'),
                  _buildInfoItem('Platform', 'Flutter'),
                  _buildInfoItem('Durum', appState.isConnected ? 'Çevrimiçi' : 'Çevrimdışı'),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Hakkında
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hakkında',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'JARVIS Computer Assistant, Iron Man tarzında gelişmiş bir bilgisayar asistanıdır. '
                    'Sesli komutlar, akıllı komut işleme ve terminal kontrolü gibi özellikler sunar.',
                    style: TextStyle(height: 1.5),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
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
              style: TextStyle(color: Colors.grey.shade700),
            ),
          ),
        ],
      ),
    );
  }

  /// Backend mesaj bildirimlerini göster
  Widget _buildBackendNotifications() {
    return Consumer(
      builder: (context, ref, child) {
        // WebSocket mesajlarını dinle
        final webSocketService = ref.watch(webSocketServiceProvider);
        
        return StreamBuilder<WebSocketMessage>(
          stream: webSocketService.messageStream,
          builder: (context, snapshot) {
            if (!snapshot.hasData) {
              return const SizedBox.shrink();
            }
            
            final message = snapshot.data!;
            
            // Sadece belirli mesaj tiplerini göster
            if (message.type == MessageType.intelligentCommandResponse ||
                message.type == MessageType.intelligentCommandProgress ||
                message.type == MessageType.intelligentCommandStep ||
                message.type == MessageType.notification ||
                message.type == MessageType.error) {
              
              return Positioned(
                top: 20,
                left: 20,
                right: 20,
                child: Card(
                  color: _getMessageColor(message.type),
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              _getMessageIcon(message.type),
                              color: Colors.white,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              _getMessageTitle(message.type),
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            const Spacer(),
                            IconButton(
                              icon: const Icon(Icons.close, color: Colors.white),
                              onPressed: () {
                                // Bildirimi kapat
                              },
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _getMessageText(message),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }
            
            return const SizedBox.shrink();
          },
        );
      },
    );
  }

  Color _getMessageColor(MessageType type) {
    switch (type) {
      case MessageType.intelligentCommandResponse:
        return Colors.green;
      case MessageType.intelligentCommandProgress:
        return Colors.blue;
      case MessageType.intelligentCommandStep:
        return Colors.orange;
      case MessageType.notification:
        return Colors.blue.shade700;
      case MessageType.error:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getMessageIcon(MessageType type) {
    switch (type) {
      case MessageType.intelligentCommandResponse:
        return Icons.check_circle;
      case MessageType.intelligentCommandProgress:
        return Icons.sync;
      case MessageType.intelligentCommandStep:
        return Icons.play_arrow;
      case MessageType.notification:
        return Icons.info;
      case MessageType.error:
        return Icons.error;
      default:
        return Icons.message;
    }
  }

  String _getMessageTitle(MessageType type) {
    switch (type) {
      case MessageType.intelligentCommandResponse:
        return 'Akıllı Komut Tamamlandı';
      case MessageType.intelligentCommandProgress:
        return 'Komut İşleniyor';
      case MessageType.intelligentCommandStep:
        return 'Komut Adımı';
      case MessageType.notification:
        return 'Bildirim';
      case MessageType.error:
        return 'Hata';
      default:
        return 'Mesaj';
    }
  }

  String _getMessageText(WebSocketMessage message) {
    switch (message.type) {
      case MessageType.intelligentCommandResponse:
        return message.data['response']?.toString() ?? 'Komut tamamlandı';
      case MessageType.intelligentCommandProgress:
        return message.data['message']?.toString() ?? 'İşlem devam ediyor...';
      case MessageType.intelligentCommandStep:
        return message.data['description']?.toString() ?? 'Adım işleniyor...';
      case MessageType.notification:
        return message.data['message']?.toString() ?? 'Bildirim';
      case MessageType.error:
        return message.data['error']?.toString() ?? 'Bilinmeyen hata';
      default:
        return 'Mesaj alındı';
    }
  }
}
