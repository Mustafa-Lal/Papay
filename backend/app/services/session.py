"""
Session service.

Responsibilities:
- Create a session for an authenticated access key.
- Validate session tokens.
- Check whether the associated access key is active.
- Check token expiration.
- Renew expired tokens.
- Return authentication information for protected requests.

This file does not:
- Authenticate activation keys.
- Generate tokens directly.
- Handle HTTP/FastAPI requests.

Those responsibilities belong to:
- authentication.py -> activation-key authentication
- security/tokens.py -> token generation and hashing
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access_key import AccessKey
from app.models.role import Role
from app.models.session import Session as AuthSession
from app.security.tokens import generate_token, hash_token


TOKEN_LIFETIME = timedelta(days=7)


def utc_now() -> datetime:
    """
    Return the current UTC time as a naive datetime.

    SQLite stores our timestamps as UTC without timezone information.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_session(
    db: Session,
    access_key: AccessKey,
):
    """
    Create or replace the session for an access key.

    Returns:
        token: Raw token that is sent to Flutter.
        expires_at: Token expiration time.
    """

    raw_token = generate_token()
    token_hash = hash_token(raw_token)

    expires_at = utc_now() + TOKEN_LIFETIME

    session = db.scalar(
        select(AuthSession).where(
            AuthSession.access_key_id == access_key.id,
        )
    )

    if session is None:
        session = AuthSession(
            access_key_id=access_key.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        db.add(session)

    else:
        session.token_hash = token_hash
        session.expires_at = expires_at

    db.commit()

    return {
        "token": raw_token,
        "expires_at": expires_at,
    }


def authenticate_token(
    db: Session,
    raw_token: str,
):
    """
    Authenticate a request using an existing session token.

    Flow:
    1. Hash the supplied token.
    2. Find the corresponding session.
    3. Find the associated access key.
    4. Reject if the access key is inactive.
    5. Check token expiration.
    6. If expired, generate and store a new token.
    7. Return authentication information.

    An expired token does NOT cause the original request to fail
    when the associated access key is still active.

    Returns:
        {
            "access_key": AccessKey,
            "role": Role,
            "new_token": str | None,
            "expires_at": datetime
        }

        Returns None when authentication fails.
    """

    token_hash = hash_token(raw_token)

    auth_session = db.scalar(
        select(AuthSession).where(
            AuthSession.token_hash == token_hash,
        )
    )

    if auth_session is None:
        return None

    access_key = db.scalar(
        select(AccessKey).where(
            AccessKey.id == auth_session.access_key_id,
        )
    )

    if access_key is None:
        return None

    # Access-key activation controls whether the user
    # is currently allowed to use the application.
    if access_key.active == 0:
        return None

    role = db.scalar(
        select(Role).where(
            Role.id == access_key.role_id,
        )
    )

    if role is None:
        return None

    now = utc_now()

    # Token is still valid.
    if auth_session.expires_at > now:
        return {
            "access_key": access_key,
            "role": role,
            "new_token": None,
            "expires_at": auth_session.expires_at,
        }

    # Token expired, but access key is still active.
    # Generate a new token and replace the old session token.
    new_token = generate_token()
    new_token_hash = hash_token(new_token)

    new_expires_at = now + TOKEN_LIFETIME

    auth_session.token_hash = new_token_hash
    auth_session.expires_at = new_expires_at

    db.commit()

    return {
        "access_key": access_key,
        "role": role,
        "new_token": new_token,
        "expires_at": new_expires_at,
    }