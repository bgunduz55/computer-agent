"""
AI Providers for JARVIS Computer Assistant

This package contains implementations for various AI providers including
OpenAI, Google Gemini, OpenRouter, and Ollama.
"""

from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .openrouter_provider import OpenRouterProvider

__all__ = [
    "OllamaProvider",
    "OpenAIProvider", 
    "GeminiProvider",
    "OpenRouterProvider"
]

__version__ = "1.0.0"
