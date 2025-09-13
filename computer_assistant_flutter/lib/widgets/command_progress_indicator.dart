import 'package:flutter/material.dart';

class CommandStep {
  final String name;
  final String description;
  final bool isCompleted;
  final bool isCurrent;
  final bool hasError;
  final String? errorMessage;

  const CommandStep({
    required this.name,
    required this.description,
    this.isCompleted = false,
    this.isCurrent = false,
    this.hasError = false,
    this.errorMessage,
  });
}

class CommandProgressIndicator extends StatelessWidget {
  final List<CommandStep> steps;
  final int currentStep;
  final String status;
  final bool isError;
  final double progress;

  const CommandProgressIndicator({
    Key? key,
    required this.steps,
    this.currentStep = 0,
    this.status = '',
    this.isError = false,
    this.progress = 0.0,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (steps.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isError ? Colors.red.shade50 : Colors.blue.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isError ? Colors.red.shade200 : Colors.blue.shade200,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                isError ? Icons.error_outline : Icons.smart_toy,
                color: isError ? Colors.red.shade600 : Colors.blue.shade600,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                isError ? 'Komut Hatası' : 'Akıllı Komut İşleniyor',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: isError ? Colors.red.shade800 : Colors.blue.shade800,
                ),
              ),
              const Spacer(),
              if (!isError && progress > 0)
                Text(
                  '${progress.toInt()}%',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.blue.shade600,
                  ),
                ),
            ],
          ),

          const SizedBox(height: 12),

          // Progress bar
          if (!isError && progress > 0) ...[
            LinearProgressIndicator(
              value: progress / 100.0,
              backgroundColor: Colors.blue.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade600),
            ),
            const SizedBox(height: 12),
          ],

          // Status message
          if (status.isNotEmpty) ...[
            Text(
              status,
              style: TextStyle(
                fontSize: 14,
                color: isError ? Colors.red.shade700 : Colors.blue.shade700,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 12),
          ],

          // Steps list
          ...steps.asMap().entries.map((entry) {
            final index = entry.key;
            final step = entry.value;
            
            return _buildStepItem(context, index, step);
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildStepItem(BuildContext context, int index, CommandStep step) {
    Color stepColor;
    IconData stepIcon;
    
    if (step.hasError) {
      stepColor = Colors.red.shade600;
      stepIcon = Icons.error;
    } else if (step.isCompleted) {
      stepColor = Colors.green.shade600;
      stepIcon = Icons.check_circle;
    } else if (step.isCurrent) {
      stepColor = Colors.blue.shade600;
      stepIcon = Icons.radio_button_checked;
    } else {
      stepColor = Colors.grey.shade400;
      stepIcon = Icons.radio_button_unchecked;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          // Step icon
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: stepColor.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              stepIcon,
              size: 16,
              color: stepColor,
            ),
          ),
          
          const SizedBox(width: 12),
          
          // Step content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  step.name,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: stepColor,
                  ),
                ),
                if (step.description.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(
                    step.description,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
                if (step.hasError && step.errorMessage != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    step.errorMessage!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.red.shade600,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class CommandProgressController {
  final List<CommandStep> _steps = [];
  int _currentStep = 0;
  String _status = '';
  bool _isError = false;
  double _progress = 0.0;

  List<CommandStep> get steps => List.unmodifiable(_steps);
  int get currentStep => _currentStep;
  String get status => _status;
  bool get isError => _isError;
  double get progress => _progress;

  void addStep(String name, String description) {
    _steps.add(CommandStep(
      name: name,
      description: description,
    ));
  }

  void setCurrentStep(int index) {
    if (index >= 0 && index < _steps.length) {
      _currentStep = index;
      _updateStepStates();
    }
  }

  void completeStep(int index) {
    if (index >= 0 && index < _steps.length) {
      _steps[index] = CommandStep(
        name: _steps[index].name,
        description: _steps[index].description,
        isCompleted: true,
      );
      _updateStepStates();
    }
  }

  void setStepError(int index, String errorMessage) {
    if (index >= 0 && index < _steps.length) {
      _steps[index] = CommandStep(
        name: _steps[index].name,
        description: _steps[index].description,
        hasError: true,
        errorMessage: errorMessage,
      );
      _isError = true;
    }
  }

  void setStatus(String status) {
    _status = status;
  }

  void setProgress(double progress) {
    _progress = progress.clamp(0.0, 100.0);
  }

  void setError(bool isError) {
    _isError = isError;
  }

  void reset() {
    _steps.clear();
    _currentStep = 0;
    _status = '';
    _isError = false;
    _progress = 0.0;
  }

  void _updateStepStates() {
    for (int i = 0; i < _steps.length; i++) {
      _steps[i] = CommandStep(
        name: _steps[i].name,
        description: _steps[i].description,
        isCompleted: i < _currentStep,
        isCurrent: i == _currentStep,
        hasError: _steps[i].hasError,
        errorMessage: _steps[i].errorMessage,
      );
    }
  }
}
