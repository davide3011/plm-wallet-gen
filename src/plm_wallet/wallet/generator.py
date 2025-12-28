"""Address generator."""

from typing import List
from ..core.derivation import derive_normal_child
from ..core.address import private_key_to_address
from ..crypto.ecc import private_to_public


def derive_addresses(account_key: bytes, account_chain_code: bytes,
                     count: int = 10, base_path: str = "") -> List[dict]:
    """
    Derive sequential addresses from account key.

    Args:
        account_key: Account-level private key
        account_chain_code: Account-level chain code
        count: Number of addresses to generate
        base_path: Base derivation path for display

    Returns:
        List of dictionaries with 'path', 'address', 'pubkey', and 'privkey'
    """
    # Derive /0 (external chain)
    external_key, external_chain_code = derive_normal_child(account_key, account_chain_code, 0)

    addresses = []
    for i in range(count):
        child_key, _ = derive_normal_child(external_key, external_chain_code, i)
        address = private_key_to_address(child_key)
        pubkey = private_to_public(child_key)
        addresses.append({
            'path': f"{base_path}/0/{i}",
            'address': address,
            'pubkey': pubkey.hex(),
            'privkey': child_key.hex()
        })

    return addresses
