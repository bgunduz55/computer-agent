import os
import sys

# Proje kök dizinini PYTHONPATH'e ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from gui import main

if __name__ == "__main__":
    main() 