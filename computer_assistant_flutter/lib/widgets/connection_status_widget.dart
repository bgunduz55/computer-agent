import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';

class ConnectionStatusWidget extends ConsumerWidget {
  const ConnectionStatusWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);

    Color statusColor;
    IconData statusIcon;
    String statusText;

    if (appState.isConnected && appState.isAuthenticated) {
      statusColor = Colors.green;
      statusIcon = Icons.wifi;
      statusText = 'Connected';
    } else if (appState.isConnected) {
      statusColor = Colors.orange;
      statusIcon = Icons.wifi_lock;
      statusText = 'Connected (Unauthenticated)';
    } else {
      statusColor = Colors.red;
      statusIcon = Icons.wifi_off;
      statusText = 'Disconnected';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: statusColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: statusColor, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            statusIcon,
            size: 16,
            color: statusColor,
          ),
          const SizedBox(width: 4),
          Text(
            statusText,
            style: TextStyle(
              color: statusColor,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
