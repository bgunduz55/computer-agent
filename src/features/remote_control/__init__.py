"""
Remote Control Features for JARVIS Computer Assistant

This package provides remote control capabilities including WebSocket server,
remote controller, and client management for mobile and web applications.
"""

from .websocket_server import (
    WebSocketServer,
    WebSocketMessage,
    MessageType,
    ClientInfo,
    get_websocket_server
)

from .remote_controller import (
    RemoteController,
    RemoteAction,
    RemoteResponse,
    get_remote_controller
)

__all__ = [
    # WebSocket Server
    "WebSocketServer",
    "WebSocketMessage",
    "MessageType",
    "ClientInfo",
    "get_websocket_server",
    
    # Remote Controller
    "RemoteController",
    "RemoteAction",
    "RemoteResponse",
    "get_remote_controller"
]

__version__ = "1.0.0"
