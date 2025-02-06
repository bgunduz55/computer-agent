import pyttsx3
from config_manager import ConfigManager

class SpeechManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        speech_config = self.config_manager.get_config("speech")
        
        # Ses tanıma ayarları
        recognition_config = speech_config.get("recognition", {})
        self.recognition_engine = recognition_config.get("engine", "google")
        self.recognition_language = recognition_config.get("language", "tr-TR")
        self.recognition_timeout = recognition_config.get("timeout", 5)
        
        # Ses sentezi ayarları
        synthesis_config = speech_config.get("synthesis", {})
        self.tts_engine = pyttsx3.init(synthesis_config.get("engine", "sapi5"))
        self.tts_engine.setProperty("voice", synthesis_config.get("voice", "tr"))
        self.tts_engine.setProperty("rate", synthesis_config.get("rate", 150))
        self.tts_engine.setProperty("volume", synthesis_config.get("volume", 0.9)) 