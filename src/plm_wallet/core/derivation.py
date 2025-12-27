"""HD key derivation (BIP32)."""

import ecdsa
from typing import Tuple
from ..crypto.hashing import hmac_sha512
from ..crypto.ecc import private_to_public
from ..config.constants import BIP84_PATH
from .keys import serialize_extended_key, get_pubkey_fingerprint


def derive_master_keys(seed: bytes) -> Tuple[bytes, bytes]:
    """
    Derive master private key and chain code from seed.

    Args:
        seed: 64-byte seed

    Returns:
        Tuple of (master_key, chain_code)
    """
    I = hmac_sha512(b"Bitcoin seed", seed)
    master_key = I[:32]
    chain_code = I[32:]
    return master_key, chain_code


def derive_hardened_child(parent_key: bytes, parent_chain_code: bytes, index: int) -> Tuple[bytes, bytes]:
    """
    Derive hardened child key.

    Args:
        parent_key: Parent private key (32 bytes)
        parent_chain_code: Parent chain code (32 bytes)
        index: Child index (will be OR'd with 0x80000000)

    Returns:
        Tuple of (child_key, child_chain_code)
    """
    # For hardened derivation, index >= 0x80000000
    index = index | 0x80000000

    data = b'\x00' + parent_key + index.to_bytes(4, 'big')
    I = hmac_sha512(parent_chain_code, data)

    child_key_int = (int.from_bytes(I[:32], 'big') + int.from_bytes(parent_key, 'big')) % ecdsa.SECP256k1.order
    child_key = child_key_int.to_bytes(32, 'big')
    child_chain_code = I[32:]

    return child_key, child_chain_code


def derive_normal_child(parent_key: bytes, parent_chain_code: bytes, index: int) -> Tuple[bytes, bytes]:
    """
    Derive normal (non-hardened) child key.

    Args:
        parent_key: Parent private key (32 bytes)
        parent_chain_code: Parent chain code (32 bytes)
        index: Child index (< 0x80000000)

    Returns:
        Tuple of (child_key, child_chain_code)
    """
    # Calculate parent public key
    parent_pubkey = private_to_public(parent_key)

    data = parent_pubkey + index.to_bytes(4, 'big')
    I = hmac_sha512(parent_chain_code, data)

    child_key_int = (int.from_bytes(I[:32], 'big') + int.from_bytes(parent_key, 'big')) % ecdsa.SECP256k1.order
    child_key = child_key_int.to_bytes(32, 'big')
    child_chain_code = I[32:]

    return child_key, child_chain_code


def derive_path(seed: bytes, path: str = BIP84_PATH) -> dict:
    """
    Derive keys from seed using specified path.

    Args:
        seed: 64-byte seed
        path: Derivation path (e.g., "m/84h/746h/0h")

    Returns:
        Dictionary with master and derived keys
    """
    master_key, master_chain_code = derive_master_keys(seed)

    # Serialize master keys
    master_xprv = serialize_extended_key(master_key, master_chain_code, 0, b'\x00\x00\x00\x00', 0, True)
    master_xpub = serialize_extended_key(master_key, master_chain_code, 0, b'\x00\x00\x00\x00', 0, False)

    # Parse path
    parts = path.replace("m/", "").split("/")

    current_key = master_key
    current_chain_code = master_chain_code
    parent_fingerprint = b'\x00\x00\x00\x00'
    depth = 0
    child_number = 0

    for part in parts:
        if part.endswith("h") or part.endswith("'"):
            index = int(part[:-1])
        else:
            index = int(part)

        parent_fingerprint = get_pubkey_fingerprint(current_key)
        current_key, current_chain_code = derive_hardened_child(current_key, current_chain_code, index)
        child_number = index | 0x80000000
        depth += 1

    xprv = serialize_extended_key(current_key, current_chain_code, depth, parent_fingerprint, child_number, True)
    xpub = serialize_extended_key(current_key, current_chain_code, depth, parent_fingerprint, child_number, False)

    return {
        'master_zprv': master_xprv,
        'master_zpub': master_xpub,
        'zprv': xprv,
        'zpub': xpub,
        'key': current_key,
        'chain_code': current_chain_code
    }
