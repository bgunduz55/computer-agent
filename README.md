# 🤖 AI Code Editor Assistant

Ses komutlarıyla kontrol edilebilen, yapay zeka destekli bir kod editör asistanı. Sesli komutlarla kodunuzu geliştirmenize ve düzenlemenize yardımcı olur.

## 🌟 Özellikler

- 🎤 Sesli komut kontrolü ve sesli yanıt
- 🤖 AI destekli kod geliştirme (deepseek-r1:7b modeli)
- 📝 Kod inceleme ve öneriler
- 🖥️ Kullanıcı dostu grafiksel arayüz
- 🎨 Modern ve temiz tasarım
- 📊 İşlem durumu göstergeleri
- 📜 Komut geçmişi
- 🔍 Ekran okuma ve metin tanıma
- 🖱️ Akıllı pencere yönetimi
- 🗣️ Sesli geri bildirim
- 🌐 Çoklu dil desteği (Türkçe, İngilizce, İspanyolca, Fransızca, Almanca)
- 🎵 Medya kontrolleri (YouTube, ses, parlaklık)
- ⚡ Sistem kontrolleri ve güç yönetimi
- 📋 Görev ve TODO yönetimi
- ⏰ Hatırlatıcılar ve zamanlayıcılar

## 🔧 Gereksinimler

- Python 3.8+
- Ollama (deepseek-r1:7b modeli yüklü olmalı)
- Çalışan bir mikrofon ve hoparlör
- İnternet bağlantısı (Google Speech Recognition için)
- Tesseract OCR (ekran okuma için)
- Windows için SAPI5 veya diğer platformlar için espeak

## 📦 Kurulum

1. **Ollama Kurulumu**
   - Ollama'yı kurun (https://ollama.ai/download adresinden)
   - ollama pull deepseek-r1:7b
   - ollama serve

2. **Tesseract OCR Kurulumu**
   - Windows:
     1. https://github.com/UB-Mannheim/tesseract/wiki adresinden Tesseract OCR'ı indirin
     2. Kurulum sırasında "Add to PATH" seçeneğini işaretleyin
     3. Varsayılan kurulum yolu: `C:\Program Files\Tesseract-OCR\`
   - Linux:
     ```bash
     sudo apt-get install tesseract-ocr
     sudo apt-get install tesseract-ocr-tur  # Türkçe dil desteği için
     ```
   - macOS:
     ```bash
     brew install tesseract
     brew install tesseract-lang  # Ek dil paketleri için
     ```

3. **Ses Sentezi Kurulumu**
   - Windows: 
     - SAPI5 Windows'ta varsayılan olarak yüklüdür
     - Kontrol Paneli > Konuşma Tanıma > Metin Okuma > Ses ekleyebilirsiniz
   - Linux:
     ```bash
     sudo apt-get install espeak
     ```
   - macOS:
     ```bash
     brew install espeak
     ```

4. **Python Bağımlılıklarını Yükleyin**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Kullanım

1. **Asistanı Başlatın**
   ```bash
   python main.py
   ```

2. **Asistanı Kullanın**
   - Sesli komutlarla veya metin girişiyle kullanabilirsiniz
   - Asistan sesli yanıt verecektir

3. **Temel Komutlar**
   - **Uygulama Kontrolü:**
     - "Chrome'u aç/kapat"
     - "Yeni bir notepad penceresi aç"
     - "Visual Studio Code'a geç"
     - "[uygulama adı]'nı kapat"

   - **Medya Kontrolü:**
     - "[şarkı/video adı] aç"
     - "Sesi artır/azalt"
     - "Sesi [0-100] yap"
     - "Parlaklığı artır/azalt"
     - "Parlaklığı [0-100] yap"

   - **Sistem Kontrolü:**
     - "Bilgisayarı uyku moduna al"
     - "Sistem bilgilerini göster"
     - "Ekran görüntüsü al"
     - "Hataları göster"

   - **Görev Yönetimi:**
     - "Yeni görev ekle: [görev]"
     - "Görevleri listele"
     - "TODO ekle: [not]"
     - "[x] dakika sonra hatırlat: [mesaj]"

   - **Web Tarayıcı:**
     - "[site-adı].com'u aç"
     - "Google'da [arama terimi] ara"
     - "Sekmeyi kapat"
     - "Yeni sekme aç"

   - **Kod Geliştirme:**
     - "Geliştir" - Yeni dosya oluştur veya mevcut dosyayı düzenle
     - "İncele" - Kodu incele ve öneriler sun
     - "Kapat" - Asistanı kapat

## 🛠️ Özelleştirme

Tüm ayarlar `src/config.json` dosyasında toplanmıştır. Bu ayarları düzenleyerek asistanın davranışlarını özelleştirebilirsiniz:

### 🤖 AI Model Ayarları
```json
{
    "ai": {
        "default_model": "qwen2.5-coder:7b",
        "models": {
            "qwen2.5-coder:7b": {
                "temperature": 0.8,
                "top_p": 0.95,
                "max_tokens": 4096,
                "context_window": 16384,
                "system_prompt": "..."
            }
        }
    }
}
```

- **Model Seçenekleri:**
  - `default_model`: Varsayılan olarak kullanılacak model
  - `temperature`: Yaratıcılık seviyesi (0.0-1.0)
  - `top_p`: Olasılık eşiği
  - `max_tokens`: Maksimum token sayısı
  - `context_window`: Bağlam penceresi boyutu
  - `system_prompt`: Model kişiliği ve görev tanımı

### 🌐 Dil ve Konuşma Ayarları
```json
{
    "language": {
        "default": "tr",
        "available": ["tr", "en", "es", "fr", "de"]
    },
    "speech": {
        "recognition": {
            "engine": "google",
            "language": "tr-TR",
            "timeout": 5
        },
        "synthesis": {
            "engine": "sapi5",
            "voice": "tr",
            "rate": 150,
            "volume": 0.9
        }
    }
}
```

- **Dil Ayarları:**
  - `default`: Varsayılan dil
  - `available`: Kullanılabilir diller

- **Ses Tanıma:**
  - `engine`: Tanıma motoru (google, sphinx)
  - `language`: Tanıma dili
  - `timeout`: Dinleme zaman aşımı (saniye)

- **Ses Sentezi:**
  - `engine`: Sentez motoru (sapi5, espeak)
  - `voice`: Ses dili
  - `rate`: Konuşma hızı
  - `volume`: Ses seviyesi (0.0-1.0)

### ⚙️ Sistem ve Arayüz Ayarları
```json
{
    "system": {
        "volume_step": 10,
        "brightness_step": 10,
        "screenshot_dir": "screenshots",
        "log_dir": "data/logs",
        "default_apps": {
            "browser": "chrome",
            "editor": "code",
            "terminal": "cmd"
        },
        "keyboard_shortcuts": {
            "stop": "ctrl+c",
            "pause": "space",
            "screenshot": "ctrl+shift+s"
        }
    },
    "gui": {
        "theme": "dark",
        "font_size": 12,
        "window_size": {
            "width": 800,
            "height": 600
        },
        "opacity": 0.95
    }
}
```

- **Sistem Ayarları:**
  - `volume_step`: Ses değişim adımı
  - `brightness_step`: Parlaklık değişim adımı
  - `screenshot_dir`: Ekran görüntüsü klasörü
  - `log_dir`: Log dosyaları klasörü
  - `default_apps`: Varsayılan uygulamalar
  - `keyboard_shortcuts`: Kısayol tuşları

- **Arayüz Ayarları:**
  - `theme`: Tema (dark/light)
  - `font_size`: Yazı boyutu
  - `window_size`: Pencere boyutu
  - `opacity`: Pencere şeffaflığı

### 💡 Programatik Kullanım

Ayarları kod içinden değiştirmek için `ConfigManager` sınıfını kullanabilirsiniz:

```python
# Model değiştirme
config_manager.set_model("codellama:13b")

# Model parametrelerini güncelleme
config_manager.update_model_config("qwen2.5-coder:7b", {
    "temperature": 0.9,
    "max_tokens": 8192
})

# Dil değiştirme
config_manager.get_config("language")["default"] = "en"

# Ses ayarlarını güncelleme
speech_config = config_manager.get_config("speech")
speech_config["synthesis"]["rate"] = 180
```

Tüm ayarlar otomatik olarak kaydedilir ve uygulamayı yeniden başlattığınızda yüklenir.

## 🔍 Hata Ayıklama

- Detaylı hata logları (`data/errors.json`)
- Çökme raporları (`data/crashes.log`)
- Debug logları (`data/debug.log`)
- Hata analizi ve çözüm önerileri
- "hataları göster" komutu ile son hataları görüntüleme

## 📝 Notlar

- Ekran okuma özelliği için Tesseract OCR'ın doğru kurulduğundan emin olun
- Ses sentezi için sistem dilinin ve ses paketlerinin yüklü olduğunu kontrol edin
- Windows dışı sistemlerde bazı özellikler sınırlı olabilir
- Yüksek DPI ekranlarda ekran okuma hassasiyeti değişebilir
- Güvenlik nedeniyle sistem komutları için onay istenir
- Uygulama kapatma işlemleri için onay gereklidir

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Branch'inizi push edin
5. Pull Request oluşturun

## 📄 Lisans

MIT License





