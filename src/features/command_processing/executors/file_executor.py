"""
File Command Executor
Handles file operations (open, save, delete, copy, move, list)
"""

import asyncio
import logging
import os
import shutil
import subprocess
import platform
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..command_classifier import CommandCategory
from ..nlp_engine import ProcessedCommand, IntentType
from ..command_executor import BaseExecutor, CommandResult, ExecutionStatus

logger = logging.getLogger(__name__)


class FileManager:
    """Manages file operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.platform = platform.system().lower()
        self._is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize file manager"""
        try:
            self._is_initialized = True
            self.logger.info("File manager initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize file manager: {e}")
            return False
    
    async def open_file(self, file_path: str) -> bool:
        """Open file with default application"""
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return False
            
            if self.platform == "windows":
                os.startfile(file_path)
            elif self.platform == "linux":
                subprocess.run(["xdg-open", file_path])
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False
            
            self.logger.info(f"Opened file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening file {file_path}: {e}")
            return False
    
    async def save_file(self, content: str, file_path: str) -> bool:
        """Save content to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Saved file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving file {file_path}: {e}")
            return False
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file or directory"""
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"File not found: {file_path}")
                return True  # Consider it successful if file doesn't exist
            
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                self.logger.info(f"Deleted directory: {file_path}")
            else:
                os.remove(file_path)
                self.logger.info(f"Deleted file: {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting {file_path}: {e}")
            return False
    
    async def copy_file(self, source_path: str, dest_path: str) -> bool:
        """Copy file or directory"""
        try:
            if not os.path.exists(source_path):
                self.logger.error(f"Source not found: {source_path}")
                return False
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
                self.logger.info(f"Copied directory: {source_path} -> {dest_path}")
            else:
                shutil.copy2(source_path, dest_path)
                self.logger.info(f"Copied file: {source_path} -> {dest_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error copying {source_path} to {dest_path}: {e}")
            return False
    
    async def move_file(self, source_path: str, dest_path: str) -> bool:
        """Move file or directory"""
        try:
            if not os.path.exists(source_path):
                self.logger.error(f"Source not found: {source_path}")
                return False
            
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            shutil.move(source_path, dest_path)
            self.logger.info(f"Moved: {source_path} -> {dest_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error moving {source_path} to {dest_path}: {e}")
            return False
    
    async def list_files(self, directory_path: str = None) -> List[Dict[str, Any]]:
        """List files in directory"""
        try:
            if directory_path is None:
                directory_path = os.getcwd()
            
            if not os.path.exists(directory_path):
                self.logger.error(f"Directory not found: {directory_path}")
                return []
            
            files = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                try:
                    stat = os.stat(item_path)
                    files.append({
                        'name': item,
                        'path': item_path,
                        'size': stat.st_size,
                        'is_directory': os.path.isdir(item_path),
                        'modified': stat.st_mtime
                    })
                except OSError:
                    continue
            
            # Sort by name
            files.sort(key=lambda x: x['name'])
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing files in {directory_path}: {e}")
            return []
    
    async def create_directory(self, directory_path: str) -> bool:
        """Create directory"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            self.logger.info(f"Created directory: {directory_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating directory {directory_path}: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            stat = os.stat(file_path)
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": stat.st_size,
                "is_directory": os.path.isdir(file_path),
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "permissions": oct(stat.st_mode)[-3:]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            return {"error": str(e)}
    
    def search_files(self, directory_path: str, pattern: str) -> List[Dict[str, Any]]:
        """Search for files matching pattern"""
        try:
            import fnmatch
            
            matches = []
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if fnmatch.fnmatch(file.lower(), pattern.lower()):
                        file_path = os.path.join(root, file)
                        matches.append(self.get_file_info(file_path))
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            return []


class FileExecutor(BaseExecutor):
    """Executor for file operation commands"""
    
    def __init__(self):
        super().__init__()
        self.file_manager = FileManager()
        self._is_running = False
    
    def can_handle(self, command: ProcessedCommand) -> bool:
        """Check if this executor can handle the command"""
        return command.category == CommandCategory.FILE
    
    async def execute(self, command: ProcessedCommand) -> CommandResult:
        """Execute file command"""
        try:
            self._is_running = True
            self.logger.info(f"Executing file command: {command.action}")
            
            if command.action == "open_file":
                return await self._execute_open_file(command)
            elif command.action == "save_file":
                return await self._execute_save_file(command)
            elif command.action == "delete_file":
                return await self._execute_delete_file(command)
            elif command.action == "copy_file":
                return await self._execute_copy_file(command)
            elif command.action == "move_file":
                return await self._execute_move_file(command)
            elif command.action == "list_files":
                return await self._execute_list_files(command)
            elif command.action == "create_directory":
                return await self._execute_create_directory(command)
            elif command.action == "search_files":
                return await self._execute_search_files(command)
            else:
                return self._create_result(
                    success=False,
                    message=f"Unknown file action: {command.action}",
                    status=ExecutionStatus.FAILED
                )
        
        except Exception as e:
            self.logger.error(f"Error executing file command: {e}")
            return self._create_result(
                success=False,
                message=f"Error executing file command: {e}",
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
        finally:
            self._is_running = False
    
    async def _execute_open_file(self, command: ProcessedCommand) -> CommandResult:
        """Execute open file command"""
        file_path = command.parameters.get('file_path', '')
        if not file_path:
            return self._create_result(
                success=False,
                message="No file path provided",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.file_manager.open_file(file_path)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Opened file: {file_path}",
                data={"file_path": file_path}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to open file: {file_path}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_save_file(self, command: ProcessedCommand) -> CommandResult:
        """Execute save file command"""
        file_path = command.parameters.get('file_path', '')
        content = command.parameters.get('content', '')
        
        if not file_path:
            return self._create_result(
                success=False,
                message="No file path provided",
                status=ExecutionStatus.FAILED
            )
        
        if not content:
            return self._create_result(
                success=False,
                message="No content provided",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.file_manager.save_file(content, file_path)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Saved file: {file_path}",
                data={"file_path": file_path, "content_length": len(content)}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to save file: {file_path}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_delete_file(self, command: ProcessedCommand) -> CommandResult:
        """Execute delete file command"""
        file_path = command.parameters.get('file_path', '')
        if not file_path:
            return self._create_result(
                success=False,
                message="No file path provided",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.file_manager.delete_file(file_path)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Deleted: {file_path}",
                data={"file_path": file_path}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to delete: {file_path}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_copy_file(self, command: ProcessedCommand) -> CommandResult:
        """Execute copy file command"""
        source_path = command.parameters.get('source_path', '')
        dest_path = command.parameters.get('dest_path', '')
        
        if not source_path or not dest_path:
            return self._create_result(
                success=False,
                message="Source and destination paths required",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.file_manager.copy_file(source_path, dest_path)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Copied: {source_path} -> {dest_path}",
                data={"source_path": source_path, "dest_path": dest_path}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to copy: {source_path} -> {dest_path}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_move_file(self, command: ProcessedCommand) -> CommandResult:
        """Execute move file command"""
        source_path = command.parameters.get('source_path', '')
        dest_path = command.parameters.get('dest_path', '')
        
        if not source_path or not dest_path:
            return self._create_result(
                success=False,
                message="Source and destination paths required",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.file_manager.move_file(source_path, dest_path)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Moved: {source_path} -> {dest_path}",
                data={"source_path": source_path, "dest_path": dest_path}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to move: {source_path} -> {dest_path}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_list_files(self, command: ProcessedCommand) -> CommandResult:
        """Execute list files command"""
        directory_path = command.parameters.get('directory_path', os.getcwd())
        
        files = await self.file_manager.list_files(directory_path)
        
        return self._create_result(
            success=True,
            message=f"Listed {len(files)} items in {directory_path}",
            data={"files": files, "directory": directory_path, "count": len(files)}
        )
    
    async def _execute_create_directory(self, command: ProcessedCommand) -> CommandResult:
        """Execute create directory command"""
        directory_path = command.parameters.get('directory_path', '')
        if not directory_path:
            return self._create_result(
                success=False,
                message="No directory path provided",
                status=ExecutionStatus.FAILED
            )
        
        success = await self.file_manager.create_directory(directory_path)
        
        if success:
            return self._create_result(
                success=True,
                message=f"Created directory: {directory_path}",
                data={"directory_path": directory_path}
            )
        else:
            return self._create_result(
                success=False,
                message=f"Failed to create directory: {directory_path}",
                status=ExecutionStatus.FAILED
            )
    
    async def _execute_search_files(self, command: ProcessedCommand) -> CommandResult:
        """Execute search files command"""
        directory_path = command.parameters.get('directory_path', os.getcwd())
        pattern = command.parameters.get('pattern', '*')
        
        matches = self.file_manager.search_files(directory_path, pattern)
        
        return self._create_result(
            success=True,
            message=f"Found {len(matches)} files matching '{pattern}'",
            data={"matches": matches, "pattern": pattern, "count": len(matches)}
        )
    
    def cleanup(self) -> None:
        """Cleanup executor resources"""
        self._is_running = False
        self.logger.info("File executor cleaned up")
