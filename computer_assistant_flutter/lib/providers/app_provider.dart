import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../models/websocket_message.dart';
import '../services/websocket_service.dart';
import 'settings_provider.dart';

// WebSocket Service Provider
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  return WebSocketService();
});

// Connection Status Provider
final connectionStatusProvider = StateProvider<bool>((ref) {
  return false;
});

// Authentication Status Provider
final authenticationStatusProvider = StateProvider<bool>((ref) {
  return false;
});

// Server URL Provider - now uses settings
final serverUrlProvider = Provider<String>((ref) {
  final settings = ref.watch(settingsProvider);
  return settings.serverUrl;
});

// Auth Token Provider
final authTokenProvider = StateProvider<String?>((ref) {
  return null;
});

// Current Voice Command Provider
final currentVoiceCommandProvider = StateProvider<String?>((ref) {
  return null;
});

// Terminal Output Provider
final terminalOutputProvider = StateProvider<List<TerminalResponse>>((ref) {
  return [];
});

// AI Response Provider
final aiResponseProvider = StateProvider<AIResponse?>((ref) {
  return null;
});

// System Info Provider
final systemInfoProvider = StateProvider<SystemInfo?>((ref) {
  return null;
});

// File List Provider
final fileListProvider = StateProvider<List<FileInfo>>((ref) {
  return [];
});

// Screenshot Provider
final screenshotProvider = StateProvider<String?>((ref) {
  return null;
});

// Error Message Provider
final errorMessageProvider = StateProvider<String?>((ref) {
  return null;
});

// App State Provider
class AppState {
  final bool isConnected;
  final bool isAuthenticated;
  final String? authToken;
  final String? currentVoiceCommand;
  final List<TerminalResponse> terminalOutput;
  final AIResponse? aiResponse;
  final SystemInfo? systemInfo;
  final List<FileInfo> fileList;
  final String? screenshot;
  final String? errorMessage;

  const AppState({
    this.isConnected = false,
    this.isAuthenticated = false,
    this.authToken,
    this.currentVoiceCommand,
    this.terminalOutput = const [],
    this.aiResponse,
    this.systemInfo,
    this.fileList = const [],
    this.screenshot,
    this.errorMessage,
  });

  AppState copyWith({
    bool? isConnected,
    bool? isAuthenticated,
    String? authToken,
    String? currentVoiceCommand,
    List<TerminalResponse>? terminalOutput,
    AIResponse? aiResponse,
    SystemInfo? systemInfo,
    List<FileInfo>? fileList,
    String? screenshot,
    String? errorMessage,
  }) {
    return AppState(
      isConnected: isConnected ?? this.isConnected,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      authToken: authToken ?? this.authToken,
      currentVoiceCommand: currentVoiceCommand ?? this.currentVoiceCommand,
      terminalOutput: terminalOutput ?? this.terminalOutput,
      aiResponse: aiResponse ?? this.aiResponse,
      systemInfo: systemInfo ?? this.systemInfo,
      fileList: fileList ?? this.fileList,
      screenshot: screenshot ?? this.screenshot,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

// App State Notifier
class AppStateNotifier extends StateNotifier<AppState> {
  final WebSocketService _webSocketService;
  final Logger _logger = Logger();

  AppStateNotifier(this._webSocketService) : super(const AppState()) {
    _initializeWebSocket();
  }

  void _initializeWebSocket() {
    // Listen to connection status
    _webSocketService.connectionStream.listen((isConnected) {
      state = state.copyWith(isConnected: isConnected);
    });

    // Listen to messages
    _webSocketService.messageStream.listen(_handleMessage);
  }

  void _handleMessage(WebSocketMessage message) {
    switch (message.type) {
      case MessageType.authResponse:
        final success = message.data['success'] as bool? ?? false;
        state = state.copyWith(isAuthenticated: success);
        break;
        
      case MessageType.voiceResponse:
        final command = message.data['command'] as String? ?? '';
        state = state.copyWith(currentVoiceCommand: command);
        break;
        
      case MessageType.terminalResponse:
        final response = TerminalResponse.fromJson(message.data);
        final newOutput = [...state.terminalOutput, response];
        state = state.copyWith(terminalOutput: newOutput);
        break;
        
      case MessageType.aiResponse:
        final response = AIResponse.fromJson(message.data);
        state = state.copyWith(aiResponse: response);
        break;
        
      case MessageType.systemInfo:
        final info = SystemInfo.fromJson(message.data);
        state = state.copyWith(systemInfo: info);
        break;
        
      case MessageType.fileResponse:
        final files = (message.data['files'] as List?)
            ?.map((file) => FileInfo.fromJson(file))
            .toList() ?? [];
        state = state.copyWith(fileList: files);
        break;
        
      case MessageType.screenshotResponse:
        final screenshot = message.data['screenshot'] as String?;
        state = state.copyWith(screenshot: screenshot);
        break;
        
      case MessageType.error:
        final error = message.data['error'] as String? ?? 'Unknown error';
        state = state.copyWith(errorMessage: error);
        break;
        
      default:
        _logger.d('Unhandled message type: ${message.type.name}');
    }
  }

  // Connection methods
  Future<bool> connect(String serverUrl, {String? authToken}) async {
    state = state.copyWith(authToken: authToken);
    return await _webSocketService.connect(serverUrl, authToken: authToken);
  }

  Future<void> disconnect() async {
    await _webSocketService.disconnect();
  }

  Future<bool> authenticate(String token) async {
    state = state.copyWith(authToken: token);
    return await _webSocketService.authenticate(token);
  }

  // Command methods
  Future<void> sendVoiceCommand(String command) async {
    await _webSocketService.sendVoiceCommand(command);
  }

  Future<void> sendTerminalCommand(String command) async {
    await _webSocketService.sendTerminalCommand(command);
  }

  Future<void> sendAIRequest(String prompt) async {
    await _webSocketService.sendAIRequest(prompt);
  }

  Future<void> sendSystemControl(String action, {Map<String, dynamic>? params}) async {
    await _webSocketService.sendSystemControl(action, params: params);
  }

  Future<void> requestSystemInfo() async {
    await _webSocketService.requestSystemInfo();
  }

  Future<void> requestFileList(String path) async {
    await _webSocketService.requestFileList(path);
  }

  Future<void> requestScreenshot() async {
    await _webSocketService.requestScreenshot();
  }

  // Utility methods
  void clearError() {
    state = state.copyWith(errorMessage: null);
  }

  void clearTerminalOutput() {
    state = state.copyWith(terminalOutput: []);
  }

  void clearAIResponse() {
    state = state.copyWith(aiResponse: null);
  }

  void clearFileList() {
    state = state.copyWith(fileList: []);
  }

  void clearScreenshot() {
    state = state.copyWith(screenshot: null);
  }
}

// App State Provider
final appStateProvider = StateNotifierProvider<AppStateNotifier, AppState>((ref) {
  final webSocketService = ref.watch(webSocketServiceProvider);
  return AppStateNotifier(webSocketService);
});
