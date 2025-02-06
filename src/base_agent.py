from src.error_handler import ErrorHandler
from PyQt6.QtCore import QObject, pyqtSignal

class BaseAgent(QObject):
    # Sinyaller
    confirmation_requested = pyqtSignal(str)
    confirmation_response = None

    def __init__(self):
        super().__init__()
        self.error_handler = ErrorHandler()
        
    def process_command(self, cmd: str) -> str:
        """
        Temel komut işleme metodu. 
        Alt sınıflar bu metodu override etmeli.
        """
        raise NotImplementedError("Bu metod alt sınıfta implement edilmeli")
        
    def wait_for_confirmation(self) -> str:
        """
        Kullanıcıdan onay bekle.
        Alt sınıflar bu metodu override edebilir.
        """
        return "hayır"  # Varsayılan yanıt 