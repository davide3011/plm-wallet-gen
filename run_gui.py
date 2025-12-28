"""
PLM Wallet Generator - GUI Entry point.

This script launches the graphical user interface for the PLM Wallet Generator.
"""

import sys
from pathlib import Path

# Add src/ to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gui.app import main

if __name__ == '__main__':
    main()
