"""
AI Provider Manager for JARVIS Computer Assistant

This module provides a centralized management system for multiple AI providers
including OpenAI, Google Gemini, OpenRouter, and Ollama.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
import json
import time
from pathlib import Path

try:
    from features.system_info import get_system_info_manager
    from features.application_control import get_application_manager
except ImportError:
    get_system_info_manager = None
    get_application_manager = None

logger = logging.getLogger(__name__)

class AIProviderType(Enum):
    """Supported AI provider types"""
    OPENAI = "openai"
    GOOGLE_GEMINI = "google_gemini"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"

class ModelType(Enum):
    """Model types for different tasks"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    CODE_GENERATION = "code_generation"

@dataclass
class ModelInfo:
    """AI model information"""
    id: str
    name: str
    provider: AIProviderType
    model_type: ModelType
    max_tokens: int
    cost_per_token: float
    context_length: int
    is_available: bool = True
    description: str = ""

@dataclass
class AIRequest:
    """AI request structure"""
    prompt: str
    model: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = False
    context: Optional[Dict[str, Any]] = None

@dataclass
class AIResponse:
    """AI response structure"""
    content: str
    model: str
    provider: AIProviderType
    tokens_used: int
    cost: float
    response_time: float
    metadata: Dict[str, Any] = None

class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        self.api_key = api_key
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._initialized = False
        self._rate_limit_remaining = 0
        self._rate_limit_reset = 0
    
    @property
    @abstractmethod
    def provider_type(self) -> AIProviderType:
        """Provider type"""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[ModelInfo]:
        """Available models"""
        pass
    
    @abstractmethod
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate AI response"""
        pass
    
    @abstractmethod
    async def generate_embedding(self, text: str, model: str = None) -> List[float]:
        """Generate text embedding"""
        pass
    
    @abstractmethod
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        pass
    
    def initialize(self) -> bool:
        """Initialize the provider"""
        if self._initialized:
            return True
        
        try:
            self._initialize_provider()
            self._initialized = True
            self.logger.info(f"AI provider {self.provider_type.value} initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize AI provider {self.provider_type.value}: {e}")
            return False
    
    @abstractmethod
    def _initialize_provider(self) -> None:
        """Initialize the specific provider"""
        pass
    
    def cleanup(self) -> None:
        """Cleanup provider resources"""
        self._initialized = False
        self.logger.info(f"AI provider {self.provider_type.value} cleaned up")
    
    def is_rate_limited(self) -> bool:
        """Check if provider is rate limited"""
        if self._rate_limit_remaining <= 0:
            return time.time() < self._rate_limit_reset
        return False
    
    def update_rate_limit(self, remaining: int, reset_time: int) -> None:
        """Update rate limit information"""
        self._rate_limit_remaining = remaining
        self._rate_limit_reset = reset_time

class AIProviderManager:
    """Central AI provider management system"""
    
    def __init__(self, config_path: str = "config/ai_providers.json"):
        self.config_path = Path(config_path)
        self.providers: Dict[AIProviderType, BaseAIProvider] = {}
        self.default_provider: Optional[AIProviderType] = None
        self.current_provider: Optional[AIProviderType] = None
        self.model_cache: Dict[str, ModelInfo] = {}
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load AI provider configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default configuration
                default_config = {
                    "providers": {
                        "openai": {
                            "api_key": "",
                            "enabled": False,
                            "models": ["gpt-4", "gpt-3.5-turbo", "text-embedding-ada-002"]
                        },
                        "google_gemini": {
                            "api_key": "",
                            "enabled": False,
                            "models": ["gemini-pro", "gemini-pro-vision"]
                        },
                        "openrouter": {
                            "api_key": "",
                            "enabled": False,
                            "models": ["openai/gpt-4", "anthropic/claude-3-sonnet"]
                        },
                        "ollama": {
                            "api_key": "",
                            "enabled": True,
                            "base_url": "http://localhost:11434",
                            "models": ["deepseek-r1:8b"]
                        }
                    },
                    "default_provider": "ollama",
                    "fallback_provider": "openai",
                    "cost_optimization": True,
                    "rate_limiting": True
                }
                
                # Save default configuration
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                
                return default_config
        except Exception as e:
            self.logger.error(f"Failed to load AI provider config: {e}")
            return {}
    
    def initialize(self) -> bool:
        """Initialize AI provider manager"""
        if self._initialized:
            return True
        
        try:
            # Initialize enabled providers
            for provider_name, provider_config in self.config.get("providers", {}).items():
                if not provider_config.get("enabled", False):
                    continue
                
                provider_type = AIProviderType(provider_name)
                provider = self._create_provider(provider_type, provider_config)
                
                if provider and provider.initialize():
                    self.providers[provider_type] = provider
                    self.logger.info(f"AI provider {provider_name} initialized")
                else:
                    self.logger.warning(f"Failed to initialize AI provider {provider_name}")
            
            # Set default provider
            default_name = self.config.get("default_provider", "ollama")
            self.default_provider = AIProviderType(default_name)
            self.current_provider = self.default_provider
            
            # Cache available models
            self._cache_models()
            
            self._initialized = True
            self.logger.info("AI provider manager initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize AI provider manager: {e}")
            return False
    
    def _create_provider(self, provider_type: AIProviderType, config: Dict[str, Any]) -> Optional[BaseAIProvider]:
        """Create AI provider instance"""
        try:
            if provider_type == AIProviderType.OPENAI:
                from .providers.openai_provider import OpenAIProvider
                return OpenAIProvider(config.get("api_key", ""), config)
            elif provider_type == AIProviderType.GOOGLE_GEMINI:
                from .providers.gemini_provider import GeminiProvider
                return GeminiProvider(config.get("api_key", ""), config)
            elif provider_type == AIProviderType.OPENROUTER:
                from .providers.openrouter_provider import OpenRouterProvider
                return OpenRouterProvider(config.get("api_key", ""), config)
            elif provider_type == AIProviderType.OLLAMA:
                from .providers.ollama_provider import OllamaProvider
                return OllamaProvider(config.get("api_key", ""), config)
            else:
                self.logger.warning(f"Unsupported provider type: {provider_type}")
                return None
        except ImportError as e:
            self.logger.error(f"Failed to import provider {provider_type.value}: {e}")
            return None
    
    def _cache_models(self) -> None:
        """Cache available models from all providers"""
        for provider in self.providers.values():
            for model in provider.available_models:
                self.model_cache[model.id] = model
    
    async def generate_response(self, prompt: str, provider: Optional[AIProviderType] = None) -> Optional[AIResponse]:
        """Generate AI response using string prompt"""
        # Add system context to prompt
        enhanced_prompt = self._enhance_prompt_with_context(prompt)
        
        # Create AIRequest from string prompt
        request = AIRequest(
            prompt=enhanced_prompt,
            model=self.config.get("default_model", "deepseek-r1:8b"),
            max_tokens=self.config.get("max_tokens", 1000),
            temperature=self.config.get("temperature", 0.7)
        )
        return await self.generate_response_with_request(request, provider)
    
    async def generate_response_with_request(self, request: AIRequest, provider: Optional[AIProviderType] = None) -> Optional[AIResponse]:
        """Generate AI response using specified or default provider"""
        try:
            # Determine provider to use
            if provider is None:
                provider = self.default_provider
            
            if provider not in self.providers:
                self.logger.error(f"Provider {provider.value} not available")
                return None
            
            # Check rate limiting
            if self.providers[provider].is_rate_limited():
                self.logger.warning(f"Provider {provider.value} is rate limited")
                # Try fallback provider
                fallback = self.config.get("fallback_provider")
                if fallback and AIProviderType(fallback) in self.providers:
                    provider = AIProviderType(fallback)
                else:
                    return None
            
            # Generate response
            response = await self.providers[provider].generate_response(request)
            
            # Update rate limiting info
            if hasattr(response, 'metadata') and response.metadata:
                self.providers[provider].update_rate_limit(
                    response.metadata.get('rate_limit_remaining', 0),
                    response.metadata.get('rate_limit_reset', 0)
                )
            
            return response
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            return None
    
    async def generate_embedding(self, text: str, model: str = None, provider: Optional[AIProviderType] = None) -> Optional[List[float]]:
        """Generate text embedding"""
        try:
            # Determine provider to use
            if provider is None:
                provider = self.default_provider
            
            if provider not in self.providers:
                self.logger.error(f"Provider {provider.value} not available")
                return None
            
            return await self.providers[provider].generate_embedding(text, model)
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def get_available_models(self, provider: Optional[AIProviderType] = None) -> List[ModelInfo]:
        """Get available models"""
        if provider:
            return self.providers.get(provider, {}).available_models
        else:
            return list(self.model_cache.values())
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        return self.model_cache.get(model_id)
    
    def get_provider_for_model(self, model_id: str) -> Optional[AIProviderType]:
        """Get provider for a specific model"""
        model_info = self.get_model_info(model_id)
        return model_info.provider if model_info else None
    
    def get_cost_estimate(self, request: AIRequest) -> float:
        """Estimate cost for a request"""
        model_info = self.get_model_info(request.model)
        if not model_info:
            return 0.0
        
        # Simple token estimation (rough)
        estimated_tokens = len(request.prompt.split()) * 1.3
        return estimated_tokens * model_info.cost_per_token
    
    def switch_default_provider(self, provider: AIProviderType) -> bool:
        """Switch default provider"""
        if provider in self.providers:
            self.default_provider = provider
            self.logger.info(f"Default provider switched to {provider.value}")
            return True
        else:
            self.logger.error(f"Provider {provider.value} not available")
            return False
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for provider_type, provider in self.providers.items():
            status[provider_type.value] = {
                "initialized": provider._initialized,
                "rate_limited": provider.is_rate_limited(),
                "models_count": len(provider.available_models)
            }
        return status
    
    def get_current_provider(self):
        """Get the current active provider"""
        try:
            if self.current_provider and self.current_provider in self.providers:
                return self.providers[self.current_provider]
            else:
                # Fallback to first available provider
                for provider in self.providers.values():
                    if provider._initialized:
                        return provider
                return None
        except Exception as e:
            self.logger.error(f"Failed to get current provider: {e}")
            return None
    
    def _enhance_prompt_with_context(self, prompt: str) -> str:
        """Enhance prompt with system context"""
        try:
            context_parts = []
            
            # Add system time context
            if get_system_info_manager is not None:
                system_info_manager = get_system_info_manager()
                if not system_info_manager._initialized:
                    system_info_manager.initialize()
                time_context = system_info_manager.get_time_context_for_ai()
                context_parts.append(f"Current Time: {time_context}")
            
            # Add application context
            if get_application_manager is not None:
                app_manager = get_application_manager()
                if app_manager._initialized:
                    app_summary = app_manager.get_application_summary()
                    if app_summary:
                        browsers = app_summary.get('browsers', [])
                        if browsers:
                            browser_names = [b['name'] for b in browsers]
                            context_parts.append(f"Running Browsers: {', '.join(browser_names)}")
            
            # Build enhanced prompt
            if context_parts:
                context_text = "\n".join(context_parts)
                enhanced_prompt = f"""System Context:
{context_text}

User Query: {prompt}

Please respond naturally and helpfully. If the user asks about:
- Time, date, or system information, use the provided context above
- Running applications or browsers, you can help manage them
- Opening/closing browser tabs or searching, you can assist with browser control

Available commands for application control:
- "close [application name]" - Close an application
- "open [url]" - Open URL in browser
- "search [query]" - Search in browser
- "close current tab" - Close current browser tab
- "list running apps" - Show running applications"""
            else:
                enhanced_prompt = prompt
            
            return enhanced_prompt
        except Exception as e:
            self.logger.error(f"Failed to enhance prompt with context: {e}")
            return prompt
    
    async def process_query(self, query: str, **kwargs) -> str:
        """Process a user query and return response"""
        try:
            self.logger.info(f"Processing AI query: {query[:50]}...")
            
            # Check if we're initialized
            if not self._initialized:
                self.logger.warning("AI provider manager not initialized, cannot process AI query")
                return "AI service is currently unavailable (not initialized)"
            
            # Enhance prompt with context
            enhanced_prompt = self._enhance_prompt_with_context(query)
            
            # Get current provider and model
            current_provider = self.get_current_provider()
            if current_provider:
                # Get default model from provider
                default_model = "deepseek-r1:8b"  # Default model
                if current_provider.available_models:
                    default_model = current_provider.available_models[0].id
                
                # Create AIRequest object
                ai_request = AIRequest(
                    prompt=enhanced_prompt,
                    model=default_model,
                    max_tokens=kwargs.get('max_tokens', 1000),
                    temperature=kwargs.get('temperature', 0.7),
                    stream=False
                )
                
                # Add timeout to prevent hanging
                try:
                    response = await asyncio.wait_for(
                        current_provider.generate_response(ai_request),
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    self.logger.warning("AI response timeout")
                    return "AI response timed out"
                except asyncio.CancelledError:
                    self.logger.warning("AI request cancelled")
                    return "AI request was cancelled"
                
                # Return content if it's an AIResponse object
                if hasattr(response, 'content'):
                    return response.content
                elif isinstance(response, str):
                    return response
                else:
                    return str(response)
            else:
                return "AI provider not available"
                
        except Exception as e:
            self.logger.error(f"Failed to process query: {e}")
            return f"Error processing query: {e}"
    
    def cleanup(self) -> None:
        """Cleanup all providers"""
        self._initialized = False
        
        for provider in self.providers.values():
            try:
                provider.cleanup()
            except Exception as e:
                self.logger.warning(f"Error cleaning up provider: {e}")
        
        self.providers.clear()
        self.model_cache.clear()
        self.logger.info("AI provider manager cleaned up")

# Global instance
_ai_manager: Optional[AIProviderManager] = None

def get_ai_manager() -> AIProviderManager:
    """Get global AI manager instance"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIProviderManager()
    return _ai_manager

def cleanup_ai_manager() -> None:
    """Cleanup global AI manager instance"""
    global _ai_manager
    if _ai_manager:
        _ai_manager.cleanup()
        _ai_manager = None
