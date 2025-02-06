from pathlib import Path
import json
import os
from config_manager import ConfigManager

class LanguageManager:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.languages_dir = Path("src/languages")
        self.languages_dir.mkdir(exist_ok=True)
        
        # Dil ayarlarını config'den al
        lang_config = self.config_manager.get_config("language")
        self.current_language = lang_config.get("default", "tr")
        self.available_languages = lang_config.get("available", ["tr"])
        self.messages = {}
        self.load_languages()
        
    def load_languages(self):
        """Tüm dil dosyalarını yükle"""
        for lang_code in self.available_languages:
            lang_file = self.languages_dir / f"{lang_code}.json"
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.messages[lang_code] = json.load(f)
                    
    def set_language(self, lang_code: str) -> bool:
        """Dili değiştir"""
        if lang_code in self.available_languages:
            self.current_language = lang_code
            return True
        return False
        
    def get_message(self, key: str, **kwargs) -> str:
        """Mesajı getir"""
        try:
            messages = self.messages[self.current_language][key]
            if isinstance(messages, list):
                import random
                message = random.choice(messages)
            else:
                message = messages
            return message.format(**kwargs)
        except Exception:
            # Mesaj bulunamazsa İngilizce'yi dene
            try:
                return self.messages["en"][key].format(**kwargs)
            except:
                return f"Message not found: {key}"
                
    def get_available_languages(self) -> dict:
        """Kullanılabilir dilleri getir"""
        return self.available_languages 