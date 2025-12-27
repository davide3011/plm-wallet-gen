"""Encoding utilities for Base58 and Bech32."""

import hashlib
import base58
from bech32 import bech32_encode, convertbits


def base58_encode_check(data: bytes) -> str:
    """
    Base58Check encoding.

    Args:
        data: Data to encode

    Returns:
        Base58Check encoded string
    """
    checksum = hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]
    return base58.b58encode(data + checksum).decode()


def bech32_encode_address(hrp: str, witprog: bytes) -> str:
    """
    Encode a bech32 address.

    Args:
        hrp: Human-readable part (e.g., 'plm')
        witprog: Witness program (20 bytes for P2WPKH)

    Returns:
        Bech32 encoded address
    """
    converted = convertbits(list(witprog), 8, 5)
    data = [0] + converted
    return bech32_encode(hrp, data)
