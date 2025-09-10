import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';
import '../utils/error_handler.dart';

class RAGWidget extends ConsumerStatefulWidget {
  const RAGWidget({super.key});

  @override
  ConsumerState<RAGWidget> createState() => _RAGWidgetState();
}

class _RAGWidgetState extends ConsumerState<RAGWidget> {
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _documentController = TextEditingController();
  final TextEditingController _metadataController = TextEditingController();
  
  bool _isSearching = false;
  bool _isAddingDocument = false;
  List<Map<String, dynamic>> _searchResults = [];
  List<Map<String, dynamic>> _documents = [];

  @override
  void initState() {
    super.initState();
    _loadDocuments();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _documentController.dispose();
    _metadataController.dispose();
    super.dispose();
  }

  Future<void> _loadDocuments() async {
    try {
      // Request documents from server via WebSocket
      await ref.read(appStateProvider.notifier).requestRAGDocuments();
      
      // Listen to RAG documents response
      ref.listen(appStateProvider, (previous, next) {
        if (next.ragDocuments != null) {
          setState(() {
            _documents = next.ragDocuments!;
          });
        }
      });
    } catch (e) {
      ErrorHandler.handleError(
        context,
        e,
        title: 'RAG Error',
        customMessage: 'Failed to load documents',
        onRetry: () => _loadDocuments(),
      );
    }
  }

  Future<void> _searchDocuments() async {
    if (_searchController.text.trim().isEmpty) return;

    setState(() {
      _isSearching = true;
    });

    try {
      // Send search request via WebSocket
      await ref.read(appStateProvider.notifier).searchRAGDocuments(_searchController.text.trim());
      
      // Listen to search results
      ref.listen(appStateProvider, (previous, next) {
        if (next.ragSearchResults != null) {
          setState(() {
            _searchResults = next.ragSearchResults!;
          });
        }
      });
    } catch (e) {
      ErrorHandler.handleError(
        context,
        e,
        title: 'Search Error',
        customMessage: 'Failed to search documents',
        onRetry: () => _searchDocuments(),
      );
    } finally {
      setState(() {
        _isSearching = false;
      });
    }
  }

  Future<void> _addDocument() async {
    if (_documentController.text.trim().isEmpty) return;

    setState(() {
      _isAddingDocument = true;
    });

    try {
      // Parse metadata
      Map<String, dynamic> metadata = {};
      if (_metadataController.text.trim().isNotEmpty) {
        // Simple key:value parsing
        final parts = _metadataController.text.trim().split(',');
        for (final part in parts) {
          final keyValue = part.split(':');
          if (keyValue.length == 2) {
            metadata[keyValue[0].trim()] = keyValue[1].trim();
          }
        }
      }
      metadata['type'] = 'user_document';
      
      // Send document addition request via WebSocket
      await ref.read(appStateProvider.notifier).addRAGDocument(
        _documentController.text.trim(),
        metadata,
      );
      
      // Clear form
      _documentController.clear();
      _metadataController.clear();
      
      // Reload documents
      await _loadDocuments();
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Document added successfully'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } catch (e) {
      ErrorHandler.handleError(
        context,
        e,
        title: 'Add Document Error',
        customMessage: 'Failed to add document',
        onRetry: () => _addDocument(),
      );
    } finally {
      setState(() {
        _isAddingDocument = false;
      });
    }
  }

  Future<void> _deleteDocument(String docId) async {
    try {
      // Send document deletion request via WebSocket
      await ref.read(appStateProvider.notifier).deleteRAGDocument(docId);
      
      // Update local state
      setState(() {
        _documents.removeWhere((doc) => doc['id'] == docId);
        _searchResults.removeWhere((doc) => doc['id'] == docId);
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Document deleted successfully'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } catch (e) {
      ErrorHandler.handleError(
        context,
        e,
        title: 'Delete Document Error',
        customMessage: 'Failed to delete document',
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                Icons.search_rounded,
                color: theme.colorScheme.primary,
                size: 28,
              ),
              const SizedBox(width: 12),
              Text(
                'RAG Knowledge Base',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          
          // Search Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Search Documents',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _searchController,
                          decoration: const InputDecoration(
                            labelText: 'Search query',
                            hintText: 'Enter your search query...',
                            prefixIcon: Icon(Icons.search_rounded),
                            filled: true,
                          ),
                          onSubmitted: (_) => _searchDocuments(),
                        ),
                      ),
                      const SizedBox(width: 12),
                      FilledButton.icon(
                        onPressed: _isSearching ? null : _searchDocuments,
                        icon: _isSearching
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.search_rounded),
                        label: Text(_isSearching ? 'Searching...' : 'Search'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Add Document Section
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Add Document',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _documentController,
                    decoration: const InputDecoration(
                      labelText: 'Document content',
                      hintText: 'Enter document content...',
                      prefixIcon: Icon(Icons.description_rounded),
                      filled: true,
                    ),
                    maxLines: 3,
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _metadataController,
                    decoration: const InputDecoration(
                      labelText: 'Metadata (optional)',
                      hintText: 'e.g., type: guide, category: voice',
                      prefixIcon: Icon(Icons.info_rounded),
                      filled: true,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      OutlinedButton(
                        onPressed: () {
                          _documentController.clear();
                          _metadataController.clear();
                        },
                        child: const Text('Clear'),
                      ),
                      const SizedBox(width: 12),
                      FilledButton.icon(
                        onPressed: _isAddingDocument ? null : _addDocument,
                        icon: _isAddingDocument
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.add_rounded),
                        label: Text(_isAddingDocument ? 'Adding...' : 'Add Document'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Results Section
          if (_searchResults.isNotEmpty) ...[
            Text(
              'Search Results',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: _searchResults.length,
                itemBuilder: (context, index) {
                  final result = _searchResults[index];
                  return _buildSearchResultCard(result, theme);
                },
              ),
            ),
          ] else ...[
            Text(
              'All Documents',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: ListView.builder(
                itemCount: _documents.length,
                itemBuilder: (context, index) {
                  final doc = _documents[index];
                  return _buildDocumentCard(doc, theme);
                },
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSearchResultCard(Map<String, dynamic> result, ThemeData theme) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: theme.colorScheme.primaryContainer,
          child: Icon(
            Icons.search_rounded,
            color: theme.colorScheme.onPrimaryContainer,
          ),
        ),
        title: Text(
          result['content'] ?? 'No content',
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(
                  Icons.star_rounded,
                  size: 16,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 4),
                Text(
                  'Similarity: ${(result['similarity'] * 100).toStringAsFixed(1)}%',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            if (result['metadata'] != null) ...[
              const SizedBox(height: 4),
              Wrap(
                spacing: 8,
                children: (result['metadata'] as Map<String, dynamic>)
                    .entries
                    .map((entry) => Chip(
                          label: Text('${entry.key}: ${entry.value}'),
                          backgroundColor: theme.colorScheme.surfaceContainerHighest,
                          labelStyle: theme.textTheme.bodySmall,
                        ))
                    .toList(),
              ),
            ],
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete_rounded),
          onPressed: () => _deleteDocument(result['id']),
          tooltip: 'Delete document',
        ),
      ),
    );
  }

  Widget _buildDocumentCard(Map<String, dynamic> doc, ThemeData theme) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: theme.colorScheme.secondaryContainer,
          child: Icon(
            Icons.description_rounded,
            color: theme.colorScheme.onSecondaryContainer,
          ),
        ),
        title: Text(
          doc['content'] ?? 'No content',
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              'ID: ${doc['id']}',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            if (doc['created_at'] != null) ...[
              const SizedBox(height: 2),
              Text(
                'Created: ${DateTime.tryParse(doc['created_at'])?.toString().split(' ')[0] ?? 'Unknown'}',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
            if (doc['metadata'] != null) ...[
              const SizedBox(height: 4),
              Wrap(
                spacing: 8,
                children: (doc['metadata'] as Map<String, dynamic>)
                    .entries
                    .map((entry) => Chip(
                          label: Text('${entry.key}: ${entry.value}'),
                          backgroundColor: theme.colorScheme.surfaceContainerHighest,
                          labelStyle: theme.textTheme.bodySmall,
                        ))
                    .toList(),
              ),
            ],
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete_rounded),
          onPressed: () => _deleteDocument(doc['id']),
          tooltip: 'Delete document',
        ),
      ),
    );
  }
}
