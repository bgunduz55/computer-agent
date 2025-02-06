import pyautogui
import pytesseract
from PIL import ImageGrab, Image
import json
import xml.etree.ElementTree as ET
import time
import re
import os

class ScreenScraper:
    def __init__(self):
        self.current_data = []
        self.last_screenshot = None
        
    def capture_area(self, x1=None, y1=None, x2=None, y2=None):
        """Belirtilen alanın ekran görüntüsünü al"""
        if all(v is None for v in [x1, y1, x2, y2]):
            # Kullanıcıdan alan seçmesini iste
            print("🔍 Lütfen veri çekmek istediğiniz alanı seçin...")
            region = pyautogui.dragSelect()
            x1, y1, x2, y2 = region
        
        # Ekran görüntüsü al
        self.last_screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        return self.last_screenshot
        
    def extract_text(self, image=None):
        """Görüntüden metin çıkar"""
        if image is None:
            image = self.last_screenshot
            
        if image is None:
            raise Exception("Önce bir ekran görüntüsü alın!")
            
        text = pytesseract.image_to_string(image, lang='tur+eng')
        return text.strip()
        
    def extract_tables(self, image=None):
        """Görüntüdeki tabloları çıkar"""
        if image is None:
            image = self.last_screenshot
            
        if image is None:
            raise Exception("Önce bir ekran görüntüsü alın!")
            
        tables = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
        return tables
        
    def save_data(self, data, format='json', filename=None):
        """Veriyi istenen formatta kaydet"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"scraped_data_{timestamp}"
            
        if format.lower() == 'json':
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        elif format.lower() == 'xml':
            root = ET.Element("data")
            for item in data:
                child = ET.SubElement(root, "item")
                for key, value in item.items():
                    ET.SubElement(child, key).text = str(value)
            tree = ET.ElementTree(root)
            tree.write(f"{filename}.xml", encoding='utf-8', xml_declaration=True)
            
        elif format.lower() == 'txt':
            with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
                f.write(str(data))
                
        return f"✅ Veriler {filename}.{format.lower()} dosyasına kaydedildi"
        
    def highlight_area(self, x, y, w, h, duration=0.5):
        """Seçili alanı vurgula"""
        pyautogui.moveTo(x, y)
        time.sleep(0.2)
        pyautogui.dragTo(x + w, y + h, duration=duration)
        time.sleep(0.2)
        pyautogui.click(x, y)  # Seçimi kaldır 