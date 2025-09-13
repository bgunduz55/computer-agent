/// WebSocket Configuration for Flutter Client
/// 
/// Centralized configuration management for WebSocket connections
/// between Flutter client and Python server.

class WebSocketConfig {
  final String host;
  final int port;
  final bool useSSL;
  final int pingInterval;
  final int pingTimeout;
  final int reconnectAttempts;
  final int reconnectDelay;
  final int connectionTimeout;
  final bool authenticationEnabled;
  final int tokenExpiry;
  final bool loggingEnabled;
  final String logLevel;
  final bool logRequests;
  final bool logResponses;

  const WebSocketConfig({
    this.host = '100.109.80.8',
    this.port = 8766,
    this.useSSL = false,
    this.pingInterval = 60,
    this.pingTimeout = 10,
    this.reconnectAttempts = 5,
    this.reconnectDelay = 2000,
    this.connectionTimeout = 30,
    this.authenticationEnabled = false,
    this.tokenExpiry = 3600,
    this.loggingEnabled = true,
    this.logLevel = 'INFO',
    this.logRequests = true,
    this.logResponses = true,
  });

  String get url {
    final protocol = useSSL ? 'wss' : 'ws';
    return '$protocol://$host:$port';
  }

  factory WebSocketConfig.fromJson(Map<String, dynamic> json) {
    final websocket = json['websocket'] ?? {};
    final auth = json['authentication'] ?? {};
    final logging = json['logging'] ?? {};

    return WebSocketConfig(
      host: websocket['host'] ?? '100.109.80.8',
      port: websocket['port'] ?? 8765,
      useSSL: websocket['use_ssl'] ?? false,
      pingInterval: websocket['ping_interval'] ?? 30,
      pingTimeout: websocket['ping_timeout'] ?? 10,
      reconnectAttempts: websocket['reconnect_attempts'] ?? 5,
      reconnectDelay: websocket['reconnect_delay'] ?? 2000,
      connectionTimeout: websocket['connection_timeout'] ?? 30,
      authenticationEnabled: auth['enabled'] ?? false,
      tokenExpiry: auth['token_expiry'] ?? 3600,
      loggingEnabled: logging['enabled'] ?? true,
      logLevel: logging['log_level'] ?? 'INFO',
      logRequests: logging['log_requests'] ?? true,
      logResponses: logging['log_responses'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'websocket': {
        'host': host,
        'port': port,
        'use_ssl': useSSL,
        'ping_interval': pingInterval,
        'ping_timeout': pingTimeout,
        'reconnect_attempts': reconnectAttempts,
        'reconnect_delay': reconnectDelay,
        'connection_timeout': connectionTimeout,
      },
      'authentication': {
        'enabled': authenticationEnabled,
        'token_expiry': tokenExpiry,
      },
      'logging': {
        'enabled': loggingEnabled,
        'log_level': logLevel,
        'log_requests': logRequests,
        'log_responses': logResponses,
      },
    };
  }

  WebSocketConfig copyWith({
    String? host,
    int? port,
    bool? useSSL,
    int? pingInterval,
    int? pingTimeout,
    int? reconnectAttempts,
    int? reconnectDelay,
    int? connectionTimeout,
    bool? authenticationEnabled,
    int? tokenExpiry,
    bool? loggingEnabled,
    String? logLevel,
    bool? logRequests,
    bool? logResponses,
  }) {
    return WebSocketConfig(
      host: host ?? this.host,
      port: port ?? this.port,
      useSSL: useSSL ?? this.useSSL,
      pingInterval: pingInterval ?? this.pingInterval,
      pingTimeout: pingTimeout ?? this.pingTimeout,
      reconnectAttempts: reconnectAttempts ?? this.reconnectAttempts,
      reconnectDelay: reconnectDelay ?? this.reconnectDelay,
      connectionTimeout: connectionTimeout ?? this.connectionTimeout,
      authenticationEnabled: authenticationEnabled ?? this.authenticationEnabled,
      tokenExpiry: tokenExpiry ?? this.tokenExpiry,
      loggingEnabled: loggingEnabled ?? this.loggingEnabled,
      logLevel: logLevel ?? this.logLevel,
      logRequests: logRequests ?? this.logRequests,
      logResponses: logResponses ?? this.logResponses,
    );
  }
}

class WebSocketConfigManager {
  static WebSocketConfigManager? _instance;
  WebSocketConfig? _config;

  WebSocketConfigManager._();

  static WebSocketConfigManager get instance {
    _instance ??= WebSocketConfigManager._();
    return _instance!;
  }

  WebSocketConfig get config {
    _config ??= const WebSocketConfig();
    return _config!;
  }

  void updateConfig(WebSocketConfig config) {
    _config = config;
  }

  Future<void> loadConfig() async {
    // For now, use default config
    // In the future, this could load from a config file or API
    _config = const WebSocketConfig();
  }

  Future<void> saveConfig() async {
    // For now, do nothing
    // In the future, this could save to a config file or API
  }
}
