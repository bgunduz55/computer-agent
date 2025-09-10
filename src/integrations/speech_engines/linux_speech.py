"""
Linux Speech Recognition Engine for JARVIS Computer Assistant

This module provides Linux-specific speech recognition and text-to-speech
using eSpeak, Festival, and other Linux speech engines.
"""

import platform
import logging
import threading
import subprocess
import tempfile
from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil

# Linux-specific imports
try:
    import speech_recognition as sr
    import pyaudio
    LINUX_AVAILABLE = True
except ImportError as e:
    LINUX_AVAILABLE = False
    print(f"Linux speech modules not available: {e}")

from .common_speech import (
    BaseSpeechRecognitionEngine, BaseTextToSpeechEngine,
    SpeechEngineType, Language, VoiceInfo, SpeechConfig
)

logger = logging.getLogger(__name__)

class LinuxSpeechRecognitionEngine(BaseSpeechRecognitionEngine):
    """Linux speech recognition engine using Google Speech Recognition"""
    
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
        return LINUX_AVAILABLE and platform.system() == "Linux"
    
    def _initialize_engine(self) -> None:
        """Initialize Linux speech recognition"""
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
            
            self.logger.info("Linux speech recognition initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Linux speech recognition: {e}")
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
        """Cleanup Linux speech recognition"""
        with self._lock:
            self.recognizer = None
            self.microphone = None
            self.logger.info("Linux speech recognition cleaned up")

class ESpeakTTSEngine(BaseTextToSpeechEngine):
    """eSpeak Text-to-Speech engine for Linux"""
    
    def __init__(self, config: SpeechConfig):
        super().__init__(config)
        self.temp_dir = Path(tempfile.gettempdir()) / "tts_cache"
        self.temp_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        
        # Language mapping
        self.language_mapping = {
            Language.TURKISH: "tr",
            Language.ENGLISH: "en",
            Language.SPANISH: "es",
            Language.FRENCH: "fr",
            Language.GERMAN: "de",
            Language.ITALIAN: "it",
            Language.RUSSIAN: "ru",
            Language.CHINESE: "zh",
            Language.JAPANESE: "ja",
            Language.KOREAN: "ko"
        }
    
    @property
    def engine_type(self) -> SpeechEngineType:
        return SpeechEngineType.ESPEAK
    
    @property
    def is_available(self) -> bool:
        return shutil.which("espeak") is not None and platform.system() == "Linux"
    
    def _initialize_engine(self) -> None:
        """Initialize eSpeak TTS engine"""
        try:
            if not self.is_available:
                raise RuntimeError("eSpeak not available")
            
            self.logger.info("eSpeak TTS engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize eSpeak TTS: {e}")
            raise
    
    def speak(self, text: str) -> bool:
        """Convert text to speech using eSpeak"""
        try:
            with self._lock:
                # Create temp file
                temp_file = self.temp_dir / f"speech_{hash(text)}.wav"
                
                # Generate speech if not cached
                if not temp_file.exists():
                    language = self.language_mapping.get(self.config.language, "en")
                    cmd = [
                        "espeak",
                        "-s", "150",  # Speed
                        "-v", language,  # Voice
                        "-w", str(temp_file),  # Output file
                        text
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        self.logger.error(f"eSpeak failed: {result.stderr}")
                        return False
                
                # Play audio using aplay or paplay
                play_cmd = None
                if shutil.which("paplay"):
                    play_cmd = ["paplay", str(temp_file)]
                elif shutil.which("aplay"):
                    play_cmd = ["aplay", str(temp_file)]
                else:
                    self.logger.error("No audio player available")
                    return False
                
                result = subprocess.run(play_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Audio playback failed: {result.stderr}")
                    return False
                
                return True
        except Exception as e:
            self.logger.error(f"eSpeak TTS failed: {e}")
            return False
    
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices"""
        voices = []
        for language, lang_code in self.language_mapping.items():
            voices.append(VoiceInfo(
                id=lang_code,
                name=f"eSpeak {language.value.upper()}",
                language=language.value,
                gender="male",  # eSpeak default
                sample_rate=22050,  # eSpeak default
                is_default=language == self.config.language
            ))
        return voices
    
    def set_voice(self, voice_id: str) -> bool:
        """Set voice (language)"""
        # eSpeak voice is set during speech generation
        return True
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate"""
        # eSpeak rate is set during speech generation
        return True
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume (not supported by eSpeak)"""
        return False
    
    def cleanup(self) -> None:
        """Cleanup eSpeak TTS engine"""
        with self._lock:
            # Clean up temp files
            try:
                for file in self.temp_dir.glob("speech_*.wav"):
                    file.unlink()
            except Exception as e:
                self.logger.error(f"Failed to clean up temp files: {e}")
            
            self.logger.info("eSpeak TTS engine cleaned up")

class FestivalTTSEngine(BaseTextToSpeechEngine):
    """Festival Text-to-Speech engine for Linux"""
    
    def __init__(self, config: SpeechConfig):
        super().__init__(config)
        self.temp_dir = Path(tempfile.gettempdir()) / "tts_cache"
        self.temp_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
    
    @property
    def engine_type(self) -> SpeechEngineType:
        return SpeechEngineType.FESTIVAL
    
    @property
    def is_available(self) -> bool:
        return shutil.which("festival") is not None and platform.system() == "Linux"
    
    def _initialize_engine(self) -> None:
        """Initialize Festival TTS engine"""
        try:
            if not self.is_available:
                raise RuntimeError("Festival not available")
            
            self.logger.info("Festival TTS engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Festival TTS: {e}")
            raise
    
    def speak(self, text: str) -> bool:
        """Convert text to speech using Festival"""
        try:
            with self._lock:
                # Create temp file
                temp_file = self.temp_dir / f"speech_{hash(text)}.wav"
                
                # Generate speech if not cached
                if not temp_file.exists():
                    cmd = [
                        "festival",
                        "--tts",
                        "--pipe"
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        input=text,
                        text=True,
                        capture_output=True
                    )
                    
                    if result.returncode != 0:
                        self.logger.error(f"Festival failed: {result.stderr}")
                        return False
                
                # Play audio using aplay or paplay
                play_cmd = None
                if shutil.which("paplay"):
                    play_cmd = ["paplay", str(temp_file)]
                elif shutil.which("aplay"):
                    play_cmd = ["aplay", str(temp_file)]
                else:
                    self.logger.error("No audio player available")
                    return False
                
                result = subprocess.run(play_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.error(f"Audio playback failed: {result.stderr}")
                    return False
                
                return True
        except Exception as e:
            self.logger.error(f"Festival TTS failed: {e}")
            return False
    
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices"""
        voices = []
        # Festival voices are complex to enumerate, so we provide basic ones
        voices.append(VoiceInfo(
            id="default",
            name="Festival Default",
            language="en",
            gender="male",
            sample_rate=16000,  # Festival default
            is_default=True
        ))
        return voices
    
    def set_voice(self, voice_id: str) -> bool:
        """Set voice (not easily supported by Festival)"""
        return True
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate (not easily supported by Festival)"""
        return True
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume (not supported by Festival)"""
        return False
    
    def cleanup(self) -> None:
        """Cleanup Festival TTS engine"""
        with self._lock:
            # Clean up temp files
            try:
                for file in self.temp_dir.glob("speech_*.wav"):
                    file.unlink()
            except Exception as e:
                self.logger.error(f"Failed to clean up temp files: {e}")
            
            self.logger.info("Festival TTS engine cleaned up")
