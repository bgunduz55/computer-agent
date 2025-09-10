/// WebSocket Protocol Definitions for Flutter Client
/// 
/// Standardized message protocol for communication between
/// Flutter client and Python server.

import 'dart:convert';

enum MessageType {
  // Connection Management
  connect,
  disconnect,
  ping,
  pong,
  heartbeat,
  
  // Authentication
  authRequest,
  authResponse,
  
  // Voice Control
  voiceCommand,
  voiceResponse,
  voiceStatus,
  
  // AI Integration
  aiRequest,
  aiResponse,
  
  // Terminal Control
  terminalCommand,
  terminalResponse,
  terminalOutput,
  
  // System Control
  systemInfo,
  systemControl,
  systemResponse,
  
  // File Operations
  fileList,
  fileUpload,
  fileDownload,
  fileResponse,
  
  // RAG System
  ragDocuments,
  ragSearch,
  ragAddDocument,
  ragDeleteDocument,
  ragResponse,
  
  // Status and Health
  status,
  error,
  notification,
  
  // Remote Control
  screenshot,
  screenshotResponse,
  keyboardInput,
  mouseInput,
}

enum MessageStatus {
  pending,
  processing,
  success,
  error,
  timeout,
}

class WebSocketMessage {
  final MessageType type;
  final Map<String, dynamic> data;
  final double timestamp;
  final String messageId;
  final String? clientId;
  final MessageStatus status;
  final String? correlationId;
  final int retryCount;
  final int maxRetries;

  const WebSocketMessage({
    required this.type,
    required this.data,
    required this.timestamp,
    required this.messageId,
    this.clientId,
    this.status = MessageStatus.pending,
    this.correlationId,
    this.retryCount = 0,
    this.maxRetries = 3,
  });

  factory WebSocketMessage.fromJson(Map<String, dynamic> json) {
    return WebSocketMessage(
      type: MessageType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => MessageType.error,
      ),
      data: Map<String, dynamic>.from(json['data'] ?? {}),
      timestamp: (json['timestamp'] ?? 0).toDouble(),
      messageId: json['message_id'] ?? '',
      clientId: json['client_id'],
      status: MessageStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => MessageStatus.pending,
      ),
      correlationId: json['correlation_id'],
      retryCount: json['retry_count'] ?? 0,
      maxRetries: json['max_retries'] ?? 3,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type.name,
      'data': data,
      'timestamp': timestamp,
      'message_id': messageId,
      'client_id': clientId,
      'status': status.name,
      'correlation_id': correlationId,
      'retry_count': retryCount,
      'max_retries': maxRetries,
    };
  }

  String toJsonString() {
    return jsonEncode(toJson());
  }

  factory WebSocketMessage.fromJsonString(String jsonString) {
    return WebSocketMessage.fromJson(jsonDecode(jsonString));
  }

  bool get isRequest {
    return [
      MessageType.authRequest,
      MessageType.voiceCommand,
      MessageType.aiRequest,
      MessageType.systemControl,
      MessageType.fileList,
      MessageType.fileUpload,
      MessageType.fileDownload,
      MessageType.ragDocuments,
      MessageType.ragSearch,
      MessageType.ragAddDocument,
      MessageType.ragDeleteDocument,
      MessageType.screenshot,
      MessageType.ping,
    ].contains(type);
  }

  bool get isResponse {
    return [
      MessageType.authResponse,
      MessageType.voiceResponse,
      MessageType.aiResponse,
      MessageType.systemResponse,
      MessageType.fileResponse,
      MessageType.ragResponse,
      MessageType.screenshotResponse,
      MessageType.pong,
      MessageType.error,
    ].contains(type);
  }

  bool get shouldRetry {
    return status == MessageStatus.error && retryCount < maxRetries;
  }

  WebSocketMessage incrementRetry() {
    return WebSocketMessage(
      type: type,
      data: data,
      timestamp: timestamp,
      messageId: messageId,
      clientId: clientId,
      status: status,
      correlationId: correlationId,
      retryCount: retryCount + 1,
      maxRetries: maxRetries,
    );
  }
}

class MessageBuilder {
  static WebSocketMessage createVoiceCommand(String command, {String? clientId}) {
    return WebSocketMessage(
      type: MessageType.voiceCommand,
      data: {'command': command},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateId(),
      clientId: clientId,
    );
  }

  static WebSocketMessage createAiRequest(String prompt, {String? model, String? clientId}) {
    final data = {'prompt': prompt};
    if (model != null) data['model'] = model;
    
    return WebSocketMessage(
      type: MessageType.aiRequest,
      data: data,
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateId(),
      clientId: clientId,
    );
  }

  static WebSocketMessage createPing({String? clientId}) {
    return WebSocketMessage(
      type: MessageType.ping,
      data: {'timestamp': DateTime.now().millisecondsSinceEpoch / 1000.0},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateId(),
      clientId: clientId,
    );
  }

  static WebSocketMessage createAuthRequest(String token, {String? clientId}) {
    return WebSocketMessage(
      type: MessageType.authRequest,
      data: {'token': token},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateId(),
      clientId: clientId,
    );
  }

  static WebSocketMessage createSystemInfoRequest({String? clientId}) {
    return WebSocketMessage(
      type: MessageType.systemInfo,
      data: {},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateId(),
      clientId: clientId,
    );
  }

  static WebSocketMessage createErrorResponse(WebSocketMessage request, String errorMessage) {
    return WebSocketMessage(
      type: _getResponseType(request.type),
      data: {'error': errorMessage},
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateId(),
      clientId: request.clientId,
      status: MessageStatus.error,
      correlationId: request.messageId,
    );
  }

  static WebSocketMessage createSuccessResponse(WebSocketMessage request, Map<String, dynamic> data) {
    return WebSocketMessage(
      type: _getResponseType(request.type),
      data: data,
      timestamp: DateTime.now().millisecondsSinceEpoch / 1000.0,
      messageId: _generateId(),
      clientId: request.clientId,
      status: MessageStatus.success,
      correlationId: request.messageId,
    );
  }

  static MessageType _getResponseType(MessageType requestType) {
    switch (requestType) {
      case MessageType.authRequest:
        return MessageType.authResponse;
      case MessageType.voiceCommand:
        return MessageType.voiceResponse;
      case MessageType.aiRequest:
        return MessageType.aiResponse;
      case MessageType.systemControl:
        return MessageType.systemResponse;
      case MessageType.fileList:
      case MessageType.fileUpload:
      case MessageType.fileDownload:
        return MessageType.fileResponse;
      case MessageType.ragDocuments:
      case MessageType.ragSearch:
      case MessageType.ragAddDocument:
      case MessageType.ragDeleteDocument:
        return MessageType.ragResponse;
      case MessageType.screenshot:
        return MessageType.screenshotResponse;
      case MessageType.ping:
        return MessageType.pong;
      default:
        return MessageType.error;
    }
  }

  static String _generateId() {
    return DateTime.now().millisecondsSinceEpoch.toString() + 
           (1000 + (DateTime.now().microsecond % 9000)).toString();
  }
}
