"""Wallet encryption using Fernet (AES-128 in CBC mode with HMAC authentication)."""

import base64
import json
from typing import Dict, Any
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .exceptions import EncryptionError, DecryptionError, InvalidPasswordError


class WalletEncryption:
    """
    Handles wallet encryption and decryption using Fernet.

    Fernet guarantees that a message encrypted using it cannot be
    manipulated or read without the key. It uses:
    - AES in CBC mode with a 128-bit key for encryption
    - PKCS7 padding
    - HMAC using SHA256 for authentication
    - Initialization vectors are generated using os.urandom()
    """

    # Number of iterations for PBKDF2 (higher = more secure but slower)
    PBKDF2_ITERATIONS = 480000  # OWASP recommendation for 2023+

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """
        Derive a cryptographic key from a password using PBKDF2.

        Args:
            password: User password
            salt: Cryptographic salt (16 bytes)

        Returns:
            32-byte key suitable for Fernet
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=WalletEncryption.PBKDF2_ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

    @staticmethod
    def encrypt_wallet(wallet_data: Dict[str, Any], password: str) -> Dict[str, str]:
        """
        Encrypt wallet data with a password.

        Args:
            wallet_data: Wallet dictionary to encrypt
            password: Password for encryption

        Returns:
            Dictionary containing encrypted data and salt

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Generate a random salt
            import os
            salt = os.urandom(16)

            # Derive encryption key from password
            key = WalletEncryption._derive_key(password, salt)

            # Create Fernet cipher
            fernet = Fernet(key)

            # Convert wallet data to JSON and encrypt
            json_data = json.dumps(wallet_data, indent=2)
            encrypted_data = fernet.encrypt(json_data.encode('utf-8'))

            # Return encrypted data with salt (both base64 encoded for JSON storage)
            return {
                'version': '1',  # Version for future compatibility
                'salt': base64.b64encode(salt).decode('utf-8'),
                'data': encrypted_data.decode('utf-8')
            }

        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}") from e

    @staticmethod
    def decrypt_wallet(encrypted_wallet: Dict[str, str], password: str) -> Dict[str, Any]:
        """
        Decrypt wallet data with a password.

        Args:
            encrypted_wallet: Dictionary containing encrypted data and salt
            password: Password for decryption

        Returns:
            Decrypted wallet dictionary

        Raises:
            InvalidPasswordError: If the password is incorrect
            DecryptionError: If decryption fails for other reasons
        """
        try:
            # Extract salt and encrypted data
            salt = base64.b64decode(encrypted_wallet['salt'])
            encrypted_data = encrypted_wallet['data'].encode('utf-8')

            # Derive the same key from password and salt
            key = WalletEncryption._derive_key(password, salt)

            # Create Fernet cipher
            fernet = Fernet(key)

            # Decrypt and parse JSON
            try:
                decrypted_data = fernet.decrypt(encrypted_data)
                wallet_data = json.loads(decrypted_data.decode('utf-8'))
                return wallet_data

            except InvalidToken:
                raise InvalidPasswordError("Incorrect password or corrupted data")

        except InvalidPasswordError:
            raise
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}") from e

    @staticmethod
    def is_encrypted(data: Dict[str, Any]) -> bool:
        """
        Check if wallet data is encrypted.

        Args:
            data: Dictionary to check

        Returns:
            True if data appears to be encrypted
        """
        return 'version' in data and 'salt' in data and 'data' in data
