# PLM Wallet Generator

HD (Hierarchical Deterministic) wallet generator for Palladium (PLM) supporting BIP39 and Electrum standards.

This tool provides full transparency in the wallet creation process, allowing users to verify and understand exactly how their Palladium wallets are generated following industry-standard cryptographic practices.

## Features

- BIP39 mnemonic generation (12, 15, 18, 21, 24 words)
- Electrum segwit mnemonic generation
- Key derivation following BIP84 (m/84h/746h/0h)
- Bech32 address generation with `plm` prefix
- Extended key export (zprv/zpub)
- Automatic derivation of the first 10 addresses

## Installation

### 1. Clone the repository

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (optional)

Create a `.env` file in the project root if you want to configure custom parameters:

```bash
# .env

# Default number of addresses to generate (default: 10)
DEFAULT_ADDRESS_COUNT=10

# Derivation path (default: m/84h/746h/0h)
DERIVATION_PATH=m/84h/746h/0h

# Human Readable Part for bech32 addresses (default: plm)
BECH32_HRP=plm
```

**Note**: The `.env` file is optional. The program works without it.

## Usage

Run the script:

```bash
python create_wallet.py
```

Follow the interactive prompts:
1. Choose the number of words for the mnemonic (12, 15, 18, 21, 24)
2. Choose the standard (BIP39 or Electrum)
3. View the results
4. Optionally save the data to a JSON file

## Output

The program generates:
- **Mnemonic**: recovery phrase
- **Master zprv/zpub**: master extended keys
- **Account zprv/zpub**: keys derived at path m/84h/746h/0h
- **Addresses**: first 10 addresses with their respective derivation paths

Example output:
```json
{
    "standard": "BIP39",
    "mnemonic": "word1 word2 word3 ...",
    "master_zprv": "zprv...",
    "master_zpub": "zpub...",
    "derivation_path": "m/84h/746h/0h",
    "zprv": "zprv...",
    "zpub": "zpub...",
    "addresses": [
        {
            "path": "m/84h/746h/0h/0/0",
            "address": "plm1..."
        },
        ...
    ]
}
```

## Security

⚠️ **WARNING**:
- **DO NOT share** your mnemonic or private keys (zprv)
- Generated JSON files contain sensitive information
- They are already configured in `.gitignore` to prevent accidental commits
- Keep a backup of your mnemonic in a secure, offline location

## Dependencies

- `mnemonic` - BIP39 mnemonic generation
- `ecdsa` - Elliptic curve cryptography
- `base58` - Base58 encoding
- `bech32` - Bech32 encoding for addresses

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.