"""
RAG (Retrieval Augmented Generation) System for JARVIS Computer Assistant

This module provides RAG capabilities including document indexing, vector storage,
semantic search, and context-aware response generation.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import hashlib
import sqlite3
from datetime import datetime
from abc import ABC, abstractmethod

# Vector database imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Text processing imports
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from .ai_provider_manager import AIProviderManager, AIRequest, AIResponse, AIProviderType

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document structure for RAG system"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class SearchResult:
    """Search result structure"""
    document: Document
    similarity_score: float
    rank: int

class BaseVectorStore(ABC):
    """Base class for vector storage implementations"""
    
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector store"""
        pass
    
    @abstractmethod
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        pass
    
    @abstractmethod
    async def list_documents(self) -> List[Document]:
        """List all documents"""
        pass

class ChromaDBVectorStore(BaseVectorStore):
    """ChromaDB vector store implementation"""
    
    def __init__(self, collection_name: str = "jarvis_documents", persist_directory: str = "data/vectordb"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize ChromaDB"""
        try:
            if not CHROMADB_AVAILABLE:
                raise RuntimeError("ChromaDB not available")
            
            # Create persist directory
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.Client(
                chromadb.config.Settings(
                    persist_directory=self.persist_directory,
                    anonymized_telemetry=False
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "JARVIS document collection"}
            )
            
            self.logger.info("ChromaDB vector store initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            return False
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to ChromaDB"""
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            # Prepare data for ChromaDB
            ids = [doc.id for doc in documents]
            contents = [doc.content for doc in documents]
            embeddings = [doc.embedding for doc in documents if doc.embedding]
            metadatas = [doc.metadata for doc in documents]
            
            # Add to collection
            if embeddings:
                self.collection.add(
                    ids=ids,
                    documents=contents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
            else:
                self.collection.add(
                    ids=ids,
                    documents=contents,
                    metadatas=metadatas
                )
            
            self.logger.info(f"Added {len(documents)} documents to ChromaDB")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add documents to ChromaDB: {e}")
            return False
    
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        """Search ChromaDB for similar documents"""
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            # Search collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Convert to SearchResult objects
            search_results = []
            for i, (doc_id, content, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                document = Document(
                    id=doc_id,
                    content=content,
                    metadata=metadata or {},
                    embedding=None  # Not needed in search results
                )
                
                # Convert distance to similarity score (1 - distance)
                similarity_score = 1.0 - distance
                
                search_results.append(SearchResult(
                    document=document,
                    similarity_score=similarity_score,
                    rank=i + 1
                ))
            
            return search_results
        except Exception as e:
            self.logger.error(f"Failed to search ChromaDB: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from ChromaDB"""
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            self.collection.delete(ids=[document_id])
            self.logger.info(f"Deleted document {document_id} from ChromaDB")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete document from ChromaDB: {e}")
            return False
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID from ChromaDB"""
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            results = self.collection.get(ids=[document_id])
            if not results['ids']:
                return None
            
            return Document(
                id=results['ids'][0],
                content=results['documents'][0],
                metadata=results['metadatas'][0] or {},
                embedding=None
            )
        except Exception as e:
            self.logger.error(f"Failed to get document from ChromaDB: {e}")
            return None
    
    async def list_documents(self) -> List[Document]:
        """List all documents from ChromaDB"""
        try:
            if not self.collection:
                raise RuntimeError("ChromaDB not initialized")
            
            results = self.collection.get()
            documents = []
            
            for i, doc_id in enumerate(results['ids']):
                documents.append(Document(
                    id=doc_id,
                    content=results['documents'][i],
                    metadata=results['metadatas'][i] or {},
                    embedding=None
                ))
            
            return documents
        except Exception as e:
            self.logger.error(f"Failed to list documents from ChromaDB: {e}")
            return []

class EmbeddingGenerator:
    """Text embedding generator"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize embedding model"""
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise RuntimeError("Sentence Transformers not available")
            
            self.model = SentenceTransformer(self.model_name)
            self.logger.info(f"Embedding model {self.model_name} initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize embedding model: {e}")
            return False
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            if not self.model:
                raise RuntimeError("Embedding model not initialized")
            
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            return []
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            if not self.model:
                raise RuntimeError("Embedding model not initialized")
            
            embeddings = self.model.encode(texts)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            return []

class RAGSystem:
    """RAG (Retrieval Augmented Generation) system"""
    
    def __init__(self, vector_store: BaseVectorStore = None, embedding_generator: EmbeddingGenerator = None):
        self.vector_store = vector_store or ChromaDBVectorStore()
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.ai_manager = None
        self.logger = logging.getLogger(__name__)
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize RAG system"""
        try:
            # Initialize vector store
            if not await self.vector_store.initialize():
                raise RuntimeError("Failed to initialize vector store")
            
            # Initialize embedding generator
            if not await self.embedding_generator.initialize():
                raise RuntimeError("Failed to initialize embedding generator")
            
            # Initialize AI manager
            from .ai_provider_manager import get_ai_manager
            self.ai_manager = get_ai_manager()
            
            self._initialized = True
            self.logger.info("RAG system initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG system: {e}")
            return False
    
    async def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the RAG system"""
        try:
            if not self._initialized:
                raise RuntimeError("RAG system not initialized")
            
            # Generate document ID
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            # Generate embedding
            embedding = await self.embedding_generator.generate_embedding(content)
            
            # Create document
            document = Document(
                id=doc_id,
                content=content,
                metadata=metadata or {},
                embedding=embedding,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Add to vector store
            await self.vector_store.add_documents([document])
            
            self.logger.info(f"Added document {doc_id} to RAG system")
            return doc_id
        except Exception as e:
            self.logger.error(f"Failed to add document: {e}")
            return ""
    
    async def search_documents(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search for relevant documents"""
        try:
            if not self._initialized:
                raise RuntimeError("RAG system not initialized")
            
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_embedding(query)
            
            # Search vector store
            results = await self.vector_store.search(query_embedding, top_k)
            
            self.logger.info(f"Found {len(results)} relevant documents for query: {query[:50]}...")
            return results
        except Exception as e:
            self.logger.error(f"Failed to search documents: {e}")
            return []
    
    async def generate_response(self, query: str, context_documents: List[SearchResult] = None, 
                              model: str = None, max_tokens: int = 1000) -> Optional[AIResponse]:
        """Generate RAG response"""
        try:
            if not self._initialized:
                raise RuntimeError("RAG system not initialized")
            
            # Search for relevant documents if not provided
            if context_documents is None:
                context_documents = await self.search_documents(query, top_k=3)
            
            # Build context from documents
            context = self._build_context(context_documents)
            
            # Create AI request
            request = AIRequest(
                prompt=query,
                model=model or "gpt-3.5-turbo",
                max_tokens=max_tokens,
                temperature=0.7,
                context={
                    "system_prompt": "You are JARVIS, an intelligent computer assistant. Use the provided context to answer questions accurately and helpfully.",
                    "context": context
                }
            )
            
            # Generate response
            response = await self.ai_manager.generate_response(request)
            
            if response:
                # Add RAG metadata
                response.metadata = response.metadata or {}
                response.metadata.update({
                    "rag_enabled": True,
                    "context_documents": len(context_documents),
                    "context_sources": [doc.document.id for doc in context_documents]
                })
            
            return response
        except Exception as e:
            self.logger.error(f"Failed to generate RAG response: {e}")
            return None
    
    def _build_context(self, documents: List[SearchResult]) -> str:
        """Build context string from documents"""
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Context {i} (Similarity: {doc.similarity_score:.3f}):\n{doc.document.content}")
        
        return "\n\n".join(context_parts)
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the RAG system"""
        try:
            if not self._initialized:
                raise RuntimeError("RAG system not initialized")
            
            return await self.vector_store.delete_document(document_id)
        except Exception as e:
            self.logger.error(f"Failed to delete document: {e}")
            return False
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        try:
            if not self._initialized:
                raise RuntimeError("RAG system not initialized")
            
            return await self.vector_store.get_document(document_id)
        except Exception as e:
            self.logger.error(f"Failed to get document: {e}")
            return None
    
    async def list_documents(self) -> List[Document]:
        """List all documents"""
        try:
            if not self._initialized:
                raise RuntimeError("RAG system not initialized")
            
            return await self.vector_store.list_documents()
        except Exception as e:
            self.logger.error(f"Failed to list documents: {e}")
            return []
    
    async def cleanup(self) -> None:
        """Cleanup RAG system"""
        self._initialized = False
        self.logger.info("RAG system cleaned up")

# Global RAG system instance
_rag_system: Optional[RAGSystem] = None

def get_rag_system() -> RAGSystem:
    """Get global RAG system instance"""
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system

async def cleanup_rag_system() -> None:
    """Cleanup global RAG system instance"""
    global _rag_system
    if _rag_system:
        await _rag_system.cleanup()
        _rag_system = None
