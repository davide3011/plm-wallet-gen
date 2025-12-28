"""Wallet generation widget."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QMessageBox, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtGui import QFont
from plm_wallet.wallet.wallet import PLMWallet
from plm_wallet.config.constants import VALID_WORD_COUNTS


class WalletGeneratorThread(QThread):
    """Thread for generating wallet without blocking UI."""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, word_count: int, standard: str):
        super().__init__()
        self.word_count = word_count
        self.standard = standard

    def run(self):
        """Generate wallet in background thread."""
        try:
            wallet = PLMWallet.generate(self.word_count, self.standard)
            wallet_data = wallet.export_json()
            self.finished.emit(wallet_data)
        except Exception as e:
            self.error.emit(str(e))


class WalletGeneratorWidget(QWidget):
    """Widget for wallet generation configuration."""

    wallet_generated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.generator_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("Generate New PLM Wallet")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        description = QLabel(
            "Create a new HD (Hierarchical Deterministic) wallet for Palladium (PLM).\n"
            "Choose the mnemonic length and standard below."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Configuration group
        config_group = QGroupBox("Wallet Configuration")
        config_layout = QVBoxLayout()

        # Word count selection
        word_count_layout = QHBoxLayout()
        word_count_label = QLabel("Mnemonic Words:")
        word_count_label.setMinimumWidth(150)
        self.word_count_combo = QComboBox()
        for count in VALID_WORD_COUNTS:
            self.word_count_combo.addItem(f"{count} words", count)
        self.word_count_combo.setCurrentIndex(0)  # Default to 12 words
        word_count_layout.addWidget(word_count_label)
        word_count_layout.addWidget(self.word_count_combo)
        word_count_layout.addStretch()
        config_layout.addLayout(word_count_layout)

        # Standard selection
        standard_layout = QHBoxLayout()
        standard_label = QLabel("Standard:")
        standard_label.setMinimumWidth(150)
        self.standard_combo = QComboBox()
        self.standard_combo.addItem("BIP39 (Most wallets)", "bip39")
        self.standard_combo.addItem("Electrum Segwit", "electrum")
        standard_layout.addWidget(standard_label)
        standard_layout.addWidget(self.standard_combo)
        standard_layout.addStretch()
        config_layout.addLayout(standard_layout)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)

        # Generate button
        self.generate_button = QPushButton("Generate Wallet")
        self.generate_button.setMinimumHeight(40)
        button_font = QFont()
        button_font.setPointSize(11)
        button_font.setBold(True)
        self.generate_button.setFont(button_font)
        self.generate_button.clicked.connect(self.generate_wallet)
        layout.addWidget(self.generate_button)

        # Warning
        warning = QLabel(
            "⚠️ WARNING: Keep your mnemonic phrase safe and secure!\n"
            "Anyone with access to it can access your funds.\n"
            "Never share it with anyone."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #d32f2f; font-weight: bold;")
        layout.addWidget(warning)

        layout.addStretch()

    def generate_wallet(self):
        """Generate a new wallet."""
        word_count = self.word_count_combo.currentData()
        standard = self.standard_combo.currentData()

        # Disable UI during generation
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)

        # Create and start generation thread
        self.generator_thread = WalletGeneratorThread(word_count, standard)
        self.generator_thread.finished.connect(self.on_generation_finished)
        self.generator_thread.error.connect(self.on_generation_error)
        self.generator_thread.start()

    def on_generation_finished(self, wallet_data: dict):
        """
        Handle successful wallet generation.

        Args:
            wallet_data: Generated wallet data
        """
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        self.wallet_generated.emit(wallet_data)

    def on_generation_error(self, error_msg: str):
        """
        Handle wallet generation error.

        Args:
            error_msg: Error message
        """
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Failed to generate wallet:\n{error_msg}")

    def set_ui_enabled(self, enabled: bool):
        """
        Enable or disable UI controls.

        Args:
            enabled: Whether to enable controls
        """
        self.word_count_combo.setEnabled(enabled)
        self.standard_combo.setEnabled(enabled)
        self.generate_button.setEnabled(enabled)
