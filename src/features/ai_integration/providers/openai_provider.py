"""
OpenAI Provider for JARVIS Computer Assistant

This module provides integration with OpenAI's API for GPT models and embeddings.
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

class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.base_url = "https://api.openai.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self._models: List[ModelInfo] = []
    
    @property
    def provider_type(self) -> AIProviderType:
        return AIProviderType.OPENAI
    
    @property
    def available_models(self) -> List[ModelInfo]:
        return self._models
    
    def _initialize_provider(self) -> None:
        """Initialize OpenAI provider"""
        try:
            if not self.api_key:
                raise ValueError("OpenAI API key is required")
            
            # Create HTTP session with headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=300)
            )
            
            # Load available models
            self._load_models()
            
            self.logger.info("OpenAI provider initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI provider: {e}")
            raise
    
    def _load_models(self) -> None:
        """Load available OpenAI models"""
        try:
            # Default OpenAI models
            default_models = [
                ModelInfo(
                    id="gpt-4",
                    name="GPT-4",
                    provider=AIProviderType.OPENAI,
                    model_type=ModelType.CHAT,
                    max_tokens=8192,
                    cost_per_token=0.00003,  # Approximate cost per token
                    context_length=8192,
                    is_available=True,
                    description="Most capable GPT-4 model"
                ),
                ModelInfo(
                    id="gpt-4-turbo",
                    name="GPT-4 Turbo",
                    provider=AIProviderType.OPENAI,
                    model_type=ModelType.CHAT,
                    max_tokens=128000,
                    cost_per_token=0.00001,
                    context_length=128000,
                    is_available=True,
                    description="Faster and more efficient GPT-4 model"
                ),
                ModelInfo(
                    id="gpt-3.5-turbo",
                    name="GPT-3.5 Turbo",
                    provider=AIProviderType.OPENAI,
                    model_type=ModelType.CHAT,
                    max_tokens=4096,
                    cost_per_token=0.000002,
                    context_length=4096,
                    is_available=True,
                    description="Fast and efficient GPT-3.5 model"
                ),
                ModelInfo(
                    id="text-embedding-ada-002",
                    name="Text Embedding Ada 002",
                    provider=AIProviderType.OPENAI,
                    model_type=ModelType.EMBEDDING,
                    max_tokens=8191,
                    cost_per_token=0.0000001,
                    context_length=8191,
                    is_available=True,
                    description="Text embedding model"
                ),
                ModelInfo(
                    id="text-embedding-3-small",
                    name="Text Embedding 3 Small",
                    provider=AIProviderType.OPENAI,
                    model_type=ModelType.EMBEDDING,
                    max_tokens=8191,
                    cost_per_token=0.00000002,
                    context_length=8191,
                    is_available=True,
                    description="Newer, more efficient embedding model"
                )
            ]
            
            self._models.extend(default_models)
            self.logger.info(f"Loaded {len(self._models)} OpenAI models")
        except Exception as e:
            self.logger.error(f"Failed to load OpenAI models: {e}")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using OpenAI API"""
        if not self.session:
            raise RuntimeError("OpenAI provider not initialized")
        
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
            
            # Make request to OpenAI
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"OpenAI API error: {response.status} - {error_message}")
                
                # Parse response
                response_data = await response.json()
                
                # Extract content
                choices = response_data.get("choices", [])
                if not choices:
                    raise RuntimeError("No response from OpenAI API")
                
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
                    provider=AIProviderType.OPENAI,
                    tokens_used=tokens_used,
                    cost=cost,
                    response_time=response_time,
                    metadata={
                        "usage": usage,
                        "finish_reason": choices[0].get("finish_reason"),
                        "model": response_data.get("model"),
                        "id": response_data.get("id"),
                        "object": response_data.get("object"),
                        "created": response_data.get("created")
                    }
                )
        
        except Exception as e:
            self.logger.error(f"Failed to generate response with OpenAI: {e}")
            raise
    
    async def generate_embedding(self, text: str, model: str = None) -> List[float]:
        """Generate text embedding using OpenAI API"""
        if not self.session:
            raise RuntimeError("OpenAI provider not initialized")
        
        try:
            # Use default embedding model if not specified
            if not model:
                model = "text-embedding-ada-002"
            
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
                    raise RuntimeError(f"OpenAI embeddings API error: {response.status} - {error_message}")
                
                response_data = await response.json()
                data = response_data.get("data", [])
                if not data:
                    raise RuntimeError("No embedding data from OpenAI API")
                
                return data[0]["embedding"]
        
        except Exception as e:
            self.logger.error(f"Failed to generate embedding with OpenAI: {e}")
            raise
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        for model in self._models:
            if model.id == model_id:
                return model
        return None
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from OpenAI API"""
        if not self.session:
            raise RuntimeError("OpenAI provider not initialized")
        
        try:
            async with self.session.get(f"{self.base_url}/models") as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"OpenAI list models API error: {response.status} - {error_message}")
                
                response_data = await response.json()
                return response_data.get("data", [])
        
        except Exception as e:
            self.logger.error(f"Failed to list OpenAI models: {e}")
            return []
    
    def cleanup(self) -> None:
        """Cleanup OpenAI provider"""
        if self.session:
            asyncio.create_task(self.session.close())
            self.session = None
        super().cleanup()
