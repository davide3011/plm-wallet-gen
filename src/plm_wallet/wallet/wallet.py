"""PLM Wallet orchestration."""

from typing import List
from ..core.mnemonic import generate_bip39, generate_electrum
from ..core.seed import mnemonic_to_seed
from ..core.derivation import derive_path
from ..config.constants import BIP84_PATH, ELECTRUM_PATH
from .generator import derive_addresses


class PLMWallet:
    """Main wallet class for PLM."""

    def __init__(self, mnemonic: str, passphrase: str = "", standard: str = "bip39"):
        """
        Initialize wallet from mnemonic.

        Args:
            mnemonic: Mnemonic phrase
            passphrase: Optional passphrase
            standard: 'bip39' or 'electrum'
        """
        self.mnemonic = mnemonic
        self.passphrase = passphrase
        self.standard = standard.lower()

        # Determine if using Electrum
        use_electrum = self.standard == "electrum"

        # Generate seed
        self.seed = mnemonic_to_seed(mnemonic, passphrase, use_electrum)

        # Choose derivation path
        self.derivation_path = ELECTRUM_PATH if use_electrum else BIP84_PATH

        # Derive keys
        self.keys = derive_path(self.seed, self.derivation_path)

    @classmethod
    def generate(cls, word_count: int, standard: str = "bip39", passphrase: str = ""):
        """
        Generate new wallet.

        Args:
            word_count: Number of words (12, 15, 18, 21, or 24)
            standard: 'bip39' or 'electrum'
            passphrase: Optional passphrase

        Returns:
            New PLMWallet instance
        """
        standard = standard.lower()
        if standard == "electrum":
            mnemonic = generate_electrum(word_count)
        else:
            mnemonic = generate_bip39(word_count)

        return cls(mnemonic, passphrase, standard)

    def get_master_keys(self) -> dict:
        """Get master extended keys."""
        return {
            'master_zprv': self.keys['master_zprv'],
            'master_zpub': self.keys['master_zpub']
        }

    def get_account_keys(self) -> dict:
        """Get account-level extended keys."""
        return {
            'zprv': self.keys['zprv'],
            'zpub': self.keys['zpub']
        }

    def generate_addresses(self, count: int = 10) -> List[dict]:
        """
        Generate addresses.

        Args:
            count: Number of addresses to generate

        Returns:
            List of dictionaries with 'path' and 'address'
        """
        return derive_addresses(
            self.keys['key'],
            self.keys['chain_code'],
            count,
            self.derivation_path
        )

    def export_json(self) -> dict:
        """
        Export wallet data as dictionary.

        Returns:
            Dictionary with all wallet data
        """
        return {
            'standard': self.standard.upper() if self.standard == "bip39" else "Electrum",
            'mnemonic': self.mnemonic,
            'master_zprv': self.keys['master_zprv'],
            'master_zpub': self.keys['master_zpub'],
            'derivation_path': self.derivation_path,
            'zprv': self.keys['zprv'],
            'zpub': self.keys['zpub'],
            'addresses': self.generate_addresses(10)
        }
