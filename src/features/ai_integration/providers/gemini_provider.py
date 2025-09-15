"""
Google Gemini Provider for JARVIS Computer Assistant

This module provides integration with Google's Gemini API for AI model inference.
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

class GeminiProvider(BaseAIProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.session: Optional[aiohttp.ClientSession] = None
        self._models: List[ModelInfo] = []
    
    @property
    def provider_type(self) -> AIProviderType:
        return AIProviderType.GOOGLE_GEMINI
    
    @property
    def available_models(self) -> List[ModelInfo]:
        return self._models
    
    def _initialize_provider(self) -> None:
        """Initialize Gemini provider"""
        try:
            if not self.api_key:
                raise ValueError("Google Gemini API key is required")
            
            # Create HTTP session with headers
            headers = {
                "Content-Type": "application/json"
            }
            
            # Create session in the current event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No event loop running, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Don't create session here, create it in generate_response
            self.session = None  # Will be created in generate_response
            
            # Load available models
            self._load_models()
            
            self.logger.info("Google Gemini provider initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini provider: {e}")
            raise
    
    def _load_models(self) -> None:
        """Load available Gemini models"""
        try:
            # Default Gemini models
            default_models = [
                ModelInfo(
                    id="gemini-1.5-flash",
                    name="Gemini 1.5 Flash",
                    provider=AIProviderType.GOOGLE_GEMINI,
                    model_type=ModelType.CHAT,
                    max_tokens=1048576,
                    cost_per_token=0.000000075,
                    context_length=1048576,
                    is_available=True,
                    description="Fast and efficient Gemini model"
                ),
                ModelInfo(
                    id="gemini-pro-vision",
                    name="Gemini Pro Vision",
                    provider=AIProviderType.GOOGLE_GEMINI,
                    model_type=ModelType.CHAT,
                    max_tokens=16384,
                    cost_per_token=0.0000005,
                    context_length=16384,
                    is_available=True,
                    description="Gemini model with vision capabilities"
                ),
                ModelInfo(
                    id="gemini-1.5-pro",
                    name="Gemini 1.5 Pro",
                    provider=AIProviderType.GOOGLE_GEMINI,
                    model_type=ModelType.CHAT,
                    max_tokens=1048576,  # 1M tokens
                    cost_per_token=0.00000125,
                    context_length=1048576,
                    is_available=True,
                    description="Latest Gemini model with extended context"
                ),
                ModelInfo(
                    id="gemini-1.5-flash",
                    name="Gemini 1.5 Flash",
                    provider=AIProviderType.GOOGLE_GEMINI,
                    model_type=ModelType.CHAT,
                    max_tokens=1048576,
                    cost_per_token=0.000000075,
                    context_length=1048576,
                    is_available=True,
                    description="Fast and efficient Gemini model"
                )
            ]
            
            self._models.extend(default_models)
            self.logger.info(f"Loaded {len(self._models)} Gemini models")
        except Exception as e:
            self.logger.error(f"Failed to load Gemini models: {e}")
    
    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Generate response using Gemini API"""
        # Always create a fresh session for each request to avoid event loop issues
        session = None
        try:
            headers = {
                "Content-Type": "application/json"
            }
            session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=300)
            )
            start_time = time.time()
            
            # Prepare request payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": request.prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": request.temperature,
                    "topP": request.top_p,
                    "maxOutputTokens": request.max_tokens or 1000,
                    "candidateCount": 1
                }
            }
            
            # Add context if provided
            if request.context:
                system_instruction = request.context.get("system_prompt", "")
                if system_instruction:
                    payload["systemInstruction"] = {
                        "parts": [{"text": system_instruction}]
                    }
            
            # Make request to Gemini
            url = f"{self.base_url}/models/{request.model}:generateContent"
            params = {"key": self.api_key}
            
            async with session.post(
                url,
                json=payload,
                params=params
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"Gemini API error: {response.status} - {error_message}")
                
                # Parse response
                response_data = await response.json()
                
                # Extract content
                candidates = response_data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("No response from Gemini API")
                
                content = ""
                for part in candidates[0].get("content", {}).get("parts", []):
                    if "text" in part:
                        content += part["text"]
                
                # Calculate metrics
                response_time = time.time() - start_time
                
                # Estimate tokens (rough calculation)
                tokens_used = len(content.split()) * 1.3
                
                # Calculate cost
                model_info = self.get_model_info(request.model)
                cost = tokens_used * model_info.cost_per_token if model_info else 0.0
                
                return AIResponse(
                    content=content,
                    model=request.model,
                    provider=AIProviderType.GOOGLE_GEMINI,
                    tokens_used=int(tokens_used),
                    cost=cost,
                    response_time=response_time,
                    metadata={
                        "candidates": candidates,
                        "usageMetadata": response_data.get("usageMetadata", {}),
                        "finishReason": candidates[0].get("finishReason"),
                        "safetyRatings": candidates[0].get("safetyRatings", [])
                    }
                )
        
        except Exception as e:
            self.logger.error(f"Failed to generate response with Gemini: {e}")
            raise
        finally:
            # Always close the session
            if session:
                try:
                    await session.close()
                except Exception as e:
                    self.logger.warning(f"Error closing Gemini session: {e}")
    
    async def generate_embedding(self, text: str, model: str = None) -> List[float]:
        """Generate text embedding using Gemini API"""
        # Create a fresh session for embedding
        session = None
        try:
            headers = {
                "Content-Type": "application/json"
            }
            session = aiohttp.ClientSession(
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=300)
            )
            # Use default embedding model if not specified
            if not model:
                model = "embedding-001"  # Default Gemini embedding model
            
            payload = {
                "model": f"models/{model}",
                "content": {
                    "parts": [
                        {"text": text}
                    ]
                }
            }
            
            url = f"{self.base_url}/models/{model}:embedContent"
            params = {"key": self.api_key}
            
            async with session.post(
                url,
                json=payload,
                params=params
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"Gemini embeddings API error: {response.status} - {error_message}")
                
                response_data = await response.json()
                embedding = response_data.get("embedding", {}).get("values", [])
                
                if not embedding:
                    raise RuntimeError("No embedding data from Gemini API")
                
                return embedding
        
        except Exception as e:
            self.logger.error(f"Failed to generate embedding with Gemini: {e}")
            raise
        finally:
            # Always close the session
            if session:
                try:
                    await session.close()
                except Exception as e:
                    self.logger.warning(f"Error closing Gemini session: {e}")
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        for model in self._models:
            if model.id == model_id:
                return model
        return None
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from Gemini API"""
        if not self.session:
            raise RuntimeError("Gemini provider not initialized")
        
        try:
            url = f"{self.base_url}/models"
            params = {"key": self.api_key}
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    error_data = await response.json()
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    raise RuntimeError(f"Gemini list models API error: {response.status} - {error_message}")
                
                response_data = await response.json()
                return response_data.get("models", [])
        
        except Exception as e:
            self.logger.error(f"Failed to list Gemini models: {e}")
            return []
    
    def cleanup(self) -> None:
        """Cleanup Gemini provider"""
        if self.session:
            try:
                # Close session in current event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule cleanup
                    asyncio.create_task(self.session.close())
                else:
                    # Run cleanup directly
                    loop.run_until_complete(self.session.close())
            except Exception as e:
                self.logger.warning(f"Error closing Gemini session: {e}")
            finally:
                self.session = None
        super().cleanup()
