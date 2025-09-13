"""
Terminal Integration Features for JARVIS Computer Assistant

This package provides cross-platform terminal integration including
command execution, package management, and script handling.
"""

from .terminal_manager import (
    TerminalManager,
    TerminalType,
    CommandType,
    CommandResult,
    TerminalSession,
    get_terminal_manager
)

from .package_manager import (
    PackageManager,
    PackageManagerType,
    PackageInfo,
    PackageManagerInfo,
    get_package_manager
)

__all__ = [
    # Terminal Manager
    "TerminalManager",
    "TerminalType",
    "CommandType",
    "CommandResult",
    "TerminalSession",
    "get_terminal_manager",
    
    # Package Manager
    "PackageManager",
    "PackageManagerType",
    "PackageInfo",
    "PackageManagerInfo",
    "get_package_manager"
]

__version__ = "1.0.0"
