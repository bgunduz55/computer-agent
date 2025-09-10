"""
OpenRouter Provider for JARVIS Computer Assistant

This module provides integration with OpenRouter for accessing multiple AI models
through a unified API.
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Any

from ..ai_provider_manager import (
    BaseAIProvider, AIProviderType, ModelType, ModelInfo, 
    AIRequest, AIResponse
)

logger = logging.getLogger(__name__)

class OpenRouterProvider(BaseAIProvider):
    """OpenRouter provider implementation"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.base_url = "https://openrouter.ai/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self._models: List[ModelInfo] = []
    
    @property
    def provider_type(self) -> AIProviderType:
        return AIProviderType.OPENROUTER
    
    @property
    def available_models(self) -> List[ModelInfo]:
        return self._models
    
    def _initialize_provider(self) -> None:
        """Initialize OpenRouter provider"""
        try:
            if not self.api_key:
                raise ValueError("OpenRouter API key is required")
            
            # Create HTTP session with headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://jarvis-assistant.com",  # Optional: for analytics
                "X-Title": "JARVIS Computer Assistant"  # Optional: for analytics
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=300)
            )
            
            # Load available models
            self._load_models()
            
            self.logger.info("OpenRouter provider initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenRouter provider: {e}")
            raise
    
    def _load_models(self) -> None:
        """Load available OpenRouter models"""
        try:
            # Default OpenRouter models
            default_models = [
                ModelInfo(
                    id="openai/gpt-4",
                    name="GPT-4",
                    provider=AIProviderType.OPENROUTER,
                    model_type=ModelType.CHAT,
                    max_tokens=8192,
                    cost_per_token=0.00003,
                    context_length=8192,
                    is_available=True,
                    description="OpenAI GPT-4 via OpenRouter"
                ),
                ModelInfo(
                    id="openai/gpt-4-turbo",
                    name="GPT-4 Turbo",
                    provider=AIProviderType.OPENROUTER,
                    model_type=ModelType.CHAT,
                    max_tokens=128000,
                    cost_per_token=0.00001,
                    context_length=128000,
                    is_available=True,
                    description="OpenAI GPT-4 Turbo via OpenRouter"
                ),
                ModelInfo(
                    id="anthropic/claude-3-sonnet",
                    name="Claude 3 Sonnet",
                    provider=AIProviderType.OPENROUTER,
                    model_type=ModelType.CHAT,
                    max_tokens=4096,
                    cost_per_token=0.000003,
                    context_length=200000,
                    is_available=True,
                    description="Anthropic Claude 3 Sonnet via OpenRouter"
                ),
                ModelInfo(
                    id="anthropic/claude-3-opus",
                    name="Claude 3 Opus",
                    provider=AIProviderType.OPENROUTER,
                    model_type=ModelType.CHAT,
                    max_tokens=4096,
                    cost_per_token=0.000015,
                    context_length=200000,
                    is_available=True,
                    description="Anthropic Claude 3 Opus via OpenRouter"
                ),
                ModelInfo(
                    id="google/gemini-pro",
                    name="Gemini Pro",
                    provider=AIProviderType.OPENROUTER,
                    model_type=ModelType.CHAT,
                    max_tokens=32768,
                    cost_per_token=0.0000005,
                    context_length=32768,
                    is_available=True,
                    description="Google Gemini Pro via OpenRouter"
                ),
                ModelInfo(
                    id="meta-llama/llama-2-70b-chat",
                    name="Llama 2 70B Chat",
                    provider=AIProviderType.OPENROUTER,
                    model_type=ModelType.CHAT,
                    max_tokens=4096,
                    cost_per_token=0.0000007,
                    context_length=4096,
                    is_available=True,
                    description="Meta Llama 2 70B Chat via OpenRouter"
                ),
                ModelInfo(
                    id="mistralai/mistral-7b-instruct",
                    name="Mistral 7B Instruct",
                    provider=AIProviderType.OPENROUTER,
                    model_type=ModelType.CHAT,
                    max_tokens=8192,
                    cost_per_token=0.0000002,
                    context_length=8192,
                    is_available=True,
                    description="Mistral 7B Instruct via OpenRouter"
                )
            ]
            
            self._models.extend(default_models)
            self.logger.info(f"Loaded {len(self._models)} OpenRouter models")
        except Exception as e:
            self.logger.error(f"Failed to load OpenRouter models: {e}")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using OpenRouter API"""
        if not self.session:
            raise RuntimeError("OpenRouter provider not initialized")
        
        try:
            start_time = time.time()
            
            # Prepare request payload
            payload = {
                "model": request.model,
                "messages": [
                    {"role": "user", "content": request.prompt}
                ],
                "max_tokens": request.max_tokens or 1000,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "frequency_penalty": request.frequency_penalty,
                "presence_penalty": request.presence_penalty,
                "stream": request.stream
            }
            
            # Add context if provided
            if request.context:
                # Add context as system message
                payload["messages"].insert(0, {
                    "role": "system", 
                    "content": request.context.get("system_prompt", "")
                })
            
            # Make request to OpenRouter
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"OpenRouter API error: {response.status} - {error_message}")
                
                # Parse response
                response_data = await response.json()
                
                # Extract content
                choices = response_data.get("choices", [])
                if not choices:
                    raise RuntimeError("No response from OpenRouter API")
                
                content = choices[0]["message"]["content"]
                
                # Calculate metrics
                response_time = time.time() - start_time
                usage = response_data.get("usage", {})
                tokens_used = usage.get("total_tokens", 0)
                
                # Calculate cost
                model_info = self.get_model_info(request.model)
                cost = tokens_used * model_info.cost_per_token if model_info else 0.0
                
                return AIResponse(
                    content=content,
                    model=request.model,
                    provider=AIProviderType.OPENROUTER,
                    tokens_used=tokens_used,
                    cost=cost,
                    response_time=response_time,
                    metadata={
                        "usage": usage,
                        "finish_reason": choices[0].get("finish_reason"),
                        "model": response_data.get("model"),
                        "id": response_data.get("id"),
                        "object": response_data.get("object"),
                        "created": response_data.get("created"),
                        "provider": response_data.get("provider")
                    }
                )
        
        except Exception as e:
            self.logger.error(f"Failed to generate response with OpenRouter: {e}")
            raise
    
    async def generate_embedding(self, text: str, model: str = None) -> List[float]:
        """Generate text embedding using OpenRouter API"""
        if not self.session:
            raise RuntimeError("OpenRouter provider not initialized")
        
        try:
            # Use default embedding model if not specified
            if not model:
                model = "text-embedding-ada-002"  # Default embedding model
            
            payload = {
                "model": model,
                "input": text
            }
            
            async with self.session.post(
                f"{self.base_url}/embeddings",
                json=payload
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"OpenRouter embeddings API error: {response.status} - {error_message}")
                
                response_data = await response.json()
                data = response_data.get("data", [])
                if not data:
                    raise RuntimeError("No embedding data from OpenRouter API")
                
                return data[0]["embedding"]
        
        except Exception as e:
            self.logger.error(f"Failed to generate embedding with OpenRouter: {e}")
            raise
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        for model in self._models:
            if model.id == model_id:
                return model
        return None
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from OpenRouter API"""
        if not self.session:
            raise RuntimeError("OpenRouter provider not initialized")
        
        try:
            async with self.session.get(f"{self.base_url}/models") as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"OpenRouter list models API error: {response.status} - {error_message}")
                
                response_data = await response.json()
                return response_data.get("data", [])
        
        except Exception as e:
            self.logger.error(f"Failed to list OpenRouter models: {e}")
            return []
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics from OpenRouter"""
        if not self.session:
            raise RuntimeError("OpenRouter provider not initialized")
        
        try:
            async with self.session.get(f"{self.base_url}/auth/key") as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"OpenRouter usage stats API error: {response.status} - {error_message}")
                
                return await response.json()
        
        except Exception as e:
            self.logger.error(f"Failed to get OpenRouter usage stats: {e}")
            return {}
    
    def cleanup(self) -> None:
        """Cleanup OpenRouter provider"""
        if self.session:
            asyncio.create_task(self.session.close())
            self.session = None
        super().cleanup()
