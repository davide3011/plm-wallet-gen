"""Text normalization utilities."""

import unicodedata


def normalize_text(text: str) -> str:
    """
    Normalize text according to Electrum standard (NFKD, lowercase, remove accents).

    Args:
        text: Input text to normalize

    Returns:
        Normalized text
    """
    # Normalize to NFKD
    text = unicodedata.normalize('NFKD', text)
    # Lowercase
    text = text.lower()
    # Remove accents (combining characters)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    # Normalize whitespaces
    text = ' '.join(text.split())
    return text
