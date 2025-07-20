# This file serves as the entry point for Streamlit Cloud deployment
# It imports and runs the Vietnamese homepage application

# Import the main page content from Trang_chủ.py
import os
import sys

# Add current directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and execute the main application from Trang_chủ.py
import importlib.util
spec = importlib.util.spec_from_file_location("main_app", "Trang_chủ.py")
main_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_app)