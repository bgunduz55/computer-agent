import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../shared/websocket_protocol.dart';
import '../services/websocket_service.dart';
import '../utils/error_handler.dart';
import '../models/response_models.dart';
import 'settings_provider.dart';

// WebSocket Service Provider
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService();
  // Initialize WebSocket service on startup
  service.initialize();
  return service;
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
  final String? lastVoiceResponse;
  final bool isProcessing;
  final bool isListening;
  final List<TerminalResponse> terminalOutput;
  final AIResponse? aiResponse;
  final SystemInfo? systemInfo;
  final List<FileInfo> fileList;
  final String? screenshot;
  final String? errorMessage;
  final List<Map<String, dynamic>>? ragDocuments;
  final List<Map<String, dynamic>>? ragSearchResults;

  const AppState({
    this.isConnected = false,
    this.isAuthenticated = false,
    this.authToken,
    this.currentVoiceCommand,
    this.lastVoiceResponse,
    this.isProcessing = false,
    this.isListening = false,
    this.terminalOutput = const [],
    this.aiResponse,
    this.systemInfo,
    this.fileList = const [],
    this.screenshot,
    this.errorMessage,
    this.ragDocuments,
    this.ragSearchResults,
  });

  AppState copyWith({
    bool? isConnected,
    bool? isAuthenticated,
    String? authToken,
    String? currentVoiceCommand,
    String? lastVoiceResponse,
    bool? isProcessing,
    bool? isListening,
    List<TerminalResponse>? terminalOutput,
    AIResponse? aiResponse,
    SystemInfo? systemInfo,
    List<FileInfo>? fileList,
    String? screenshot,
    String? errorMessage,
    List<Map<String, dynamic>>? ragDocuments,
    List<Map<String, dynamic>>? ragSearchResults,
  }) {
    return AppState(
      isConnected: isConnected ?? this.isConnected,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      authToken: authToken ?? this.authToken,
      currentVoiceCommand: currentVoiceCommand ?? this.currentVoiceCommand,
      lastVoiceResponse: lastVoiceResponse ?? this.lastVoiceResponse,
      isProcessing: isProcessing ?? this.isProcessing,
      isListening: isListening ?? this.isListening,
      terminalOutput: terminalOutput ?? this.terminalOutput,
      aiResponse: aiResponse ?? this.aiResponse,
      systemInfo: systemInfo ?? this.systemInfo,
      fileList: fileList ?? this.fileList,
      screenshot: screenshot ?? this.screenshot,
      errorMessage: errorMessage ?? this.errorMessage,
      ragDocuments: ragDocuments ?? this.ragDocuments,
      ragSearchResults: ragSearchResults ?? this.ragSearchResults,
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
    try {
      switch (message.type) {
        case MessageType.authResponse:
          final success = message.data['success'] as bool? ?? false;
          state = state.copyWith(isAuthenticated: success);
          break;
          
        case MessageType.voiceResponse:
          final command = message.data['command'] as String? ?? '';
          final response = message.data['response'] as String? ?? '';
          final success = message.data['success'] as bool? ?? false;
          
          state = state.copyWith(
            currentVoiceCommand: command,
            lastVoiceResponse: response,
            isProcessing: false,
          );
          
          if (success) {
            _logger.i('Voice command processed successfully: $command -> $response');
          } else {
            _logger.w('Voice command failed: $command');
          }
          break;
          
        case MessageType.commandResponse:
          final command = message.data['command'] as String? ?? '';
          final response = message.data['result'] as String? ?? '';
          final success = message.data['success'] as bool? ?? true;
          
          state = state.copyWith(
            currentVoiceCommand: command,
            lastVoiceResponse: response,
            isProcessing: false,
          );
          
          if (success) {
            _logger.i('Command processed successfully: $command -> $response');
          } else {
            _logger.w('Command failed: $command');
          }
          break;
          
        case MessageType.notification:
          final notification = message.data['message'] as String? ?? '';
          final type = message.data['type'] as String? ?? 'info';
          _logger.i('Notification ($type): $notification');
          // You can add notification display logic here
          break;
          
        case MessageType.error:
          final error = message.data['error'] as String? ?? '';
          _logger.e('Server error: $error');
          // You can add error display logic here
          break;
          
        case MessageType.pong:
          _logger.d('Received pong from server');
          break;
          
        case MessageType.status:
          final serverTime = message.data['server_time'] as double? ?? 0.0;
          final connectedClients = message.data['connected_clients'] as int? ?? 0;
          final uptime = message.data['uptime'] as double? ?? 0.0;
          _logger.d('Server status: $connectedClients clients, uptime: ${uptime.toStringAsFixed(1)}s');
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
          
        case MessageType.ragResponse:
          final documents = (message.data['documents'] as List?)
              ?.map((doc) => Map<String, dynamic>.from(doc))
              .toList();
          final searchResults = (message.data['searchResults'] as List?)
              ?.map((result) => Map<String, dynamic>.from(result))
              .toList();
          
          if (documents != null) {
            state = state.copyWith(ragDocuments: documents);
          }
          if (searchResults != null) {
            state = state.copyWith(ragSearchResults: searchResults);
          }
          break;
          
        case MessageType.error:
          final error = message.data['error'] as String? ?? 'Unknown error';
          state = state.copyWith(errorMessage: error);
          ErrorHandler.logError('AppProvider', 'Server error: $error');
          break;
          
        default:
          _logger.d('Unhandled message type: ${message.type.name}');
      }
    } catch (e) {
      ErrorHandler.logError('AppProvider', 'Error handling message: $e');
      state = state.copyWith(errorMessage: 'Error processing server response');
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

  Future<void> sendCommand(String command) async {
    await _webSocketService.sendCommand(command);
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

  // RAG methods
  Future<void> requestRAGDocuments() async {
    try {
      await _webSocketService.requestRAGDocuments();
    } catch (e) {
      ErrorHandler.logError('AppProvider', 'Failed to request RAG documents: $e');
      rethrow;
    }
  }

  Future<void> searchRAGDocuments(String query) async {
    try {
      await _webSocketService.searchRAGDocuments(query);
    } catch (e) {
      ErrorHandler.logError('AppProvider', 'Failed to search RAG documents: $e');
      rethrow;
    }
  }

  Future<void> addRAGDocument(String content, Map<String, dynamic> metadata) async {
    try {
      await _webSocketService.addRAGDocument(content, metadata);
    } catch (e) {
      ErrorHandler.logError('AppProvider', 'Failed to add RAG document: $e');
      rethrow;
    }
  }

  Future<void> deleteRAGDocument(String docId) async {
    try {
      await _webSocketService.deleteRAGDocument(docId);
    } catch (e) {
      ErrorHandler.logError('AppProvider', 'Failed to delete RAG document: $e');
      rethrow;
    }
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
