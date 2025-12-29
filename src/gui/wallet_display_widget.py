"""Wallet display widget."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QScrollArea, QCheckBox, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QClipboard
from PyQt6.QtWidgets import QApplication
import json
from pathlib import Path

from .password_dialog import PasswordDialog
from plm_wallet.crypto.encryption import WalletEncryption
from plm_wallet.crypto.exceptions import EncryptionError


class WalletDisplayWidget(QWidget):
    """Widget for displaying wallet information."""

    wallet_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.wallet_data = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Wallet Details")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Placeholder
        self.placeholder = QLabel("No wallet generated yet.\nGo to 'Generate Wallet' tab to create a new wallet.")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: gray; font-size: 14px; padding: 50px;")
        layout.addWidget(self.placeholder)

        # Wallet info container (hidden initially)
        self.wallet_container = QWidget()
        wallet_layout = QVBoxLayout(self.wallet_container)
        wallet_layout.setSpacing(10)
        wallet_layout.setContentsMargins(0, 0, 0, 0)

        # Standard and Derivation Path
        info_group = QGroupBox("Wallet Information")
        info_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        info_layout = QVBoxLayout()

        self.standard_label = QLabel()
        self.standard_label.setFont(QFont("Courier", 10))
        info_layout.addWidget(self.standard_label)

        self.derivation_label = QLabel()
        self.derivation_label.setFont(QFont("Courier", 10))
        info_layout.addWidget(self.derivation_label)

        info_group.setLayout(info_layout)
        wallet_layout.addWidget(info_group)

        # Mnemonic group
        mnemonic_group = QGroupBox("Mnemonic Phrase")
        mnemonic_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        mnemonic_layout = QVBoxLayout()

        self.mnemonic_text = QTextEdit()
        self.mnemonic_text.setReadOnly(True)
        self.mnemonic_text.setMaximumHeight(80)
        self.mnemonic_text.setFont(QFont("Courier", 11))
        self.mnemonic_text.setStyleSheet("background-color: #fff9e6; color: #000;")
        mnemonic_layout.addWidget(self.mnemonic_text)

        mnemonic_btn_layout = QHBoxLayout()
        copy_mnemonic_btn = QPushButton("Copy Mnemonic")
        copy_mnemonic_btn.clicked.connect(lambda: self.copy_to_clipboard(self.mnemonic_text.toPlainText()))
        mnemonic_btn_layout.addWidget(copy_mnemonic_btn)
        mnemonic_btn_layout.addStretch()
        mnemonic_layout.addLayout(mnemonic_btn_layout)

        mnemonic_group.setLayout(mnemonic_layout)
        wallet_layout.addWidget(mnemonic_group)

        # Show Master Keys checkbox
        self.show_master_checkbox = QCheckBox("Show Master Extended Keys (Advanced)")
        self.show_master_checkbox.setChecked(False)
        self.show_master_checkbox.stateChanged.connect(self.toggle_master_keys)
        wallet_layout.addWidget(self.show_master_checkbox)

        # Master keys group
        self.master_group = QGroupBox("Master Extended Keys")
        self.master_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        self.master_group.setVisible(False)  # Hidden by default
        master_layout = QVBoxLayout()

        # Master zprv
        master_zprv_label = QLabel("Master Private Key (zprv):")
        master_zprv_label.setFont(QFont("", 9, QFont.Weight.Bold))
        master_layout.addWidget(master_zprv_label)

        self.master_zprv_text = QTextEdit()
        self.master_zprv_text.setReadOnly(True)
        self.master_zprv_text.setMaximumHeight(60)
        self.master_zprv_text.setFont(QFont("Courier", 9))
        self.master_zprv_text.setStyleSheet("background-color: #ffebee; color: #000;")
        master_layout.addWidget(self.master_zprv_text)

        copy_master_zprv_btn = QPushButton("Copy Master zprv")
        copy_master_zprv_btn.clicked.connect(lambda: self.copy_to_clipboard(self.master_zprv_text.toPlainText()))
        master_layout.addWidget(copy_master_zprv_btn)

        # Master zpub
        master_zpub_label = QLabel("Master Public Key (zpub):")
        master_zpub_label.setFont(QFont("", 9, QFont.Weight.Bold))
        master_layout.addWidget(master_zpub_label)

        self.master_zpub_text = QTextEdit()
        self.master_zpub_text.setReadOnly(True)
        self.master_zpub_text.setMaximumHeight(60)
        self.master_zpub_text.setFont(QFont("Courier", 9))
        master_layout.addWidget(self.master_zpub_text)

        copy_master_zpub_btn = QPushButton("Copy Master zpub")
        copy_master_zpub_btn.clicked.connect(lambda: self.copy_to_clipboard(self.master_zpub_text.toPlainText()))
        master_layout.addWidget(copy_master_zpub_btn)

        self.master_group.setLayout(master_layout)
        wallet_layout.addWidget(self.master_group)

        # Account keys group
        account_group = QGroupBox("Account Extended Keys")
        account_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        account_layout = QVBoxLayout()

        # Account zprv
        account_zprv_label = QLabel("Account Private Key (zprv):")
        account_zprv_label.setFont(QFont("", 9, QFont.Weight.Bold))
        account_layout.addWidget(account_zprv_label)

        self.account_zprv_text = QTextEdit()
        self.account_zprv_text.setReadOnly(True)
        self.account_zprv_text.setMaximumHeight(60)
        self.account_zprv_text.setFont(QFont("Courier", 9))
        self.account_zprv_text.setStyleSheet("background-color: #ffebee; color: #000;")
        account_layout.addWidget(self.account_zprv_text)

        copy_account_zprv_btn = QPushButton("Copy Account zprv")
        copy_account_zprv_btn.clicked.connect(lambda: self.copy_to_clipboard(self.account_zprv_text.toPlainText()))
        account_layout.addWidget(copy_account_zprv_btn)

        # Account zpub
        account_zpub_label = QLabel("Account Public Key (zpub):")
        account_zpub_label.setFont(QFont("", 9, QFont.Weight.Bold))
        account_layout.addWidget(account_zpub_label)

        self.account_zpub_text = QTextEdit()
        self.account_zpub_text.setReadOnly(True)
        self.account_zpub_text.setMaximumHeight(60)
        self.account_zpub_text.setFont(QFont("Courier", 9))
        account_layout.addWidget(self.account_zpub_text)

        copy_account_zpub_btn = QPushButton("Copy Account zpub")
        copy_account_zpub_btn.clicked.connect(lambda: self.copy_to_clipboard(self.account_zpub_text.toPlainText()))
        account_layout.addWidget(copy_account_zpub_btn)

        account_group.setLayout(account_layout)
        wallet_layout.addWidget(account_group)

        # Addresses group
        addresses_group = QGroupBox("Generated Addresses")
        addresses_group.setStyleSheet("QGroupBox::title { font-weight: bold; }")
        addresses_layout = QVBoxLayout()

        # Show keys checkbox
        self.show_keys_checkbox = QCheckBox("Show Public Keys and Private Keys")
        self.show_keys_checkbox.setChecked(False)
        self.show_keys_checkbox.setToolTip("Display the public key (compressed) and private key in hexadecimal format for each address")
        self.show_keys_checkbox.stateChanged.connect(self.toggle_keys_display)
        addresses_layout.addWidget(self.show_keys_checkbox)

        self.addresses_table = QTableWidget()
        self.addresses_table.setColumnCount(2)
        self.addresses_table.setHorizontalHeaderLabels(["Path", "Address"])
        self.addresses_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.addresses_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.addresses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.addresses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.addresses_table.setAlternatingRowColors(True)
        self.addresses_table.verticalHeader().setVisible(False)
        self.addresses_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                selection-background-color: #0078d7;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:hover {
                background-color: transparent;
            }
        """)
        addresses_layout.addWidget(self.addresses_table)

        # Buttons layout
        addr_btn_layout = QHBoxLayout()

        copy_addresses_btn = QPushButton("Copy All Addresses")
        copy_addresses_btn.clicked.connect(self.copy_all_addresses)
        addr_btn_layout.addWidget(copy_addresses_btn)

        copy_selected_btn = QPushButton("Copy Selected Row")
        copy_selected_btn.clicked.connect(self.copy_selected_row)
        addr_btn_layout.addWidget(copy_selected_btn)

        addr_btn_layout.addStretch()
        addresses_layout.addLayout(addr_btn_layout)

        addresses_group.setLayout(addresses_layout)
        wallet_layout.addWidget(addresses_group)

        # Action buttons
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("Save to JSON")
        save_btn.setMinimumHeight(35)
        save_btn.clicked.connect(self.save_to_file)
        btn_layout.addWidget(save_btn)

        export_mnemonic_btn = QPushButton("Export Mnemonic Only")
        export_mnemonic_btn.setMinimumHeight(35)
        export_mnemonic_btn.clicked.connect(self.export_mnemonic)
        btn_layout.addWidget(export_mnemonic_btn)

        wallet_layout.addLayout(btn_layout)

        self.wallet_container.setLayout(wallet_layout)
        self.wallet_container.setVisible(False)
        layout.addWidget(self.wallet_container)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def display_wallet(self, wallet_data: dict):
        """
        Display wallet information.

        Args:
            wallet_data: Wallet data to display
        """
        self.wallet_data = wallet_data

        # Hide placeholder, show wallet info
        self.placeholder.setVisible(False)
        self.wallet_container.setVisible(True)

        # Populate fields
        self.standard_label.setText(f"Standard: {wallet_data['standard']}")
        self.derivation_label.setText(f"Derivation Path: {wallet_data['derivation_path']}")
        self.mnemonic_text.setPlainText(wallet_data['mnemonic'])
        self.master_zprv_text.setPlainText(wallet_data['master_zprv'])
        self.master_zpub_text.setPlainText(wallet_data['master_zpub'])
        self.account_zprv_text.setPlainText(wallet_data['zprv'])
        self.account_zpub_text.setPlainText(wallet_data['zpub'])

        # Populate addresses table
        self._populate_addresses_table()

    def _populate_addresses_table(self):
        """Populate the addresses table based on current settings."""
        if not self.wallet_data:
            return

        addresses = self.wallet_data['addresses']
        show_keys = self.show_keys_checkbox.isChecked()

        # Always use 2 columns: Path and Details
        self.addresses_table.setColumnCount(2)
        self.addresses_table.setHorizontalHeaderLabels(["Path", "Address & Keys"])
        self.addresses_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.addresses_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # Populate rows
        self.addresses_table.setRowCount(len(addresses))
        for i, addr_info in enumerate(addresses):
            # Path
            path_item = QTableWidgetItem(addr_info['path'])
            path_item.setFont(QFont("", 9))
            self.addresses_table.setItem(i, 0, path_item)

            # Create custom widget for Address & Keys with copy buttons
            details_widget = self._create_details_widget(addr_info, show_keys)
            self.addresses_table.setCellWidget(i, 1, details_widget)

        # Adjust row heights based on content
        if show_keys:
            for i in range(len(addresses)):
                self.addresses_table.setRowHeight(i, 95)
        else:
            for i in range(len(addresses)):
                self.addresses_table.setRowHeight(i, 35)

        self.addresses_table.resizeColumnToContents(0)

        # Adjust table height based on content
        self._adjust_table_height(show_keys, len(addresses))

    def _create_details_widget(self, addr_info: dict, show_keys: bool) -> QWidget:
        """
        Create a custom widget for address details with copy buttons.

        Args:
            addr_info: Address information dictionary
            show_keys: Whether to show keys

        Returns:
            QWidget with formatted details and copy buttons
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(2)

        # Address row
        addr_layout = QHBoxLayout()
        addr_layout.setSpacing(5)

        if show_keys:
            addr_label = QLabel("Address:")
            addr_label.setFont(QFont("", 9))
            addr_label.setFixedWidth(60)
            addr_layout.addWidget(addr_label)

        addr_value = QLabel(addr_info['address'])
        addr_value.setFont(QFont("Courier", 9))
        addr_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        addr_layout.addWidget(addr_value)

        copy_addr_btn = QPushButton("📋")
        copy_addr_btn.setFixedSize(25, 20)
        copy_addr_btn.setToolTip("Copy address")
        copy_addr_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0078d7;
                color: white;
                border: 1px solid #0078d7;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        copy_addr_btn.clicked.connect(lambda checked=False, btn=copy_addr_btn, txt=addr_info['address']: self._copy_with_feedback(btn, txt))
        addr_layout.addWidget(copy_addr_btn)

        layout.addLayout(addr_layout)

        if show_keys:
            # PubKey row
            pubkey = addr_info.get('pubkey', 'N/A')
            pubkey_layout = QHBoxLayout()
            pubkey_layout.setSpacing(5)

            pubkey_label = QLabel("PubKey:")
            pubkey_label.setFont(QFont("", 9))
            pubkey_label.setFixedWidth(60)
            pubkey_layout.addWidget(pubkey_label)

            pubkey_value = QLabel(pubkey)
            pubkey_value.setFont(QFont("Courier", 8))
            pubkey_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            pubkey_value.setStyleSheet("color: #2e7d32;")  # Dark green
            pubkey_layout.addWidget(pubkey_value)

            copy_pubkey_btn = QPushButton("📋")
            copy_pubkey_btn.setFixedSize(25, 20)
            copy_pubkey_btn.setToolTip("Copy public key")
            copy_pubkey_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2e7d32;
                    color: white;
                    border: 1px solid #2e7d32;
                }
                QPushButton:pressed {
                    background-color: #1b5e20;
                }
            """)
            copy_pubkey_btn.clicked.connect(lambda checked=False, btn=copy_pubkey_btn, key=pubkey: self._copy_with_feedback(btn, key))
            pubkey_layout.addWidget(copy_pubkey_btn)

            layout.addLayout(pubkey_layout)

            # PrivKey row
            privkey = addr_info.get('privkey', 'N/A')
            privkey_layout = QHBoxLayout()
            privkey_layout.setSpacing(5)

            privkey_label = QLabel("PrivKey:")
            privkey_label.setFont(QFont("", 9))
            privkey_label.setFixedWidth(60)
            privkey_layout.addWidget(privkey_label)

            privkey_value = QLabel(privkey)
            privkey_value.setFont(QFont("Courier", 8))
            privkey_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            privkey_value.setStyleSheet("color: #c62828;")  # Dark red
            privkey_layout.addWidget(privkey_value)

            copy_privkey_btn = QPushButton("📋")
            copy_privkey_btn.setFixedSize(25, 20)
            copy_privkey_btn.setToolTip("Copy private key")
            copy_privkey_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c62828;
                    color: white;
                    border: 1px solid #c62828;
                }
                QPushButton:pressed {
                    background-color: #8e0000;
                }
            """)
            copy_privkey_btn.clicked.connect(lambda checked=False, btn=copy_privkey_btn, key=privkey: self._copy_with_feedback(btn, key))
            privkey_layout.addWidget(copy_privkey_btn)

            layout.addLayout(privkey_layout)

        return widget

    def _copy_to_clipboard_silent(self, text: str):
        """
        Copy text to clipboard without showing a popup message.

        Args:
            text: Text to copy
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        # Optional: Show brief status in status bar if available
        # For now, just copy silently for better UX

    def _copy_with_feedback(self, button: QPushButton, text: str):
        """
        Copy text to clipboard and show visual feedback on the button.

        Args:
            button: The button that was clicked
            text: Text to copy
        """
        from PyQt6.QtCore import QTimer

        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        # Store original text
        original_text = button.text()

        # Change button to checkmark
        button.setText("✓")

        # Reset button text after 1 second
        QTimer.singleShot(1000, lambda: button.setText(original_text))

    def _adjust_table_height(self, show_keys: bool, num_addresses: int):
        """
        Adjust table height based on content.

        Args:
            show_keys: Whether keys are shown
            num_addresses: Number of addresses
        """
        # Calculate height based on content
        header_height = self.addresses_table.horizontalHeader().height()

        if show_keys:
            # Each row is 95px when keys are shown (with copy buttons)
            row_height = 95
            total_height = header_height + (row_height * num_addresses) + 2  # +2 for borders
        else:
            # Each row is ~35px when keys are hidden
            row_height = 35
            total_height = header_height + (row_height * num_addresses) + 2

        # Set minimum and maximum heights for better UX
        min_height = 200  # Minimum height
        max_height = 650  # Maximum height to avoid too large tables

        calculated_height = max(min_height, min(total_height, max_height))
        self.addresses_table.setMinimumHeight(calculated_height)
        self.addresses_table.setMaximumHeight(calculated_height)

    def toggle_keys_display(self):
        """Toggle the display of public and private keys in the addresses table."""
        self._populate_addresses_table()

    def toggle_master_keys(self, state):
        """
        Toggle visibility of master extended keys.

        Args:
            state: Checkbox state
        """
        self.master_group.setVisible(state == Qt.CheckState.Checked.value)

    def copy_to_clipboard(self, text: str):
        """
        Copy text to clipboard.

        Args:
            text: Text to copy
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "Copied", "Text copied to clipboard!")

    def copy_all_addresses(self):
        """Copy all addresses to clipboard."""
        if not self.wallet_data:
            return

        show_keys = self.show_keys_checkbox.isChecked()

        if show_keys:
            addresses_text = "\n".join([
                f"{addr['path']}\n"
                f"  Address: {addr['address']}\n"
                f"  PubKey:  {addr.get('pubkey', 'N/A')}\n"
                f"  PrivKey: {addr.get('privkey', 'N/A')}\n"
                for addr in self.wallet_data['addresses']
            ])
        else:
            addresses_text = "\n".join([
                f"{addr['path']}: {addr['address']}"
                for addr in self.wallet_data['addresses']
            ])

        self.copy_to_clipboard(addresses_text)

    def copy_selected_row(self):
        """Copy the selected row data to clipboard."""
        if not self.wallet_data:
            return

        selected_rows = self.addresses_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a row first.")
            return

        # Get the row index
        row = self.addresses_table.currentRow()
        if row < 0 or row >= len(self.wallet_data['addresses']):
            return

        addr_info = self.wallet_data['addresses'][row]
        show_keys = self.show_keys_checkbox.isChecked()

        if show_keys:
            text = (
                f"Path: {addr_info['path']}\n"
                f"Address: {addr_info['address']}\n"
                f"Public Key: {addr_info.get('pubkey', 'N/A')}\n"
                f"Private Key: {addr_info.get('privkey', 'N/A')}"
            )
        else:
            text = f"{addr_info['path']}: {addr_info['address']}"

        self.copy_to_clipboard(text)

    def save_to_file(self):
        """Save wallet data to JSON file."""
        if not self.wallet_data:
            return

        # Create wallets directory if it doesn't exist
        wallets_dir = Path("wallets")
        wallets_dir.mkdir(parents=True, exist_ok=True)

        # Generate default filename based on standard and timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        standard = self.wallet_data.get('standard', 'wallet').replace(' ', '_')
        default_filename = f"{standard}_{timestamp}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Wallet Data",
            str(wallets_dir / default_filename),
            "JSON Files (*.json)"
        )

        if file_path:
            # Ask if user wants to encrypt the wallet
            reply = QMessageBox.question(
                self,
                "Encrypt Wallet?",
                "Do you want to encrypt this wallet with a password?\n\n"
                "Encrypted wallets are more secure but require a password to open.\n"
                "Choose 'No' to save without encryption.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return

            try:
                data_to_save = self.wallet_data

                # If user wants encryption, show password dialog
                if reply == QMessageBox.StandardButton.Yes:
                    password_dialog = PasswordDialog(self, mode='encrypt')
                    if password_dialog.exec() == QDialog.DialogCode.Accepted:
                        password = password_dialog.get_password()
                        if password:
                            # Encrypt the wallet data
                            data_to_save = WalletEncryption.encrypt_wallet(self.wallet_data, password)
                    else:
                        # User cancelled the password dialog
                        return

                # Save to file
                with open(file_path, 'w') as f:
                    json.dump(data_to_save, f, indent=2)

                encryption_status = "encrypted " if reply == QMessageBox.StandardButton.Yes else ""
                QMessageBox.information(
                    self,
                    "Success",
                    f"Wallet {encryption_status}saved to:\n{file_path}"
                )
                self.wallet_saved.emit()  # Notify that wallet was saved

            except EncryptionError as e:
                QMessageBox.critical(self, "Encryption Error", f"Failed to encrypt wallet:\n{str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save wallet:\n{str(e)}")

    def export_mnemonic(self):
        """Export only the mnemonic phrase to a text file."""
        if not self.wallet_data:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Mnemonic",
            str(Path.home() / "mnemonic.txt"),
            "Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.wallet_data['mnemonic'])
                QMessageBox.information(self, "Success", f"Mnemonic exported to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export mnemonic:\n{str(e)}")
