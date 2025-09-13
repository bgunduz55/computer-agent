"""
Command Classification System
Classifies user commands into different categories for proper execution
"""

import re
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class CommandCategory(Enum):
    """Command categories for classification"""
    TYPING = "typing"
    APPLICATION = "application"
    BROWSER = "browser"
    SYSTEM = "system"
    MEDIA = "media"
    FILE = "file"
    UNKNOWN = "unknown"


@dataclass
class ClassificationResult:
    """Result of command classification"""
    category: CommandCategory
    confidence: float
    extracted_parameters: Dict[str, str]
    original_text: str


class CommandClassifier:
    """Classifies user commands into appropriate categories"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_patterns()
        self._setup_keywords()
    
    def _setup_patterns(self) -> None:
        """Setup regex patterns for command detection"""
        self.patterns = {
            CommandCategory.TYPING: [
                r'\b(yaz|type|write|yazdır)\b',
                r'\b(enter|gir|bas)\b',
                r'\b(backspace|sil|delete)\b',
                r'\b(tab|sekme)\b',
                r'\b(space|boşluk)\b',
                r'\b(ctrl|control)\b',
                r'\b(alt|option)\b',
                r'\b(shift)\b',
                r'\b(esc|escape)\b'
            ],
            CommandCategory.APPLICATION: [
                r'\b(aç|open|launch|başlat)\b',
                r'\b(kapat|close|kapat|sonlandır)\b',
                r'\b(değiştir|switch|geç)\b',
                r'\b(listele|list|göster)\b',
                r'\b(cursor|vscode|chrome|firefox|notepad|calculator)\b'
            ],
            CommandCategory.BROWSER: [
                r'\b(tarayıcı|browser|chrome|firefox|edge)\b',
                r'\b(sekme|tab)\b',
                r'\b(url|link|adres)\b',
                r'\b(ara|search|google|youtube|github)\b',
                r'\b(yeni sekme|new tab)\b',
                r'\b(sekme kapat|close tab)\b'
            ],
            CommandCategory.SYSTEM: [
                r'\b(sistem|system)\b',
                r'\b(kapat|shutdown|kapat)\b',
                r'\b(yeniden başlat|restart|reboot)\b',
                r'\b(uyku|sleep|sleep mode)\b',
                r'\b(kilit|lock|kilitle)\b',
                r'\b(ses|volume|vol)\b',
                r'\b(parlaklık|brightness)\b'
            ],
            CommandCategory.MEDIA: [
                r'\b(çal|play|oynat)\b',
                r'\b(dur|pause|duraklat)\b',
                r'\b(sonraki|next|ileri)\b',
                r'\b(önceki|previous|geri)\b',
                r'\b(müzik|music|şarkı|song)\b',
                r'\b(video|film|movie)\b',
                r'\b(spotify|youtube|netflix)\b'
            ],
            CommandCategory.FILE: [
                r'\b(dosya|file|folder|klasör)\b',
                r'\b(aç|open|göster|show)\b',
                r'\b(kaydet|save|store)\b',
                r'\b(sil|delete|remove)\b',
                r'\b(kopyala|copy|kopya)\b',
                r'\b(taşı|move|move)\b'
            ]
        }
    
    def _setup_keywords(self) -> None:
        """Setup keyword mappings for better classification"""
        self.keywords = {
            CommandCategory.TYPING: [
                'yaz', 'type', 'write', 'yazdır', 'enter', 'gir', 'bas',
                'backspace', 'sil', 'delete', 'tab', 'sekme', 'space', 'boşluk',
                'ctrl', 'control', 'alt', 'option', 'shift', 'esc', 'escape'
            ],
            CommandCategory.APPLICATION: [
                'aç', 'open', 'launch', 'başlat', 'kapat', 'close', 'sonlandır',
                'değiştir', 'switch', 'geç', 'listele', 'list', 'göster',
                'cursor', 'vscode', 'chrome', 'firefox', 'notepad', 'calculator',
                'explorer', 'explorer', 'word', 'excel', 'powerpoint'
            ],
            CommandCategory.BROWSER: [
                'tarayıcı', 'browser', 'chrome', 'firefox', 'edge', 'safari',
                'sekme', 'tab', 'url', 'link', 'adres', 'ara', 'search',
                'google', 'youtube', 'github', 'yeni sekme', 'new tab',
                'sekme kapat', 'close tab', 'web', 'internet'
            ],
            CommandCategory.SYSTEM: [
                'sistem', 'system', 'kapat', 'shutdown', 'kapat',
                'yeniden başlat', 'restart', 'reboot', 'uyku', 'sleep',
                'kilit', 'lock', 'kilitle', 'ses', 'volume', 'vol',
                'parlaklık', 'brightness', 'ekran', 'screen'
            ],
            CommandCategory.MEDIA: [
                'çal', 'play', 'oynat', 'dur', 'pause', 'duraklat',
                'sonraki', 'next', 'ileri', 'önceki', 'previous', 'geri',
                'müzik', 'music', 'şarkı', 'song', 'video', 'film', 'movie',
                'spotify', 'youtube', 'netflix', 'medya', 'media'
            ],
            CommandCategory.FILE: [
                'dosya', 'file', 'folder', 'klasör', 'aç', 'open', 'göster', 'show',
                'kaydet', 'save', 'store', 'sil', 'delete', 'remove',
                'kopyala', 'copy', 'kopya', 'taşı', 'move', 'hareket'
            ]
        }
    
    def classify_command(self, text: str) -> ClassificationResult:
        """
        Classify a command into appropriate category
        
        Args:
            text: User command text
            
        Returns:
            ClassificationResult with category, confidence, and parameters
        """
        try:
            # Clean and normalize text
            clean_text = self._clean_text(text)
            
            # Get classification scores
            scores = self._calculate_category_scores(clean_text)
            
            # Find best match
            best_category, best_score = max(scores.items(), key=lambda x: x[1])
            
            # Extract parameters
            parameters = self._extract_parameters(clean_text, best_category)
            
            # Create result
            result = ClassificationResult(
                category=best_category,
                confidence=best_score,
                extracted_parameters=parameters,
                original_text=text
            )
            
            self.logger.info(f"Classified command: '{text}' -> {best_category.value} (confidence: {best_score:.2f})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error classifying command '{text}': {e}")
            return ClassificationResult(
                category=CommandCategory.UNKNOWN,
                confidence=0.0,
                extracted_parameters={},
                original_text=text
            )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for processing"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep Turkish characters
        text = re.sub(r'[^\w\sçğıöşüÇĞIİÖŞÜ]', '', text)
        
        return text
    
    def _calculate_category_scores(self, text: str) -> Dict[CommandCategory, float]:
        """Calculate confidence scores for each category"""
        scores = {}
        
        for category in CommandCategory:
            if category == CommandCategory.UNKNOWN:
                continue
                
            # Pattern matching score
            pattern_score = self._calculate_pattern_score(text, category)
            
            # Keyword matching score
            keyword_score = self._calculate_keyword_score(text, category)
            
            # Combined score (weighted average)
            combined_score = (pattern_score * 0.6) + (keyword_score * 0.4)
            scores[category] = combined_score
        
        return scores
    
    def _calculate_pattern_score(self, text: str, category: CommandCategory) -> float:
        """Calculate score based on regex pattern matching"""
        if category not in self.patterns:
            return 0.0
        
        max_score = 0.0
        for pattern in self.patterns[category]:
            matches = re.findall(pattern, text)
            if matches:
                # Score based on number of matches and pattern complexity
                pattern_score = len(matches) * 0.3
                if len(pattern) > 10:  # More specific patterns get higher weight
                    pattern_score *= 1.2
                max_score = max(max_score, pattern_score)
        
        return min(max_score, 1.0)
    
    def _calculate_keyword_score(self, text: str, category: CommandCategory) -> float:
        """Calculate score based on keyword matching"""
        if category not in self.keywords:
            return 0.0
        
        words = text.split()
        keyword_matches = 0
        total_keywords = len(self.keywords[category])
        
        for word in words:
            for keyword in self.keywords[category]:
                # Exact match
                if word == keyword:
                    keyword_matches += 1
                    break
                # Fuzzy match for similar words
                elif self._fuzzy_match(word, keyword, threshold=0.8):
                    keyword_matches += 0.7
                    break
        
        if total_keywords == 0:
            return 0.0
        
        return min(keyword_matches / total_keywords, 1.0)
    
    def _fuzzy_match(self, word1: str, word2: str, threshold: float = 0.8) -> bool:
        """Check if two words are similar using fuzzy matching"""
        similarity = SequenceMatcher(None, word1, word2).ratio()
        return similarity >= threshold
    
    def _extract_parameters(self, text: str, category: CommandCategory) -> Dict[str, str]:
        """Extract parameters from command text"""
        parameters = {}
        
        try:
            if category == CommandCategory.TYPING:
                parameters = self._extract_typing_parameters(text)
            elif category == CommandCategory.APPLICATION:
                parameters = self._extract_application_parameters(text)
            elif category == CommandCategory.BROWSER:
                parameters = self._extract_browser_parameters(text)
            elif category == CommandCategory.SYSTEM:
                parameters = self._extract_system_parameters(text)
            elif category == CommandCategory.MEDIA:
                parameters = self._extract_media_parameters(text)
            elif category == CommandCategory.FILE:
                parameters = self._extract_file_parameters(text)
        
        except Exception as e:
            self.logger.error(f"Error extracting parameters: {e}")
        
        return parameters
    
    def _extract_typing_parameters(self, text: str) -> Dict[str, str]:
        """Extract parameters for typing commands"""
        parameters = {}
        
        # Extract text to type
        if 'yaz' in text or 'type' in text:
            # Find text after "yaz" or "type"
            match = re.search(r'(?:yaz|type)\s+(.+)', text)
            if match:
                parameters['text'] = match.group(1).strip()
        
        # Extract special keys
        special_keys = ['enter', 'gir', 'tab', 'sekme', 'space', 'boşluk', 
                       'backspace', 'sil', 'ctrl', 'alt', 'shift', 'esc']
        
        for key in special_keys:
            if key in text:
                parameters['key'] = key
                break
        
        return parameters
    
    def _extract_application_parameters(self, text: str) -> Dict[str, str]:
        """Extract parameters for application commands"""
        parameters = {}
        
        # Extract action
        if any(word in text for word in ['aç', 'open', 'launch', 'başlat']):
            parameters['action'] = 'open'
        elif any(word in text for word in ['kapat', 'close', 'sonlandır']):
            parameters['action'] = 'close'
        elif any(word in text for word in ['değiştir', 'switch', 'geç']):
            parameters['action'] = 'switch'
        elif any(word in text for word in ['listele', 'list', 'göster']):
            parameters['action'] = 'list'
        
        # Extract application name
        app_names = ['cursor', 'vscode', 'chrome', 'firefox', 'notepad', 
                    'calculator', 'explorer', 'word', 'excel', 'powerpoint']
        
        for app in app_names:
            if app in text:
                parameters['app_name'] = app
                break
        
        return parameters
    
    def _extract_browser_parameters(self, text: str) -> Dict[str, str]:
        """Extract parameters for browser commands"""
        parameters = {}
        
        # Extract action
        if any(word in text for word in ['ara', 'search']):
            parameters['action'] = 'search'
        elif any(word in text for word in ['aç', 'open']):
            parameters['action'] = 'open_url'
        elif 'yeni sekme' in text or 'new tab' in text:
            parameters['action'] = 'new_tab'
        elif 'sekme kapat' in text or 'close tab' in text:
            parameters['action'] = 'close_tab'
        
        # Extract search engine
        search_engines = ['google', 'youtube', 'github', 'stackoverflow']
        for engine in search_engines:
            if engine in text:
                parameters['engine'] = engine
                break
        
        # Extract URL or search query
        if 'ara' in text or 'search' in text:
            # Find text after search keywords
            match = re.search(r'(?:ara|search)\s+(.+)', text)
            if match:
                parameters['query'] = match.group(1).strip()
        
        return parameters
    
    def _extract_system_parameters(self, text: str) -> Dict[str, str]:
        """Extract parameters for system commands"""
        parameters = {}
        
        # Extract action
        if any(word in text for word in ['kapat', 'shutdown']):
            parameters['action'] = 'shutdown'
        elif any(word in text for word in ['yeniden başlat', 'restart', 'reboot']):
            parameters['action'] = 'restart'
        elif any(word in text for word in ['uyku', 'sleep']):
            parameters['action'] = 'sleep'
        elif any(word in text for word in ['kilit', 'lock']):
            parameters['action'] = 'lock'
        elif any(word in text for word in ['ses', 'volume']):
            parameters['action'] = 'volume'
        elif any(word in text for word in ['parlaklık', 'brightness']):
            parameters['action'] = 'brightness'
        
        return parameters
    
    def _extract_media_parameters(self, text: str) -> Dict[str, str]:
        """Extract parameters for media commands"""
        parameters = {}
        
        # Extract action
        if any(word in text for word in ['çal', 'play', 'oynat']):
            parameters['action'] = 'play'
        elif any(word in text for word in ['dur', 'pause', 'duraklat']):
            parameters['action'] = 'pause'
        elif any(word in text for word in ['sonraki', 'next']):
            parameters['action'] = 'next'
        elif any(word in text for word in ['önceki', 'previous']):
            parameters['action'] = 'previous'
        
        # Extract media source
        media_sources = ['spotify', 'youtube', 'netflix']
        for source in media_sources:
            if source in text:
                parameters['source'] = source
                break
        
        return parameters
    
    def _extract_file_parameters(self, text: str) -> Dict[str, str]:
        """Extract parameters for file commands"""
        parameters = {}
        
        # Extract action
        if any(word in text for word in ['aç', 'open']):
            parameters['action'] = 'open'
        elif any(word in text for word in ['kaydet', 'save']):
            parameters['action'] = 'save'
        elif any(word in text for word in ['sil', 'delete']):
            parameters['action'] = 'delete'
        elif any(word in text for word in ['kopyala', 'copy']):
            parameters['action'] = 'copy'
        elif any(word in text for word in ['taşı', 'move']):
            parameters['action'] = 'move'
        
        return parameters
