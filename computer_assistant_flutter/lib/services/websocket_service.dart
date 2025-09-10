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
