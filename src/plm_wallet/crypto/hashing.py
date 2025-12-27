"""Hashing utilities."""

import hashlib
import hmac


def sha256(data: bytes) -> bytes:
    """SHA256 hash."""
    return hashlib.sha256(data).digest()


def ripemd160(data: bytes) -> bytes:
    """RIPEMD160 hash."""
    return hashlib.new('ripemd160', data).digest()


def hash160(data: bytes) -> bytes:
    """SHA256 followed by RIPEMD160."""
    return ripemd160(sha256(data))


def hmac_sha512(key: bytes, data: bytes) -> bytes:
    """HMAC-SHA512."""
    return hmac.new(key, data, hashlib.sha512).digest()
