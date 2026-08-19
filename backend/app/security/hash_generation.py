import hashlib
import hmac


def hash_activation_key(key: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()