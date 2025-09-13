# 🔌 JARVIS Computer Assistant - Plugin Geliştirme Kılavuzu

Bu kılavuz, JARVIS Computer Assistant için özel plugin'ler geliştirmeyi öğretir.

## 📋 **İçindekiler**

- [Plugin Sistemi Genel Bakış](#plugin-sistemi-genel-bakış)
- [Temel Plugin Oluşturma](#temel-plugin-oluşturma)
- [Plugin Tipleri](#plugin-tipleri)
- [Gelişmiş Özellikler](#gelişmiş-özellikler)
- [Plugin Konfigürasyonu](#plugin-konfigürasyonu)
- [Testing ve Debugging](#testing-ve-debugging)
- [Plugin Yayınlama](#plugin-yayınlama)
- [Best Practices](#best-practices)

## 🎯 **Plugin Sistemi Genel Bakış**

JARVIS Plugin Sistemi, uygulamayı genişletmek için modüler bir yaklaşım sağlar. Plugin'ler:

- **Bağımsız çalışır**: Ana uygulamadan ayrı olarak yüklenir/kaldırılır
- **Event-driven**: Sistem olaylarına tepki verir
- **Konfigürasyonlu**: JSON schema ile yapılandırılabilir
- **Güvenli**: Sandboxed ortamda çalışır
- **Performanslı**: Asenkron ve optimize edilmiş

### **Plugin Yaşam Döngüsü**

```
1. Discovery → 2. Loading → 3. Initialization → 4. Starting → 5. Running
                                                                    ↓
6. Stopping ← 7. Cleanup ← 8. Unloading ← 9. Disabled ← 10. Error
```

## 🚀 **Temel Plugin Oluşturma**

### **1. Plugin Klasörü Oluşturma**

```bash
mkdir src/plugins/community_plugins/my_plugin
cd src/plugins/community_plugins/my_plugin
```

### **2. Temel Plugin Dosyası**

`my_plugin.py` dosyası oluşturun:

```python
"""
My Custom Plugin for JARVIS Computer Assistant
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from plugins.base_plugin import BasePlugin, PluginInfo, PluginType, PluginConfig


class MyPlugin(BasePlugin):
    """My custom plugin implementation"""
    
    PLUGIN_INFO = PluginInfo(
        name="my_plugin",
        version="1.0.0",
        description="A custom plugin for JARVIS",
        author="Your Name",
        plugin_type=PluginType.UTILITY,
        dependencies=[],
        config_schema={
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": True},
                "api_key": {"type": "string", "description": "API key for external service"},
                "timeout": {"type": "integer", "default": 30, "description": "Request timeout in seconds"},
                "retries": {"type": "integer", "default": 3, "description": "Number of retry attempts"}
            },
            "required": ["api_key"]
        }
    )
    
    PRIORITY = 50  # Plugin priority (higher = loaded first)
    
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.api_key = None
        self.timeout = 30
        self.retries = 3
        self._data_cache = {}
        
    async def _initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            # Load configuration
            settings = self.config.settings or {}
            self.api_key = settings.get("api_key")
            self.timeout = settings.get("timeout", 30)
            self.retries = settings.get("retries", 3)
            
            if not self.api_key:
                self.logger.error("API key is required")
                return False
            
            self.logger.info("My plugin initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin: {e}")
            return False
    
    async def _cleanup(self) -> None:
        """Cleanup plugin resources"""
        self._data_cache.clear()
        self.logger.info("My plugin cleaned up")
    
    async def _start(self) -> bool:
        """Start the plugin"""
        self.logger.info("My plugin started")
        return True
    
    async def _stop(self) -> None:
        """Stop the plugin"""
        self.logger.info("My plugin stopped")
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle voice commands"""
        command_lower = command.lower()
        
        if "my command" in command_lower:
            try:
                # Process the command
                result = await self._process_command(command)
                return f"My plugin response: {result}"
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
                return "Sorry, I couldn't process that command."
        
        return None
    
    async def handle_ai_request(self, request: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle AI requests"""
        if "my data" in request.lower():
            try:
                data = await self._get_data()
                return f"Here's the data: {data}"
            except Exception as e:
                self.logger.error(f"Error handling AI request: {e}")
                return None
        
        return None
    
    async def handle_system_event(self, event: str, data: Any = None) -> None:
        """Handle system events"""
        if event == "system_startup":
            self.logger.info("System started, initializing my plugin data")
            await self._initialize_data()
        elif event == "system_shutdown":
            self.logger.info("System shutting down, cleaning up my plugin")
            await self._cleanup_data()
    
    def get_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "my command",
            "show my data",
            "update my settings"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            "voice_commands",
            "ai_requests",
            "data_processing",
            "external_api"
        ]
    
    # Private methods
    async def _process_command(self, command: str) -> str:
        """Process a voice command"""
        # Implement your command processing logic here
        return f"Processed: {command}"
    
    async def _get_data(self) -> Dict[str, Any]:
        """Get data from external API"""
        # Implement your data fetching logic here
        return {"status": "success", "data": "sample data"}
    
    async def _initialize_data(self) -> None:
        """Initialize plugin data"""
        # Implement your initialization logic here
        pass
    
    async def _cleanup_data(self) -> None:
        """Cleanup plugin data"""
        # Implement your cleanup logic here
        pass
```

### **3. Plugin'i Test Etme**

`test_my_plugin.py` dosyası oluşturun:

```python
"""
Test script for My Plugin
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from plugins.community_plugins.my_plugin import MyPlugin
from plugins.base_plugin import PluginInfo, PluginConfig


async def test_plugin():
    """Test the plugin"""
    print("Testing My Plugin...")
    
    # Create plugin info
    plugin_info = MyPlugin.PLUGIN_INFO
    
    # Create plugin config
    config = PluginConfig(
        enabled=True,
        settings={
            "api_key": "test-api-key",
            "timeout": 30,
            "retries": 3
        }
    )
    
    # Create plugin instance
    plugin = MyPlugin(plugin_info, config)
    
    try:
        # Test initialization
        print("1. Testing initialization...")
        success = await plugin.load()
        if success:
            print("   ✅ Plugin loaded successfully")
        else:
            print("   ❌ Plugin failed to load")
            return
        
        # Test starting
        print("2. Testing start...")
        success = await plugin.start()
        if success:
            print("   ✅ Plugin started successfully")
        else:
            print("   ❌ Plugin failed to start")
            return
        
        # Test voice command handling
        print("3. Testing voice command handling...")
        response = await plugin.handle_voice_command("my command test")
        if response:
            print(f"   ✅ Voice command response: {response}")
        else:
            print("   ❌ No response to voice command")
        
        # Test AI request handling
        print("4. Testing AI request handling...")
        response = await plugin.handle_ai_request("show my data")
        if response:
            print(f"   ✅ AI request response: {response}")
        else:
            print("   ❌ No response to AI request")
        
        # Test system event handling
        print("5. Testing system event handling...")
        await plugin.handle_system_event("system_startup")
        print("   ✅ System event handled")
        
        # Test stopping
        print("6. Testing stop...")
        await plugin.stop()
        print("   ✅ Plugin stopped successfully")
        
        # Test cleanup
        print("7. Testing cleanup...")
        await plugin.unload()
        print("   ✅ Plugin cleaned up successfully")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_plugin())
```

## 🏷️ **Plugin Tipleri**

### **1. Voice Plugin**

Ses komutlarını işleyen plugin'ler:

```python
class VoicePlugin(BasePlugin):
    PLUGIN_INFO = PluginInfo(
        name="voice_plugin",
        plugin_type=PluginType.VOICE,
        # ...
    )
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        # Voice command processing
        pass
```

### **2. AI Plugin**

AI isteklerini işleyen plugin'ler:

```python
class AIPlugin(BasePlugin):
    PLUGIN_INFO = PluginInfo(
        name="ai_plugin",
        plugin_type=PluginType.AI,
        # ...
    )
    
    async def handle_ai_request(self, request: str, context: Dict[str, Any] = None) -> Optional[str]:
        # AI request processing
        pass
```

### **3. System Plugin**

Sistem olaylarını işleyen plugin'ler:

```python
class SystemPlugin(BasePlugin):
    PLUGIN_INFO = PluginInfo(
        name="system_plugin",
        plugin_type=PluginType.SYSTEM,
        # ...
    )
    
    async def handle_system_event(self, event: str, data: Any = None) -> None:
        # System event processing
        pass
```

### **4. Communication Plugin**

İletişim servislerini yöneten plugin'ler:

```python
class CommunicationPlugin(BasePlugin):
    PLUGIN_INFO = PluginInfo(
        name="communication_plugin",
        plugin_type=PluginType.COMMUNICATION,
        # ...
    )
```

### **5. Productivity Plugin**

Üretkenlik araçlarını sağlayan plugin'ler:

```python
class ProductivityPlugin(BasePlugin):
    PLUGIN_INFO = PluginInfo(
        name="productivity_plugin",
        plugin_type=PluginType.PRODUCTIVITY,
        # ...
    )
```

## 🔧 **Gelişmiş Özellikler**

### **1. Event Handling**

```python
class AdvancedPlugin(BasePlugin):
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        
        # Register event handlers
        self.add_event_handler("voice_command_received", self._on_voice_command)
        self.add_event_handler("system_error", self._on_system_error)
    
    async def _on_voice_command(self, event: str, data: Any) -> None:
        """Handle voice command events"""
        command = data.get("command", "")
        self.logger.info(f"Voice command received: {command}")
    
    async def _on_system_error(self, event: str, data: Any) -> None:
        """Handle system error events"""
        error = data.get("error", "")
        self.logger.error(f"System error: {error}")
```

### **2. Periodic Tasks**

```python
class PeriodicPlugin(BasePlugin):
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self._task = None
        self._interval = 60  # 60 seconds
    
    async def _start(self) -> bool:
        """Start periodic task"""
        self._task = asyncio.create_task(self._periodic_task())
        return True
    
    async def _stop(self) -> None:
        """Stop periodic task"""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _periodic_task(self) -> None:
        """Periodic task"""
        while True:
            try:
                await self._do_periodic_work()
                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in periodic task: {e}")
                await asyncio.sleep(5)
    
    async def _do_periodic_work(self) -> None:
        """Do periodic work"""
        # Implement your periodic work here
        pass
```

### **3. Data Persistence**

```python
import json
from pathlib import Path

class DataPlugin(BasePlugin):
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.data_file = Path("data/plugins/my_plugin_data.json")
        self._data = {}
    
    async def _initialize(self) -> bool:
        """Load persisted data"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    self._data = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            return False
    
    async def _cleanup(self) -> None:
        """Save data"""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
    
    def get_data(self, key: str) -> Any:
        """Get data by key"""
        return self._data.get(key)
    
    def set_data(self, key: str, value: Any) -> None:
        """Set data by key"""
        self._data[key] = value
```

### **4. External API Integration**

```python
import aiohttp
import asyncio

class APIPlugin(BasePlugin):
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.session = None
        self.base_url = "https://api.example.com"
    
    async def _initialize(self) -> bool:
        """Initialize HTTP session"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize session: {e}")
            return False
    
    async def _cleanup(self) -> None:
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        for attempt in range(self.retries):
            try:
                async with self.session.request(method, url, headers=headers, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.warning(f"API request failed: {response.status}")
            except Exception as e:
                self.logger.error(f"API request error (attempt {attempt + 1}): {e}")
                if attempt < self.retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("API request failed after all retries")
```

## ⚙️ **Plugin Konfigürasyonu**

### **1. Configuration Schema**

```python
config_schema = {
    "type": "object",
    "properties": {
        "enabled": {
            "type": "boolean",
            "default": True,
            "description": "Enable/disable the plugin"
        },
        "api_key": {
            "type": "string",
            "description": "API key for external service",
            "minLength": 10
        },
        "timeout": {
            "type": "integer",
            "default": 30,
            "minimum": 1,
            "maximum": 300,
            "description": "Request timeout in seconds"
        },
        "retries": {
            "type": "integer",
            "default": 3,
            "minimum": 0,
            "maximum": 10,
            "description": "Number of retry attempts"
        },
        "settings": {
            "type": "object",
            "properties": {
                "debug": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable debug logging"
                },
                "cache_ttl": {
                    "type": "integer",
                    "default": 3600,
                    "description": "Cache time-to-live in seconds"
                }
            }
        }
    },
    "required": ["api_key"],
    "additionalProperties": False
}
```

### **2. Configuration Validation**

```python
def validate_config(self, config: Dict[str, Any]) -> List[str]:
    """Validate plugin configuration"""
    errors = []
    
    # Check required fields
    if "api_key" not in config:
        errors.append("API key is required")
    
    # Check field types and values
    if "timeout" in config:
        if not isinstance(config["timeout"], int):
            errors.append("Timeout must be an integer")
        elif config["timeout"] < 1 or config["timeout"] > 300:
            errors.append("Timeout must be between 1 and 300 seconds")
    
    if "retries" in config:
        if not isinstance(config["retries"], int):
            errors.append("Retries must be an integer")
        elif config["retries"] < 0 or config["retries"] > 10:
            errors.append("Retries must be between 0 and 10")
    
    return errors
```

## 🧪 **Testing ve Debugging**

### **1. Unit Testing**

```python
import pytest
from unittest.mock import Mock, AsyncMock
from plugins.community_plugins.my_plugin import MyPlugin
from plugins.base_plugin import PluginInfo, PluginConfig

@pytest.fixture
def plugin():
    """Create plugin instance for testing"""
    plugin_info = MyPlugin.PLUGIN_INFO
    config = PluginConfig(
        enabled=True,
        settings={"api_key": "test-key", "timeout": 30}
    )
    return MyPlugin(plugin_info, config)

@pytest.mark.asyncio
async def test_plugin_initialization(plugin):
    """Test plugin initialization"""
    success = await plugin.load()
    assert success == True
    assert plugin.api_key == "test-key"
    assert plugin.timeout == 30

@pytest.mark.asyncio
async def test_voice_command_handling(plugin):
    """Test voice command handling"""
    await plugin.load()
    await plugin.start()
    
    response = await plugin.handle_voice_command("my command test")
    assert response is not None
    assert "My plugin response" in response
    
    # Test command that should not be handled
    response = await plugin.handle_voice_command("other command")
    assert response is None

@pytest.mark.asyncio
async def test_ai_request_handling(plugin):
    """Test AI request handling"""
    await plugin.load()
    await plugin.start()
    
    response = await plugin.handle_ai_request("show my data")
    assert response is not None
    assert "Here's the data" in response

def test_plugin_commands(plugin):
    """Test plugin commands"""
    commands = plugin.get_commands()
    assert "my command" in commands
    assert "show my data" in commands

def test_plugin_capabilities(plugin):
    """Test plugin capabilities"""
    capabilities = plugin.get_capabilities()
    assert "voice_commands" in capabilities
    assert "ai_requests" in capabilities
```

### **2. Integration Testing**

```python
import asyncio
from plugins import get_plugin_manager

async def test_plugin_integration():
    """Test plugin integration with plugin manager"""
    plugin_manager = get_plugin_manager()
    
    # Initialize plugin manager
    await plugin_manager.initialize()
    
    # Test plugin loading
    result = await plugin_manager.load_plugin("my_plugin")
    assert result.success == True
    
    # Test plugin starting
    success = await plugin_manager.start_plugin("my_plugin")
    assert success == True
    
    # Test voice command handling
    response = await plugin_manager.handle_voice_command("my command test")
    assert response is not None
    
    # Test plugin stopping
    success = await plugin_manager.stop_plugin("my_plugin")
    assert success == True
    
    # Test plugin unloading
    success = await plugin_manager.unload_plugin("my_plugin")
    assert success == True
    
    # Cleanup
    await plugin_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(test_plugin_integration())
```

### **3. Debugging**

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

class DebugPlugin(BasePlugin):
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.debug = config.settings.get("debug", False) if config.settings else False
    
    async def _initialize(self) -> bool:
        """Initialize with debug logging"""
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("Debug mode enabled")
        
        # Your initialization code here
        return True
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle voice command with debug logging"""
        if self.debug:
            self.logger.debug(f"Processing voice command: {command}")
            self.logger.debug(f"Context: {context}")
        
        # Your command processing code here
        return "Debug response"
```

## 📦 **Plugin Yayınlama**

### **1. Plugin Paketleme**

`setup.py` dosyası oluşturun:

```python
from setuptools import setup, find_packages

setup(
    name="jarvis-my-plugin",
    version="1.0.0",
    description="My custom plugin for JARVIS Computer Assistant",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/jarvis-my-plugin",
    packages=find_packages(),
    install_requires=[
        "jarvis-assistant-sdk>=1.0.0",
        "aiohttp>=3.8.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)
```

### **2. Plugin Metadata**

`plugin.json` dosyası oluşturun:

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "description": "A custom plugin for JARVIS Computer Assistant",
  "author": "Your Name",
  "email": "your.email@example.com",
  "url": "https://github.com/yourusername/jarvis-my-plugin",
  "license": "MIT",
  "dependencies": [
    "aiohttp>=3.8.0"
  ],
  "tags": ["utility", "api", "custom"],
  "category": "productivity",
  "min_jarvis_version": "1.0.0",
  "max_jarvis_version": "2.0.0",
  "platforms": ["windows", "linux"],
  "python_versions": ["3.8", "3.9", "3.10", "3.11"]
}
```

### **3. Plugin Yükleme**

```bash
# Plugin'i yükleyin
pip install jarvis-my-plugin

# Veya geliştirme modunda
pip install -e /path/to/your/plugin
```

## 🏆 **Best Practices**

### **1. Kod Kalitesi**

- **Type Hints**: Tüm fonksiyonlarda type hints kullanın
- **Docstrings**: Google style docstrings yazın
- **Error Handling**: Kapsamlı hata yönetimi yapın
- **Logging**: Uygun log seviyeleri kullanın
- **Testing**: Unit ve integration testleri yazın

### **2. Performans**

- **Async/Await**: Asenkron işlemler kullanın
- **Caching**: Gereksiz API çağrılarını önleyin
- **Resource Management**: Kaynakları düzgün yönetin
- **Memory Usage**: Bellek kullanımını optimize edin

### **3. Güvenlik**

- **Input Validation**: Tüm girdileri doğrulayın
- **API Keys**: Hassas bilgileri güvenli saklayın
- **Error Messages**: Hassas bilgi sızıntısını önleyin
- **Rate Limiting**: API çağrılarını sınırlayın

### **4. Kullanıcı Deneyimi**

- **Error Messages**: Anlaşılır hata mesajları verin
- **Configuration**: Kolay konfigürasyon sağlayın
- **Documentation**: Kapsamlı dokümantasyon yazın
- **Backwards Compatibility**: Geriye uyumluluk sağlayın

### **5. Plugin Geliştirme Süreci**

1. **Planlama**: Plugin'in amacını ve özelliklerini belirleyin
2. **Prototyping**: Hızlı prototip oluşturun
3. **Development**: Temiz kod yazın
4. **Testing**: Kapsamlı testler yazın
5. **Documentation**: Dokümantasyon oluşturun
6. **Packaging**: Plugin'i paketleyin
7. **Publishing**: Plugin'i yayınlayın
8. **Maintenance**: Plugin'i sürdürün

---

**Daha fazla bilgi için:**
- [JARVIS Plugin Examples](https://github.com/yourusername/jarvis-plugins)
- [Plugin Development Forum](https://forum.jarvis-assistant.com/plugins)
- [Discord Plugin Channel](https://discord.gg/jarvis-plugins)
