"""
Common Speech Interface for JARVIS Computer Assistant

This module provides a common interface for speech recognition and synthesis
across different platforms and engines.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import threading
import asyncio
import time
from pathlib import Path

# Import WakeWordState from enhanced_voice_recognition
try:
    from .enhanced_voice_recognition import WakeWordState
except ImportError:
    # Fallback if enhanced_voice_recognition is not available
    class WakeWordState(Enum):
        LISTENING = "listening"
        DETECTED = "detected"
        PROCESSING = "processing"
        IDLE = "idle"

logger = logging.getLogger(__name__)

class SpeechEngineType(Enum):
    """Supported speech engine types"""
    GOOGLE_SPEECH = "google_speech"
    WINDOWS_SPEECH_PLATFORM = "windows_speech_platform"
    SAPI5 = "sapi5"
    EDGE_TTS = "edge_tts"
    ESPEAK = "espeak"
    FESTIVAL = "festival"
    PYTTSX3 = "pyttsx3"

class Language(Enum):
    """Supported languages"""
    TURKISH = "tr"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"

@dataclass
class VoiceInfo:
    """Voice information"""
    id: str
    name: str
    language: str
    gender: str
    sample_rate: int
    is_default: bool = False

@dataclass
class AudioConfig:
    """Audio configuration"""
    sample_rate: int = 44100
    channels: int = 1
    chunk_size: int = 1024
    format: str = "int16"
    device_index: Optional[int] = None

@dataclass
class SpeechConfig:
    """Speech recognition configuration"""
    language: Language = Language.TURKISH
    engine: SpeechEngineType = SpeechEngineType.GOOGLE_SPEECH
    timeout: int = 5
    phrase_timeout: int = 0.5
    energy_threshold: int = 300
    dynamic_energy_threshold: bool = True
    pause_threshold: float = 0.8
    operation_timeout: Optional[int] = None
    
    # Enhanced voice recognition settings
    use_enhanced_voice: bool = True
    wake_words: List[str] = None
    confidence_threshold: float = 0.7
    noise_reduction: bool = True
    vad_enabled: bool = True
    adaptive_threshold: bool = True
    
    def __post_init__(self):
        if self.wake_words is None:
            self.wake_words = ['jarvis', 'hey jarvis']
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return getattr(self, key, default)

class BaseSpeechEngine(ABC):
    """Base class for speech engines"""
    
    def __init__(self, config: SpeechConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
        self._lock = threading.Lock()
    
    @property
    @abstractmethod
    def engine_type(self) -> SpeechEngineType:
        """Speech engine type"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if engine is available"""
        pass
    
    def initialize(self) -> bool:
        """Initialize the speech engine"""
        if self._initialized:
            return True
        
        try:
            with self._lock:
                self._initialize_engine()
                self._initialized = True
                self.logger.info(f"Speech engine {self.engine_type.value} initialized")
                return True
        except Exception as e:
            self.logger.error(f"Failed to initialize speech engine {self.engine_type.value}: {e}")
            return False
    
    @abstractmethod
    def _initialize_engine(self) -> None:
        """Initialize the specific speech engine"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup speech engine resources"""
        pass

class BaseSpeechRecognitionEngine(BaseSpeechEngine):
    """Base class for speech recognition engines"""
    
    @abstractmethod
    def recognize_audio(self, audio_data: bytes) -> Optional[str]:
        """Recognize speech from audio data"""
        pass
    
    @abstractmethod
    def listen_for_audio(self, timeout: int = None) -> Optional[bytes]:
        """Listen for audio input"""
        pass
    
    @abstractmethod
    def adjust_for_ambient_noise(self, duration: float = 1.0) -> None:
        """Adjust for ambient noise"""
        pass
    
    @abstractmethod
    def get_available_languages(self) -> List[Language]:
        """Get available languages"""
        pass

class BaseTextToSpeechEngine(BaseSpeechEngine):
    """Base class for text-to-speech engines"""
    
    @abstractmethod
    def speak(self, text: str) -> bool:
        """Convert text to speech"""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices"""
        pass
    
    @abstractmethod
    def set_voice(self, voice_id: str) -> bool:
        """Set voice"""
        pass
    
    @abstractmethod
    def set_rate(self, rate: int) -> bool:
        """Set speech rate"""
        pass
    
    @abstractmethod
    def set_volume(self, volume: float) -> bool:
        """Set speech volume"""
        pass

class SpeechManager:
    """Central speech management system"""
    
    def __init__(self, config: SpeechConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._recognition_engine: Optional[BaseSpeechRecognitionEngine] = None
        self._tts_engine: Optional[BaseTextToSpeechEngine] = None
        self._enhanced_recognition: Optional[EnhancedVoiceRecognition] = None
        self._lock = threading.Lock()
        self._use_enhanced = False
    
    def initialize(self) -> bool:
        """Initialize speech manager"""
        try:
            with self._lock:
                # Try to initialize enhanced voice recognition first
                if ENHANCED_VOICE_AVAILABLE and self.config.get('use_enhanced_voice', True):
                    try:
                        self._enhanced_recognition = create_enhanced_voice_recognition(
                            wake_words=self.config.get('wake_words', ['jarvis', 'hey jarvis']),
                            confidence_threshold=self.config.get('confidence_threshold', 0.7),
                            energy_threshold=self.config.get('energy_threshold', 300),
                            noise_reduction=self.config.get('noise_reduction', True),
                            vad_enabled=self.config.get('vad_enabled', True),
                            adaptive_threshold=self.config.get('adaptive_threshold', True)
                        )
                        
                        if self._enhanced_recognition.initialize():
                            self._use_enhanced = True
                            self.logger.info("Enhanced voice recognition initialized")
                        else:
                            self.logger.warning("Enhanced voice recognition failed, falling back to standard")
                            self._enhanced_recognition = None
                            self._use_enhanced = False
                    except Exception as e:
                        self.logger.warning(f"Enhanced voice recognition not available: {e}")
                        self._enhanced_recognition = None
                        self._use_enhanced = False
                
                # Initialize standard recognition engine if enhanced not available
                if not self._use_enhanced:
                    self._recognition_engine = self._create_recognition_engine()
                    if not self._recognition_engine or not self._recognition_engine.initialize():
                        self.logger.error("Failed to initialize recognition engine")
                        return False
                
                # Initialize TTS engine
                self._tts_engine = self._create_tts_engine()
                if not self._tts_engine or not self._tts_engine.initialize():
                    self.logger.error("Failed to initialize TTS engine")
                    return False
                
                self.logger.info("Speech manager initialized successfully")
                return True
        except Exception as e:
            self.logger.error(f"Failed to initialize speech manager: {e}")
            return False
    
    def _create_recognition_engine(self) -> Optional[BaseSpeechRecognitionEngine]:
        """Create recognition engine based on config"""
        try:
            if self.config.engine == SpeechEngineType.GOOGLE_SPEECH:
                from .google_speech import GoogleSpeechRecognitionEngine
                return GoogleSpeechRecognitionEngine(self.config)
            elif self.config.engine == SpeechEngineType.WINDOWS_SPEECH_PLATFORM:
                from .windows_speech import WindowsSpeechRecognitionEngine
                return WindowsSpeechRecognitionEngine(self.config)
            else:
                self.logger.warning(f"Unsupported recognition engine: {self.config.engine}")
                return None
        except ImportError as e:
            self.logger.error(f"Failed to import recognition engine: {e}")
            return None
    
    def _create_tts_engine(self) -> Optional[BaseTextToSpeechEngine]:
        """Create TTS engine based on config"""
        try:
            if self.config.engine == SpeechEngineType.SAPI5:
                from .windows_speech import SAPI5TTSEngine
                return SAPI5TTSEngine(self.config)
            elif self.config.engine == SpeechEngineType.EDGE_TTS:
                from .windows_speech import EdgeTTSEngine
                return EdgeTTSEngine(self.config)
            elif self.config.engine == SpeechEngineType.ESPEAK:
                from .linux_speech import ESpeakTTSEngine
                return ESpeakTTSEngine(self.config)
            elif self.config.engine == SpeechEngineType.FESTIVAL:
                from .linux_speech import FestivalTTSEngine
                return FestivalTTSEngine(self.config)
            else:
                # Default to SAPI5 on Windows, eSpeak on Linux
                import platform
                if platform.system() == "Windows":
                    from .windows_speech import SAPI5TTSEngine
                    return SAPI5TTSEngine(self.config)
                else:
                    from .linux_speech import ESpeakTTSEngine
                    return ESpeakTTSEngine(self.config)
        except ImportError as e:
            self.logger.error(f"Failed to import TTS engine: {e}")
            return None
    
    def recognize_speech(self, timeout: int = None) -> Optional[str]:
        """Recognize speech"""
        if self._use_enhanced and self._enhanced_recognition:
            # Use enhanced voice recognition
            try:
                # Start listening if not already
                if not self._enhanced_recognition.is_listening:
                    self._enhanced_recognition.start_listening()
                
                # Wait for speech detection
                start_time = time.time()
                while time.time() - start_time < (timeout or 10):
                    if self._enhanced_recognition.state == WakeWordState.DETECTED:
                        # Speech detected, wait for processing
                        time.sleep(0.5)
                        if self._enhanced_recognition.state == WakeWordState.LISTENING:
                            # Processing complete, get the result
                            return getattr(self._enhanced_recognition, '_last_speech_text', None)
                    time.sleep(0.1)
                
                return None
            except Exception as e:
                self.logger.error(f"Enhanced speech recognition failed: {e}")
                return None
        else:
            # Use standard recognition
            if not self._recognition_engine:
                self.logger.error("Recognition engine not initialized")
                return None
            
            try:
                return self._recognition_engine.recognize_audio(
                    self._recognition_engine.listen_for_audio(timeout)
                )
            except Exception as e:
                self.logger.error(f"Speech recognition failed: {e}")
                return None
    
    def speak_text(self, text: str) -> bool:
        """Convert text to speech"""
        if not self._tts_engine:
            self.logger.error("TTS engine not initialized")
            return False
        
        try:
            return self._tts_engine.speak(text)
        except Exception as e:
            self.logger.error(f"Text-to-speech failed: {e}")
            return False
    
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices"""
        if not self._tts_engine:
            return []
        
        try:
            return self._tts_engine.get_available_voices()
        except Exception as e:
            self.logger.error(f"Failed to get voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set voice"""
        if not self._tts_engine:
            return False
        
        try:
            return self._tts_engine.set_voice(voice_id)
        except Exception as e:
            self.logger.error(f"Failed to set voice: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup speech manager"""
        with self._lock:
            if self._enhanced_recognition:
                self._enhanced_recognition.cleanup()
                self._enhanced_recognition = None
            
            if self._recognition_engine:
                self._recognition_engine.cleanup()
                self._recognition_engine = None
            
            if self._tts_engine:
                self._tts_engine.cleanup()
                self._tts_engine = None
            
            self.logger.info("Speech manager cleaned up")
    
    def start_enhanced_listening(self) -> bool:
        """Start enhanced voice recognition listening"""
        if self._use_enhanced and self._enhanced_recognition:
            return self._enhanced_recognition.start_listening()
        return False
    
    def stop_enhanced_listening(self) -> None:
        """Stop enhanced voice recognition listening"""
        if self._use_enhanced and self._enhanced_recognition:
            self._enhanced_recognition.stop_listening()
    
    def get_enhanced_metrics(self) -> Dict[str, Any]:
        """Get enhanced voice recognition metrics"""
        if self._use_enhanced and self._enhanced_recognition:
            return self._enhanced_recognition.get_performance_metrics()
        return {}
    
    def set_enhanced_callbacks(self, on_wake_word: Callable = None, on_speech: Callable = None) -> None:
        """Set enhanced voice recognition callbacks"""
        if self._use_enhanced and self._enhanced_recognition:
            self._enhanced_recognition.on_wake_word_detected = on_wake_word
            self._enhanced_recognition.on_speech_detected = on_speech
    
    def cleanup(self) -> None:
        """Cleanup speech manager and all resources"""
        try:
            with self._lock:
                self.logger.info("Cleaning up speech manager...")
                
                # Stop enhanced recognition
                if self._enhanced_recognition:
                    try:
                        self._enhanced_recognition.stop_listening()
                        self._enhanced_recognition = None
                    except Exception as e:
                        self.logger.warning(f"Error cleaning up enhanced recognition: {e}")
                
                # Cleanup recognition engine
                if self._recognition_engine:
                    try:
                        if hasattr(self._recognition_engine, 'cleanup'):
                            self._recognition_engine.cleanup()
                        self._recognition_engine = None
                    except Exception as e:
                        self.logger.warning(f"Error cleaning up recognition engine: {e}")
                
                # Cleanup TTS engine
                if self._tts_engine:
                    try:
                        if hasattr(self._tts_engine, 'cleanup'):
                            self._tts_engine.cleanup()
                        self._tts_engine = None
                    except Exception as e:
                        self.logger.warning(f"Error cleaning up TTS engine: {e}")
                
                self.logger.info("Speech manager cleanup completed")
                
        except Exception as e:
            self.logger.error(f"Error during speech manager cleanup: {e}")

class WakeWordDetector:
    """Wake word detection system"""
    
    def __init__(self, wake_words: List[str] = None):
        self.wake_words = wake_words or ["jarvis", "hey jarvis", "ok jarvis"]
        self.logger = logging.getLogger(__name__)
        self._is_listening = False
        self._lock = threading.Lock()
    
    def is_wake_word(self, text: str) -> bool:
        """Check if text contains wake word"""
        if not text:
            return False
        
        text_lower = text.lower().strip()
        for wake_word in self.wake_words:
            if wake_word.lower() in text_lower:
                self.logger.info(f"Wake word detected: {wake_word}")
                return True
        
        return False
    
    def extract_command(self, text: str) -> str:
        """Extract command from text after wake word"""
        if not text:
            return ""
        
        text_lower = text.lower().strip()
        for wake_word in self.wake_words:
            if wake_word.lower() in text_lower:
                # Remove wake word and clean up
                command = text_lower.replace(wake_word.lower(), "").strip()
                return command
        
        return text_lower

class VoiceCommandProcessor:
    """Voice command processing system"""
    
    def __init__(self, speech_manager: SpeechManager, wake_word_detector: WakeWordDetector):
        self.speech_manager = speech_manager
        self.wake_word_detector = wake_word_detector
        self.logger = logging.getLogger(__name__)
        self._is_processing = False
        self._lock = threading.Lock()
    
    def process_voice_input(self, text: str) -> Optional[str]:
        """Process voice input and return command"""
        if not text:
            return None
        
        # Check for wake word
        if self.wake_word_detector.is_wake_word(text):
            command = self.wake_word_detector.extract_command(text)
            if command:
                self.logger.info(f"Command extracted: {command}")
                return command
        
        return None
    
    def listen_for_command(self, timeout: int = 5) -> Optional[str]:
        """Listen for voice command"""
        try:
            with self._lock:
                self._is_processing = True
                
                # Recognize speech
                text = self.speech_manager.recognize_speech(timeout)
                if not text:
                    return None
                
                # Process command
                return self.process_voice_input(text)
        
        except Exception as e:
            self.logger.error(f"Voice command processing failed: {e}")
            return None
        finally:
            with self._lock:
                self._is_processing = False

# Global speech manager instance
_speech_manager: Optional[SpeechManager] = None

def get_speech_manager() -> SpeechManager:
    """Get global speech manager instance"""
    global _speech_manager
    if _speech_manager is None:
        # Create default config
        from dataclasses import dataclass
        
        config = SpeechConfig()
        _speech_manager = SpeechManager(config)
    return _speech_manager

def cleanup_speech_manager() -> None:
    """Cleanup global speech manager instance"""
    global _speech_manager
    if _speech_manager:
        _speech_manager.cleanup()
        _speech_manager = None

# Enhanced Voice Recognition imports
try:
    from .enhanced_voice_recognition import EnhancedVoiceRecognition, create_enhanced_voice_recognition
    ENHANCED_VOICE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhanced voice recognition not available: {e}")
    ENHANCED_VOICE_AVAILABLE = False
