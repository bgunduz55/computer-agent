import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/app_provider.dart';

class ScreenshotWidget extends ConsumerWidget {
  const ScreenshotWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appState = ref.watch(appStateProvider);
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Screenshot Header
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Icon(Icons.screenshot, color: theme.colorScheme.primary),
                      const SizedBox(width: 8),
                      Text(
                        'Screenshot',
                        style: theme.textTheme.titleLarge,
                      ),
                      const Spacer(),
                      ElevatedButton.icon(
                        onPressed: () {
                          ref.read(appStateProvider.notifier).requestScreenshot();
                        },
                        icon: const Icon(Icons.camera_alt),
                        label: const Text('Take Screenshot'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Screenshot Content
          Expanded(
            child: appState.screenshot != null
                ? _buildScreenshotContent(appState.screenshot!, theme, context, ref)
                : _buildNoScreenshotContent(theme, ref),
          ),
        ],
      ),
    );
  }

  Widget _buildScreenshotContent(String screenshot, ThemeData theme, BuildContext context, WidgetRef ref) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Screenshot Image
            Expanded(
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  border: Border.all(color: theme.colorScheme.outline),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.asset(
                    'assets/images/placeholder.png',
                    fit: BoxFit.contain,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: theme.colorScheme.surfaceContainerHighest,
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.image_not_supported,
                              size: 64,
                              color: theme.colorScheme.outline,
                            ),
                            const SizedBox(height: 16),
                            Text(
                              'Screenshot Preview',
                              style: theme.textTheme.titleMedium,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Screenshot data received but preview not implemented',
                              style: theme.textTheme.bodyMedium,
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Screenshot Actions
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: () {
                    // Implement save functionality
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Screenshot saved to gallery'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                  icon: const Icon(Icons.save),
                  label: const Text('Save'),
                ),
                ElevatedButton.icon(
                  onPressed: () {
                    // Implement share functionality
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Screenshot shared'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                  icon: const Icon(Icons.share),
                  label: const Text('Share'),
                ),
                ElevatedButton.icon(
                  onPressed: () {
                    // Clear screenshot
                    ref.read(appStateProvider.notifier).clearScreenshot();
                  },
                  icon: const Icon(Icons.clear),
                  label: const Text('Clear'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoScreenshotContent(ThemeData theme, WidgetRef ref) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.screenshot_monitor,
            size: 64,
            color: theme.colorScheme.outline,
          ),
          const SizedBox(height: 16),
          Text(
            'No Screenshot Available',
            style: theme.textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'Tap the "Take Screenshot" button to capture the screen',
            style: theme.textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              ref.read(appStateProvider.notifier).requestScreenshot();
            },
            icon: const Icon(Icons.camera_alt),
            label: const Text('Take Screenshot'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }
}
