"""Main window for PLM Wallet Generator GUI."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from .wallet_generator_widget import WalletGeneratorWidget
from .wallet_display_widget import WalletDisplayWidget


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PLM Wallet Generator")
        self.setMinimumSize(900, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Generator tab
        self.generator_widget = WalletGeneratorWidget()
        self.tabs.addTab(self.generator_widget, "Generate Wallet")

        # Display tab
        self.display_widget = WalletDisplayWidget()
        self.tabs.addTab(self.display_widget, "Wallet Details")

        # Connect signals
        self.generator_widget.wallet_generated.connect(self.on_wallet_generated)

        # Set initial tab
        self.tabs.setCurrentIndex(0)

    def on_wallet_generated(self, wallet_data: dict):
        """
        Handle wallet generation.

        Args:
            wallet_data: Generated wallet data
        """
        self.display_widget.display_wallet(wallet_data)
        self.tabs.setCurrentIndex(1)
