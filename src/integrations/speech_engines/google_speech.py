"""
Google Speech Recognition Engine for JARVIS Computer Assistant

This module provides Google Speech Recognition integration for both
Windows and Linux platforms.
"""

import platform
import logging
import threading
from typing import List, Optional, Dict, Any

# Google Speech Recognition imports
try:
    import speech_recognition as sr
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError as e:
    GOOGLE_SPEECH_AVAILABLE = False
    print(f"Google Speech Recognition not available: {e}")

from .common_speech import (
    BaseSpeechRecognitionEngine,
    SpeechEngineType, Language, SpeechConfig
)

logger = logging.getLogger(__name__)

class GoogleSpeechRecognitionEngine(BaseSpeechRecognitionEngine):
    """Google Speech Recognition engine for cross-platform use"""
    
    def __init__(self, config: SpeechConfig):
        super().__init__(config)
        self.recognizer = None
        self.microphone = None
        self._lock = threading.Lock()
    
    @property
    def engine_type(self) -> SpeechEngineType:
        return SpeechEngineType.GOOGLE_SPEECH
    
    @property
    def is_available(self) -> bool:
        return GOOGLE_SPEECH_AVAILABLE
    
    def _initialize_engine(self) -> None:
        """Initialize Google Speech Recognition"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Configure recognizer
            self.recognizer.energy_threshold = self.config.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.config.dynamic_energy_threshold
            self.recognizer.pause_threshold = self.config.pause_threshold
            self.recognizer.operation_timeout = self.config.operation_timeout
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            
            self.logger.info("Google Speech Recognition initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Speech Recognition: {e}")
            raise
    
    def recognize_audio(self, audio_data: bytes) -> Optional[str]:
        """Recognize speech from audio data"""
        if not self.recognizer:
            return None
        
        try:
            with self._lock:
                # Convert audio data to AudioData object
                audio = sr.AudioData(audio_data, 44100, 2)
                
                # Recognize using Google Speech Recognition
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.config.language.value
                )
                
                if text:
                    self.logger.debug(f"Recognized text: {text}")
                    return text.strip()
                
                return None
        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition request failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Speech recognition failed: {e}")
            return None
    
    def listen_for_audio(self, timeout: int = None) -> Optional[bytes]:
        """Listen for audio input"""
        if not self.recognizer or not self.microphone:
            return None
        
        try:
            with self._lock:
                with self.microphone as source:
                    # Listen for audio
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout or self.config.timeout,
                        phrase_time_limit=self.config.phrase_timeout
                    )
                    
                    if audio:
                        return audio.get_wav_data()
                    
                    return None
        except sr.WaitTimeoutError:
            self.logger.debug("Listening timeout")
            return None
        except Exception as e:
            self.logger.error(f"Audio listening failed: {e}")
            return None
    
    def adjust_for_ambient_noise(self, duration: float = 1.0) -> None:
        """Adjust for ambient noise"""
        if not self.recognizer or not self.microphone:
            return
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self.logger.info(f"Adjusted for ambient noise (duration: {duration}s)")
        except Exception as e:
            self.logger.error(f"Failed to adjust for ambient noise: {e}")
    
    def get_available_languages(self) -> List[Language]:
        """Get available languages"""
        return [
            Language.TURKISH,
            Language.ENGLISH,
            Language.SPANISH,
            Language.FRENCH,
            Language.GERMAN,
            Language.ITALIAN,
            Language.RUSSIAN,
            Language.CHINESE,
            Language.JAPANESE,
            Language.KOREAN
        ]
    
    def cleanup(self) -> None:
        """Cleanup Google Speech Recognition"""
        with self._lock:
            self.recognizer = None
            self.microphone = None
            self.logger.info("Google Speech Recognition cleaned up")
