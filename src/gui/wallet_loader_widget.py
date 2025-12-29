"""Wallet loader widget for opening saved wallets."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
import json

from .password_dialog import PasswordDialog
from plm_wallet.crypto.encryption import WalletEncryption
from plm_wallet.crypto.exceptions import InvalidPasswordError, DecryptionError
from plm_wallet.config.constants import WALLETS_DIR


class WalletLoaderWidget(QWidget):
    """Widget for loading saved wallets from JSON files."""

    wallet_loaded = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.wallets_dir = WALLETS_DIR
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("Open Saved Wallet")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        description = QLabel(
            "Select a wallet from the list below to view its details.\n"
            "Wallets are stored in the 'wallets' folder."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.load_wallet_list)
        refresh_layout.addWidget(refresh_btn)

        browse_btn = QPushButton("Browse Other Location...")
        browse_btn.clicked.connect(self.browse_wallet)
        refresh_layout.addWidget(browse_btn)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)

        # Wallet list
        list_label = QLabel("Saved Wallets:")
        list_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(list_label)

        self.wallet_list = QListWidget()
        self.wallet_list.itemDoubleClicked.connect(self.on_wallet_double_clicked)
        layout.addWidget(self.wallet_list)

        # Empty state label
        self.empty_label = QLabel("No wallets found in the 'wallets' folder.\nGenerate a new wallet and save it to see it here.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: gray; font-size: 13px; padding: 40px;")
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label)

        # Buttons
        btn_layout = QHBoxLayout()

        self.open_btn = QPushButton("Open Selected Wallet")
        self.open_btn.setMinimumHeight(40)
        self.open_btn.setEnabled(False)
        button_font = QFont()
        button_font.setPointSize(11)
        button_font.setBold(True)
        self.open_btn.setFont(button_font)
        self.open_btn.clicked.connect(self.open_selected_wallet)
        btn_layout.addWidget(self.open_btn)

        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_selected_wallet)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        # Connect selection change
        self.wallet_list.itemSelectionChanged.connect(self.on_selection_changed)

        # Load initial list
        self.load_wallet_list()

    def load_wallet_list(self):
        """Load the list of wallet files from the wallets directory."""
        self.wallet_list.clear()

        # Create wallets directory if it doesn't exist
        if not self.wallets_dir.exists():
            self.wallets_dir.mkdir(parents=True, exist_ok=True)

        # Find all JSON files
        json_files = list(self.wallets_dir.glob("*.json"))

        if not json_files:
            self.wallet_list.setVisible(False)
            self.empty_label.setVisible(True)
            self.open_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        self.wallet_list.setVisible(True)
        self.empty_label.setVisible(False)

        # Add files to list
        for json_file in sorted(json_files):
            item = QListWidgetItem(json_file.name)
            item.setData(Qt.ItemDataRole.UserRole, str(json_file))

            # Try to read wallet info for display
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    standard = data.get('standard', 'Unknown')
                    num_addresses = len(data.get('addresses', []))
                    item.setToolTip(f"Standard: {standard}\nAddresses: {num_addresses}")
            except Exception:
                item.setToolTip("Could not read wallet details")

            self.wallet_list.addItem(item)

    def on_selection_changed(self):
        """Handle wallet selection change."""
        has_selection = len(self.wallet_list.selectedItems()) > 0
        self.open_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def on_wallet_double_clicked(self, item):
        """Handle double-click on wallet item."""
        self.open_wallet_file(item.data(Qt.ItemDataRole.UserRole))

    def open_selected_wallet(self):
        """Open the currently selected wallet."""
        selected_items = self.wallet_list.selectedItems()
        if not selected_items:
            return

        file_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.open_wallet_file(file_path)

    def browse_wallet(self):
        """Browse for a wallet file in another location."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Wallet File",
            str(Path.home()),
            "JSON Files (*.json)"
        )

        if file_path:
            self.open_wallet_file(file_path)

    def open_wallet_file(self, file_path: str):
        """
        Open and load a wallet file.

        Args:
            file_path: Path to the wallet JSON file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                wallet_data = json.load(f)

            # Check if wallet is encrypted
            if WalletEncryption.is_encrypted(wallet_data):
                # Show password dialog
                filename = Path(file_path).name
                max_attempts = 3

                for attempt in range(max_attempts):
                    password_dialog = PasswordDialog(self, mode='decrypt', filename=filename)
                    if password_dialog.exec() == QDialog.DialogCode.Accepted:
                        password = password_dialog.get_password()
                        if password:
                            try:
                                # Decrypt the wallet
                                wallet_data = WalletEncryption.decrypt_wallet(wallet_data, password)
                                break  # Successfully decrypted
                            except InvalidPasswordError:
                                remaining = max_attempts - attempt - 1
                                if remaining > 0:
                                    QMessageBox.warning(
                                        self,
                                        "Invalid Password",
                                        f"Incorrect password. {remaining} attempt(s) remaining."
                                    )
                                else:
                                    QMessageBox.critical(
                                        self,
                                        "Access Denied",
                                        "Maximum password attempts reached. Cannot open wallet."
                                    )
                                    return
                            except DecryptionError as e:
                                QMessageBox.critical(
                                    self,
                                    "Decryption Error",
                                    f"Failed to decrypt wallet:\n{str(e)}"
                                )
                                return
                    else:
                        # User cancelled password dialog
                        return

            # Validate wallet data
            required_fields = ['mnemonic', 'standard', 'derivation_path', 'addresses']
            if not all(field in wallet_data for field in required_fields):
                raise ValueError("Invalid wallet file format")

            # Emit signal with wallet data
            self.wallet_loaded.emit(wallet_data)

        except json.JSONDecodeError:
            QMessageBox.critical(
                self,
                "Error",
                f"Invalid JSON file:\n{file_path}"
            )
        except ValueError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Invalid wallet file:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open wallet:\n{str(e)}"
            )

    def delete_selected_wallet(self):
        """Delete the currently selected wallet file."""
        selected_items = self.wallet_list.selectedItems()
        if not selected_items:
            return

        file_path = Path(selected_items[0].data(Qt.ItemDataRole.UserRole))
        file_name = file_path.name

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{file_name}'?\n\n"
            "This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                file_path.unlink()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Wallet '{file_name}' has been deleted."
                )
                self.load_wallet_list()
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete wallet:\n{str(e)}"
                )
