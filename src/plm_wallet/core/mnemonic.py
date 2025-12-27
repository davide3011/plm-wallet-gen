"""Mnemonic generation (BIP39 and Electrum)."""

import secrets
import hashlib
import hmac
from mnemonic import Mnemonic
from ..config.constants import VALID_WORD_COUNTS
from ..utils.text import normalize_text


def entropy_bits_for_words(word_count: int) -> int:
    """
    Calculate entropy bits needed for given word count.

    Args:
        word_count: Number of words (12, 15, 18, 21, or 24)

    Returns:
        Entropy bits required
    """
    if word_count not in VALID_WORD_COUNTS:
        raise ValueError(f"Invalid word count. Must be one of {VALID_WORD_COUNTS}")
    return {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[word_count]


def generate_bip39(word_count: int) -> str:
    """
    Generate BIP39 mnemonic.

    Args:
        word_count: Number of words (12, 15, 18, 21, or 24)

    Returns:
        BIP39 mnemonic phrase
    """
    mnemo = Mnemonic("english")
    entropy_bits = entropy_bits_for_words(word_count)
    return mnemo.generate(entropy_bits)


def generate_electrum(word_count: int) -> str:
    """
    Generate Electrum-compatible mnemonic (segwit native).

    Args:
        word_count: Number of words (12, 15, 18, 21, or 24)

    Returns:
        Electrum mnemonic phrase
    """
    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist

    # Electrum generates mnemonic and verifies hash starts with "100" for segwit
    while True:
        entropy_bits = entropy_bits_for_words(word_count)
        entropy = secrets.token_bytes(entropy_bits // 8)

        # Generate words from entropy
        h = hashlib.sha256(entropy).digest()
        b = (int.from_bytes(entropy, 'big') << 256 - entropy_bits) | (int.from_bytes(h, 'big') >> entropy_bits)

        words = []
        for i in range(word_count):
            idx = (b >> (11 * (word_count - 1 - i))) & 0x7FF
            words.append(wordlist[idx % len(wordlist)])

        mnemonic = " ".join(words)

        # Verify Electrum prefix for segwit native (0x100)
        normalized = normalize_text(mnemonic)
        hm = hmac.new(b"Seed version", normalized.encode('utf-8'), hashlib.sha512).hexdigest()
        if hm.startswith("100"):
            return mnemonic
