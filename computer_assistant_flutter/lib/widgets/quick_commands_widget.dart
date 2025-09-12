import 'package:flutter/material.dart';
import '../services/command_service.dart';

class QuickCommandsWidget extends StatelessWidget {
  const QuickCommandsWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quick Commands',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            // Typing commands
            _buildCommandSection(
              'Typing',
              Icons.keyboard,
              [
                _buildQuickCommand('yaz Merhaba', () => _sendTypingCommand('Merhaba')),
                _buildQuickCommand('enter', () => _sendTypingCommand('enter')),
                _buildQuickCommand('tab', () => _sendTypingCommand('tab')),
                _buildQuickCommand('ctrl+c', () => _sendTypingCommand('ctrl+c')),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Application commands
            _buildCommandSection(
              'Applications',
              Icons.apps,
              [
                _buildQuickCommand('aç cursor', () => _sendApplicationCommand('aç', 'cursor')),
                _buildQuickCommand('aç chrome', () => _sendApplicationCommand('aç', 'chrome')),
                _buildQuickCommand('kapat notepad', () => _sendApplicationCommand('kapat', 'notepad')),
                _buildQuickCommand('listele uygulamalar', () => _sendApplicationCommand('listele', 'uygulamalar')),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Browser commands
            _buildCommandSection(
              'Browser',
              Icons.web,
              [
                _buildQuickCommand('yeni sekme', () => _sendBrowserCommand('yeni_sekme')),
                _buildQuickCommand('ara google', () => _sendBrowserCommand('search', query: 'google')),
                _buildQuickCommand('ara youtube', () => _sendBrowserCommand('search', query: 'youtube', engine: 'youtube')),
                _buildQuickCommand('kapat sekme', () => _sendBrowserCommand('close_tab')),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // System commands
            _buildCommandSection(
              'System',
              Icons.settings,
              [
                _buildQuickCommand('sistem bilgi', () => _sendSystemCommand('info')),
                _buildQuickCommand('ses 50', () => _sendSystemCommand('volume', parameters: {'level': 50})),
                _buildQuickCommand('parlaklık 80', () => _sendSystemCommand('brightness', parameters: {'level': 80})),
                _buildQuickCommand('kilit', () => _sendSystemCommand('lock')),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Media commands
            _buildCommandSection(
              'Media',
              Icons.play_circle,
              [
                _buildQuickCommand('çal', () => _sendMediaCommand('play')),
                _buildQuickCommand('dur', () => _sendMediaCommand('pause')),
                _buildQuickCommand('sonraki', () => _sendMediaCommand('next')),
                _buildQuickCommand('önceki', () => _sendMediaCommand('previous')),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCommandSection(String title, IconData icon, List<Widget> commands) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: Colors.grey.shade600),
            const SizedBox(width: 8),
            Text(
              title,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade700,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: commands,
        ),
      ],
    );
  }

  Widget _buildQuickCommand(String text, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.blue.shade100,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.blue.shade300),
        ),
        child: Text(
          text,
          style: TextStyle(
            color: Colors.blue.shade800,
            fontSize: 12,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }

  void _sendTypingCommand(String text) {
    CommandService().sendTypingCommand(text);
  }

  void _sendApplicationCommand(String action, String appName) {
    CommandService().sendApplicationCommand(action, appName);
  }

  void _sendBrowserCommand(String action, {String? query, String? engine}) {
    CommandService().sendBrowserCommand(action, query: query, engine: engine);
  }

  void _sendSystemCommand(String action, {Map<String, dynamic>? parameters}) {
    CommandService().sendSystemCommand(action, parameters: parameters);
  }

  void _sendMediaCommand(String action, {String? songName, String? artist, int? volume}) {
    CommandService().sendMediaCommand(action, songName: songName, artist: artist, volume: volume);
  }
}
