import 'package:flutter/material.dart';

class QuickCommands extends StatelessWidget {
  final Function(String) onCommandSelected;
  final bool enabled;

  const QuickCommands({
    Key? key,
    required this.onCommandSelected,
    this.enabled = true,
  }) : super(key: key);

  static const List<Map<String, dynamic>> _commands = [
    {
      'text': 'Yaz',
      'icon': Icons.keyboard,
      'command': 'yaz ',
      'color': Colors.blue,
    },
    {
      'text': 'Enter',
      'icon': Icons.keyboard_return,
      'command': 'enter',
      'color': Colors.green,
    },
    {
      'text': 'Aç',
      'icon': Icons.open_in_new,
      'command': 'aç ',
      'color': Colors.orange,
    },
    {
      'text': 'Kapat',
      'icon': Icons.close,
      'command': 'kapat ',
      'color': Colors.red,
    },
    {
      'text': 'Ara',
      'icon': Icons.search,
      'command': 'ara ',
      'color': Colors.purple,
    },
    {
      'text': 'Listele',
      'icon': Icons.list,
      'command': 'listele ',
      'color': Colors.teal,
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
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
          Row(
            children: [
              Icon(
                Icons.flash_on,
                color: Colors.amber.shade600,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Hızlı Komutlar',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade800,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: _commands.map((cmd) => _buildCommandChip(cmd)).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildCommandChip(Map<String, dynamic> cmd) {
    return GestureDetector(
      onTap: enabled ? () => onCommandSelected(cmd['command']) : null,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: enabled 
              ? (cmd['color'] as Color).withOpacity(0.1)
              : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(25),
          border: Border.all(
            color: enabled 
                ? (cmd['color'] as Color).withOpacity(0.3)
                : Colors.grey.shade300,
            width: 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              cmd['icon'],
              size: 18,
              color: enabled 
                  ? cmd['color'] as Color
                  : Colors.grey.shade500,
            ),
            const SizedBox(width: 8),
            Text(
              cmd['text'],
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: enabled 
                    ? cmd['color'] as Color
                    : Colors.grey.shade500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
