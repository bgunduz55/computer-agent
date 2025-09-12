import 'package:flutter/material.dart';

class CommandInputWidget extends StatefulWidget {
  final TextEditingController controller;
  final Function(String) onSend;
  final String hintText;
  final bool enabled;
  final IconData? icon;
  final bool showVoiceButton;

  const CommandInputWidget({
    Key? key,
    required this.controller,
    required this.onSend,
    required this.hintText,
    this.enabled = true,
    this.icon,
    this.showVoiceButton = false,
  }) : super(key: key);

  @override
  State<CommandInputWidget> createState() => _CommandInputWidgetState();
}

class _CommandInputWidgetState extends State<CommandInputWidget> {
  bool _isSending = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Input field
            TextField(
              controller: widget.controller,
              enabled: widget.enabled && !_isSending,
              decoration: InputDecoration(
                hintText: widget.hintText,
                prefixIcon: widget.icon != null ? Icon(widget.icon) : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: widget.enabled ? Colors.white : Colors.grey.shade100,
              ),
              maxLines: 3,
              minLines: 1,
              textInputAction: TextInputAction.send,
              onSubmitted: (value) {
                if (value.trim().isNotEmpty && widget.enabled && !_isSending) {
                  _sendCommand(value);
                }
              },
            ),
            
            const SizedBox(height: 12),
            
            // Action buttons
            Row(
              children: [
                // Send button
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: widget.enabled && !_isSending
                        ? () => _sendCommand(widget.controller.text)
                        : null,
                    icon: _isSending
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.send),
                    label: Text(_isSending ? 'Sending...' : 'Send'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ),
                
                if (widget.showVoiceButton) ...[
                  const SizedBox(width: 8),
                  // Voice button
                  IconButton(
                    onPressed: widget.enabled && !_isSending ? _startVoiceInput : null,
                    icon: const Icon(Icons.mic),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.blue.shade100,
                      foregroundColor: Colors.blue,
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _sendCommand(String command) {
    if (command.trim().isEmpty) return;
    
    setState(() {
      _isSending = true;
    });
    
    widget.onSend(command);
    
    // Reset sending state after a short delay
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) {
        setState(() {
          _isSending = false;
        });
      }
    });
  }

  void _startVoiceInput() {
    // TODO: Implement voice input
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Voice input not implemented yet')),
    );
  }
}
