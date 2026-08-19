import hashlib
import secrets


def generate_token() -> str:
    """
    Generate a cryptographically secure random session token.
    """
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """
    Hash the session token before storing it in the database.
    """
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()   