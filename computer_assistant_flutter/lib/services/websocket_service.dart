import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:logger/logger.dart';
import '../shared/websocket_config.dart';
import '../shared/websocket_protocol.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;

  final Logger _logger = Logger();
  WebSocketChannel? _channel;
  StreamController<WebSocketMessage>? _messageController;
  StreamController<bool>? _connectionController;
  Timer? _pingTimer;
  Timer? _reconnectTimer;
  
  String? _serverUrl;
  String? _authToken;
  bool _isConnected = false;
  bool _isAuthenticated = false;
  int _reconnectAttempts = 0;
  
  late WebSocketConfig _config;
  
  WebSocketService._internal() {
    _config = WebSocketConfigManager.instance.config;
  }
  
  // Message queuing for offline mode
  final List<WebSocketMessage> _messageQueue = [];
  static const int _maxQueueSize = 100;

  // Getters
  bool get isConnected => _isConnected;
  bool get isAuthenticated => _isAuthenticated;
  String? get serverUrl => _serverUrl;
  String? get authToken => _authToken;

  // Streams
  Stream<WebSocketMessage> get messageStream {
    _messageController ??= StreamController<WebSocketMessage>.broadcast();
    return _messageController!.stream;
  }

  Stream<bool> get connectionStream {
    _connectionController ??= StreamController<bool>.broadcast();
    return _connectionController!.stream;
  }

  /// Initialize and auto-connect if enabled
  Future<void> initialize() async {
    // Auto-connect if config allows it
    if (_config.loggingEnabled) {
      _logger.i('Initializing WebSocket service with config: ${_config.url}');
    }
    
    // Auto-connect
    await connect(_config.url);
  }

  /// Connect to WebSocket server
  Future<bool> connect(String serverUrl, {String? authToken}) async {
    try {
      _serverUrl = serverUrl;
      _authToken = authToken;
      
      if (_config.loggingEnabled) {
        _logger.i('Connecting to WebSocket server: $serverUrl');
      }
      
      // Validate server URL
      if (!_isValidUrl(serverUrl)) {
        throw Exception('Invalid server URL format. Must start with ws:// or wss://');
      }
      
      _channel = WebSocketChannel.connect(Uri.parse(serverUrl));
      
      // Listen to messages with enhanced error handling
      _channel!.stream.listen(
        _onMessage,
        onError: (error) {
          if (_config.loggingEnabled) {
            _logger.e('WebSocket stream error: $error');
          }
          _onError(error);
        },
        onDone: () {
          if (_config.loggingEnabled) {
            _logger.i('WebSocket stream closed');
          }
          _onDone();
        },
        cancelOnError: false,
      );
      
      _isConnected = true;
      _connectionController?.add(true);
      
      // Start ping timer
      _startPingTimer();
      
      // Authentication disabled for now
      if (_config.loggingEnabled) {
        _logger.i('Authentication disabled - connecting without auth');
      }
      
      // Send queued messages
      await _sendQueuedMessages();
      
      _logger.i('Connected to WebSocket server');
      return true;
      
    } catch (e) {
      _logger.e('Failed to connect to WebSocket server: $e');
      _isConnected = false;
      _connectionController?.add(false);
      
      // Attempt to reconnect
      _attemptReconnect();
      return false;
    }
  }
  
  /// Validate URL format
  bool _isValidUrl(String url) {
    try {
      final uri = Uri.parse(url);
      return uri.hasScheme && (uri.scheme == 'ws' || uri.scheme == 'wss');
    } catch (e) {
      return false;
    }
  }

  /// Disconnect from WebSocket server
  Future<void> disconnect() async {
    try {
      _logger.i('Disconnecting from WebSocket server');
      
      _stopPingTimer();
      _stopReconnectTimer();
      
      await _channel?.sink.close(status.goingAway);
      _channel = null;
      
      _isConnected = false;
      _isAuthenticated = false;
      _connectionController?.add(false);
      
      _logger.i('Disconnected from WebSocket server');
      
    } catch (e) {
      _logger.e('Error disconnecting from WebSocket server: $e');
    }
  }

  /// Authenticate with server
  Future<bool> authenticate(String token) async {
    try {
      _logger.i('Authenticating with server');
      
      final message = WebSocketMessage(
        type: MessageType.authRequest,
        data: {'token': token},
        timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
        messageId: _generateMessageId(),
      );
      
      await sendMessage(message);
      
      // Wait for authentication response
      final completer = Completer<bool>();
      late StreamSubscription subscription;
      
      subscription = messageStream.listen((msg) {
        if (msg.type == MessageType.authResponse) {
          subscription.cancel();
          final success = msg.data['success'] as bool? ?? false;
          _isAuthenticated = success;
          completer.complete(success);
          
          if (success) {
            _logger.i('Authentication successful');
            _reconnectAttempts = 0;
          } else {
            _logger.w('Authentication failed: ${msg.data['message']}');
          }
        }
      });
      
      // Timeout after 10 seconds
      Timer(const Duration(seconds: 10), () {
        if (!completer.isCompleted) {
          subscription.cancel();
          completer.complete(false);
          _logger.w('Authentication timeout');
        }
      });
      
      return await completer.future;
      
    } catch (e) {
      _logger.e('Authentication error: $e');
      return false;
    }
  }

  /// Send message to server
  Future<void> sendMessage(WebSocketMessage message) async {
    try {
      if (_channel == null || !_isConnected) {
        if (_config.loggingEnabled) {
          _logger.w('Cannot send message: not connected, queuing message');
        }
        _queueMessage(message);
        return;
      }
      
      final json = message.toJsonString();
      _channel!.sink.add(json);
      
      if (_config.loggingEnabled && _config.logRequests) {
        _logger.d('Sent message: ${message.type.name}');
        _logger.d('Message JSON: $json');
      }
      
    } catch (e) {
      if (_config.loggingEnabled) {
        _logger.e('Error sending message: $e');
      }
      _queueMessage(message);
    }
  }

  /// Queue message for later sending
  void _queueMessage(WebSocketMessage message) {
    if (_messageQueue.length >= _maxQueueSize) {
      _messageQueue.removeAt(0); // Remove oldest message
    }
    _messageQueue.add(message);
    _logger.d('Queued message: ${message.type.name} (queue size: ${_messageQueue.length})');
  }

  /// Send queued messages
  Future<void> _sendQueuedMessages() async {
    if (_messageQueue.isEmpty) return;
    
    _logger.i('Sending ${_messageQueue.length} queued messages');
    
    final messages = List<WebSocketMessage>.from(_messageQueue);
    _messageQueue.clear();
    
    for (final message in messages) {
      try {
        final json = jsonEncode(message.toJson());
        _channel!.sink.add(json);
        _logger.d('Sent queued message: ${message.type.name}');
      } catch (e) {
        _logger.e('Error sending queued message: $e');
        _queueMessage(message); // Re-queue failed message
      }
    }
  }

  /// Send voice command
  Future<void> sendVoiceCommand(String command, {String? language, double? confidence}) async {
    final message = WebSocketMessage(
      type: MessageType.voiceCommand,
      data: {
        'command': command,
        if (language != null) 'language': language,
        if (confidence != null) 'confidence': confidence,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send command
  Future<void> sendCommand(String command) async {
    final message = WebSocketMessage(
      type: MessageType.command,
      data: {'command': command},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send terminal command
  Future<void> sendTerminalCommand(String command, {String? terminalType, String? workingDirectory}) async {
    final message = WebSocketMessage(
      type: MessageType.terminalCommand,
      data: {
        'command': command,
        if (terminalType != null) 'terminal_type': terminalType,
        if (workingDirectory != null) 'working_directory': workingDirectory,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send AI request
  Future<void> sendAIRequest(String prompt, {String? model, int? maxTokens, double? temperature, double? topP}) async {
    final message = WebSocketMessage(
      type: MessageType.aiRequest,
      data: {
        'prompt': prompt,
        if (model != null) 'model': model,
        if (maxTokens != null) 'max_tokens': maxTokens,
        if (temperature != null) 'temperature': temperature,
        if (topP != null) 'top_p': topP,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send intelligent command (AI-powered multi-step commands)
  Future<void> sendIntelligentCommand(String command, {Map<String, dynamic>? context}) async {
    final message = WebSocketMessage(
      type: MessageType.intelligentCommand,
      data: {
        'command': command,
        'context': context ?? {},
        'timestamp': DateTime.now().millisecondsSinceEpoch / 1000.0,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send quick command (single action commands)
  Future<void> sendQuickCommand(String command, {String? language, double? confidence}) async {
    final message = WebSocketMessage(
      type: MessageType.quickCommand,
      data: {
        'command': command,
        if (language != null) 'language': language,
        if (confidence != null) 'confidence': confidence,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Request capabilities
  Future<void> requestCapabilities() async {
    final message = WebSocketMessage(
      type: MessageType.capabilityRequest,
      data: {},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send system control command
  Future<void> sendSystemControl(String action, {Map<String, dynamic>? params}) async {
    final message = WebSocketMessage(
      type: MessageType.systemControl,
      data: {
        'action': action,
        if (params != null) 'params': params,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Request system info
  Future<void> requestSystemInfo() async {
    final message = WebSocketMessage(
      type: MessageType.systemInfo,
      data: {},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Request file list
  Future<void> requestFileList(String path) async {
    final message = WebSocketMessage(
      type: MessageType.fileList,
      data: {'path': path},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Request screenshot
  Future<void> requestScreenshot() async {
    final message = WebSocketMessage(
      type: MessageType.screenshot,
      data: {},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  // RAG methods
  /// Request RAG documents
  Future<void> requestRAGDocuments() async {
    final message = WebSocketMessage(
      type: MessageType.ragDocuments,
      data: {},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Search RAG documents
  Future<void> searchRAGDocuments(String query) async {
    final message = WebSocketMessage(
      type: MessageType.ragSearch,
      data: {'query': query},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Add RAG document
  Future<void> addRAGDocument(String content, Map<String, dynamic> metadata) async {
    final message = WebSocketMessage(
      type: MessageType.ragAddDocument,
      data: {
        'content': content,
        'metadata': metadata,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Delete RAG document
  Future<void> deleteRAGDocument(String docId) async {
    final message = WebSocketMessage(
      type: MessageType.ragDeleteDocument,
      data: {'docId': docId},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send ping
  Future<void> sendPing() async {
    final message = WebSocketMessage(
      type: MessageType.ping,
      data: {},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  // ===== NEW BACKEND INTEGRATION METHODS =====

  /// Send progress tracking request
  Future<void> requestProgressTracking(String executionId) async {
    final message = WebSocketMessage(
      type: MessageType.progressStart,
      data: {'execution_id': executionId},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send feedback
  Future<void> sendFeedback(String executionId, Map<String, dynamic> feedback) async {
    final message = WebSocketMessage(
      type: MessageType.feedbackSubmit,
      data: {
        'execution_id': executionId,
        'feedback': feedback,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Create terminal session
  Future<void> createTerminalSession({
    String? name,
    String? sessionType,
    String? terminalType,
    String? workingDirectory,
    String? description,
    List<String>? tags,
  }) async {
    final message = WebSocketMessage(
      type: MessageType.terminalSessionCreate,
      data: {
        if (name != null) 'name': name,
        if (sessionType != null) 'session_type': sessionType,
        if (terminalType != null) 'terminal_type': terminalType,
        if (workingDirectory != null) 'working_directory': workingDirectory,
        if (description != null) 'description': description,
        if (tags != null) 'tags': tags,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Execute terminal command in session
  Future<void> executeTerminalSessionCommand(String sessionId, String command, {int? timeout}) async {
    final message = WebSocketMessage(
      type: MessageType.terminalSessionExecute,
      data: {
        'session_id': sessionId,
        'command': command,
        if (timeout != null) 'timeout': timeout,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// List terminal sessions
  Future<void> listTerminalSessions() async {
    final message = WebSocketMessage(
      type: MessageType.terminalSessionList,
      data: {},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Get terminal session history
  Future<void> getTerminalSessionHistory(String sessionId, {int? limit, String? query}) async {
    final message = WebSocketMessage(
      type: MessageType.terminalSessionHistory,
      data: {
        'session_id': sessionId,
        if (limit != null) 'limit': limit,
        if (query != null) 'query': query,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Request analytics data
  Future<void> requestAnalytics({String? reportType, int? hours}) async {
    final message = WebSocketMessage(
      type: MessageType.analyticsRequest,
      data: {
        if (reportType != null) 'report_type': reportType,
        if (hours != null) 'hours': hours,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Request real-time metrics
  Future<void> requestRealTimeMetrics() async {
    final message = WebSocketMessage(
      type: MessageType.analyticsMetrics,
      data: {},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Log event
  Future<void> logEvent(String level, String eventType, String message, {
    String? sessionId,
    String? component,
    Map<String, dynamic>? metadata,
    List<String>? tags,
  }) async {
    final logMessage = WebSocketMessage(
      type: MessageType.logEvent,
      data: {
        'level': level,
        'event_type': eventType,
        'message': message,
        if (sessionId != null) 'session_id': sessionId,
        if (component != null) 'component': component,
        if (metadata != null) 'metadata': metadata,
        if (tags != null) 'tags': tags,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(logMessage);
  }

  /// Record metric
  Future<void> recordMetric(String metricType, String name, dynamic value, {
    String? unit,
    Map<String, String>? labels,
    Map<String, dynamic>? metadata,
  }) async {
    final message = WebSocketMessage(
      type: MessageType.metricsRecord,
      data: {
        'metric_type': metricType,
        'name': name,
        'value': value,
        if (unit != null) 'unit': unit,
        if (labels != null) 'labels': labels,
        if (metadata != null) 'metadata': metadata,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Update execution context
  Future<void> updateExecutionContext(String sessionId, Map<String, dynamic> contextUpdates) async {
    final message = WebSocketMessage(
      type: MessageType.contextUpdate,
      data: {
        'session_id': sessionId,
        'context_updates': contextUpdates,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Store memory entry
  Future<void> storeMemoryEntry(String sessionId, String key, dynamic value, {
    String? contextType,
    String? priority,
    List<String>? tags,
    double? expiresAt,
  }) async {
    final message = WebSocketMessage(
      type: MessageType.memoryStore,
      data: {
        'session_id': sessionId,
        'key': key,
        'value': value,
        if (contextType != null) 'context_type': contextType,
        if (priority != null) 'priority': priority,
        if (tags != null) 'tags': tags,
        if (expiresAt != null) 'expires_at': expiresAt,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Search memory entries
  Future<void> searchMemoryEntries(String sessionId, {
    String? query,
    String? contextType,
    String? priority,
    List<String>? tags,
    int? limit,
  }) async {
    final message = WebSocketMessage(
      type: MessageType.memorySearch,
      data: {
        'session_id': sessionId,
        if (query != null) 'query': query,
        if (contextType != null) 'context_type': contextType,
        if (priority != null) 'priority': priority,
        if (tags != null) 'tags': tags,
        if (limit != null) 'limit': limit,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Start web automation
  Future<void> startWebAutomation(String action, Map<String, dynamic> parameters) async {
    final message = WebSocketMessage(
      type: MessageType.webAutomationStart,
      data: {
        'action': action,
        'parameters': parameters,
      },
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Send mobile status
  Future<void> sendMobileStatus(Map<String, dynamic> status) async {
    final message = WebSocketMessage(
      type: MessageType.mobileStatus,
      data: status,
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateMessageId(),
    );
    
    await sendMessage(message);
  }

  /// Handle incoming messages
  void _onMessage(dynamic data) {
    try {
      final message = WebSocketMessage.fromJsonString(data);
      _messageController?.add(message);
      
      if (_config.loggingEnabled && _config.logResponses) {
        _logger.d('Received message: ${message.type.name}');
        _logger.d('Message data: ${message.data}');
      }
      
      // Handle specific message types
      _handleMessageType(message);
      
    } catch (e) {
      if (_config.loggingEnabled) {
        _logger.e('Error parsing message: $e');
      }
    }
  }
  
  /// Handle specific message types
  void _handleMessageType(WebSocketMessage message) {
    switch (message.type) {
      case MessageType.voiceResponse:
        _handleVoiceResponse(message);
        break;
      case MessageType.notification:
        _handleNotification(message);
        break;
      case MessageType.error:
        _handleError(message);
        break;
      case MessageType.pong:
        _handlePong(message);
        break;
      // Intelligent Commands
      case MessageType.intelligentCommandResponse:
        _handleIntelligentCommandResponse(message);
        break;
      case MessageType.intelligentCommandProgress:
        _handleIntelligentCommandProgress(message);
        break;
      case MessageType.intelligentCommandStep:
        _handleIntelligentCommandStep(message);
        break;
      // Progress Tracking
      case MessageType.progressStart:
      case MessageType.progressUpdate:
      case MessageType.progressComplete:
      case MessageType.progressError:
        _handleProgressMessage(message);
        break;
      // Terminal Session Management
      case MessageType.terminalSessionResponse:
      case MessageType.terminalSessionOutput:
      case MessageType.terminalSessionHistory:
      case MessageType.terminalSessionList:
        _handleTerminalSessionMessage(message);
        break;
      // Analytics and Logging
      case MessageType.analyticsResponse:
      case MessageType.analyticsMetrics:
      case MessageType.analyticsReport:
      case MessageType.logResponse:
      case MessageType.metricsResponse:
        _handleAnalyticsMessage(message);
        break;
      // Context-Aware Execution
      case MessageType.contextResponse:
      case MessageType.memoryRetrieve:
      case MessageType.memorySearch:
        _handleContextMessage(message);
        break;
      // Web Automation
      case MessageType.webAutomationResponse:
      case MessageType.webAutomationProgress:
      case MessageType.webAutomationComplete:
      case MessageType.webAutomationScreenshot:
        _handleWebAutomationMessage(message);
        break;
      // Mobile Monitoring
      case MessageType.mobileStatusResponse:
      case MessageType.mobileCommandResponse:
      case MessageType.mobileNotification:
        _handleMobileMessage(message);
        break;
      // Feedback System
      case MessageType.feedbackResponse:
        _handleFeedbackMessage(message);
        break;
      default:
        if (_config.loggingEnabled) {
          _logger.d('Unhandled message type: ${message.type.name}');
        }
    }
  }
  
  /// Handle voice response
  void _handleVoiceResponse(WebSocketMessage message) {
    final response = message.data['response'] as String?;
    if (response != null) {
      _logger.i('Voice response: $response');
      // Update UI with voice response
      _messageController?.add(message);
    }
  }
  
  /// Handle notification
  void _handleNotification(WebSocketMessage message) {
    final notification = message.data['message'] as String?;
    final type = message.data['type'] as String?;
    if (notification != null) {
      _logger.i('Notification ($type): $notification');
      // Show notification to user
      _messageController?.add(message);
    }
  }
  
  /// Handle error
  void _handleError(WebSocketMessage message) {
    final error = message.data['error'] as String?;
    if (error != null) {
      _logger.e('Server error: $error');
      // Show error to user
      _messageController?.add(message);
    }
  }
  
  /// Handle pong
  void _handlePong(WebSocketMessage message) {
    if (_config.loggingEnabled) {
      _logger.d('Received pong from server');
    }
  }

  // ===== NEW MESSAGE HANDLERS =====

  /// Handle progress tracking messages
  void _handleProgressMessage(WebSocketMessage message) {
    final executionId = message.data['execution_id'] as String?;
    final progress = message.data['progress'] as double?;
    final status = message.data['status'] as String?;
    final message_text = message.data['message'] as String?;
    
    if (_config.loggingEnabled) {
      _logger.d('Progress update: $executionId - $status (${progress?.toStringAsFixed(1)}%)');
    }
    
    // Forward to message stream for UI consumption
    _messageController?.add(message);
  }

  /// Handle terminal session messages
  void _handleTerminalSessionMessage(WebSocketMessage message) {
    final sessionId = message.data['session_id'] as String?;
    final output = message.data['output'] as String?;
    final command = message.data['command'] as String?;
    
    if (_config.loggingEnabled) {
      _logger.d('Terminal session update: $sessionId - ${message.type.name}');
    }
    
    // Forward to message stream for UI consumption
    _messageController?.add(message);
  }

  /// Handle analytics messages
  void _handleAnalyticsMessage(WebSocketMessage message) {
    final reportType = message.data['report_type'] as String?;
    final metrics = message.data['metrics'] as Map<String, dynamic>?;
    
    if (_config.loggingEnabled) {
      _logger.d('Analytics update: ${message.type.name} - $reportType');
    }
    
    // Forward to message stream for UI consumption
    _messageController?.add(message);
  }

  /// Handle context-aware execution messages
  void _handleContextMessage(WebSocketMessage message) {
    final sessionId = message.data['session_id'] as String?;
    final context = message.data['context'] as Map<String, dynamic>?;
    final memory = message.data['memory'] as List<dynamic>?;
    
    if (_config.loggingEnabled) {
      _logger.d('Context update: $sessionId - ${message.type.name}');
    }
    
    // Forward to message stream for UI consumption
    _messageController?.add(message);
  }

  /// Handle web automation messages
  void _handleWebAutomationMessage(WebSocketMessage message) {
    final action = message.data['action'] as String?;
    final status = message.data['status'] as String?;
    final screenshot = message.data['screenshot'] as String?;
    
    if (_config.loggingEnabled) {
      _logger.d('Web automation update: $action - $status');
    }
    
    // Forward to message stream for UI consumption
    _messageController?.add(message);
  }

  /// Handle mobile monitoring messages
  void _handleMobileMessage(WebSocketMessage message) {
    final status = message.data['status'] as String?;
    final command = message.data['command'] as String?;
    final notification = message.data['notification'] as String?;
    
    if (_config.loggingEnabled) {
      _logger.d('Mobile update: ${message.type.name} - $status');
    }
    
    // Forward to message stream for UI consumption
    _messageController?.add(message);
  }

  /// Handle feedback messages
  void _handleFeedbackMessage(WebSocketMessage message) {
    final executionId = message.data['execution_id'] as String?;
    final feedback = message.data['feedback'] as Map<String, dynamic>?;
    final status = message.data['status'] as String?;
    
    if (_config.loggingEnabled) {
      _logger.d('Feedback update: $executionId - $status');
    }
    
    // Forward to message stream for UI consumption
    _messageController?.add(message);
  }

  /// Handle connection errors
  void _onError(error) {
    _logger.e('WebSocket error: $error');
    _isConnected = false;
    _isAuthenticated = false;
    _connectionController?.add(false);
    
    // Attempt to reconnect
    _attemptReconnect();
  }

  /// Handle connection close
  void _onDone() {
    _logger.i('WebSocket connection closed');
    _isConnected = false;
    _isAuthenticated = false;
    _connectionController?.add(false);
    
    // Attempt to reconnect
    _attemptReconnect();
  }

  /// Start ping timer
  void _startPingTimer() {
    _stopPingTimer();
    _pingTimer = Timer.periodic(Duration(seconds: _config.pingInterval), (timer) {
      if (_isConnected) {
        sendPing();
      }
    });
  }

  /// Stop ping timer
  void _stopPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = null;
  }

  /// Stop reconnect timer
  void _stopReconnectTimer() {
    _reconnectTimer?.cancel();
    _reconnectTimer = null;
  }

  /// Attempt to reconnect
  void _attemptReconnect() {
    if (_reconnectAttempts >= _config.reconnectAttempts) {
      if (_config.loggingEnabled) {
        _logger.w('Max reconnection attempts reached');
      }
      _connectionController?.add(false);
      return;
    }
    
    _reconnectAttempts++;
    if (_config.loggingEnabled) {
      _logger.i('Attempting to reconnect (${_reconnectAttempts}/${_config.reconnectAttempts})');
    }
    
    // Exponential backoff
    final delay = Duration(milliseconds: _config.reconnectDelay * _reconnectAttempts);
    
    _reconnectTimer = Timer(delay, () async {
      if (_serverUrl != null) {
        final success = await connect(_serverUrl!, authToken: _authToken);
        if (!success) {
          _attemptReconnect();
        }
      }
    });
  }

  /// Handle intelligent command response
  void _handleIntelligentCommandResponse(WebSocketMessage message) {
    _logger.i('Intelligent command response: ${message.data}');
    _messageController?.add(message);
  }

  /// Handle intelligent command progress
  void _handleIntelligentCommandProgress(WebSocketMessage message) {
    _logger.i('Intelligent command progress: ${message.data}');
    _messageController?.add(message);
  }

  /// Handle intelligent command step
  void _handleIntelligentCommandStep(WebSocketMessage message) {
    _logger.i('Intelligent command step: ${message.data}');
    _messageController?.add(message);
  }

  /// Generate unique message ID
  String _generateMessageId() {
    return '${DateTime.now().millisecondsSinceEpoch}${1000 + (DateTime.now().microsecond % 1000)}';
  }

  /// Dispose resources
  void dispose() {
    _stopPingTimer();
    _stopReconnectTimer();
    _messageController?.close();
    _connectionController?.close();
    _channel?.sink.close();
  }
}
