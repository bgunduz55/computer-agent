# 🏗️ JARVIS Computer Assistant - Proje Yapısı

## 📁 Detaylı Klasör Organizasyonu

```
computer-assistant/
├── 📁 src/                           # Ana kaynak kod dizini
│   ├── 📁 core/                      # Çekirdek iş mantığı
│   │   ├── 📁 domain/                # Domain entities ve value objects
│   │   │   ├── 📄 entities/          # Domain entities
│   │   │   │   ├── user.py           # Kullanıcı entity
│   │   │   │   ├── command.py        # Komut entity
│   │   │   │   ├── session.py        # Oturum entity
│   │   │   │   └── plugin.py         # Plugin entity
│   │   │   ├── 📄 value_objects/     # Value objects
│   │   │   │   ├── voice_settings.py # Ses ayarları
│   │   │   │   ├── ai_config.py      # AI konfigürasyonu
│   │   │   │   └── system_info.py    # Sistem bilgileri
│   │   │   └── 📄 repositories/      # Repository interfaces
│   │   │       ├── user_repository.py
│   │   │       ├── command_repository.py
│   │   │       └── session_repository.py
│   │   ├── 📁 application/           # Use cases ve application services
│   │   │   ├── 📄 use_cases/         # Use case'ler
│   │   │   │   ├── voice_recognition_use_case.py
│   │   │   │   ├── ai_processing_use_case.py
│   │   │   │   ├── system_control_use_case.py
│   │   │   │   └── user_management_use_case.py
│   │   │   ├── 📄 services/          # Application services
│   │   │   │   ├── voice_service.py
│   │   │   │   ├── ai_service.py
│   │   │   │   ├── system_service.py
│   │   │   │   └── user_service.py
│   │   │   └── 📄 dto/               # Data Transfer Objects
│   │   │       ├── voice_dto.py
│   │   │       ├── command_dto.py
│   │   │       └── response_dto.py
│   │   └── 📁 infrastructure/        # External dependencies
│   │       ├── 📄 repositories/      # Repository implementations
│   │       │   ├── sqlite_user_repository.py
│   │       │   ├── file_command_repository.py
│   │       │   └── memory_session_repository.py
│   │       ├── 📄 external_services/ # External service integrations
│   │       │   ├── openai_client.py
│   │       │   ├── gemini_client.py
│   │       │   └── ollama_client.py
│   │       └── 📄 config/            # Configuration management
│   │           ├── settings.py
│   │           ├── database_config.py
│   │           └── logging_config.py
│   ├── 📁 features/                  # Feature modules
│   │   ├── 📁 voice_recognition/     # Ses tanıma özelliği
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 voice_engine.py    # Ses tanıma motoru
│   │   │   ├── 📄 wake_word_detector.py # Wake word tespiti
│   │   │   ├── 📄 noise_filter.py    # Gürültü filtreleme
│   │   │   └── 📄 voice_commands.py  # Ses komutları
│   │   ├── 📁 ai_integration/        # AI entegrasyonu
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 ai_provider_manager.py # AI provider yönetimi
│   │   │   ├── 📄 rag_system.py      # RAG sistemi
│   │   │   ├── 📄 context_manager.py # Bağlam yönetimi
│   │   │   └── 📄 providers/         # AI provider'lar
│   │   │       ├── 📄 ollama_provider.py
│   │   │       ├── 📄 openai_provider.py
│   │   │       ├── 📄 gemini_provider.py
│   │   │       └── 📄 openrouter_provider.py
│   │   ├── 📁 system_control/        # Sistem kontrolü
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 system_controller.py # Sistem kontrolcüsü
│   │   │   ├── 📄 app_manager.py     # Uygulama yöneticisi
│   │   │   ├── 📄 window_manager.py  # Pencere yöneticisi
│   │   │   └── 📄 terminal_manager.py # Terminal yöneticisi
│   │   ├── 📁 remote_control/        # Uzak kontrol
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 websocket_server.py # WebSocket sunucu
│   │   │   ├── 📄 command_router.py  # Komut yönlendirici
│   │   │   ├── 📄 authentication.py  # Kimlik doğrulama
│   │   │   └── 📄 file_transfer.py   # Dosya transferi
│   │   └── 📁 media_control/         # Medya kontrolü
│   │       ├── 📄 __init__.py
│   │       ├── 📄 media_manager.py   # Medya yöneticisi
│   │       ├── 📄 youtube_controller.py # YouTube kontrolü
│   │       └── 📄 audio_controller.py # Ses kontrolü
│   ├── 📁 shared/                    # Paylaşılan bileşenler
│   │   ├── 📄 utils/                 # Utility fonksiyonları
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 file_utils.py      # Dosya işlemleri
│   │   │   ├── 📄 string_utils.py    # String işlemleri
│   │   │   ├── 📄 date_utils.py      # Tarih işlemleri
│   │   │   └── 📄 validation_utils.py # Doğrulama işlemleri
│   │   ├── 📄 exceptions/            # Özel exception'lar
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 base_exceptions.py # Temel exception'lar
│   │   │   ├── 📄 voice_exceptions.py # Ses tanıma exception'ları
│   │   │   ├── 📄 ai_exceptions.py   # AI exception'ları
│   │   │   └── 📄 system_exceptions.py # Sistem exception'ları
│   │   ├── 📄 constants/             # Sabitler
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 voice_constants.py # Ses tanıma sabitleri
│   │   │   ├── 📄 ai_constants.py    # AI sabitleri
│   │   │   └── 📄 system_constants.py # Sistem sabitleri
│   │   └── 📄 decorators/            # Decorator'lar
│   │       ├── 📄 __init__.py
│   │       ├── 📄 retry_decorator.py # Retry decorator
│   │       ├── 📄 cache_decorator.py # Cache decorator
│   │       └── 📄 logging_decorator.py # Logging decorator
│   ├── 📁 plugins/                   # Plugin sistemi
│   │   ├── 📄 __init__.py
│   │   ├── 📄 plugin_manager.py      # Plugin yöneticisi
│   │   ├── 📄 plugin_loader.py       # Plugin yükleyici
│   │   ├── 📄 plugin_registry.py     # Plugin kayıt sistemi
│   │   ├── 📄 base_plugin.py         # Temel plugin sınıfı
│   │   ├── 📁 core_plugins/          # Temel plugin'ler
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 voice_plugin.py    # Ses tanıma plugin'i
│   │   │   ├── 📄 ai_plugin.py       # AI plugin'i
│   │   │   └── 📄 system_plugin.py   # Sistem plugin'i
│   │   ├── 📁 community_plugins/     # Topluluk plugin'leri
│   │   │   └── 📄 README.md
│   │   └── 📁 custom_plugins/        # Özel plugin'ler
│   │       └── 📄 README.md
│   ├── 📁 api/                       # API katmanı
│   │   ├── 📄 __init__.py
│   │   ├── 📁 rest/                  # REST API
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 app.py             # FastAPI uygulaması
│   │   │   ├── 📄 routes/            # API route'ları
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 voice_routes.py
│   │   │   │   ├── 📄 ai_routes.py
│   │   │   │   ├── 📄 system_routes.py
│   │   │   │   └── 📄 user_routes.py
│   │   │   ├── 📄 middleware/        # Middleware'ler
│   │   │   │   ├── 📄 __init__.py
│   │   │   │   ├── 📄 auth_middleware.py
│   │   │   │   ├── 📄 cors_middleware.py
│   │   │   │   └── 📄 logging_middleware.py
│   │   │   └── 📄 schemas/           # Pydantic şemaları
│   │   │       ├── 📄 __init__.py
│   │   │       ├── 📄 voice_schemas.py
│   │   │       ├── 📄 ai_schemas.py
│   │   │       └── 📄 system_schemas.py
│   │   └── 📁 websocket/             # WebSocket API
│   │       ├── 📄 __init__.py
│   │       ├── 📄 websocket_server.py
│   │       ├── 📄 message_handler.py
│   │       └── 📄 connection_manager.py
│   ├── 📁 ui/                        # Kullanıcı arayüzü
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main_window.py         # Ana pencere
│   │   ├── 📄 settings_dialog.py     # Ayarlar dialog'u
│   │   ├── 📄 components/            # UI bileşenleri
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 voice_panel.py     # Ses paneli
│   │   │   ├── 📄 command_panel.py   # Komut paneli
│   │   │   ├── 📄 status_panel.py    # Durum paneli
│   │   │   └── 📄 settings_panel.py  # Ayarlar paneli
│   │   └── 📄 styles/                # Stil dosyaları
│   │       ├── 📄 main_style.qss
│   │       ├── 📄 dark_theme.qss
│   │       └── 📄 light_theme.qss
│   ├── 📁 monitoring/                # İzleme sistemi
│   │   ├── 📄 __init__.py
│   │   ├── 📄 system_monitor.py      # Sistem izleyici
│   │   ├── 📄 performance_monitor.py # Performans izleyici
│   │   ├── 📄 health_checker.py      # Sağlık kontrolü
│   │   └── 📄 metrics_collector.py   # Metrik toplayıcı
│   ├── 📁 security/                  # Güvenlik sistemi
│   │   ├── 📄 __init__.py
│   │   ├── 📄 authentication.py      # Kimlik doğrulama
│   │   ├── 📄 authorization.py       # Yetkilendirme
│   │   ├── 📄 encryption.py          # Şifreleme
│   │   └── 📄 audit_logger.py        # Denetim kayıtları
│   └── 📄 main.py                    # Ana uygulama dosyası
├── 📁 tests/                         # Test dosyaları
│   ├── 📄 __init__.py
│   ├── 📁 unit/                      # Unit testler
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_voice_recognition.py
│   │   ├── 📄 test_ai_providers.py
│   │   ├── 📄 test_system_control.py
│   │   └── 📄 test_user_management.py
│   ├── 📁 integration/               # Integration testler
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_voice_to_command.py
│   │   ├── 📄 test_ai_integration.py
│   │   └── 📄 test_websocket_communication.py
│   ├── 📁 e2e/                       # End-to-end testler
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_complete_workflow.py
│   │   ├── 📄 test_multi_user_scenarios.py
│   │   └── 📄 test_performance_scenarios.py
│   ├── 📁 fixtures/                  # Test fixtures
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_data/             # Test verileri
│   │   ├── 📄 mock_services/         # Mock servisler
│   │   └── 📄 test_configs/          # Test konfigürasyonları
│   └── 📁 utils/                     # Test utilities
│       ├── 📄 __init__.py
│       ├── 📄 test_helpers.py
│       └── 📄 mock_factory.py
├── 📁 docs/                          # Dokümantasyon
│   ├── 📄 api/                       # API dokümantasyonu
│   │   ├── 📄 rest_api.md
│   │   ├── 📄 websocket_api.md
│   │   └── 📄 plugin_api.md
│   ├── 📄 user_guide/                # Kullanıcı kılavuzu
│   │   ├── 📄 getting_started.md
│   │   ├── 📄 voice_commands.md
│   │   ├── 📄 settings.md
│   │   └── 📄 troubleshooting.md
│   ├── 📄 developer/                 # Geliştirici dokümantasyonu
│   │   ├── 📄 architecture.md
│   │   ├── 📄 plugin_development.md
│   │   ├── 📄 contributing.md
│   │   └── 📄 code_style.md
│   └── 📄 deployment/                # Dağıtım dokümantasyonu
│       ├── 📄 installation.md
│       ├── 📄 configuration.md
│       └── 📄 maintenance.md
├── 📁 config/                        # Konfigürasyon dosyaları
│   ├── 📄 default.json               # Varsayılan ayarlar
│   ├── 📄 user.json                  # Kullanıcı ayarları
│   ├── 📄 schema.json                # JSON şeması
│   └── 📄 environments/              # Ortam ayarları
│       ├── 📄 development.json
│       ├── 📄 staging.json
│       └── 📄 production.json
├── 📁 data/                          # Veri dosyaları
│   ├── 📁 backups/                   # Yedek dosyaları
│   ├── 📁 logs/                      # Log dosyaları
│   ├── 📁 cache/                     # Cache dosyaları
│   ├── 📁 temp/                      # Geçici dosyalar
│   └── 📁 security/                  # Güvenlik dosyaları
├── 📁 scripts/                       # Yardımcı scriptler
│   ├── 📄 setup.py                   # Kurulum scripti
│   ├── 📄 install_dependencies.py    # Bağımlılık kurulumu
│   ├── 📄 run_tests.py               # Test çalıştırma
│   └── 📄 build.py                   # Build scripti
├── 📁 assets/                        # Statik dosyalar
│   ├── 📁 icons/                     # İkon dosyaları
│   ├── 📁 sounds/                    # Ses dosyaları
│   ├── 📁 images/                    # Görsel dosyalar
│   └── 📁 themes/                    # Tema dosyaları
├── 📁 computer-assistant-flutter/    # Flutter mobil uygulaması
│   ├── 📁 lib/                       # Dart kaynak kodları
│   │   ├── 📁 core/                  # Çekirdek modüller
│   │   ├── 📁 features/              # Özellik modülleri
│   │   ├── 📁 shared/                # Paylaşılan bileşenler
│   │   └── 📄 main.dart              # Ana uygulama dosyası
│   ├── 📁 assets/                    # Flutter asset'leri
│   ├── 📁 test/                      # Flutter testleri
│   └── 📄 pubspec.yaml               # Flutter bağımlılıkları
├── 📁 .github/                       # GitHub Actions
│   └── 📁 workflows/
│       ├── 📄 ci-cd.yml              # CI/CD pipeline
│       ├── 📄 security-scan.yml      # Güvenlik taraması
│       └── 📄 release.yml            # Release pipeline
├── 📄 .cursorrules                   # Cursor rules
├── 📄 .gitignore                     # Git ignore
├── 📄 .env.example                   # Environment variables örneği
├── 📄 .pre-commit-config.yaml        # Pre-commit hooks
├── 📄 pyproject.toml                 # Python proje konfigürasyonu
├── 📄 requirements.txt               # Python bağımlılıkları
├── 📄 requirements-dev.txt           # Geliştirme bağımlılıkları
├── 📄 Dockerfile                     # Docker konfigürasyonu
├── 📄 docker-compose.yml             # Docker Compose
├── 📄 pytest.ini                    # Pytest konfigürasyonu
├── 📄 mypy.ini                       # MyPy konfigürasyonu
├── 📄 .flake8                        # Flake8 konfigürasyonu
├── 📄 .pylintrc                      # Pylint konfigürasyonu
├── 📄 README.md                      # Proje açıklaması
├── 📄 JARVIS_DEVELOPMENT_PLAN.md     # Geliştirme planı
├── 📄 PROJECT_STRUCTURE.md           # Proje yapısı (bu dosya)
└── 📄 CHANGELOG.md                   # Değişiklik geçmişi
```

## 🎯 Klasör Açıklamaları

### 📁 src/core/
**Amaç**: Temel iş mantığı ve domain katmanı
- **domain/**: Domain entities, value objects ve repository interfaces
- **application/**: Use case'ler ve application services
- **infrastructure/**: External dependencies ve repository implementations

### 📁 src/features/
**Amaç**: Özellik bazlı modüler yapı
- Her özellik kendi klasöründe
- Bağımsız olarak geliştirilebilir
- Plugin sistemi ile genişletilebilir

### 📁 src/shared/
**Amaç**: Tüm modüller arasında paylaşılan bileşenler
- Utility fonksiyonları
- Custom exception'lar
- Sabitler ve decorator'lar

### 📁 src/plugins/
**Amaç**: Modüler plugin sistemi
- Core plugins: Temel özellikler
- Community plugins: Topluluk eklentileri
- Custom plugins: Özel eklentiler

### 📁 src/api/
**Amaç**: API katmanı
- REST API: HTTP tabanlı API
- WebSocket API: Real-time communication

### 📁 tests/
**Amaç**: Kapsamlı test stratejisi
- Unit tests: Tekil bileşen testleri
- Integration tests: Bileşen entegrasyon testleri
- E2E tests: End-to-end senaryo testleri

### 📁 docs/
**Amaç**: Kapsamlı dokümantasyon
- API dokümantasyonu
- Kullanıcı kılavuzu
- Geliştirici dokümantasyonu

## 🔧 Konfigürasyon Dosyaları

### Python Proje Konfigürasyonu
- **pyproject.toml**: Modern Python proje konfigürasyonu
- **requirements.txt**: Production bağımlılıkları
- **requirements-dev.txt**: Development bağımlılıkları

### Test Konfigürasyonu
- **pytest.ini**: Pytest ayarları
- **.coverage**: Coverage raporu
- **test_configs/**: Test ortamı konfigürasyonları

### Code Quality
- **.flake8**: Flake8 linting ayarları
- **.pylintrc**: Pylint ayarları
- **mypy.ini**: Type checking ayarları
- **.pre-commit-config.yaml**: Pre-commit hooks

### CI/CD
- **.github/workflows/**: GitHub Actions workflows
- **Dockerfile**: Container konfigürasyonu
- **docker-compose.yml**: Multi-container setup

## 🚀 Kurulum ve Çalıştırma

### Geliştirme Ortamı Kurulumu
```bash
# Repository'yi klonla
git clone <repository-url>
cd computer-assistant

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Pre-commit hooks kur
pre-commit install

# Testleri çalıştır
pytest tests/

# Uygulamayı çalıştır
python src/main.py
```

### Docker ile Çalıştırma
```bash
# Docker image build et
docker build -t jarvis-assistant .

# Container çalıştır
docker run -p 8080:8080 -p 8765:8765 jarvis-assistant

# Docker Compose ile çalıştır
docker-compose up -d
```

Bu yapı, temiz kod prensipleri, modüler mimari ve enterprise-grade geliştirme standartlarına uygun olarak tasarlanmıştır. Her klasör ve dosya, belirli bir sorumluluğa sahip ve projenin genel mimarisine katkıda bulunmaktadır.
