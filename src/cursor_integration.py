import subprocess
import os
import json
import requests
from pathlib import Path

class CursorIntegration:
    def __init__(self):
        self.cursor_path = self._find_cursor_path()
        
    def _find_cursor_path(self):
        """Cursor uygulamasının yolunu bulur"""
        # Windows için tipik kurulum yolu
        windows_path = r"C:\Users\{}\AppData\Local\Programs\Cursor\Cursor.exe".format(os.getenv("USERNAME"))
        if os.path.exists(windows_path):
            return windows_path
            
        # macOS için tipik kurulum yolu
        mac_path = "/Applications/Cursor.app/Contents/MacOS/Cursor"
        if os.path.exists(mac_path):
            return mac_path
            
        return None
        
    def open_cursor(self, file_path=None):
        """Cursor'u açar ve isteğe bağlı olarak belirtilen dosyayı açar"""
        if not self.cursor_path:
            raise Exception("Cursor uygulaması bulunamadı!")
            
        cmd = [self.cursor_path]
        if file_path:
            cmd.append(file_path)
            
        subprocess.Popen(cmd)
        
    def send_to_chat(self, message: str):
        """Cursor chat penceresine mesaj gönderir"""
        # Cursor'un yerel API'sine HTTP isteği gönder
        try:
            response = requests.post(
                "http://localhost:3000/api/chat",
                json={"message": message}
            )
            return response.json()
        except Exception as e:
            raise Exception(f"Cursor chat'e mesaj gönderilemedi: {str(e)}") 