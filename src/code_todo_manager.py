import re
from pathlib import Path
from datetime import datetime

class CodeTodoManager:
    def __init__(self):
        self.current_file = None
        self.todos = []
        
    def add_todo(self, message: str) -> bool:
        """Yeni TODO notu ekle"""
        try:
            todo = {
                'id': len(self.todos) + 1,
                'message': message,
                'created_at': datetime.now().isoformat(),
                'completed': False
            }
            self.todos.append(todo)
            self.save_todos()
            
            # Sesli yanıt değişikliği için TODO
            self.add_development_todo("Sesli yanıtları özelleştirilebilir hale getir (örn: 'Sizi dinliyorum' -> 'Hoop')")
            
            return True
        except Exception as e:
            self.logger.error(f"TODO eklenirken hata: {str(e)}")
            return False

    def add_development_todo(self, message: str) -> bool:
        """Geliştirme ile ilgili TODO notu ekle"""
        try:
            todo = {
                'id': len(self.todos) + 1,
                'message': f"[DEV] {message}",
                'created_at': datetime.now().isoformat(),
                'completed': False,
                'type': 'development'
            }
            self.todos.append(todo)
            self.save_todos()
            return True
        except Exception as e:
            self.logger.error(f"Geliştirme TODO'su eklenirken hata: {str(e)}")
            return False
        
    def add_todo(self, file_path: str, message: str, line_number: int = None):
        """Kod dosyasına TODO notu ekle"""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"❌ Dosya bulunamadı: {file_path}"
                
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Eğer satır numarası belirtilmemişse, uygun bir yer bul
            if line_number is None:
                line_number = self._find_suitable_line(lines)
                
            # TODO notunu hazırla
            indent = self._get_indent(lines[line_number-1]) if lines else ""
            todo = f"{indent}# TODO: {message} (Eklendi: {datetime.now().strftime('%Y-%m-%d %H:%M')})\n"
            
            # TODO notunu ekle
            lines.insert(line_number, todo)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            return f"✅ TODO notu eklendi: {message}"
            
        except Exception as e:
            return f"❌ TODO notu eklenirken hata oluştu: {str(e)}"
            
    def _find_suitable_line(self, lines: list) -> int:
        """TODO notu için uygun satırı bul"""
        # Fonksiyon tanımlamalarını bul
        function_lines = []
        for i, line in enumerate(lines):
            if re.match(r'^\s*(?:def|class)\s+\w+', line):
                function_lines.append(i)
                
        if not function_lines:
            return 0  # Dosya boşsa başa ekle
            
        # En son fonksiyon tanımından sonraki satıra ekle
        return function_lines[-1] + 1
        
    def _get_indent(self, line: str) -> str:
        """Satırın girinti seviyesini al"""
        return re.match(r'^\s*', line).group()
        
    def get_todos(self, file_path: str = None) -> list:
        """Dosyadaki TODO notlarını listele"""
        todos = []
        try:
            if file_path:
                path = Path(file_path)
                if not path.exists():
                    return []
                    
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines, 1):
                    if '# TODO:' in line:
                        todos.append({
                            'file': file_path,
                            'line': i,
                            'text': line.strip()
                        })
                        
            return todos
            
        except Exception:
            return [] 