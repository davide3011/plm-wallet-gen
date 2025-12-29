# PLM Wallet Generator

A proper HD (Hierarchical Deterministic) wallet generator for Palladium cryptocurrency.

## What This Does

Generates BIP39/Electrum-compatible wallets for PLM (Palladium). Nothing fancy, just clean implementation of the standard cryptographic algorithms. You get:

- Proper mnemonic generation (BIP39 or Electrum)
- Correct key derivation (BIP84 standard at m/84h/746h/0h)
- Native SegWit addresses with `plm` prefix (bech32)
- Optional AES-128 encryption for wallet files

The code is transparent. You can read exactly what it's doing. No magic, no bullshit.

## Installation

You need Python 3.8 or newer. If you're still on Python 2, what are you doing?

```bash
# Clone it

# Virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### GUI Version (If You Like Clicking Things)

```bash
python run_gui.py
```

The GUI does what you'd expect:
- Generate wallets with a few clicks
- Open saved wallets
- Copy addresses/keys to clipboard
- Save wallets (with optional encryption)

If you can't figure out the GUI, I can't help you.

### CLI Version

```bash
python run.py
```

Follow the prompts. Pick your mnemonic length, pick your standard, done.

## Security - Read This Part

Let's be clear about a few things:

### Your Mnemonic is Everything

Your mnemonic phrase **IS** your wallet. Anyone who has it owns your coins. Period.

- Don't store it on your computer unencrypted
- Don't take a screenshot of it
- Don't email it to yourself
- Write it on paper. Multiple copies. Different locations.

### About Encryption

The encryption feature uses **Fernet** (AES-128-CBC + HMAC-SHA256). Industry standard, battle-tested, nothing exotic. Key derivation uses PBKDF2-HMAC-SHA256 with 480,000 iterations because that's what OWASP recommends in 2024.

**Critical point**: If you lose the password, the wallet is gone. Forever. There is no "forgot password" button. There is no recovery. There is no customer support. This is cryptography, not Facebook.

Choose a strong password. Use a password manager. Don't be clever.

### Encrypted vs Unencrypted Files

**Encrypted file format:**
```json
{
  "version": "1",
  "salt": "base64-random-salt",
  "data": "encrypted-blob"
}
```

**Unencrypted file format:**
```json
{
  "mnemonic": "your twelve or more words",
  "standard": "BIP39",
  "derivation_path": "m/84h/746h/0h",
  "master_zprv": "master-private-key",
  "master_zpub": "master-public-key",
  "zprv": "account-private-key",
  "zpub": "account-public-key",
  "addresses": [
    {
      "path": "m/84h/746h/0h/0/0",
      "address": "plm1q...",
      "pubkey": "02...",
      "privkey": "..."
    }
  ]
}
```

The files in the `wallets/` directory are already in `.gitignore`. Don't remove that unless you want your private keys on GitHub.

## Wallet Encryption

### Encrypting a Wallet

1. Generate or open a wallet
2. Click "Save to JSON"
3. When asked "Encrypt wallet?", say yes
4. Enter password (minimum 8 characters, but use more)
5. Confirm password
6. Done

The encrypted file uses AES-128. The salt is random for each file. The password goes through 480,000 rounds of PBKDF2. This is secure if your password isn't "password123".

### Opening an Encrypted Wallet

1. Select the encrypted file
2. Enter password
3. Done

### Command-Line Encryption (Programmatic)

If you want to script this:

```python
from plm_wallet.crypto.encryption import WalletEncryption
import json

# Load wallet
with open("wallet.json") as f:
    wallet = json.load(f)

# Encrypt
encrypted = WalletEncryption.encrypt_wallet(wallet, "strong-password-here")

# Save
with open("wallet_encrypted.json", "w") as f:
    json.dump(encrypted, f, indent=2)

# Decrypt (when needed)
with open("wallet_encrypted.json") as f:
    encrypted = json.load(f)

wallet = WalletEncryption.decrypt_wallet(encrypted, "strong-password-here")
```

## Technical Details

### Standards Compliance

- **BIP39**: Mnemonic generation with proper entropy and checksum
- **BIP32**: HD key derivation (the actual hierarchical deterministic part)
- **BIP44/BIP84**: Derivation paths (we use BIP84 for native SegWit)
- **Bech32**: Address encoding with PLM prefix (not Bitcoin's `bc1`)

### Cryptography Stack

- **Mnemonic**: PBKDF2-HMAC-SHA512 (BIP39 standard)
- **Key derivation**: HMAC-SHA512 (BIP32 standard)
- **Signatures**: ECDSA secp256k1 (Bitcoin-compatible)
- **Encryption**: Fernet (AES-128-CBC + HMAC-SHA256)
- **KDF for encryption**: PBKDF2-HMAC-SHA256, 480k iterations

## Dependencies

All standard libraries that do one thing and do it well:

- `mnemonic` - BIP39 implementation
- `ecdsa` - Elliptic curve operations
- `base58` - Base58 encoding (Bitcoin-style)
- `bech32` - Bech32 encoding (SegWit addresses)
- `cryptography` - Fernet encryption (from PyCA)
- `PyQt6` - GUI framework (optional, only for GUI)

See `requirements.txt` for versions.

## Configuration

Optional `.env` file if you want to change defaults:

```bash
# Number of addresses to generate (default: 10)
DEFAULT_ADDRESS_COUNT=20

# Derivation path (default: m/84h/746h/0h)
DERIVATION_PATH=m/84h/746h/0h

# Bech32 prefix (default: plm)
BECH32_HRP=plm
```

Don't change `BECH32_HRP` unless you know what you're doing.

## Common Issues

### "Import Error" / "Module not found"

You didn't install dependencies. Read the installation section again.

### "Cannot decrypt wallet" / "Invalid password"

You typed the wrong password. Or the file is corrupted. Or cosmic rays flipped a bit. Probably the first one.

### GUI doesn't start on Linux

You need PyQt6 system dependencies. On Ubuntu/Debian:

```bash
sudo apt-get install python3-pyqt6
```

Or just use the CLI version.

## FAQ

**Q: Can I use this for other cryptocurrencies?**
A: No. It's hardcoded for PLM. Fork it if you want something else.

**Q: Can you add feature X?**
A: Probably not. This does what it needs to do.

**Q: Is this secure?**
A: The cryptography is standard. The implementation is straightforward. The security depends on your password strength and how you handle your mnemonic. Don't be stupid and it's secure enough.

**Q: I lost my password, can you recover it?**
A: No. That's the entire point of encryption.

**Q: Why AES-128 and not AES-256?**
A: Because Fernet uses AES-128 and it's perfectly fine. AES-128 is not "weak". If you think you need AES-256, you don't understand cryptography.

**Q: Can I trust this?**
A: Read the code. It's not that long. Trust is earned by inspection, not by asking.

## License

MIT License. Do what you want with it. See `LICENSE` file.

## Credits

Built following Bitcoin Improvement Proposals (BIPs) and standard cryptographic practices. No reinvented wheels here.

---

**Remember**: Your mnemonic is your money. Protect it like you'd protect your bank vault key. Actually, protect it better, because banks have insurance and Bitcoin doesn't.

If you lose your mnemonic or forget your password, your coins are gone. This is not a bug, it's how cryptography works. Nobody can help you. Not me, not your government, not God himself.

You have been warned.
