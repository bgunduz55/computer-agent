"""
Text Manipulation Capabilities for JARVIS Computer Assistant

Provides advanced text processing, formatting, and manipulation capabilities.
"""

import asyncio
import logging
import time
import re
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TextFormatType(Enum):
    """Types of text formatting"""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    PLAIN_TEXT = "plain_text"

class TextSearchType(Enum):
    """Types of text search operations"""
    EXACT_MATCH = "exact_match"
    REGEX = "regex"
    FUZZY = "fuzzy"
    CASE_INSENSITIVE = "case_insensitive"
    WORD_BOUNDARY = "word_boundary"

@dataclass
class TextFormattingResult:
    """Result of text formatting operation"""
    success: bool
    original_text: str
    formatted_text: str
    format_type: TextFormatType
    execution_time: float
    error: Optional[str] = None

@dataclass
class TextSearchResult:
    """Result of text search operation"""
    success: bool
    search_term: str
    matches: List[Dict[str, Any]]
    total_matches: int
    execution_time: float
    error: Optional[str] = None

@dataclass
class TextExtractionResult:
    """Result of text extraction operation"""
    success: bool
    original_text: str
    extracted_data: Dict[str, Any]
    extraction_type: str
    execution_time: float
    error: Optional[str] = None

class TextFormattingEngine:
    """Engine for text formatting operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def format_text(self, text: str, format_type: TextFormatType, 
                         parameters: Dict[str, Any] = None) -> TextFormattingResult:
        """Format text according to specified format type"""
        start_time = time.time()
        
        try:
            if format_type == TextFormatType.MARKDOWN:
                formatted_text = await self._format_markdown(text, parameters)
            elif format_type == TextFormatType.HTML:
                formatted_text = await self._format_html(text, parameters)
            elif format_type == TextFormatType.JSON:
                formatted_text = await self._format_json(text, parameters)
            elif format_type == TextFormatType.XML:
                formatted_text = await self._format_xml(text, parameters)
            elif format_type == TextFormatType.CSV:
                formatted_text = await self._format_csv(text, parameters)
            elif format_type == TextFormatType.YAML:
                formatted_text = await self._format_yaml(text, parameters)
            else:
                formatted_text = text
            
            execution_time = time.time() - start_time
            return TextFormattingResult(
                success=True,
                original_text=text,
                formatted_text=formatted_text,
                format_type=format_type,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TextFormattingResult(
                success=False,
                original_text=text,
                formatted_text="",
                format_type=format_type,
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _format_markdown(self, text: str, parameters: Dict[str, Any] = None) -> str:
        """Format text as Markdown"""
        lines = text.split('\n')
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
            
            # Code blocks
            elif line.startswith('```'):
                formatted_lines.append(line)
            elif line.startswith('`') and line.endswith('`'):
                formatted_lines.append(line)
            
            # Regular text
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    async def _format_html(self, text: str, parameters: Dict[str, Any] = None) -> str:
        """Format text as HTML"""
        lines = text.split('\n')
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
            
            # Links
            elif line.startswith('http'):
                formatted_lines.append(f'<a href="{line}">{line}</a>')
            
            # Regular text
            else:
                formatted_lines.append(f"<p>{line}</p>")
        
        return '\n'.join(formatted_lines)
    
    async def _format_json(self, text: str, parameters: Dict[str, Any] = None) -> str:
        """Format text as JSON"""
        try:
            # Try to parse as JSON first
            data = json.loads(text)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # If not valid JSON, create a simple structure
            return json.dumps({"text": text}, indent=2, ensure_ascii=False)
    
    async def _format_xml(self, text: str, parameters: Dict[str, Any] = None) -> str:
        """Format text as XML"""
        # Simple XML formatting
        return f"<text>{text}</text>"
    
    async def _format_csv(self, text: str, parameters: Dict[str, Any] = None) -> str:
        """Format text as CSV"""
        lines = text.split('\n')
        csv_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Split by common delimiters and quote if necessary
                parts = re.split(r'[,\t|]', line)
                quoted_parts = [f'"{part.strip()}"' if ',' in part or '"' in part else part.strip() for part in parts]
                csv_lines.append(','.join(quoted_parts))
        
        return '\n'.join(csv_lines)
    
    async def _format_yaml(self, text: str, parameters: Dict[str, Any] = None) -> str:
        """Format text as YAML"""
        # Simple YAML formatting
        return f"text: {text}"

class TextSearchEngine:
    """Engine for text search operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def search_text(self, text: str, search_term: str, search_type: TextSearchType,
                         parameters: Dict[str, Any] = None) -> TextSearchResult:
        """Search for text based on search type"""
        start_time = time.time()
        
        try:
            matches = []
            
            if search_type == TextSearchType.EXACT_MATCH:
                matches = await self._exact_search(text, search_term)
            elif search_type == TextSearchType.REGEX:
                matches = await self._regex_search(text, search_term)
            elif search_type == TextSearchType.FUZZY:
                matches = await self._fuzzy_search(text, search_term)
            elif search_type == TextSearchType.CASE_INSENSITIVE:
                matches = await self._case_insensitive_search(text, search_term)
            elif search_type == TextSearchType.WORD_BOUNDARY:
                matches = await self._word_boundary_search(text, search_term)
            
            execution_time = time.time() - start_time
            return TextSearchResult(
                success=True,
                search_term=search_term,
                matches=matches,
                total_matches=len(matches),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TextSearchResult(
                success=False,
                search_term=search_term,
                matches=[],
                total_matches=0,
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _exact_search(self, text: str, search_term: str) -> List[Dict[str, Any]]:
        """Perform exact text search"""
        matches = []
        start = 0
        
        while True:
            pos = text.find(search_term, start)
            if pos == -1:
                break
            
            matches.append({
                "position": pos,
                "text": search_term,
                "context": text[max(0, pos-20):pos+len(search_term)+20]
            })
            start = pos + 1
        
        return matches
    
    async def _regex_search(self, text: str, search_term: str) -> List[Dict[str, Any]]:
        """Perform regex search"""
        matches = []
        
        try:
            pattern = re.compile(search_term)
            for match in pattern.finditer(text):
                matches.append({
                    "position": match.start(),
                    "text": match.group(),
                    "context": text[max(0, match.start()-20):match.end()+20]
                })
        except re.error as e:
            self.logger.error(f"Regex error: {e}")
        
        return matches
    
    async def _fuzzy_search(self, text: str, search_term: str) -> List[Dict[str, Any]]:
        """Perform fuzzy search (simplified implementation)"""
        matches = []
        words = text.split()
        search_words = search_term.split()
        
        for i, word in enumerate(words):
            for search_word in search_words:
                if self._fuzzy_match(word, search_word):
                    matches.append({
                        "position": i,
                        "text": word,
                        "context": ' '.join(words[max(0, i-2):i+3])
                    })
        
        return matches
    
    async def _case_insensitive_search(self, text: str, search_term: str) -> List[Dict[str, Any]]:
        """Perform case-insensitive search"""
        matches = []
        text_lower = text.lower()
        search_term_lower = search_term.lower()
        start = 0
        
        while True:
            pos = text_lower.find(search_term_lower, start)
            if pos == -1:
                break
            
            matches.append({
                "position": pos,
                "text": text[pos:pos+len(search_term)],
                "context": text[max(0, pos-20):pos+len(search_term)+20]
            })
            start = pos + 1
        
        return matches
    
    async def _word_boundary_search(self, text: str, search_term: str) -> List[Dict[str, Any]]:
        """Perform word boundary search"""
        matches = []
        pattern = r'\b' + re.escape(search_term) + r'\b'
        
        try:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append({
                    "position": match.start(),
                    "text": match.group(),
                    "context": text[max(0, match.start()-20):match.end()+20]
                })
        except re.error as e:
            self.logger.error(f"Word boundary search error: {e}")
        
        return matches
    
    def _fuzzy_match(self, word1: str, word2: str, threshold: float = 0.6) -> bool:
        """Simple fuzzy matching algorithm"""
        if not word1 or not word2:
            return False
        
        # Simple Levenshtein distance-based fuzzy matching
        distance = self._levenshtein_distance(word1.lower(), word2.lower())
        max_len = max(len(word1), len(word2))
        
        if max_len == 0:
            return True
        
        similarity = 1 - (distance / max_len)
        return similarity >= threshold
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

class TextExtractionEngine:
    """Engine for text extraction operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def extract_data(self, text: str, extraction_type: str, 
                          parameters: Dict[str, Any] = None) -> TextExtractionResult:
        """Extract data from text based on extraction type"""
        start_time = time.time()
        
        try:
            if extraction_type == "emails":
                extracted_data = await self._extract_emails(text)
            elif extraction_type == "phones":
                extracted_data = await self._extract_phones(text)
            elif extraction_type == "urls":
                extracted_data = await self._extract_urls(text)
            elif extraction_type == "dates":
                extracted_data = await self._extract_dates(text)
            elif extraction_type == "numbers":
                extracted_data = await self._extract_numbers(text)
            elif extraction_type == "names":
                extracted_data = await self._extract_names(text)
            elif extraction_type == "addresses":
                extracted_data = await self._extract_addresses(text)
            else:
                extracted_data = {"error": f"Unknown extraction type: {extraction_type}"}
            
            execution_time = time.time() - start_time
            return TextExtractionResult(
                success=True,
                original_text=text,
                extracted_data=extracted_data,
                extraction_type=extraction_type,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TextExtractionResult(
                success=False,
                original_text=text,
                extracted_data={},
                extraction_type=extraction_type,
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _extract_emails(self, text: str) -> Dict[str, Any]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return {"emails": emails, "count": len(emails)}
    
    async def _extract_phones(self, text: str) -> Dict[str, Any]:
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US format
            r'\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}',  # International
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return {"phones": phones, "count": len(phones)}
    
    async def _extract_urls(self, text: str) -> Dict[str, Any]:
        """Extract URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        return {"urls": urls, "count": len(urls)}
    
    async def _extract_dates(self, text: str) -> Dict[str, Any]:
        """Extract dates from text"""
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return {"dates": dates, "count": len(dates)}
    
    async def _extract_numbers(self, text: str) -> Dict[str, Any]:
        """Extract numbers from text"""
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, text)
        return {"numbers": numbers, "count": len(numbers)}
    
    async def _extract_names(self, text: str) -> Dict[str, Any]:
        """Extract potential names from text (simplified)"""
        # Simple name extraction - looks for capitalized words
        words = text.split()
        potential_names = []
        
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 1 and word.isalpha():
                # Check if next word is also capitalized (likely a name)
                if i + 1 < len(words) and words[i + 1][0].isupper() and words[i + 1].isalpha():
                    potential_names.append(f"{word} {words[i + 1]}")
        
        return {"names": potential_names, "count": len(potential_names)}
    
    async def _extract_addresses(self, text: str) -> Dict[str, Any]:
        """Extract potential addresses from text (simplified)"""
        # Simple address extraction - looks for street numbers and common address words
        address_pattern = r'\b\d+\s+(?:[A-Za-z]+\s+){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b'
        addresses = re.findall(address_pattern, text, re.IGNORECASE)
        return {"addresses": addresses, "count": len(addresses)}

class TextManipulationExecutor:
    """Executes text manipulation operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self.formatting_engine = TextFormattingEngine()
        self.search_engine = TextSearchEngine()
        self.extraction_engine = TextExtractionEngine()
        
    async def initialize(self) -> bool:
        """Initialize text manipulation executor"""
        try:
            self._is_initialized = True
            self.logger.info("Text manipulation executor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize text manipulation executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if this executor can handle the given capability"""
        return ("text_manipulation" in parameters or
                "text_formatting" in parameters or
                "text_search" in parameters or
                "text_extraction" in parameters)
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text manipulation capability"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "Text manipulation executor not initialized"}
            
            operation = parameters.get("operation", "format")
            
            if operation == "format":
                return await self._execute_formatting(parameters, context)
            elif operation == "search":
                return await self._execute_search(parameters, context)
            elif operation == "extract":
                return await self._execute_extraction(parameters, context)
            else:
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            self.logger.error(f"Error executing text manipulation capability: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_formatting(self, parameters: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text formatting operation"""
        try:
            text = parameters.get("text", "")
            format_type_str = parameters.get("format_type", "plain_text")
            
            if not text:
                return {"success": False, "error": "No text provided"}
            
            try:
                format_type = TextFormatType(format_type_str)
            except ValueError:
                return {"success": False, "error": f"Invalid format type: {format_type_str}"}
            
            result = await self.formatting_engine.format_text(text, format_type, parameters)
            
            return {
                "success": result.success,
                "original_text": result.original_text,
                "formatted_text": result.formatted_text,
                "format_type": result.format_type.value,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_search(self, parameters: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text search operation"""
        try:
            text = parameters.get("text", "")
            search_term = parameters.get("search_term", "")
            search_type_str = parameters.get("search_type", "exact_match")
            
            if not text or not search_term:
                return {"success": False, "error": "Text and search term required"}
            
            try:
                search_type = TextSearchType(search_type_str)
            except ValueError:
                return {"success": False, "error": f"Invalid search type: {search_type_str}"}
            
            result = await self.search_engine.search_text(text, search_term, search_type, parameters)
            
            return {
                "success": result.success,
                "search_term": result.search_term,
                "matches": result.matches,
                "total_matches": result.total_matches,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_extraction(self, parameters: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute text extraction operation"""
        try:
            text = parameters.get("text", "")
            extraction_type = parameters.get("extraction_type", "emails")
            
            if not text:
                return {"success": False, "error": "No text provided"}
            
            result = await self.extraction_engine.extract_data(text, extraction_type, parameters)
            
            return {
                "success": result.success,
                "original_text": result.original_text,
                "extracted_data": result.extracted_data,
                "extraction_type": result.extraction_type,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

