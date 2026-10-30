import base64
from cryptography.fernet import Fernet
from app.core.config import settings

def _get_fernet() -> Fernet:
    try:
        return Fernet(settings.ENCRYPTION_KEY.encode())
    except Exception:
        key = base64.urlsafe_b64encode(settings.ENCRYPTION_KEY.encode().ljust(32)[:32])
        return Fernet(key)

def encrypt_pii(value: str) -> str:
    """Encrypt sensitive PII string before persisting."""
    if not value:
        return value
    f = _get_fernet()
    return f.encrypt(value.encode()).decode()

def decrypt_pii(cipher_text: str) -> str:
    """Decrypt sensitive PII string for authorized viewer."""
    if not cipher_text:
        return cipher_text
    try:
        f = _get_fernet()
        return f.decrypt(cipher_text.encode()).decode()
    except Exception:
        return "[ENCRYPTED_PII]"
