#!/usr/bin/env python3
"""
Cross-platform setup script for JARVIS Computer Assistant
Detects platform and installs appropriate dependencies
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

class PlatformSetup:
    """Cross-platform setup manager"""
    
    def __init__(self):
        self.platform_name = platform.system().lower()
        self.python_version = sys.version_info
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config" / "platforms"
        
    def run(self):
        """Run platform-specific setup"""
        print(f"🤖 JARVIS Computer Assistant - Platform Setup")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print("-" * 50)
        
        # Load platform configuration
        config = self.load_platform_config()
        if not config:
            print("❌ Failed to load platform configuration")
            return False
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Install Python dependencies
        if not self.install_python_dependencies():
            return False
        
        # Install platform-specific dependencies
        if not self.install_platform_dependencies(config):
            return False
        
        # Verify installation
        if not self.verify_installation(config):
            return False
        
        print("✅ Setup completed successfully!")
        return True
    
    def load_platform_config(self) -> Optional[Dict]:
        """Load platform-specific configuration"""
        config_file = self.config_dir / f"{self.platform_name}.json"
        
        if not config_file.exists():
            print(f"❌ Platform configuration not found: {config_file}")
            return None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load platform config: {e}")
            return None
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        if self.python_version < (3, 11):
            print(f"❌ Python 3.11+ required, found {self.python_version.major}.{self.python_version.minor}")
            return False
        
        print(f"✅ Python version compatible: {self.python_version.major}.{self.python_version.minor}")
        return True
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        try:
            # Install core requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.project_root / "requirements.txt")
            ], check=True)
            
            # Install platform-specific requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.project_root / "requirements-platform.txt")
            ], check=True)
            
            print("✅ Python dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
    
    def install_platform_dependencies(self, config: Dict) -> bool:
        """Install platform-specific system dependencies"""
        if self.platform_name == "windows":
            return self.install_windows_dependencies(config)
        elif self.platform_name == "linux":
            return self.install_linux_dependencies(config)
        else:
            print(f"⚠️  Platform {self.platform_name} not fully supported")
            return True
    
    def install_windows_dependencies(self, config: Dict) -> bool:
        """Install Windows-specific dependencies"""
        print("🪟 Installing Windows dependencies...")
        
        # Check for Windows Speech Platform
        try:
            import win32com.client
            print("✅ Windows Speech Platform available")
        except ImportError:
            print("⚠️  Windows Speech Platform not available - using fallback")
        
        # Check for SAPI5
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            print(f"✅ SAPI5 TTS available with {len(voices)} voices")
        except Exception as e:
            print(f"⚠️  SAPI5 TTS not available: {e}")
        
        return True
    
    def install_linux_dependencies(self, config: Dict) -> bool:
        """Install Linux-specific dependencies"""
        print("🐧 Installing Linux dependencies...")
        
        system_packages = config.get("dependencies", {}).get("system_packages", [])
        if not system_packages:
            print("⚠️  No system packages to install")
            return True
        
        # Detect package manager
        package_manager = self.detect_package_manager()
        if not package_manager:
            print("❌ No supported package manager found")
            return False
        
        print(f"📦 Using package manager: {package_manager}")
        
        # Install system packages
        for package in system_packages:
            if not self.install_system_package(package, package_manager):
                print(f"⚠️  Failed to install {package}")
        
        # Verify installation
        return self.verify_linux_dependencies(config)
    
    def detect_package_manager(self) -> Optional[str]:
        """Detect available package manager"""
        package_managers = {
            "apt": ["apt", "apt-get"],
            "yum": ["yum"],
            "dnf": ["dnf"],
            "pacman": ["pacman"],
            "zypper": ["zypper"]
        }
        
        for manager, commands in package_managers.items():
            for cmd in commands:
                try:
                    subprocess.run([cmd, "--version"], 
                                 capture_output=True, check=True)
                    return manager
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        return None
    
    def install_system_package(self, package: str, manager: str) -> bool:
        """Install a system package"""
        try:
            if manager == "apt":
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "-y", package], check=True)
            elif manager == "yum":
                subprocess.run(["sudo", "yum", "install", "-y", package], check=True)
            elif manager == "dnf":
                subprocess.run(["sudo", "dnf", "install", "-y", package], check=True)
            elif manager == "pacman":
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", package], check=True)
            elif manager == "zypper":
                subprocess.run(["sudo", "zypper", "install", "-y", package], check=True)
            else:
                return False
            
            print(f"✅ Installed {package}")
            return True
            
        except subprocess.CalledProcessError:
            return False
    
    def verify_linux_dependencies(self, config: Dict) -> bool:
        """Verify Linux dependencies are installed"""
        features = config.get("features", {})
        
        # Check eSpeak
        if features.get("espeak", False):
            try:
                subprocess.run(["espeak", "--version"], 
                             capture_output=True, check=True)
                print("✅ eSpeak available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  eSpeak not available")
        
        # Check PulseAudio
        if features.get("pulseaudio", False):
            try:
                subprocess.run(["pulseaudio", "--version"], 
                             capture_output=True, check=True)
                print("✅ PulseAudio available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  PulseAudio not available")
        
        # Check xrandr
        if features.get("xrandr", False):
            try:
                subprocess.run(["xrandr", "--version"], 
                             capture_output=True, check=True)
                print("✅ xrandr available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  xrandr not available")
        
        return True
    
    def verify_installation(self, config: Dict) -> bool:
        """Verify the installation"""
        print("🔍 Verifying installation...")
        
        # Test core imports
        try:
            import PyQt6
            print("✅ PyQt6 available")
        except ImportError:
            print("❌ PyQt6 not available")
            return False
        
        # Test platform-specific features
        features = config.get("features", {})
        
        if self.platform_name == "windows":
            # Test Windows features
            if features.get("sapi5_tts", False):
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    print("✅ SAPI5 TTS available")
                except Exception as e:
                    print(f"⚠️  SAPI5 TTS not available: {e}")
        
        elif self.platform_name == "linux":
            # Test Linux features
            if features.get("espeak", False):
                try:
                    subprocess.run(["espeak", "--version"], 
                                 capture_output=True, check=True)
                    print("✅ eSpeak available")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("⚠️  eSpeak not available")
        
        return True

def main():
    """Main entry point"""
    setup = PlatformSetup()
    success = setup.run()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("You can now run JARVIS with: python src/main.py")
    else:
        print("\n❌ Setup failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
