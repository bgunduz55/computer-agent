import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';
import '../models/websocket_message.dart';

class FileExplorerWidget extends ConsumerStatefulWidget {
  const FileExplorerWidget({super.key});

  @override
  ConsumerState<FileExplorerWidget> createState() => _FileExplorerWidgetState();
}

class _FileExplorerWidgetState extends ConsumerState<FileExplorerWidget> {
  String _currentPath = '.';
  final TextEditingController _pathController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _pathController.text = _currentPath;
    // Load initial directory
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(appStateProvider.notifier).requestFileList(_currentPath);
    });
  }

  @override
  void dispose() {
    _pathController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final appState = ref.watch(appStateProvider);
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // File Explorer Header
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Icon(Icons.folder, color: theme.colorScheme.primary),
                      const SizedBox(width: 8),
                      Text(
                        'File Explorer',
                        style: theme.textTheme.titleLarge,
                      ),
                      const Spacer(),
                      ElevatedButton.icon(
                        onPressed: () {
                          ref.read(appStateProvider.notifier).requestFileList(_currentPath);
                        },
                        icon: const Icon(Icons.refresh),
                        label: const Text('Refresh'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _pathController,
                          decoration: const InputDecoration(
                            labelText: 'Current Path',
                            hintText: 'Enter directory path...',
                            border: OutlineInputBorder(),
                          ),
                          onSubmitted: (value) => _navigateToPath(value),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        onPressed: () => _navigateToPath(_pathController.text),
                        icon: const Icon(Icons.navigate_next),
                        style: IconButton.styleFrom(
                          backgroundColor: theme.colorScheme.primary,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // File List
          Expanded(
            child: appState.fileList.isNotEmpty
                ? _buildFileList(appState.fileList, theme)
                : _buildNoDataContent(theme),
          ),
        ],
      ),
    );
  }

  Widget _buildFileList(List<FileInfo> files, ThemeData theme) {
    return Card(
      child: ListView.builder(
        itemCount: files.length,
        itemBuilder: (context, index) {
          final file = files[index];
          return _buildFileItem(file, theme);
        },
      ),
    );
  }

  Widget _buildFileItem(FileInfo file, ThemeData theme) {
    return ListTile(
      leading: Icon(
        file.isDirectory ? Icons.folder : Icons.insert_drive_file,
        color: file.isDirectory ? Colors.blue : Colors.grey,
      ),
      title: Text(
        file.name,
        style: const TextStyle(fontWeight: FontWeight.w500),
      ),
      subtitle: Text(
        file.isDirectory 
            ? 'Directory' 
            : '${_formatFileSize(file.size)}',
        style: theme.textTheme.bodySmall,
      ),
      trailing: file.isDirectory
          ? IconButton(
              icon: const Icon(Icons.navigate_next),
              onPressed: () => _navigateToDirectory(file.path),
            )
          : PopupMenuButton<String>(
              onSelected: (value) => _handleFileAction(value, file),
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'download',
                  child: Row(
                    children: [
                      Icon(Icons.download),
                      SizedBox(width: 8),
                      Text('Download'),
                    ],
                  ),
                ),
                const PopupMenuItem(
                  value: 'delete',
                  child: Row(
                    children: [
                      Icon(Icons.delete),
                      SizedBox(width: 8),
                      Text('Delete'),
                    ],
                  ),
                ),
                const PopupMenuItem(
                  value: 'properties',
                  child: Row(
                    children: [
                      Icon(Icons.info),
                      SizedBox(width: 8),
                      Text('Properties'),
                    ],
                  ),
                ),
              ],
            ),
      onTap: () {
        if (file.isDirectory) {
          _navigateToDirectory(file.path);
        } else {
          _showFilePreview(file);
        }
      },
    );
  }

  Widget _buildNoDataContent(ThemeData theme) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.folder_open,
            size: 64,
            color: theme.colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No Files Found',
            style: theme.textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'This directory appears to be empty',
            style: theme.textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  String _formatFileSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    if (bytes < 1024 * 1024 * 1024) return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
  }

  void _navigateToPath(String path) {
    setState(() {
      _currentPath = path;
      _pathController.text = path;
    });
    ref.read(appStateProvider.notifier).requestFileList(path);
  }

  void _navigateToDirectory(String path) {
    _navigateToPath(path);
  }

  void _handleFileAction(String action, FileInfo file) {
    switch (action) {
      case 'download':
        _downloadFile(file);
        break;
      case 'delete':
        _deleteFile(file);
        break;
      case 'properties':
        _showFileProperties(file);
        break;
    }
  }

  void _downloadFile(FileInfo file) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Downloading ${file.name}...'),
        duration: const Duration(seconds: 2),
      ),
    );
    // Implement file download
  }

  void _deleteFile(FileInfo file) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete File'),
        content: Text('Are you sure you want to delete "${file.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('${file.name} deleted'),
                  duration: const Duration(seconds: 2),
                ),
              );
              // Refresh file list
              ref.read(appStateProvider.notifier).requestFileList(_currentPath);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  void _showFileProperties(FileInfo file) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Properties: ${file.name}'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Name: ${file.name}'),
            Text('Path: ${file.path}'),
            Text('Type: ${file.isDirectory ? 'Directory' : 'File'}'),
            Text('Size: ${_formatFileSize(file.size)}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showFilePreview(FileInfo file) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Preview: ${file.name}'),
        content: const Text('File preview will be implemented here'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
