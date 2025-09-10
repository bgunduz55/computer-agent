import 'package:flutter/material.dart';
import 'package:logger/logger.dart';

/// Centralized error handling utility for the JARVIS Flutter app
class ErrorHandler {
  static final Logger _logger = Logger();
  
  /// Handle and display errors with appropriate UI feedback
  static void handleError(
    BuildContext context,
    dynamic error, {
    String? title,
    String? customMessage,
    VoidCallback? onRetry,
    bool showSnackBar = true,
    bool showDialog = false,
  }) {
    final errorMessage = _getErrorMessage(error, customMessage);
    final errorTitle = title ?? 'Error';
    
    _logger.e('Error: $errorTitle - $errorMessage', error: error);
    
    if (showDialog) {
      _showErrorDialog(context, errorTitle, errorMessage, onRetry);
    } else if (showSnackBar) {
      _showErrorSnackBar(context, errorMessage, onRetry);
    }
  }
  
  /// Handle network errors specifically
  static void handleNetworkError(
    BuildContext context,
    dynamic error, {
    VoidCallback? onRetry,
  }) {
    String message = 'Network error occurred';
    
    if (error.toString().contains('SocketException')) {
      message = 'Unable to connect to server. Please check your internet connection.';
    } else if (error.toString().contains('TimeoutException')) {
      message = 'Request timed out. Please try again.';
    } else if (error.toString().contains('HandshakeException')) {
      message = 'Secure connection failed. Please check server configuration.';
    } else if (error.toString().contains('FormatException')) {
      message = 'Invalid response format from server.';
    }
    
    handleError(
      context,
      error,
      title: 'Connection Error',
      customMessage: message,
      onRetry: onRetry,
      showDialog: true,
    );
  }
  
  /// Handle authentication errors
  static void handleAuthError(
    BuildContext context,
    dynamic error, {
    VoidCallback? onRetry,
  }) {
    String message = 'Authentication failed';
    
    if (error.toString().contains('401') || error.toString().contains('Unauthorized')) {
      message = 'Invalid authentication token. Please check your credentials.';
    } else if (error.toString().contains('403') || error.toString().contains('Forbidden')) {
      message = 'Access denied. You do not have permission to perform this action.';
    } else if (error.toString().contains('Token expired')) {
      message = 'Your session has expired. Please log in again.';
    }
    
    handleError(
      context,
      error,
      title: 'Authentication Error',
      customMessage: message,
      onRetry: onRetry,
      showDialog: true,
    );
  }
  
  /// Handle voice recognition errors
  static void handleVoiceError(
    BuildContext context,
    dynamic error, {
    VoidCallback? onRetry,
  }) {
    String message = 'Voice recognition error';
    
    if (error.toString().contains('Permission denied')) {
      message = 'Microphone permission is required for voice recognition.';
    } else if (error.toString().contains('No speech detected')) {
      message = 'No speech detected. Please try speaking again.';
    } else if (error.toString().contains('Network error')) {
      message = 'Voice recognition service is unavailable. Please check your connection.';
    } else if (error.toString().contains('Language not supported')) {
      message = 'Selected language is not supported for voice recognition.';
    }
    
    handleError(
      context,
      error,
      title: 'Voice Recognition Error',
      customMessage: message,
      onRetry: onRetry,
      showSnackBar: true,
    );
  }
  
  /// Handle file operation errors
  static void handleFileError(
    BuildContext context,
    dynamic error, {
    VoidCallback? onRetry,
  }) {
    String message = 'File operation failed';
    
    if (error.toString().contains('Permission denied')) {
      message = 'Permission denied. Unable to access the requested file or directory.';
    } else if (error.toString().contains('File not found')) {
      message = 'File or directory not found.';
    } else if (error.toString().contains('Disk full')) {
      message = 'Insufficient disk space to complete the operation.';
    } else if (error.toString().contains('Access denied')) {
      message = 'Access denied. You do not have permission to perform this file operation.';
    }
    
    handleError(
      context,
      error,
      title: 'File Operation Error',
      customMessage: message,
      onRetry: onRetry,
      showSnackBar: true,
    );
  }
  
  /// Handle AI service errors
  static void handleAIError(
    BuildContext context,
    dynamic error, {
    VoidCallback? onRetry,
  }) {
    String message = 'AI service error';
    
    if (error.toString().contains('API key')) {
      message = 'Invalid or missing API key for AI service.';
    } else if (error.toString().contains('Rate limit')) {
      message = 'AI service rate limit exceeded. Please try again later.';
    } else if (error.toString().contains('Quota exceeded')) {
      message = 'AI service quota exceeded. Please check your subscription.';
    } else if (error.toString().contains('Model not available')) {
      message = 'Selected AI model is not available. Please try a different model.';
    }
    
    handleError(
      context,
      error,
      title: 'AI Service Error',
      customMessage: message,
      onRetry: onRetry,
      showSnackBar: true,
    );
  }
  
  /// Get user-friendly error message
  static String _getErrorMessage(dynamic error, String? customMessage) {
    if (customMessage != null) return customMessage;
    
    if (error is String) return error;
    
    if (error is Exception) {
      return error.toString().replaceFirst('Exception: ', '');
    }
    
    return 'An unexpected error occurred. Please try again.';
  }
  
  /// Show error dialog
  static void _showErrorDialog(
    BuildContext context,
    String title,
    String message,
    VoidCallback? onRetry,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.error_outline_rounded,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(width: 8),
            Text(title),
          ],
        ),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
          if (onRetry != null)
            FilledButton(
              onPressed: () {
                Navigator.of(context).pop();
                onRetry();
              },
              child: const Text('Retry'),
            ),
        ],
      ),
    );
  }
  
  /// Show error snackbar
  static void _showErrorSnackBar(
    BuildContext context,
    String message,
    VoidCallback? onRetry,
  ) {
    final theme = Theme.of(context);
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: theme.colorScheme.errorContainer,
        behavior: SnackBarBehavior.floating,
        action: onRetry != null
            ? SnackBarAction(
                label: 'Retry',
                textColor: theme.colorScheme.onErrorContainer,
                onPressed: onRetry,
              )
            : null,
        duration: const Duration(seconds: 4),
      ),
    );
  }
  
  /// Log error for debugging
  static void logError(String context, dynamic error, [StackTrace? stackTrace]) {
    _logger.e('Error in $context: $error', error: error, stackTrace: stackTrace);
  }
  
  /// Log warning
  static void logWarning(String context, String message) {
    _logger.w('Warning in $context: $message');
  }
  
  /// Log info
  static void logInfo(String context, String message) {
    _logger.i('Info in $context: $message');
  }
}
