"""
Document Processing Capabilities for JARVIS Computer Assistant

Provides advanced document creation, editing, and processing capabilities.
"""

import asyncio
import logging
import os
import time
import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Types of documents"""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"

class DocumentFormat(Enum):
    """Document formatting options"""
    PLAIN = "plain"
    FORMATTED = "formatted"
    STRUCTURED = "structured"
    TEMPLATE = "template"

@dataclass
class DocumentTemplate:
    """Document template definition"""
    name: str
    template_type: DocumentType
    content: str
    placeholders: List[str]
    description: Optional[str] = None
    created_at: Optional[float] = None

@dataclass
class DocumentMetadata:
    """Document metadata"""
    title: str
    author: str
    created_at: datetime
    modified_at: datetime
    tags: List[str]
    category: str
    version: str
    description: Optional[str] = None

@dataclass
class DocumentProcessingResult:
    """Result of document processing operation"""
    success: bool
    document_path: str
    document_type: DocumentType
    processing_time: float
    metadata: Optional[DocumentMetadata] = None
    error: Optional[str] = None

class DocumentTemplateManager:
    """Manages document templates"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates: Dict[str, DocumentTemplate] = {}
        self.templates_dir = "templates"
        os.makedirs(self.templates_dir, exist_ok=True)
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from files"""
        try:
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    template_path = os.path.join(self.templates_dir, filename)
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    
                    template = DocumentTemplate(
                        name=template_data['name'],
                        template_type=DocumentType(template_data['template_type']),
                        content=template_data['content'],
                        placeholders=template_data['placeholders'],
                        description=template_data.get('description'),
                        created_at=template_data.get('created_at')
                    )
                    self.templates[template.name] = template
                    
        except Exception as e:
            self.logger.error(f"Error loading templates: {e}")
    
    def save_template(self, template: DocumentTemplate) -> bool:
        """Save a template to file"""
        try:
            template_path = os.path.join(self.templates_dir, f"{template.name}.json")
            template_data = {
                'name': template.name,
                'template_type': template.template_type.value,
                'content': template.content,
                'placeholders': template.placeholders,
                'description': template.description,
                'created_at': template.created_at or time.time()
            }
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            self.templates[template.name] = template
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving template: {e}")
            return False
    
    def get_template(self, name: str) -> Optional[DocumentTemplate]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[DocumentTemplate]:
        """List all templates"""
        return list(self.templates.values())
    
    def create_template_from_document(self, name: str, document_path: str, 
                                    template_type: DocumentType) -> Optional[DocumentTemplate]:
        """Create a template from an existing document"""
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract placeholders (simple pattern matching)
            placeholders = re.findall(r'\{(\w+)\}', content)
            
            template = DocumentTemplate(
                name=name,
                template_type=template_type,
                content=content,
                placeholders=placeholders,
                created_at=time.time()
            )
            
            if self.save_template(template):
                return template
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating template from document: {e}")
            return None

class DocumentFormatter:
    """Handles document formatting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_document(self, content: str, document_type: DocumentType, 
                       format_type: DocumentFormat) -> str:
        """Format document content based on type and format"""
        try:
            if format_type == DocumentFormat.PLAIN:
                return self._format_plain(content, document_type)
            elif format_type == DocumentFormat.FORMATTED:
                return self._format_formatted(content, document_type)
            elif format_type == DocumentFormat.STRUCTURED:
                return self._format_structured(content, document_type)
            elif format_type == DocumentFormat.TEMPLATE:
                return self._format_template(content, document_type)
            else:
                return content
                
        except Exception as e:
            self.logger.error(f"Error formatting document: {e}")
            return content
    
    def _format_plain(self, content: str, document_type: DocumentType) -> str:
        """Format as plain text"""
        return content.strip()
    
    def _format_formatted(self, content: str, document_type: DocumentType) -> str:
        """Format with basic formatting"""
        if document_type == DocumentType.MARKDOWN:
            return self._format_markdown(content)
        elif document_type == DocumentType.HTML:
            return self._format_html(content)
        elif document_type == DocumentType.JSON:
            return self._format_json(content)
        else:
            return content
    
    def _format_structured(self, content: str, document_type: DocumentType) -> str:
        """Format with structured layout"""
        if document_type == DocumentType.MARKDOWN:
            return self._format_structured_markdown(content)
        elif document_type == DocumentType.HTML:
            return self._format_structured_html(content)
        else:
            return content
    
    def _format_template(self, content: str, document_type: DocumentType) -> str:
        """Format as template with placeholders"""
        # Add template placeholders
        template_content = f"# {{{{title}}}}\n\n"
        template_content += f"**Author:** {{{{author}}}}\n"
        template_content += f"**Date:** {{{{date}}}}\n"
        template_content += f"**Version:** {{{{version}}}}\n\n"
        template_content += "---\n\n"
        template_content += content
        template_content += "\n\n---\n\n"
        template_content += "**Tags:** {{{{tags}}}}\n"
        template_content += "**Category:** {{{{category}}}}"
        
        return template_content
    
    def _format_markdown(self, content: str) -> str:
        """Format as Markdown"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append("")
                continue
            
            # Headers
            if line.startswith('# '):
                formatted_lines.append(f"# {line[2:]}")
            elif line.startswith('## '):
                formatted_lines.append(f"## {line[3:]}")
            elif line.startswith('### '):
                formatted_lines.append(f"### {line[4:]}")
            
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                formatted_lines.append(f"- {line[2:]}")
            elif line.startswith('1. '):
                formatted_lines.append(f"1. {line[3:]}")
            
            # Bold and italic
            elif line.startswith('**') and line.endswith('**'):
                formatted_lines.append(f"**{line[2:-2]}**")
            elif line.startswith('*') and line.endswith('*'):
                formatted_lines.append(f"*{line[1:-1]}*")
            
            # Regular text
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_html(self, content: str) -> str:
        """Format as HTML"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append("<br>")
                continue
            
            # Headers
            if line.startswith('# '):
                formatted_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith('## '):
                formatted_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith('### '):
                formatted_lines.append(f"<h3>{line[4:]}</h3>")
            
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                formatted_lines.append(f"<li>{line[2:]}</li>")
            elif line.startswith('1. '):
                formatted_lines.append(f"<li>{line[3:]}</li>")
            
            # Bold and italic
            elif line.startswith('**') and line.endswith('**'):
                formatted_lines.append(f"<strong>{line[2:-2]}</strong>")
            elif line.startswith('*') and line.endswith('*'):
                formatted_lines.append(f"<em>{line[1:-1]}</em>")
            
            # Regular text
            else:
                formatted_lines.append(f"<p>{line}</p>")
        
        return '\n'.join(formatted_lines)
    
    def _format_json(self, content: str) -> str:
        """Format as JSON"""
        try:
            data = json.loads(content)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return content
    
    def _format_structured_markdown(self, content: str) -> str:
        """Format as structured Markdown"""
        # Add table of contents
        toc = self._generate_toc(content)
        structured_content = f"# Table of Contents\n{toc}\n\n---\n\n"
        structured_content += content
        structured_content += "\n\n---\n\n"
        structured_content += "*Generated on {date}*"
        
        return structured_content
    
    def _format_structured_html(self, content: str) -> str:
        """Format as structured HTML"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1, h2, h3 {{ color: #333; }}
        .toc {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
{self._format_html(content)}
</body>
</html>"""
        return html_content
    
    def _generate_toc(self, content: str) -> str:
        """Generate table of contents from content"""
        lines = content.split('\n')
        toc_items = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                title = line[2:]
                anchor = title.lower().replace(' ', '-')
                toc_items.append(f"1. [{title}](#{anchor})")
            elif line.startswith('## '):
                title = line[3:]
                anchor = title.lower().replace(' ', '-')
                toc_items.append(f"   1. [{title}](#{anchor})")
            elif line.startswith('### '):
                title = line[4:]
                anchor = title.lower().replace(' ', '-')
                toc_items.append(f"       1. [{title}](#{anchor})")
        
        return '\n'.join(toc_items)

class DocumentProcessor:
    """Main document processor"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.template_manager = DocumentTemplateManager()
        self.formatter = DocumentFormatter()
        self.documents_dir = "documents"
        os.makedirs(self.documents_dir, exist_ok=True)
    
    async def create_document(self, title: str, content: str, document_type: DocumentType,
                            format_type: DocumentFormat = DocumentFormat.FORMATTED,
                            metadata: Optional[DocumentMetadata] = None) -> DocumentProcessingResult:
        """Create a new document"""
        start_time = time.time()
        
        try:
            # Format content
            formatted_content = self.formatter.format_document(content, document_type, format_type)
            
            # Generate filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')
            
            # Get file extension
            extensions = {
                DocumentType.TEXT: '.txt',
                DocumentType.MARKDOWN: '.md',
                DocumentType.HTML: '.html',
                DocumentType.JSON: '.json',
                DocumentType.XML: '.xml',
                DocumentType.CSV: '.csv',
                DocumentType.YAML: '.yaml'
            }
            
            extension = extensions.get(document_type, '.txt')
            filename = f"{safe_title}{extension}"
            document_path = os.path.join(self.documents_dir, filename)
            
            # Create document content with metadata
            if metadata:
                document_content = self._add_metadata(formatted_content, metadata, document_type)
            else:
                document_content = formatted_content
            
            # Write document
            with open(document_path, 'w', encoding='utf-8') as f:
                f.write(document_content)
            
            processing_time = time.time() - start_time
            
            return DocumentProcessingResult(
                success=True,
                document_path=document_path,
                document_type=document_type,
                processing_time=processing_time,
                metadata=metadata
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return DocumentProcessingResult(
                success=False,
                document_path="",
                document_type=document_type,
                processing_time=processing_time,
                error=str(e)
            )
    
    async def create_document_from_template(self, template_name: str, title: str,
                                          placeholders: Dict[str, str],
                                          metadata: Optional[DocumentMetadata] = None) -> DocumentProcessingResult:
        """Create document from template"""
        start_time = time.time()
        
        try:
            template = self.template_manager.get_template(template_name)
            if not template:
                return DocumentProcessingResult(
                    success=False,
                    document_path="",
                    document_type=DocumentType.TEXT,
                    processing_time=time.time() - start_time,
                    error=f"Template not found: {template_name}"
                )
            
            # Replace placeholders
            content = template.content
            for placeholder, value in placeholders.items():
                content = content.replace(f"{{{placeholder}}}", value)
            
            # Create document
            return await self.create_document(title, content, template.template_type, 
                                            DocumentFormat.FORMATTED, metadata)
            
        except Exception as e:
            processing_time = time.time() - start_time
            return DocumentProcessingResult(
                success=False,
                document_path="",
                document_type=DocumentType.TEXT,
                processing_time=processing_time,
                error=str(e)
            )
    
    async def process_document(self, document_path: str, operation: str,
                             parameters: Dict[str, Any] = None) -> DocumentProcessingResult:
        """Process an existing document"""
        start_time = time.time()
        
        try:
            if not os.path.exists(document_path):
                return DocumentProcessingResult(
                    success=False,
                    document_path=document_path,
                    document_type=DocumentType.TEXT,
                    processing_time=time.time() - start_time,
                    error="Document not found"
                )
            
            # Read document
            with open(document_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine document type
            document_type = self._detect_document_type(document_path)
            
            # Process based on operation
            if operation == "format":
                format_type = DocumentFormat(parameters.get('format_type', 'formatted'))
                formatted_content = self.formatter.format_document(content, document_type, format_type)
                
                with open(document_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
            
            elif operation == "convert":
                target_type = DocumentType(parameters.get('target_type', 'text'))
                converted_content = self._convert_document(content, document_type, target_type)
                
                # Update file extension if needed
                new_path = self._update_file_extension(document_path, target_type)
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(converted_content)
                
                document_path = new_path
                document_type = target_type
            
            elif operation == "extract_metadata":
                metadata = self._extract_metadata(content, document_type)
                return DocumentProcessingResult(
                    success=True,
                    document_path=document_path,
                    document_type=document_type,
                    processing_time=time.time() - start_time,
                    metadata=metadata
                )
            
            processing_time = time.time() - start_time
            
            return DocumentProcessingResult(
                success=True,
                document_path=document_path,
                document_type=document_type,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return DocumentProcessingResult(
                success=False,
                document_path=document_path,
                document_type=DocumentType.TEXT,
                processing_time=processing_time,
                error=str(e)
            )
    
    def _add_metadata(self, content: str, metadata: DocumentMetadata, document_type: DocumentType) -> str:
        """Add metadata to document content"""
        if document_type == DocumentType.MARKDOWN:
            metadata_header = f"""---
title: {metadata.title}
author: {metadata.author}
created: {metadata.created_at.isoformat()}
modified: {metadata.modified_at.isoformat()}
version: {metadata.version}
tags: {', '.join(metadata.tags)}
category: {metadata.category}
description: {metadata.description or ''}
---

"""
        elif document_type == DocumentType.HTML:
            metadata_header = f"""<!--
title: {metadata.title}
author: {metadata.author}
created: {metadata.created_at.isoformat()}
modified: {metadata.modified_at.isoformat()}
version: {metadata.version}
tags: {', '.join(metadata.tags)}
category: {metadata.category}
description: {metadata.description or ''}
-->
"""
        else:
            metadata_header = f"""Title: {metadata.title}
Author: {metadata.author}
Created: {metadata.created_at.isoformat()}
Modified: {metadata.modified_at.isoformat()}
Version: {metadata.version}
Tags: {', '.join(metadata.tags)}
Category: {metadata.category}
Description: {metadata.description or ''}

"""
        
        return metadata_header + content
    
    def _detect_document_type(self, file_path: str) -> DocumentType:
        """Detect document type from file extension"""
        extension = os.path.splitext(file_path)[1].lower()
        
        type_mapping = {
            '.txt': DocumentType.TEXT,
            '.md': DocumentType.MARKDOWN,
            '.html': DocumentType.HTML,
            '.htm': DocumentType.HTML,
            '.json': DocumentType.JSON,
            '.xml': DocumentType.XML,
            '.csv': DocumentType.CSV,
            '.yaml': DocumentType.YAML,
            '.yml': DocumentType.YAML,
            '.pdf': DocumentType.PDF,
            '.doc': DocumentType.WORD,
            '.docx': DocumentType.WORD,
            '.xls': DocumentType.EXCEL,
            '.xlsx': DocumentType.EXCEL,
            '.ppt': DocumentType.POWERPOINT,
            '.pptx': DocumentType.POWERPOINT
        }
        
        return type_mapping.get(extension, DocumentType.TEXT)
    
    def _convert_document(self, content: str, source_type: DocumentType, target_type: DocumentType) -> str:
        """Convert document between types"""
        if source_type == target_type:
            return content
        
        # Simple conversion logic
        if source_type == DocumentType.MARKDOWN and target_type == DocumentType.HTML:
            return self.formatter._format_html(content)
        elif source_type == DocumentType.HTML and target_type == DocumentType.MARKDOWN:
            # Basic HTML to Markdown conversion
            content = re.sub(r'<h1>(.*?)</h1>', r'# \1', content)
            content = re.sub(r'<h2>(.*?)</h2>', r'## \1', content)
            content = re.sub(r'<h3>(.*?)</h3>', r'### \1', content)
            content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
            content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
            content = re.sub(r'<li>(.*?)</li>', r'- \1', content)
            content = re.sub(r'<p>(.*?)</p>', r'\1\n', content)
            content = re.sub(r'<br>', r'\n', content)
            return content
        else:
            return content
    
    def _update_file_extension(self, file_path: str, document_type: DocumentType) -> str:
        """Update file extension based on document type"""
        base_path = os.path.splitext(file_path)[0]
        
        extensions = {
            DocumentType.TEXT: '.txt',
            DocumentType.MARKDOWN: '.md',
            DocumentType.HTML: '.html',
            DocumentType.JSON: '.json',
            DocumentType.XML: '.xml',
            DocumentType.CSV: '.csv',
            DocumentType.YAML: '.yaml'
        }
        
        extension = extensions.get(document_type, '.txt')
        return f"{base_path}{extension}"
    
    def _extract_metadata(self, content: str, document_type: DocumentType) -> DocumentMetadata:
        """Extract metadata from document content"""
        # Simple metadata extraction
        title = "Untitled Document"
        author = "Unknown"
        created_at = datetime.now()
        modified_at = datetime.now()
        tags = []
        category = "General"
        version = "1.0"
        description = None
        
        if document_type == DocumentType.MARKDOWN:
            # Extract from YAML front matter
            if content.startswith('---'):
                lines = content.split('\n')
                for line in lines[1:]:
                    if line.strip() == '---':
                        break
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'title':
                            title = value
                        elif key == 'author':
                            author = value
                        elif key == 'tags':
                            tags = [tag.strip() for tag in value.split(',')]
                        elif key == 'category':
                            category = value
                        elif key == 'version':
                            version = value
                        elif key == 'description':
                            description = value
        
        return DocumentMetadata(
            title=title,
            author=author,
            created_at=created_at,
            modified_at=modified_at,
            tags=tags,
            category=category,
            version=version,
            description=description
        )

class DocumentProcessorExecutor:
    """Executor for document processing operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.processor = DocumentProcessor()
        
    async def initialize(self) -> bool:
        """Initialize document processor executor"""
        try:
            self._is_initialized = True
            self.logger.info("Document processor executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize document processor executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("document_processing" in parameters or
                "create_document" in parameters or
                "process_document" in parameters or
                "template_processing" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute document processing capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Document processor executor not initialized"}
            
            operation = parameters.get("operation", "create_document")
            
            if operation == "create_document":
                return await self._execute_create_document(parameters, context)
            elif operation == "process_document":
                return await self._execute_process_document(parameters, context)
            elif operation == "create_from_template":
                return await self._execute_create_from_template(parameters, context)
            elif operation == "list_templates":
                return await self._execute_list_templates(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing document processing capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_create_document(self, parameters: Dict[str, Any], 
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create document operation"""
        try:
            title = parameters.get("title", "Untitled Document")
            content = parameters.get("content", "")
            document_type_str = parameters.get("document_type", "text")
            format_type_str = parameters.get("format_type", "formatted")
            
            try:
                document_type = DocumentType(document_type_str)
                format_type = DocumentFormat(format_type_str)
            except ValueError as e:
                return {"success": False, "error": f"Invalid type: {e}"}
            
            # Create metadata if provided
            metadata = None
            if "metadata" in parameters:
                meta_data = parameters["metadata"]
                metadata = DocumentMetadata(
                    title=meta_data.get("title", title),
                    author=meta_data.get("author", "Unknown"),
                    created_at=datetime.now(),
                    modified_at=datetime.now(),
                    tags=meta_data.get("tags", []),
                    category=meta_data.get("category", "General"),
                    version=meta_data.get("version", "1.0"),
                    description=meta_data.get("description")
                )
            
            result = await self.processor.create_document(
                title, content, document_type, format_type, metadata
            )
            
            return {
                "success": result.success,
                "document_path": result.document_path,
                "document_type": result.document_type.value,
                "processing_time": result.processing_time,
                "metadata": result.metadata.__dict__ if result.metadata else None,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_process_document(self, parameters: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute process document operation"""
        try:
            document_path = parameters.get("document_path", "")
            operation = parameters.get("process_operation", "format")
            
            if not document_path:
                return {"success": False, "error": "Document path required"}
            
            result = await self.processor.process_document(document_path, operation, parameters)
            
            return {
                "success": result.success,
                "document_path": result.document_path,
                "document_type": result.document_type.value,
                "processing_time": result.processing_time,
                "metadata": result.metadata.__dict__ if result.metadata else None,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_create_from_template(self, parameters: Dict[str, Any], 
                                          context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create document from template operation"""
        try:
            template_name = parameters.get("template_name", "")
            title = parameters.get("title", "Untitled Document")
            placeholders = parameters.get("placeholders", {})
            
            if not template_name:
                return {"success": False, "error": "Template name required"}
            
            result = await self.processor.create_document_from_template(
                template_name, title, placeholders
            )
            
            return {
                "success": result.success,
                "document_path": result.document_path,
                "document_type": result.document_type.value,
                "processing_time": result.processing_time,
                "metadata": result.metadata.__dict__ if result.metadata else None,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_list_templates(self, parameters: Dict[str, Any], 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute list templates operation"""
        try:
            templates = self.processor.template_manager.list_templates()
            
            template_list = []
            for template in templates:
                template_list.append({
                    "name": template.name,
                    "template_type": template.template_type.value,
                    "placeholders": template.placeholders,
                    "description": template.description,
                    "created_at": template.created_at
                })
            
            return {
                "success": True,
                "templates": template_list,
                "total_templates": len(template_list)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

