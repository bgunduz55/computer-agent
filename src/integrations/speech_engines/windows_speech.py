"""
Windows Speech Recognition Engine for JARVIS Computer Assistant

This module provides Windows-specific speech recognition using Windows Speech Platform
and SAPI5 for text-to-speech.
"""

import platform
import logging
import threading
import time
from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
import asyncio

# Windows-specific imports
try:
    import win32com.client
    import pyttsx3
    import speech_recognition as sr
    from gtts import gTTS
    import edge_tts
    import winsound
    WINDOWS_AVAILABLE = True
except ImportError as e:
    WINDOWS_AVAILABLE = False
    print(f"Windows speech modules not available: {e}")

from .common_speech import (
    BaseSpeechRecognitionEngine, BaseTextToSpeechEngine, 
    SpeechEngineType, Language, VoiceInfo, SpeechConfig
)

logger = logging.getLogger(__name__)

class WindowsSpeechRecognitionEngine(BaseSpeechRecognitionEngine):
    """Windows Speech Platform recognition engine"""
    
    def __init__(self, config: SpeechConfig):
        super().__init__(config)
        self.recognizer = None
        self.microphone = None
        self._lock = threading.Lock()
    
    @property
    def engine_type(self) -> SpeechEngineType:
        return SpeechEngineType.WINDOWS_SPEECH_PLATFORM
    
    @property
    def is_available(self) -> bool:
        return WINDOWS_AVAILABLE and platform.system() == "Windows"
    
    def _initialize_engine(self) -> None:
        """Initialize Windows Speech Platform"""
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
            
            self.logger.info("Windows Speech Platform initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Windows Speech Platform: {e}")
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
        """Cleanup Windows Speech Platform"""
        with self._lock:
            self.recognizer = None
            self.microphone = None
            self.logger.info("Windows Speech Platform cleaned up")

class SAPI5TTSEngine(BaseTextToSpeechEngine):
    """SAPI5 Text-to-Speech engine"""
    
    def __init__(self, config: SpeechConfig):
        super().__init__(config)
        self.engine = None
        self._lock = threading.Lock()
    
    @property
    def engine_type(self) -> SpeechEngineType:
        return SpeechEngineType.SAPI5
    
    @property
    def is_available(self) -> bool:
        return WINDOWS_AVAILABLE and platform.system() == "Windows"
    
    def _initialize_engine(self) -> None:
        """Initialize SAPI5 TTS engine"""
        try:
            self.engine = pyttsx3.init(driverName='sapi5')
            
            # Configure engine
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            
            # Set voice based on language with proper error handling
            voices = self.engine.getProperty('voices')
            if voices:
                # Get language string safely
                language_str = None
                if hasattr(self.config, 'language'):
                    if hasattr(self.config.language, 'value'):
                        language_str = self.config.language.value
                    else:
                        language_str = str(self.config.language)
                else:
                    language_str = "en"  # Default to English
                
                # Find matching voice
                for voice in voices:
                    try:
                        # Check if voice has languages attribute and it contains our language
                        if hasattr(voice, 'languages') and voice.languages:
                            if language_str in voice.languages or language_str in voice.id.lower():
                                self.engine.setProperty('voice', voice.id)
                                self.logger.info(f"Voice selected: {voice.id}")
                                break
                        elif language_str in voice.id.lower():
                            self.engine.setProperty('voice', voice.id)
                            self.logger.info(f"Voice selected: {voice.id}")
                            break
                    except Exception as e:
                        self.logger.warning(f"Error checking voice {voice.id}: {e}")
                        continue
            
            self.logger.info("SAPI5 TTS engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize SAPI5 TTS: {e}")
            raise
    
    def speak(self, text: str) -> bool:
        """Convert text to speech"""
        if not self.engine:
            return False
        
        try:
            with self._lock:
                self.logger.debug(f"Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                return True
        except Exception as e:
            self.logger.error(f"SAPI5 TTS failed: {e}")
            return False
    
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices"""
        if not self.engine:
            return []
        
        try:
            voices = []
            engine_voices = self.engine.getProperty('voices')
            
            for voice in engine_voices:
                voices.append(VoiceInfo(
                    id=voice.id,
                    name=voice.name,
                    language=voice.languages[0] if voice.languages else "en",
                    gender="male" if "male" in voice.name.lower() else "female",
                    sample_rate=22050,  # Default SAPI5 sample rate
                    is_default=len(voices) == 0
                ))
            
            return voices
        except Exception as e:
            self.logger.error(f"Failed to get voices: {e}")
            return []
    
    def set_voice(self, voice_id: str) -> bool:
        """Set voice"""
        if not self.engine:
            return False
        
        try:
            with self._lock:
                self.engine.setProperty('voice', voice_id)
                self.logger.info(f"Voice set to: {voice_id}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to set voice: {e}")
            return False
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate"""
        if not self.engine:
            return False
        
        try:
            with self._lock:
                self.engine.setProperty('rate', rate)
                self.logger.info(f"Speech rate set to: {rate}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to set rate: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume"""
        if not self.engine:
            return False
        
        try:
            with self._lock:
                self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
                self.logger.info(f"Speech volume set to: {volume}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to set volume: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup SAPI5 TTS engine"""
        with self._lock:
            self.engine = None
            self.logger.info("SAPI5 TTS engine cleaned up")

class EdgeTTSEngine(BaseTextToSpeechEngine):
    """Microsoft Edge TTS engine"""
    
    def __init__(self, config: SpeechConfig):
        super().__init__(config)
        self.temp_dir = Path(tempfile.gettempdir()) / "tts_cache"
        self.temp_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        
        # Voice mapping
        self.voice_mapping = {
            Language.TURKISH: "tr-TR-AhmetNeural",
            Language.ENGLISH: "en-US-ChristopherNeural",
            Language.SPANISH: "es-ES-AlvaroNeural",
            Language.FRENCH: "fr-FR-DeniseNeural",
            Language.GERMAN: "de-DE-KasperNeural",
            Language.ITALIAN: "it-IT-DiegoNeural",
            Language.RUSSIAN: "ru-RU-DmitryNeural",
            Language.CHINESE: "zh-CN-YunxiNeural",
            Language.JAPANESE: "ja-JP-KeitaNeural",
            Language.KOREAN: "ko-KR-InJoonNeural"
        }
    
    @property
    def engine_type(self) -> SpeechEngineType:
        return SpeechEngineType.EDGE_TTS
    
    @property
    def is_available(self) -> bool:
        return WINDOWS_AVAILABLE and platform.system() == "Windows"
    
    def _initialize_engine(self) -> None:
        """Initialize Edge TTS engine"""
        try:
            self.logger.info("Edge TTS engine initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Edge TTS: {e}")
            raise
    
    async def _generate_speech(self, text: str, output_file: str) -> None:
        """Generate speech using Edge TTS"""
        try:
            # Get language string safely
            language_str = None
            if hasattr(self.config, 'language'):
                if hasattr(self.config.language, 'value'):
                    language_str = self.config.language.value
                else:
                    language_str = str(self.config.language)
            else:
                language_str = "en"  # Default to English
            
            # Map language to voice with fallback
            voice = self.voice_mapping.get(language_str, "en-US-ChristopherNeural")
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
        except Exception as e:
            self.logger.error(f"Edge TTS generation failed: {e}")
            raise
    
    def speak(self, text: str) -> bool:
        """Convert text to speech"""
        try:
            with self._lock:
                # Create temp file
                temp_file = self.temp_dir / f"speech_{hash(text)}.wav"
                
                # Generate speech if not cached
                if not temp_file.exists():
                    asyncio.run(self._generate_speech(text, str(temp_file)))
                
                # Play audio
                winsound.PlaySound(str(temp_file), winsound.SND_FILENAME)
                return True
        except Exception as e:
            self.logger.error(f"Edge TTS failed: {e}")
            return False
    
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get available voices"""
        voices = []
        for language, voice_id in self.voice_mapping.items():
            voices.append(VoiceInfo(
                id=voice_id,
                name=voice_id,
                language=language.value,
                gender="male" if "Neural" in voice_id else "female",
                sample_rate=24000,  # Edge TTS sample rate
                is_default=language == self.config.language
            ))
        return voices
    
    def set_voice(self, voice_id: str) -> bool:
        """Set voice"""
        # Edge TTS voice is set during speech generation
        return True
    
    def set_rate(self, rate: int) -> bool:
        """Set speech rate (not supported by Edge TTS)"""
        return False
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume (not supported by Edge TTS)"""
        return False
    
    def cleanup(self) -> None:
        """Cleanup Edge TTS engine"""
        with self._lock:
            # Clean up temp files
            try:
                for file in self.temp_dir.glob("speech_*.wav"):
                    file.unlink()
            except Exception as e:
                self.logger.error(f"Failed to clean up temp files: {e}")
            
            self.logger.info("Edge TTS engine cleaned up")
