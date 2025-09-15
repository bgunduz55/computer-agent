import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../providers/app_provider.dart';

class SettingsPanel extends ConsumerStatefulWidget {
  final VoidCallback onClose;

  const SettingsPanel({
    Key? key,
    required this.onClose,
  }) : super(key: key);

  @override
  ConsumerState<SettingsPanel> createState() => _SettingsPanelState();
}

class _SettingsPanelState extends ConsumerState<SettingsPanel> {
  final TextEditingController _serverUrlController = TextEditingController();
  final TextEditingController _openaiKeyController = TextEditingController();
  final TextEditingController _geminiKeyController = TextEditingController();
  final TextEditingController _openrouterKeyController = TextEditingController();
  
  bool _autoConnect = true;
  String _language = 'tr-TR';
  double _sensitivity = 0.5;
  String _theme = 'light';
  double _fontSize = 16.0;
  
  // AI Settings
  String _aiProvider = 'ollama';
  String _aiModel = 'deepseek-r1:8b';
  double _temperature = 0.7;
  int _maxTokens = 1000;
  bool _ragEnabled = true;
  
  // Provider Settings
  bool _openaiEnabled = false;
  bool _geminiEnabled = false;
  bool _openrouterEnabled = false;
  bool _ollamaEnabled = true;
  
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  @override
  void dispose() {
    _serverUrlController.dispose();
    _openaiKeyController.dispose();
    _geminiKeyController.dispose();
    _openrouterKeyController.dispose();
    super.dispose();
  }

  void _loadSettings() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      // Load settings from backend
      final response = await http.get(
        Uri.parse('http://100.109.80.8:8766/api/settings/'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['success']) {
          final settings = data['data'];
          
          // Load AI settings
          final aiSettings = settings['ai'];
          setState(() {
            _aiProvider = aiSettings['default_provider'] ?? 'ollama';
            _aiModel = aiSettings['default_model'] ?? 'deepseek-r1:8b';
            _temperature = (aiSettings['temperature'] ?? 0.7).toDouble();
            _maxTokens = aiSettings['max_tokens'] ?? 1000;
            _ragEnabled = aiSettings['rag_enabled'] ?? true;
            
            _openaiEnabled = aiSettings['openai_enabled'] ?? false;
            _geminiEnabled = aiSettings['gemini_enabled'] ?? false;
            _openrouterEnabled = aiSettings['openrouter_enabled'] ?? false;
            _ollamaEnabled = aiSettings['ollama_enabled'] ?? true;
            
            _openaiKeyController.text = aiSettings['openai_api_key'] ?? '';
            _geminiKeyController.text = aiSettings['gemini_api_key'] ?? '';
            _openrouterKeyController.text = aiSettings['openrouter_api_key'] ?? '';
          });
        }
      }
    } catch (e) {
      print('Error loading settings: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
    
    // Default values
    _serverUrlController.text = "ws://100.109.80.8:8765";
  }

  void _saveSettings() async {
    setState(() {
      _isLoading = true;
    });
    
    try {
      // Save AI settings
      final aiSettings = {
        'default_provider': _aiProvider,
        'default_model': _aiModel,
        'temperature': _temperature,
        'max_tokens': _maxTokens,
        'rag_enabled': _ragEnabled,
        'openai_enabled': _openaiEnabled,
        'gemini_enabled': _geminiEnabled,
        'openrouter_enabled': _openrouterEnabled,
        'ollama_enabled': _ollamaEnabled,
        'openai_api_key': _openaiKeyController.text,
        'gemini_api_key': _geminiKeyController.text,
        'openrouter_api_key': _openrouterKeyController.text,
      };
      
      final response = await http.put(
        Uri.parse('http://100.109.80.8:8765/api/settings/ai'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(aiSettings),
      );
      
      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Ayarlar başarıyla kaydedildi'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        throw Exception('Failed to save settings');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ayarlar kaydedilemedi: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _testConnection() async {
    final serverUrl = _serverUrlController.text;
    if (serverUrl.isEmpty) return;

    try {
      await ref.read(appStateProvider.notifier).connect(serverUrl);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Bağlantı başarılı'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Bağlantı hatası: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      height: 600,
      child: Column(
        children: [
          // Başlık
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.settings,
                  color: Colors.blue.shade600,
                  size: 24,
                ),
                const SizedBox(width: 12),
                const Text(
                  'Ayarlar',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                IconButton(
                  onPressed: widget.onClose,
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
          ),
          
          // Ayarlar içeriği
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // WebSocket Bağlantısı
                  _buildSection(
                    title: 'WebSocket Bağlantısı',
                    icon: Icons.wifi,
                    children: [
                      TextField(
                        controller: _serverUrlController,
                        decoration: const InputDecoration(
                          labelText: 'Sunucu URL',
                          hintText: 'ws://100.109.80.8:8765',
                          border: OutlineInputBorder(),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _testConnection,
                              icon: const Icon(Icons.wifi_find),
                              label: const Text('Bağlantıyı Test Et'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Switch(
                            value: _autoConnect,
                            onChanged: (value) {
                              setState(() {
                                _autoConnect = value;
                              });
                            },
                          ),
                          const SizedBox(width: 8),
                          const Text('Otomatik Bağlan'),
                        ],
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Ses Ayarları
                  _buildSection(
                    title: 'Ses Ayarları',
                    icon: Icons.mic,
                    children: [
                      DropdownButtonFormField<String>(
                        value: _language,
                        decoration: const InputDecoration(
                          labelText: 'Dil',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(value: 'tr-TR', child: Text('Türkçe')),
                          DropdownMenuItem(value: 'en-US', child: Text('English')),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _language = value ?? 'tr-TR';
                          });
                        },
                      ),
                      const SizedBox(height: 16),
                      Text('Hassasiyet: ${(_sensitivity * 100).round()}%'),
                      Slider(
                        value: _sensitivity,
                        onChanged: (value) {
                          setState(() {
                            _sensitivity = value;
                          });
                        },
                        divisions: 10,
                        min: 0.0,
                        max: 1.0,
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Görsel Ayarlar
                  _buildSection(
                    title: 'Görsel Ayarlar',
                    icon: Icons.palette,
                    children: [
                      DropdownButtonFormField<String>(
                        value: _theme,
                        decoration: const InputDecoration(
                          labelText: 'Tema',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(value: 'light', child: Text('Açık')),
                          DropdownMenuItem(value: 'dark', child: Text('Koyu')),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _theme = value ?? 'light';
                          });
                        },
                      ),
                      const SizedBox(height: 16),
                      Text('Yazı Boyutu: ${_fontSize.round()}'),
                      Slider(
                        value: _fontSize,
                        onChanged: (value) {
                          setState(() {
                            _fontSize = value;
                          });
                        },
                        divisions: 8,
                        min: 12.0,
                        max: 20.0,
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // AI Ayarları
                  _buildSection(
                    title: 'AI Ayarları',
                    icon: Icons.psychology,
                    children: [
                      // AI Provider Selection
                      DropdownButtonFormField<String>(
                        value: _aiProvider,
                        decoration: const InputDecoration(
                          labelText: 'AI Provider',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(value: 'ollama', child: Text('Ollama (Local)')),
                          DropdownMenuItem(value: 'openai', child: Text('OpenAI')),
                          DropdownMenuItem(value: 'gemini', child: Text('Google Gemini')),
                          DropdownMenuItem(value: 'openrouter', child: Text('OpenRouter')),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _aiProvider = value ?? 'ollama';
                          });
                        },
                      ),
                      const SizedBox(height: 16),
                      
                      // Model Selection
                      TextField(
                        controller: TextEditingController(text: _aiModel),
                        decoration: const InputDecoration(
                          labelText: 'Model',
                          hintText: 'deepseek-r1:8b',
                          border: OutlineInputBorder(),
                        ),
                        onChanged: (value) {
                          _aiModel = value;
                        },
                      ),
                      const SizedBox(height: 16),
                      
                      // Temperature
                      Text('Temperature: ${_temperature.toStringAsFixed(1)}'),
                      Slider(
                        value: _temperature,
                        onChanged: (value) {
                          setState(() {
                            _temperature = value;
                          });
                        },
                        divisions: 20,
                        min: 0.0,
                        max: 2.0,
                      ),
                      const SizedBox(height: 16),
                      
                      // Max Tokens
                      Text('Max Tokens: $_maxTokens'),
                      Slider(
                        value: _maxTokens.toDouble(),
                        onChanged: (value) {
                          setState(() {
                            _maxTokens = value.round();
                          });
                        },
                        divisions: 20,
                        min: 100.0,
                        max: 4000.0,
                      ),
                      const SizedBox(height: 16),
                      
                      // RAG System
                      SwitchListTile(
                        title: const Text('RAG Sistemi'),
                        subtitle: const Text('Kullanıcı tercihleri ile öğrenme'),
                        value: _ragEnabled,
                        onChanged: (value) {
                          setState(() {
                            _ragEnabled = value;
                          });
                        },
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // API Keys
                  _buildSection(
                    title: 'API Keys',
                    icon: Icons.key,
                    children: [
                      // OpenAI
                      SwitchListTile(
                        title: const Text('OpenAI'),
                        subtitle: const Text('GPT-4, GPT-3.5-turbo'),
                        value: _openaiEnabled,
                        onChanged: (value) {
                          setState(() {
                            _openaiEnabled = value;
                          });
                        },
                      ),
                      if (_openaiEnabled) ...[
                        TextField(
                          controller: _openaiKeyController,
                          decoration: const InputDecoration(
                            labelText: 'OpenAI API Key',
                            border: OutlineInputBorder(),
                          ),
                          obscureText: true,
                        ),
                        const SizedBox(height: 16),
                      ],
                      
                      // Gemini
                      SwitchListTile(
                        title: const Text('Google Gemini'),
                        subtitle: const Text('Gemini Pro'),
                        value: _geminiEnabled,
                        onChanged: (value) {
                          setState(() {
                            _geminiEnabled = value;
                          });
                        },
                      ),
                      if (_geminiEnabled) ...[
                        TextField(
                          controller: _geminiKeyController,
                          decoration: const InputDecoration(
                            labelText: 'Gemini API Key',
                            border: OutlineInputBorder(),
                          ),
                          obscureText: true,
                        ),
                        const SizedBox(height: 16),
                      ],
                      
                      // OpenRouter
                      SwitchListTile(
                        title: const Text('OpenRouter'),
                        subtitle: const Text('Multiple AI Models'),
                        value: _openrouterEnabled,
                        onChanged: (value) {
                          setState(() {
                            _openrouterEnabled = value;
                          });
                        },
                      ),
                      if (_openrouterEnabled) ...[
                        TextField(
                          controller: _openrouterKeyController,
                          decoration: const InputDecoration(
                            labelText: 'OpenRouter API Key',
                            border: OutlineInputBorder(),
                          ),
                          obscureText: true,
                        ),
                        const SizedBox(height: 16),
                      ],
                      
                      // Ollama
                      SwitchListTile(
                        title: const Text('Ollama (Local)'),
                        subtitle: const Text('Local AI models'),
                        value: _ollamaEnabled,
                        onChanged: (value) {
                          setState(() {
                            _ollamaEnabled = value;
                          });
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          // Alt butonlar
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.grey.shade50,
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(16),
                bottomRight: Radius.circular(16),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: widget.onClose,
                    child: const Text('İptal'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _saveSettings,
                    child: const Text('Kaydet'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: Colors.blue.shade600, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...children,
        ],
      ),
    );
  }
}
