import 'dart:async';
import 'package:logger/logger.dart';
import 'websocket_service.dart';
import '../shared/websocket_protocol.dart';

class CommandService {
  static final CommandService _instance = CommandService._internal();
  factory CommandService() => _instance;

  final Logger _logger = Logger();
  final WebSocketService _webSocketService = WebSocketService();
  
  // Command history
  final List<CommandHistory> _commandHistory = [];
  static const int _maxHistorySize = 100;

  CommandService._internal();

  // Getters
  List<CommandHistory> get commandHistory => List.unmodifiable(_commandHistory);
  bool get isConnected => _webSocketService.isConnected;

  /// Initialize command service
  Future<void> initialize() async {
    _logger.i('Initializing Command Service');
    
    // Listen to WebSocket messages for command responses
    _webSocketService.messageStream.listen(_handleMessage);
    
    _logger.i('Command Service initialized');
  }

  /// Send voice command
  Future<void> sendVoiceCommand(String command, {String? language, double? confidence}) async {
    try {
      _logger.i('Sending voice command: $command');
      
      // Add to history
      _addToHistory(CommandHistory(
        command: command,
        type: CommandType.voice,
        timestamp: DateTime.now(),
        status: CommandStatus.sending,
      ));
      
      // Send via WebSocket
      await _webSocketService.sendVoiceCommand(command, language: language, confidence: confidence);
      
    } catch (e) {
      _logger.e('Error sending voice command: $e');
      _updateLastCommandStatus(CommandStatus.failed, error: e.toString());
    }
  }

  /// Send typing command
  Future<void> sendTypingCommand(String text, {double? delay}) async {
    try {
      _logger.i('Sending typing command: $text');
      
      // Add to history
      _addToHistory(CommandHistory(
        command: 'yaz $text',
        type: CommandType.typing,
        timestamp: DateTime.now(),
        status: CommandStatus.sending,
        parameters: {'text': text, 'delay': delay},
      ));
      
      // Send as voice command with typing prefix
      await _webSocketService.sendVoiceCommand('yaz $text');
      
    } catch (e) {
      _logger.e('Error sending typing command: $e');
      _updateLastCommandStatus(CommandStatus.failed, error: e.toString());
    }
  }

  /// Send application control command
  Future<void> sendApplicationCommand(String action, String appName) async {
    try {
      _logger.i('Sending application command: $action $appName');
      
      String command;
      switch (action.toLowerCase()) {
        case 'open':
        case 'aç':
          command = 'aç $appName';
          break;
        case 'close':
        case 'kapat':
          command = 'kapat $appName';
          break;
        case 'switch':
        case 'değiştir':
          command = 'değiştir $appName';
          break;
        default:
          command = '$action $appName';
      }
      
      // Add to history
      _addToHistory(CommandHistory(
        command: command,
        type: CommandType.application,
        timestamp: DateTime.now(),
        status: CommandStatus.sending,
        parameters: {'action': action, 'app_name': appName},
      ));
      
      // Send via WebSocket
      await _webSocketService.sendVoiceCommand(command);
      
    } catch (e) {
      _logger.e('Error sending application command: $e');
      _updateLastCommandStatus(CommandStatus.failed, error: e.toString());
    }
  }

  /// Send browser command
  Future<void> sendBrowserCommand(String action, {String? url, String? query, String? engine}) async {
    try {
      _logger.i('Sending browser command: $action');
      
      String command;
      switch (action.toLowerCase()) {
        case 'open':
        case 'aç':
          command = url != null ? 'aç $url' : 'yeni sekme';
          break;
        case 'search':
        case 'ara':
          command = 'ara $query';
          if (engine != null) {
            command = '$engine $command';
          }
          break;
        case 'new_tab':
        case 'yeni_sekme':
          command = 'yeni sekme';
          break;
        case 'close_tab':
        case 'kapat_sekme':
          command = 'sekme kapat';
          break;
        default:
          command = action;
      }
      
      // Add to history
      _addToHistory(CommandHistory(
        command: command,
        type: CommandType.browser,
        timestamp: DateTime.now(),
        status: CommandStatus.sending,
        parameters: {'action': action, 'url': url, 'query': query, 'engine': engine},
      ));
      
      // Send via WebSocket
      await _webSocketService.sendVoiceCommand(command);
      
    } catch (e) {
      _logger.e('Error sending browser command: $e');
      _updateLastCommandStatus(CommandStatus.failed, error: e.toString());
    }
  }

  /// Send system command
  Future<void> sendSystemCommand(String action, {Map<String, dynamic>? parameters}) async {
    try {
      _logger.i('Sending system command: $action');
      
      String command;
      switch (action.toLowerCase()) {
        case 'shutdown':
        case 'kapat':
          command = 'sistem kapat';
          break;
        case 'restart':
        case 'yeniden_başlat':
          command = 'sistem yeniden başlat';
          break;
        case 'sleep':
        case 'uyku':
          command = 'sistem uyku';
          break;
        case 'lock':
        case 'kilit':
          command = 'sistem kilit';
          break;
        case 'volume':
        case 'ses':
          final level = parameters?['level'] ?? 50;
          command = 'ses $level';
          break;
        case 'brightness':
        case 'parlaklık':
          final level = parameters?['level'] ?? 50;
          command = 'parlaklık $level';
          break;
        default:
          command = action;
      }
      
      // Add to history
      _addToHistory(CommandHistory(
        command: command,
        type: CommandType.system,
        timestamp: DateTime.now(),
        status: CommandStatus.sending,
        parameters: parameters,
      ));
      
      // Send via WebSocket
      await _webSocketService.sendVoiceCommand(command);
      
    } catch (e) {
      _logger.e('Error sending system command: $e');
      _updateLastCommandStatus(CommandStatus.failed, error: e.toString());
    }
  }

  /// Send media command
  Future<void> sendMediaCommand(String action, {String? songName, String? artist, int? volume}) async {
    try {
      _logger.i('Sending media command: $action');
      
      String command;
      switch (action.toLowerCase()) {
        case 'play':
        case 'çal':
          command = songName != null ? 'çal $songName' : 'çal';
          if (artist != null) {
            command = '$artist $command';
          }
          break;
        case 'pause':
        case 'dur':
          command = 'dur';
          break;
        case 'next':
        case 'sonraki':
          command = 'sonraki';
          break;
        case 'previous':
        case 'önceki':
          command = 'önceki';
          break;
        case 'volume':
        case 'ses':
          command = 'ses ${volume ?? 50}';
          break;
        default:
          command = action;
      }
      
      // Add to history
      _addToHistory(CommandHistory(
        command: command,
        type: CommandType.media,
        timestamp: DateTime.now(),
        status: CommandStatus.sending,
        parameters: {'action': action, 'song_name': songName, 'artist': artist, 'volume': volume},
      ));
      
      // Send via WebSocket
      await _webSocketService.sendVoiceCommand(command);
      
    } catch (e) {
      _logger.e('Error sending media command: $e');
      _updateLastCommandStatus(CommandStatus.failed, error: e.toString());
    }
  }

  /// Send file command
  Future<void> sendFileCommand(String action, {String? filePath, String? content, String? destination}) async {
    try {
      _logger.i('Sending file command: $action');
      
      String command;
      switch (action.toLowerCase()) {
        case 'open':
        case 'aç':
          command = 'aç $filePath';
          break;
        case 'save':
        case 'kaydet':
          command = 'kaydet $filePath';
          break;
        case 'delete':
        case 'sil':
          command = 'sil $filePath';
          break;
        case 'copy':
        case 'kopyala':
          command = 'kopyala $filePath';
          break;
        case 'move':
        case 'taşı':
          command = 'taşı $filePath $destination';
          break;
        case 'list':
        case 'listele':
          command = 'listele $filePath';
          break;
        default:
          command = action;
      }
      
      // Add to history
      _addToHistory(CommandHistory(
        command: command,
        type: CommandType.file,
        timestamp: DateTime.now(),
        status: CommandStatus.sending,
        parameters: {'action': action, 'file_path': filePath, 'content': content, 'destination': destination},
      ));
      
      // Send via WebSocket
      await _webSocketService.sendVoiceCommand(command);
      
    } catch (e) {
      _logger.e('Error sending file command: $e');
      _updateLastCommandStatus(CommandStatus.failed, error: e.toString());
    }
  }

  /// Send custom command
  Future<void> sendCustomCommand(String command, {CommandType? type, Map<String, dynamic>? parameters}) async {
    try {
      _logger.i('Sending custom command: $command');
      
      // Add to history
      _addToHistory(CommandHistory(
        command: command,
        type: type ?? CommandType.custom,
        timestamp: DateTime.now(),
        status: CommandStatus.sending,
        parameters: parameters,
      ));
      
      // Send via WebSocket
      await _webSocketService.sendVoiceCommand(command);
      
    } catch (e) {
      _logger.e('Error sending custom command: $e');
      _updateLastCommandStatus(CommandStatus.failed, error: e.toString());
    }
  }

  /// Handle incoming messages
  void _handleMessage(WebSocketMessage message) {
    switch (message.type) {
      case MessageType.voiceResponse:
        _handleVoiceResponse(message);
        break;
      case MessageType.error:
        _handleError(message);
        break;
      case MessageType.notification:
        _handleNotification(message);
        break;
      default:
        // Handle other message types if needed
        break;
    }
  }

  /// Handle voice response
  void _handleVoiceResponse(WebSocketMessage message) {
    final success = message.data['success'] as bool? ?? false;
    final responseMessage = message.data['message'] as String? ?? '';
    final executionTime = message.data['execution_time'] as double? ?? 0.0;
    
    _logger.i('Voice response: $responseMessage (success: $success, time: ${executionTime}s)');
    
    // Update last command status
    _updateLastCommandStatus(
      success ? CommandStatus.completed : CommandStatus.failed,
      response: responseMessage,
      executionTime: executionTime,
    );
  }

  /// Handle error response
  void _handleError(WebSocketMessage message) {
    final error = message.data['error'] as String? ?? 'Unknown error';
    _logger.e('Command error: $error');
    
    // Update last command status
    _updateLastCommandStatus(CommandStatus.failed, error: error);
  }

  /// Handle notification
  void _handleNotification(WebSocketMessage message) {
    final notification = message.data['message'] as String? ?? '';
    final type = message.data['type'] as String? ?? 'info';
    
    _logger.i('Notification ($type): $notification');
    
    // Update last command status if it's related to a command
    if (type == 'command_completed' || type == 'command_failed') {
      _updateLastCommandStatus(
        type == 'command_completed' ? CommandStatus.completed : CommandStatus.failed,
        response: notification,
      );
    }
  }

  /// Add command to history
  void _addToHistory(CommandHistory command) {
    _commandHistory.add(command);
    if (_commandHistory.length > _maxHistorySize) {
      _commandHistory.removeAt(0);
    }
  }

  /// Update last command status
  void _updateLastCommandStatus(CommandStatus status, {String? response, String? error, double? executionTime}) {
    if (_commandHistory.isNotEmpty) {
      final lastCommand = _commandHistory.last;
      _commandHistory[_commandHistory.length - 1] = CommandHistory(
        command: lastCommand.command,
        type: lastCommand.type,
        timestamp: lastCommand.timestamp,
        status: status,
        parameters: lastCommand.parameters,
        response: response,
        error: error,
        executionTime: executionTime,
      );
    }
  }

  /// Clear command history
  void clearHistory() {
    _commandHistory.clear();
    _logger.i('Command history cleared');
  }

  /// Get command statistics
  Map<String, dynamic> getStatistics() {
    final total = _commandHistory.length;
    final completed = _commandHistory.where((c) => c.status == CommandStatus.completed).length;
    final failed = _commandHistory.where((c) => c.status == CommandStatus.failed).length;
    final pending = _commandHistory.where((c) => c.status == CommandStatus.sending).length;
    
    return {
      'total': total,
      'completed': completed,
      'failed': failed,
      'pending': pending,
      'success_rate': total > 0 ? (completed / total) : 0.0,
    };
  }

  /// Dispose resources
  void dispose() {
    _logger.i('Command Service disposed');
  }
}

/// Command history model
class CommandHistory {
  final String command;
  final CommandType type;
  final DateTime timestamp;
  final CommandStatus status;
  final Map<String, dynamic>? parameters;
  final String? response;
  final String? error;
  final double? executionTime;

  CommandHistory({
    required this.command,
    required this.type,
    required this.timestamp,
    required this.status,
    this.parameters,
    this.response,
    this.error,
    this.executionTime,
  });
}

/// Command types
enum CommandType {
  voice,
  typing,
  application,
  browser,
  system,
  media,
  file,
  custom,
}

/// Command status
enum CommandStatus {
  sending,
  completed,
  failed,
}
