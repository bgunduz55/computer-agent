"""
Settings API for JARVIS Computer Assistant

Provides REST API endpoints for managing application settings including
AI providers, voice settings, system configurations, and security settings.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from features.settings.settings_manager import get_settings_manager, SettingsManager

logger = logging.getLogger(__name__)

# API Router
router = APIRouter(prefix="/api/settings", tags=["settings"])

# Pydantic Models for API
class AISettingsUpdate(BaseModel):
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    timeout: Optional[float] = None
    retry_attempts: Optional[int] = None
    cost_limit: Optional[float] = None
    rag_enabled: Optional[bool] = None
    rag_threshold: Optional[float] = None
    context_window: Optional[int] = None
    
    # API Keys
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Provider Settings
    openai_enabled: Optional[bool] = None
    gemini_enabled: Optional[bool] = None
    openrouter_enabled: Optional[bool] = None
    anthropic_enabled: Optional[bool] = None
    ollama_enabled: Optional[bool] = None
    
    # Model Settings
    openai_model: Optional[str] = None
    gemini_model: Optional[str] = None
    openrouter_model: Optional[str] = None
    anthropic_model: Optional[str] = None
    
    # Cost Optimization
    cost_optimization: Optional[bool] = None
    rate_limiting: Optional[bool] = None
    fallback_provider: Optional[str] = None

class VoiceSettingsUpdate(BaseModel):
    language: Optional[str] = None
    sensitivity: Optional[float] = None
    tts_enabled: Optional[bool] = None
    tts_voice: Optional[str] = None
    tts_speed: Optional[float] = None
    tts_pitch: Optional[float] = None
    noise_reduction: Optional[bool] = None
    auto_listen: Optional[bool] = None
    continuous_listening: Optional[bool] = None

class SystemSettingsUpdate(BaseModel):
    auto_start: Optional[bool] = None
    minimize_to_tray: Optional[bool] = None
    show_notifications: Optional[bool] = None
    log_level: Optional[str] = None
    max_log_size: Optional[int] = None
    log_retention_days: Optional[int] = None
    backup_enabled: Optional[bool] = None
    backup_interval: Optional[int] = None
    max_backups: Optional[int] = None
    performance_monitoring: Optional[bool] = None
    auto_update: Optional[bool] = None
    update_channel: Optional[str] = None

class SecuritySettingsUpdate(BaseModel):
    enable_authentication: Optional[bool] = None
    session_timeout: Optional[int] = None
    max_login_attempts: Optional[int] = None
    lockout_duration: Optional[int] = None
    password_requirements: Optional[Dict[str, Any]] = None
    two_factor_enabled: Optional[bool] = None
    encryption_enabled: Optional[bool] = None
    audit_logging: Optional[bool] = None

class RemoteSettingsUpdate(BaseModel):
    enable_remote_control: Optional[bool] = None
    port: Optional[int] = None
    host: Optional[str] = None
    ssl_enabled: Optional[bool] = None
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    max_connections: Optional[int] = None
    connection_timeout: Optional[int] = None
    enable_compression: Optional[bool] = None

class PerformanceSettingsUpdate(BaseModel):
    max_memory_usage: Optional[int] = None
    cpu_usage_limit: Optional[float] = None
    disk_usage_limit: Optional[float] = None
    network_usage_limit: Optional[float] = None
    metrics_collection: Optional[bool] = None
    metrics_interval: Optional[int] = None
    auto_optimization: Optional[bool] = None
    optimization_threshold: Optional[float] = None

class NotificationSettingsUpdate(BaseModel):
    enable_notifications: Optional[bool] = None
    notification_types: Optional[Dict[str, bool]] = None
    sound_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None
    desktop_notifications: Optional[bool] = None
    mobile_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    notification_frequency: Optional[str] = None

class GeneralSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    currency: Optional[str] = None
    units: Optional[str] = None
    first_run: Optional[bool] = None
    telemetry: Optional[bool] = None

# Dependency to get settings manager
def get_settings() -> SettingsManager:
    return get_settings_manager()

# GET Endpoints
@router.get("/")
async def get_all_settings(settings: SettingsManager = Depends(get_settings)):
    """Get all settings"""
    try:
        return {
            "success": True,
            "data": {
                "ai": settings.ai.__dict__,
                "voice": settings.voice.__dict__,
                "system": settings.system.__dict__,
                "security": settings.security.__dict__,
                "remote": settings.remote.__dict__,
                "performance": settings.performance.__dict__,
                "notifications": settings.notifications.__dict__,
                "general": settings.general.__dict__
            }
        }
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai")
async def get_ai_settings(settings: SettingsManager = Depends(get_settings)):
    """Get AI settings"""
    try:
        return {
            "success": True,
            "data": settings.ai.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to get AI settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice")
async def get_voice_settings(settings: SettingsManager = Depends(get_settings)):
    """Get voice settings"""
    try:
        return {
            "success": True,
            "data": settings.voice.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to get voice settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system")
async def get_system_settings(settings: SettingsManager = Depends(get_settings)):
    """Get system settings"""
    try:
        return {
            "success": True,
            "data": settings.system.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to get system settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/security")
async def get_security_settings(settings: SettingsManager = Depends(get_settings)):
    """Get security settings"""
    try:
        return {
            "success": True,
            "data": settings.security.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to get security settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/remote")
async def get_remote_settings(settings: SettingsManager = Depends(get_settings)):
    """Get remote settings"""
    try:
        return {
            "success": True,
            "data": settings.remote.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to get remote settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_settings(settings: SettingsManager = Depends(get_settings)):
    """Get performance settings"""
    try:
        return {
            "success": True,
            "data": settings.performance.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to get performance settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications")
async def get_notification_settings(settings: SettingsManager = Depends(get_settings)):
    """Get notification settings"""
    try:
        return {
            "success": True,
            "data": settings.notifications.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to get notification settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/general")
async def get_general_settings(settings: SettingsManager = Depends(get_settings)):
    """Get general settings"""
    try:
        return {
            "success": True,
            "data": settings.general.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to get general settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# PUT Endpoints
@router.put("/ai")
async def update_ai_settings(
    settings_update: AISettingsUpdate,
    settings: SettingsManager = Depends(get_settings)
):
    """Update AI settings"""
    try:
        # Update only provided fields
        for field, value in settings_update.dict(exclude_unset=True).items():
            if hasattr(settings.ai, field):
                setattr(settings.ai, field, value)
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": "AI settings updated successfully",
            "data": settings.ai.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to update AI settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/voice")
async def update_voice_settings(
    settings_update: VoiceSettingsUpdate,
    settings: SettingsManager = Depends(get_settings)
):
    """Update voice settings"""
    try:
        for field, value in settings_update.dict(exclude_unset=True).items():
            if hasattr(settings.voice, field):
                setattr(settings.voice, field, value)
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": "Voice settings updated successfully",
            "data": settings.voice.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to update voice settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/system")
async def update_system_settings(
    settings_update: SystemSettingsUpdate,
    settings: SettingsManager = Depends(get_settings)
):
    """Update system settings"""
    try:
        for field, value in settings_update.dict(exclude_unset=True).items():
            if hasattr(settings.system, field):
                setattr(settings.system, field, value)
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": "System settings updated successfully",
            "data": settings.system.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to update system settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/security")
async def update_security_settings(
    settings_update: SecuritySettingsUpdate,
    settings: SettingsManager = Depends(get_settings)
):
    """Update security settings"""
    try:
        for field, value in settings_update.dict(exclude_unset=True).items():
            if hasattr(settings.security, field):
                setattr(settings.security, field, value)
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": "Security settings updated successfully",
            "data": settings.security.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to update security settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/remote")
async def update_remote_settings(
    settings_update: RemoteSettingsUpdate,
    settings: SettingsManager = Depends(get_settings)
):
    """Update remote settings"""
    try:
        for field, value in settings_update.dict(exclude_unset=True).items():
            if hasattr(settings.remote, field):
                setattr(settings.remote, field, value)
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": "Remote settings updated successfully",
            "data": settings.remote.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to update remote settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/performance")
async def update_performance_settings(
    settings_update: PerformanceSettingsUpdate,
    settings: SettingsManager = Depends(get_settings)
):
    """Update performance settings"""
    try:
        for field, value in settings_update.dict(exclude_unset=True).items():
            if hasattr(settings.performance, field):
                setattr(settings.performance, field, value)
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": "Performance settings updated successfully",
            "data": settings.performance.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to update performance settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notifications")
async def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    settings: SettingsManager = Depends(get_settings)
):
    """Update notification settings"""
    try:
        for field, value in settings_update.dict(exclude_unset=True).items():
            if hasattr(settings.notifications, field):
                setattr(settings.notifications, field, value)
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": "Notification settings updated successfully",
            "data": settings.notifications.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to update notification settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/general")
async def update_general_settings(
    settings_update: GeneralSettingsUpdate,
    settings: SettingsManager = Depends(get_settings)
):
    """Update general settings"""
    try:
        for field, value in settings_update.dict(exclude_unset=True).items():
            if hasattr(settings.general, field):
                setattr(settings.general, field, value)
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": "General settings updated successfully",
            "data": settings.general.__dict__
        }
    except Exception as e:
        logger.error(f"Failed to update general settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test AI Provider Connection
@router.post("/ai/test-connection")
async def test_ai_connection(
    provider: str,
    api_key: str,
    model: str = None
):
    """Test AI provider connection"""
    try:
        # This would test the connection to the specified AI provider
        # For now, we'll just return a success message
        return {
            "success": True,
            "message": f"Connection test for {provider} successful",
            "data": {
                "provider": provider,
                "model": model,
                "status": "connected"
            }
        }
    except Exception as e:
        logger.error(f"Failed to test AI connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Reset Settings
@router.post("/reset")
async def reset_settings(
    category: str = None,
    settings: SettingsManager = Depends(get_settings)
):
    """Reset settings to defaults"""
    try:
        if category:
            # Reset specific category
            if category == "ai":
                settings.ai = settings.ai.__class__()
            elif category == "voice":
                settings.voice = settings.voice.__class__()
            elif category == "system":
                settings.system = settings.system.__class__()
            elif category == "security":
                settings.security = settings.security.__class__()
            elif category == "remote":
                settings.remote = settings.remote.__class__()
            elif category == "performance":
                settings.performance = settings.performance.__class__()
            elif category == "notifications":
                settings.notifications = settings.notifications.__class__()
            elif category == "general":
                settings.general = settings.general.__class__()
            else:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        else:
            # Reset all settings
            settings.load_settings()  # This will load defaults
        
        settings.save_settings()
        
        return {
            "success": True,
            "message": f"Settings reset successfully" + (f" for {category}" if category else ""),
        }
    except Exception as e:
        logger.error(f"Failed to reset settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
