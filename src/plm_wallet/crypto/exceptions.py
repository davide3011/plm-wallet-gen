"""Custom exceptions for wallet encryption."""


class EncryptionError(Exception):
    """Base exception for encryption-related errors."""
    pass


class DecryptionError(Exception):
    """Raised when decryption fails."""
    pass


class InvalidPasswordError(DecryptionError):
    """Raised when the password is incorrect."""
    pass
