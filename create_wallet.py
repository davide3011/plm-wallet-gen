"""
PLM Wallet Generator - Entry point wrapper.

This file maintains backward compatibility while delegating
to the new modular architecture in src/.
"""

import sys
from pathlib import Path

# Add src/ to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cli.main import main

if __name__ == '__main__':
    main()
