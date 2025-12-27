"""Elliptic curve cryptography operations."""

import ecdsa


def private_to_public(private_key: bytes) -> bytes:
    """
    Convert private key to compressed public key.

    Args:
        private_key: 32-byte private key

    Returns:
        33-byte compressed public key
    """
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pubkey_bytes = vk.to_string()
    x = pubkey_bytes[:32]
    y = pubkey_bytes[32:]

    # Compress public key
    prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
    return prefix + x


def get_public_key_uncompressed(private_key: bytes) -> tuple[bytes, bytes]:
    """
    Get uncompressed public key coordinates.

    Args:
        private_key: 32-byte private key

    Returns:
        Tuple of (x, y) coordinates (32 bytes each)
    """
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pubkey_bytes = vk.to_string()
    x = pubkey_bytes[:32]
    y = pubkey_bytes[32:]
    return x, y
