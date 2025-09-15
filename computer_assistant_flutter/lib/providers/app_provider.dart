import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../shared/websocket_protocol.dart';
import '../services/websocket_service.dart';
import '../utils/error_handler.dart';
import '../models/response_models.dart';

// WebSocket Service Provider - Singleton
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  // WebSocketService is already a singleton, no need to create new instances
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

// Server URL Provider - hardcoded for now
final serverUrlProvider = Provider<String>((ref) {
  return 'ws://100.109.80.8:8765';
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

// Backend Integration Providers
final latestProgressUpdateProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final latestIntelligentCommandResponseProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final terminalSessionsProvider = StateProvider<List<Map<String, dynamic>>>((ref) {
  return [];
});

final terminalOutputsProvider = StateProvider<Map<String, List<Map<String, dynamic>>>>((ref) {
  return {};
});

final latestRealTimeMetricsProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final latestAnalyticsReportProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final latestExecutionContextUpdateProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final latestErrorLogProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final latestLearningResponseProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final latestWebAutomationProgressProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final latestFeedbackResponseProvider = StateProvider<Map<String, dynamic>?>((ref) {
  return null;
});

final latestScreenshotProvider = StateProvider<Uint8List?>((ref) {
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
  
  // Notification fields
  final String? notificationMessage;
  final String? notificationType;
  final int? notificationTimestamp;
  
  // Intelligent Command State
  final bool isIntelligentCommandProcessing;
  final String? currentIntelligentCommand;
  final String? intelligentCommandStatus;
  final double intelligentCommandProgress;
  final String? currentStep;
  final List<Map<String, dynamic>>? commandSteps;
  final List<Map<String, dynamic>>? capabilities;

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
    this.notificationMessage,
    this.notificationType,
    this.notificationTimestamp,
    this.isIntelligentCommandProcessing = false,
    this.currentIntelligentCommand,
    this.intelligentCommandStatus,
    this.intelligentCommandProgress = 0.0,
    this.currentStep,
    this.commandSteps,
    this.capabilities,
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
    String? notificationMessage,
    String? notificationType,
    int? notificationTimestamp,
    bool? isIntelligentCommandProcessing,
    String? currentIntelligentCommand,
    String? intelligentCommandStatus,
    double? intelligentCommandProgress,
    String? currentStep,
    List<Map<String, dynamic>>? commandSteps,
    List<Map<String, dynamic>>? capabilities,
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
      notificationMessage: notificationMessage ?? this.notificationMessage,
      notificationType: notificationType ?? this.notificationType,
      notificationTimestamp: notificationTimestamp ?? this.notificationTimestamp,
      isIntelligentCommandProcessing: isIntelligentCommandProcessing ?? this.isIntelligentCommandProcessing,
      currentIntelligentCommand: currentIntelligentCommand ?? this.currentIntelligentCommand,
      intelligentCommandStatus: intelligentCommandStatus ?? this.intelligentCommandStatus,
      intelligentCommandProgress: intelligentCommandProgress ?? this.intelligentCommandProgress,
      currentStep: currentStep ?? this.currentStep,
      commandSteps: commandSteps ?? this.commandSteps,
      capabilities: capabilities ?? this.capabilities,
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
          
          // Update state with notification data
          state = state.copyWith(
            notificationMessage: notification,
            notificationType: type,
            notificationTimestamp: DateTime.now().millisecondsSinceEpoch,
          );
          break;
          
        case MessageType.pong:
          _logger.d('Received pong from server');
          break;
          
        case MessageType.status:
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
          
        case MessageType.intelligentCommandResponse:
          final command = message.data['command'] as String? ?? '';
          final response = message.data['response'] as String? ?? '';
          final success = message.data['success'] as bool? ?? false;
          
          state = state.copyWith(
            currentIntelligentCommand: command,
            intelligentCommandStatus: response,
            isIntelligentCommandProcessing: false,
          );
          
          if (success) {
            _logger.i('Intelligent command processed successfully: $command -> $response');
          } else {
            _logger.w('Intelligent command failed: $command');
          }
          break;
          
        case MessageType.intelligentCommandProgress:
          final progress = (message.data['progress'] as num?)?.toDouble() ?? 0.0;
          final status = message.data['status'] as String? ?? '';
          final currentStep = message.data['currentStep'] as String? ?? '';
          final steps = (message.data['steps'] as List?)
              ?.map((step) => Map<String, dynamic>.from(step))
              .toList();
          
          state = state.copyWith(
            intelligentCommandProgress: progress,
            intelligentCommandStatus: status,
            currentStep: currentStep,
            commandSteps: steps,
          );
          break;
          
        case MessageType.intelligentCommandStep:
          final stepName = message.data['stepName'] as String? ?? '';
          final stepStatus = message.data['stepStatus'] as String? ?? '';
          final stepProgress = (message.data['stepProgress'] as num?)?.toDouble() ?? 0.0;
          
          state = state.copyWith(
            currentStep: stepName,
            intelligentCommandStatus: stepStatus,
            intelligentCommandProgress: stepProgress,
          );
          break;
          
        case MessageType.quickCommandResponse:
          final command = message.data['command'] as String? ?? '';
          final response = message.data['response'] as String? ?? '';
          final success = message.data['success'] as bool? ?? false;
          
          state = state.copyWith(
            currentVoiceCommand: command,
            lastVoiceResponse: response,
            isProcessing: false,
          );
          
          if (success) {
            _logger.i('Quick command processed successfully: $command -> $response');
          } else {
            _logger.w('Quick command failed: $command');
          }
          break;
          
        case MessageType.capabilityResponse:
          final capabilities = (message.data['capabilities'] as List?)
              ?.map((cap) => Map<String, dynamic>.from(cap))
              .toList();
          
          if (capabilities != null) {
            state = state.copyWith(capabilities: capabilities);
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

  // Intelligent Command methods
  Future<void> sendIntelligentCommand(String command, {Map<String, dynamic>? context}) async {
    state = state.copyWith(
      isIntelligentCommandProcessing: true,
      currentIntelligentCommand: command,
      intelligentCommandStatus: 'Processing intelligent command...',
      intelligentCommandProgress: 0.0,
    );
    
    await _webSocketService.sendIntelligentCommand(command, context: context);
  }

  Future<void> sendQuickCommand(String command, {String? language, double? confidence}) async {
    state = state.copyWith(isProcessing: true);
    await _webSocketService.sendQuickCommand(command, language: language, confidence: confidence);
  }

  Future<void> requestCapabilities() async {
    await _webSocketService.requestCapabilities();
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
