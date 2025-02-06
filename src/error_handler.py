import traceback
from datetime import datetime
from pathlib import Path
import json
import logging
import sys
import os

class ErrorHandler:
    def __init__(self):
        # Log dizinini oluştur
        self.log_dir = Path("data")
        self.log_dir.mkdir(exist_ok=True)
        
        # Log dosyaları
        self.errors_file = self.log_dir / "errors.json"
        self.crash_file = self.log_dir / "crashes.log"
        self.debug_file = self.log_dir / "debug.log"
        
        # Logging ayarlarını yapılandır
        logging.basicConfig(
            filename=self.debug_file,
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('AICodeEditor')
        
        # Konsola da log gönder
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        
        # Hata listesini başlat/yükle
        self.load_errors()
        
        # Global exception handler'ı ayarla
        sys.excepthook = self.handle_uncaught_exception
        
    def load_errors(self):
        """Kayıtlı hataları yükle"""
        try:
            if self.errors_file.exists() and self.errors_file.stat().st_size > 0:
                with open(self.errors_file, 'r', encoding='utf-8') as f:
                    self.errors = json.load(f)
            else:
                # Dosya yoksa veya boşsa yeni liste oluştur
                self.errors = []
                # Boş JSON dosyası oluştur
                self.save_errors()
        except json.JSONDecodeError:
            # JSON dosyası bozuksa yeni liste oluştur
            self.logger.warning("Hata dosyası bozuk, yeni liste oluşturuluyor")
            self.errors = []
            self.save_errors()
        except Exception as e:
            self.logger.error(f"Hata dosyası yüklenirken beklenmeyen hata: {str(e)}")
            self.errors = []
            
    def save_errors(self):
        """Hataları kaydet"""
        try:
            with open(self.errors_file, 'w', encoding='utf-8') as f:
                json.dump(self.errors, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Hatalar kaydedilirken hata oluştu: {str(e)}")
            
    def handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Yakalanmamış hataları yakala ve logla"""
        try:
            error_data = {
                'timestamp': datetime.now().isoformat(),
                'error_type': exc_type.__name__,
                'error_message': str(exc_value),
                'traceback': ''.join(traceback.format_tb(exc_traceback)),
                'command': 'UNCAUGHT_EXCEPTION',
                'context': 'Global Exception Handler',
                'stack_info': ''.join(traceback.format_stack())
            }
            
            # Hatayı JSON dosyasına kaydet
            self.errors.append(error_data)
            self.save_errors()
            
            # Debug log'a yaz
            self.logger.error(
                f"Uncaught Exception:\nType: {exc_type.__name__}\n"
                f"Message: {str(exc_value)}\nTraceback:\n"
                f"{''.join(traceback.format_tb(exc_traceback))}"
            )
            
            # Crash log'a yaz
            with open(self.crash_file, 'a', encoding='utf-8') as f:
                f.write('\n' + '='*50 + '\n')
                f.write(f"CRASH REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Type: {exc_type.__name__}\n")
                f.write(f"Message: {str(exc_value)}\n")
                f.write("Traceback:\n")
                f.write(''.join(traceback.format_tb(exc_traceback)))
                f.write("Stack Info:\n")
                f.write(error_data['stack_info'])
                f.write('\n' + '='*50 + '\n')
                
        except Exception as e:
            print(f"Error while logging error: {str(e)}")
            print(traceback.format_exc())
            
    def log_error(self, error: Exception, command: str = None, context: str = None):
        """Hatayı kaydet"""
        try:
            error_data = {
                'timestamp': datetime.now().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc(),
                'command': command or 'Unknown Command',
                'context': context or 'Unknown Context',
                'stack_info': ''.join(traceback.format_stack())
            }
            
            self.errors.append(error_data)
            self.save_errors()
            
            # Debug log'a yaz
            self.logger.error(
                f"Error in {context or 'Unknown Context'}:\n"
                f"Command: {command or 'Unknown Command'}\n"
                f"Type: {type(error).__name__}\n"
                f"Message: {str(error)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            
            # Kritik hataları crash log'a da yaz
            if isinstance(error, (SystemError, RuntimeError, AttributeError, TypeError, KeyError)):
                with open(self.crash_file, 'a', encoding='utf-8') as f:
                    f.write('\n' + '='*50 + '\n')
                    f.write(f"ERROR REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Command: {command}\n")
                    f.write(f"Context: {context}\n")
                    f.write(f"Type: {type(error).__name__}\n")
                    f.write(f"Message: {str(error)}\n")
                    f.write("Traceback:\n")
                    f.write(traceback.format_exc())
                    f.write("Stack Info:\n")
                    f.write(error_data['stack_info'])
                    f.write('\n' + '='*50 + '\n')
                    
            return error_data
            
        except Exception as e:
            # Loglama sırasında hata oluşursa bunu konsola yaz
            print(f"Error while logging error: {str(e)}")
            print(traceback.format_exc())
            return None
        
    def show_error_details(self, error_data: dict):
        """Hata detaylarını göster"""
        details = [
            "🔍 Hata Detayları:",
            f"Zaman: {datetime.fromisoformat(error_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Tip: {error_data['error_type']}",
            f"Mesaj: {error_data['error_message']}",
            "\nKomut Bilgisi:",
            f"Komut: {error_data['command']}",
            f"Bağlam: {error_data['context']}",
            "\nHata İzleme:",
            error_data['traceback']
        ]
        
        # Hata detaylarını geçici bir dosyaya yaz
        temp_file = Path("temp_error.txt")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(details))
            
        # VS Code'u aç
        try:
            subprocess.run(['code', str(temp_file)])
        except Exception:
            # VS Code açılamazsa dosyayı varsayılan metin editörüyle aç
            os.startfile(temp_file)

    def analyze_recent_errors(self) -> dict:
        """Son hataları analiz et ve özet çıkar"""
        try:
            summary = {
                'total_errors': 0,
                'common_errors': {},
                'critical_errors': [],
                'last_error': None,
                'speech_errors': 0,
                'connection_errors': 0,
                'command_errors': 0
            }
            
            # Debug loglarını kontrol et
            if self.debug_file.exists():
                with open(self.debug_file, 'r', encoding='utf-8') as f:
                    logs = f.readlines()
                    for log in logs[-100:]:  # Son 100 log
                        if 'ERROR' in log:
                            summary['total_errors'] += 1
                            
                            # Konuşma hataları
                            if 'SAPI.SpVoice' in log or 'speak' in log.lower():
                                summary['speech_errors'] += 1
                                
                            # Bağlantı hataları    
                            if 'connection' in log.lower() or 'could not locate' in log.lower():
                                summary['connection_errors'] += 1
                                
                            # Komut hataları
                            if 'command' in log.lower() or 'not understood' in log.lower():
                                summary['command_errors'] += 1
                                
                            # Son hatayı kaydet
                            summary['last_error'] = log.strip()
            
            # Errors.json'ı kontrol et
            if self.errors_file.exists():
                with open(self.errors_file, 'r', encoding='utf-8') as f:
                    error_data = json.load(f)
                    for error in error_data:
                        error_type = error.get('error_type', '')
                        if error_type in summary['common_errors']:
                            summary['common_errors'][error_type] += 1
                        else:
                            summary['common_errors'][error_type] = 1
                            
                        if error.get('is_critical', False):
                            summary['critical_errors'].append(error)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Hata analizi sırasında hata: {str(e)}")
            return None
            
    def suggest_solutions(self, error_summary: dict) -> list:
        """Hata özetine göre çözüm önerileri sun"""
        solutions = []
        
        if error_summary['speech_errors'] > 0:
            solutions.append({
                'type': 'speech',
                'message': 'Ses motoru hataları tespit edildi',
                'suggestions': [
                    'Windows SAPI5 ayarlarını kontrol edin',
                    'Alternatif TTS motoru pyttsx3 kullanılabilir',
                    'Türkçe ses paketinin yüklü olduğundan emin olun'
                ]
            })
            
        if error_summary['connection_errors'] > 0:
            solutions.append({
                'type': 'connection',
                'message': 'Bağlantı hataları tespit edildi',
                'suggestions': [
                    'İnternet bağlantınızı kontrol edin',
                    'Güvenlik duvarı ayarlarını kontrol edin',
                    'Chrome yüklü ve PATH\'te olduğundan emin olun'
                ]
            })
            
        if error_summary['command_errors'] > 0:
            solutions.append({
                'type': 'command',
                'message': 'Komut algılama hataları tespit edildi',
                'suggestions': [
                    'Mikrofon ayarlarını kontrol edin',
                    'Ambient noise kalibrasyonunu tekrar yapın',
                    'Komut kelimelerini daha net söyleyin'
                ]
            })
            
        return solutions

    def handle_error_with_analysis(self, error: Exception, command: str = "", context: str = "") -> tuple:
        """Hatayı logla ve analiz et"""
        # Önce hatayı normal şekilde logla
        error_data = self.log_error(error, command, context)
        
        # Hata analizini yap
        error_summary = self.analyze_recent_errors()
        
        # Çözüm önerilerini al
        solutions = self.suggest_solutions(error_summary)
        
        return error_data, error_summary, solutions 