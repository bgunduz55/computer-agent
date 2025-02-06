import threading
from PyQt6.QtCore import QObject, pyqtSignal
import speech_recognition as sr
from gtts import gTTS
import edge_tts
import asyncio
import pyttsx3
from config_manager import ConfigManager
from language_manager import LanguageManager
import os
import tempfile
from pathlib import Path
import wave
import time
import logging
import platform
import winsound  # Windows için ses çalma

# Loglama ayarları
log_dir = Path("data/logs")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "voice.log"

# Root logger ayarları
logger = logging.getLogger("AICodeEditor")
logger.setLevel(logging.DEBUG)

# Dosya handler
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Konsol handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)

# Handler'ları ekle
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class TTSEngine:
    """Soyut TTS motor sınıfı"""
    def speak(self, text: str):
        raise NotImplementedError

class WindowsTTSEngine(TTSEngine):
    """Windows için özel TTS motoru"""
    def __init__(self, language="tr"):
        self.logger = logger.getChild("TTS.Windows")
        try:
            self.engine = pyttsx3.init(driverName='sapi5')
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            self._lock = threading.Lock()
            
            # Dile göre ses seç
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if language in voice.languages or language in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    self.logger.info(f"Ses seçildi: {voice.id}")
                    break
        except Exception as e:
            self.logger.error(f"Windows TTS başlatma hatası: {str(e)}")
            raise
                
    def speak(self, text: str):
        try:
            with self._lock:
                self.logger.debug(f"Metin seslendiriliyor: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Windows TTS hatası: {str(e)}")
            print(f"🔊 {text}")

class EdgeTTSEngine(TTSEngine):
    """Microsoft Edge TTS motoru"""
    def __init__(self, language="tr"):
        self.logger = logger.getChild("TTS.Edge")
        self.language = language
        self.temp_dir = Path(tempfile.gettempdir()) / "tts_cache"
        self.temp_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        
        # Dil koduna göre ses seç
        self.voice = {
            "tr": "tr-TR-AhmetNeural",    # Erkek ses
            "tr-f": "tr-TR-EmelNeural",   # Kadın ses
            "en": "en-US-ChristopherNeural",
            "en-f": "en-US-JennyNeural"
        }.get(language, "tr-TR-AhmetNeural")
        
    async def _generate_speech(self, text: str, output_file: str):
        """Metni sese çevir"""
        try:
            self.logger.debug(f"Edge TTS ile ses üretiliyor: {text}")
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_file)
        except Exception as e:
            self.logger.error(f"Edge TTS ses üretme hatası: {str(e)}")
            raise
        
    def speak(self, text: str):
        try:
            with self._lock:
                # Geçici ses dosyası oluştur
                temp_file = self.temp_dir / f"speech_{hash(text)}.wav"
                
                # Eğer aynı metin daha önce sentezlenmişse, önbelleği kullan
                if not temp_file.exists():
                    try:
                        asyncio.run(self._generate_speech(text, str(temp_file)))
                    except Exception as e:
                        self.logger.error(f"Edge TTS hatası: {str(e)}")
                        raise
                
                try:
                    # Windows'ta winsound ile çal
                    self.logger.debug(f"Ses dosyası çalınıyor: {temp_file}")
                    winsound.PlaySound(str(temp_file), winsound.SND_FILENAME)
                except Exception as e:
                    self.logger.error(f"Ses çalma hatası: {str(e)}")
                    raise
                    
        except Exception as e:
            self.logger.error(f"EdgeTTS hatası: {str(e)}")
            # Hata durumunda Windows TTS'e geç
            backup_engine = WindowsTTSEngine(language=self.language)
            backup_engine.speak(text)

class VoiceListener(QObject):
    command_received = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    text_detected = pyqtSignal(str)
    command_detected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = logger.getChild("VoiceListener")
        self.config_manager = ConfigManager()
        self.language_manager = LanguageManager()
        
        # Ayarları yükle
        speech_config = self.config_manager.get_config("speech")
        commands_config = self.config_manager.get_config("commands")
        
        # Varsayılan değerler
        default_speech_config = {
            "recognition": {"language": "tr-TR"},
            "synthesis": {
                "engine": "edge",  # edge veya windows
                "language": "tr",
                "voice": "tr-TR-AhmetNeural",  # veya tr-TR-EmelNeural
                "rate": 150,
                "volume": 0.9
            }
        }
        
        # Ayarları birleştir
        self.speech_config = {**default_speech_config, **(speech_config or {})}
        self.commands_config = commands_config or {}
        
        # Ses tanıma ayarları
        self.recognizer = sr.Recognizer()
        self.recognition_language = self.speech_config["recognition"]["language"]
        
        # TTS motoru seç
        self._setup_tts_engine()
        
        # Durum değişkenleri
        self.is_listening = False
        self.is_active = False
        
        # Komut kelimeleri
        self.wake_words = self.commands_config.get("triggers", {}).get("wake_word", ["hey alimer"])
        self.pause_words = self.commands_config.get("triggers", {}).get("pause_word", ["dur", "bekle"])
        
    def _setup_tts_engine(self):
        """TTS motorunu ayarla"""
        try:
            # Windows'ta önce Windows TTS'i dene
            if platform.system().lower() == "windows":
                self.logger.info("Windows TTS motoru başlatılıyor...")
                self.tts_engine = WindowsTTSEngine(
                    language=self.speech_config["synthesis"]["language"]
                )
            # Windows değilse veya Windows TTS başarısız olursa Edge TTS'i dene
            else:
                self.logger.info("Edge TTS motoru başlatılıyor...")
                self.tts_engine = EdgeTTSEngine(
                    language=self.speech_config["synthesis"]["language"]
                )
        except Exception as e:
            self.logger.error(f"TTS motor hatası: {str(e)}")
            # Hiçbir TTS motoru çalışmazsa, basit bir print motoru oluştur
            self.logger.warning("Print motoru kullanılıyor...")
            class PrintEngine(TTSEngine):
                def speak(self, text):
                    print(f"🔊 {text}")
            self.tts_engine = PrintEngine()
            
    def _listen_loop(self):
        """Sürekli dinleme döngüsü"""
        try:
            with sr.Microphone() as source:
                self.logger.info("Mikrofon başlatıldı, gürültü ayarlanıyor...")
                self.recognizer.adjust_for_ambient_noise(source)
                
                while self.is_listening:
                    try:
                        self.logger.debug("Ses bekleniyor...")
                        audio = self.recognizer.listen(source, timeout=5)
                        text = self.recognizer.recognize_google(audio, language=self.recognition_language)
                        self.logger.debug(f"Algılanan metin: {text}")
                        
                        # Algılanan metni ilet
                        self.text_detected.emit(text)
                        
                        if not self.is_active:
                            # Wake word kontrolü
                            if any(word in text.lower() for word in self.wake_words):
                                self.is_active = True
                                self.speak(self.language_manager.get_message("listening_started"))
                                self.status_changed.emit("active")
                        else:
                            # Pause word kontrolü
                            if any(word in text.lower() for word in self.pause_words):
                                self.is_active = False
                                self.speak(self.language_manager.get_message("listening_paused"))
                                self.status_changed.emit("paused")
                            else:
                                # Normal komut işleme
                                self.command_detected.emit(text)
                                self.command_received.emit(text)
                                
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        self.logger.error(f"Dinleme döngüsü hatası: {str(e)}")
                        time.sleep(1)  # Hata durumunda kısa bir bekleme
                        
        except Exception as e:
            self.logger.error(f"Mikrofon hatası: {str(e)}")
            self.status_changed.emit("error")
                    
    def start_listening(self):
        """Dinlemeyi başlat"""
        if not self.is_listening:
            try:
                self.logger.info("Dinleme başlatılıyor...")
                self.is_listening = True
                self.speak(self.language_manager.get_message("welcome"))
                threading.Thread(target=self._listen_loop, daemon=True).start()
                self.status_changed.emit("started")
            except Exception as e:
                self.logger.error(f"Dinleme başlatma hatası: {str(e)}")
                self.status_changed.emit("error")
            
    def stop_listening(self):
        """Dinlemeyi tamamen durdur"""
        try:
            self.logger.info("Dinleme durduruluyor...")
            self.is_listening = False
            self.is_active = False
            self.speak(self.language_manager.get_message("goodbye"))
            self.status_changed.emit("stopped")
        except Exception as e:
            self.logger.error(f"Dinleme durdurma hatası: {str(e)}")
            self.status_changed.emit("error")

    def speak(self, text: str):
        """Metni seslendir"""
        try:
            self.logger.debug(f"Seslendirilecek metin: {text}")
            print(f"🗣️ AI: {text}")
            self.tts_engine.speak(text)
        except Exception as e:
            self.logger.error(f"Konuşma hatası: {str(e)}")
            print(f"🔊 {text}")  # En azından metni yazdır

    def __del__(self):
        """Yıkıcı metod"""
        try:
            self.logger.info("VoiceListener kapatılıyor...")
            self.stop_listening()
        except:
            pass 