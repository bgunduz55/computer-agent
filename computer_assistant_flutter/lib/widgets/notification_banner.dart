import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';

class NotificationBanner extends ConsumerWidget {
  const NotificationBanner({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    
    if (appState.notificationMessage == null) {
      return const SizedBox.shrink();
    }

    final message = appState.notificationMessage ?? '';
    final type = appState.notificationType ?? 'info';
    final timestamp = appState.notificationTimestamp ?? 0;
    
    // Auto-hide after 5 seconds
    Future.delayed(const Duration(seconds: 5), () {
      if (ref.read(appStateProvider).notificationMessage == message) {
        ref.read(appStateProvider.notifier).state = ref.read(appStateProvider).copyWith(
          notificationMessage: null,
          notificationType: null,
          notificationTimestamp: null,
        );
      }
    });

    Color backgroundColor;
    Color textColor;
    IconData icon;

    switch (type.toLowerCase()) {
      case 'success':
        backgroundColor = Colors.green.shade100;
        textColor = Colors.green.shade800;
        icon = Icons.check_circle;
        break;
      case 'error':
        backgroundColor = Colors.red.shade100;
        textColor = Colors.red.shade800;
        icon = Icons.error;
        break;
      case 'warning':
        backgroundColor = Colors.orange.shade100;
        textColor = Colors.orange.shade800;
        icon = Icons.warning;
        break;
      case 'info':
      default:
        backgroundColor = Colors.blue.shade100;
        textColor = Colors.blue.shade800;
        icon = Icons.info;
        break;
    }

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: textColor.withOpacity(0.3),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: textColor,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  message,
                  style: TextStyle(
                    color: textColor,
                    fontWeight: FontWeight.w500,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatTimestamp(timestamp),
                  style: TextStyle(
                    color: textColor.withOpacity(0.7),
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () {
              ref.read(appStateProvider.notifier).state = ref.read(appStateProvider).copyWith(
                notificationMessage: null,
                notificationType: null,
                notificationTimestamp: null,
              );
            },
            icon: Icon(
              Icons.close,
              color: textColor,
              size: 18,
            ),
            padding: EdgeInsets.zero,
            constraints: const BoxConstraints(
              minWidth: 24,
              minHeight: 24,
            ),
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(int timestamp) {
    final now = DateTime.now().millisecondsSinceEpoch;
    final diff = now - timestamp;
    
    if (diff < 1000) {
      return 'Şimdi';
    } else if (diff < 60000) {
      return '${(diff / 1000).round()} saniye önce';
    } else if (diff < 3600000) {
      return '${(diff / 60000).round()} dakika önce';
    } else {
      return '${(diff / 3600000).round()} saat önce';
    }
  }
}
