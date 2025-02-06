from enum import Enum
from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict, Optional

class TaskStatus(Enum):
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
    BLOCKED = "Blocked"

class TaskPriority(Enum):
    LOW = "Düşük"
    MEDIUM = "Orta"
    HIGH = "Yüksek"

class Task:
    def __init__(self, title: str, description: str = "", priority: TaskPriority = TaskPriority.MEDIUM):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.title = title
        self.description = description
        self.status = TaskStatus.TODO
        self.priority = priority
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.started_at = None
        self.completed_at = None
        self.related_todos = []  # Kod içindeki ilgili TODO'lar
        self.notes = []  # Task ile ilgili notlar
        
class TaskBoard:
    def __init__(self):
        self.tasks_file = Path("data/tasks.json")
        self.tasks_file.parent.mkdir(exist_ok=True)
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()
        
    def load_tasks(self):
        """Kayıtlı görevleri yükle"""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_data in data:
                    task = Task(task_data['title'])
                    task.__dict__.update(task_data)
                    task.status = TaskStatus(task_data['status'])
                    task.priority = TaskPriority(task_data['priority'])
                    self.tasks[task.id] = task
                    
    def save_tasks(self):
        """Görevleri kaydet"""
        tasks_data = []
        for task in self.tasks.values():
            task_dict = task.__dict__.copy()
            task_dict['status'] = task.status.value
            task_dict['priority'] = task.priority.value
            tasks_data.append(task_dict)
            
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks_data, f, ensure_ascii=False, indent=2)
            
    def add_task(self, title: str, description: str = "", priority: str = "MEDIUM") -> Task:
        """Yeni görev ekle"""
        task = Task(title, description, TaskPriority[priority.upper()])
        self.tasks[task.id] = task
        self.save_tasks()
        return task
        
    def update_task_status(self, task_id: str, new_status: TaskStatus) -> Optional[Task]:
        """Görev durumunu güncelle"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            old_status = task.status
            task.status = new_status
            task.updated_at = datetime.now().isoformat()
            
            if new_status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.now().isoformat()
            elif new_status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now().isoformat()
                
            self.save_tasks()
            return task
        return None
        
    def add_note_to_task(self, task_id: str, note: str) -> bool:
        """Göreve not ekle"""
        if task_id in self.tasks:
            self.tasks[task_id].notes.append({
                'text': note,
                'created_at': datetime.now().isoformat()
            })
            self.save_tasks()
            return True
        return False
        
    def link_todo_to_task(self, task_id: str, file_path: str, todo_text: str) -> bool:
        """Göreve TODO bağla"""
        if task_id in self.tasks:
            self.tasks[task_id].related_todos.append({
                'file': file_path,
                'text': todo_text,
                'linked_at': datetime.now().isoformat()
            })
            self.save_tasks()
            return True
        return False
        
    def get_board_view(self) -> Dict[str, List[Task]]:
        """Kanban board görünümü için görevleri grupla"""
        board = {status.value: [] for status in TaskStatus}
        for task in self.tasks.values():
            board[task.status.value].append(task)
        return board
        
    def get_task_details(self, task_id: str) -> Optional[Dict]:
        """Görev detaylarını getir"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status.value,
                'priority': task.priority.value,
                'created_at': task.created_at,
                'started_at': task.started_at,
                'completed_at': task.completed_at,
                'notes': task.notes,
                'todos': task.related_todos
            }
        return None 