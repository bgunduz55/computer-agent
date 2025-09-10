import 'package:json_annotation/json_annotation.dart';

part 'websocket_message.g.dart';

enum MessageType {
  @JsonValue('auth_request')
  authRequest,
  @JsonValue('auth_response')
  authResponse,
  @JsonValue('voice_command')
  voiceCommand,
  @JsonValue('voice_response')
  voiceResponse,
  @JsonValue('voice_status')
  voiceStatus,
  @JsonValue('terminal_command')
  terminalCommand,
  @JsonValue('terminal_response')
  terminalResponse,
  @JsonValue('terminal_output')
  terminalOutput,
  @JsonValue('ai_request')
  aiRequest,
  @JsonValue('ai_response')
  aiResponse,
  @JsonValue('system_info')
  systemInfo,
  @JsonValue('system_control')
  systemControl,
  @JsonValue('system_response')
  systemResponse,
  @JsonValue('file_upload')
  fileUpload,
  @JsonValue('file_download')
  fileDownload,
  @JsonValue('file_list')
  fileList,
  @JsonValue('file_response')
  fileResponse,
  @JsonValue('ping')
  ping,
  @JsonValue('pong')
  pong,
  @JsonValue('status')
  status,
  @JsonValue('error')
  error,
  @JsonValue('screenshot')
  screenshot,
  @JsonValue('screenshot_response')
  screenshotResponse,
  @JsonValue('keyboard_input')
  keyboardInput,
  @JsonValue('mouse_input')
  mouseInput,
}

@JsonSerializable()
class WebSocketMessage {
  final MessageType type;
  final Map<String, dynamic> data;
  final double timestamp;
  final String messageId;
  final String? clientId;

  const WebSocketMessage({
    required this.type,
    required this.data,
    required this.timestamp,
    required this.messageId,
    this.clientId,
  });

  factory WebSocketMessage.fromJson(Map<String, dynamic> json) =>
      _$WebSocketMessageFromJson(json);

  Map<String, dynamic> toJson() => _$WebSocketMessageToJson(this);

  WebSocketMessage copyWith({
    MessageType? type,
    Map<String, dynamic>? data,
    double? timestamp,
    String? messageId,
    String? clientId,
  }) {
    return WebSocketMessage(
      type: type ?? this.type,
      data: data ?? this.data,
      timestamp: timestamp ?? this.timestamp,
      messageId: messageId ?? this.messageId,
      clientId: clientId ?? this.clientId,
    );
  }
}

@JsonSerializable()
class ClientInfo {
  final String clientId;
  final bool authenticated;
  final double connectedAt;
  final double lastActivity;
  final String? userAgent;
  final String? ipAddress;
  final List<String>? permissions;

  const ClientInfo({
    required this.clientId,
    required this.authenticated,
    required this.connectedAt,
    required this.lastActivity,
    this.userAgent,
    this.ipAddress,
    this.permissions,
  });

  factory ClientInfo.fromJson(Map<String, dynamic> json) =>
      _$ClientInfoFromJson(json);

  Map<String, dynamic> toJson() => _$ClientInfoToJson(this);
}

@JsonSerializable()
class VoiceCommand {
  final String command;
  final String? language;
  final double? confidence;

  const VoiceCommand({
    required this.command,
    this.language,
    this.confidence,
  });

  factory VoiceCommand.fromJson(Map<String, dynamic> json) =>
      _$VoiceCommandFromJson(json);

  Map<String, dynamic> toJson() => _$VoiceCommandToJson(this);
}

@JsonSerializable()
class TerminalCommand {
  final String command;
  final String? terminalType;
  final String? workingDirectory;

  const TerminalCommand({
    required this.command,
    this.terminalType,
    this.workingDirectory,
  });

  factory TerminalCommand.fromJson(Map<String, dynamic> json) =>
      _$TerminalCommandFromJson(json);

  Map<String, dynamic> toJson() => _$TerminalCommandToJson(this);
}

@JsonSerializable()
class TerminalResponse {
  final String command;
  final String output;
  final String error;
  final int exitCode;
  final bool success;
  final double executionTime;

  const TerminalResponse({
    required this.command,
    required this.output,
    required this.error,
    required this.exitCode,
    required this.success,
    required this.executionTime,
  });

  factory TerminalResponse.fromJson(Map<String, dynamic> json) =>
      _$TerminalResponseFromJson(json);

  Map<String, dynamic> toJson() => _$TerminalResponseToJson(this);
}

@JsonSerializable()
class AIRequest {
  final String prompt;
  final String? model;
  final int? maxTokens;
  final double? temperature;
  final double? topP;

  const AIRequest({
    required this.prompt,
    this.model,
    this.maxTokens,
    this.temperature,
    this.topP,
  });

  factory AIRequest.fromJson(Map<String, dynamic> json) =>
      _$AIRequestFromJson(json);

  Map<String, dynamic> toJson() => _$AIRequestToJson(this);
}

@JsonSerializable()
class AIResponse {
  final String prompt;
  final String response;
  final String model;
  final int tokensUsed;
  final double cost;
  final bool success;

  const AIResponse({
    required this.prompt,
    required this.response,
    required this.model,
    required this.tokensUsed,
    required this.cost,
    required this.success,
  });

  factory AIResponse.fromJson(Map<String, dynamic> json) =>
      _$AIResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AIResponseToJson(this);
}

@JsonSerializable()
class SystemInfo {
  final String platform;
  final String platformVersion;
  final String architecture;
  final String processor;
  final String pythonVersion;
  final List<String> availableTerminals;
  final int activeSessions;
  final int commandHistorySize;

  const SystemInfo({
    required this.platform,
    required this.platformVersion,
    required this.architecture,
    required this.processor,
    required this.pythonVersion,
    required this.availableTerminals,
    required this.activeSessions,
    required this.commandHistorySize,
  });

  factory SystemInfo.fromJson(Map<String, dynamic> json) =>
      _$SystemInfoFromJson(json);

  Map<String, dynamic> toJson() => _$SystemInfoToJson(this);
}

@JsonSerializable()
class FileInfo {
  final String name;
  final String path;
  final bool isDirectory;
  final int size;

  const FileInfo({
    required this.name,
    required this.path,
    required this.isDirectory,
    required this.size,
  });

  factory FileInfo.fromJson(Map<String, dynamic> json) =>
      _$FileInfoFromJson(json);

  Map<String, dynamic> toJson() => _$FileInfoToJson(this);
}
