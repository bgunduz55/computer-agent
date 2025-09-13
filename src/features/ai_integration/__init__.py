"""
AI Integration Features for JARVIS Computer Assistant

This package provides AI integration capabilities including multiple AI providers,
RAG system, and context management.
"""

from .ai_provider_manager import (
    AIProviderManager,
    BaseAIProvider,
    AIProviderType,
    ModelType,
    ModelInfo,
    AIRequest,
    AIResponse,
    get_ai_manager,
    cleanup_ai_manager
)

from .rag_system import (
    RAGSystem,
    Document,
    SearchResult,
    ChromaDBVectorStore,
    EmbeddingGenerator,
    get_rag_system,
    cleanup_rag_system
)

from .providers import (
    OllamaProvider,
    OpenAIProvider,
    GeminiProvider,
    OpenRouterProvider
)

__all__ = [
    # AI Provider Manager
    "AIProviderManager",
    "BaseAIProvider",
    "AIProviderType",
    "ModelType", 
    "ModelInfo",
    "AIRequest",
    "AIResponse",
    "get_ai_manager",
    "cleanup_ai_manager",
    
    # RAG System
    "RAGSystem",
    "Document",
    "SearchResult",
    "ChromaDBVectorStore",
    "EmbeddingGenerator",
    "get_rag_system",
    "cleanup_rag_system",
    
    # Providers
    "OllamaProvider",
    "OpenAIProvider",
    "GeminiProvider", 
    "OpenRouterProvider"
]

__version__ = "1.0.0"
