#!/usr/bin/env python3
"""
Lakewatch Node GUI Launcher
----------------------------
This script launches the Lakewatch Node monitoring GUI.
"""

import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from node.node.ui import start_gui
    
    print("Launching Lakewatch Node Monitoring GUI...")
    # Use test data for now - can be changed to False to use real sensor data
    start_gui(use_test_data=True)
    
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("\nPlease make sure you have installed the required dependencies:")
    print("  - tkinter")
    print("  - matplotlib")
    print("\nYou can install them with:")
    print("  pip install matplotlib")
    print("  (tkinter should be installed with Python, but may require additional system packages)")
    sys.exit(1)
except Exception as e:
    print(f"Error launching GUI: {e}")
    sys.exit(1)