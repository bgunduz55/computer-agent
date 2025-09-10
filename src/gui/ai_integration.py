"""
JARVIS AI Integration GUI
AI yönetim ve test arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import asyncio
import logging
from typing import Dict, List, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class AIIntegrationWindow:
    """AI entegrasyon penceresi"""
    
    def __init__(self, parent, jarvis_core=None):
        self.parent = parent
        self.jarvis_core = jarvis_core
        self.window = None
        self.current_provider = "Ollama"
        self.providers = ["Ollama", "OpenAI", "Google Gemini", "Anthropic", "Cohere"]
        
    def show(self):
        """Pencereyi göster"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("🤖 AI Integration")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Ana frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🤖 AI Integration Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook oluştur
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Provider sekmesi
        self.create_provider_tab(notebook)
        
        # Test sekmesi
        self.create_test_tab(notebook)
        
        # RAG sekmesi
        self.create_rag_tab(notebook)
        
        # Settings sekmesi
        self.create_settings_tab(notebook)
        
    def create_provider_tab(self, notebook):
        """Provider sekmesini oluştur"""
        provider_frame = ttk.Frame(notebook)
        notebook.add(provider_frame, text="🔌 Providers")
        
        # Provider seçimi
        selection_frame = ttk.LabelFrame(provider_frame, text="Select AI Provider", padding="10")
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(selection_frame, text="Current Provider:").pack(side=tk.LEFT)
        self.provider_var = tk.StringVar(value=self.current_provider)
        provider_combo = ttk.Combobox(selection_frame, textvariable=self.provider_var,
                                     values=self.providers, state="readonly", width=20)
        provider_combo.pack(side=tk.LEFT, padx=(10, 20))
        provider_combo.bind('<<ComboboxSelected>>', self.on_provider_change)
        
        ttk.Button(selection_frame, text="🔄 Switch Provider", 
                  command=self.switch_provider).pack(side=tk.LEFT)
        
        # Provider durumu
        status_frame = ttk.LabelFrame(provider_frame, text="Provider Status", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.provider_status_text = scrolledtext.ScrolledText(status_frame, height=8, width=80)
        self.provider_status_text.pack(fill=tk.BOTH, expand=True)
        
        # Provider bilgilerini yükle
        self.load_provider_status()
        
    def create_test_tab(self, notebook):
        """Test sekmesini oluştur"""
        test_frame = ttk.Frame(notebook)
        notebook.add(test_frame, text="🧪 Test")
        
        # Test alanı
        test_area_frame = ttk.LabelFrame(test_frame, text="AI Test", padding="10")
        test_area_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Input alanı
        input_frame = ttk.Frame(test_area_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Test Message:").pack(side=tk.LEFT)
        self.test_input = ttk.Entry(input_frame, width=50)
        self.test_input.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        self.test_input.bind('<Return>', self.test_ai)
        
        ttk.Button(input_frame, text="Send", command=self.test_ai).pack(side=tk.RIGHT)
        
        # Response alanı
        ttk.Label(test_area_frame, text="AI Response:").pack(anchor=tk.W, pady=(10, 5))
        self.test_response_text = scrolledtext.ScrolledText(test_area_frame, height=15, width=80)
        self.test_response_text.pack(fill=tk.BOTH, expand=True)
        
        # Test örnekleri
        examples_frame = ttk.LabelFrame(test_frame, text="Test Examples", padding="10")
        examples_frame.pack(fill=tk.X, padx=10, pady=5)
        
        examples = [
            "What is the weather like today?",
            "Explain quantum computing in simple terms",
            "Write a Python function to sort a list",
            "What are the benefits of renewable energy?",
            "Tell me a joke"
        ]
        
        for i, example in enumerate(examples):
            btn = ttk.Button(examples_frame, text=example, 
                           command=lambda e=example: self.set_test_input(e))
            btn.pack(side=tk.LEFT, padx=(0, 5), pady=2)
    
    def create_rag_tab(self, notebook):
        """RAG sekmesini oluştur"""
        rag_frame = ttk.Frame(notebook)
        notebook.add(rag_frame, text="📚 RAG")
        
        # RAG durumu
        status_frame = ttk.LabelFrame(rag_frame, text="RAG System Status", padding="10")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.rag_status_text = scrolledtext.ScrolledText(status_frame, height=8, width=80)
        self.rag_status_text.pack(fill=tk.BOTH, expand=True)
        
        # RAG kontrolleri
        controls_frame = ttk.LabelFrame(rag_frame, text="RAG Controls", padding="10")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="🔄 Refresh Status", 
                  command=self.refresh_rag_status).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="📁 Add Documents", 
                  command=self.add_documents).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="🗑️ Clear Knowledge Base", 
                  command=self.clear_knowledge_base).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="🔍 Search Knowledge", 
                  command=self.search_knowledge).pack(side=tk.LEFT)
        
        # RAG durumunu yükle
        self.refresh_rag_status()
        
    def create_settings_tab(self, notebook):
        """Settings sekmesini oluştur"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        
        # AI ayarları
        ai_settings_frame = ttk.LabelFrame(settings_frame, text="AI Settings", padding="10")
        ai_settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Model seçimi
        model_frame = ttk.Frame(ai_settings_frame)
        model_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value="gpt-oss:20b")
        model_combo = ttk.Combobox(model_frame, textvariable=self.model_var,
                                  values=["gpt-oss:20b", "gpt-4", "gpt-3.5-turbo"],
                                  state="readonly", width=30)
        model_combo.pack(side=tk.LEFT, padx=(10, 20))
        
        # Temperature ayarı
        temp_frame = ttk.Frame(ai_settings_frame)
        temp_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(temp_frame, text="Temperature:").pack(side=tk.LEFT)
        self.temperature_var = tk.DoubleVar(value=0.7)
        temp_scale = ttk.Scale(temp_frame, from_=0.0, to=2.0, variable=self.temperature_var,
                              orient=tk.HORIZONTAL, length=200)
        temp_scale.pack(side=tk.LEFT, padx=(10, 10))
        
        temp_label = ttk.Label(temp_frame, text="0.7")
        temp_label.pack(side=tk.LEFT)
        
        def update_temp_label(value):
            temp_label.config(text=f"{float(value):.1f}")
        temp_scale.config(command=update_temp_label)
        
        # Max tokens ayarı
        tokens_frame = ttk.Frame(ai_settings_frame)
        tokens_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(tokens_frame, text="Max Tokens:").pack(side=tk.LEFT)
        self.max_tokens_var = tk.IntVar(value=1000)
        tokens_spin = ttk.Spinbox(tokens_frame, from_=100, to=4000, textvariable=self.max_tokens_var,
                                 width=10)
        tokens_spin.pack(side=tk.LEFT, padx=(10, 20))
        
        # API Key ayarları
        api_frame = ttk.LabelFrame(settings_frame, text="API Keys", padding="10")
        api_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # API Key'ler için form
        self.api_keys = {}
        api_providers = ["OpenAI", "Google Gemini", "Anthropic", "Cohere"]
        
        for i, provider in enumerate(api_providers):
            key_frame = ttk.Frame(api_frame)
            key_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(key_frame, text=f"{provider} API Key:", width=15).pack(side=tk.LEFT)
            self.api_keys[provider] = ttk.Entry(key_frame, width=50, show="*")
            self.api_keys[provider].pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
            
            ttk.Button(key_frame, text="Test", 
                      command=lambda p=provider: self.test_api_key(p)).pack(side=tk.RIGHT)
        
        # Kaydet butonu
        save_frame = ttk.Frame(settings_frame)
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(save_frame, text="💾 Save Settings", 
                  command=self.save_settings).pack(side=tk.RIGHT)
        ttk.Button(save_frame, text="🔄 Load Settings", 
                  command=self.load_settings).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Ayarları yükle
        self.load_settings()
        
    def on_provider_change(self, event=None):
        """Provider değiştiğinde"""
        self.current_provider = self.provider_var.get()
        self.load_provider_status()
        
    def switch_provider(self):
        """Provider'ı değiştir"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'ai_manager'):
                # Provider'ı değiştir
                self.jarvis_core.ai_manager.switch_provider(self.current_provider)
                messagebox.showinfo("Success", f"Switched to {self.current_provider}")
                self.load_provider_status()
            else:
                messagebox.showwarning("Warning", "AI Manager not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch provider: {e}")
    
    def load_provider_status(self):
        """Provider durumunu yükle"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'ai_manager'):
                status = self.jarvis_core.ai_manager.get_status()
                
                status_text = f"""Current Provider: {self.current_provider}

Status: {'Active' if status.get('is_active') else 'Inactive'}
Available Providers: {', '.join(status.get('available_providers', []))}
Current Model: {status.get('current_model', 'Unknown')}
Total Requests: {status.get('total_requests', 0)}
Successful Requests: {status.get('successful_requests', 0)}
Failed Requests: {status.get('failed_requests', 0)}
Average Response Time: {status.get('avg_response_time', 0):.2f}s

Configuration:
- Temperature: {status.get('temperature', 0.7)}
- Max Tokens: {status.get('max_tokens', 1000)}
- Timeout: {status.get('timeout', 30)}s
                """
                
                self.provider_status_text.delete(1.0, tk.END)
                self.provider_status_text.insert(tk.END, status_text)
            else:
                self.provider_status_text.delete(1.0, tk.END)
                self.provider_status_text.insert(tk.END, "AI Manager not available")
        except Exception as e:
            self.provider_status_text.delete(1.0, tk.END)
            self.provider_status_text.insert(tk.END, f"Error loading status: {e}")
    
    def test_ai(self, event=None):
        """AI'yi test et"""
        message = self.test_input.get()
        if not message:
            return
        
        self.test_response_text.delete(1.0, tk.END)
        self.test_response_text.insert(tk.END, "Processing...\n")
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if self.jarvis_core and hasattr(self.jarvis_core, 'ai_manager'):
                    response = loop.run_until_complete(
                        self.jarvis_core.ai_manager.process_query(message)
                    )
                    self.window.after(0, lambda r=response: self._update_test_response(r))
                else:
                    self.window.after(0, lambda: self._update_test_response("AI Manager not available"))
            except Exception as e:
                error_msg = f"Error: {e}"
                self.window.after(0, lambda: self._update_test_response(error_msg))
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        
        self.test_input.delete(0, tk.END)
    
    def set_test_input(self, text: str):
        """Test input'unu ayarla"""
        self.test_input.delete(0, tk.END)
        self.test_input.insert(0, text)
    
    def _update_test_response(self, response: str):
        """Test response'unu güncelle"""
        self.test_response_text.delete(1.0, tk.END)
        self.test_response_text.insert(tk.END, response)
    
    def refresh_rag_status(self):
        """RAG durumunu yenile"""
        try:
            if self.jarvis_core and hasattr(self.jarvis_core, 'rag_system'):
                status = self.jarvis_core.rag_system.get_status()
                
                status_text = f"""RAG System Status:

Vector Store: {'Active' if status.get('vector_store_active') else 'Inactive'}
Embedding Model: {status.get('embedding_model', 'Unknown')}
Total Documents: {status.get('total_documents', 0)}
Total Chunks: {status.get('total_chunks', 0)}
Index Size: {status.get('index_size', 0)} MB
Last Updated: {status.get('last_updated', 'Never')}

Performance:
- Average Query Time: {status.get('avg_query_time', 0):.2f}s
- Total Queries: {status.get('total_queries', 0)}
- Cache Hit Rate: {status.get('cache_hit_rate', 0):.1f}%
                """
                
                self.rag_status_text.delete(1.0, tk.END)
                self.rag_status_text.insert(tk.END, status_text)
            else:
                self.rag_status_text.delete(1.0, tk.END)
                self.rag_status_text.insert(tk.END, "RAG System not available")
        except Exception as e:
            self.rag_status_text.delete(1.0, tk.END)
            self.rag_status_text.insert(tk.END, f"Error loading RAG status: {e}")
    
    def add_documents(self):
        """Doküman ekle"""
        try:
            files = filedialog.askopenfilenames(
                title="Select Documents",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("PDF files", "*.pdf"),
                    ("Word files", "*.docx"),
                    ("All files", "*.*")
                ]
            )
            
            if files:
                if self.jarvis_core and hasattr(self.jarvis_core, 'rag_system'):
                    def add_async():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            for file_path in files:
                                loop.run_until_complete(
                                    self.jarvis_core.rag_system.add_document(file_path)
                                )
                            self.window.after(0, lambda: messagebox.showinfo("Success", f"Added {len(files)} documents"))
                            self.window.after(0, self.refresh_rag_status)
                        except Exception as e:
                            self.window.after(0, lambda: messagebox.showerror("Error", f"Failed to add documents: {e}"))
                        finally:
                            loop.close()
                    
                    thread = threading.Thread(target=add_async, daemon=True)
                    thread.start()
                else:
                    messagebox.showwarning("Warning", "RAG System not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add documents: {e}")
    
    def clear_knowledge_base(self):
        """Bilgi tabanını temizle"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the knowledge base?"):
            try:
                if self.jarvis_core and hasattr(self.jarvis_core, 'rag_system'):
                    def clear_async():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(self.jarvis_core.rag_system.clear_knowledge_base())
                            self.window.after(0, lambda: messagebox.showinfo("Success", "Knowledge base cleared"))
                            self.window.after(0, self.refresh_rag_status)
                        except Exception as e:
                            self.window.after(0, lambda: messagebox.showerror("Error", f"Failed to clear knowledge base: {e}"))
                        finally:
                            loop.close()
                    
                    thread = threading.Thread(target=clear_async, daemon=True)
                    thread.start()
                else:
                    messagebox.showwarning("Warning", "RAG System not available")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear knowledge base: {e}")
    
    def search_knowledge(self):
        """Bilgi tabanında ara"""
        query = tk.simpledialog.askstring("Search Knowledge", "Enter search query:")
        if query:
            try:
                if self.jarvis_core and hasattr(self.jarvis_core, 'rag_system'):
                    def search_async():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            results = loop.run_until_complete(
                                self.jarvis_core.rag_system.search(query, limit=5)
                            )
                            self.window.after(0, lambda: self._show_search_results(results))
                        except Exception as e:
                            self.window.after(0, lambda: messagebox.showerror("Error", f"Search failed: {e}"))
                        finally:
                            loop.close()
                    
                    thread = threading.Thread(target=search_async, daemon=True)
                    thread.start()
                else:
                    messagebox.showwarning("Warning", "RAG System not available")
            except Exception as e:
                messagebox.showerror("Error", f"Search failed: {e}")
    
    def _show_search_results(self, results):
        """Arama sonuçlarını göster"""
        if results:
            result_text = "Search Results:\n\n"
            for i, result in enumerate(results, 1):
                result_text += f"{i}. {result.get('content', '')[:200]}...\n"
                result_text += f"   Score: {result.get('score', 0):.3f}\n\n"
            
            # Sonuçları yeni pencerede göster
            result_window = tk.Toplevel(self.window)
            result_window.title("Search Results")
            result_window.geometry("800x600")
            
            text_widget = scrolledtext.ScrolledText(result_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, result_text)
            text_widget.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("Search Results", "No results found")
    
    def test_api_key(self, provider: str):
        """API key'i test et"""
        api_key = self.api_keys[provider].get()
        if not api_key:
            messagebox.showwarning("Warning", f"Please enter {provider} API key")
            return
        
        messagebox.showinfo("Info", f"API key testing for {provider} will be implemented")
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            settings = {
                "ai_provider": self.current_provider,
                "model": self.model_var.get(),
                "temperature": self.temperature_var.get(),
                "max_tokens": self.max_tokens_var.get(),
                "api_keys": {provider: key.get() for provider, key in self.api_keys.items()}
            }
            
            settings_file = Path("config/ai_settings.json")
            settings_file.parent.mkdir(exist_ok=True)
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def load_settings(self):
        """Ayarları yükle"""
        try:
            settings_file = Path("config/ai_settings.json")
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                self.current_provider = settings.get("ai_provider", "Ollama")
                self.provider_var.set(self.current_provider)
                self.model_var.set(settings.get("model", "deepseek-r1:7b"))
                self.temperature_var.set(settings.get("temperature", 0.7))
                self.max_tokens_var.set(settings.get("max_tokens", 1000))
                
                api_keys = settings.get("api_keys", {})
                for provider, key in api_keys.items():
                    if provider in self.api_keys:
                        self.api_keys[provider].insert(0, key)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
