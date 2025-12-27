"""Main CLI entry point."""

from plm_wallet.wallet.wallet import PLMWallet
from .prompts import prompt_word_count, prompt_standard, prompt_save_wallet
from .output import print_wallet_info, save_to_json


def main():
    """Main CLI function."""
    print("=== Generatore Wallet HD ===\n")

    try:
        # Prompt for word count
        word_count = prompt_word_count()

        # Prompt for standard
        standard = prompt_standard()

        # Generate wallet
        wallet = PLMWallet.generate(word_count, standard)

        # Export wallet data
        wallet_data = wallet.export_json()

        # Display results
        print_wallet_info(wallet_data)

        # Prompt to save
        should_save, filename = prompt_save_wallet()
        if should_save:
            save_to_json(wallet_data, filename)

    except ImportError as e:
        print(f"Errore: {e}")
    except Exception as e:
        print(f"Errore: {e}")


if __name__ == '__main__':
    main()
