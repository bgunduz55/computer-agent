"""
Speech Engines Integration for JARVIS Computer Assistant

This package provides cross-platform speech recognition and text-to-speech
engines for Windows and Linux platforms.
"""

from .common_speech import (
    BaseSpeechEngine,
    BaseSpeechRecognitionEngine,
    BaseTextToSpeechEngine,
    SpeechManager,
    WakeWordDetector,
    VoiceCommandProcessor,
    SpeechEngineType,
    Language,
    VoiceInfo,
    AudioConfig,
    SpeechConfig,
    get_speech_manager
)

# Platform-specific engines
try:
    from .windows_speech import (
        WindowsSpeechRecognitionEngine,
        SAPI5TTSEngine,
        EdgeTTSEngine
    )
    WINDOWS_ENGINES_AVAILABLE = True
except ImportError:
    WINDOWS_ENGINES_AVAILABLE = False

try:
    from .linux_speech import (
        LinuxSpeechRecognitionEngine,
        ESpeakTTSEngine,
        FestivalTTSEngine
    )
    LINUX_ENGINES_AVAILABLE = True
except ImportError:
    LINUX_ENGINES_AVAILABLE = False

try:
    from .google_speech import GoogleSpeechRecognitionEngine
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False

__all__ = [
    # Common interfaces
    "BaseSpeechEngine",
    "BaseSpeechRecognitionEngine", 
    "BaseTextToSpeechEngine",
    "SpeechManager",
    "WakeWordDetector",
    "VoiceCommandProcessor",
    "SpeechEngineType",
    "Language",
    "VoiceInfo",
    "AudioConfig",
    "SpeechConfig",
    "get_speech_manager",
    
    # Windows engines
    "WindowsSpeechRecognitionEngine",
    "SAPI5TTSEngine", 
    "EdgeTTSEngine",
    
    # Linux engines
    "LinuxSpeechRecognitionEngine",
    "ESpeakTTSEngine",
    "FestivalTTSEngine",
    
    # Cross-platform engines
    "GoogleSpeechRecognitionEngine",
    
    # Availability flags
    "WINDOWS_ENGINES_AVAILABLE",
    "LINUX_ENGINES_AVAILABLE", 
    "GOOGLE_SPEECH_AVAILABLE"
]

__version__ = "1.0.0"
