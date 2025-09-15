"""
WebSocket Configuration Manager

Centralized configuration management for WebSocket connections
between Flutter client and Python server.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class WebSocketConfig:
    """WebSocket configuration data class"""
    host: str
    port: int
    use_ssl: bool
    ping_interval: int
    ping_timeout: int
    reconnect_attempts: int
    reconnect_delay: int
    connection_timeout: int
    authentication_enabled: bool
    token_expiry: int
    logging_enabled: bool
    log_level: str
    log_requests: bool
    log_responses: bool
    
    @property
    def url(self) -> str:
        """Get WebSocket URL"""
        protocol = "wss" if self.use_ssl else "ws"
        return f"{protocol}://{self.host}:{self.port}"
    
    @property
    def server_bind_address(self) -> tuple:
        """Get server bind address"""
        return (self.host, self.port)

class WebSocketConfigManager:
    """WebSocket configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config: Optional[WebSocketConfig] = None
        self.logger = logging.getLogger(__name__)
    
    def _get_default_config_path(self) -> str:
        """Get default config file path"""
        # Look for config in project root
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / "config" / "websocket_config.json"
        
        if config_file.exists():
            return str(config_file)
        
        # Fallback to current directory
        return "websocket_config.json"
    
    def load_config(self) -> WebSocketConfig:
        """Load WebSocket configuration"""
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return self._get_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            websocket_config = config_data.get('websocket', {})
            auth_config = config_data.get('authentication', {})
            logging_config = config_data.get('logging', {})
            
            config = WebSocketConfig(
                host=websocket_config.get('host', '0.0.0.0'),
                port=websocket_config.get('port', 8765),
                use_ssl=websocket_config.get('use_ssl', False),
                ping_interval=websocket_config.get('ping_interval', 30),
                ping_timeout=websocket_config.get('ping_timeout', 10),
                reconnect_attempts=websocket_config.get('reconnect_attempts', 5),
                reconnect_delay=websocket_config.get('reconnect_delay', 2000),
                connection_timeout=websocket_config.get('connection_timeout', 30),
                authentication_enabled=auth_config.get('enabled', True),
                token_expiry=auth_config.get('token_expiry', 3600),
                logging_enabled=logging_config.get('enabled', True),
                log_level=logging_config.get('log_level', 'INFO'),
                log_requests=logging_config.get('log_requests', True),
                log_responses=logging_config.get('log_responses', True)
            )
            
            self._config = config
            self.logger.info(f"WebSocket config loaded from {self.config_path}")
            self.logger.info(f"Server will bind to {config.server_bind_address}")
            self.logger.info(f"Client URL: {config.url}")
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load WebSocket config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> WebSocketConfig:
        """Get default configuration"""
        return WebSocketConfig(
            host='0.0.0.0',
            port=8765,
            use_ssl=False,
            ping_interval=60,  # 30'dan 60'a çıkarıldı
            ping_timeout=10,
            reconnect_attempts=5,
            reconnect_delay=2000,
            connection_timeout=30,
            authentication_enabled=True,
            token_expiry=3600,
            logging_enabled=True,
            log_level='INFO',
            log_requests=True,
            log_responses=True
        )
    
    def get_config(self) -> WebSocketConfig:
        """Get current configuration"""
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def save_config(self, config: WebSocketConfig) -> bool:
        """Save configuration to file"""
        try:
            config_data = {
                'websocket': {
                    'host': config.host,
                    'port': config.port,
                    'use_ssl': config.use_ssl,
                    'ping_interval': config.ping_interval,
                    'ping_timeout': config.ping_timeout,
                    'reconnect_attempts': config.reconnect_attempts,
                    'reconnect_delay': config.reconnect_delay,
                    'connection_timeout': config.connection_timeout
                },
                'authentication': {
                    'enabled': config.authentication_enabled,
                    'token_expiry': config.token_expiry
                },
                'logging': {
                    'enabled': config.logging_enabled,
                    'log_level': config.log_level,
                    'log_requests': config.log_requests,
                    'log_responses': config.log_responses
                }
            }
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"WebSocket config saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save WebSocket config: {e}")
            return False

# Global instance
_config_manager: Optional[WebSocketConfigManager] = None

def get_websocket_config_manager() -> WebSocketConfigManager:
    """Get global WebSocket config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = WebSocketConfigManager()
    return _config_manager

def get_websocket_config() -> WebSocketConfig:
    """Get current WebSocket configuration"""
    return get_websocket_config_manager().get_config()
