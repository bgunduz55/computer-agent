import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:permission_handler/permission_handler.dart';

class VoiceButton extends StatefulWidget {
  final Function(String) onCommandRecognized;
  final Function() onStartListening;
  final Function() onStopListening;
  final bool enabled;

  const VoiceButton({
    Key? key,
    required this.onCommandRecognized,
    required this.onStartListening,
    required this.onStopListening,
    this.enabled = true,
  }) : super(key: key);

  @override
  State<VoiceButton> createState() => _VoiceButtonState();
}

class _VoiceButtonState extends State<VoiceButton>
    with TickerProviderStateMixin {
  late AnimationController _pulseController;
  late AnimationController _scaleController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _scaleAnimation;

  final SpeechToText _speech = SpeechToText();
  bool _isListening = false;
  bool _isAvailable = false;
  String _lastWords = '';

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
    if (!_isAvailable || !widget.enabled) return;

    await _speech.listen(
      onResult: (result) {
        setState(() {
          _lastWords = result.recognizedWords;
        });
        
        // Eğer sonuç kesin ise (final result), hemen gönder
        if (result.finalResult) {
          final recognizedText = result.recognizedWords.trim();
          if (recognizedText.isNotEmpty) {
            widget.onCommandRecognized(recognizedText);
            setState(() {
              _lastWords = '';
            });
          }
        }
      },
      localeId: 'tr_TR', // Türkçe
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 3),
      partialResults: true,
      cancelOnError: true,
      listenMode: ListenMode.dictation, // Dictation mode daha iyi çalışır
    );
  }

  Future<void> _stopListening() async {
    await _speech.stop();
    
    // Son tanınan metni al ve gönder
    final recognizedText = _lastWords.trim();
    if (recognizedText.isNotEmpty) {
      widget.onCommandRecognized(recognizedText);
      setState(() {
        _lastWords = '';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Ana ses butonu
        GestureDetector(
          onTapDown: (_) {
            if (widget.enabled && _isAvailable) {
              _scaleController.forward();
              _startListening();
            }
          },
          onTapUp: (_) {
            _scaleController.reverse();
            _stopListening();
          },
          onTapCancel: () {
            _scaleController.reverse();
            _stopListening();
          },
          child: AnimatedBuilder(
            animation: Listenable.merge([_pulseAnimation, _scaleAnimation]),
            builder: (context, child) {
              return Transform.scale(
                scale: _isListening ? _pulseAnimation.value : _scaleAnimation.value,
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: _isListening
                          ? [Colors.red.shade400, Colors.red.shade600]
                          : widget.enabled
                              ? [Colors.blue.shade400, Colors.blue.shade600]
                              : [Colors.grey.shade400, Colors.grey.shade600],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: (_isListening ? Colors.red : Colors.blue).withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: Icon(
                    _isListening ? Icons.mic : Icons.mic_none,
                    size: 50,
                    color: Colors.white,
                  ),
                ),
              );
            },
          ),
        ),
        
        const SizedBox(height: 20),
        
        // Durum metni
        Text(
          _isListening
              ? 'Dinleniyor... Bırakın'
              : _isAvailable
                  ? 'Basılı tutun ve konuşun'
                  : 'Ses tanıma kullanılamıyor',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w500,
            color: _isAvailable ? Colors.grey.shade700 : Colors.red.shade600,
          ),
          textAlign: TextAlign.center,
        ),
        
        // Tanınan metin
        if (_lastWords.isNotEmpty) ...[
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
                Text(
                  'Tanınan komut:',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.blue.shade800,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  _lastWords,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                  textAlign: TextAlign.center,
                ),
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
