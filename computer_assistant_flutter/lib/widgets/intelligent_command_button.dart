import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:permission_handler/permission_handler.dart';

class IntelligentCommandButton extends StatefulWidget {
  final Function(String) onCommandRecognized;
  final Function() onStartListening;
  final Function() onStopListening;
  final bool enabled;
  final bool isProcessing;
  final String currentStep;
  final double progress;

  const IntelligentCommandButton({
    Key? key,
    required this.onCommandRecognized,
    required this.onStartListening,
    required this.onStopListening,
    this.enabled = true,
    this.isProcessing = false,
    this.currentStep = '',
    this.progress = 0.0,
  }) : super(key: key);

  @override
  State<IntelligentCommandButton> createState() => _IntelligentCommandButtonState();
}

class _IntelligentCommandButtonState extends State<IntelligentCommandButton>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _scaleController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _scaleAnimation;

  final SpeechToText _speech = SpeechToText();
  bool _isListening = false;
  bool _isAvailable = false;
  String _lastWords = '';
  bool _isProcessing = false;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeSpeech();
  }

  void _initializeAnimations() {
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    
    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );

    _pulseAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _pulseController,
      curve: Curves.easeInOut,
    ));

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: Curves.easeInOut,
    ));
  }

  Future<void> _initializeSpeech() async {
    // Mikrofon izni iste
    final status = await Permission.microphone.request();
    if (status != PermissionStatus.granted) {
      setState(() {
        _isAvailable = false;
      });
      return;
    }

    // Ses tanıma kullanılabilirliğini kontrol et
    _isAvailable = await _speech.initialize(
      onStatus: (status) {
        setState(() {
          _isListening = status == 'listening';
        });
        
        if (status == 'listening') {
          widget.onStartListening();
          _pulseController.repeat(reverse: true);
        } else if (status == 'notListening') {
          widget.onStopListening();
          _pulseController.stop();
          _pulseController.reset();
        }
      },
      onError: (error) {
        setState(() {
          _isListening = false;
        });
        _pulseController.stop();
        _pulseController.reset();
        
        // Hata mesajı göster
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Ses tanıma hatası: ${error.errorMsg}'),
            backgroundColor: Colors.red,
          ),
        );
      },
    );

    setState(() {});
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _scaleController.dispose();
    super.dispose();
  }

  Future<void> _startListening() async {
    if (!_isAvailable || !widget.enabled || _isProcessing) return;

    setState(() {
      _isProcessing = true;
      _lastWords = '';
    });

    try {
      await _speech.listen(
        onResult: (result) {
          setState(() {
            _lastWords = result.recognizedWords;
          });
          
          if (result.finalResult) {
            final recognizedText = result.recognizedWords.trim();
            if (recognizedText.isNotEmpty) {
              widget.onCommandRecognized(recognizedText);
              setState(() {
                _lastWords = '';
                _isProcessing = false;
                _isListening = false;
              });
            }
          }
        },
        localeId: 'tr_TR',
        listenFor: const Duration(seconds: 60), // Daha uzun süre
        pauseFor: const Duration(seconds: 10),
        partialResults: true,
        cancelOnError: true,
        listenMode: ListenMode.dictation,
      );
      
      setState(() {
        _isListening = true;
      });
    } catch (e) {
      setState(() {
        _isProcessing = false;
        _isListening = false;
        _lastWords = '';
      });
    }
  }

  Future<void> _stopListening() async {
    if (!_isProcessing) return;
    
    try {
      await _speech.stop();
    } catch (e) {
      // Hata durumunda da state'i sıfırla
    } finally {
      setState(() {
        _lastWords = '';
        _isProcessing = false;
        _isListening = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Ana intelligent command butonu
        GestureDetector(
          onTapDown: (_) {
            if (widget.enabled && _isAvailable && !_isProcessing) {
              _scaleController.forward();
              _startListening();
            }
          },
          onTapUp: (_) {
            if (_isProcessing) {
              _scaleController.reverse();
              _stopListening();
            }
          },
          onTapCancel: () {
            if (_isProcessing) {
              _scaleController.reverse();
              _stopListening();
            }
          },
          child: AnimatedBuilder(
            animation: Listenable.merge([_pulseAnimation, _scaleAnimation]),
            builder: (context, child) {
              return Transform.scale(
                scale: _isListening ? _pulseAnimation.value : _scaleAnimation.value,
                child: Container(
                  width: 140,
                  height: 140,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: _isListening
                          ? [Colors.purple.shade400, Colors.purple.shade600]
                          : widget.enabled
                              ? [Colors.green.shade400, Colors.green.shade600]
                              : [Colors.grey.shade400, Colors.grey.shade600],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: (_isListening ? Colors.purple : Colors.green).withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Stack(
                    children: [
                      // Progress indicator
                      if (widget.isProcessing && widget.progress > 0)
                        Positioned.fill(
                          child: CircularProgressIndicator(
                            value: widget.progress / 100.0,
                            strokeWidth: 4,
                            backgroundColor: Colors.white.withOpacity(0.3),
                            valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        ),
                      // Icon
                      Center(
                        child: Icon(
                          _isListening ? Icons.smart_toy : Icons.psychology,
                          size: 60,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        
        const SizedBox(height: 20),
        
        // Durum metni
        Text(
          _isProcessing
              ? (_isListening ? 'Akıllı komut dinleniyor... Bırakın' : 'Akıllı komut işleniyor...')
              : _isAvailable
                  ? 'Basılı tutun ve akıllı komut söyleyin'
                  : 'Ses tanıma kullanılamıyor',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            color: _isAvailable ? Colors.grey.shade700 : Colors.red.shade600,
          ),
          textAlign: TextAlign.center,
        ),
        
        // Tanınan metin
        const SizedBox(height: 16),
        Container(
          height: 100,
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: _lastWords.isNotEmpty ? Colors.green.shade50 : Colors.grey.shade50,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: _lastWords.isNotEmpty ? Colors.green.shade200 : Colors.grey.shade200,
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                _lastWords.isNotEmpty ? 'Akıllı komut:' : 'Akıllı komut bekleniyor...',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: _lastWords.isNotEmpty ? Colors.green.shade800 : Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 8),
              Expanded(
                child: Center(
                  child: Text(
                    _lastWords.isNotEmpty ? _lastWords : '',
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.black87,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ),
            ],
          ),
        ),

        // Progress indicator for multi-step commands
        if (widget.isProcessing && widget.currentStep.isNotEmpty) ...[
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.blue.shade200),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Adım: ${widget.currentStep}',
                        style: TextStyle(
                          color: Colors.blue.shade800,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
                if (widget.progress > 0) ...[
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: widget.progress / 100.0,
                    backgroundColor: Colors.blue.shade200,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade600),
                  ),
                ],
              ],
            ),
          ),
        ],
        
        // Kullanılabilirlik durumu
        if (!_isAvailable) ...[
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.red.shade50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.red.shade200),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.error_outline, color: Colors.red.shade600, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Mikrofon izni gerekli',
                  style: TextStyle(
                    color: Colors.red.shade600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}
