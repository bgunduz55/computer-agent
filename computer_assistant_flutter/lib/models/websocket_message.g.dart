// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'websocket_message.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WebSocketMessage _$WebSocketMessageFromJson(Map<String, dynamic> json) =>
    WebSocketMessage(
      type: $enumDecode(_$MessageTypeEnumMap, json['type']),
      data: json['data'] as Map<String, dynamic>,
      timestamp: (json['timestamp'] as num).toDouble(),
      messageId: json['messageId'] as String,
      clientId: json['clientId'] as String?,
    );

Map<String, dynamic> _$WebSocketMessageToJson(WebSocketMessage instance) =>
    <String, dynamic>{
      'type': _$MessageTypeEnumMap[instance.type]!,
      'data': instance.data,
      'timestamp': instance.timestamp,
      'messageId': instance.messageId,
      'clientId': instance.clientId,
    };

const _$MessageTypeEnumMap = {
  MessageType.authRequest: 'auth_request',
  MessageType.authResponse: 'auth_response',
  MessageType.voiceCommand: 'voice_command',
  MessageType.voiceResponse: 'voice_response',
  MessageType.voiceStatus: 'voice_status',
  MessageType.terminalCommand: 'terminal_command',
  MessageType.terminalResponse: 'terminal_response',
  MessageType.terminalOutput: 'terminal_output',
  MessageType.aiRequest: 'ai_request',
  MessageType.aiResponse: 'ai_response',
  MessageType.systemInfo: 'system_info',
  MessageType.systemControl: 'system_control',
  MessageType.systemResponse: 'system_response',
  MessageType.fileUpload: 'file_upload',
  MessageType.fileDownload: 'file_download',
  MessageType.fileList: 'file_list',
  MessageType.fileResponse: 'file_response',
  MessageType.ping: 'ping',
  MessageType.pong: 'pong',
  MessageType.status: 'status',
  MessageType.error: 'error',
  MessageType.screenshot: 'screenshot',
  MessageType.screenshotResponse: 'screenshot_response',
  MessageType.keyboardInput: 'keyboard_input',
  MessageType.mouseInput: 'mouse_input',
};

ClientInfo _$ClientInfoFromJson(Map<String, dynamic> json) => ClientInfo(
      clientId: json['clientId'] as String,
      authenticated: json['authenticated'] as bool,
      connectedAt: (json['connectedAt'] as num).toDouble(),
      lastActivity: (json['lastActivity'] as num).toDouble(),
      userAgent: json['userAgent'] as String?,
      ipAddress: json['ipAddress'] as String?,
      permissions: (json['permissions'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$ClientInfoToJson(ClientInfo instance) =>
    <String, dynamic>{
      'clientId': instance.clientId,
      'authenticated': instance.authenticated,
      'connectedAt': instance.connectedAt,
      'lastActivity': instance.lastActivity,
      'userAgent': instance.userAgent,
      'ipAddress': instance.ipAddress,
      'permissions': instance.permissions,
    };

VoiceCommand _$VoiceCommandFromJson(Map<String, dynamic> json) => VoiceCommand(
      command: json['command'] as String,
      language: json['language'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$VoiceCommandToJson(VoiceCommand instance) =>
    <String, dynamic>{
      'command': instance.command,
      'language': instance.language,
      'confidence': instance.confidence,
    };

TerminalCommand _$TerminalCommandFromJson(Map<String, dynamic> json) =>
    TerminalCommand(
      command: json['command'] as String,
      terminalType: json['terminalType'] as String?,
      workingDirectory: json['workingDirectory'] as String?,
    );

Map<String, dynamic> _$TerminalCommandToJson(TerminalCommand instance) =>
    <String, dynamic>{
      'command': instance.command,
      'terminalType': instance.terminalType,
      'workingDirectory': instance.workingDirectory,
    };

TerminalResponse _$TerminalResponseFromJson(Map<String, dynamic> json) =>
    TerminalResponse(
      command: json['command'] as String,
      output: json['output'] as String,
      error: json['error'] as String,
      exitCode: (json['exitCode'] as num).toInt(),
      success: json['success'] as bool,
      executionTime: (json['executionTime'] as num).toDouble(),
    );

Map<String, dynamic> _$TerminalResponseToJson(TerminalResponse instance) =>
    <String, dynamic>{
      'command': instance.command,
      'output': instance.output,
      'error': instance.error,
      'exitCode': instance.exitCode,
      'success': instance.success,
      'executionTime': instance.executionTime,
    };

AIRequest _$AIRequestFromJson(Map<String, dynamic> json) => AIRequest(
      prompt: json['prompt'] as String,
      model: json['model'] as String?,
      maxTokens: (json['maxTokens'] as num?)?.toInt(),
      temperature: (json['temperature'] as num?)?.toDouble(),
      topP: (json['topP'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$AIRequestToJson(AIRequest instance) => <String, dynamic>{
      'prompt': instance.prompt,
      'model': instance.model,
      'maxTokens': instance.maxTokens,
      'temperature': instance.temperature,
      'topP': instance.topP,
    };

AIResponse _$AIResponseFromJson(Map<String, dynamic> json) => AIResponse(
      prompt: json['prompt'] as String,
      response: json['response'] as String,
      model: json['model'] as String,
      tokensUsed: (json['tokensUsed'] as num).toInt(),
      cost: (json['cost'] as num).toDouble(),
      success: json['success'] as bool,
    );

Map<String, dynamic> _$AIResponseToJson(AIResponse instance) =>
    <String, dynamic>{
      'prompt': instance.prompt,
      'response': instance.response,
      'model': instance.model,
      'tokensUsed': instance.tokensUsed,
      'cost': instance.cost,
      'success': instance.success,
    };

SystemInfo _$SystemInfoFromJson(Map<String, dynamic> json) => SystemInfo(
      platform: json['platform'] as String,
      platformVersion: json['platformVersion'] as String,
      architecture: json['architecture'] as String,
      processor: json['processor'] as String,
      pythonVersion: json['pythonVersion'] as String,
      availableTerminals: (json['availableTerminals'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      activeSessions: (json['activeSessions'] as num).toInt(),
      commandHistorySize: (json['commandHistorySize'] as num).toInt(),
    );

Map<String, dynamic> _$SystemInfoToJson(SystemInfo instance) =>
    <String, dynamic>{
      'platform': instance.platform,
      'platformVersion': instance.platformVersion,
      'architecture': instance.architecture,
      'processor': instance.processor,
      'pythonVersion': instance.pythonVersion,
      'availableTerminals': instance.availableTerminals,
      'activeSessions': instance.activeSessions,
      'commandHistorySize': instance.commandHistorySize,
    };

FileInfo _$FileInfoFromJson(Map<String, dynamic> json) => FileInfo(
      name: json['name'] as String,
      path: json['path'] as String,
      isDirectory: json['isDirectory'] as bool,
      size: (json['size'] as num).toInt(),
    );

Map<String, dynamic> _$FileInfoToJson(FileInfo instance) => <String, dynamic>{
      'name': instance.name,
      'path': instance.path,
      'isDirectory': instance.isDirectory,
      'size': instance.size,
    };
