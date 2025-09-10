/// Response Models for Flutter Client
/// 
/// Data models for various response types from the server.

class TerminalResponse {
  final String command;
  final String output;
  final String? error;
  final int exitCode;
  final bool success;
  final double executionTime;

  const TerminalResponse({
    required this.command,
    required this.output,
    this.error,
    required this.exitCode,
    required this.success,
    required this.executionTime,
  });

  factory TerminalResponse.fromJson(Map<String, dynamic> json) {
    return TerminalResponse(
      command: json['command'] ?? '',
      output: json['output'] ?? '',
      error: json['error'],
      exitCode: json['exit_code'] ?? 0,
      success: json['success'] ?? false,
      executionTime: (json['execution_time'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'command': command,
      'output': output,
      'error': error,
      'exit_code': exitCode,
      'success': success,
      'execution_time': executionTime,
    };
  }
}

class AIResponse {
  final String prompt;
  final String response;
  final String? model;
  final int? tokensUsed;
  final double? cost;
  final bool success;

  const AIResponse({
    required this.prompt,
    required this.response,
    this.model,
    this.tokensUsed,
    this.cost,
    required this.success,
  });

  factory AIResponse.fromJson(Map<String, dynamic> json) {
    return AIResponse(
      prompt: json['prompt'] ?? '',
      response: json['response'] ?? '',
      model: json['model'],
      tokensUsed: json['tokens_used'],
      cost: json['cost']?.toDouble(),
      success: json['success'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'prompt': prompt,
      'response': response,
      'model': model,
      'tokens_used': tokensUsed,
      'cost': cost,
      'success': success,
    };
  }
}

class SystemInfo {
  final String os;
  final String version;
  final String architecture;
  final int totalMemory;
  final int freeMemory;
  final double cpuUsage;
  final double diskUsage;
  final String hostname;
  final String username;
  final String platform;
  final String platformVersion;
  final String processor;
  final String pythonVersion;
  final List<String> availableTerminals;
  final int activeSessions;
  final int commandHistorySize;

  const SystemInfo({
    required this.os,
    required this.version,
    required this.architecture,
    required this.totalMemory,
    required this.freeMemory,
    required this.cpuUsage,
    required this.diskUsage,
    required this.hostname,
    required this.username,
    this.platform = '',
    this.platformVersion = '',
    this.processor = '',
    this.pythonVersion = '',
    this.availableTerminals = const [],
    this.activeSessions = 0,
    this.commandHistorySize = 0,
  });

  factory SystemInfo.fromJson(Map<String, dynamic> json) {
    return SystemInfo(
      os: json['os'] ?? '',
      version: json['version'] ?? '',
      architecture: json['architecture'] ?? '',
      totalMemory: json['total_memory'] ?? 0,
      freeMemory: json['free_memory'] ?? 0,
      cpuUsage: (json['cpu_usage'] ?? 0.0).toDouble(),
      diskUsage: (json['disk_usage'] ?? 0.0).toDouble(),
      hostname: json['hostname'] ?? '',
      username: json['username'] ?? '',
      platform: json['platform'] ?? '',
      platformVersion: json['platform_version'] ?? '',
      processor: json['processor'] ?? '',
      pythonVersion: json['python_version'] ?? '',
      availableTerminals: List<String>.from(json['available_terminals'] ?? []),
      activeSessions: json['active_sessions'] ?? 0,
      commandHistorySize: json['command_history_size'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'os': os,
      'version': version,
      'architecture': architecture,
      'total_memory': totalMemory,
      'free_memory': freeMemory,
      'cpu_usage': cpuUsage,
      'disk_usage': diskUsage,
      'hostname': hostname,
      'username': username,
      'platform': platform,
      'platform_version': platformVersion,
      'processor': processor,
      'python_version': pythonVersion,
      'available_terminals': availableTerminals,
      'active_sessions': activeSessions,
      'command_history_size': commandHistorySize,
    };
  }
}

class FileInfo {
  final String name;
  final String path;
  final bool isDirectory;
  final int size;
  final DateTime? lastModified;
  final String? permissions;

  const FileInfo({
    required this.name,
    required this.path,
    required this.isDirectory,
    required this.size,
    this.lastModified,
    this.permissions,
  });

  factory FileInfo.fromJson(Map<String, dynamic> json) {
    return FileInfo(
      name: json['name'] ?? '',
      path: json['path'] ?? '',
      isDirectory: json['is_directory'] ?? false,
      size: json['size'] ?? 0,
      lastModified: json['last_modified'] != null 
          ? DateTime.fromMillisecondsSinceEpoch(json['last_modified'])
          : null,
      permissions: json['permissions'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'path': path,
      'is_directory': isDirectory,
      'size': size,
      'last_modified': lastModified?.millisecondsSinceEpoch,
      'permissions': permissions,
    };
  }
}
