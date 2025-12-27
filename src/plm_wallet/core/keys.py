"""Key management and serialization."""

from ..crypto.ecc import private_to_public
from ..crypto.encoding import base58_encode_check
from ..crypto.hashing import hash160
from ..config.constants import ZPRV_VERSION, ZPUB_VERSION


def serialize_extended_key(key: bytes, chain_code: bytes, depth: int, fingerprint: bytes,
                            child_number: int, is_private: bool) -> str:
    """
    Serialize extended key in base58check format (zprv/zpub).

    Args:
        key: Private or public key (32 bytes)
        chain_code: Chain code (32 bytes)
        depth: Depth in derivation path
        fingerprint: Parent fingerprint (4 bytes)
        child_number: Child number
        is_private: True for private key, False for public key

    Returns:
        Base58check encoded extended key (zprv or zpub)
    """
    if is_private:
        version = ZPRV_VERSION.to_bytes(4, 'big')
        key_data = b'\x00' + key
    else:
        # Calculate compressed public key
        pubkey = private_to_public(key)
        key_data = pubkey
        version = ZPUB_VERSION.to_bytes(4, 'big')

    raw = (version +
           bytes([depth]) +
           fingerprint +
           child_number.to_bytes(4, 'big') +
           chain_code +
           key_data)

    return base58_encode_check(raw)


def get_pubkey_fingerprint(private_key: bytes) -> bytes:
    """
    Calculate public key fingerprint (first 4 bytes of hash160).

    Args:
        private_key: 32-byte private key

    Returns:
        4-byte fingerprint
    """
    pubkey = private_to_public(private_key)
    return hash160(pubkey)[:4]
