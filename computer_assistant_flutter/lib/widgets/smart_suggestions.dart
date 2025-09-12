import 'package:flutter/material.dart';

class SmartSuggestions extends StatefulWidget {
  final Function(String) onSuggestionSelected;
  final bool enabled;

  const SmartSuggestions({
    Key? key,
    required this.onSuggestionSelected,
    this.enabled = true,
  }) : super(key: key);

  @override
  State<SmartSuggestions> createState() => _SmartSuggestionsState();
}

class _SmartSuggestionsState extends State<SmartSuggestions> {
  final TextEditingController _textController = TextEditingController();
  List<String> _suggestions = [];
  bool _isLoading = false;

  // Örnek AI önerileri
  final List<String> _sampleSuggestions = [
    'Yaz merhaba dünya',
    'Aç tarayıcı',
    'Listele çalışan uygulamalar',
    'Sistem bilgisini göster',
    'Müzik çal',
    'Dosya aç',
    'Klasör listele',
    'Uygulama kapat',
  ];

  @override
  void initState() {
    super.initState();
    _loadSuggestions();
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  void _loadSuggestions() {
    setState(() {
      _isLoading = true;
    });

    // Simüle edilmiş AI yanıtı
    Future.delayed(const Duration(seconds: 1), () {
      if (mounted) {
        setState(() {
          _suggestions = _sampleSuggestions;
          _isLoading = false;
        });
      }
    });
  }

  void _searchSuggestions(String query) {
    if (query.isEmpty) {
      setState(() {
        _suggestions = _sampleSuggestions;
      });
      return;
    }

    setState(() {
      _isLoading = true;
    });

    // Simüle edilmiş arama
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) {
        final filtered = _sampleSuggestions
            .where((suggestion) => 
                suggestion.toLowerCase().contains(query.toLowerCase()))
            .toList();
        
        setState(() {
          _suggestions = filtered;
          _isLoading = false;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
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
          // Başlık ve arama
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.purple.shade50,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
              ),
            ),
            child: Column(
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.psychology,
                      color: Colors.purple.shade600,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Akıllı Öneriler',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey.shade800,
                      ),
                    ),
                    const Spacer(),
                    Icon(
                      Icons.auto_awesome,
                      color: Colors.amber.shade600,
                      size: 20,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _textController,
                  onChanged: _searchSuggestions,
                  enabled: widget.enabled,
                  decoration: InputDecoration(
                    hintText: 'Komut ara veya yazın...',
                    prefixIcon: Icon(
                      Icons.search,
                      color: Colors.grey.shade600,
                    ),
                    suffixIcon: _textController.text.isNotEmpty
                        ? IconButton(
                            onPressed: () {
                              _textController.clear();
                              _searchSuggestions('');
                            },
                            icon: Icon(
                              Icons.clear,
                              color: Colors.grey.shade600,
                            ),
                          )
                        : null,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey.shade300),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.grey.shade300),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: Colors.purple.shade400),
                    ),
                    filled: true,
                    fillColor: Colors.white,
                  ),
                ),
              ],
            ),
          ),
          
          // Öneriler listesi
          Expanded(
            child: _isLoading
                ? _buildLoadingState()
                : _suggestions.isEmpty
                    ? _buildEmptyState()
                    : _buildSuggestionsList(),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text(
            'AI önerileri yükleniyor...',
            style: TextStyle(
              color: Colors.grey,
              fontSize: 14,
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
            Icons.search_off,
            size: 64,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            'Öneri bulunamadı',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Farklı bir arama terimi deneyin',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionsList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _suggestions.length,
      itemBuilder: (context, index) {
        final suggestion = _suggestions[index];
        return _buildSuggestionItem(suggestion, index);
      },
    );
  }

  Widget _buildSuggestionItem(String suggestion, int index) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: widget.enabled ? () => widget.onSuggestionSelected(suggestion) : null,
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: widget.enabled ? Colors.grey.shade50 : Colors.grey.shade100,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Colors.purple.shade200,
                width: 1,
              ),
            ),
            child: Row(
              children: [
                // AI ikonu
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: Colors.purple.shade100,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.auto_awesome,
                    color: Colors.purple.shade600,
                    size: 18,
                  ),
                ),
                
                const SizedBox(width: 12),
                
                // Öneri metni
                Expanded(
                  child: Text(
                    suggestion,
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: widget.enabled ? Colors.black87 : Colors.grey.shade600,
                    ),
                  ),
                ),
                
                // Kullan butonu
                if (widget.enabled)
                  IconButton(
                    onPressed: () => widget.onSuggestionSelected(suggestion),
                    icon: Icon(
                      Icons.arrow_forward_ios,
                      color: Colors.purple.shade600,
                      size: 16,
                    ),
                    tooltip: 'Kullan',
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
