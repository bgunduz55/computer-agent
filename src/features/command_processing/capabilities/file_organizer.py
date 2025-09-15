"""
File Organization Capabilities for JARVIS Computer Assistant

Provides advanced file organization, management, and batch operations.
"""

import asyncio
import logging
import os
import time
import shutil
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import glob
import re

logger = logging.getLogger(__name__)

class OrganizationRuleType(Enum):
    """File organization rule types"""
    BY_EXTENSION = "by_extension"
    BY_DATE = "by_date"
    BY_SIZE = "by_size"
    BY_NAME = "by_name"
    BY_TYPE = "by_type"
    BY_PATTERN = "by_pattern"
    BY_DUPLICATE = "by_duplicate"

class FileType(Enum):
    """File types for organization"""
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CODE = "code"
    EXECUTABLE = "executable"
    OTHER = "other"

@dataclass
class FileInfo:
    """File information structure"""
    path: str
    name: str
    size: int
    extension: str
    file_type: FileType
    created_at: datetime
    modified_at: datetime
    hash: Optional[str] = None
    duplicate_of: Optional[str] = None

@dataclass
class OrganizationResult:
    """Result of file organization operation"""
    success: bool
    files_processed: int
    files_moved: int
    files_organized: int
    duplicates_found: int
    execution_time: float
    errors: List[str] = None
    organized_files: List[str] = None

@dataclass
class OrganizationRule:
    """File organization rule definition"""
    name: str
    rule_type: OrganizationRuleType
    pattern: str
    target_folder: str
    enabled: bool = True
    description: Optional[str] = None

class FileTypeDetector:
    """Detects file types based on extensions and content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.extension_mapping = {
            # Documents
            '.txt': FileType.DOCUMENT, '.md': FileType.DOCUMENT, '.doc': FileType.DOCUMENT,
            '.docx': FileType.DOCUMENT, '.pdf': FileType.DOCUMENT, '.rtf': FileType.DOCUMENT,
            '.odt': FileType.DOCUMENT, '.pages': FileType.DOCUMENT,
            
            # Images
            '.jpg': FileType.IMAGE, '.jpeg': FileType.IMAGE, '.png': FileType.IMAGE,
            '.gif': FileType.IMAGE, '.bmp': FileType.IMAGE, '.tiff': FileType.IMAGE,
            '.svg': FileType.IMAGE, '.webp': FileType.IMAGE, '.ico': FileType.IMAGE,
            
            # Videos
            '.mp4': FileType.VIDEO, '.avi': FileType.VIDEO, '.mov': FileType.VIDEO,
            '.wmv': FileType.VIDEO, '.flv': FileType.VIDEO, '.webm': FileType.VIDEO,
            '.mkv': FileType.VIDEO, '.m4v': FileType.VIDEO,
            
            # Audio
            '.mp3': FileType.AUDIO, '.wav': FileType.AUDIO, '.flac': FileType.AUDIO,
            '.aac': FileType.AUDIO, '.ogg': FileType.AUDIO, '.wma': FileType.AUDIO,
            '.m4a': FileType.AUDIO, '.opus': FileType.AUDIO,
            
            # Archives
            '.zip': FileType.ARCHIVE, '.rar': FileType.ARCHIVE, '.7z': FileType.ARCHIVE,
            '.tar': FileType.ARCHIVE, '.gz': FileType.ARCHIVE, '.bz2': FileType.ARCHIVE,
            '.xz': FileType.ARCHIVE, '.cab': FileType.ARCHIVE,
            
            # Code
            '.py': FileType.CODE, '.js': FileType.CODE, '.html': FileType.CODE,
            '.css': FileType.CODE, '.java': FileType.CODE, '.cpp': FileType.CODE,
            '.c': FileType.CODE, '.h': FileType.CODE, '.php': FileType.CODE,
            '.rb': FileType.CODE, '.go': FileType.CODE, '.rs': FileType.CODE,
            '.ts': FileType.CODE, '.jsx': FileType.CODE, '.tsx': FileType.CODE,
            '.json': FileType.CODE, '.xml': FileType.CODE, '.yaml': FileType.CODE,
            '.yml': FileType.CODE, '.sql': FileType.CODE, '.sh': FileType.CODE,
            '.bat': FileType.CODE, '.ps1': FileType.CODE,
            
            # Executables
            '.exe': FileType.EXECUTABLE, '.msi': FileType.EXECUTABLE, '.deb': FileType.EXECUTABLE,
            '.rpm': FileType.EXECUTABLE, '.dmg': FileType.EXECUTABLE, '.app': FileType.EXECUTABLE,
            '.bin': FileType.EXECUTABLE, '.run': FileType.EXECUTABLE
        }
    
    def detect_file_type(self, file_path: str) -> FileType:
        """Detect file type from extension"""
        _, ext = os.path.splitext(file_path.lower())
        return self.extension_mapping.get(ext, FileType.OTHER)
    
    def get_file_category(self, file_type: FileType) -> str:
        """Get category name for file type"""
        category_mapping = {
            FileType.DOCUMENT: "Documents",
            FileType.IMAGE: "Images",
            FileType.VIDEO: "Videos",
            FileType.AUDIO: "Audio",
            FileType.ARCHIVE: "Archives",
            FileType.CODE: "Code",
            FileType.EXECUTABLE: "Executables",
            FileType.OTHER: "Other"
        }
        return category_mapping.get(file_type, "Other")

class DuplicateDetector:
    """Detects duplicate files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def find_duplicates(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """Find duplicate files by hash"""
        hash_groups = {}
        
        for file_path in file_paths:
            if os.path.isfile(file_path):
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    if file_hash not in hash_groups:
                        hash_groups[file_hash] = []
                    hash_groups[file_hash].append(file_path)
        
        # Return only groups with duplicates
        return {hash_val: files for hash_val, files in hash_groups.items() if len(files) > 1}

class FileOrganizer:
    """Main file organizer"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.type_detector = FileTypeDetector()
        self.duplicate_detector = DuplicateDetector()
        self.organization_rules: List[OrganizationRule] = []
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default organization rules"""
        default_rules = [
            OrganizationRule(
                name="Organize by File Type",
                rule_type=OrganizationRuleType.BY_TYPE,
                pattern="*",
                target_folder="organized",
                description="Organize files by their type (documents, images, etc.)"
            ),
            OrganizationRule(
                name="Organize by Extension",
                rule_type=OrganizationRuleType.BY_EXTENSION,
                pattern="*",
                target_folder="by_extension",
                description="Organize files by their file extension"
            ),
            OrganizationRule(
                name="Organize by Date",
                rule_type=OrganizationRuleType.BY_DATE,
                pattern="*",
                target_folder="by_date",
                description="Organize files by creation date"
            )
        ]
        
        self.organization_rules.extend(default_rules)
    
    async def organize_files(self, source_directory: str, target_directory: str,
                           rule_type: OrganizationRuleType, pattern: str = "*",
                           create_backup: bool = True) -> OrganizationResult:
        """Organize files according to specified rule"""
        start_time = time.time()
        files_processed = 0
        files_moved = 0
        files_organized = 0
        duplicates_found = 0
        errors = []
        organized_files = []
        
        try:
            # Create target directory
            os.makedirs(target_directory, exist_ok=True)
            
            # Find files matching pattern
            file_paths = self._find_files(source_directory, pattern)
            files_processed = len(file_paths)
            
            if files_processed == 0:
                return OrganizationResult(
                    success=True,
                    files_processed=0,
                    files_moved=0,
                    files_organized=0,
                    duplicates_found=0,
                    execution_time=time.time() - start_time,
                    organized_files=[]
                )
            
            # Create backup if requested
            if create_backup:
                backup_dir = os.path.join(target_directory, "backup")
                await self._create_backup(file_paths, backup_dir)
            
            # Find duplicates
            duplicates = self.duplicate_detector.find_duplicates(file_paths)
            duplicates_found = sum(len(files) - 1 for files in duplicates.values())
            
            # Organize files based on rule type
            if rule_type == OrganizationRuleType.BY_TYPE:
                files_moved, organized_files = await self._organize_by_type(
                    file_paths, target_directory
                )
            elif rule_type == OrganizationRuleType.BY_EXTENSION:
                files_moved, organized_files = await self._organize_by_extension(
                    file_paths, target_directory
                )
            elif rule_type == OrganizationRuleType.BY_DATE:
                files_moved, organized_files = await self._organize_by_date(
                    file_paths, target_directory
                )
            elif rule_type == OrganizationRuleType.BY_SIZE:
                files_moved, organized_files = await self._organize_by_size(
                    file_paths, target_directory
                )
            elif rule_type == OrganizationRuleType.BY_NAME:
                files_moved, organized_files = await self._organize_by_name(
                    file_paths, target_directory
                )
            elif rule_type == OrganizationRuleType.BY_PATTERN:
                files_moved, organized_files = await self._organize_by_pattern(
                    file_paths, target_directory, pattern
                )
            elif rule_type == OrganizationRuleType.BY_DUPLICATE:
                files_moved, organized_files = await self._organize_duplicates(
                    file_paths, target_directory, duplicates
                )
            
            files_organized = files_moved
            
            execution_time = time.time() - start_time
            
            return OrganizationResult(
                success=True,
                files_processed=files_processed,
                files_moved=files_moved,
                files_organized=files_organized,
                duplicates_found=duplicates_found,
                execution_time=execution_time,
                errors=errors,
                organized_files=organized_files
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            errors.append(str(e))
            
            return OrganizationResult(
                success=False,
                files_processed=files_processed,
                files_moved=files_moved,
                files_organized=files_organized,
                duplicates_found=duplicates_found,
                execution_time=execution_time,
                errors=errors,
                organized_files=organized_files
            )
    
    def _find_files(self, directory: str, pattern: str) -> List[str]:
        """Find files matching pattern in directory"""
        file_paths = []
        
        try:
            # Use glob to find files
            search_pattern = os.path.join(directory, "**", pattern)
            file_paths = glob.glob(search_pattern, recursive=True)
            
            # Filter out directories
            file_paths = [f for f in file_paths if os.path.isfile(f)]
            
        except Exception as e:
            self.logger.error(f"Error finding files: {e}")
        
        return file_paths
    
    async def _create_backup(self, file_paths: List[str], backup_dir: str):
        """Create backup of files before organization"""
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            for file_path in file_paths:
                if os.path.isfile(file_path):
                    # Create relative path structure in backup
                    rel_path = os.path.relpath(file_path, os.path.dirname(file_path))
                    backup_path = os.path.join(backup_dir, rel_path)
                    backup_file_dir = os.path.dirname(backup_path)
                    os.makedirs(backup_file_dir, exist_ok=True)
                    
                    shutil.copy2(file_path, backup_path)
                    
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
    
    async def _organize_by_type(self, file_paths: List[str], target_directory: str) -> Tuple[int, List[str]]:
        """Organize files by type"""
        files_moved = 0
        organized_files = []
        
        for file_path in file_paths:
            try:
                file_type = self.type_detector.detect_file_type(file_path)
                category = self.type_detector.get_file_category(file_type)
                
                # Create category directory
                category_dir = os.path.join(target_directory, category)
                os.makedirs(category_dir, exist_ok=True)
                
                # Move file
                filename = os.path.basename(file_path)
                target_path = os.path.join(category_dir, filename)
                
                # Handle filename conflicts
                target_path = self._resolve_filename_conflict(target_path)
                
                shutil.move(file_path, target_path)
                organized_files.append(target_path)
                files_moved += 1
                
            except Exception as e:
                self.logger.error(f"Error organizing file {file_path}: {e}")
        
        return files_moved, organized_files
    
    async def _organize_by_extension(self, file_paths: List[str], target_directory: str) -> Tuple[int, List[str]]:
        """Organize files by extension"""
        files_moved = 0
        organized_files = []
        
        for file_path in file_paths:
            try:
                _, ext = os.path.splitext(file_path)
                ext = ext.lower() if ext else "no_extension"
                
                # Create extension directory
                ext_dir = os.path.join(target_directory, ext[1:])  # Remove the dot
                os.makedirs(ext_dir, exist_ok=True)
                
                # Move file
                filename = os.path.basename(file_path)
                target_path = os.path.join(ext_dir, filename)
                
                # Handle filename conflicts
                target_path = self._resolve_filename_conflict(target_path)
                
                shutil.move(file_path, target_path)
                organized_files.append(target_path)
                files_moved += 1
                
            except Exception as e:
                self.logger.error(f"Error organizing file {file_path}: {e}")
        
        return files_moved, organized_files
    
    async def _organize_by_date(self, file_paths: List[str], target_directory: str) -> Tuple[int, List[str]]:
        """Organize files by creation date"""
        files_moved = 0
        organized_files = []
        
        for file_path in file_paths:
            try:
                # Get file creation time
                stat = os.stat(file_path)
                created_time = datetime.fromtimestamp(stat.st_ctime)
                
                # Create date directory (YYYY-MM format)
                date_dir = created_time.strftime("%Y-%m")
                target_date_dir = os.path.join(target_directory, date_dir)
                os.makedirs(target_date_dir, exist_ok=True)
                
                # Move file
                filename = os.path.basename(file_path)
                target_path = os.path.join(target_date_dir, filename)
                
                # Handle filename conflicts
                target_path = self._resolve_filename_conflict(target_path)
                
                shutil.move(file_path, target_path)
                organized_files.append(target_path)
                files_moved += 1
                
            except Exception as e:
                self.logger.error(f"Error organizing file {file_path}: {e}")
        
        return files_moved, organized_files
    
    async def _organize_by_size(self, file_paths: List[str], target_directory: str) -> Tuple[int, List[str]]:
        """Organize files by size"""
        files_moved = 0
        organized_files = []
        
        for file_path in file_paths:
            try:
                file_size = os.path.getsize(file_path)
                
                # Categorize by size
                if file_size < 1024:  # < 1KB
                    size_category = "tiny"
                elif file_size < 1024 * 1024:  # < 1MB
                    size_category = "small"
                elif file_size < 1024 * 1024 * 10:  # < 10MB
                    size_category = "medium"
                elif file_size < 1024 * 1024 * 100:  # < 100MB
                    size_category = "large"
                else:  # >= 100MB
                    size_category = "huge"
                
                # Create size category directory
                size_dir = os.path.join(target_directory, size_category)
                os.makedirs(size_dir, exist_ok=True)
                
                # Move file
                filename = os.path.basename(file_path)
                target_path = os.path.join(size_dir, filename)
                
                # Handle filename conflicts
                target_path = self._resolve_filename_conflict(target_path)
                
                shutil.move(file_path, target_path)
                organized_files.append(target_path)
                files_moved += 1
                
            except Exception as e:
                self.logger.error(f"Error organizing file {file_path}: {e}")
        
        return files_moved, organized_files
    
    async def _organize_by_name(self, file_paths: List[str], target_directory: str) -> Tuple[int, List[str]]:
        """Organize files by name (alphabetically)"""
        files_moved = 0
        organized_files = []
        
        # Sort files by name
        sorted_files = sorted(file_paths, key=lambda x: os.path.basename(x).lower())
        
        for file_path in sorted_files:
            try:
                filename = os.path.basename(file_path)
                first_letter = filename[0].upper() if filename else "0"
                
                # Create letter directory
                letter_dir = os.path.join(target_directory, first_letter)
                os.makedirs(letter_dir, exist_ok=True)
                
                # Move file
                target_path = os.path.join(letter_dir, filename)
                
                # Handle filename conflicts
                target_path = self._resolve_filename_conflict(target_path)
                
                shutil.move(file_path, target_path)
                organized_files.append(target_path)
                files_moved += 1
                
            except Exception as e:
                self.logger.error(f"Error organizing file {file_path}: {e}")
        
        return files_moved, organized_files
    
    async def _organize_by_pattern(self, file_paths: List[str], target_directory: str, pattern: str) -> Tuple[int, List[str]]:
        """Organize files by custom pattern"""
        files_moved = 0
        organized_files = []
        
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
        except re.error:
            self.logger.error(f"Invalid pattern: {pattern}")
            return files_moved, organized_files
        
        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                
                if compiled_pattern.search(filename):
                    # Create pattern match directory
                    pattern_dir = os.path.join(target_directory, "pattern_matches")
                    os.makedirs(pattern_dir, exist_ok=True)
                    
                    # Move file
                    target_path = os.path.join(pattern_dir, filename)
                    
                    # Handle filename conflicts
                    target_path = self._resolve_filename_conflict(target_path)
                    
                    shutil.move(file_path, target_path)
                    organized_files.append(target_path)
                    files_moved += 1
                
            except Exception as e:
                self.logger.error(f"Error organizing file {file_path}: {e}")
        
        return files_moved, organized_files
    
    async def _organize_duplicates(self, file_paths: List[str], target_directory: str, 
                                 duplicates: Dict[str, List[str]]) -> Tuple[int, List[str]]:
        """Organize duplicate files"""
        files_moved = 0
        organized_files = []
        
        # Create duplicates directory
        duplicates_dir = os.path.join(target_directory, "duplicates")
        os.makedirs(duplicates_dir, exist_ok=True)
        
        for hash_val, duplicate_files in duplicates.items():
            try:
                # Keep the first file, move the rest to duplicates folder
                for i, file_path in enumerate(duplicate_files[1:], 1):
                    filename = os.path.basename(file_path)
                    # Add index to filename to avoid conflicts
                    name, ext = os.path.splitext(filename)
                    duplicate_filename = f"{name}_duplicate_{i}{ext}"
                    target_path = os.path.join(duplicates_dir, duplicate_filename)
                    
                    shutil.move(file_path, target_path)
                    organized_files.append(target_path)
                    files_moved += 1
                
            except Exception as e:
                self.logger.error(f"Error organizing duplicates: {e}")
        
        return files_moved, organized_files
    
    def _resolve_filename_conflict(self, target_path: str) -> str:
        """Resolve filename conflicts by adding a number"""
        if not os.path.exists(target_path):
            return target_path
        
        base_path, ext = os.path.splitext(target_path)
        counter = 1
        
        while True:
            new_path = f"{base_path}_{counter}{ext}"
            if not os.path.exists(new_path):
                return new_path
            counter += 1
    
    async def batch_operations(self, file_paths: List[str], operations: List[str],
                             parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform batch operations on files"""
        results = {
            "success": True,
            "operations_performed": 0,
            "files_processed": 0,
            "errors": []
        }
        
        try:
            for operation in operations:
                if operation == "rename":
                    await self._batch_rename(file_paths, parameters or {})
                elif operation == "copy":
                    await self._batch_copy(file_paths, parameters or {})
                elif operation == "move":
                    await self._batch_move(file_paths, parameters or {})
                elif operation == "delete":
                    await self._batch_delete(file_paths, parameters or {})
                elif operation == "compress":
                    await self._batch_compress(file_paths, parameters or {})
                
                results["operations_performed"] += 1
            
            results["files_processed"] = len(file_paths)
            
        except Exception as e:
            results["success"] = False
            results["errors"].append(str(e))
        
        return results
    
    async def _batch_rename(self, file_paths: List[str], parameters: Dict[str, Any]):
        """Batch rename files"""
        pattern = parameters.get("pattern", "")
        replacement = parameters.get("replacement", "")
        
        for file_path in file_paths:
            try:
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                
                if pattern and replacement:
                    new_filename = re.sub(pattern, replacement, filename)
                else:
                    new_filename = filename
                
                new_path = os.path.join(directory, new_filename)
                os.rename(file_path, new_path)
                
            except Exception as e:
                self.logger.error(f"Error renaming file {file_path}: {e}")
    
    async def _batch_copy(self, file_paths: List[str], parameters: Dict[str, Any]):
        """Batch copy files"""
        destination = parameters.get("destination", "")
        
        if not destination:
            return
        
        os.makedirs(destination, exist_ok=True)
        
        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                target_path = os.path.join(destination, filename)
                target_path = self._resolve_filename_conflict(target_path)
                shutil.copy2(file_path, target_path)
                
            except Exception as e:
                self.logger.error(f"Error copying file {file_path}: {e}")
    
    async def _batch_move(self, file_paths: List[str], parameters: Dict[str, Any]):
        """Batch move files"""
        destination = parameters.get("destination", "")
        
        if not destination:
            return
        
        os.makedirs(destination, exist_ok=True)
        
        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                target_path = os.path.join(destination, filename)
                target_path = self._resolve_filename_conflict(target_path)
                shutil.move(file_path, target_path)
                
            except Exception as e:
                self.logger.error(f"Error moving file {file_path}: {e}")
    
    async def _batch_delete(self, file_paths: List[str], parameters: Dict[str, Any]):
        """Batch delete files"""
        for file_path in file_paths:
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                
            except Exception as e:
                self.logger.error(f"Error deleting {file_path}: {e}")
    
    async def _batch_compress(self, file_paths: List[str], parameters: Dict[str, Any]):
        """Batch compress files"""
        # This would require additional compression library
        # For now, just log the operation
        self.logger.info(f"Batch compress operation requested for {len(file_paths)} files")

class FileOrganizerExecutor:
    """Executor for file organization operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.organizer = FileOrganizer()
        
    async def initialize(self) -> bool:
        """Initialize file organizer executor"""
        try:
            self._is_initialized = True
            self.logger.info("File organizer executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize file organizer executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("file_organization" in parameters or
                "organize_files" in parameters or
                "batch_operations" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file organization capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "File organizer executor not initialized"}
            
            operation = parameters.get("operation", "organize_files")
            
            if operation == "organize_files":
                return await self._execute_organize_files(parameters, context)
            elif operation == "batch_operations":
                return await self._execute_batch_operations(parameters, context)
            elif operation == "find_duplicates":
                return await self._execute_find_duplicates(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing file organization capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_organize_files(self, parameters: Dict[str, Any], 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute organize files operation"""
        try:
            source_directory = parameters.get("source_directory", "")
            target_directory = parameters.get("target_directory", "")
            rule_type_str = parameters.get("rule_type", "by_type")
            pattern = parameters.get("pattern", "*")
            create_backup = parameters.get("create_backup", True)
            
            if not source_directory or not target_directory:
                return {"success": False, "error": "Source and target directories required"}
            
            try:
                rule_type = OrganizationRuleType(rule_type_str)
            except ValueError:
                return {"success": False, "error": f"Invalid rule type: {rule_type_str}"}
            
            result = await self.organizer.organize_files(
                source_directory, target_directory, rule_type, pattern, create_backup
            )
            
            return {
                "success": result.success,
                "files_processed": result.files_processed,
                "files_moved": result.files_moved,
                "files_organized": result.files_organized,
                "duplicates_found": result.duplicates_found,
                "execution_time": result.execution_time,
                "errors": result.errors,
                "organized_files": result.organized_files
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_batch_operations(self, parameters: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute batch operations"""
        try:
            file_paths = parameters.get("file_paths", [])
            operations = parameters.get("operations", [])
            
            if not file_paths or not operations:
                return {"success": False, "error": "File paths and operations required"}
            
            result = await self.organizer.batch_operations(file_paths, operations, parameters)
            
            return {
                "success": result["success"],
                "operations_performed": result["operations_performed"],
                "files_processed": result["files_processed"],
                "errors": result["errors"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_find_duplicates(self, parameters: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute find duplicates operation"""
        try:
            directory = parameters.get("directory", "")
            
            if not directory:
                return {"success": False, "error": "Directory required"}
            
            # Find all files in directory
            file_paths = self.organizer._find_files(directory, "*")
            
            # Find duplicates
            duplicates = self.organizer.duplicate_detector.find_duplicates(file_paths)
            
            return {
                "success": True,
                "duplicates_found": sum(len(files) - 1 for files in duplicates.values()),
                "duplicate_groups": len(duplicates),
                "duplicates": duplicates
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
