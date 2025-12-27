"""Seed generation from mnemonic."""

import hashlib
from ..utils.text import normalize_text


def mnemonic_to_seed(mnemonic: str, passphrase: str = "", electrum: bool = False) -> bytes:
    """
    Convert mnemonic to seed using PBKDF2.

    Args:
        mnemonic: Mnemonic phrase
        passphrase: Optional passphrase
        electrum: Use Electrum standard if True, BIP39 otherwise

    Returns:
        64-byte seed
    """
    if electrum:
        # Electrum normalizes text before conversion
        mnemonic = normalize_text(mnemonic)
        passphrase = normalize_text(passphrase) if passphrase else ''
        # Electrum uses "electrum" + passphrase as salt
        salt = (b'electrum' + passphrase.encode('utf-8'))
    else:
        # BIP39 uses "mnemonic" + passphrase as salt
        salt = ("mnemonic" + passphrase).encode('utf-8')

    return hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), salt, 2048)
