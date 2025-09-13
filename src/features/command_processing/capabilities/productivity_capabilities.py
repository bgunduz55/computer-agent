"""
Productivity Capability Executors

Implements concrete executors for productivity operations including
text editing, file management, note-taking, and document creation.
"""

import asyncio
import logging
import os
import platform
import subprocess
import webbrowser
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from ..capability_system import BaseCapabilityExecutor

logger = logging.getLogger(__name__)

class TextEditorExecutor(BaseCapabilityExecutor):
    """Executor for text editing operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text editing operation"""
        try:
            action = parameters.get('action', 'open')
            file_path = parameters.get('file_path', '')
            content = parameters.get('content', '')
            editor = parameters.get('editor', 'notepad')
            line_number = parameters.get('line_number', 1)
            
            if action == "open":
                return await self._open_editor(file_path, editor, line_number)
            elif action == "create":
                return await self._create_file(file_path, content)
            elif action == "search_replace":
                return await self._search_replace(file_path, parameters.get('search_text', ''), parameters.get('replace_text', ''))
            elif action == "count":
                return await self._count_text(file_path)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing text editor operation: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if text editor operation can be executed"""
        action = parameters.get('action', 'open')
        return action in ['open', 'create', 'search_replace', 'count']
    
    async def _open_editor(self, file_path: str, editor: str, line_number: int) -> Dict[str, Any]:
        """Open text editor with file"""
        try:
            if platform.system() == "Windows":
                if editor == "notepad":
                    cmd = ["notepad", file_path] if file_path else ["notepad"]
                elif editor == "notepad++":
                    cmd = ["notepad++", file_path] if file_path else ["notepad++"]
                elif editor == "vscode":
                    cmd = ["code", file_path] if file_path else ["code"]
                else:
                    cmd = ["notepad", file_path] if file_path else ["notepad"]
            else:
                if editor == "vim":
                    cmd = ["vim", file_path] if file_path else ["vim"]
                elif editor == "nano":
                    cmd = ["nano", file_path] if file_path else ["nano"]
                elif editor == "gedit":
                    cmd = ["gedit", file_path] if file_path else ["gedit"]
                elif editor == "vscode":
                    cmd = ["code", file_path] if file_path else ["code"]
                else:
                    cmd = ["nano", file_path] if file_path else ["nano"]
            
            if line_number > 1 and editor in ["vim", "nano"]:
                cmd.extend(["+", str(line_number)])
            
            subprocess.Popen(cmd)
            return {"success": True, "message": f"Opened {file_path} in {editor}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to open editor: {e}"}
    
    async def _create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Create a new text file with content"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {"success": True, "message": f"Created file: {file_path}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to create file: {e}"}
    
    async def _search_replace(self, file_path: str, search_text: str, replace_text: str) -> Dict[str, Any]:
        """Search and replace text in file"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Perform replacement
            new_content = content.replace(search_text, replace_text)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {"success": True, "message": f"Replaced '{search_text}' with '{replace_text}' in {file_path}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to search and replace: {e}"}
    
    async def _count_text(self, file_path: str) -> Dict[str, Any]:
        """Count lines, words, and characters in file"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = len(content.splitlines())
            words = len(content.split())
            characters = len(content)
            
            return {
                "success": True,
                "data": {
                    "lines": lines,
                    "words": words,
                    "characters": characters
                },
                "message": f"File {file_path}: {lines} lines, {words} words, {characters} characters"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to count text: {e}"}

class FileManagerExecutor(BaseCapabilityExecutor):
    """Executor for file management operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file management operation"""
        try:
            action = parameters.get('action', 'list')
            path = parameters.get('path', '.')
            file_name = parameters.get('file_name', '')
            new_name = parameters.get('new_name', '')
            
            if action == "list":
                return await self._list_files(path)
            elif action == "create":
                return await self._create_file(path, file_name)
            elif action == "delete":
                return await self._delete_file(path, file_name)
            elif action == "rename":
                return await self._rename_file(path, file_name, new_name)
            elif action == "copy":
                return await self._copy_file(path, file_name, parameters.get('destination', ''))
            elif action == "move":
                return await self._move_file(path, file_name, parameters.get('destination', ''))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing file management operation: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if file management operation can be executed"""
        action = parameters.get('action', 'list')
        return action in ['list', 'create', 'delete', 'rename', 'copy', 'move']
    
    async def _list_files(self, path: str) -> Dict[str, Any]:
        """List files and directories"""
        try:
            if not os.path.exists(path):
                return {"success": False, "error": f"Path not found: {path}"}
            
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                items.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            
            return {
                "success": True,
                "data": items,
                "message": f"Listed {len(items)} items in {path}"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to list files: {e}"}
    
    async def _create_file(self, path: str, file_name: str) -> Dict[str, Any]:
        """Create a new file"""
        try:
            file_path = os.path.join(path, file_name)
            
            # Create directory if it doesn't exist
            os.makedirs(path, exist_ok=True)
            
            # Create empty file
            with open(file_path, 'w') as f:
                pass
            
            return {"success": True, "message": f"Created file: {file_path}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to create file: {e}"}
    
    async def _delete_file(self, path: str, file_name: str) -> Dict[str, Any]:
        """Delete a file or directory"""
        try:
            file_path = os.path.join(path, file_name)
            
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}
            
            if os.path.isdir(file_path):
                os.rmdir(file_path)
                return {"success": True, "message": f"Deleted directory: {file_path}"}
            else:
                os.remove(file_path)
                return {"success": True, "message": f"Deleted file: {file_path}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to delete file: {e}"}
    
    async def _rename_file(self, path: str, file_name: str, new_name: str) -> Dict[str, Any]:
        """Rename a file or directory"""
        try:
            old_path = os.path.join(path, file_name)
            new_path = os.path.join(path, new_name)
            
            if not os.path.exists(old_path):
                return {"success": False, "error": f"File not found: {old_path}"}
            
            os.rename(old_path, new_path)
            return {"success": True, "message": f"Renamed {file_name} to {new_name}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to rename file: {e}"}
    
    async def _copy_file(self, path: str, file_name: str, destination: str) -> Dict[str, Any]:
        """Copy a file to destination"""
        try:
            source_path = os.path.join(path, file_name)
            
            if not os.path.exists(source_path):
                return {"success": False, "error": f"File not found: {source_path}"}
            
            # Create destination directory if it doesn't exist
            os.makedirs(destination, exist_ok=True)
            
            dest_path = os.path.join(destination, file_name)
            
            if os.path.isdir(source_path):
                # Copy directory recursively
                import shutil
                shutil.copytree(source_path, dest_path)
            else:
                # Copy file
                import shutil
                shutil.copy2(source_path, dest_path)
            
            return {"success": True, "message": f"Copied {file_name} to {destination}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to copy file: {e}"}
    
    async def _move_file(self, path: str, file_name: str, destination: str) -> Dict[str, Any]:
        """Move a file to destination"""
        try:
            source_path = os.path.join(path, file_name)
            
            if not os.path.exists(source_path):
                return {"success": False, "error": f"File not found: {source_path}"}
            
            # Create destination directory if it doesn't exist
            os.makedirs(destination, exist_ok=True)
            
            dest_path = os.path.join(destination, file_name)
            
            if os.path.isdir(source_path):
                # Move directory
                import shutil
                shutil.move(source_path, dest_path)
            else:
                # Move file
                import shutil
                shutil.move(source_path, dest_path)
            
            return {"success": True, "message": f"Moved {file_name} to {destination}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to move file: {e}"}

class NoteTakingExecutor(BaseCapabilityExecutor):
    """Executor for note-taking operations"""
    
    def __init__(self):
        super().__init__()
        self.notes_dir = "notes"
        os.makedirs(self.notes_dir, exist_ok=True)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute note-taking operation"""
        try:
            action = parameters.get('action', 'create')
            title = parameters.get('title', '')
            content = parameters.get('content', '')
            category = parameters.get('category', 'general')
            tags = parameters.get('tags', [])
            priority = parameters.get('priority', 'medium')
            
            if action == "create":
                return await self._create_note(title, content, category, tags, priority)
            elif action == "list":
                return await self._list_notes(category, tags)
            elif action == "search":
                return await self._search_notes(parameters.get('query', ''))
            elif action == "get":
                return await self._get_note(title)
            elif action == "update":
                return await self._update_note(title, content)
            elif action == "delete":
                return await self._delete_note(title)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error executing note-taking operation: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if note-taking operation can be executed"""
        action = parameters.get('action', 'create')
        return action in ['create', 'list', 'search', 'get', 'update', 'delete']
    
    async def _create_note(self, title: str, content: str, category: str, tags: List[str], priority: str) -> Dict[str, Any]:
        """Create a new note"""
        try:
            # Sanitize title for filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            file_path = os.path.join(self.notes_dir, f"{safe_title}.md")
            
            # Create note content
            note_content = f"""# {title}

**Category:** {category}  
**Priority:** {priority}  
**Tags:** {', '.join(tags) if tags else 'None'}  
**Created:** {datetime.now().isoformat()}

---

{content}
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            return {"success": True, "message": f"Created note: {title}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to create note: {e}"}
    
    async def _list_notes(self, category: str, tags: List[str]) -> Dict[str, Any]:
        """List all notes"""
        try:
            notes = []
            
            for filename in os.listdir(self.notes_dir):
                if filename.endswith('.md'):
                    file_path = os.path.join(self.notes_dir, filename)
                    stat = os.stat(file_path)
                    
                    # Read note metadata
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    title = lines[0].replace('# ', '').strip() if lines else filename
                    
                    notes.append({
                        "title": title,
                        "filename": filename,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "size": stat.st_size
                    })
            
            return {
                "success": True,
                "data": notes,
                "message": f"Found {len(notes)} notes"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to list notes: {e}"}
    
    async def _search_notes(self, query: str) -> Dict[str, Any]:
        """Search through notes"""
        try:
            results = []
            
            for filename in os.listdir(self.notes_dir):
                if filename.endswith('.md'):
                    file_path = os.path.join(self.notes_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if query.lower() in content.lower():
                        lines = content.split('\n')
                        title = lines[0].replace('# ', '').strip() if lines else filename
                        
                        results.append({
                            "title": title,
                            "filename": filename,
                            "matches": content.lower().count(query.lower())
                        })
            
            return {
                "success": True,
                "data": results,
                "message": f"Found {len(results)} notes matching '{query}'"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to search notes: {e}"}
    
    async def _get_note(self, title: str) -> Dict[str, Any]:
        """Get a specific note"""
        try:
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            file_path = os.path.join(self.notes_dir, f"{safe_title}.md")
            
            if not os.path.exists(file_path):
                return {"success": False, "error": f"Note not found: {title}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "data": {"title": title, "content": content},
                "message": f"Retrieved note: {title}"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get note: {e}"}
    
    async def _update_note(self, title: str, content: str) -> Dict[str, Any]:
        """Update an existing note"""
        try:
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            file_path = os.path.join(self.notes_dir, f"{safe_title}.md")
            
            if not os.path.exists(file_path):
                return {"success": False, "error": f"Note not found: {title}"}
            
            # Read existing note to preserve metadata
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Extract metadata
            metadata_lines = []
            content_start = 0
            for i, line in enumerate(lines):
                if line.startswith('---'):
                    content_start = i + 1
                    break
                metadata_lines.append(line)
            
            # Create updated note
            updated_content = ''.join(metadata_lines) + "---\n\n" + content
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return {"success": True, "message": f"Updated note: {title}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to update note: {e}"}
    
    async def _delete_note(self, title: str) -> Dict[str, Any]:
        """Delete a note"""
        try:
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            file_path = os.path.join(self.notes_dir, f"{safe_title}.md")
            
            if not os.path.exists(file_path):
                return {"success": False, "error": f"Note not found: {title}"}
            
            os.remove(file_path)
            return {"success": True, "message": f"Deleted note: {title}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to delete note: {e}"}

class ApplicationLauncherExecutor(BaseCapabilityExecutor):
    """Executor for application launching operations"""
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute application launching operation"""
        try:
            # Support both old and new parameter names
            app_name = parameters.get('application_name') or parameters.get('app_name', '')
            app_path = parameters.get('app_path', '')
            arguments = parameters.get('arguments', [])
            
            if not app_name:
                return {"success": False, "error": "No application name provided"}
            
            return await self._launch_application(app_name, app_path, arguments)
                
        except Exception as e:
            logger.error(f"Error executing application launcher operation: {e}")
            return {"success": False, "error": str(e)}
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if application launcher operation can be executed"""
        return "application_name" in parameters or "app_name" in parameters
    
    async def _launch_application(self, app_name: str, app_path: str = "", arguments: List[str] = None) -> Dict[str, Any]:
        """Launch an application"""
        try:
            if app_path:
                cmd = [app_path] + arguments
            else:
                # Try to find application by name
                cmd = await self._find_application(app_name)
                if not cmd:
                    return {"success": False, "error": f"Application not found: {app_name}"}
                cmd.extend(arguments)
            
            subprocess.Popen(cmd)
            return {"success": True, "message": f"Launched application: {app_name}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to launch application: {e}"}
    
    async def _find_application(self, app_name: str) -> Optional[List[str]]:
        """Find application executable by name"""
        try:
            if platform.system() == "Windows":
                # Common Windows applications
                apps = {
                    "notepad": ["notepad.exe"],
                    "calculator": ["calc.exe"],
                    "paint": ["mspaint.exe"],
                    "chrome": ["chrome.exe"],
                    "firefox": ["firefox.exe"],
                    "edge": ["msedge.exe"],
                    "vscode": ["code.exe"],
                    "explorer": ["explorer.exe"]
                }
            else:
                # Common Linux applications
                apps = {
                    "notepad": ["gedit"],
                    "calculator": ["gnome-calculator"],
                    "paint": ["gimp"],
                    "chrome": ["google-chrome"],
                    "firefox": ["firefox"],
                    "vscode": ["code"],
                    "explorer": ["nautilus"]
                }
            
            return apps.get(app_name.lower())
            
        except Exception:
            return None
    
    async def _close_application(self, app_name: str) -> Dict[str, Any]:
        """Close an application"""
        try:
            if platform.system() == "Windows":
                if app_name.lower() == "notepad":
                    subprocess.run(["taskkill", "/f", "/im", "notepad.exe"], check=False)
                elif app_name.lower() == "calculator":
                    subprocess.run(["taskkill", "/f", "/im", "calc.exe"], check=False)
                elif app_name.lower() == "chrome":
                    subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=False)
                elif app_name.lower() == "firefox":
                    subprocess.run(["taskkill", "/f", "/im", "firefox.exe"], check=False)
                else:
                    subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], check=False)
            else:
                subprocess.run(["pkill", app_name], check=False)
            
            return {"success": True, "message": f"Closed application: {app_name}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to close application: {e}"}
    
    async def _list_applications(self) -> Dict[str, Any]:
        """List running applications"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["tasklist"], capture_output=True, text=True, check=True)
                processes = result.stdout.split('\n')[3:]  # Skip header lines
                apps = []
                for process in processes:
                    if process.strip():
                        parts = process.split()
                        if len(parts) >= 1:
                            apps.append({"name": parts[0], "pid": parts[1] if len(parts) > 1 else "N/A"})
            else:
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True, check=True)
                processes = result.stdout.split('\n')[1:]  # Skip header line
                apps = []
                for process in processes:
                    if process.strip():
                        parts = process.split()
                        if len(parts) >= 11:
                            apps.append({"name": parts[10], "pid": parts[1]})
            
            return {
                "success": True,
                "data": apps,
                "message": f"Found {len(apps)} running applications"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to list applications: {e}"}

# Export all executors
__all__ = [
    'TextEditorExecutor',
    'FileManagerExecutor',
    'NoteTakingExecutor',
    'ApplicationLauncherExecutor'
]
