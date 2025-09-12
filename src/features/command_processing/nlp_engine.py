"""
Natural Language Processing Engine
Processes natural language commands and converts them to structured format
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

from .command_classifier import CommandClassifier, CommandCategory, ClassificationResult

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents"""
    EXECUTE = "execute"
    QUERY = "query"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    HELP = "help"


@dataclass
class ProcessedCommand:
    """Structured representation of a processed command"""
    original_text: str
    category: CommandCategory
    intent: IntentType
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    error_message: Optional[str] = None


class ContextManager:
    """Manages conversation and system context"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._conversation_history: List[ProcessedCommand] = []
        self._system_context: Dict[str, Any] = {}
        self._max_history = 10
    
    def add_command(self, command: ProcessedCommand) -> None:
        """Add command to conversation history"""
        self._conversation_history.append(command)
        if len(self._conversation_history) > self._max_history:
            self._conversation_history.pop(0)
    
    def get_recent_context(self, count: int = 3) -> List[ProcessedCommand]:
        """Get recent commands for context"""
        return self._conversation_history[-count:] if self._conversation_history else []
    
    def update_system_context(self, context: Dict[str, Any]) -> None:
        """Update system context information"""
        self._system_context.update(context)
    
    def get_system_context(self) -> Dict[str, Any]:
        """Get current system context"""
        return self._system_context.copy()
    
    def clear_context(self) -> None:
        """Clear conversation history and context"""
        self._conversation_history.clear()
        self._system_context.clear()


class EntityExtractor:
    """Extracts entities from natural language text"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_entity_patterns()
    
    def _setup_entity_patterns(self) -> None:
        """Setup patterns for entity extraction"""
        self.patterns = {
            'url': r'https?://[^\s]+',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'number': r'\b\d+\b',
            'time': r'\b\d{1,2}:\d{2}\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'file_path': r'[A-Za-z]:\\[^\\/:*?"<>|]+\.[A-Za-z0-9]+',
            'quoted_text': r'"([^"]*)"',
            'parenthesized_text': r'\(([^)]*)\)'
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text"""
        entities = {}
        
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities


class IntentClassifier:
    """Classifies user intent from natural language"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_intent_patterns()
    
    def _setup_intent_patterns(self) -> None:
        """Setup patterns for intent classification"""
        self.intent_patterns = {
            IntentType.EXECUTE: [
                r'\b(yap|do|execute|run|çalıştır|uygula)\b',
                r'\b(aç|open|launch|başlat)\b',
                r'\b(kapat|close|shutdown|sonlandır)\b',
                r'\b(yaz|type|write|yazdır)\b',
                r'\b(ara|search|find|bul)\b'
            ],
            IntentType.QUERY: [
                r'\b(ne|what|nasıl|how|neden|why)\b',
                r'\b(göster|show|listele|list|display)\b',
                r'\b(bilgi|info|information|hakkında|about)\b',
                r'\b(durum|status|state|durumu)\b'
            ],
            IntentType.CONFIRM: [
                r'\b(evet|yes|tamam|ok|doğru|correct)\b',
                r'\b(onayla|confirm|approve|kabul|accept)\b',
                r'\b(devam|continue|proceed|ilerle)\b'
            ],
            IntentType.CANCEL: [
                r'\b(hayır|no|iptal|cancel|stop|dur)\b',
                r'\b(vazgeç|abort|quit|çık|exit)\b',
                r'\b(durdur|stop|halt|kes)\b'
            ],
            IntentType.HELP: [
                r'\b(yardım|help|assist|destek|support)\b',
                r'\b(ne yapabilir|what can|nasıl|how to)\b',
                r'\b(komutlar|commands|ne var|what is)\b'
            ]
        }
    
    def classify_intent(self, text: str) -> Tuple[IntentType, float]:
        """Classify user intent"""
        text_lower = text.lower()
        scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += len(matches) * 0.3
            scores[intent_type] = min(score, 1.0)
        
        if not scores or max(scores.values()) == 0:
            return IntentType.EXECUTE, 0.5  # Default to execute
        
        best_intent = max(scores.items(), key=lambda x: x[1])
        return best_intent[0], best_intent[1]


class NLPEngine:
    """Natural Language Processing Engine for command processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.classifier = CommandClassifier()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.context_manager = ContextManager()
        self._setup_command_templates()
    
    def _setup_command_templates(self) -> None:
        """Setup command templates for better processing"""
        self.command_templates = {
            CommandCategory.TYPING: {
                'type_text': [
                    r'(?:yaz|type|write)\s+(.+)',
                    r'(?:yazdır|print)\s+(.+)'
                ],
                'press_key': [
                    r'(?:bas|press)\s+(\w+)',
                    r'(?:gir|enter)\s+(\w+)',
                    r'(\w+)\s+(?:tuşu|key)'
                ],
                'key_combination': [
                    r'(?:ctrl|control)\s*\+\s*(\w+)',
                    r'(?:alt)\s*\+\s*(\w+)',
                    r'(?:shift)\s*\+\s*(\w+)'
                ]
            },
            CommandCategory.APPLICATION: {
                'open_app': [
                    r'(?:aç|open|launch|başlat)\s+(\w+)',
                    r'(\w+)\s+(?:aç|open|launch|başlat)'
                ],
                'close_app': [
                    r'(?:kapat|close|sonlandır)\s+(\w+)',
                    r'(\w+)\s+(?:kapat|close|sonlandır)'
                ],
                'switch_app': [
                    r'(?:değiştir|switch|geç)\s+(\w+)',
                    r'(\w+)\s+(?:a|e)\s+(?:geç|switch)'
                ]
            },
            CommandCategory.BROWSER: {
                'open_url': [
                    r'(?:aç|open)\s+(https?://[^\s]+)',
                    r'(?:git|go)\s+(.+)'
                ],
                'search': [
                    r'(?:ara|search)\s+(.+)',
                    r'(?:google|youtube|github)\s+(?:da|de|da)\s+(.+)',
                    r'(.+)?\s+(?:ara|search)'
                ],
                'new_tab': [
                    r'(?:yeni|new)\s+(?:sekme|tab)',
                    r'(?:sekme|tab)\s+(?:aç|open)'
                ]
            }
        }
    
    def process_command(self, text: str, context: Optional[Dict[str, Any]] = None) -> ProcessedCommand:
        """
        Process natural language command into structured format
        
        Args:
            text: Natural language command text
            context: Optional context information
            
        Returns:
            ProcessedCommand object
        """
        try:
            self.logger.info(f"Processing command: '{text}'")
            
            # Clean and normalize text
            clean_text = self._clean_text(text)
            
            # Classify command category
            classification = self.classifier.classify_command(clean_text)
            
            # Classify intent
            intent, intent_confidence = self.intent_classifier.classify_intent(clean_text)
            
            # Extract entities
            entities = self.entity_extractor.extract_entities(clean_text)
            
            # Determine action and parameters
            action, parameters = self._determine_action_and_parameters(
                clean_text, classification.category, entities
            )
            
            # Check if command requires confirmation
            requires_confirmation = self._requires_confirmation(classification.category, action, parameters)
            
            # Create processed command
            processed_command = ProcessedCommand(
                original_text=text,
                category=classification.category,
                intent=intent,
                action=action,
                parameters=parameters,
                confidence=classification.confidence * intent_confidence,
                context=context or {},
                requires_confirmation=requires_confirmation
            )
            
            # Add to context
            self.context_manager.add_command(processed_command)
            
            self.logger.info(f"Processed command: {processed_command.action} "
                           f"({processed_command.category.value}) - "
                           f"confidence: {processed_command.confidence:.2f}")
            
            return processed_command
            
        except Exception as e:
            self.logger.error(f"Error processing command '{text}': {e}")
            return ProcessedCommand(
                original_text=text,
                category=CommandCategory.UNKNOWN,
                intent=IntentType.EXECUTE,
                action="error",
                parameters={},
                confidence=0.0,
                error_message=str(e)
            )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Turkish characters
        text = re.sub(r'[^\w\sçğıöşüÇĞIİÖŞÜ]', ' ', text)
        
        return text
    
    def _determine_action_and_parameters(self, text: str, category: CommandCategory, 
                                       entities: Dict[str, List[str]]) -> Tuple[str, Dict[str, Any]]:
        """Determine action and parameters from text and category"""
        action = "unknown"
        parameters = {}
        
        try:
            if category == CommandCategory.TYPING:
                action, parameters = self._process_typing_command(text, entities)
            elif category == CommandCategory.APPLICATION:
                action, parameters = self._process_application_command(text, entities)
            elif category == CommandCategory.BROWSER:
                action, parameters = self._process_browser_command(text, entities)
            elif category == CommandCategory.SYSTEM:
                action, parameters = self._process_system_command(text, entities)
            elif category == CommandCategory.MEDIA:
                action, parameters = self._process_media_command(text, entities)
            elif category == CommandCategory.FILE:
                action, parameters = self._process_file_command(text, entities)
        
        except Exception as e:
            self.logger.error(f"Error determining action and parameters: {e}")
            action = "error"
            parameters = {"error": str(e)}
        
        return action, parameters
    
    def _process_typing_command(self, text: str, entities: Dict[str, List[str]]) -> Tuple[str, Dict[str, Any]]:
        """Process typing commands"""
        # Check for text to type
        if 'yaz' in text or 'type' in text:
            # Extract text after "yaz" or "type"
            match = re.search(r'(?:yaz|type|write)\s+(.+)', text)
            if match:
                return "type_text", {"text": match.group(1).strip()}
        
        # Check for special keys
        special_keys = {
            'enter': ['enter', 'gir', 'bas'],
            'tab': ['tab', 'sekme'],
            'space': ['space', 'boşluk'],
            'backspace': ['backspace', 'sil', 'delete'],
            'ctrl': ['ctrl', 'control'],
            'alt': ['alt', 'option'],
            'shift': ['shift'],
            'esc': ['esc', 'escape']
        }
        
        for key, keywords in special_keys.items():
            if any(kw in text for kw in keywords):
                return "press_key", {"key": key}
        
        # Check for key combinations
        if 'ctrl' in text and '+' in text:
            match = re.search(r'ctrl\s*\+\s*(\w+)', text)
            if match:
                return "key_combination", {"keys": ["ctrl", match.group(1)]}
        
        return "type_text", {"text": text}
    
    def _process_application_command(self, text: str, entities: Dict[str, List[str]]) -> Tuple[str, Dict[str, Any]]:
        """Process application commands"""
        # Extract action
        if any(word in text for word in ['aç', 'open', 'launch', 'başlat']):
            action = "open_app"
        elif any(word in text for word in ['kapat', 'close', 'sonlandır']):
            action = "close_app"
        elif any(word in text for word in ['değiştir', 'switch', 'geç']):
            action = "switch_app"
        elif any(word in text for word in ['listele', 'list', 'göster']):
            action = "list_apps"
        else:
            action = "open_app"  # Default action
        
        # Extract application name
        app_names = ['cursor', 'vscode', 'chrome', 'firefox', 'notepad', 
                    'calculator', 'explorer', 'word', 'excel', 'powerpoint']
        
        app_name = None
        for app in app_names:
            if app in text:
                app_name = app
                break
        
        parameters = {}
        if app_name:
            parameters["app_name"] = app_name
        
        return action, parameters
    
    def _process_browser_command(self, text: str, entities: Dict[str, List[str]]) -> Tuple[str, Dict[str, Any]]:
        """Process browser commands"""
        # Check for URL
        if 'url' in entities:
            return "open_url", {"url": entities['url'][0]}
        
        # Check for search
        if any(word in text for word in ['ara', 'search']):
            # Extract search query
            match = re.search(r'(?:ara|search)\s+(.+)', text)
            if match:
                query = match.group(1).strip()
            else:
                query = text.replace('ara', '').replace('search', '').strip()
            
            # Determine search engine
            engine = "google"  # Default
            if 'youtube' in text:
                engine = "youtube"
            elif 'github' in text:
                engine = "github"
            elif 'stackoverflow' in text:
                engine = "stackoverflow"
            
            return "search", {"query": query, "engine": engine}
        
        # Check for new tab
        if 'yeni sekme' in text or 'new tab' in text:
            return "new_tab", {}
        
        # Check for close tab
        if 'sekme kapat' in text or 'close tab' in text:
            return "close_tab", {}
        
        # Default to search
        return "search", {"query": text, "engine": "google"}
    
    def _process_system_command(self, text: str, entities: Dict[str, List[str]]) -> Tuple[str, Dict[str, Any]]:
        """Process system commands"""
        if any(word in text for word in ['kapat', 'shutdown']):
            return "shutdown", {}
        elif any(word in text for word in ['yeniden başlat', 'restart', 'reboot']):
            return "restart", {}
        elif any(word in text for word in ['uyku', 'sleep']):
            return "sleep", {}
        elif any(word in text for word in ['kilit', 'lock']):
            return "lock", {}
        elif any(word in text for word in ['ses', 'volume']):
            # Extract volume level
            match = re.search(r'(\d+)', text)
            level = int(match.group(1)) if match else 50
            return "set_volume", {"level": level}
        elif any(word in text for word in ['parlaklık', 'brightness']):
            # Extract brightness level
            match = re.search(r'(\d+)', text)
            level = int(match.group(1)) if match else 50
            return "set_brightness", {"level": level}
        
        return "system_info", {}
    
    def _process_media_command(self, text: str, entities: Dict[str, List[str]]) -> Tuple[str, Dict[str, Any]]:
        """Process media commands"""
        if any(word in text for word in ['çal', 'play', 'oynat']):
            return "play", {}
        elif any(word in text for word in ['dur', 'pause', 'duraklat']):
            return "pause", {}
        elif any(word in text for word in ['sonraki', 'next']):
            return "next_track", {}
        elif any(word in text for word in ['önceki', 'previous']):
            return "previous_track", {}
        elif any(word in text for word in ['ses', 'volume']):
            # Extract volume level
            match = re.search(r'(\d+)', text)
            level = int(match.group(1)) if match else 50
            return "set_volume", {"level": level}
        
        return "play", {}
    
    def _process_file_command(self, text: str, entities: Dict[str, List[str]]) -> Tuple[str, Dict[str, Any]]:
        """Process file commands"""
        if any(word in text for word in ['aç', 'open']):
            return "open_file", {}
        elif any(word in text for word in ['kaydet', 'save']):
            return "save_file", {}
        elif any(word in text for word in ['sil', 'delete']):
            return "delete_file", {}
        elif any(word in text for word in ['kopyala', 'copy']):
            return "copy_file", {}
        elif any(word in text for word in ['taşı', 'move']):
            return "move_file", {}
        
        return "list_files", {}
    
    def _requires_confirmation(self, category: CommandCategory, action: str, parameters: Dict[str, Any]) -> bool:
        """Determine if command requires user confirmation"""
        # Commands that require confirmation
        dangerous_actions = [
            'shutdown', 'restart', 'delete_file', 'close_app'
        ]
        
        if action in dangerous_actions:
            return True
        
        # System commands generally require confirmation
        if category == CommandCategory.SYSTEM and action in ['shutdown', 'restart']:
            return True
        
        return False
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context"""
        recent_commands = self.context_manager.get_recent_context()
        system_context = self.context_manager.get_system_context()
        
        return {
            "recent_commands": [
                {
                    "text": cmd.original_text,
                    "action": cmd.action,
                    "category": cmd.category.value
                }
                for cmd in recent_commands
            ],
            "system_context": system_context
        }
