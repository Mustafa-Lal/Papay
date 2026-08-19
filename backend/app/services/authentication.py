from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access_key import AccessKey
from app.models.role import Role
from app.models.session import Session as AuthSession
from app.security.hash_generation import hash_activation_key
from app.security.tokens import generate_token, hash_token
from datetime import datetime, timedelta, timezone


TOKEN_LIFETIME = timedelta(days=7)


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def authenticate_activation_key(
    db: Session,
    raw_key: str,
    secret: str,
):
    submitted_hash = hash_activation_key(
        raw_key,
        secret,
    )

    access_key = db.scalar(
        select(AccessKey).where(
            AccessKey.key_hash == submitted_hash,
            AccessKey.active != 0,
        )
    )

    if access_key is None:
        return None

    role = db.scalar(
        select(Role).where(
            Role.id == access_key.role_id,
        )
    )

    if role is None:
        return None

    return {
        "access_key": access_key,
        "role": role,
    }


def create_session(
    db: Session,
    access_key: AccessKey,
):
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