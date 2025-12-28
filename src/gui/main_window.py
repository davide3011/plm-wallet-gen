"""Main window for PLM Wallet Generator GUI."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from .wallet_generator_widget import WalletGeneratorWidget
from .wallet_display_widget import WalletDisplayWidget
from .wallet_loader_widget import WalletLoaderWidget


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

        # Loader tab
        self.loader_widget = WalletLoaderWidget()
        self.tabs.addTab(self.loader_widget, "Open Wallet")

        # Display tab
        self.display_widget = WalletDisplayWidget()
        self.tabs.addTab(self.display_widget, "Wallet Details")

        # Connect signals
        self.generator_widget.wallet_generated.connect(self.on_wallet_generated)
        self.loader_widget.wallet_loaded.connect(self.on_wallet_loaded)
        self.display_widget.wallet_saved.connect(self.on_wallet_saved)

        # Set initial tab
        self.tabs.setCurrentIndex(0)

    def on_wallet_generated(self, wallet_data: dict):
        """
        Handle wallet generation.

        Args:
            wallet_data: Generated wallet data
        """
        self.display_widget.display_wallet(wallet_data)
        self.tabs.setCurrentIndex(2)  # Switch to Wallet Details tab

    def on_wallet_loaded(self, wallet_data: dict):
        """
        Handle wallet loading from file.

        Args:
            wallet_data: Loaded wallet data
        """
        self.display_widget.display_wallet(wallet_data)
        self.tabs.setCurrentIndex(2)  # Switch to Wallet Details tab

    def on_wallet_saved(self):
        """Handle wallet save event to refresh the loader list."""
        self.loader_widget.load_wallet_list()
