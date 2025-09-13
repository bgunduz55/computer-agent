import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';

class CommandHistory extends ConsumerWidget {
  final Function(String) onCommandSelected;
  final bool enabled;

  const CommandHistory({
    Key? key,
    required this.onCommandSelected,
    this.enabled = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    
    // Örnek komut geçmişi (gerçek uygulamada state'den gelecek)
    final commandHistory = [
      {
        'command': 'Yaz merhaba dünya',
        'timestamp': DateTime.now().subtract(const Duration(minutes: 5)),
        'success': true,
      },
      {
        'command': 'Key enter',
        'timestamp': DateTime.now().subtract(const Duration(minutes: 3)),
        'success': true,
      },
      {
        'command': 'List running apps',
        'timestamp': DateTime.now().subtract(const Duration(minutes: 1)),
        'success': true,
      },
      {
        'command': 'Open browser',
        'timestamp': DateTime.now().subtract(const Duration(seconds: 30)),
        'success': false,
      },
    ];

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade300,
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Başlık
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey.shade50,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.history,
                  color: Colors.blue.shade600,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  'Komut Geçmişi',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.grey.shade800,
                  ),
                ),
                const Spacer(),
                if (commandHistory.isNotEmpty)
                  TextButton(
                    onPressed: () {
                      // Geçmişi temizle
                    },
                    child: Text(
                      'Temizle',
                      style: TextStyle(
                        color: Colors.red.shade600,
                        fontSize: 12,
                      ),
                    ),
                  ),
              ],
            ),
          ),
          
          // Komut listesi
          Expanded(
            child: commandHistory.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: commandHistory.length,
                    itemBuilder: (context, index) {
                      final item = commandHistory[index];
                      return _buildCommandItem(item);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.history,
            size: 64,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            'Henüz komut yok',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Sesli komut vererek başlayın',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCommandItem(Map<String, dynamic> item) {
    final command = item['command'] as String;
    final timestamp = item['timestamp'] as DateTime;
    final success = item['success'] as bool;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: enabled ? () => onCommandSelected(command) : null,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: enabled ? Colors.grey.shade50 : Colors.grey.shade100,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: success ? Colors.green.shade200 : Colors.red.shade200,
                width: 1,
              ),
            ),
            child: Row(
              children: [
                // Durum ikonu
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: success ? Colors.green.shade100 : Colors.red.shade100,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    success ? Icons.check : Icons.close,
                    color: success ? Colors.green.shade600 : Colors.red.shade600,
                    size: 18,
                  ),
                ),
                
                const SizedBox(width: 12),
                
                // Komut içeriği
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        command,
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: enabled ? Colors.black87 : Colors.grey.shade600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _formatTimestamp(timestamp),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade500,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Tekrar gönder butonu
                if (enabled)
                  IconButton(
                    onPressed: () => onCommandSelected(command),
                    icon: Icon(
                      Icons.replay,
                      color: Colors.blue.shade600,
                      size: 20,
                    ),
                    tooltip: 'Tekrar gönder',
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'Az önce';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} dakika önce';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} saat önce';
    } else {
      return '${difference.inDays} gün önce';
    }
  }
}
