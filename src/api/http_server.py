"""
HTTP Server for JARVIS Computer Assistant

Provides REST API endpoints for settings management and other HTTP-based operations.
"""

import asyncio
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.settings_api import router as settings_router
from features.settings import get_settings_manager

logger = logging.getLogger(__name__)

# Global HTTP server instance
_http_server: Optional[FastAPI] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app"""
    # Startup
    logger.info("HTTP server starting up...")
    yield
    # Shutdown
    logger.info("HTTP server shutting down...")

def create_http_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="JARVIS Computer Assistant API",
        description="REST API for JARVIS Computer Assistant",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(settings_router)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "JARVIS Computer Assistant API",
            "version": "1.0.0"
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "JARVIS Computer Assistant API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "settings": "/api/settings/",
                "docs": "/docs"
            }
        }
    
    return app

def get_http_server() -> FastAPI:
    """Get global HTTP server instance"""
    global _http_server
    if _http_server is None:
        _http_server = create_http_app()
    return _http_server

async def start_http_server(host: str = "0.0.0.0", port: int = 8765) -> None:
    """Start HTTP server"""
    try:
        import uvicorn
        
        app = get_http_server()
        
        logger.info(f"Starting HTTP server on {host}:{port}")
        
        # Run server
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Failed to start HTTP server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(start_http_server())
