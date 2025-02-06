from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QTextEdit, QPushButton, QLabel, QProgressBar, QScrollArea, QHBoxLayout, QDialog, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QFont, QIcon, QTextCursor
import sys
from voice_listener import VoiceListener
from code_agent import CodeEditorAgent

class ChatBubble(QLabel):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {'#DCF8C6' if is_user else '#E8E8E8'};
                border-radius: 10px;
                padding: 10px;
                margin: {'10px 50px 10px 10px' if is_user else '10px 10px 10px 50px'};
                color: #000000;
                font-weight: bold;
                font-size: 14px;
            }}
        """)

class VoiceListenerThread(QThread):
    text_received = pyqtSignal(str)
    command_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.listener = VoiceListener()
        self.listener.text_detected.connect(lambda x: self.text_received.emit(x))
        self.listener.command_detected.connect(lambda x: self.command_received.emit(x))

    def run(self):
        self.listener.start_listening()

    def stop(self):
        self.listener.stop_listening()

class AIResponseThread(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, agent, command):
        super().__init__()
        self.agent = agent
        self.command = command
        
    def run(self):
        try:
            response = self.agent.process_command(self.command)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))

class AICodeEditorGUI(QMainWindow):
    confirmation_response = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.agent = CodeEditorAgent()
        self.init_ui()
        self.start_voice_listener()
        self.setup_confirmation_dialog()
        
    def init_ui(self):
        self.setWindowTitle('AI Code Editor Assistant')
        self.setGeometry(100, 100, 800, 600)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Status ve mikrofon durumu
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Başlatılıyor...")
        self.mic_status = QLabel("🎤 ...")
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.mic_status)
        layout.addLayout(status_layout)
        
        # Chat alanı
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.addStretch()
        
        scroll.setWidget(self.chat_widget)
        layout.addWidget(scroll)
        
        # Scroll alanını sakla
        self.scroll_area = scroll
        
        # Kontrol butonları
        button_layout = QHBoxLayout()
        
        # Dil seçimi için combobox
        self.language_combo = QComboBox()
        languages = self.agent.language_manager.get_available_languages()
        for lang_code in languages:
            self.language_combo.addItem(lang_code.upper(), lang_code)
        
        # Mevcut dili seç
        current_index = self.language_combo.findData(self.agent.language_manager.current_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        
        self.language_combo.currentIndexChanged.connect(self.change_language)
        button_layout.addWidget(self.language_combo)
        
        # Başlat/Durdur butonları
        self.start_button = QPushButton("Başlat")
        self.stop_button = QPushButton("Durdur")
        
        self.start_button.clicked.connect(self.start_voice_listener)
        self.stop_button.clicked.connect(self.stop_voice_listener)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        self.apply_styles()

    def add_chat_message(self, text, is_user=True):
        """Chat mesajı ekle ve otomatik scroll"""
        bubble = ChatBubble(text, is_user)
        # Son mesajdan önceki stretch'i kaldır
        self.chat_layout.takeAt(self.chat_layout.count() - 1)
        # Yeni mesajı ekle
        self.chat_layout.addWidget(bubble)
        # Yeni stretch ekle
        self.chat_layout.addStretch()
        
        # Scroll'u en alta kaydır
        QTimer.singleShot(100, self._scroll_to_bottom)
        
    def _scroll_to_bottom(self):
        """Chat alanını en alta kaydır"""
        vsb = self.scroll_area.verticalScrollBar()
        vsb.setValue(vsb.maximum())
        
    def start_voice_listener(self):
        self.voice_thread = VoiceListenerThread()
        self.voice_thread.text_received.connect(self.update_mic_status)
        self.voice_thread.command_received.connect(self.handle_command)
        self.voice_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def handle_command(self, command):
        """Komutu işle ve AI yanıtını al"""
        self.add_chat_message(command, True)  # Kullanıcı mesajını göster
        
        # Yeni thread oluştur
        self.response_thread = AIResponseThread(self.agent, command)
        self.response_thread.response_ready.connect(
            lambda response: self.add_chat_message(response, False)
        )
        self.response_thread.error_occurred.connect(
            lambda error: self.add_chat_message(f"Hata: {error}", False)
        )
        self.response_thread.start()

    def stop_voice_listener(self):
        if hasattr(self, 'voice_thread'):
            self.voice_thread.stop()
            self.voice_thread.wait()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Dinleme durduruldu")
        
    def update_status(self, status):
        self.status_label.setText(status)
        
    def update_mic_status(self, text):
        self.mic_status.setText(text)
        
    def apply_styles(self):
        """Arayüz stillerini uygula"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
            QPushButton:pressed {
                background-color: #004c80;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QComboBox {
                padding: 8px;
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #007acc;
                border-radius: 4px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3c3c;
                color: white;
                selection-background-color: #007acc;
            }
        """)

    def closeEvent(self, event):
        """Uygulama kapatılırken onay iste"""
        reply = QMessageBox.question(
            self,
            self.agent.language_manager.get_message("confirm_close_title"),
            self.agent.language_manager.get_message("confirm_close"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Voice listener'ı durdur
            self.stop_voice_listener()
            # Kapatma işlemini onayla
            event.accept()
            # Uygulamayı tamamen kapat
            QApplication.quit()
        else:
            event.ignore()
            
    def close_application(self):
        """Uygulamayı programatik olarak kapat"""
        self.close()

    def setup_confirmation_dialog(self):
        """Onay dialog penceresini hazırla"""
        self.confirmation_dialog = QDialog(self)
        self.confirmation_dialog.setWindowTitle(
            self.agent.language_manager.get_message("confirm_dialog_title")
        )
        
        layout = QVBoxLayout()
        
        self.confirm_label = QLabel()
        layout.addWidget(self.confirm_label)
        
        button_layout = QHBoxLayout()
        
        self.yes_button = QPushButton(self.agent.language_manager.get_message("yes"))
        self.no_button = QPushButton(self.agent.language_manager.get_message("no"))
        
        self.yes_button.clicked.connect(lambda: self.handle_confirmation("evet"))
        self.no_button.clicked.connect(lambda: self.handle_confirmation("hayır"))
        
        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.no_button)
        
        layout.addLayout(button_layout)
        self.confirmation_dialog.setLayout(layout)
        
    def show_confirmation_dialog(self, message):
        """Onay dialogunu göster"""
        self.confirm_label.setText(message)
        self.confirmation_dialog.exec()
        
    def handle_confirmation(self, response):
        """Onay yanıtını işle"""
        self.confirmation_response.emit(response)
        self.confirmation_dialog.close()

    def show_error_dialog(self, message: str):
        """Hata dialogu göster"""
        reply = QMessageBox.question(
            self,
            self.agent.language_manager.get_message("error_dialog_title"),
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def show_welcome_message(self):
        """Hoş geldin mesajını göster"""
        welcome_text = """
        🤖 AI Kod Editör Asistanına Hoş Geldiniz!
        
        Kullanılabilir Komutlar:
        1. 'Hey Alimer' diyerek beni aktifleştirebilirsiniz
        2. Kod geliştirme için: 'geliştir', 'ekle', 'yaz', 'oluştur'
        3. Kod inceleme için: 'incele', 'kontrol et', 'review'
        4. Çıkmak için: 'Hey Alimer dur' veya 'dur'
        
        İyi çalışmalar! 🚀
        """
        self.update_chat(welcome_text, is_user=False)

    def change_language(self):
        """Dili değiştir"""
        lang_code = self.language_combo.currentData()
        if self.agent.language_manager.set_language(lang_code):
            # Arayüzü güncelle
            self.update_ui_texts()
        
    def update_ui_texts(self):
        """Arayüz metinlerini güncelle"""
        self.start_button.setText(self.agent.get_message("button_start"))
        self.stop_button.setText(self.agent.get_message("button_stop"))
        # ... diğer UI metinleri ...

def main():
    app = QApplication(sys.argv)
    window = AICodeEditorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 