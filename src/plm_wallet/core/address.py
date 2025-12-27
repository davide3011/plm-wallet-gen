"""Address generation."""

from ..crypto.ecc import private_to_public
from ..crypto.hashing import hash160
from ..crypto.encoding import bech32_encode_address
from ..config.constants import HRP


def private_key_to_address(private_key: bytes, hrp: str = HRP) -> str:
    """
    Generate bech32 address from private key.

    Args:
        private_key: 32-byte private key
        hrp: Human-readable part (default: 'plm')

    Returns:
        Bech32 encoded address
    """
    # Get compressed public key
    pubkey = private_to_public(private_key)

    # Generate witness program (hash160 of pubkey)
    witprog = hash160(pubkey)

    # Encode as bech32
    return bech32_encode_address(hrp, witprog)
