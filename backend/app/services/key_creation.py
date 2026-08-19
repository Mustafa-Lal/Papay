"""
Access-key creation service.

Responsibilities:
- Generate new activation keys.
- Hash activation keys using the server-side authentication secret.
- Store only the activation-key hash.
- Associate the key with a role.
- Return the raw activation key once to the caller.

This service does not:
- Authenticate the requesting admin.
- Handle HTTP/FastAPI requests.
- Store raw activation keys.

The caller is responsible for ensuring that only an
authenticated ADMIN can invoke this service.
"""

import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access_key import AccessKey
from app.models.role import Role
from app.security.hash_generation import hash_activation_key


KEY_PREFIX = "PG"
KEY_RANDOM_BYTES = 18


def generate_activation_key() -> str:
    """
    Generate a cryptographically secure activation key.
    """

    random_part = secrets.token_urlsafe(
        KEY_RANDOM_BYTES
    )

    return f"{KEY_PREFIX}-{random_part}"


def create_access_key(
    db: Session,
    role_id: int,
    secret: str,
):
    """
    Create a new activation key.

    The raw key is generated, hashed, and stored only
    as a hash in the database.

    The raw key is returned once so the authenticated
    admin can distribute/save it.

    Returns:
        {
            "success": True,
            "key": raw_key,
            "role": role.name,
            "access_key_id": access_key.id,
        }

    Returns None when creation fails.
    """

    role = db.scalar(
        select(Role).where(
            Role.id == role_id,
        )
    )

    if role is None:
        return None

    # Do not allow creation of additional ADMIN keys
    # through the normal key-creation flow.
    if role.name == "ADMIN":
        return None

    raw_key = generate_activation_key()

    key_hash = hash_activation_key(
        raw_key,
        secret,
    )

    access_key = AccessKey(
        role_id=role.id,
        key_hash=key_hash,
        active=1,
    )

    db.add(access_key)

    try:
        db.commit()
        db.refresh(access_key)

    except Exception:
        db.rollback()
        return None

    return {
        "success": True,
        "key": raw_key,
        "role": role.name,
        "access_key_id": access_key.id,
    }