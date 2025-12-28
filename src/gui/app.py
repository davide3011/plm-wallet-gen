"""GUI application entry point."""

import sys
from PyQt6.QtWidgets import QApplication
from .main_window import MainWindow


def main():
    """Start the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("PLM Wallet Generator")
    app.setOrganizationName("PLM")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
