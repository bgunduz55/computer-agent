"""
Simple Settings Manager for JARVIS Computer Assistant

A clean, simple settings management system that actually works.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SimpleAISettings:
    """Simple AI settings"""
    default_provider: str = "ollama"
    default_model: str = "llama2"
    max_tokens: int = 1000
    temperature: float = 0.7
    enable_rag: bool = True
    
    # API Keys
    openai_api_key: str = ""
    gemini_api_key: str = ""
    openrouter_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Provider Enable/Disable
    openai_enabled: bool = False
    gemini_enabled: bool = False
    openrouter_enabled: bool = False
    anthropic_enabled: bool = False
    ollama_enabled: bool = True

@dataclass
class SimpleVoiceSettings:
    """Simple voice settings"""
    engine: str = "google"
    language: str = "en-US"
    wake_word: str = "hey jarvis"
    confidence_threshold: float = 0.7
    auto_listen: bool = False

@dataclass
class SimpleSystemSettings:
    """Simple system settings"""
    auto_start: bool = False
    minimize_to_tray: bool = True
    log_level: str = "INFO"

@dataclass
class SimpleRemoteSettings:
    """Simple remote settings"""
    websocket_host: str = "0.0.0.0"
    websocket_port: int = 8765

@dataclass
class SimpleSettings:
    """Simple settings container"""
    ai: SimpleAISettings
    voice: SimpleVoiceSettings
    system: SimpleSystemSettings
    remote: SimpleRemoteSettings

class SimpleSettingsManager:
    """Simple settings manager that actually works"""
    
    def __init__(self, config_file: str = "config/simple_settings.json"):
        self.config_file = Path(config_file)
        self.settings = self._load_default_settings()
        self._ensure_config_dir()
        self.load_settings()
        
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _load_default_settings(self) -> SimpleSettings:
        """Load default settings"""
        return SimpleSettings(
            ai=SimpleAISettings(),
            voice=SimpleVoiceSettings(),
            system=SimpleSystemSettings(),
            remote=SimpleRemoteSettings()
        )
    
    def load_settings(self) -> bool:
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load AI settings
                if 'ai' in data:
                    ai_data = data['ai']
                    self.settings.ai = SimpleAISettings(
                        default_provider=ai_data.get('default_provider', 'ollama'),
                        default_model=ai_data.get('default_model', 'llama2'),
                        max_tokens=ai_data.get('max_tokens', 1000),
                        temperature=ai_data.get('temperature', 0.7),
                        enable_rag=ai_data.get('enable_rag', True),
                        openai_api_key=ai_data.get('openai_api_key', ''),
                        gemini_api_key=ai_data.get('gemini_api_key', ''),
                        openrouter_api_key=ai_data.get('openrouter_api_key', ''),
                        anthropic_api_key=ai_data.get('anthropic_api_key', ''),
                        openai_enabled=ai_data.get('openai_enabled', False),
                        gemini_enabled=ai_data.get('gemini_enabled', False),
                        openrouter_enabled=ai_data.get('openrouter_enabled', False),
                        anthropic_enabled=ai_data.get('anthropic_enabled', False),
                        ollama_enabled=ai_data.get('ollama_enabled', True)
                    )
                
                # Load voice settings
                if 'voice' in data:
                    voice_data = data['voice']
                    self.settings.voice = SimpleVoiceSettings(
                        engine=voice_data.get('engine', 'google'),
                        language=voice_data.get('language', 'en-US'),
                        wake_word=voice_data.get('wake_word', 'hey jarvis'),
                        confidence_threshold=voice_data.get('confidence_threshold', 0.7),
                        auto_listen=voice_data.get('auto_listen', False)
                    )
                
                # Load system settings
                if 'system' in data:
                    system_data = data['system']
                    self.settings.system = SimpleSystemSettings(
                        auto_start=system_data.get('auto_start', False),
                        minimize_to_tray=system_data.get('minimize_to_tray', True),
                        log_level=system_data.get('log_level', 'INFO')
                    )
                
                # Load remote settings
                if 'remote' in data:
                    remote_data = data['remote']
                    self.settings.remote = SimpleRemoteSettings(
                        websocket_host=remote_data.get('websocket_host', '0.0.0.0'),
                        websocket_port=remote_data.get('websocket_port', 8765)
                    )
                
                logger.info("Settings loaded successfully from file")
                return True
            else:
                logger.info("No settings file found, using defaults")
                self.save_settings()
                return True
                
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return False
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            data = {
                'ai': asdict(self.settings.ai),
                'voice': asdict(self.settings.voice),
                'system': asdict(self.settings.system),
                'remote': asdict(self.settings.remote)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info("Settings saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        try:
            if category == 'ai':
                return getattr(self.settings.ai, key, default)
            elif category == 'voice':
                return getattr(self.settings.voice, key, default)
            elif category == 'system':
                return getattr(self.settings.system, key, default)
            elif category == 'remote':
                return getattr(self.settings.remote, key, default)
            else:
                return default
        except Exception as e:
            logger.error(f"Error getting setting {category}.{key}: {e}")
            return default
    
    def set_setting(self, category: str, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        try:
            if category == 'ai':
                setattr(self.settings.ai, key, value)
            elif category == 'voice':
                setattr(self.settings.voice, key, value)
            elif category == 'system':
                setattr(self.settings.system, key, value)
            elif category == 'remote':
                setattr(self.settings.remote, key, value)
            else:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error setting {category}.{key}: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary"""
        return {
            'ai': asdict(self.settings.ai),
            'voice': asdict(self.settings.voice),
            'system': asdict(self.settings.system),
            'remote': asdict(self.settings.remote)
        }
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self.settings = self._load_default_settings()
            return self.save_settings()
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            return False

# Global instance
_settings_manager = None

def get_simple_settings_manager() -> SimpleSettingsManager:
    """Get global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SimpleSettingsManager()
    return _settings_manager

