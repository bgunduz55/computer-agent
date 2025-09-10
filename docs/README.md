# 🤖 JARVIS Computer Assistant

**Akıllı Bilgisayar Asistanı - Windows 11 & Linux Desteği**

JARVIS Computer Assistant, Iron Man filmlerindeki JARVIS'e benzer şekilde çalışan, ses tanıma, AI entegrasyonu, uzak kontrol ve gelişmiş sistem yönetimi özelliklerine sahip kapsamlı bir bilgisayar asistanıdır.

## ✨ **Özellikler**

### 🎤 **Gelişmiş Ses Tanıma**
- Windows+H seviyesinde akıllı dinleme
- Gürültü filtreleme ve VAD (Voice Activity Detection)
- Uyandırma kelimesi algılama ("JARVIS", "Hey JARVIS")
- Cross-platform ses desteği (Windows & Linux)
- Çoklu dil desteği (Türkçe, İngilizce)

### 🧠 **AI Entegrasyonu**
- **Çoklu AI Provider**: Ollama, OpenAI, Google Gemini, OpenRouter
- **RAG Sistemi**: Bağlam bazlı öğrenme ve hafıza
- **Akıllı Yanıtlar**: Sistem durumu ve uygulama bağlamı ile
- **Model Değiştirme**: Duruma göre en uygun AI modeli seçimi

### 🖥️ **Sistem Kontrolü**
- **Uygulama Yönetimi**: Açma, kapama, tarayıcı kontrolü
- **Terminal Entegrasyonu**: PowerShell, CMD, Linux terminal
- **Sistem Bilgileri**: Gerçek zamanlı sistem durumu
- **Medya Kontrolü**: Ses, parlaklık, güç yönetimi

### 📱 **Uzak Kontrol**
- **WebSocket Server**: Real-time uzak erişim
- **Flutter Mobil App**: Android/iOS client
- **VPN Desteği**: Güvenli uzak bağlantı
- **Ayarlar Yönetimi**: IP/Port konfigürasyonu

### 🔌 **Plugin Sistemi**
- **Genişletilebilir Mimari**: Özel eklentiler
- **Core Plugins**: Hava durumu, takvim, email, haberler
- **Sistem İzleme**: Performans ve güvenlik takibi
- **Otomatik Yükleme**: Plugin keşfi ve yönetimi

### 🔒 **Güvenlik**
- **Komut Doğrulama**: Tehlikeli komutları engelleme
- **Kimlik Doğrulama**: JWT token tabanlı güvenlik
- **Şifreleme**: Hassas veri koruması
- **Tehdit Algılama**: Şüpheli aktivite tespiti

### 📊 **Analytics & Monitoring**
- **Performans İzleme**: CPU, RAM, yanıt süreleri
- **Kullanım Analizi**: Komut geçmişi ve istatistikler
- **Güvenlik Raporları**: Tehdit analizi ve loglar
- **Otomatik Optimizasyon**: Performans iyileştirmeleri

## 🚀 **Hızlı Başlangıç**

### **Gereksinimler**
- Python 3.8+
- Windows 11 veya Linux (Ubuntu/Debian/Fedora)
- Mikrofon ve hoparlör
- 4GB+ RAM (8GB önerilen)

### **Kurulum**

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/yourusername/jarvis-computer-assistant.git
cd jarvis-computer-assistant
```

2. **Dependencies'leri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Konfigürasyonu ayarlayın:**
```bash
cp config/default.json config/user.json
# user.json dosyasını düzenleyin
```

4. **Uygulamayı başlatın:**
```bash
python src/main.py
```

### **İlk Kurulum**

1. **Ses Tanıma Ayarları:**
   - Mikrofonu test edin
   - Uyandırma kelimesini ayarlayın
   - Dil seçimini yapın

2. **AI Provider Ayarları:**
   - API anahtarlarınızı ekleyin
   - Varsayılan modeli seçin
   - RAG sistemini etkinleştirin

3. **Uzak Kontrol Ayarları:**
   - WebSocket portunu ayarlayın
   - Güvenlik token'ını oluşturun
   - Flutter uygulamasını indirin

## 📖 **Kullanım Kılavuzu**

### **Ses Komutları**

#### **Temel Komutlar**
- `"Hey JARVIS"` - Asistanı uyandır
- `"What time is it?"` - Saati sor
- `"Open Google"` - Web sitesi aç
- `"Close current tab"` - Mevcut sekmeyi kapat
- `"Search for Python tutorials"` - Web'de ara

#### **Sistem Komutları**
- `"Show running applications"` - Çalışan uygulamaları göster
- `"Close Chrome"` - Uygulamayı kapat
- `"Increase volume"` - Sesi artır
- `"Set brightness to 50%"` - Parlaklığı ayarla
- `"Show system status"` - Sistem durumunu göster

#### **Terminal Komutları**
- `"Run git status"` - Git durumunu kontrol et
- `"Install package numpy"` - Paket yükle
- `"List files in current directory"` - Dosyaları listele
- `"Create new file test.py"` - Dosya oluştur

### **Plugin Kullanımı**

#### **Hava Durumu Plugin**
- `"What's the weather?"` - Hava durumunu sor
- `"Weather in Istanbul"` - Belirli şehir hava durumu
- `"Weather forecast"` - Hava tahmini

#### **Takvim Plugin**
- `"What's on my calendar today?"` - Bugünkü etkinlikler
- `"Add meeting tomorrow at 2 PM"` - Toplantı ekle
- `"Show next event"` - Sıradaki etkinlik

#### **Email Plugin**
- `"Check my emails"` - E-postaları kontrol et
- `"How many unread emails?"` - Okunmamış e-posta sayısı
- `"Send email to john@example.com"` - E-posta gönder

### **Uzak Kontrol**

#### **Flutter Mobil Uygulama**
1. Uygulamayı indirin ve yükleyin
2. Ayarlardan server IP ve port'u girin
3. Bağlantıyı test edin
4. Uzaktan komut gönderin

#### **WebSocket API**
```javascript
const ws = new WebSocket('ws://your-server:8765');
ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'voice_command',
        command: 'What time is it?'
    }));
};
```

## ⚙️ **Konfigürasyon**

### **Ana Konfigürasyon (config/user.json)**

```json
{
  "voice": {
    "language": "tr",
    "wake_words": ["jarvis", "hey jarvis"],
    "confidence_threshold": 0.7,
    "use_enhanced_voice": true
  },
  "ai": {
    "default_provider": "ollama",
    "default_model": "gpt-oss:20b",
    "enable_rag": true
  },
  "remote_control": {
    "enabled": true,
    "port": 8765,
    "host": "0.0.0.0"
  },
  "security": {
    "enable_command_validation": true,
    "blocked_patterns": ["rm -rf", "format"]
  }
}
```

### **AI Provider Ayarları**

#### **Ollama**
```json
{
  "ollama": {
    "base_url": "http://localhost:11434",
    "models": ["gpt-oss:20b", "deepseek-r1:7b"]
  }
}
```

#### **OpenAI**
```json
{
  "openai": {
    "api_key": "your-api-key",
    "models": ["gpt-3.5-turbo", "gpt-4"]
  }
}
```

### **Plugin Ayarları**

#### **Hava Durumu Plugin**
```json
{
  "weather": {
    "api_key": "your-openweathermap-key",
    "default_city": "Istanbul",
    "units": "metric"
  }
}
```

## 🔧 **Geliştirici Kılavuzu**

### **Plugin Geliştirme**

1. **Yeni Plugin Oluşturun:**
```python
from plugins.base_plugin import BasePlugin, PluginInfo, PluginType

class MyPlugin(BasePlugin):
    PLUGIN_INFO = PluginInfo(
        name="my_plugin",
        version="1.0.0",
        description="My custom plugin",
        author="Your Name",
        plugin_type=PluginType.UTILITY
    )
    
    async def _initialize(self) -> bool:
        # Plugin initialization
        return True
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        # Handle voice commands
        if "my command" in command.lower():
            return "Plugin response"
        return None
```

2. **Plugin'i Kaydedin:**
   - `src/plugins/community_plugins/` klasörüne ekleyin
   - Otomatik olarak yüklenecektir

### **API Geliştirme**

#### **WebSocket Endpoints**
```python
# Yeni endpoint ekleme
@websocket_server.route("/custom")
async def custom_endpoint(websocket, path):
    # Custom logic
    pass
```

#### **REST API**
```python
# REST endpoint ekleme
@app.route("/api/custom", methods=["POST"])
async def custom_api():
    # API logic
    pass
```

### **Test Yazma**

```python
import pytest
from src.core.jarvis_core import JARVISCore

@pytest.mark.asyncio
async def test_voice_command():
    core = JARVISCore()
    await core.initialize()
    
    result = await core.process_voice_command("test command")
    assert result is not None
    
    await core.shutdown()
```

## 🐛 **Sorun Giderme**

### **Ses Tanıma Sorunları**

**Problem**: Mikrofon algılanmıyor
**Çözüm**: 
- Mikrofon izinlerini kontrol edin
- Ses cihazlarını test edin
- `src/integrations/speech_engines/test_microphone.py` çalıştırın

**Problem**: Düşük tanıma doğruluğu
**Çözüm**:
- Gürültü seviyesini azaltın
- `confidence_threshold` değerini düşürün
- Enhanced voice recognition'ı etkinleştirin

### **AI Entegrasyon Sorunları**

**Problem**: AI yanıt vermiyor
**Çözüm**:
- API anahtarlarını kontrol edin
- İnternet bağlantısını test edin
- Model durumunu kontrol edin

**Problem**: RAG sistemi çalışmıyor
**Çözüm**:
- ChromaDB kurulumunu kontrol edin
- Vektör veritabanını yeniden oluşturun

### **Uzak Kontrol Sorunları**

**Problem**: Flutter uygulaması bağlanamıyor
**Çözüm**:
- Firewall ayarlarını kontrol edin
- IP ve port ayarlarını doğrulayın
- VPN bağlantısını test edin

### **Performans Sorunları**

**Problem**: Yavaş yanıt süreleri
**Çözüm**:
- Performance manager'ı kontrol edin
- Gereksiz plugin'leri devre dışı bırakın
- Sistem kaynaklarını izleyin

## 📊 **Monitoring & Analytics**

### **Performans Metrikleri**
- CPU kullanımı
- Bellek kullanımı
- Yanıt süreleri
- Hata oranları

### **Kullanım İstatistikleri**
- Komut sayıları
- Başarı oranları
- En çok kullanılan özellikler
- Kullanıcı davranışları

### **Güvenlik Raporları**
- Engellenen komutlar
- Tehdit algılamaları
- Kimlik doğrulama logları
- Güvenlik olayları

## 🤝 **Katkıda Bulunma**

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

### **Geliştirme Standartları**
- PEP 8 kod stili
- Type hints kullanın
- Docstring'ler yazın
- Test yazın
- Clean code prensiplerini takip edin

## 📄 **Lisans**

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 **Teşekkürler**

- OpenAI - AI modelleri
- Google - Speech Recognition
- Microsoft - Windows Speech Platform
- Ollama - Yerel AI modelleri
- Flutter - Mobil uygulama framework'ü

## 📞 **Destek**

- **GitHub Issues**: Bug raporları ve özellik istekleri
- **Discord**: Topluluk desteği
- **Email**: support@jarvis-assistant.com
- **Dokümantasyon**: https://docs.jarvis-assistant.com

---

**JARVIS Computer Assistant** - Geleceğin bilgisayar asistanı bugün burada! 🚀
