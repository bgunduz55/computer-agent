import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:logger/logger.dart';
import '../models/websocket_message.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

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
  static const int _maxReconnectAttempts = 5;
  static const Duration _reconnectDelay = Duration(seconds: 5);

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

  /// Connect to WebSocket server
  Future<bool> connect(String serverUrl, {String? authToken}) async {
    try {
      _serverUrl = serverUrl;
      _authToken = authToken;
      
      _logger.i('Connecting to WebSocket server: $serverUrl');
      
      _channel = WebSocketChannel.connect(Uri.parse(serverUrl));
      
      // Listen to messages
      _channel!.stream.listen(
        _onMessage,
        onError: _onError,
        onDone: _onDone,
      );
      
      _isConnected = true;
      _connectionController?.add(true);
      
      // Start ping timer
      _startPingTimer();
      
      // Authenticate if token provided
      if (authToken != null) {
        await authenticate(authToken);
      }
      
      _logger.i('Connected to WebSocket server');
      return true;
      
    } catch (e) {
      _logger.e('Failed to connect to WebSocket server: $e');
      _isConnected = false;
      _connectionController?.add(false);
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
        _logger.w('Cannot send message: not connected');
        return;
      }
      
      final json = jsonEncode(message.toJson());
      _channel!.sink.add(json);
      
      _logger.d('Sent message: ${message.type.name}');
      
    } catch (e) {
      _logger.e('Error sending message: $e');
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
      final json = jsonDecode(data);
      final message = WebSocketMessage.fromJson(json);
      _messageController?.add(message);
      
      _logger.d('Received message: ${message.type.name}');
      
    } catch (e) {
      _logger.e('Error parsing message: $e');
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
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
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
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      _logger.w('Max reconnection attempts reached');
      return;
    }
    
    _reconnectAttempts++;
    _logger.i('Attempting to reconnect (${_reconnectAttempts}/$_maxReconnectAttempts)');
    
    _reconnectTimer = Timer(_reconnectDelay, () {
      if (_serverUrl != null) {
        connect(_serverUrl!, authToken: _authToken);
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
