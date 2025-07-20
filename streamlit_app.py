#!/usr/bin/env python3
"""
Entry point for Streamlit Cloud deployment
Redirects to the Vietnamese homepage
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Execute the Vietnamese homepage
try:
    exec(open("🏠_Trang_chủ.py").read())
except FileNotFoundError:
    # Fallback to original file
    exec(open("Trang_chủ.py").read())