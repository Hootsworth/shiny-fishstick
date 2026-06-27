import os

from cryptography.fernet import Fernet

_fernet_instance = None

def get_fernet() -> Fernet:
    global _fernet_instance
    if _fernet_instance is not None:
        return _fernet_instance

    key = os.environ.get("SHINY_FISHSTICK_ENCRYPTION_KEY")
    if key:
        if isinstance(key, str):
            key = key.encode("utf-8")
        _fernet_instance = Fernet(key)
        return _fernet_instance

    # Fallback to local file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
    key_file = os.path.join(project_root, ".encryption.key")

    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            key = f.read().strip()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        print(f"[Security] Generated new local encryption key and saved to: {key_file}")

    _fernet_instance = Fernet(key)
    return _fernet_instance

def encrypt_data(plain_text: str) -> str:
    if not plain_text:
        return ""
    fernet = get_fernet()
    cipher_bytes = fernet.encrypt(plain_text.encode("utf-8"))
    return cipher_bytes.decode("utf-8")

def decrypt_data(cipher_text: str) -> str:
    if not cipher_text:
        return ""
    fernet = get_fernet()
    plain_bytes = fernet.decrypt(cipher_text.encode("utf-8"))
    return plain_bytes.decode("utf-8")
