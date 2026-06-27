from backend.app.core.security import decrypt_data, encrypt_data


def test_encryption_roundtrip():
    plain_text = "my-secure-password-123!"
    cipher = encrypt_data(plain_text)
    assert cipher != plain_text
    assert cipher.startswith("gAAAAA")
    decrypted = decrypt_data(cipher)
    assert decrypted == plain_text

def test_empty_string():
    assert encrypt_data("") == ""
    assert decrypt_data("") == ""
