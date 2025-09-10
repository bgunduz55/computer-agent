import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Settings Model
class ClientSettings {
  final String serverHost;
  final int serverPort;
  final bool useSSL;
  final int connectionTimeout;
  final int heartbeatInterval;
  final bool autoConnect;
  final bool saveCredentials;
  final String? savedAuthToken;
  
  // AI Provider Settings
  final String aiProvider;
  final String aiModel;
  final String? aiApiKey;
  final double aiTemperature;
  final int aiMaxTokens;
  final bool showApiKey;

  const ClientSettings({
    this.serverHost = '100.109.80.8',
    this.serverPort = 8765,
    this.useSSL = false,
    this.connectionTimeout = 30,
    this.heartbeatInterval = 30,
    this.autoConnect = true,
    this.saveCredentials = true,
    this.savedAuthToken,
    this.aiProvider = 'ollama',
    this.aiModel = 'llama3.1',
    this.aiApiKey,
    this.aiTemperature = 0.7,
    this.aiMaxTokens = 2000,
    this.showApiKey = false,
  });

  ClientSettings copyWith({
    String? serverHost,
    int? serverPort,
    bool? useSSL,
    int? connectionTimeout,
    int? heartbeatInterval,
    bool? autoConnect,
    bool? saveCredentials,
    String? savedAuthToken,
    String? aiProvider,
    String? aiModel,
    String? aiApiKey,
    double? aiTemperature,
    int? aiMaxTokens,
    bool? showApiKey,
  }) {
    return ClientSettings(
      serverHost: serverHost ?? this.serverHost,
      serverPort: serverPort ?? this.serverPort,
      useSSL: useSSL ?? this.useSSL,
      connectionTimeout: connectionTimeout ?? this.connectionTimeout,
      heartbeatInterval: heartbeatInterval ?? this.heartbeatInterval,
      autoConnect: autoConnect ?? this.autoConnect,
      saveCredentials: saveCredentials ?? this.saveCredentials,
      savedAuthToken: savedAuthToken ?? this.savedAuthToken,
      aiProvider: aiProvider ?? this.aiProvider,
      aiModel: aiModel ?? this.aiModel,
      aiApiKey: aiApiKey ?? this.aiApiKey,
      aiTemperature: aiTemperature ?? this.aiTemperature,
      aiMaxTokens: aiMaxTokens ?? this.aiMaxTokens,
      showApiKey: showApiKey ?? this.showApiKey,
    );
  }

  String get serverUrl {
    final protocol = useSSL ? 'wss' : 'ws';
    return '$protocol://$serverHost:$serverPort';
  }

  Map<String, dynamic> toJson() {
    return {
      'serverHost': serverHost,
      'serverPort': serverPort,
      'useSSL': useSSL,
      'connectionTimeout': connectionTimeout,
      'heartbeatInterval': heartbeatInterval,
      'autoConnect': autoConnect,
      'saveCredentials': saveCredentials,
      'savedAuthToken': savedAuthToken,
      'aiProvider': aiProvider,
      'aiModel': aiModel,
      'aiApiKey': aiApiKey,
      'aiTemperature': aiTemperature,
      'aiMaxTokens': aiMaxTokens,
      'showApiKey': showApiKey,
    };
  }

  factory ClientSettings.fromJson(Map<String, dynamic> json) {
    return ClientSettings(
      serverHost: json['serverHost'] as String? ?? '192.168.1.100',
      serverPort: json['serverPort'] as int? ?? 8765,
      useSSL: json['useSSL'] as bool? ?? false,
      connectionTimeout: json['connectionTimeout'] as int? ?? 30,
      heartbeatInterval: json['heartbeatInterval'] as int? ?? 30,
      autoConnect: json['autoConnect'] as bool? ?? false,
      saveCredentials: json['saveCredentials'] as bool? ?? true,
      savedAuthToken: json['savedAuthToken'] as String?,
      aiProvider: json['aiProvider'] as String? ?? 'ollama',
      aiModel: json['aiModel'] as String? ?? 'llama3.1',
      aiApiKey: json['aiApiKey'] as String?,
      aiTemperature: (json['aiTemperature'] as num?)?.toDouble() ?? 0.7,
      aiMaxTokens: json['aiMaxTokens'] as int? ?? 2000,
      showApiKey: json['showApiKey'] as bool? ?? false,
    );
  }
}

// Settings Notifier
class SettingsNotifier extends StateNotifier<ClientSettings> {
  static const String _settingsKey = 'client_settings';
  static const String _authTokenKey = 'saved_auth_token';

  SettingsNotifier() : super(const ClientSettings()) {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final settingsJson = prefs.getString(_settingsKey);
      final savedToken = prefs.getString(_authTokenKey);

      if (settingsJson != null) {
        final settingsMap = Map<String, dynamic>.from(
          Uri.splitQueryString(settingsJson)
        );
        state = ClientSettings.fromJson(settingsMap).copyWith(
          savedAuthToken: savedToken,
        );
      }
    } catch (e) {
      // Use default settings if loading fails
      state = const ClientSettings();
    }
  }

  Future<void> _saveSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      
      // Save settings as query string for simplicity
      final settingsJson = Uri(queryParameters: state.toJson().map(
        (key, value) => MapEntry(key, value.toString()),
      )).query;
      
      await prefs.setString(_settingsKey, settingsJson);
      
      // Save auth token separately if credentials should be saved
      if (state.saveCredentials && state.savedAuthToken != null) {
        await prefs.setString(_authTokenKey, state.savedAuthToken!);
      } else if (!state.saveCredentials) {
        await prefs.remove(_authTokenKey);
      }
    } catch (e) {
      // Handle save error silently or show user notification
    }
  }

  Future<void> updateServerHost(String host) async {
    state = state.copyWith(serverHost: host);
    await _saveSettings();
  }

  Future<void> updateServerPort(int port) async {
    state = state.copyWith(serverPort: port);
    await _saveSettings();
  }

  Future<void> updateUseSSL(bool useSSL) async {
    state = state.copyWith(useSSL: useSSL);
    await _saveSettings();
  }

  Future<void> updateConnectionTimeout(int timeout) async {
    state = state.copyWith(connectionTimeout: timeout);
    await _saveSettings();
  }

  Future<void> updateHeartbeatInterval(int interval) async {
    state = state.copyWith(heartbeatInterval: interval);
    await _saveSettings();
  }

  Future<void> updateAutoConnect(bool autoConnect) async {
    state = state.copyWith(autoConnect: autoConnect);
    await _saveSettings();
  }

  Future<void> updateSaveCredentials(bool saveCredentials) async {
    state = state.copyWith(saveCredentials: saveCredentials);
    await _saveSettings();
  }

  Future<void> updateAuthToken(String? token) async {
    state = state.copyWith(savedAuthToken: token);
    await _saveSettings();
  }

  // AI Provider methods
  Future<void> updateAIProvider(String provider) async {
    state = state.copyWith(aiProvider: provider);
    await _saveSettings();
  }

  Future<void> updateAIModel(String model) async {
    state = state.copyWith(aiModel: model);
    await _saveSettings();
  }

  Future<void> updateAIApiKey(String? apiKey) async {
    state = state.copyWith(aiApiKey: apiKey);
    await _saveSettings();
  }

  Future<void> updateAITemperature(double temperature) async {
    state = state.copyWith(aiTemperature: temperature);
    await _saveSettings();
  }

  Future<void> updateAIMaxTokens(int maxTokens) async {
    state = state.copyWith(aiMaxTokens: maxTokens);
    await _saveSettings();
  }

  void toggleApiKeyVisibility() {
    state = state.copyWith(showApiKey: !state.showApiKey);
  }

  Future<void> updateSettings({
    String? serverHost,
    int? serverPort,
    bool? useSSL,
    int? connectionTimeout,
    int? heartbeatInterval,
    bool? autoConnect,
    bool? saveCredentials,
    String? savedAuthToken,
  }) async {
    state = state.copyWith(
      serverHost: serverHost,
      serverPort: serverPort,
      useSSL: useSSL,
      connectionTimeout: connectionTimeout,
      heartbeatInterval: heartbeatInterval,
      autoConnect: autoConnect,
      saveCredentials: saveCredentials,
      savedAuthToken: savedAuthToken,
    );
    await _saveSettings();
  }

  // Validation methods
  List<String> validateSettings() {
    final errors = <String>[];

    // Validate host
    if (state.serverHost.isEmpty) {
      errors.add('Server host cannot be empty');
    } else if (!_isValidHost(state.serverHost)) {
      errors.add('Invalid server host format');
    }

    // Validate port
    if (state.serverPort < 1 || state.serverPort > 65535) {
      errors.add('Port must be between 1 and 65535');
    }

    // Validate timeouts
    if (state.connectionTimeout < 1) {
      errors.add('Connection timeout must be at least 1 second');
    }

    if (state.heartbeatInterval < 1) {
      errors.add('Heartbeat interval must be at least 1 second');
    }

    return errors;
  }

  bool _isValidHost(String host) {
    // Basic host validation
    if (host == 'localhost' || host == '127.0.0.1') {
      return true;
    }

    // IP address validation
    final parts = host.split('.');
    if (parts.length == 4) {
      for (final part in parts) {
        if (!part.isNotEmpty || int.tryParse(part) == null) {
          return false;
        }
        final num = int.parse(part);
        if (num < 0 || num > 255) {
          return false;
        }
      }
      return true;
    }

    // Domain name validation (basic)
    if (host.contains('.')) {
      return RegExp(r'^[a-zA-Z0-9.-]+$').hasMatch(host);
    }

    return false;
  }

  // Reset to defaults
  Future<void> resetToDefaults() async {
    state = const ClientSettings();
    await _saveSettings();
  }
}

// Settings Provider
final settingsProvider = StateNotifierProvider<SettingsNotifier, ClientSettings>((ref) {
  return SettingsNotifier();
});

// Convenience providers
final serverUrlProvider = Provider<String>((ref) {
  final settings = ref.watch(settingsProvider);
  return settings.serverUrl;
});

final serverHostProvider = Provider<String>((ref) {
  final settings = ref.watch(settingsProvider);
  return settings.serverHost;
});

final serverPortProvider = Provider<int>((ref) {
  final settings = ref.watch(settingsProvider);
  return settings.serverPort;
});

final useSSLProvider = Provider<bool>((ref) {
  final settings = ref.watch(settingsProvider);
  return settings.useSSL;
});
