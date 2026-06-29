import os

from cryptography.fernet import Fernet

_fernet_instance = None

import sys
from pathlib import Path


def get_fernet() -> Fernet:
    global _fernet_instance
    if _fernet_instance is not None:
        return _fernet_instance

    key_str = os.environ.get("SHINY_FISHSTICK_ENCRYPTION_KEY")
    if key_str:
        if isinstance(key_str, str):
            key = key_str.encode("utf-8")
        else:
            key = key_str

        # Validate key strength and format
        import base64
        try:
            decoded = base64.urlsafe_b64decode(key)
            if len(decoded) != 32:
                print("WARNING: SHINY_FISHSTICK_ENCRYPTION_KEY must be a 32-byte URL-safe base64 key. Using it may be insecure.", file=sys.stderr)
            if key_str in ["weak_secret_key", "default_key", "default_weak_key", "1234567890123456789012345678901234567890123="]:
                print("WARNING: SHINY_FISHSTICK_ENCRYPTION_KEY is using a weak or default secret key. Do not use this in production!", file=sys.stderr)
        except Exception:
            print("WARNING: SHINY_FISHSTICK_ENCRYPTION_KEY is not a valid base64 format.", file=sys.stderr)
    else:
        # Fallback to local file in project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
        key_path = Path(project_root) / ".encryption.key"

        if key_path.exists():
            key = key_path.read_bytes().strip()
        else:
            if os.getenv("ENV") == "production":
                print("ERROR: No encryption key in production. Set SHINY_FISHSTICK_ENCRYPTION_KEY.", file=sys.stderr)
                sys.exit(1)
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            print(f"[Security] Generated new local encryption key and saved to: {key_path}")

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
