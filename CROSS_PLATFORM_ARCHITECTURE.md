# 🌐 JARVIS Computer Assistant - Cross-Platform Architecture

## 🎯 Cross-Platform Hedefler

### Desteklenen Platformlar
- **Windows 11**: Native Windows Speech Platform, SAPI5 TTS
- **Linux (Ubuntu/Debian/Fedora)**: espeak/festival TTS, PulseAudio
- **Mobil (Android/iOS)**: Flutter cross-platform uygulama

### Temel Prensipler
1. **Platform Abstraction**: Platform-specific kodları soyutlama katmanı ile ayırma
2. **Common Interface**: Ortak arayüzler ile platform bağımsızlığı
3. **Conditional Imports**: Platform detection ile gerekli modülleri yükleme
4. **Graceful Degradation**: Platform özelliği yoksa alternatif çözümler
5. **No Code Duplication**: Ortak kodları tekrar kullanma

---

## 🏗️ Platform Abstraction Layer

### Base Platform Interface
```python
# src/core/platform/base_platform.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum

class PlatformType(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    ANDROID = "android"
    IOS = "ios"

class BasePlatform(ABC):
    """Base platform interface for cross-platform compatibility"""
    
    @property
    @abstractmethod
    def platform_type(self) -> PlatformType:
        """Platform type identifier"""
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Human-readable platform name"""
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        pass
    
    @abstractmethod
    def get_audio_devices(self) -> List[Dict[str, Any]]:
        """Get available audio devices"""
        pass
    
    @abstractmethod
    def get_screen_resolution(self) -> tuple:
        """Get screen resolution"""
        pass
    
    @abstractmethod
    def is_feature_supported(self, feature: str) -> bool:
        """Check if platform supports specific feature"""
        pass
```

### Windows Platform Implementation
```python
# src/core/platform/windows_platform.py
import platform
import win32api
import win32con
import win32gui
import pycaw
from .base_platform import BasePlatform, PlatformType

class WindowsPlatform(BasePlatform):
    """Windows-specific platform implementation"""
    
    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.WINDOWS
    
    @property
    def platform_name(self) -> str:
        return f"Windows {platform.release()}"
    
    def get_system_info(self) -> Dict[str, Any]:
        return {
            "os": "Windows",
            "version": platform.release(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "machine": platform.machine()
        }
    
    def get_audio_devices(self) -> List[Dict[str, Any]]:
        # Windows-specific audio device enumeration
        pass
    
    def get_screen_resolution(self) -> tuple:
        # Windows-specific screen resolution detection
        pass
    
    def is_feature_supported(self, feature: str) -> bool:
        features = {
            "windows_speech": True,
            "sapi5_tts": True,
            "com_interface": True,
            "windows_api": True,
            "pulseaudio": False,
            "espeak": False
        }
        return features.get(feature, False)
```

### Linux Platform Implementation
```python
# src/core/platform/linux_platform.py
import platform
import subprocess
import os
from .base_platform import BasePlatform, PlatformType

class LinuxPlatform(BasePlatform):
    """Linux-specific platform implementation"""
    
    @property
    def platform_type(self) -> PlatformType:
        return PlatformType.LINUX
    
    @property
    def platform_name(self) -> str:
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        return f"Linux {platform.release()}"
    
    def get_system_info(self) -> Dict[str, Any]:
        return {
            "os": "Linux",
            "version": platform.release(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "machine": platform.machine(),
            "distribution": self._get_distribution_info()
        }
    
    def get_audio_devices(self) -> List[Dict[str, Any]]:
        # Linux-specific audio device enumeration using PulseAudio
        pass
    
    def get_screen_resolution(self) -> tuple:
        # Linux-specific screen resolution detection using xrandr
        pass
    
    def is_feature_supported(self, feature: str) -> bool:
        features = {
            "windows_speech": False,
            "sapi5_tts": False,
            "com_interface": False,
            "windows_api": False,
            "pulseaudio": self._check_pulseaudio(),
            "espeak": self._check_espeak(),
            "festival": self._check_festival()
        }
        return features.get(feature, False)
    
    def _check_pulseaudio(self) -> bool:
        try:
            subprocess.run(['pulseaudio', '--version'], 
                         capture_output=True, check=True)
            return True
        except:
            return False
    
    def _check_espeak(self) -> bool:
        try:
            subprocess.run(['espeak', '--version'], 
                         capture_output=True, check=True)
            return True
        except:
            return False
```

### Platform Factory
```python
# src/core/platform/platform_factory.py
import platform
from typing import Optional
from .base_platform import BasePlatform, PlatformType
from .windows_platform import WindowsPlatform
from .linux_platform import LinuxPlatform

class PlatformFactory:
    """Factory for creating platform-specific implementations"""
    
    @staticmethod
    def create_platform() -> BasePlatform:
        """Create platform instance based on current OS"""
        system = platform.system().lower()
        
        if system == "windows":
            return WindowsPlatform()
        elif system == "linux":
            return LinuxPlatform()
        else:
            raise NotImplementedError(f"Platform {system} not supported")
    
    @staticmethod
    def get_platform_type() -> PlatformType:
        """Get current platform type"""
        system = platform.system().lower()
        
        if system == "windows":
            return PlatformType.WINDOWS
        elif system == "linux":
            return PlatformType.LINUX
        else:
            return PlatformType.LINUX  # Default fallback
```

---

## 🎤 Cross-Platform Voice Recognition

### Voice Engine Abstraction
```python
# src/integrations/speech_engines/common_speech.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from enum import Enum

class VoiceEngineType(Enum):
    GOOGLE = "google"
    WINDOWS_SPEECH = "windows_speech"
    ESPEAK = "espeak"
    FESTIVAL = "festival"

class BaseVoiceEngine(ABC):
    """Base voice recognition engine interface"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the voice engine"""
        pass
    
    @abstractmethod
    def recognize_speech(self, audio_data: bytes) -> Optional[str]:
        """Recognize speech from audio data"""
        pass
    
    @abstractmethod
    def synthesize_speech(self, text: str) -> bytes:
        """Synthesize speech from text"""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get available voices"""
        pass
    
    @abstractmethod
    def set_voice(self, voice_id: str) -> bool:
        """Set voice for synthesis"""
        pass
```

### Windows Speech Engine
```python
# src/integrations/speech_engines/windows_speech.py
import win32com.client
import speech_recognition as sr
from .common_speech import BaseVoiceEngine, VoiceEngineType

class WindowsSpeechEngine(BaseVoiceEngine):
    """Windows Speech Platform implementation"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = None
        self.voice_id = None
    
    def initialize(self) -> bool:
        try:
            # Initialize Windows TTS
            self.tts_engine = win32com.client.Dispatch("SAPI.SpVoice")
            return True
        except Exception as e:
            print(f"Windows Speech initialization failed: {e}")
            return False
    
    def recognize_speech(self, audio_data: bytes) -> Optional[str]:
        try:
            with sr.AudioData(audio_data, 16000, 2) as audio:
                text = self.recognizer.recognize_google(audio, language='tr-TR')
                return text
        except Exception as e:
            print(f"Speech recognition failed: {e}")
            return None
    
    def synthesize_speech(self, text: str) -> bytes:
        try:
            if self.tts_engine and self.voice_id:
                self.tts_engine.Voice = self.tts_engine.GetVoices().Item(self.voice_id)
            
            # Windows TTS synthesis
            self.tts_engine.Speak(text)
            return b""  # Windows TTS plays directly
        except Exception as e:
            print(f"Speech synthesis failed: {e}")
            return b""
```

### Linux Speech Engine
```python
# src/integrations/speech_engines/linux_speech.py
import subprocess
import tempfile
import os
from .common_speech import BaseVoiceEngine, VoiceEngineType

class LinuxSpeechEngine(BaseVoiceEngine):
    """Linux speech engines implementation"""
    
    def __init__(self):
        self.engine_type = self._detect_available_engine()
        self.voice_id = None
    
    def _detect_available_engine(self) -> VoiceEngineType:
        """Detect available speech engine on Linux"""
        if self._check_espeak():
            return VoiceEngineType.ESPEAK
        elif self._check_festival():
            return VoiceEngineType.FESTIVAL
        else:
            return VoiceEngineType.GOOGLE  # Fallback to Google
    
    def initialize(self) -> bool:
        return self.engine_type != VoiceEngineType.GOOGLE
    
    def recognize_speech(self, audio_data: bytes) -> Optional[str]:
        # Use Google Speech Recognition as fallback
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        try:
            with sr.AudioData(audio_data, 16000, 2) as audio:
                return recognizer.recognize_google(audio, language='tr-TR')
        except:
            return None
    
    def synthesize_speech(self, text: str) -> bytes:
        if self.engine_type == VoiceEngineType.ESPEAK:
            return self._espeak_synthesis(text)
        elif self.engine_type == VoiceEngineType.FESTIVAL:
            return self._festival_synthesis(text)
        else:
            return b""
    
    def _espeak_synthesis(self, text: str) -> bytes:
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                cmd = ['espeak', '-s', '150', '-v', 'tr', '-w', tmp.name, text]
                subprocess.run(cmd, check=True)
                with open(tmp.name, 'rb') as f:
                    return f.read()
        except Exception as e:
            print(f"eSpeak synthesis failed: {e}")
            return b""
```

---

## 🎛️ Cross-Platform System Control

### System Control Abstraction
```python
# src/integrations/system_apis/common_api.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseSystemAPI(ABC):
    """Base system control interface"""
    
    @abstractmethod
    def get_volume(self) -> float:
        """Get current system volume (0.0-1.0)"""
        pass
    
    @abstractmethod
    def set_volume(self, volume: float) -> bool:
        """Set system volume (0.0-1.0)"""
        pass
    
    @abstractmethod
    def get_brightness(self) -> float:
        """Get current screen brightness (0.0-1.0)"""
        pass
    
    @abstractmethod
    def set_brightness(self, brightness: float) -> bool:
        """Set screen brightness (0.0-1.0)"""
        pass
    
    @abstractmethod
    def get_running_apps(self) -> List[Dict[str, Any]]:
        """Get list of running applications"""
        pass
    
    @abstractmethod
    def launch_app(self, app_name: str) -> bool:
        """Launch application by name"""
        pass
    
    @abstractmethod
    def get_window_list(self) -> List[Dict[str, Any]]:
        """Get list of open windows"""
        pass
    
    @abstractmethod
    def focus_window(self, window_id: str) -> bool:
        """Focus window by ID"""
        pass
```

### Windows System API
```python
# src/integrations/system_apis/windows_api.py
import win32api
import win32con
import win32gui
import pycaw
import psutil
from .common_api import BaseSystemAPI

class WindowsSystemAPI(BaseSystemAPI):
    """Windows-specific system control implementation"""
    
    def __init__(self):
        self.audio_interface = self._init_audio_interface()
    
    def get_volume(self) -> float:
        try:
            # Windows volume control using pycaw
            devices = self.audio_interface.GetDefaultAudioEndpoint(0, 0)
            volume = devices.Activate(pycaw.IAudioEndpointVolume._iid_, 0, None)
            return volume.GetMasterScalarVolume()
        except:
            return 0.0
    
    def set_volume(self, volume: float) -> bool:
        try:
            devices = self.audio_interface.GetDefaultAudioEndpoint(0, 0)
            volume_control = devices.Activate(pycaw.IAudioEndpointVolume._iid_, 0, None)
            volume_control.SetMasterScalarVolume(volume, None)
            return True
        except:
            return False
    
    def get_brightness(self) -> float:
        try:
            # Windows brightness control
            import screen_brightness_control as sbc
            return sbc.get_brightness()[0] / 100.0
        except:
            return 0.5
    
    def set_brightness(self, brightness: float) -> bool:
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(int(brightness * 100))
            return True
        except:
            return False
```

### Linux System API
```python
# src/integrations/system_apis/linux_api.py
import subprocess
import psutil
import dbus
from .common_api import BaseSystemAPI

class LinuxSystemAPI(BaseSystemAPI):
    """Linux-specific system control implementation"""
    
    def __init__(self):
        self.pulse_interface = self._init_pulse_interface()
    
    def get_volume(self) -> float:
        try:
            # Linux volume control using PulseAudio
            bus = dbus.SessionBus()
            pulse = bus.get_object('org.PulseAudio1', '/org/pulseaudio/server_lookup1')
            server = dbus.Interface(pulse, 'org.freedesktop.DBus.Properties')
            return float(server.Get('org.PulseAudio.ServerLookup1', 'DefaultSink'))
        except:
            return 0.0
    
    def set_volume(self, volume: float) -> bool:
        try:
            # Use pactl to set volume
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', 
                          f'{int(volume * 100)}%'], check=True)
            return True
        except:
            return False
    
    def get_brightness(self) -> float:
        try:
            # Linux brightness control using xrandr
            result = subprocess.run(['xrandr', '--verbose'], 
                                  capture_output=True, text=True)
            # Parse brightness from xrandr output
            return 0.5  # Placeholder
        except:
            return 0.5
    
    def set_brightness(self, brightness: float) -> bool:
        try:
            # Use xrandr to set brightness
            subprocess.run(['xrandr', '--output', 'eDP-1', '--brightness', 
                          str(brightness)], check=True)
            return True
        except:
            return False
```

---

## 🔧 Cross-Platform Configuration

### Platform-Specific Configs
```json
// config/platforms/windows.json
{
  "platform": "windows",
  "voice": {
    "engine": "windows_speech",
    "tts_engine": "sapi5",
    "voices": {
      "tr": "Microsoft Zira Desktop - Turkish",
      "en": "Microsoft David Desktop - English (United States)"
    }
  },
  "system": {
    "audio_control": "pycaw",
    "brightness_control": "screen_brightness_control",
    "window_management": "win32gui"
  },
  "features": {
    "windows_speech": true,
    "com_interface": true,
    "windows_api": true
  }
}
```

```json
// config/platforms/linux.json
{
  "platform": "linux",
  "voice": {
    "engine": "espeak",
    "tts_engine": "espeak",
    "voices": {
      "tr": "tr",
      "en": "en"
    }
  },
  "system": {
    "audio_control": "pulseaudio",
    "brightness_control": "xrandr",
    "window_management": "wmctrl"
  },
  "features": {
    "pulseaudio": true,
    "espeak": true,
    "festival": false
  }
}
```

### Dynamic Configuration Loading
```python
# src/core/config/platform_config.py
import json
import platform
from pathlib import Path
from typing import Dict, Any

class PlatformConfig:
    """Platform-specific configuration loader"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.config = self._load_platform_config()
    
    def _load_platform_config(self) -> Dict[str, Any]:
        """Load platform-specific configuration"""
        config_path = Path(f"config/platforms/{self.platform}.json")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Fallback to default configuration
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default cross-platform configuration"""
        return {
            "platform": "generic",
            "voice": {
                "engine": "google",
                "tts_engine": "pyttsx3"
            },
            "system": {
                "audio_control": "generic",
                "brightness_control": "generic"
            },
            "features": {}
        }
    
    def get_voice_config(self) -> Dict[str, Any]:
        """Get voice configuration for current platform"""
        return self.config.get("voice", {})
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration for current platform"""
        return self.config.get("system", {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled for current platform"""
        features = self.config.get("features", {})
        return features.get(feature, False)
```

---

## 🚀 Cross-Platform Build & Deployment

### Multi-Platform CI/CD
```yaml
# .github/workflows/cross-platform.yml
name: Cross-Platform Build

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Windows dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run Windows tests
        run: pytest tests/ -m "windows or not linux"

  test-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Linux dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y espeak espeak-data pulseaudio
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run Linux tests
        run: pytest tests/ -m "linux or not windows"

  build-windows:
    needs: [test-windows]
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Windows executable
        run: |
          pip install pyinstaller
          pyinstaller --onefile --windowed src/main.py
      - name: Upload Windows artifact
        uses: actions/upload-artifact@v3
        with:
          name: jarvis-windows
          path: dist/

  build-linux:
    needs: [test-linux]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Linux AppImage
        run: |
          pip install pyinstaller
          pyinstaller --onefile src/main.py
      - name: Upload Linux artifact
        uses: actions/upload-artifact@v3
        with:
          name: jarvis-linux
          path: dist/
```

### Platform Detection & Feature Flags
```python
# src/core/platform/platform_detector.py
import platform
import sys
from typing import Dict, List, Optional

class PlatformDetector:
    """Detect platform capabilities and features"""
    
    @staticmethod
    def detect_platform() -> str:
        """Detect current platform"""
        return platform.system().lower()
    
    @staticmethod
    def get_platform_info() -> Dict[str, any]:
        """Get detailed platform information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "architecture": platform.architecture()
        }
    
    @staticmethod
    def get_available_features() -> List[str]:
        """Get list of available features on current platform"""
        features = []
        current_platform = PlatformDetector.detect_platform()
        
        if current_platform == "windows":
            features.extend([
                "windows_speech",
                "sapi5_tts",
                "com_interface",
                "windows_api",
                "pycaw_audio"
            ])
        elif current_platform == "linux":
            features.extend([
                "pulseaudio",
                "espeak",
                "festival",
                "xrandr_brightness",
                "wmctrl_windows"
            ])
        
        # Common features
        features.extend([
            "google_speech",
            "pyttsx3_tts",
            "psutil_system",
            "pyautogui_automation"
        ])
        
        return features
    
    @staticmethod
    def check_feature_availability(feature: str) -> bool:
        """Check if specific feature is available"""
        try:
            if feature == "windows_speech":
                import win32com.client
                return True
            elif feature == "pulseaudio":
                import subprocess
                subprocess.run(['pulseaudio', '--version'], 
                             capture_output=True, check=True)
                return True
            elif feature == "espeak":
                import subprocess
                subprocess.run(['espeak', '--version'], 
                             capture_output=True, check=True)
                return True
            # Add more feature checks as needed
            return False
        except:
            return False
```

Bu cross-platform mimari, Windows 11 ve Linux'ta sorunsuz çalışacak şekilde tasarlanmıştır. Platform-specific kodlar ayrılmış, ortak arayüzler kullanılmış ve graceful degradation ile platform özellikleri yoksa alternatif çözümler sunulmuştur.
