# 🔧 JARVIS Computer Assistant - Kurulum Kılavuzu

Bu kılavuz, JARVIS Computer Assistant'ı Windows 11 ve Linux sistemlerde kurmak için adım adım talimatlar içerir.

## 📋 **Sistem Gereksinimleri**

### **Minimum Gereksinimler**
- **İşletim Sistemi**: Windows 11 veya Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- **Python**: 3.8 veya üzeri
- **RAM**: 4GB (8GB önerilen)
- **Disk Alanı**: 2GB boş alan
- **İnternet**: AI servisleri için gerekli

### **Önerilen Gereksinimler**
- **İşletim Sistemi**: Windows 11 Pro veya Ubuntu 22.04 LTS
- **Python**: 3.10 veya üzeri
- **RAM**: 16GB
- **Disk Alanı**: 10GB SSD
- **İşlemci**: 4+ çekirdek
- **Ses**: Kaliteli mikrofon ve hoparlör

## 🪟 **Windows 11 Kurulumu**

### **1. Python Kurulumu**

1. **Python 3.10+ indirin:**
   - [python.org](https://www.python.org/downloads/) adresinden indirin
   - "Add Python to PATH" seçeneğini işaretleyin
   - Kurulumu tamamlayın

2. **Python kurulumunu doğrulayın:**
```cmd
python --version
pip --version
```

### **2. Git Kurulumu**

1. **Git indirin:**
   - [git-scm.com](https://git-scm.com/download/win) adresinden indirin
   - Varsayılan ayarlarla kurun

2. **Git kurulumunu doğrulayın:**
```cmd
git --version
```

### **3. Visual Studio Build Tools (Gerekli)**

1. **Visual Studio Build Tools indirin:**
   - [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/) adresinden
   - "Build Tools for Visual Studio 2022" seçin

2. **C++ Build Tools'u yükleyin:**
   - "C++ build tools" workload'unu seçin
   - "Windows 10/11 SDK" seçin
   - Kurulumu tamamlayın

### **4. JARVIS Kurulumu**

1. **Repository'yi klonlayın:**
```cmd
git clone https://github.com/yourusername/jarvis-computer-assistant.git
cd jarvis-computer-assistant
```

2. **Virtual environment oluşturun:**
```cmd
python -m venv jarvis_env
jarvis_env\Scripts\activate
```

3. **Dependencies'leri yükleyin:**
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Konfigürasyonu ayarlayın:**
```cmd
copy config\default.json config\user.json
```

5. **Test kurulumu:**
```cmd
python test_production_integration.py
```

## 🐧 **Linux Kurulumu**

### **Ubuntu/Debian**

1. **Sistem paketlerini güncelleyin:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Gerekli paketleri yükleyin:**
```bash
sudo apt install -y python3.10 python3.10-venv python3-pip git build-essential
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y espeak espeak-data libespeak1 libespeak-dev
sudo apt install -y festival festvox-kallpc16k
sudo apt install -y pulseaudio pulseaudio-utils
```

3. **Python 3.10+ kurulumu (gerekirse):**
```bash
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```

4. **JARVIS kurulumu:**
```bash
git clone https://github.com/yourusername/jarvis-computer-assistant.git
cd jarvis-computer-assistant
python3.10 -m venv jarvis_env
source jarvis_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### **Fedora**

1. **Sistem paketlerini güncelleyin:**
```bash
sudo dnf update -y
```

2. **Gerekli paketleri yükleyin:**
```bash
sudo dnf install -y python3.10 python3.10-pip git gcc gcc-c++ make
sudo dnf install -y portaudio-devel python3-pyaudio
sudo dnf install -y espeak espeak-devel
sudo dnf install -y festival festival-devel
sudo dnf install -y pulseaudio pulseaudio-utils
```

3. **JARVIS kurulumu:**
```bash
git clone https://github.com/yourusername/jarvis-computer-assistant.git
cd jarvis-computer-assistant
python3.10 -m venv jarvis_env
source jarvis_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔧 **Konfigürasyon**

### **1. Temel Konfigürasyon**

`config/user.json` dosyasını düzenleyin:

```json
{
  "voice": {
    "language": "tr",
    "wake_words": ["jarvis", "hey jarvis"],
    "confidence_threshold": 0.7,
    "use_enhanced_voice": true,
    "energy_threshold": 300,
    "noise_reduction": true,
    "vad_enabled": true
  },
  "ai": {
    "default_provider": "ollama",
    "default_model": "deepseek-r1:8b",
    "enable_rag": true,
    "max_tokens": 1000,
    "temperature": 0.7
  },
  "remote_control": {
    "enabled": true,
    "port": 8765,
    "host": "0.0.0.0",
    "use_ssl": false
  },
  "security": {
    "enable_command_validation": true,
    "max_command_length": 1000,
    "blocked_patterns": [
      "rm -rf /",
      "format",
      "del /q",
      "shutdown"
    ]
  },
  "performance": {
    "monitoring_interval": 30,
    "optimization_interval": 300,
    "auto_optimize": true,
    "cpu_threshold": 80.0,
    "memory_threshold": 85.0
  }
}
```

### **2. AI Provider Ayarları**

#### **Ollama (Önerilen)**

1. **Ollama'yı indirin:**
   - [ollama.ai](https://ollama.ai) adresinden indirin
   - Kurulumu tamamlayın

2. **Model indirin:**
```bash
ollama pull deepseek-r1:8b
ollama pull deepseek-r1:7b
```

3. **Konfigürasyon:**
```json
{
  "ai": {
    "providers": {
      "ollama": {
        "base_url": "http://localhost:11434",
        "api_key": "",
        "models": ["deepseek-r1:8b", "deepseek-r1:7b"]
      }
    }
  }
}
```

#### **OpenAI**

1. **API anahtarı alın:**
   - [platform.openai.com](https://platform.openai.com) adresinden
   - API anahtarı oluşturun

2. **Konfigürasyon:**
```json
{
  "ai": {
    "providers": {
      "openai": {
        "api_key": "your-openai-api-key",
        "models": ["gpt-3.5-turbo", "gpt-4"]
      }
    }
  }
}
```

#### **Google Gemini**

1. **API anahtarı alın:**
   - [makersuite.google.com](https://makersuite.google.com) adresinden
   - API anahtarı oluşturun

2. **Konfigürasyon:**
```json
{
  "ai": {
    "providers": {
      "gemini": {
        "api_key": "your-gemini-api-key",
        "models": ["gemini-pro"]
      }
    }
  }
}
```

### **3. Plugin Ayarları**

#### **Hava Durumu Plugin**
```json
{
  "plugins": {
    "weather": {
      "api_key": "your-openweathermap-api-key",
      "default_city": "Istanbul",
      "units": "metric",
      "language": "tr"
    }
  }
}
```

#### **Email Plugin**
```json
{
  "plugins": {
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "imap_server": "imap.gmail.com",
      "imap_port": 993,
      "email_address": "your-email@gmail.com",
      "password": "your-app-password",
      "use_tls": true
    }
  }
}
```

## 🚀 **İlk Çalıştırma**

### **1. Uygulamayı Başlatın**

```bash
# Windows
jarvis_env\Scripts\activate
python src\main.py

# Linux
source jarvis_env/bin/activate
python src/main.py
```

### **2. İlk Kurulum Sihirbazı**

Uygulama ilk kez çalıştırıldığında kurulum sihirbazı başlar:

1. **Ses Testi:**
   - Mikrofonu test edin
   - "Test" butonuna basın
   - Ses seviyesini ayarlayın

2. **Dil Seçimi:**
   - Türkçe veya İngilizce seçin
   - Uyandırma kelimelerini ayarlayın

3. **AI Provider:**
   - Kullanılabilir provider'ları seçin
   - API anahtarlarını girin
   - Model testini yapın

4. **Uzak Kontrol:**
   - WebSocket portunu ayarlayın
   - Güvenlik token'ını oluşturun

### **3. Test Komutları**

Kurulum tamamlandıktan sonra test edin:

```
"Hey JARVIS, what time is it?"
"Hey JARVIS, open Google"
"Hey JARVIS, show system status"
"Hey JARVIS, what's the weather?"
```

## 📱 **Flutter Mobil Uygulama Kurulumu**

### **1. Android APK İndirme**

1. **APK dosyasını indirin:**
   - `computer_assistant_flutter/build/app/outputs/flutter-apk/` klasöründen
   - `app-debug.apk` dosyasını indirin

2. **Android cihazınızda yükleyin:**
   - "Bilinmeyen kaynaklardan yükleme" iznini verin
   - APK dosyasını açın ve yükleyin

### **2. Uygulama Ayarları**

1. **Uygulamayı açın**
2. **Ayarlar > Bağlantı Ayarları**'na gidin
3. **Server Host**: Bilgisayarınızın IP adresini girin
4. **Server Port**: 8765 (varsayılan)
5. **Test Bağlantısı** butonuna basın

### **3. Bağlantı Testi**

1. **Ana ekranda "Bağlan" butonuna basın**
2. **Bağlantı durumunu kontrol edin**
3. **Test komutu gönderin**

## 🔧 **Gelişmiş Konfigürasyon**

### **1. Sistem Servisi (Linux)**

JARVIS'i sistem servisi olarak çalıştırmak için:

1. **Servis dosyası oluşturun:**
```bash
sudo nano /etc/systemd/system/jarvis.service
```

2. **Servis içeriği:**
```ini
[Unit]
Description=JARVIS Computer Assistant
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/jarvis-computer-assistant
Environment=PATH=/path/to/jarvis-computer-assistant/jarvis_env/bin
ExecStart=/path/to/jarvis-computer-assistant/jarvis_env/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Servisi etkinleştirin:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable jarvis
sudo systemctl start jarvis
```

### **2. Windows Servisi**

1. **NSSM indirin:**
   - [nssm.cc](https://nssm.cc) adresinden indirin

2. **Servis oluşturun:**
```cmd
nssm install JARVIS
nssm set JARVIS Application C:\path\to\jarvis-computer-assistant\jarvis_env\Scripts\python.exe
nssm set JARVIS AppParameters C:\path\to\jarvis-computer-assistant\src\main.py
nssm set JARVIS AppDirectory C:\path\to\jarvis-computer-assistant
nssm start JARVIS
```

### **3. Docker Kurulumu**

1. **Dockerfile oluşturun:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "src/main.py"]
```

2. **Docker Compose:**
```yaml
version: '3.8'
services:
  jarvis:
    build: .
    ports:
      - "8765:8765"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
```

## 🐛 **Sorun Giderme**

### **Yaygın Sorunlar**

#### **1. Mikrofon Algılanmıyor**

**Windows:**
```cmd
# Ses cihazlarını kontrol edin
python -c "import sounddevice; print(sounddevice.query_devices())"
```

**Linux:**
```bash
# PulseAudio durumunu kontrol edin
pulseaudio --check -v
# Mikrofon testi
arecord -l
```

#### **2. Python Dependencies Hatası**

```bash
# Virtual environment'ı yeniden oluşturun
rm -rf jarvis_env
python -m venv jarvis_env
source jarvis_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### **3. Port Zaten Kullanımda**

```bash
# Port kullanımını kontrol edin
netstat -tulpn | grep 8765
# Farklı port kullanın
# config/user.json'da port değerini değiştirin
```

#### **4. AI Provider Bağlantı Hatası**

```bash
# Ollama durumunu kontrol edin
curl http://localhost:11434/api/tags
# API anahtarlarını kontrol edin
# İnternet bağlantısını test edin
```

### **Log Dosyaları**

- **Ana log**: `data/logs/jarvis.log`
- **Hata logları**: `data/logs/errors.log`
- **Ses logları**: `data/logs/voice.log`
- **Debug logları**: `data/debug.log`

### **Debug Modu**

```bash
# Debug modunda çalıştırın
python src/main.py --debug --verbose
```

## ✅ **Kurulum Doğrulama**

Kurulumun başarılı olduğunu doğrulamak için:

1. **Test scriptini çalıştırın:**
```bash
python test_production_integration.py
```

2. **Tüm testlerin geçtiğini kontrol edin:**
```
✅ Platform Detection
✅ Speech Recognition
✅ AI Integration
✅ Plugin System
✅ Performance Manager
✅ Security Manager
✅ Analytics Manager
```

3. **Uygulamayı başlatın ve test edin:**
```bash
python src/main.py
# "Hey JARVIS, test" komutunu söyleyin
```

## 🎉 **Kurulum Tamamlandı!**

JARVIS Computer Assistant başarıyla kuruldu! Artık:

- 🎤 Ses komutlarını kullanabilirsiniz
- 🧠 AI ile konuşabilirsiniz
- 📱 Mobil uygulamadan uzaktan kontrol edebilirsiniz
- 🔌 Plugin'lerle özelleştirebilirsiniz
- 📊 Performans ve kullanım istatistiklerini izleyebilirsiniz

**Sonraki adımlar:**
- [Kullanım Kılavuzu](USAGE.md) okuyun
- [Plugin Geliştirme](PLUGIN_DEVELOPMENT.md) öğrenin
- [API Dokümantasyonu](API.md) inceleyin

---

**Sorun yaşıyorsanız:** [GitHub Issues](https://github.com/yourusername/jarvis-computer-assistant/issues) sayfasından destek alın.
