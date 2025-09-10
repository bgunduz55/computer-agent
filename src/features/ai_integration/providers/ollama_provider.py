"""
Ollama AI Provider for JARVIS Computer Assistant

This module provides integration with Ollama for local AI model inference.
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..ai_provider_manager import (
    BaseAIProvider, AIProviderType, ModelType, ModelInfo, 
    AIRequest, AIResponse
)

logger = logging.getLogger(__name__)

class OllamaProvider(BaseAIProvider):
    """Ollama AI provider implementation"""
    
    def __init__(self, api_key: str = "", config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.base_url = self.config.get("base_url", "http://localhost:11434")
        self.session: Optional[aiohttp.ClientSession] = None
        self._models: List[ModelInfo] = []
    
    @property
    def provider_type(self) -> AIProviderType:
        return AIProviderType.OLLAMA
    
    @property
    def available_models(self) -> List[ModelInfo]:
        return self._models
    
    def _initialize_provider(self) -> None:
        """Initialize Ollama provider"""
        try:
            # Create HTTP session with better configuration
            connector = aiohttp.TCPConnector(
                limit=10,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(
                    total=300,
                    connect=30,
                    sock_read=60
                ),
                headers={
                    'User-Agent': 'JARVIS-Computer-Assistant/1.0',
                    'Content-Type': 'application/json'
                }
            )
            
            # Load available models
            self._load_models()
            
            self.logger.info("Ollama provider initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama provider: {e}")
            raise
    
    def _load_models(self) -> None:
        """Load available Ollama models"""
        try:
            # Default models from config
            default_models = self.config.get("models", [
                "gpt-oss:20b",
                "deepseek-r1:7b",
                "llama2:7b",
                "codellama:7b"
            ])
            
            for model_id in default_models:
                self._models.append(ModelInfo(
                    id=model_id,
                    name=model_id,
                    provider=AIProviderType.OLLAMA,
                    model_type=ModelType.CHAT,
                    max_tokens=4096,
                    cost_per_token=0.0,  # Local inference is free
                    context_length=4096,
                    is_available=True,
                    description=f"Ollama {model_id} model"
                ))
            
            self.logger.info(f"Loaded {len(self._models)} Ollama models")
        except Exception as e:
            self.logger.error(f"Failed to load Ollama models: {e}")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using Ollama"""
        if not self.session:
            raise RuntimeError("Ollama provider not initialized")
        
        try:
            self.logger.info(f"Generating response for model: {request.model}")
            
            start_time = time.time()
            
            # Prepare request payload
            payload = {
                "model": request.model,
                "prompt": request.prompt,
                "stream": request.stream,
                "options": {
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "num_predict": request.max_tokens or 1000
                }
            }
            
            # Add context if provided
            if request.context:
                payload["context"] = request.context
            
            # Make request to Ollama with new session to avoid event loop issues
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=10, limit_per_host=5),
                timeout=aiohttp.ClientTimeout(total=300, connect=30, sock_read=60),
                headers={'User-Agent': 'JARVIS-Computer-Assistant/1.0', 'Content-Type': 'application/json'}
            ) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(f"Ollama API error: {response.status} - {error_text}")
                    
                    # Parse response
                    response_data = await response.json()
                    
                    # Extract content
                    content = response_data.get("response", "")
                    
                    # Calculate metrics
                    response_time = time.time() - start_time
                    tokens_used = len(content.split())  # Rough estimation
                    
                    return AIResponse(
                        content=content,
                        model=request.model,
                        provider=AIProviderType.OLLAMA,
                        tokens_used=tokens_used,
                        cost=0.0,  # Local inference is free
                        response_time=response_time,
                        metadata={
                            "context": response_data.get("context"),
                            "done": response_data.get("done", True),
                            "total_duration": response_data.get("total_duration", 0),
                            "load_duration": response_data.get("load_duration", 0),
                            "prompt_eval_duration": response_data.get("prompt_eval_duration", 0),
                            "eval_duration": response_data.get("eval_duration", 0)
                        }
                    )
        
        except Exception as e:
            self.logger.error(f"Failed to generate response with Ollama: {e}")
            raise
    
    async def generate_embedding(self, text: str, model: str = None) -> List[float]:
        """Generate text embedding using Ollama"""
        if not self.session:
            raise RuntimeError("Ollama provider not initialized")
        
        try:
            # Use default embedding model if not specified
            if not model:
                model = "nomic-embed-text"  # Default Ollama embedding model
            
            payload = {
                "model": model,
                "prompt": text
            }
            
            async with self.session.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama embeddings API error: {response.status} - {error_text}")
                
                response_data = await response.json()
                return response_data.get("embedding", [])
        
        except Exception as e:
            self.logger.error(f"Failed to generate embedding with Ollama: {e}")
            raise
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        for model in self._models:
            if model.id == model_id:
                return model
        return None
    
    async def pull_model(self, model_id: str) -> bool:
        """Pull a model from Ollama registry"""
        if not self.session:
            raise RuntimeError("Ollama provider not initialized")
        
        try:
            payload = {
                "name": model_id,
                "stream": False
            }
            
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    self.logger.error(f"Failed to pull model {model_id}: {error_text}")
                    return False
                
                self.logger.info(f"Successfully pulled model {model_id}")
                return True
        
        except Exception as e:
            self.logger.error(f"Failed to pull model {model_id}: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """List available models in Ollama"""
        if not self.session:
            raise RuntimeError("Ollama provider not initialized")
        
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama list models API error: {response.status} - {error_text}")
                
                response_data = await response.json()
                models = response_data.get("models", [])
                return [model["name"] for model in models]
        
        except Exception as e:
            self.logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    async def check_model_availability(self, model_id: str) -> bool:
        """Check if a model is available locally"""
        try:
            available_models = await self.list_models()
            return model_id in available_models
        except Exception as e:
            self.logger.error(f"Failed to check model availability: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup Ollama provider"""
        if self.session:
            try:
                # Check if event loop is still running
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running() and not loop.is_closed():
                        # Create task to close session
                        asyncio.create_task(self.session.close())
                    else:
                        # Event loop is closed or not running, close session synchronously
                        if hasattr(self.session, '_connector'):
                            self.session._connector.close()
                except RuntimeError:
                    # No running event loop, close session synchronously
                    if hasattr(self.session, '_connector'):
                        self.session._connector.close()
            except Exception as e:
                self.logger.warning(f"Error closing Ollama session: {e}")
            finally:
                self.session = None
        super().cleanup()
