"""
Access-key activation service.

Responsibilities:
- Activate an existing access key.
- Deactivate an existing access key.
- Locate an access key using its raw activation key.
- Update the active status of the access key.

Security:
- The raw activation key is never stored.
- The server-side AUTH_HASH_SECRET is used to calculate
  the HMAC used for database lookup.
- Authorization that the caller is an ADMIN is handled
  before this service is called.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access_key import AccessKey
from app.security.hash_generation import hash_activation_key


def activate_access_key(
    db: Session,
    raw_key: str,
    secret: str,
) -> bool:
    """
    Activate an existing access key.

    Returns:
        True  -> key found and activated
        False -> key not found or activation failed
    """

    key_hash = hash_activation_key(
        raw_key,
        secret,
    )

    access_key = db.scalar(
        select(AccessKey).where(
            AccessKey.key_hash == key_hash,
        )
    )

    if access_key is None:
        return False

    access_key.active = 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        return False

    return True


def deactivate_access_key(
    db: Session,
    raw_key: str,
    secret: str,
) -> bool:
    """
    Deactivate an existing access key.

    Returns:
        True  -> key found and deactivated
        False -> key not found or deactivation failed
    """

    key_hash = hash_activation_key(
        raw_key,
        secret,
    )

    access_key = db.scalar(
        select(AccessKey).where(
            AccessKey.key_hash == key_hash,
        )
    )

    if access_key is None:
        return False

    access_key.active = 0

    try:
        db.commit()
    except Exception:
        db.rollback()
        return False

    return True