"""Wallet display widget."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QClipboard
from PyQt6.QtWidgets import QApplication
import json
from pathlib import Path


class WalletDisplayWidget(QWidget):
    """Widget for displaying wallet information."""

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
        layout.setSpacing(15)

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
        wallet_layout.setSpacing(15)

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

        self.addresses_table = QTableWidget()
        self.addresses_table.setColumnCount(2)
        self.addresses_table.setHorizontalHeaderLabels(["Derivation Path", "Address"])
        self.addresses_table.horizontalHeader().setStretchLastSection(True)
        self.addresses_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.addresses_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        addresses_layout.addWidget(self.addresses_table)

        copy_addresses_btn = QPushButton("Copy All Addresses")
        copy_addresses_btn.clicked.connect(self.copy_all_addresses)
        addresses_layout.addWidget(copy_addresses_btn)

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

        layout.addStretch()

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
        addresses = wallet_data['addresses']
        self.addresses_table.setRowCount(len(addresses))
        for i, addr_info in enumerate(addresses):
            path_item = QTableWidgetItem(addr_info['path'])
            address_item = QTableWidgetItem(addr_info['address'])
            address_item.setFont(QFont("Courier", 9))
            self.addresses_table.setItem(i, 0, path_item)
            self.addresses_table.setItem(i, 1, address_item)

        self.addresses_table.resizeColumnsToContents()

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

        addresses_text = "\n".join([
            f"{addr['path']}: {addr['address']}"
            for addr in self.wallet_data['addresses']
        ])
        self.copy_to_clipboard(addresses_text)

    def save_to_file(self):
        """Save wallet data to JSON file."""
        if not self.wallet_data:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Wallet Data",
            str(Path.home() / "wallet.json"),
            "JSON Files (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.wallet_data, f, indent=2)
                QMessageBox.information(self, "Success", f"Wallet saved to:\n{file_path}")
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
