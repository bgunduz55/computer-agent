/// WebSocket Message Models
/// 
/// Re-exports WebSocket message classes from the protocol definition
/// for easier imports and code generation compatibility.

export '../shared/websocket_protocol.dart';

// Additional message models that might be needed
class ClientInfo {
  final String id;
  final String name;
  final String platform;
  final String version;
  final Map<String, dynamic> capabilities;
  final double lastSeen;

  const ClientInfo({
    required this.id,
    required this.name,
    required this.platform,
    required this.version,
    required this.capabilities,
    required this.lastSeen,
  });

  factory ClientInfo.fromJson(Map<String, dynamic> json) {
    return ClientInfo(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      platform: json['platform'] ?? '',
      version: json['version'] ?? '',
      capabilities: Map<String, dynamic>.from(json['capabilities'] ?? {}),
      lastSeen: (json['last_seen'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'platform': platform,
      'version': version,
      'capabilities': capabilities,
      'last_seen': lastSeen,
    };
  }
}

class VoiceCommand {
  final String command;
  final String? language;
  final double confidence;

  const VoiceCommand({
    required this.command,
    this.language,
    this.confidence = 1.0,
  });

  factory VoiceCommand.fromJson(Map<String, dynamic> json) {
    return VoiceCommand(
      command: json['command'] ?? '',
      language: json['language'],
      confidence: (json['confidence'] ?? 1.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'command': command,
      'language': language,
      'confidence': confidence,
    };
  }
}

class TerminalCommand {
  final String command;
  final String? workingDirectory;
  final Map<String, String>? environment;

  const TerminalCommand({
    required this.command,
    this.workingDirectory,
    this.environment,
  });

  factory TerminalCommand.fromJson(Map<String, dynamic> json) {
    return TerminalCommand(
      command: json['command'] ?? '',
      workingDirectory: json['working_directory'],
      environment: json['environment'] != null 
          ? Map<String, String>.from(json['environment'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'command': command,
      'working_directory': workingDirectory,
      'environment': environment,
    };
  }
}

class TerminalResponse {
  final String output;
  final String? error;
  final int exitCode;
  final double timestamp;
  final String? command;

  const TerminalResponse({
    required this.output,
    this.error,
    required this.exitCode,
    required this.timestamp,
    this.command,
  });

  factory TerminalResponse.fromJson(Map<String, dynamic> json) {
    return TerminalResponse(
      output: json['output'] ?? '',
      error: json['error'],
      exitCode: json['exit_code'] ?? 0,
      timestamp: (json['timestamp'] ?? 0).toDouble(),
      command: json['command'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'output': output,
      'error': error,
      'exit_code': exitCode,
      'timestamp': timestamp,
      'command': command,
    };
  }
}

class AIRequest {
  final String prompt;
  final String? model;
  final Map<String, dynamic>? parameters;

  const AIRequest({
    required this.prompt,
    this.model,
    this.parameters,
  });

  factory AIRequest.fromJson(Map<String, dynamic> json) {
    return AIRequest(
      prompt: json['prompt'] ?? '',
      model: json['model'],
      parameters: json['parameters'] != null 
          ? Map<String, dynamic>.from(json['parameters'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'prompt': prompt,
      'model': model,
      'parameters': parameters,
    };
  }
}

class AIResponse {
  final String response;
  final String? model;
  final Map<String, dynamic>? metadata;
  final double timestamp;

  const AIResponse({
    required this.response,
    this.model,
    this.metadata,
    required this.timestamp,
  });

  factory AIResponse.fromJson(Map<String, dynamic> json) {
    return AIResponse(
      response: json['response'] ?? '',
      model: json['model'],
      metadata: json['metadata'] != null 
          ? Map<String, dynamic>.from(json['metadata'])
          : null,
      timestamp: (json['timestamp'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'response': response,
      'model': model,
      'metadata': metadata,
      'timestamp': timestamp,
    };
  }
}

class SystemInfo {
  final String platform;
  final String version;
  final String architecture;
  final Map<String, dynamic> hardware;
  final Map<String, dynamic> software;
  final double timestamp;

  const SystemInfo({
    required this.platform,
    required this.version,
    required this.architecture,
    required this.hardware,
    required this.software,
    required this.timestamp,
  });

  factory SystemInfo.fromJson(Map<String, dynamic> json) {
    return SystemInfo(
      platform: json['platform'] ?? '',
      version: json['version'] ?? '',
      architecture: json['architecture'] ?? '',
      hardware: Map<String, dynamic>.from(json['hardware'] ?? {}),
      software: Map<String, dynamic>.from(json['software'] ?? {}),
      timestamp: (json['timestamp'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'platform': platform,
      'version': version,
      'architecture': architecture,
      'hardware': hardware,
      'software': software,
      'timestamp': timestamp,
    };
  }
}

class FileInfo {
  final String name;
  final String path;
  final int size;
  final String type;
  final double modified;

  const FileInfo({
    required this.name,
    required this.path,
    required this.size,
    required this.type,
    required this.modified,
  });

  factory FileInfo.fromJson(Map<String, dynamic> json) {
    return FileInfo(
      name: json['name'] ?? '',
      path: json['path'] ?? '',
      size: json['size'] ?? 0,
      type: json['type'] ?? '',
      modified: (json['modified'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'path': path,
      'size': size,
      'type': type,
      'modified': modified,
    };
  }
}
