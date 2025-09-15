/// Backend Integration Models for Flutter Client
/// 
/// Data models for new backend features integration:
/// - Progress Tracking (T010)
/// - Terminal Session Management (T014)
/// - Analytics and Logging (T015)
/// - Context-Aware Execution (T005)
/// - Error Recovery and Learning (T006)
/// - Advanced Web Automation (T002, T003)
/// - Mobile Monitoring (T012)

import 'dart:convert';

// ===== PROGRESS TRACKING MODELS =====

class ProgressUpdate {
  final String executionId;
  final double progress; // 0.0 to 1.0
  final String status;
  final String message;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  const ProgressUpdate({
    required this.executionId,
    required this.progress,
    required this.status,
    required this.message,
    required this.timestamp,
    this.metadata,
  });

  factory ProgressUpdate.fromJson(Map<String, dynamic> json) {
    return ProgressUpdate(
      executionId: json['execution_id'] as String,
      progress: (json['progress'] as num).toDouble(),
      status: json['status'] as String,
      message: json['message'] as String,
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'execution_id': executionId,
      'progress': progress,
      'status': status,
      'message': message,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
      if (metadata != null) 'metadata': metadata,
    };
  }
}

class FeedbackSubmission {
  final String executionId;
  final int rating; // 1-5
  final String? comment;
  final List<String>? tags;
  final Map<String, dynamic>? metadata;
  final DateTime timestamp;

  const FeedbackSubmission({
    required this.executionId,
    required this.rating,
    this.comment,
    this.tags,
    this.metadata,
    required this.timestamp,
  });

  factory FeedbackSubmission.fromJson(Map<String, dynamic> json) {
    return FeedbackSubmission(
      executionId: json['execution_id'] as String,
      rating: json['rating'] as int,
      comment: json['comment'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.cast<String>(),
      metadata: json['metadata'] as Map<String, dynamic>?,
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'execution_id': executionId,
      'rating': rating,
      if (comment != null) 'comment': comment,
      if (tags != null) 'tags': tags,
      if (metadata != null) 'metadata': metadata,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
    };
  }
}

// ===== TERMINAL SESSION MODELS =====

enum TerminalSessionType {
  interactive,
  batch,
  script,
  monitoring,
  debug,
}

enum TerminalSessionStatus {
  active,
  inactive,
  suspended,
  terminated,
  error,
}

class TerminalSession {
  final String sessionId;
  final String name;
  final TerminalSessionType sessionType;
  final String terminalType;
  final String? workingDirectory;
  final String? description;
  final List<String> tags;
  final TerminalSessionStatus status;
  final DateTime createdAt;
  final DateTime? lastActivity;
  final Map<String, dynamic> context;
  final Map<String, dynamic> metadata;

  const TerminalSession({
    required this.sessionId,
    required this.name,
    required this.sessionType,
    required this.terminalType,
    this.workingDirectory,
    this.description,
    required this.tags,
    required this.status,
    required this.createdAt,
    this.lastActivity,
    required this.context,
    required this.metadata,
  });

  factory TerminalSession.fromJson(Map<String, dynamic> json) {
    return TerminalSession(
      sessionId: json['session_id'] as String,
      name: json['name'] as String,
      sessionType: TerminalSessionType.values.firstWhere(
        (e) => e.name == json['session_type'],
        orElse: () => TerminalSessionType.interactive,
      ),
      terminalType: json['terminal_type'] as String,
      workingDirectory: json['working_directory'] as String?,
      description: json['description'] as String?,
      tags: (json['tags'] as List<dynamic>).cast<String>(),
      status: TerminalSessionStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => TerminalSessionStatus.inactive,
      ),
      createdAt: DateTime.fromMillisecondsSinceEpoch(
        (json['created_at'] as num).toInt() * 1000,
      ),
      lastActivity: json['last_activity'] != null
          ? DateTime.fromMillisecondsSinceEpoch(
              (json['last_activity'] as num).toInt() * 1000,
            )
          : null,
      context: Map<String, dynamic>.from(json['context'] ?? {}),
      metadata: Map<String, dynamic>.from(json['metadata'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'name': name,
      'session_type': sessionType.name,
      'terminal_type': terminalType,
      if (workingDirectory != null) 'working_directory': workingDirectory,
      if (description != null) 'description': description,
      'tags': tags,
      'status': status.name,
      'created_at': createdAt.millisecondsSinceEpoch / 1000.0,
      if (lastActivity != null)
        'last_activity': lastActivity!.millisecondsSinceEpoch / 1000.0,
      'context': context,
      'metadata': metadata,
    };
  }
}

class TerminalCommand {
  final String commandId;
  final String sessionId;
  final String command;
  final DateTime timestamp;
  final String? output;
  final String? error;
  final int? exitCode;
  final int? duration;

  const TerminalCommand({
    required this.commandId,
    required this.sessionId,
    required this.command,
    required this.timestamp,
    this.output,
    this.error,
    this.exitCode,
    this.duration,
  });

  factory TerminalCommand.fromJson(Map<String, dynamic> json) {
    return TerminalCommand(
      commandId: json['command_id'] as String,
      sessionId: json['session_id'] as String,
      command: json['command'] as String,
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
      output: json['output'] as String?,
      error: json['error'] as String?,
      exitCode: json['exit_code'] as int?,
      duration: json['duration'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'command_id': commandId,
      'session_id': sessionId,
      'command': command,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
      if (output != null) 'output': output,
      if (error != null) 'error': error,
      if (exitCode != null) 'exit_code': exitCode,
      if (duration != null) 'duration': duration,
    };
  }
}

// ===== ANALYTICS MODELS =====

class AnalyticsMetrics {
  final String metricType;
  final String name;
  final dynamic value;
  final String? unit;
  final Map<String, String>? labels;
  final Map<String, dynamic>? metadata;
  final DateTime timestamp;

  const AnalyticsMetrics({
    required this.metricType,
    required this.name,
    required this.value,
    this.unit,
    this.labels,
    this.metadata,
    required this.timestamp,
  });

  factory AnalyticsMetrics.fromJson(Map<String, dynamic> json) {
    return AnalyticsMetrics(
      metricType: json['metric_type'] as String,
      name: json['name'] as String,
      value: json['value'],
      unit: json['unit'] as String?,
      labels: json['labels'] != null
          ? Map<String, String>.from(json['labels'])
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'metric_type': metricType,
      'name': name,
      'value': value,
      if (unit != null) 'unit': unit,
      if (labels != null) 'labels': labels,
      if (metadata != null) 'metadata': metadata,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
    };
  }
}

class LogEvent {
  final String eventId;
  final String level;
  final String eventType;
  final String message;
  final String? sessionId;
  final String? component;
  final Map<String, dynamic>? metadata;
  final List<String>? tags;
  final DateTime timestamp;

  const LogEvent({
    required this.eventId,
    required this.level,
    required this.eventType,
    required this.message,
    this.sessionId,
    this.component,
    this.metadata,
    this.tags,
    required this.timestamp,
  });

  factory LogEvent.fromJson(Map<String, dynamic> json) {
    return LogEvent(
      eventId: json['event_id'] as String,
      level: json['level'] as String,
      eventType: json['event_type'] as String,
      message: json['message'] as String,
      sessionId: json['session_id'] as String?,
      component: json['component'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      tags: (json['tags'] as List<dynamic>?)?.cast<String>(),
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'event_id': eventId,
      'level': level,
      'event_type': eventType,
      'message': message,
      if (sessionId != null) 'session_id': sessionId,
      if (component != null) 'component': component,
      if (metadata != null) 'metadata': metadata,
      if (tags != null) 'tags': tags,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
    };
  }
}

// ===== CONTEXT-AWARE EXECUTION MODELS =====

enum ContextType {
  userPreference,
  systemState,
  executionHistory,
  environment,
  temporary,
}

enum ContextPriority {
  low,
  medium,
  high,
  critical,
}

class MemoryEntry {
  final String entryId;
  final String sessionId;
  final String key;
  final dynamic value;
  final ContextType contextType;
  final ContextPriority priority;
  final DateTime timestamp;
  final List<String> tags;
  final DateTime? expiresAt;

  const MemoryEntry({
    required this.entryId,
    required this.sessionId,
    required this.key,
    required this.value,
    required this.contextType,
    required this.priority,
    required this.timestamp,
    required this.tags,
    this.expiresAt,
  });

  factory MemoryEntry.fromJson(Map<String, dynamic> json) {
    return MemoryEntry(
      entryId: json['entry_id'] as String,
      sessionId: json['session_id'] as String,
      key: json['key'] as String,
      value: json['value'],
      contextType: ContextType.values.firstWhere(
        (e) => e.name == json['context_type'],
        orElse: () => ContextType.temporary,
      ),
      priority: ContextPriority.values.firstWhere(
        (e) => e.name == json['priority'],
        orElse: () => ContextPriority.medium,
      ),
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
      tags: (json['tags'] as List<dynamic>).cast<String>(),
      expiresAt: json['expires_at'] != null
          ? DateTime.fromMillisecondsSinceEpoch(
              (json['expires_at'] as num).toInt() * 1000,
            )
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'entry_id': entryId,
      'session_id': sessionId,
      'key': key,
      'value': value,
      'context_type': contextType.name,
      'priority': priority.name,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
      'tags': tags,
      if (expiresAt != null)
        'expires_at': expiresAt!.millisecondsSinceEpoch / 1000.0,
    };
  }
}

class ExecutionContext {
  final String sessionId;
  final String? userId;
  final DateTime startedAt;
  final DateTime lastActivity;
  final List<String> commandSequence;
  final int? currentStep;
  final int? totalSteps;
  final String status;
  final Map<String, dynamic> variables;
  final Map<String, dynamic> metadata;

  const ExecutionContext({
    required this.sessionId,
    this.userId,
    required this.startedAt,
    required this.lastActivity,
    required this.commandSequence,
    this.currentStep,
    this.totalSteps,
    required this.status,
    required this.variables,
    required this.metadata,
  });

  factory ExecutionContext.fromJson(Map<String, dynamic> json) {
    return ExecutionContext(
      sessionId: json['session_id'] as String,
      userId: json['user_id'] as String?,
      startedAt: DateTime.fromMillisecondsSinceEpoch(
        (json['started_at'] as num).toInt() * 1000,
      ),
      lastActivity: DateTime.fromMillisecondsSinceEpoch(
        (json['last_activity'] as num).toInt() * 1000,
      ),
      commandSequence: (json['command_sequence'] as List<dynamic>).cast<String>(),
      currentStep: json['current_step'] as int?,
      totalSteps: json['total_steps'] as int?,
      status: json['status'] as String,
      variables: Map<String, dynamic>.from(json['variables'] ?? {}),
      metadata: Map<String, dynamic>.from(json['metadata'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      if (userId != null) 'user_id': userId,
      'started_at': startedAt.millisecondsSinceEpoch / 1000.0,
      'last_activity': lastActivity.millisecondsSinceEpoch / 1000.0,
      'command_sequence': commandSequence,
      if (currentStep != null) 'current_step': currentStep,
      if (totalSteps != null) 'total_steps': totalSteps,
      'status': status,
      'variables': variables,
      'metadata': metadata,
    };
  }
}

// ===== ERROR RECOVERY MODELS =====

enum ErrorSeverity {
  low,
  medium,
  high,
  critical,
}

enum ErrorCategory {
  aiProcessing,
  capabilityExecution,
  systemIntegration,
  userInput,
  network,
  unknown,
}

class ErrorLogEntry {
  final String errorId;
  final DateTime timestamp;
  final String errorType;
  final String message;
  final ErrorSeverity severity;
  final ErrorCategory category;
  final Map<String, dynamic> context;
  final bool isResolved;
  final String? resolutionNotes;
  final bool recoveryAttempted;
  final bool? recoverySuccess;
  final String? recoveryMessage;

  const ErrorLogEntry({
    required this.errorId,
    required this.timestamp,
    required this.errorType,
    required this.message,
    required this.severity,
    required this.category,
    required this.context,
    required this.isResolved,
    this.resolutionNotes,
    required this.recoveryAttempted,
    this.recoverySuccess,
    this.recoveryMessage,
  });

  factory ErrorLogEntry.fromJson(Map<String, dynamic> json) {
    return ErrorLogEntry(
      errorId: json['error_id'] as String,
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
      errorType: json['error_type'] as String,
      message: json['message'] as String,
      severity: ErrorSeverity.values.firstWhere(
        (e) => e.name == json['severity'],
        orElse: () => ErrorSeverity.medium,
      ),
      category: ErrorCategory.values.firstWhere(
        (e) => e.name == json['category'],
        orElse: () => ErrorCategory.unknown,
      ),
      context: Map<String, dynamic>.from(json['context'] ?? {}),
      isResolved: json['is_resolved'] as bool,
      resolutionNotes: json['resolution_notes'] as String?,
      recoveryAttempted: json['recovery_attempted'] as bool,
      recoverySuccess: json['recovery_success'] as bool?,
      recoveryMessage: json['recovery_message'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'error_id': errorId,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
      'error_type': errorType,
      'message': message,
      'severity': severity.name,
      'category': category.name,
      'context': context,
      'is_resolved': isResolved,
      if (resolutionNotes != null) 'resolution_notes': resolutionNotes,
      'recovery_attempted': recoveryAttempted,
      if (recoverySuccess != null) 'recovery_success': recoverySuccess,
      if (recoveryMessage != null) 'recovery_message': recoveryMessage,
    };
  }
}

// ===== WEB AUTOMATION MODELS =====

class WebAutomationAction {
  final String actionId;
  final String action;
  final Map<String, dynamic> parameters;
  final String status;
  final String? result;
  final String? screenshot;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  const WebAutomationAction({
    required this.actionId,
    required this.action,
    required this.parameters,
    required this.status,
    this.result,
    this.screenshot,
    required this.timestamp,
    this.metadata,
  });

  factory WebAutomationAction.fromJson(Map<String, dynamic> json) {
    return WebAutomationAction(
      actionId: json['action_id'] as String,
      action: json['action'] as String,
      parameters: Map<String, dynamic>.from(json['parameters'] ?? {}),
      status: json['status'] as String,
      result: json['result'] as String?,
      screenshot: json['screenshot'] as String?,
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'action_id': actionId,
      'action': action,
      'parameters': parameters,
      'status': status,
      if (result != null) 'result': result,
      if (screenshot != null) 'screenshot': screenshot,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
      if (metadata != null) 'metadata': metadata,
    };
  }
}

// ===== MOBILE MONITORING MODELS =====

class MobileStatus {
  final String deviceId;
  final String status;
  final String? command;
  final Map<String, dynamic>? systemInfo;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  const MobileStatus({
    required this.deviceId,
    required this.status,
    this.command,
    this.systemInfo,
    required this.timestamp,
    this.metadata,
  });

  factory MobileStatus.fromJson(Map<String, dynamic> json) {
    return MobileStatus(
      deviceId: json['device_id'] as String,
      status: json['status'] as String,
      command: json['command'] as String?,
      systemInfo: json['system_info'] as Map<String, dynamic>?,
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'device_id': deviceId,
      'status': status,
      if (command != null) 'command': command,
      if (systemInfo != null) 'system_info': systemInfo,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
      if (metadata != null) 'metadata': metadata,
    };
  }
}

class MobileNotification {
  final String notificationId;
  final String type;
  final String title;
  final String message;
  final Map<String, dynamic>? data;
  final DateTime timestamp;
  final bool isRead;

  const MobileNotification({
    required this.notificationId,
    required this.type,
    required this.title,
    required this.message,
    this.data,
    required this.timestamp,
    required this.isRead,
  });

  factory MobileNotification.fromJson(Map<String, dynamic> json) {
    return MobileNotification(
      notificationId: json['notification_id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      message: json['message'] as String,
      data: json['data'] as Map<String, dynamic>?,
      timestamp: DateTime.fromMillisecondsSinceEpoch(
        (json['timestamp'] as num).toInt() * 1000,
      ),
      isRead: json['is_read'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'notification_id': notificationId,
      'type': type,
      'title': title,
      'message': message,
      if (data != null) 'data': data,
      'timestamp': timestamp.millisecondsSinceEpoch / 1000.0,
      'is_read': isRead,
    };
  }
}
