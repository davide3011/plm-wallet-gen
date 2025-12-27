"""PLM Wallet Generator - HD wallet generator for Palladium."""

from .wallet.wallet import PLMWallet
from .config.constants import COIN_TYPE, HRP, BIP84_PATH, ELECTRUM_PATH, VALID_WORD_COUNTS
from .core.mnemonic import generate_bip39, generate_electrum

__version__ = "2.0.0"
__all__ = [
    'PLMWallet',
    'COIN_TYPE',
    'HRP',
    'BIP84_PATH',
    'ELECTRUM_PATH',
    'VALID_WORD_COUNTS',
    'generate_bip39',
    'generate_electrum',
]
