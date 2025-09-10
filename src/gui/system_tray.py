"""
JARVIS System Tray GUI
Sistem tepsisinde çalışan minimal arayüz
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import sys
import pystray
from PIL import Image, ImageDraw
import io

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.jarvis_core import get_jarvis_core
from features.settings import get_settings_manager

logger = logging.getLogger(__name__)

class JARVISSystemTray:
    """JARVIS System Tray Application"""
    
    def __init__(self):
        self.jarvis_core = None
        self.settings_manager = None
        self.tray_icon = None
        self.is_running = False
        self.main_window = None
        
    def create_icon_image(self) -> Image.Image:
        """Create system tray icon"""
        # Create a simple icon with JARVIS text
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='#1e3a8a')
        draw = ImageDraw.Draw(image)
        
        # Draw a simple robot face
        # Head
        draw.ellipse([10, 10, 54, 54], fill='#3b82f6', outline='#1e40af', width=2)
        
        # Eyes
        draw.ellipse([20, 20, 28, 28], fill='#ffffff')
        draw.ellipse([36, 20, 44, 28], fill='#ffffff')
        
        # Mouth
        draw.arc([20, 35, 44, 45], 0, 180, fill='#1e40af', width=3)
        
        return image
    
    def create_menu(self) -> pystray.Menu:
        """Create system tray menu"""
        return pystray.Menu(
            pystray.MenuItem("JARVIS Status", self.show_status, default=True),
            pystray.MenuItem("Settings", self.show_settings),
            pystray.MenuItem("Voice Commands", self.show_voice_commands),
            pystray.MenuItem("System Info", self.show_system_info),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start Listening", self.start_listening, enabled=lambda item: not self.is_running),
            pystray.MenuItem("Stop Listening", self.stop_listening, enabled=lambda item: self.is_running),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Restart", self.restart_jarvis),
            pystray.MenuItem("Exit", self.quit_application)
        )
    
    def show_status(self, icon=None, item=None):
        """Show JARVIS status window"""
        if self.main_window and self.main_window.winfo_exists():
            self.main_window.lift()
            self.main_window.focus()
            return
        
        self.main_window = tk.Toplevel()
        self.main_window.title("JARVIS Computer Assistant - Status")
        self.main_window.geometry("600x400")
        self.main_window.resizable(True, True)
        
        # Make window stay on top
        self.main_window.attributes('-topmost', True)
        self.main_window.after(100, lambda: self.main_window.attributes('-topmost', False))
        
        # Create main frame
        main_frame = ttk.Frame(self.main_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.main_window.columnconfigure(0, weight=1)
        self.main_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 JARVIS Computer Assistant", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Status labels
        status_labels = {
            "Status": "Running" if self.is_running else "Stopped",
            "Platform": "Windows" if self.jarvis_core else "Unknown",
            "Voice Recognition": "Active" if self.is_running else "Inactive",
            "AI Integration": "Active" if self.jarvis_core else "Inactive",
            "Remote Control": "Active" if self.jarvis_core else "Inactive",
            "WebSocket Port": "8765" if self.jarvis_core else "N/A"
        }
        
        row = 0
        for label, value in status_labels.items():
            ttk.Label(status_frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(
                row=row, column=0, sticky=tk.W, padx=(0, 10))
            ttk.Label(status_frame, text=value, font=('Arial', 10)).grid(
                row=row, column=1, sticky=tk.W)
            row += 1
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Recent Logs", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Log text area
        log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add some sample logs
        log_text.insert(tk.END, "2025-09-10 02:14:58 - JARVIS Computer Assistant is running!\n")
        log_text.insert(tk.END, "2025-09-10 02:14:58 - WebSocket server started on 0.0.0.0:8765\n")
        log_text.insert(tk.END, "2025-09-10 02:14:58 - Authentication token: caeed0c5-2e69-430b-9c20-9bc82637dfc0\n")
        log_text.insert(tk.END, "2025-09-10 02:14:58 - Press Ctrl+C to stop\n")
        log_text.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Start Listening", 
                  command=self.start_listening).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Stop Listening", 
                  command=self.stop_listening).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Settings", 
                  command=self.show_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", 
                  command=self.main_window.destroy).pack(side=tk.RIGHT)
    
    def show_settings(self, icon=None, item=None):
        """Show settings window"""
        try:
            from features.settings import show_settings
            show_settings()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def show_voice_commands(self, icon=None, item=None):
        """Show voice commands help"""
        commands = """
Available Voice Commands:

Basic Commands:
- "Hey JARVIS" - Wake up the assistant
- "What time is it?" - Get current time
- "Open Google" - Open web browser
- "Close current tab" - Close browser tab

System Commands:
- "Show running applications" - List running apps
- "Close Chrome" - Close specific application
- "Increase volume" - Adjust system volume
- "Set brightness to 50%" - Adjust screen brightness

Terminal Commands:
- "Run git status" - Execute git command
- "Install package numpy" - Install Python package
- "List files in current directory" - Show directory contents

Plugin Commands:
- "What's the weather?" - Get weather information
- "Show my calendar" - Display calendar events
- "Check my emails" - Check email inbox
- "Show system status" - Display system information
        """
        
        # Create help window
        help_window = tk.Toplevel()
        help_window.title("JARVIS Voice Commands")
        help_window.geometry("500x600")
        help_window.resizable(True, True)
        
        # Create text widget
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, commands)
        text_widget.config(state=tk.DISABLED)
        
        # Add close button
        ttk.Button(help_window, text="Close", 
                  command=help_window.destroy).pack(pady=10)
    
    def show_system_info(self, icon=None, item=None):
        """Show system information"""
        if not self.jarvis_core:
            messagebox.showwarning("Warning", "JARVIS is not running")
            return
        
        try:
            status = self.jarvis_core.get_status()
            
            info_window = tk.Toplevel()
            info_window.title("JARVIS System Information")
            info_window.geometry("400x300")
            info_window.resizable(True, True)
            
            # Create text widget
            text_widget = scrolledtext.ScrolledText(info_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Format status information
            info_text = f"""JARVIS System Information:

Status: {'Running' if status.get('is_running') else 'Stopped'}
Initialized: {'Yes' if status.get('is_initialized') else 'No'}
Listening: {'Yes' if status.get('is_listening') else 'No'}
Platform: {status.get('platform', 'Unknown')}

Services:
"""
            
            services = status.get('services', {})
            for service, active in services.items():
                status_text = "Active" if active else "Inactive"
                info_text += f"  {service}: {status_text}\n"
            
            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)
            
            # Add close button
            ttk.Button(info_window, text="Close", 
                      command=info_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get system info: {e}")
    
    def start_listening(self, icon=None, item=None):
        """Start voice listening"""
        if not self.jarvis_core:
            messagebox.showwarning("Warning", "JARVIS is not running")
            return
        
        try:
            # Start listening in a separate thread
            def start_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.jarvis_core.start_listening())
            
            thread = threading.Thread(target=start_async, daemon=True)
            thread.start()
            
            self.is_running = True
            messagebox.showinfo("Success", "Voice listening started")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start listening: {e}")
    
    def stop_listening(self, icon=None, item=None):
        """Stop voice listening"""
        if not self.jarvis_core:
            messagebox.showwarning("Warning", "JARVIS is not running")
            return
        
        try:
            # Stop listening in a separate thread
            def stop_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.jarvis_core.stop_listening())
            
            thread = threading.Thread(target=stop_async, daemon=True)
            thread.start()
            
            self.is_running = False
            messagebox.showinfo("Success", "Voice listening stopped")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop listening: {e}")
    
    def restart_jarvis(self, icon=None, item=None):
        """Restart JARVIS"""
        try:
            messagebox.showinfo("Info", "Restarting JARVIS...")
            # Implementation for restart would go here
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart JARVIS: {e}")
    
    def quit_application(self, icon=None, item=None):
        """Quit the application"""
        try:
            if self.jarvis_core:
                # Shutdown JARVIS in a separate thread
                def shutdown_async():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.jarvis_core.shutdown())
                
                thread = threading.Thread(target=shutdown_async, daemon=True)
                thread.start()
                thread.join(timeout=5)  # Wait max 5 seconds
            
            # Stop system tray
            if self.tray_icon:
                self.tray_icon.stop()
            
            # Exit application
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            sys.exit(1)
    
    def run(self):
        """Run the system tray application"""
        try:
            # Initialize JARVIS in main thread
            self.jarvis_core = get_jarvis_core()
            self.settings_manager = get_settings_manager()
            
            # Create system tray icon
            icon_image = self.create_icon_image()
            menu = self.create_menu()
            
            self.tray_icon = pystray.Icon(
                "JARVIS",
                icon_image,
                "JARVIS Computer Assistant",
                menu
            )
            
            # Start system tray in main thread
            self.tray_icon.run()
            
        except Exception as e:
            logger.error(f"Failed to run system tray: {e}")
            messagebox.showerror("Error", f"Failed to start JARVIS system tray: {e}")

def main():
    """Main entry point for system tray application"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run system tray
    app = JARVISSystemTray()
    app.run()

if __name__ == "__main__":
    main()
