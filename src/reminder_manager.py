from datetime import datetime, timedelta
import json
import os
from pathlib import Path

class ReminderManager:
    def __init__(self):
        self.reminders_file = Path("data/reminders.json")
        self.reminders_file.parent.mkdir(exist_ok=True)
        self.load_reminders()
        
    def load_reminders(self):
        """Kayıtlı hatırlatıcıları yükle"""
        if self.reminders_file.exists():
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                self.reminders = json.load(f)
        else:
            self.reminders = []
            
    def save_reminders(self):
        """Hatırlatıcıları kaydet"""
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(self.reminders, f, ensure_ascii=False, indent=2)
            
    def add_reminder(self, text, when):
        """Yeni hatırlatıcı ekle"""
        reminder = {
            "text": text,
            "when": when,
            "created_at": datetime.now().isoformat()
        }
        self.reminders.append(reminder)
        self.save_reminders()
        return f"Hatırlatıcı eklendi: {text} - {when}"
        
    def get_due_reminders(self):
        """Zamanı gelen hatırlatıcıları getir"""
        now = datetime.now()
        due_reminders = []
        remaining_reminders = []
        
        for reminder in self.reminders:
            when = datetime.fromisoformat(reminder["when"])
            if when <= now:
                due_reminders.append(reminder)
            else:
                remaining_reminders.append(reminder)
                
        self.reminders = remaining_reminders
        self.save_reminders()
        return due_reminders 