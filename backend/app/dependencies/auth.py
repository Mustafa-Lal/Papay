from collections.abc import Generator

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.access_key import AccessKey
from app.models.role import Role
from app.services.session import authenticate_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """Provide one database session for the lifetime of a request."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_access_key(
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> AccessKey:
    """Return the active access key represented by a bearer token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required.",
        )

    authentication = authenticate_token(
        db=db,
        raw_token=credentials.credentials,
    )

    if authentication is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive session.",
        )

    if authentication["new_token"] is not None:
        response.headers["X-Session-Token"] = authentication["new_token"]
        response.headers["X-Session-Expires-At"] = (
            authentication["expires_at"].isoformat()
        )

    return authentication["access_key"]


def require_admin(
    db: Session = Depends(get_db),
    access_key: AccessKey = Depends(get_current_access_key),
) -> AccessKey:
    """
    Ensure the current session belongs to an ADMIN role.

    Raises 403 Forbidden if the key holder is not an admin.
    Returns the AccessKey on success.
    """
    role = db.scalar(
        select(Role).where(Role.id == access_key.role_id)
    )

    if role is None or role.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return access_key


def require_owner(
    db: Session = Depends(get_db),
    access_key: AccessKey = Depends(get_current_access_key),
) -> AccessKey:
    """
    Ensure the current session belongs to an OWNER role.

    Raises 403 Forbidden if the key holder is not an owner.
    Returns the AccessKey on success.
    """
    role = db.scalar(
        select(Role).where(Role.id == access_key.role_id)
    )

    if role is None or role.name != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required.",
        )

    return access_key
