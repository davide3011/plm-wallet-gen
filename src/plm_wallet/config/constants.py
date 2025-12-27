"""Constants for PLM wallet generation."""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
WALLETS_DIR = PROJECT_ROOT / "wallets"

# Palladium specific
COIN_TYPE = 746
HRP = 'plm'

# Derivation paths
BIP84_PATH = "m/84h/746h/0h"
ELECTRUM_PATH = "m/0h"

# Mnemonic
VALID_WORD_COUNTS = [12, 15, 18, 21, 24]

# BIP84 versions (zpub/zprv)
ZPRV_VERSION = 0x04B2430C
ZPUB_VERSION = 0x04B24746
