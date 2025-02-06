from datetime import datetime
import json
from pathlib import Path
import re

class ContextReminder:
    def __init__(self):
        self.reminders_file = Path("data/context_reminders.json")
        self.reminders_file.parent.mkdir(exist_ok=True)
        self.current_context = None
        self.load_reminders()
        
    def load_reminders(self):
        """Kayıtlı bağlamsal hatırlatıcıları yükle"""
        if self.reminders_file.exists():
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                self.reminders = json.load(f)
        else:
            self.reminders = {
                "context_based": {},  # Bağlama göre hatırlatıcılar
                "general": []         # Genel hatırlatıcılar
            }
            
    def save_reminders(self):
        """Hatırlatıcıları kaydet"""
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(self.reminders, f, ensure_ascii=False, indent=2)
            
    def add_reminder(self, text: str, context: str = None):
        """Yeni hatırlatıcı ekle"""
        reminder = {
            "text": text,
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        
        if context:
            # Bağlama özel hatırlatıcı
            if context not in self.reminders["context_based"]:
                self.reminders["context_based"][context] = []
            self.reminders["context_based"][context].append(reminder)
        else:
            # Genel hatırlatıcı
            self.reminders["general"].append(reminder)
            
        self.save_reminders()
        return f"✅ Hatırlatıcı eklendi: {text}"
        
    def set_current_context(self, context: str):
        """Mevcut bağlamı ayarla"""
        self.current_context = context
        # Bağlamla ilgili hatırlatıcıları kontrol et
        return self.get_context_reminders(context)
        
    def get_context_reminders(self, context: str = None):
        """Belirli bir bağlamdaki hatırlatıcıları getir"""
        if not context:
            context = self.current_context
            
        if context and context in self.reminders["context_based"]:
            active_reminders = [r for r in self.reminders["context_based"][context] 
                              if not r["completed"]]
            if active_reminders:
                return f"Bu işlem için hatırlatıcılar:\n" + "\n".join(
                    f"- {r['text']}" for r in active_reminders
                )
        return None
        
    def get_all_reminders(self):
        """Tüm aktif hatırlatıcıları getir"""
        output = []
        
        # Bağlama özel hatırlatıcılar
        for context, reminders in self.reminders["context_based"].items():
            active = [r for r in reminders if not r["completed"]]
            if active:
                output.append(f"\n📌 {context} için hatırlatıcılar:")
                output.extend(f"  - {r['text']}" for r in active)
                
        # Genel hatırlatıcılar
        general = [r for r in self.reminders["general"] if not r["completed"]]
        if general:
            output.append("\n📝 Genel hatırlatıcılar:")
            output.extend(f"  - {r['text']}" for r in general)
            
        return "\n".join(output) if output else "Aktif hatırlatıcı bulunmuyor."
        
    def mark_completed(self, text: str, context: str = None):
        """Hatırlatıcıyı tamamlandı olarak işaretle"""
        if context and context in self.reminders["context_based"]:
            for r in self.reminders["context_based"][context]:
                if r["text"].lower() == text.lower() and not r["completed"]:
                    r["completed"] = True
                    self.save_reminders()
                    return True
                    
        for r in self.reminders["general"]:
            if r["text"].lower() == text.lower() and not r["completed"]:
                r["completed"] = True
                self.save_reminders()
                return True
                
        return False 