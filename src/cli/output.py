"""Output formatting and file saving."""

import json
from pathlib import Path
from plm_wallet.config.constants import WALLETS_DIR


def print_wallet_info(wallet_data: dict):
    """
    Print wallet information to console.

    Args:
        wallet_data: Wallet data dictionary
    """
    print("\n" + "=" * 50)
    print(json.dumps(wallet_data, indent=4))
    print("=" * 50)


def save_to_json(wallet_data: dict, filename: str):
    """
    Save wallet data to JSON file in wallets/ directory.

    Args:
        wallet_data: Wallet data dictionary
        filename: Filename (e.g., 'wallet.json')
    """
    # Ensure wallets directory exists
    WALLETS_DIR.mkdir(exist_ok=True)

    # Save to wallets/ directory
    filepath = WALLETS_DIR / filename

    with open(filepath, 'w') as f:
        json.dump(wallet_data, f, indent=4)

    print(f"Saved to: {filepath}")
