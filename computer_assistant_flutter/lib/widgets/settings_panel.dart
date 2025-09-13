import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
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
  bool _autoConnect = true;
  String _language = 'tr-TR';
  double _sensitivity = 0.5;
  String _theme = 'light';
  double _fontSize = 16.0;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  @override
  void dispose() {
    _serverUrlController.dispose();
    super.dispose();
  }

  void _loadSettings() {
    // Varsayılan ayarları yükle
    _serverUrlController.text = "ws://100.109.80.8:8765";
  }

  void _saveSettings() {
    // Ayarları kaydet
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Ayarlar kaydedildi'),
        backgroundColor: Colors.green,
      ),
    );
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
                      SwitchListTile(
                        title: const Text('RAG Sistemi'),
                        subtitle: const Text('Kullanıcı tercihleri ile öğrenme'),
                        value: true,
                        onChanged: (value) {
                          // RAG ayarı
                        },
                      ),
                      SwitchListTile(
                        title: const Text('Akıllı Öneriler'),
                        subtitle: const Text('AI tabanlı komut önerileri'),
                        value: true,
                        onChanged: (value) {
                          // Akıllı öneriler ayarı
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
