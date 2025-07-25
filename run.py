#!/usr/bin/env python3
"""
IPyTV Player - Launch Script
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import and run the main application
from main import main

if __name__ == "__main__":
    sys.exit(main())
