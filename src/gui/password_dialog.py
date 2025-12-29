"""Password input dialog for wallet encryption/decryption."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PasswordDialog(QDialog):
    """Dialog for entering encryption password."""

    def __init__(self, parent=None, mode='encrypt', filename=''):
        """
        Initialize password dialog.

        Args:
            parent: Parent widget
            mode: 'encrypt' or 'decrypt'
            filename: Name of the file (for decrypt mode)
        """
        super().__init__(parent)
        self.mode = mode
        self.filename = filename
        self.password = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        if self.mode == 'encrypt':
            self.setWindowTitle("Encrypt Wallet")
        else:
            self.setWindowTitle("Decrypt Wallet")

        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("🔒 Wallet Encryption" if self.mode == 'encrypt' else "🔓 Wallet Decryption")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        if self.mode == 'encrypt':
            description = QLabel(
                "Enter a strong password to encrypt your wallet.\n"
                "This password will be required to decrypt the wallet later.\n\n"
                "⚠️ WARNING: If you lose this password, your wallet cannot be recovered!"
            )
        else:
            description = QLabel(
                f"Enter the password to decrypt:\n{self.filename}\n\n"
                "The wallet is encrypted and requires the correct password."
            )
        description.setWordWrap(True)
        description.setStyleSheet("color: #555; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(description)

        # Password input
        password_label = QLabel("Password:")
        password_label.setFont(QFont("", 10, QFont.Weight.Bold))
        layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.setPlaceholderText("Enter password...")
        self.password_input.textChanged.connect(self.on_password_changed)
        self.password_input.returnPressed.connect(self.accept_if_valid)
        layout.addWidget(self.password_input)

        # Confirm password (only for encryption)
        if self.mode == 'encrypt':
            confirm_label = QLabel("Confirm Password:")
            confirm_label.setFont(QFont("", 10, QFont.Weight.Bold))
            layout.addWidget(confirm_label)

            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setMinimumHeight(35)
            self.confirm_input.setPlaceholderText("Re-enter password...")
            self.confirm_input.textChanged.connect(self.on_password_changed)
            self.confirm_input.returnPressed.connect(self.accept_if_valid)
            layout.addWidget(self.confirm_input)

            # Password match indicator
            self.match_label = QLabel("")
            self.match_label.setStyleSheet("font-size: 11px;")
            layout.addWidget(self.match_label)

        # Show password checkbox
        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_cb)

        layout.addSpacing(10)

        # Buttons
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.ok_btn = QPushButton("Encrypt" if self.mode == 'encrypt' else "Decrypt")
        self.ok_btn.setMinimumHeight(35)
        self.ok_btn.setEnabled(False)
        button_font = QFont()
        button_font.setBold(True)
        self.ok_btn.setFont(button_font)
        self.ok_btn.clicked.connect(self.accept_password)
        btn_layout.addWidget(self.ok_btn)

        layout.addLayout(btn_layout)

        # Focus on password input
        self.password_input.setFocus()

    def on_password_changed(self):
        """Handle password input changes."""
        password = self.password_input.text()

        if self.mode == 'encrypt':
            confirm = self.confirm_input.text()

            # Check password strength
            if len(password) == 0:
                self.match_label.setText("")
                self.ok_btn.setEnabled(False)
            elif len(password) < 8:
                self.match_label.setText("⚠️ Password too short (minimum 8 characters)")
                self.match_label.setStyleSheet("color: orange; font-size: 11px;")
                self.ok_btn.setEnabled(False)
            elif password != confirm:
                self.match_label.setText("❌ Passwords do not match")
                self.match_label.setStyleSheet("color: red; font-size: 11px;")
                self.ok_btn.setEnabled(False)
            else:
                self.match_label.setText("✅ Passwords match")
                self.match_label.setStyleSheet("color: green; font-size: 11px;")
                self.ok_btn.setEnabled(True)
        else:
            # Decrypt mode - just check if password is not empty
            self.ok_btn.setEnabled(len(password) > 0)

    def toggle_password_visibility(self, state):
        """Toggle password visibility."""
        if state == Qt.CheckState.Checked.value:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            if self.mode == 'encrypt':
                self.confirm_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            if self.mode == 'encrypt':
                self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)

    def accept_if_valid(self):
        """Accept dialog if password is valid."""
        if self.ok_btn.isEnabled():
            self.accept_password()

    def accept_password(self):
        """Accept the dialog and store the password."""
        self.password = self.password_input.text()
        self.accept()

    def get_password(self) -> str:
        """
        Get the entered password.

        Returns:
            The password string, or None if dialog was cancelled
        """
        return self.password
