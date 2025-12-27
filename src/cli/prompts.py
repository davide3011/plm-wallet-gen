"""Interactive prompts for CLI."""

from plm_wallet.config.constants import VALID_WORD_COUNTS


def prompt_word_count() -> int:
    """
    Prompt user for mnemonic word count.

    Returns:
        Selected word count
    """
    print("Quante parole vuoi usare per il mnemonic?")
    print("Opzioni: 12, 15, 18, 21, 24")
    while True:
        try:
            word_count = int(input("Numero parole: ").strip())
            if word_count in VALID_WORD_COUNTS:
                return word_count
            print("Valore non valido. Scegli tra: 12, 15, 18, 21, 24")
        except ValueError:
            print("Inserisci un numero valido.")


def prompt_standard() -> str:
    """
    Prompt user for mnemonic standard.

    Returns:
        'bip39' or 'electrum'
    """
    print("\nQuale standard vuoi usare?")
    print("1. BIP39 (compatibile con la maggior parte dei wallet)")
    print("2. Electrum (standard Electrum segwit)")
    while True:
        choice = input("Scelta (1/2): ").strip()
        if choice == "1":
            return "bip39"
        elif choice == "2":
            return "electrum"
        print("Scelta non valida. Inserisci 1 o 2.")


def prompt_save_wallet() -> tuple[bool, str]:
    """
    Prompt user if they want to save wallet.

    Returns:
        Tuple of (save, filename)
    """
    save = input("\nVuoi salvare i dati in un file? (s/n): ").strip().lower()
    if save == 's':
        filename = input("Nome file (senza estensione): ").strip()
        if not filename:
            filename = "wallet"
        if not filename.endswith('.json'):
            filename += '.json'
        return True, filename
    return False, ""
