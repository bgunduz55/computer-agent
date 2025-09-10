"""
JARVIS Terminal Integration GUI
Terminal yönetim ve komut çalıştırma arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import asyncio
import logging
from typing import Dict, List, Optional
import subprocess
import os
import platform
from pathlib import Path

logger = logging.getLogger(__name__)

class TerminalIntegrationWindow:
    """Terminal entegrasyon penceresi"""
    
    def __init__(self, parent, jarvis_core=None):
        self.parent = parent
        self.jarvis_core = jarvis_core
        self.window = None
        self.current_shell = "powershell" if platform.system() == "Windows" else "bash"
        self.shells = ["powershell", "cmd", "bash", "zsh", "fish"] if platform.system() == "Windows" else ["bash", "zsh", "fish"]
        self.command_history = []
        self.history_index = -1
        self.current_directory = os.getcwd()
        
    def show(self):
        """Pencereyi göster"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("💻 Terminal Integration")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Ana frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="💻 Terminal Integration", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Terminal kontrolleri
        self.create_terminal_controls(main_frame)
        
        # Terminal çıktısı
        self.create_terminal_output(main_frame)
        
        # Hızlı komutlar
        self.create_quick_commands(main_frame)
        
        # Package manager
        self.create_package_manager(main_frame)
        
    def create_terminal_controls(self, parent):
        """Terminal kontrollerini oluştur"""
        controls_frame = ttk.LabelFrame(parent, text="Terminal Controls", padding="10")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sol taraf - Shell seçimi
        left_frame = ttk.Frame(controls_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(left_frame, text="Shell:").pack(side=tk.LEFT)
        self.shell_var = tk.StringVar(value=self.current_shell)
        shell_combo = ttk.Combobox(left_frame, textvariable=self.shell_var,
                                  values=self.shells, state="readonly", width=15)
        shell_combo.pack(side=tk.LEFT, padx=(10, 20))
        shell_combo.bind('<<ComboboxSelected>>', self.on_shell_change)
        
        # Working directory
        ttk.Label(left_frame, text="Directory:").pack(side=tk.LEFT)
        self.dir_var = tk.StringVar(value=self.current_directory)
        dir_entry = ttk.Entry(left_frame, textvariable=self.dir_var, width=40)
        dir_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        dir_entry.bind('<Return>', self.change_directory)
        
        # Sağ taraf - Butonlar
        right_frame = ttk.Frame(controls_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Button(right_frame, text="📁 Browse", command=self.browse_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="🔄 Refresh", command=self.refresh_terminal).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="🗑️ Clear", command=self.clear_terminal).pack(side=tk.LEFT)
        
    def create_terminal_output(self, parent):
        """Terminal çıktısını oluştur"""
        terminal_frame = ttk.LabelFrame(parent, text="Terminal Output", padding="10")
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Terminal çıktısı
        self.terminal_output = scrolledtext.ScrolledText(terminal_frame, height=20, width=100, 
                                                        font=('Consolas', 10))
        self.terminal_output.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Komut girişi
        input_frame = ttk.Frame(terminal_frame)
        input_frame.pack(fill=tk.X)
        
        # Prompt
        self.prompt_label = ttk.Label(input_frame, text=f"{self.current_shell}> ", 
                                     font=('Consolas', 10, 'bold'))
        self.prompt_label.pack(side=tk.LEFT)
        
        # Komut girişi
        self.command_input = ttk.Entry(input_frame, font=('Consolas', 10))
        self.command_input.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        self.command_input.bind('<Return>', self.execute_command)
        self.command_input.bind('<Up>', self.history_up)
        self.command_input.bind('<Down>', self.history_down)
        
        # Execute butonu
        ttk.Button(input_frame, text="Execute", command=self.execute_command).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Terminal çıktısını başlat
        self.initialize_terminal()
        
    def create_quick_commands(self, parent):
        """Hızlı komutları oluştur"""
        quick_frame = ttk.LabelFrame(parent, text="Quick Commands", padding="10")
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Git komutları
        git_frame = ttk.Frame(quick_frame)
        git_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(git_frame, text="Git:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Button(git_frame, text="Status", command=lambda: self.execute_quick_command("git status")).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(git_frame, text="Log", command=lambda: self.execute_quick_command("git log --oneline -5")).pack(side=tk.LEFT, padx=5)
        ttk.Button(git_frame, text="Pull", command=lambda: self.execute_quick_command("git pull")).pack(side=tk.LEFT, padx=5)
        ttk.Button(git_frame, text="Push", command=lambda: self.execute_quick_command("git push")).pack(side=tk.LEFT, padx=5)
        
        # Sistem komutları
        sys_frame = ttk.Frame(quick_frame)
        sys_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(sys_frame, text="System:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Button(sys_frame, text="List Files", command=lambda: self.execute_quick_command("dir" if platform.system() == "Windows" else "ls -la")).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(sys_frame, text="Process List", command=lambda: self.execute_quick_command("tasklist" if platform.system() == "Windows" else "ps aux")).pack(side=tk.LEFT, padx=5)
        ttk.Button(sys_frame, text="Disk Usage", command=lambda: self.execute_quick_command("dir" if platform.system() == "Windows" else "df -h")).pack(side=tk.LEFT, padx=5)
        ttk.Button(sys_frame, text="Network", command=lambda: self.execute_quick_command("ipconfig" if platform.system() == "Windows" else "ifconfig")).pack(side=tk.LEFT, padx=5)
        
        # Python komutları
        py_frame = ttk.Frame(quick_frame)
        py_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(py_frame, text="Python:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Button(py_frame, text="Version", command=lambda: self.execute_quick_command("python --version")).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(py_frame, text="Pip List", command=lambda: self.execute_quick_command("pip list")).pack(side=tk.LEFT, padx=5)
        ttk.Button(py_frame, text="Pip Update", command=lambda: self.execute_quick_command("pip list --outdated")).pack(side=tk.LEFT, padx=5)
        ttk.Button(py_frame, text="Pip Install", command=self.show_pip_install).pack(side=tk.LEFT, padx=5)
        
    def create_package_manager(self, parent):
        """Package manager oluştur"""
        package_frame = ttk.LabelFrame(parent, text="Package Manager", padding="10")
        package_frame.pack(fill=tk.X)
        
        # Package manager seçimi
        manager_frame = ttk.Frame(package_frame)
        manager_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(manager_frame, text="Manager:").pack(side=tk.LEFT)
        self.manager_var = tk.StringVar(value="pip")
        manager_combo = ttk.Combobox(manager_frame, textvariable=self.manager_var,
                                    values=["pip", "npm", "yarn", "choco", "winget", "apt", "yum", "dnf", "pacman", "brew", "cargo", "go", "composer", "gem", "conda"],
                                    state="readonly", width=15)
        manager_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Package işlemleri
        package_ops_frame = ttk.Frame(package_frame)
        package_ops_frame.pack(fill=tk.X)
        
        ttk.Label(package_ops_frame, text="Package:").pack(side=tk.LEFT)
        self.package_input = ttk.Entry(package_ops_frame, width=30)
        self.package_input.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.package_input.bind('<Return>', self.install_package)
        
        ttk.Button(package_ops_frame, text="Install", command=self.install_package).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(package_ops_frame, text="Uninstall", command=self.uninstall_package).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(package_ops_frame, text="List", command=self.list_packages).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(package_ops_frame, text="Update", command=self.update_packages).pack(side=tk.LEFT)
        
    def on_shell_change(self, event=None):
        """Shell değiştiğinde"""
        self.current_shell = self.shell_var.get()
        self.prompt_label.config(text=f"{self.current_shell}> ")
        self.terminal_output.insert(tk.END, f"Switched to {self.current_shell}\n")
        self.terminal_output.see(tk.END)
        
    def change_directory(self, event=None):
        """Dizin değiştir"""
        new_dir = self.dir_var.get()
        try:
            os.chdir(new_dir)
            self.current_directory = os.getcwd()
            self.dir_var.set(self.current_directory)
            self.terminal_output.insert(tk.END, f"Changed directory to: {self.current_directory}\n")
            self.terminal_output.see(tk.END)
        except Exception as e:
            self.terminal_output.insert(tk.END, f"Error changing directory: {e}\n")
            self.terminal_output.see(tk.END)
            
    def browse_directory(self):
        """Dizin seç"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(initialdir=self.current_directory)
        if directory:
            self.dir_var.set(directory)
            self.change_directory()
            
    def refresh_terminal(self):
        """Terminal'i yenile"""
        self.terminal_output.insert(tk.END, f"Terminal refreshed - {self.current_shell} in {self.current_directory}\n")
        self.terminal_output.see(tk.END)
        
    def clear_terminal(self):
        """Terminal'i temizle"""
        self.terminal_output.delete(1.0, tk.END)
        
    def initialize_terminal(self):
        """Terminal'i başlat"""
        self.terminal_output.insert(tk.END, f"JARVIS Terminal Integration\n")
        self.terminal_output.insert(tk.END, f"Shell: {self.current_shell}\n")
        self.terminal_output.insert(tk.END, f"Directory: {self.current_directory}\n")
        self.terminal_output.insert(tk.END, f"Type commands and press Enter to execute\n")
        self.terminal_output.insert(tk.END, f"Use Up/Down arrows for command history\n\n")
        self.terminal_output.see(tk.END)
        
    def execute_command(self, event=None):
        """Komut çalıştır"""
        command = self.command_input.get().strip()
        if not command:
            return
            
        # Komut geçmişine ekle
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Terminal'e komutu yazdır
        self.terminal_output.insert(tk.END, f"{self.current_shell}> {command}\n")
        self.terminal_output.see(tk.END)
        
        # Komutu temizle
        self.command_input.delete(0, tk.END)
        
        # Komutu çalıştır
        def run_command():
            try:
                if self.jarvis_core and hasattr(self.jarvis_core, 'terminal_manager'):
                    # JARVIS terminal manager kullan
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(
                            self.jarvis_core.terminal_manager.execute_command(command)
                        )
                        self.window.after(0, lambda: self._show_command_result(result))
                    finally:
                        loop.close()
                else:
                    # Doğrudan subprocess kullan
                    result = self._execute_direct_command(command)
                    self.window.after(0, lambda: self._show_command_result(result))
            except Exception as e:
                self.window.after(0, lambda: self._show_command_error(str(e)))
        
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
        
    def _execute_direct_command(self, command: str) -> Dict:
        """Komutu doğrudan çalıştır"""
        try:
            # Shell'e göre komutu ayarla
            if self.current_shell == "powershell":
                cmd = ["powershell", "-Command", command]
            elif self.current_shell == "cmd":
                cmd = ["cmd", "/c", command]
            else:
                cmd = [self.current_shell, "-c", command]
            
            # Komutu çalıştır
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  cwd=self.current_directory, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Command timed out after 30 seconds",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "return_code": -1
            }
    
    def _show_command_result(self, result: Dict):
        """Komut sonucunu göster"""
        if result["success"]:
            if result["output"]:
                self.terminal_output.insert(tk.END, result["output"])
            if result["error"]:
                self.terminal_output.insert(tk.END, f"Warning: {result['error']}")
        else:
            self.terminal_output.insert(tk.END, f"Error: {result['error']}")
            if result["output"]:
                self.terminal_output.insert(tk.END, f"Output: {result['output']}")
        
        self.terminal_output.insert(tk.END, f"\n[Return code: {result['return_code']}]\n\n")
        self.terminal_output.see(tk.END)
    
    def _show_command_error(self, error: str):
        """Komut hatasını göster"""
        self.terminal_output.insert(tk.END, f"Error: {error}\n\n")
        self.terminal_output.see(tk.END)
    
    def history_up(self, event=None):
        """Geçmişte yukarı git"""
        if self.history_index > 0:
            self.history_index -= 1
            self.command_input.delete(0, tk.END)
            self.command_input.insert(0, self.command_history[self.history_index])
        return "break"
    
    def history_down(self, event=None):
        """Geçmişte aşağı git"""
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_input.delete(0, tk.END)
            self.command_input.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)
            self.command_input.delete(0, tk.END)
        return "break"
    
    def execute_quick_command(self, command: str):
        """Hızlı komut çalıştır"""
        self.command_input.delete(0, tk.END)
        self.command_input.insert(0, command)
        self.execute_command()
    
    def show_pip_install(self):
        """Pip install dialog göster"""
        package = tk.simpledialog.askstring("Install Package", "Enter package name:")
        if package:
            self.execute_quick_command(f"pip install {package}")
    
    def install_package(self, event=None):
        """Paket yükle"""
        package = self.package_input.get().strip()
        if not package:
            return
        
        manager = self.manager_var.get()
        command = self._get_install_command(manager, package)
        if command:
            self.execute_quick_command(command)
            self.package_input.delete(0, tk.END)
    
    def uninstall_package(self):
        """Paket kaldır"""
        package = self.package_input.get().strip()
        if not package:
            return
        
        manager = self.manager_var.get()
        command = self._get_uninstall_command(manager, package)
        if command:
            self.execute_quick_command(command)
            self.package_input.delete(0, tk.END)
    
    def list_packages(self):
        """Paketleri listele"""
        manager = self.manager_var.get()
        command = self._get_list_command(manager)
        if command:
            self.execute_quick_command(command)
    
    def update_packages(self):
        """Paketleri güncelle"""
        manager = self.manager_var.get()
        command = self._get_update_command(manager)
        if command:
            self.execute_quick_command(command)
    
    def _get_install_command(self, manager: str, package: str) -> str:
        """Install komutu al"""
        commands = {
            "pip": f"pip install {package}",
            "npm": f"npm install {package}",
            "yarn": f"yarn add {package}",
            "choco": f"choco install {package}",
            "winget": f"winget install {package}",
            "apt": f"sudo apt install {package}",
            "yum": f"sudo yum install {package}",
            "dnf": f"sudo dnf install {package}",
            "pacman": f"sudo pacman -S {package}",
            "brew": f"brew install {package}",
            "cargo": f"cargo install {package}",
            "go": f"go install {package}",
            "composer": f"composer require {package}",
            "gem": f"gem install {package}",
            "conda": f"conda install {package}"
        }
        return commands.get(manager, "")
    
    def _get_uninstall_command(self, manager: str, package: str) -> str:
        """Uninstall komutu al"""
        commands = {
            "pip": f"pip uninstall {package}",
            "npm": f"npm uninstall {package}",
            "yarn": f"yarn remove {package}",
            "choco": f"choco uninstall {package}",
            "winget": f"winget uninstall {package}",
            "apt": f"sudo apt remove {package}",
            "yum": f"sudo yum remove {package}",
            "dnf": f"sudo dnf remove {package}",
            "pacman": f"sudo pacman -R {package}",
            "brew": f"brew uninstall {package}",
            "cargo": f"cargo uninstall {package}",
            "go": f"go clean -i {package}",
            "composer": f"composer remove {package}",
            "gem": f"gem uninstall {package}",
            "conda": f"conda remove {package}"
        }
        return commands.get(manager, "")
    
    def _get_list_command(self, manager: str) -> str:
        """List komutu al"""
        commands = {
            "pip": "pip list",
            "npm": "npm list -g --depth=0",
            "yarn": "yarn list --depth=0",
            "choco": "choco list --local-only",
            "winget": "winget list",
            "apt": "dpkg -l",
            "yum": "yum list installed",
            "dnf": "dnf list installed",
            "pacman": "pacman -Q",
            "brew": "brew list",
            "cargo": "cargo install --list",
            "go": "go list ...",
            "composer": "composer show",
            "gem": "gem list",
            "conda": "conda list"
        }
        return commands.get(manager, "")
    
    def _get_update_command(self, manager: str) -> str:
        """Update komutu al"""
        commands = {
            "pip": "pip list --outdated",
            "npm": "npm outdated -g",
            "yarn": "yarn outdated",
            "choco": "choco outdated",
            "winget": "winget upgrade",
            "apt": "sudo apt update && sudo apt upgrade",
            "yum": "sudo yum update",
            "dnf": "sudo dnf update",
            "pacman": "sudo pacman -Syu",
            "brew": "brew update && brew upgrade",
            "cargo": "cargo update",
            "go": "go get -u all",
            "composer": "composer update",
            "gem": "gem update",
            "conda": "conda update --all"
        }
        return commands.get(manager, "")

