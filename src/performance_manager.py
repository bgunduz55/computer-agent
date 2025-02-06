import psutil
import os
import gc
import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta
import threading
import time

class PerformanceManager:
    def __init__(self):
        self.logger = logging.getLogger("AICodeEditor.Performance")
        self.temp_dir = Path("data/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Performans metrikleri
        self.metrics = {
            "memory_usage": [],
            "cpu_usage": [],
            "disk_usage": [],
            "response_times": []
        }
        
        # Komut zamanlaması için
        self.command_timings = {}
        self.start_times = {}
        
        # Kaynak limitleri
        self.resource_limits = {
            "max_memory_percent": 80,  # Maksimum bellek kullanımı %
            "max_cpu_percent": 70,     # Maksimum CPU kullanımı %
            "max_disk_percent": 90,    # Maksimum disk kullanımı %
            "memory_cleanup_threshold": 70  # Bellek temizleme eşiği %
        }
        
        # Performans izleme thread'ini başlat
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitor_thread.start()
        
    def _monitor_resources(self):
        """Sistem kaynaklarını sürekli izle"""
        while self.monitoring:
            try:
                # Metrikleri topla
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=1)
                disk = psutil.disk_usage('/')
                
                # Metrikleri kaydet
                self.metrics["memory_usage"].append(memory.percent)
                self.metrics["cpu_usage"].append(cpu)
                self.metrics["disk_usage"].append(disk.percent)
                
                # Son 10 ölçümü tut
                for metric in self.metrics.values():
                    if len(metric) > 10:
                        metric.pop(0)
                
                # Kaynak kontrolü
                self._check_resource_usage()
                
                time.sleep(5)  # 5 saniye bekle
                
            except Exception as e:
                self.logger.error(f"Kaynak izleme hatası: {str(e)}")
                time.sleep(10)  # Hata durumunda 10 saniye bekle
    
    def _check_resource_usage(self):
        """Kaynak kullanımını kontrol et ve gerekirse önlem al"""
        try:
            # Bellek kullanımı yüksekse
            memory = psutil.virtual_memory()
            if memory.percent > self.resource_limits["memory_cleanup_threshold"]:
                self.optimize_memory()
            
            # CPU kullanımı yüksekse
            cpu = psutil.cpu_percent()
            if cpu > self.resource_limits["max_cpu_percent"]:
                self.optimize_cpu()
            
            # Disk kullanımı yüksekse
            disk = psutil.disk_usage('/')
            if disk.percent > self.resource_limits["max_disk_percent"]:
                self.cleanup_disk()
                
        except Exception as e:
            self.logger.error(f"Kaynak kontrolü hatası: {str(e)}")
    
    def optimize_memory(self):
        """Bellek optimizasyonu yap"""
        try:
            # Garbage collector'ı çalıştır
            gc.collect()
            
            # Temp dosyalarını temizle
            self.cleanup_temp_files()
            
            # Bellek kullanımını logla
            memory = psutil.virtual_memory()
            self.logger.info(f"Bellek optimizasyonu yapıldı. Kullanım: {memory.percent}%")
            
        except Exception as e:
            self.logger.error(f"Bellek optimizasyonu hatası: {str(e)}")
    
    def optimize_cpu(self):
        """CPU kullanımını optimize et"""
        try:
            # Yüksek CPU kullanan işlemleri bul
            high_cpu_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 20:  # %20'den fazla CPU kullanan işlemler
                        high_cpu_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Durumu logla
            if high_cpu_processes:
                self.logger.warning(f"Yüksek CPU kullanan işlemler: {high_cpu_processes}")
            
        except Exception as e:
            self.logger.error(f"CPU optimizasyonu hatası: {str(e)}")
    
    def cleanup_disk(self):
        """Disk temizliği yap"""
        try:
            # Temp dosyalarını temizle
            self.cleanup_temp_files()
            
            # Log dosyalarını arşivle
            self._archive_old_logs()
            
            # Disk kullanımını logla
            disk = psutil.disk_usage('/')
            self.logger.info(f"Disk temizliği yapıldı. Kullanım: {disk.percent}%")
            
        except Exception as e:
            self.logger.error(f"Disk temizliği hatası: {str(e)}")
    
    def cleanup_temp_files(self):
        """Geçici dosyaları temizle"""
        try:
            # 24 saatten eski temp dosyalarını sil
            cutoff = datetime.now() - timedelta(hours=24)
            
            for file in self.temp_dir.glob("*"):
                if file.stat().st_mtime < cutoff.timestamp():
                    if file.is_file():
                        file.unlink()
                    elif file.is_dir():
                        os.rmdir(file)
            
            self.logger.info("Geçici dosyalar temizlendi")
            
        except Exception as e:
            self.logger.error(f"Temp dosya temizleme hatası: {str(e)}")
    
    def _archive_old_logs(self):
        """Eski logları arşivle"""
        try:
            log_dir = Path("data/logs")
            archive_dir = log_dir / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            # 7 günden eski logları arşivle
            cutoff = datetime.now() - timedelta(days=7)
            
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff.timestamp():
                    archive_path = archive_dir / f"{log_file.stem}_{datetime.now():%Y%m%d}.log"
                    log_file.rename(archive_path)
            
        except Exception as e:
            self.logger.error(f"Log arşivleme hatası: {str(e)}")
    
    def get_performance_metrics(self) -> Dict:
        """Performans metriklerini getir"""
        try:
            current_metrics = {
                "memory": psutil.virtual_memory().percent,
                "cpu": psutil.cpu_percent(),
                "disk": psutil.disk_usage('/').percent,
                "average_response_time": sum(self.metrics["response_times"][-10:]) / len(self.metrics["response_times"][-10:]) if self.metrics["response_times"] else 0
            }
            return current_metrics
        except Exception as e:
            self.logger.error(f"Performans metrikleri alma hatası: {str(e)}")
            return {}
    
    def log_response_time(self, response_time: float):
        """Yanıt süresini kaydet"""
        try:
            self.metrics["response_times"].append(response_time)
            if len(self.metrics["response_times"]) > 100:
                self.metrics["response_times"].pop(0)
        except Exception as e:
            self.logger.error(f"Yanıt süresi kaydetme hatası: {str(e)}")
    
    def start_command_timing(self, command: str):
        """Komut zamanlamasını başlat"""
        self.start_times[command] = time.time()
        
    def end_command_timing(self, command: str):
        """Komut zamanlamasını bitir ve süreyi kaydet"""
        if command in self.start_times:
            end_time = time.time()
            duration = end_time - self.start_times[command]
            
            if command not in self.command_timings:
                self.command_timings[command] = []
                
            self.command_timings[command].append(duration)
            del self.start_times[command]
            
            # Son 10 ölçümü tut
            if len(self.command_timings[command]) > 10:
                self.command_timings[command].pop(0)
                
            return duration
        return None
    
    def __del__(self):
        """Yıkıcı metod"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=1) 