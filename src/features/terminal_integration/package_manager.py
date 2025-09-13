"""
Package Manager Integration for JARVIS Computer Assistant

This module provides cross-platform package manager integration including
pip, npm, chocolatey, winget, apt, yum, and other package managers.
"""

import asyncio
import logging
import subprocess
import json
import platform
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .terminal_manager import TerminalManager, CommandResult, get_terminal_manager

logger = logging.getLogger(__name__)

class PackageManagerType(Enum):
    """Supported package managers"""
    PIP = "pip"
    NPM = "npm"
    YARN = "yarn"
    CHOCOLATEY = "choco"
    WINGET = "winget"
    APT = "apt"
    YUM = "yum"
    DNF = "dnf"
    PACMAN = "pacman"
    BREW = "brew"
    CARGO = "cargo"
    GO = "go"
    COMPOSER = "composer"
    GEM = "gem"
    CONDA = "conda"

@dataclass
class PackageInfo:
    """Package information"""
    name: str
    version: str
    description: str
    installed: bool
    latest_version: Optional[str] = None
    size: Optional[str] = None
    dependencies: List[str] = None

@dataclass
class PackageManagerInfo:
    """Package manager information"""
    manager_type: PackageManagerType
    available: bool
    version: Optional[str] = None
    path: Optional[str] = None

class PackageManager:
    """Cross-platform package manager integration"""
    
    def __init__(self):
        self.terminal_manager = get_terminal_manager()
        self.logger = logging.getLogger(__name__)
        
        # Platform-specific package manager configurations
        self.manager_configs = self._load_manager_configs()
        
        # Available package managers (will be initialized asynchronously)
        self.available_managers = []
    
    async def initialize(self) -> bool:
        """Initialize package manager"""
        try:
            # Detect available package managers
            self.available_managers = await self._detect_available_managers()
            self.logger.info(f"Package manager initialized with {len(self.available_managers)} available managers")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize package manager: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup package manager"""
        try:
            self.available_managers.clear()
            self.logger.info("Package manager cleaned up")
        except Exception as e:
            self.logger.error(f"Failed to cleanup package manager: {e}")
    
    def _load_manager_configs(self) -> Dict[PackageManagerType, Dict[str, Any]]:
        """Load package manager configurations"""
        return {
            PackageManagerType.PIP: {
                "install_command": "pip install",
                "uninstall_command": "pip uninstall",
                "list_command": "pip list",
                "search_command": "pip search",
                "update_command": "pip install --upgrade",
                "show_command": "pip show",
                "available": True
            },
            PackageManagerType.NPM: {
                "install_command": "npm install",
                "uninstall_command": "npm uninstall",
                "list_command": "npm list",
                "search_command": "npm search",
                "update_command": "npm update",
                "show_command": "npm info",
                "available": True
            },
            PackageManagerType.YARN: {
                "install_command": "yarn add",
                "uninstall_command": "yarn remove",
                "list_command": "yarn list",
                "search_command": "yarn search",
                "update_command": "yarn upgrade",
                "show_command": "yarn info",
                "available": True
            },
            PackageManagerType.CHOCOLATEY: {
                "install_command": "choco install",
                "uninstall_command": "choco uninstall",
                "list_command": "choco list",
                "search_command": "choco search",
                "update_command": "choco upgrade",
                "show_command": "choco info",
                "available": platform.system() == "Windows"
            },
            PackageManagerType.WINGET: {
                "install_command": "winget install",
                "uninstall_command": "winget uninstall",
                "list_command": "winget list",
                "search_command": "winget search",
                "update_command": "winget upgrade",
                "show_command": "winget show",
                "available": platform.system() == "Windows"
            },
            PackageManagerType.APT: {
                "install_command": "sudo apt install",
                "uninstall_command": "sudo apt remove",
                "list_command": "apt list --installed",
                "search_command": "apt search",
                "update_command": "sudo apt update && sudo apt upgrade",
                "show_command": "apt show",
                "available": platform.system() == "Linux"
            },
            PackageManagerType.YUM: {
                "install_command": "sudo yum install",
                "uninstall_command": "sudo yum remove",
                "list_command": "yum list installed",
                "search_command": "yum search",
                "update_command": "sudo yum update",
                "show_command": "yum info",
                "available": platform.system() == "Linux"
            },
            PackageManagerType.DNF: {
                "install_command": "sudo dnf install",
                "uninstall_command": "sudo dnf remove",
                "list_command": "dnf list installed",
                "search_command": "dnf search",
                "update_command": "sudo dnf update",
                "show_command": "dnf info",
                "available": platform.system() == "Linux"
            },
            PackageManagerType.PACMAN: {
                "install_command": "sudo pacman -S",
                "uninstall_command": "sudo pacman -R",
                "list_command": "pacman -Q",
                "search_command": "pacman -Ss",
                "update_command": "sudo pacman -Syu",
                "show_command": "pacman -Si",
                "available": platform.system() == "Linux"
            },
            PackageManagerType.BREW: {
                "install_command": "brew install",
                "uninstall_command": "brew uninstall",
                "list_command": "brew list",
                "search_command": "brew search",
                "update_command": "brew upgrade",
                "show_command": "brew info",
                "available": platform.system() in ["Darwin", "Linux"]
            },
            PackageManagerType.CARGO: {
                "install_command": "cargo install",
                "uninstall_command": "cargo uninstall",
                "list_command": "cargo install --list",
                "search_command": "cargo search",
                "update_command": "cargo install --force",
                "show_command": "cargo show",
                "available": True
            },
            PackageManagerType.GO: {
                "install_command": "go install",
                "uninstall_command": "go clean -i",
                "list_command": "go list -m all",
                "search_command": "go search",
                "update_command": "go get -u",
                "show_command": "go list -m",
                "available": True
            },
            PackageManagerType.COMPOSER: {
                "install_command": "composer require",
                "uninstall_command": "composer remove",
                "list_command": "composer show",
                "search_command": "composer search",
                "update_command": "composer update",
                "show_command": "composer show",
                "available": True
            },
            PackageManagerType.GEM: {
                "install_command": "gem install",
                "uninstall_command": "gem uninstall",
                "list_command": "gem list",
                "search_command": "gem search",
                "update_command": "gem update",
                "show_command": "gem info",
                "available": True
            },
            PackageManagerType.CONDA: {
                "install_command": "conda install",
                "uninstall_command": "conda remove",
                "list_command": "conda list",
                "search_command": "conda search",
                "update_command": "conda update",
                "show_command": "conda info",
                "available": True
            }
        }
    
    async def _detect_available_managers(self) -> List[PackageManagerInfo]:
        """Detect available package managers on the system"""
        available = []
        
        for manager_type, config in self.manager_configs.items():
            if not config.get("available", False):
                continue
            
            # Check if manager is available
            is_available = await self._check_manager_availability(manager_type)
            version = None
            path = None
            
            if is_available:
                version, path = await self._get_manager_info(manager_type)
            
            available.append(PackageManagerInfo(
                manager_type=manager_type,
                available=is_available,
                version=version,
                path=path
            ))
        
        return available
    
    async def _check_manager_availability(self, manager_type: PackageManagerType) -> bool:
        """Check if a package manager is available"""
        try:
            if manager_type == PackageManagerType.PIP:
                result = await self.terminal_manager.execute_command("pip --version")
                return result.success
            elif manager_type == PackageManagerType.NPM:
                result = await self.terminal_manager.execute_command("npm --version")
                return result.success
            elif manager_type == PackageManagerType.YARN:
                result = await self.terminal_manager.execute_command("yarn --version")
                return result.success
            elif manager_type == PackageManagerType.CHOCOLATEY:
                result = await self.terminal_manager.execute_command("choco --version")
                return result.success
            elif manager_type == PackageManagerType.WINGET:
                result = await self.terminal_manager.execute_command("winget --version")
                return result.success
            elif manager_type == PackageManagerType.APT:
                result = await self.terminal_manager.execute_command("apt --version")
                return result.success
            elif manager_type == PackageManagerType.YUM:
                result = await self.terminal_manager.execute_command("yum --version")
                return result.success
            elif manager_type == PackageManagerType.DNF:
                result = await self.terminal_manager.execute_command("dnf --version")
                return result.success
            elif manager_type == PackageManagerType.PACMAN:
                result = await self.terminal_manager.execute_command("pacman --version")
                return result.success
            elif manager_type == PackageManagerType.BREW:
                result = await self.terminal_manager.execute_command("brew --version")
                return result.success
            elif manager_type == PackageManagerType.CARGO:
                result = await self.terminal_manager.execute_command("cargo --version")
                return result.success
            elif manager_type == PackageManagerType.GO:
                result = await self.terminal_manager.execute_command("go version")
                return result.success
            elif manager_type == PackageManagerType.COMPOSER:
                result = await self.terminal_manager.execute_command("composer --version")
                return result.success
            elif manager_type == PackageManagerType.GEM:
                result = await self.terminal_manager.execute_command("gem --version")
                return result.success
            elif manager_type == PackageManagerType.CONDA:
                result = await self.terminal_manager.execute_command("conda --version")
                return result.success
            
            return False
        except Exception as e:
            self.logger.debug(f"Package manager {manager_type.value} not available: {e}")
            return False
    
    async def _get_manager_info(self, manager_type: PackageManagerType) -> Tuple[Optional[str], Optional[str]]:
        """Get package manager version and path"""
        try:
            if manager_type == PackageManagerType.PIP:
                result = await self.terminal_manager.execute_command("pip --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            elif manager_type == PackageManagerType.NPM:
                result = await self.terminal_manager.execute_command("npm --version")
                if result.success:
                    return result.output.strip(), None
            elif manager_type == PackageManagerType.YARN:
                result = await self.terminal_manager.execute_command("yarn --version")
                if result.success:
                    return result.output.strip(), None
            elif manager_type == PackageManagerType.CHOCOLATEY:
                result = await self.terminal_manager.execute_command("choco --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            elif manager_type == PackageManagerType.WINGET:
                result = await self.terminal_manager.execute_command("winget --version")
                if result.success:
                    return result.output.strip(), None
            elif manager_type == PackageManagerType.APT:
                result = await self.terminal_manager.execute_command("apt --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            elif manager_type == PackageManagerType.YUM:
                result = await self.terminal_manager.execute_command("yum --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            elif manager_type == PackageManagerType.DNF:
                result = await self.terminal_manager.execute_command("dnf --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            elif manager_type == PackageManagerType.PACMAN:
                result = await self.terminal_manager.execute_command("pacman --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            elif manager_type == PackageManagerType.BREW:
                result = await self.terminal_manager.execute_command("brew --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            elif manager_type == PackageManagerType.CARGO:
                result = await self.terminal_manager.execute_command("cargo --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            elif manager_type == PackageManagerType.GO:
                result = await self.terminal_manager.execute_command("go version")
                if result.success:
                    version = result.output.split()[2] if len(result.output.split()) > 2 else None
                    return version, None
            elif manager_type == PackageManagerType.COMPOSER:
                result = await self.terminal_manager.execute_command("composer --version")
                if result.success:
                    version = result.output.split()[2] if len(result.output.split()) > 2 else None
                    return version, None
            elif manager_type == PackageManagerType.GEM:
                result = await self.terminal_manager.execute_command("gem --version")
                if result.success:
                    return result.output.strip(), None
            elif manager_type == PackageManagerType.CONDA:
                result = await self.terminal_manager.execute_command("conda --version")
                if result.success:
                    version = result.output.split()[1] if len(result.output.split()) > 1 else None
                    return version, None
            
            return None, None
        except Exception as e:
            self.logger.debug(f"Failed to get info for {manager_type.value}: {e}")
            return None, None
    
    async def install_package(self, package_name: str, manager_type: Optional[PackageManagerType] = None,
                            version: Optional[str] = None, global_install: bool = False) -> CommandResult:
        """Install a package using specified package manager"""
        try:
            # Auto-detect package manager if not specified
            if manager_type is None:
                manager_type = self._detect_package_manager(package_name)
            
            if not self._is_manager_available(manager_type):
                raise ValueError(f"Package manager {manager_type.value} is not available")
            
            config = self.manager_configs[manager_type]
            install_command = config["install_command"]
            
            # Add global flag if needed
            if global_install and manager_type in [PackageManagerType.NPM, PackageManagerType.YARN]:
                install_command += " -g"
            
            # Add version if specified
            if version:
                package_name = f"{package_name}=={version}"
            
            command = f"{install_command} {package_name}"
            
            result = await self.terminal_manager.execute_command(command)
            
            if result.success:
                self.logger.info(f"Successfully installed {package_name} using {manager_type.value}")
            else:
                self.logger.error(f"Failed to install {package_name} using {manager_type.value}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to install package {package_name}: {e}")
            return CommandResult(
                command=f"install {package_name}",
                output="",
                error=str(e),
                exit_code=-1,
                execution_time=0,
                success=False
            )
    
    async def uninstall_package(self, package_name: str, manager_type: Optional[PackageManagerType] = None) -> CommandResult:
        """Uninstall a package using specified package manager"""
        try:
            if manager_type is None:
                manager_type = self._detect_package_manager(package_name)
            
            if not self._is_manager_available(manager_type):
                raise ValueError(f"Package manager {manager_type.value} is not available")
            
            config = self.manager_configs[manager_type]
            uninstall_command = config["uninstall_command"]
            
            command = f"{uninstall_command} {package_name}"
            
            result = await self.terminal_manager.execute_command(command)
            
            if result.success:
                self.logger.info(f"Successfully uninstalled {package_name} using {manager_type.value}")
            else:
                self.logger.error(f"Failed to uninstall {package_name} using {manager_type.value}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to uninstall package {package_name}: {e}")
            return CommandResult(
                command=f"uninstall {package_name}",
                output="",
                error=str(e),
                exit_code=-1,
                execution_time=0,
                success=False
            )
    
    async def list_packages(self, manager_type: Optional[PackageManagerType] = None) -> List[PackageInfo]:
        """List installed packages"""
        try:
            if manager_type is None:
                # List packages from all available managers
                all_packages = []
                for manager in self.available_managers:
                    if manager.available:
                        packages = await self._list_packages_for_manager(manager.manager_type)
                        all_packages.extend(packages)
                return all_packages
            else:
                return await self._list_packages_for_manager(manager_type)
        
        except Exception as e:
            self.logger.error(f"Failed to list packages: {e}")
            return []
    
    async def _list_packages_for_manager(self, manager_type: PackageManagerType) -> List[PackageInfo]:
        """List packages for a specific manager"""
        try:
            if not self._is_manager_available(manager_type):
                return []
            
            config = self.manager_configs[manager_type]
            list_command = config["list_command"]
            
            result = await self.terminal_manager.execute_command(list_command)
            
            if not result.success:
                return []
            
            # Parse output based on manager type
            packages = self._parse_package_list(result.output, manager_type)
            return packages
        
        except Exception as e:
            self.logger.error(f"Failed to list packages for {manager_type.value}: {e}")
            return []
    
    def _parse_package_list(self, output: str, manager_type: PackageManagerType) -> List[PackageInfo]:
        """Parse package list output"""
        packages = []
        
        try:
            lines = output.strip().split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                
                # Parse based on manager type
                if manager_type == PackageManagerType.PIP:
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        version = parts[1]
                        packages.append(PackageInfo(
                            name=name,
                            version=version,
                            description="",
                            installed=True
                        ))
                elif manager_type == PackageManagerType.NPM:
                    if not line.startswith('├──') and not line.startswith('└──') and not line.startswith('npm'):
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1]
                            packages.append(PackageInfo(
                                name=name,
                                version=version,
                                description="",
                                installed=True
                            ))
                # Add more parsers for other managers as needed
            
            return packages
        
        except Exception as e:
            self.logger.error(f"Failed to parse package list for {manager_type.value}: {e}")
            return []
    
    def _detect_package_manager(self, package_name: str) -> PackageManagerType:
        """Detect appropriate package manager for a package"""
        # Simple heuristic - can be improved with more sophisticated detection
        if package_name.startswith('@'):
            return PackageManagerType.NPM
        elif package_name.endswith('.py'):
            return PackageManagerType.PIP
        elif package_name.endswith('.rs'):
            return PackageManagerType.CARGO
        elif package_name.endswith('.go'):
            return PackageManagerType.GO
        elif package_name.endswith('.php'):
            return PackageManagerType.COMPOSER
        elif package_name.endswith('.rb'):
            return PackageManagerType.GEM
        else:
            # Default to pip for Python packages
            return PackageManagerType.PIP
    
    def _is_manager_available(self, manager_type: PackageManagerType) -> bool:
        """Check if a package manager is available"""
        for manager in self.available_managers:
            if manager.manager_type == manager_type:
                return manager.available
        return False
    
    async def get_available_managers(self) -> List[PackageManagerInfo]:
        """Get list of available package managers"""
        if not self.available_managers:
            self.available_managers = await self._detect_available_managers()
        return self.available_managers
    
    def get_manager_info(self, manager_type: PackageManagerType) -> Optional[PackageManagerInfo]:
        """Get information about a specific package manager"""
        for manager in self.available_managers:
            if manager.manager_type == manager_type:
                return manager
        return None

# Global package manager instance
_package_manager: Optional[PackageManager] = None

def get_package_manager() -> PackageManager:
    """Get global package manager instance"""
    global _package_manager
    if _package_manager is None:
        _package_manager = PackageManager()
    return _package_manager
