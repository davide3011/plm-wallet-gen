import json
import secrets
import hashlib
import hmac
from typing import Tuple

# BIP39 wordlist (English)
try:
    from mnemonic import Mnemonic
    HAS_MNEMONIC = True
except ImportError:
    HAS_MNEMONIC = False


VALID_WORD_COUNTS = [12, 15, 18, 21, 24]
DERIVATION_PATH = "m/84h/746h/0h"

def entropy_bits_for_words(word_count: int) -> int:
    """Calcola i bit di entropia necessari per il numero di parole."""
    return {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}[word_count]

def generate_bip39_mnemonic(word_count: int) -> str:
    """Genera mnemonic BIP39."""
    if not HAS_MNEMONIC:
        raise ImportError("Libreria 'mnemonic' non installata. Esegui: pip install mnemonic")

    mnemo = Mnemonic("english")
    entropy_bits = entropy_bits_for_words(word_count)
    return mnemo.generate(entropy_bits)

def generate_electrum_mnemonic(word_count: int) -> str:
    """Genera mnemonic standard Electrum (segwit)."""
    if not HAS_MNEMONIC:
        raise ImportError("Libreria 'mnemonic' non installata. Esegui: pip install mnemonic")

    mnemo = Mnemonic("english")
    wordlist = mnemo.wordlist

    # Electrum genera mnemonic e verifica che l'hash inizi con "01" per segwit
    while True:
        entropy_bits = entropy_bits_for_words(word_count)
        entropy = secrets.token_bytes(entropy_bits // 8)

        # Genera parole dall'entropia
        h = hashlib.sha256(entropy).digest()
        b = (int.from_bytes(entropy, 'big') << 256 - entropy_bits) | (int.from_bytes(h, 'big') >> entropy_bits)

        words = []
        for i in range(word_count):
            idx = (b >> (11 * (word_count - 1 - i))) & 0x7FF
            words.append(wordlist[idx % len(wordlist)])

        mnemonic = " ".join(words)

        # Verifica prefisso Electrum per segwit native (0x100)
        hm = hmac.new(b"Seed version", mnemonic.encode('utf-8'), hashlib.sha512).hexdigest()
        if hm.startswith("100"):
            return mnemonic

def mnemonic_to_seed(mnemonic: str, passphrase: str = "", electrum: bool = False) -> bytes:
    """Converte mnemonic in seed."""
    if electrum:
        # Electrum usa "electrum" + passphrase come salt
        salt = ("electrum" + passphrase).encode('utf-8')
    else:
        # BIP39 usa "mnemonic" + passphrase come salt
        salt = ("mnemonic" + passphrase).encode('utf-8')

    return hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), salt, 2048)

def derive_master_keys(seed: bytes) -> Tuple[bytes, bytes]:
    """Deriva master key e chain code dal seed."""
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    master_key = I[:32]
    chain_code = I[32:]
    return master_key, chain_code

def serialize_extended_key(key: bytes, chain_code: bytes, depth: int, fingerprint: bytes,
                           child_number: int, is_private: bool) -> str:
    """Serializza una chiave estesa in formato base58check."""
    import base58
    import ecdsa

    if is_private:
        version = bytes.fromhex("04B2430C")  # zprv (BIP84)
        key_data = b'\x00' + key
    else:
        # Calcola chiave pubblica
        sk = ecdsa.SigningKey.from_string(key, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        pubkey_bytes = vk.to_string()
        x = pubkey_bytes[:32]
        y = pubkey_bytes[32:]
        prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
        key_data = prefix + x
        version = bytes.fromhex("04B24746")  # zpub (BIP84)

    raw = (version +
           bytes([depth]) +
           fingerprint +
           child_number.to_bytes(4, 'big') +
           chain_code +
           key_data)

    checksum = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[:4]
    return base58.b58encode(raw + checksum).decode()

def derive_hardened_child(parent_key: bytes, parent_chain_code: bytes, index: int) -> Tuple[bytes, bytes]:
    """Deriva una chiave figlio hardened."""
    import ecdsa

    # Per derivazione hardened, index >= 0x80000000
    index = index | 0x80000000

    data = b'\x00' + parent_key + index.to_bytes(4, 'big')
    I = hmac.new(parent_chain_code, data, hashlib.sha512).digest()

    child_key_int = (int.from_bytes(I[:32], 'big') + int.from_bytes(parent_key, 'big')) % ecdsa.SECP256k1.order
    child_key = child_key_int.to_bytes(32, 'big')
    child_chain_code = I[32:]

    return child_key, child_chain_code

def derive_normal_child(parent_key: bytes, parent_chain_code: bytes, index: int) -> Tuple[bytes, bytes]:
    """Deriva una chiave figlio normale (non-hardened)."""
    import ecdsa

    # Calcola chiave pubblica del parent
    sk = ecdsa.SigningKey.from_string(parent_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pubkey_bytes = vk.to_string()
    x = pubkey_bytes[:32]
    y = pubkey_bytes[32:]
    prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
    parent_pubkey = prefix + x

    data = parent_pubkey + index.to_bytes(4, 'big')
    I = hmac.new(parent_chain_code, data, hashlib.sha512).digest()

    child_key_int = (int.from_bytes(I[:32], 'big') + int.from_bytes(parent_key, 'big')) % ecdsa.SECP256k1.order
    child_key = child_key_int.to_bytes(32, 'big')
    child_chain_code = I[32:]

    return child_key, child_chain_code

def private_key_to_address(private_key: bytes) -> str:
    """Genera indirizzo bech32 da chiave privata."""
    import ecdsa
    from bech32 import bech32_encode, convertbits

    HRP = 'plm'

    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pubkey_bytes = vk.to_string()
    x = pubkey_bytes[:32]
    y = pubkey_bytes[32:]
    prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
    pubkey = prefix + x

    sha256_pubkey = hashlib.sha256(pubkey).digest()
    ripemd160 = hashlib.new('ripemd160', sha256_pubkey).digest()

    converted = convertbits(list(ripemd160), 8, 5)
    data = [0] + converted
    return bech32_encode(HRP, data)

def get_pubkey_fingerprint(private_key: bytes) -> bytes:
    """Calcola il fingerprint della chiave pubblica."""
    import ecdsa

    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    pubkey_bytes = vk.to_string()
    x = pubkey_bytes[:32]
    y = pubkey_bytes[32:]
    prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
    pubkey = prefix + x

    sha256_hash = hashlib.sha256(pubkey).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
    return ripemd160_hash[:4]

def derive_path(seed: bytes, path: str = DERIVATION_PATH) -> dict:
    """Deriva chiavi dal seed usando il path specificato."""
    master_key, master_chain_code = derive_master_keys(seed)

    # Master key serializzate
    master_xprv = serialize_extended_key(master_key, master_chain_code, 0, b'\x00\x00\x00\x00', 0, True)
    master_xpub = serialize_extended_key(master_key, master_chain_code, 0, b'\x00\x00\x00\x00', 0, False)

    # Parse path
    parts = path.replace("m/", "").split("/")

    current_key = master_key
    current_chain_code = master_chain_code
    parent_fingerprint = b'\x00\x00\x00\x00'
    depth = 0
    child_number = 0

    for part in parts:
        if part.endswith("h") or part.endswith("'"):
            index = int(part[:-1])
        else:
            index = int(part)

        parent_fingerprint = get_pubkey_fingerprint(current_key)
        current_key, current_chain_code = derive_hardened_child(current_key, current_chain_code, index)
        child_number = index | 0x80000000
        depth += 1

    xprv = serialize_extended_key(current_key, current_chain_code, depth, parent_fingerprint, child_number, True)
    xpub = serialize_extended_key(current_key, current_chain_code, depth, parent_fingerprint, child_number, False)

    return {
        'master_zprv': master_xprv,
        'master_zpub': master_xpub,
        'zprv': xprv,
        'zpub': xpub,
        'key': current_key,
        'chain_code': current_chain_code
    }

def derive_addresses(account_key: bytes, account_chain_code: bytes, count: int = 10) -> list:
    """Deriva i primi N indirizzi dal path m/84h/746h/0h/0/i."""
    # Deriva /0 (external chain)
    external_key, external_chain_code = derive_normal_child(account_key, account_chain_code, 0)

    addresses = []
    for i in range(count):
        child_key, _ = derive_normal_child(external_key, external_chain_code, i)
        address = private_key_to_address(child_key)
        addresses.append({
            'path': f"m/84h/746h/0h/0/{i}",
            'address': address
        })

    return addresses

def main():
    print("=== Generatore Wallet HD ===\n")

    # Scelta numero parole
    print("Quante parole vuoi usare per il mnemonic?")
    print("Opzioni: 12, 15, 18, 21, 24")
    while True:
        try:
            word_count = int(input("Numero parole: ").strip())
            if word_count in VALID_WORD_COUNTS:
                break
            print("Valore non valido. Scegli tra: 12, 15, 18, 21, 24")
        except ValueError:
            print("Inserisci un numero valido.")

    # Scelta standard
    print("\nQuale standard vuoi usare?")
    print("1. BIP39 (compatibile con la maggior parte dei wallet)")
    print("2. Electrum (standard Electrum segwit)")
    while True:
        choice = input("Scelta (1/2): ").strip()
        if choice in ["1", "2"]:
            use_electrum = choice == "2"
            break
        print("Scelta non valida. Inserisci 1 o 2.")

    try:
        # Genera mnemonic
        if use_electrum:
            mnemonic = generate_electrum_mnemonic(word_count)
            standard = "Electrum"
        else:
            mnemonic = generate_bip39_mnemonic(word_count)
            standard = "BIP39"

        # Genera seed
        seed = mnemonic_to_seed(mnemonic, "", use_electrum)

        # Deriva chiavi
        keys = derive_path(seed, DERIVATION_PATH)

        # Deriva primi 10 indirizzi
        addresses = derive_addresses(keys['key'], keys['chain_code'], 10)

        # Risultato
        result = {
            'standard': standard,
            'mnemonic': mnemonic,
            'master_zprv': keys['master_zprv'],
            'master_zpub': keys['master_zpub'],
            'derivation_path': DERIVATION_PATH,
            'zprv': keys['zprv'],
            'zpub': keys['zpub'],
            'addresses': addresses
        }

        print("\n" + "=" * 50)
        print(json.dumps(result, indent=4))
        print("=" * 50)

        # Salvataggio opzionale
        save = input("\nVuoi salvare i dati in un file? (s/n): ").strip().lower()
        if save == 's':
            filename = input("Nome file (senza estensione): ").strip()
            if not filename:
                filename = "wallet"
            if not filename.endswith('.json'):
                filename += '.json'
            with open(filename, 'w') as f:
                json.dump(result, f, indent=4)
            print(f"Salvato in: {filename}")

    except ImportError as e:
        print(f"Errore: {e}")
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == '__main__':
    main()
