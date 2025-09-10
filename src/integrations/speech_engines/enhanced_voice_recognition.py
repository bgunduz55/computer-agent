"""
Enhanced Voice Recognition System
Windows+H level intelligent listening with noise filtering and smart wake word detection
"""

import asyncio
import logging
import numpy as np
import threading
import time
import wave
import io
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import pyaudio
import speech_recognition as sr
from scipy import signal
from scipy.io import wavfile
import noisereduce as nr
from collections import deque
import queue

try:
    import webrtcvad
    WEBRTC_VAD_AVAILABLE = True
except ImportError:
    WEBRTC_VAD_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

logger = logging.getLogger(__name__)

class WakeWordState(Enum):
    """Wake word detection states"""
    LISTENING = "listening"
    DETECTED = "detected"
    PROCESSING = "processing"
    IDLE = "idle"

@dataclass
class AudioQualityMetrics:
    """Audio quality metrics"""
    snr_db: float
    noise_level: float
    speech_energy: float
    background_noise: float
    clarity_score: float
    is_clear: bool

@dataclass
class WakeWordConfig:
    """Wake word detection configuration"""
    wake_words: List[str]
    confidence_threshold: float
    energy_threshold: int
    pause_threshold: float
    phrase_threshold: float
    non_speaking_duration: float
    timeout: float
    dynamic_energy_threshold: bool
    noise_reduction: bool
    vad_enabled: bool
    adaptive_threshold: bool

class EnhancedVoiceRecognition:
    """Enhanced voice recognition with Windows+H level intelligence"""
    
    def __init__(self, config: WakeWordConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Audio processing
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 16000
        self.chunk_size = 1024
        
        # State management
        self.state = WakeWordState.IDLE
        self.is_listening = False
        self.is_processing = False
        
        # Audio buffers
        self.audio_buffer = deque(maxlen=int(self.sample_rate * 10))  # 10 seconds
        self.speech_buffer = deque(maxlen=int(self.sample_rate * 5))   # 5 seconds
        
        # Quality metrics
        self.quality_metrics = AudioQualityMetrics(0, 0, 0, 0, 0, False)
        self.adaptive_threshold = config.energy_threshold
        
        # Noise reduction
        self.noise_profile = None
        self.noise_samples = deque(maxlen=int(self.sample_rate * 2))  # 2 seconds
        
        # VAD (Voice Activity Detection)
        self.vad = None
        if WEBRTC_VAD_AVAILABLE:
            self.vad = webrtcvad.Vad(2)  # Aggressiveness level 2
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Callbacks
        self.on_wake_word_detected: Optional[Callable] = None
        self.on_speech_detected: Optional[Callable] = None
        self.on_audio_quality_changed: Optional[Callable] = None
        
        # Threading
        self.listen_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Performance tracking
        self.detection_times = deque(maxlen=100)
        self.false_positives = 0
        self.true_positives = 0
        
    def initialize(self) -> bool:
        """Initialize enhanced voice recognition"""
        try:
            # Initialize microphone
            self.microphone = sr.Microphone(sample_rate=self.sample_rate)
            
            # Configure recognizer
            self.recognizer.energy_threshold = self.adaptive_threshold
            self.recognizer.dynamic_energy_threshold = self.config.dynamic_energy_threshold
            self.recognizer.pause_threshold = self.config.pause_threshold
            self.recognizer.phrase_threshold = self.config.phrase_threshold
            self.recognizer.non_speaking_duration = self.config.non_speaking_duration
            self.recognizer.timeout = self.config.timeout
            
            # Calibrate for ambient noise
            self._calibrate_ambient_noise()
            
            self.logger.info("Enhanced voice recognition initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced voice recognition: {e}")
            return False
    
    def start_listening(self) -> bool:
        """Start continuous listening for wake words"""
        if self.is_listening:
            return True
            
        try:
            self.is_listening = True
            self.state = WakeWordState.LISTENING
            self.stop_event.clear()
            
            # Start listening thread
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            
            self.logger.info("Enhanced voice recognition started listening")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
            return False
    
    def stop_listening(self) -> None:
        """Stop continuous listening"""
        self.is_listening = False
        self.state = WakeWordState.IDLE
        self.stop_event.set()
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        
        self.logger.info("Enhanced voice recognition stopped listening")
    
    def cleanup(self) -> None:
        """Cleanup enhanced voice recognition resources"""
        try:
            self.logger.info("Cleaning up enhanced voice recognition...")
            
            # Stop listening first
            self.stop_listening()
            
            # Clear audio buffers
            self.audio_buffer.clear()
            self.speech_buffer.clear()
            self.noise_samples.clear()
            
            # Reset state
            self.state = WakeWordState.IDLE
            self.is_processing = False
            
            # Clear callbacks
            self.on_wake_word_detected = None
            self.on_speech_detected = None
            self.on_audio_quality_changed = None
            
            # Clear performance tracking
            self.detection_times.clear()
            self.false_positives = 0
            self.true_positives = 0
            
            # Reset quality metrics
            self.quality_metrics = AudioQualityMetrics(0, 0, 0, 0, 0, False)
            
            self.logger.info("Enhanced voice recognition cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during enhanced voice recognition cleanup: {e}")
    
    def _listen_loop(self) -> None:
        """Main listening loop"""
        while self.is_listening and not self.stop_event.is_set():
            try:
                # Listen for audio
                with self.microphone as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=5.0)
                    
                    # Process audio
                    self._process_audio(audio)
                    
            except sr.WaitTimeoutError:
                # No audio detected, continue listening
                continue
            except Exception as e:
                self.logger.error(f"Error in listening loop: {e}")
                time.sleep(0.1)
    
    def _process_audio(self, audio: sr.AudioData) -> None:
        """Process audio for wake word detection and speech recognition"""
        try:
            # Convert to numpy array
            audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)
            
            # Apply noise reduction if enabled
            if self.config.noise_reduction:
                audio_data = self._apply_noise_reduction(audio_data)
            
            # Calculate audio quality metrics
            self._calculate_quality_metrics(audio_data)
            
            # Check if audio quality is sufficient
            if not self.quality_metrics.is_clear:
                self.logger.debug("Audio quality too low, skipping")
                return
            
            # Voice Activity Detection
            if self.config.vad_enabled and self.vad:
                if not self._is_speech(audio_data):
                    return
            
            # Wake word detection
            if self._detect_wake_word(audio_data):
                self._handle_wake_word_detected(audio_data)
            
            # Speech recognition
            if self.state == WakeWordState.DETECTED:
                self._recognize_speech(audio)
                
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
    
    def _apply_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply noise reduction to audio data"""
        try:
            # Update noise profile
            if len(self.noise_samples) < self.sample_rate:
                self.noise_samples.extend(audio_data)
                return audio_data
            
            # Apply noise reduction
            if self.noise_profile is None:
                self.noise_profile = np.array(self.noise_samples)
            
            # Use noisereduce library
            reduced_audio = nr.reduce_noise(
                y=audio_data.astype(np.float32),
                sr=self.sample_rate,
                y_noise=self.noise_profile.astype(np.float32)
            )
            
            return reduced_audio.astype(np.int16)
            
        except Exception as e:
            self.logger.error(f"Error applying noise reduction: {e}")
            return audio_data
    
    def _calculate_quality_metrics(self, audio_data: np.ndarray) -> None:
        """Calculate audio quality metrics"""
        try:
            # Convert to float for processing
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Calculate signal energy
            signal_energy = np.mean(audio_float ** 2)
            
            # Estimate background noise (using quiet parts)
            quiet_threshold = np.percentile(np.abs(audio_float), 20)
            quiet_samples = audio_float[np.abs(audio_float) < quiet_threshold]
            background_noise = np.mean(quiet_samples ** 2) if len(quiet_samples) > 0 else 0
            
            # Calculate SNR
            if background_noise > 0:
                snr_db = 10 * np.log10(signal_energy / background_noise)
            else:
                snr_db = 50  # High SNR if no background noise
            
            # Calculate clarity score (0-1)
            clarity_score = min(1.0, max(0.0, (snr_db - 10) / 30))
            
            # Update metrics
            self.quality_metrics = AudioQualityMetrics(
                snr_db=snr_db,
                noise_level=background_noise,
                speech_energy=signal_energy,
                background_noise=background_noise,
                clarity_score=clarity_score,
                is_clear=clarity_score > 0.3 and snr_db > 15
            )
            
            # Adaptive threshold adjustment
            if self.config.adaptive_threshold:
                self._adjust_energy_threshold()
            
        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {e}")
    
    def _adjust_energy_threshold(self) -> None:
        """Adjust energy threshold based on ambient noise"""
        try:
            # Calculate new threshold based on background noise
            noise_level = self.quality_metrics.background_noise
            new_threshold = int(noise_level * 32768 * 2)  # Convert to int16 range
            
            # Smooth threshold changes
            self.adaptive_threshold = int(0.7 * self.adaptive_threshold + 0.3 * new_threshold)
            
            # Update recognizer
            self.recognizer.energy_threshold = self.adaptive_threshold
            
        except Exception as e:
            self.logger.error(f"Error adjusting energy threshold: {e}")
    
    def _is_speech(self, audio_data: np.ndarray) -> bool:
        """Check if audio contains speech using VAD"""
        try:
            if not self.vad:
                return True
            
            # Convert to 16kHz, 16-bit PCM
            if len(audio_data) < 160:  # Need at least 10ms at 16kHz
                return False
            
            # Pad or truncate to 10ms chunks
            chunk_size = 160  # 10ms at 16kHz
            if len(audio_data) < chunk_size:
                audio_data = np.pad(audio_data, (0, chunk_size - len(audio_data)))
            elif len(audio_data) > chunk_size:
                audio_data = audio_data[:chunk_size]
            
            # Convert to bytes
            audio_bytes = audio_data.astype(np.int16).tobytes()
            
            # Check if speech
            return self.vad.is_speech(audio_bytes, self.sample_rate)
            
        except Exception as e:
            self.logger.error(f"Error in VAD: {e}")
            return True
    
    def _detect_wake_word(self, audio_data: np.ndarray) -> bool:
        """Detect wake words in audio data"""
        try:
            # Convert to AudioData for recognition
            audio_bytes = audio_data.astype(np.int16).tobytes()
            audio_data_obj = sr.AudioData(audio_bytes, self.sample_rate, 2)
            
            # Try to recognize speech
            try:
                text = self.recognizer.recognize_google(
                    audio_data_obj,
                    language="en-US",
                    show_all=False
                ).lower()
                
                # Check for wake words
                for wake_word in self.config.wake_words:
                    if wake_word.lower() in text:
                        self.logger.info(f"Wake word detected: '{wake_word}' in '{text}'")
                        return True
                
            except sr.UnknownValueError:
                # No speech detected
                pass
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition error: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error detecting wake word: {e}")
            return False
    
    def _handle_wake_word_detected(self, audio_data: np.ndarray) -> None:
        """Handle wake word detection"""
        try:
            self.state = WakeWordState.DETECTED
            self.true_positives += 1
            
            # Record detection time
            self.detection_times.append(time.time())
            
            # Call callback
            if self.on_wake_word_detected:
                self.on_wake_word_detected(audio_data)
            
            self.logger.info("Wake word detected, ready for command")
            
        except Exception as e:
            self.logger.error(f"Error handling wake word detection: {e}")
    
    def _recognize_speech(self, audio: sr.AudioData) -> None:
        """Recognize speech after wake word detection"""
        try:
            self.state = WakeWordState.PROCESSING
            
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio, language="en-US")
                
                if text:
                    self.logger.info(f"Speech recognized: '{text}'")
                    
                    # Call callback
                    if self.on_speech_detected:
                        self.on_speech_detected(text)
                
            except sr.UnknownValueError:
                self.logger.debug("Could not understand audio")
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition error: {e}")
            
            # Reset state
            self.state = WakeWordState.LISTENING
            
        except Exception as e:
            self.logger.error(f"Error recognizing speech: {e}")
            self.state = WakeWordState.LISTENING
    
    def _calibrate_ambient_noise(self) -> None:
        """Calibrate for ambient noise"""
        try:
            with self.microphone as source:
                self.logger.info("Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2.0)
                self.logger.info("Ambient noise calibration complete")
                
        except Exception as e:
            self.logger.error(f"Error calibrating ambient noise: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            total_detections = self.true_positives + self.false_positives
            accuracy = self.true_positives / total_detections if total_detections > 0 else 0
            
            avg_detection_time = np.mean(self.detection_times) if self.detection_times else 0
            
            return {
                "accuracy": accuracy,
                "true_positives": self.true_positives,
                "false_positives": self.false_positives,
                "total_detections": total_detections,
                "average_detection_time": avg_detection_time,
                "current_threshold": self.adaptive_threshold,
                "quality_metrics": {
                    "snr_db": self.quality_metrics.snr_db,
                    "clarity_score": self.quality_metrics.clarity_score,
                    "is_clear": self.quality_metrics.is_clear
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {}
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            self.stop_listening()
            
            # Clear buffers
            self.audio_buffer.clear()
            self.speech_buffer.clear()
            self.noise_samples.clear()
            self.detection_times.clear()
            
            self.logger.info("Enhanced voice recognition cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


# Factory function
def create_enhanced_voice_recognition(
    wake_words: List[str] = None,
    confidence_threshold: float = 0.7,
    energy_threshold: int = 300,
    noise_reduction: bool = True,
    vad_enabled: bool = True,
    adaptive_threshold: bool = True
) -> EnhancedVoiceRecognition:
    """Create enhanced voice recognition instance"""
    
    if wake_words is None:
        wake_words = ["jarvis", "hey jarvis", "ok jarvis", "computer"]
    
    config = WakeWordConfig(
        wake_words=wake_words,
        confidence_threshold=confidence_threshold,
        energy_threshold=energy_threshold,
        pause_threshold=0.8,
        phrase_threshold=0.3,
        non_speaking_duration=0.5,
        timeout=5.0,
        dynamic_energy_threshold=True,
        noise_reduction=noise_reduction,
        vad_enabled=vad_enabled,
        adaptive_threshold=adaptive_threshold
    )
    
    return EnhancedVoiceRecognition(config)
