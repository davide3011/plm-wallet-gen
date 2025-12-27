"""Interactive prompts for CLI."""

from plm_wallet.config.constants import VALID_WORD_COUNTS


def prompt_word_count() -> int:
    """
    Prompt user for mnemonic word count.

    Returns:
        Selected word count
    """
    print("How many words do you want for the mnemonic?")
    print("Options: 12, 15, 18, 21, 24")
    while True:
        try:
            word_count = int(input("Number of words: ").strip())
            if word_count in VALID_WORD_COUNTS:
                return word_count
            print("Invalid value. Choose from: 12, 15, 18, 21, 24")
        except ValueError:
            print("Please enter a valid number.")


def prompt_standard() -> str:
    """
    Prompt user for mnemonic standard.

    Returns:
        'bip39' or 'electrum'
    """
    print("\nWhich standard do you want to use?")
    print("1. BIP39 (compatible with most wallets)")
    print("2. Electrum (Electrum segwit standard)")
    while True:
        choice = input("Choice (1/2): ").strip()
        if choice == "1":
            return "bip39"
        elif choice == "2":
            return "electrum"
        print("Invalid choice. Enter 1 or 2.")


def prompt_save_wallet() -> tuple[bool, str]:
    """
    Prompt user if they want to save wallet.

    Returns:
        Tuple of (save, filename)
    """
    save = input("\nDo you want to save the data to a file? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("Filename (without extension): ").strip()
        if not filename:
            filename = "wallet"
        if not filename.endswith('.json'):
            filename += '.json'
        return True, filename
    return False, ""
