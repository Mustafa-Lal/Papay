"""
Authentication router.

Routes:
    POST /auth/activate — Employee uses raw key to get a session token
    POST /auth/logout   — Invalidate the current session
    GET  /auth/me       — Return the caller's identity

These routes do NOT require admin access.
POST /auth/activate requires no existing session (it creates one).
POST /auth/logout and GET /auth/me require an active session.
"""

import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_access_key, get_db
from app.models.access_key import AccessKey
from app.models.role import Role
from app.models.session import Session as AuthSession
from app.schemas.access_key import ActivationRequest, MeResponse, TokenResponse
from app.schemas.settings import VersionCheckResponse
from app.services.authentication import authenticate_activation_key, create_session

router = APIRouter(prefix="/auth")


def _get_secret() -> str:
    """Read AUTH_HASH_SECRET from environment at request time."""
    secret = os.getenv("AUTH_HASH_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server authentication secret is not configured.",
        )
    return secret


# ---------------------------------------------------------
# POST /auth/activate — Employee logs in with their raw key
# ---------------------------------------------------------

@router.post(
    "/activate",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def activate_endpoint(
    payload: ActivationRequest,
    db: Session = Depends(get_db),
):
    secret = _get_secret()

    result = authenticate_activation_key(
        db=db,
        raw_key=payload.activation_key,
        secret=secret,
    )

    if result is None:
        # Deliberately vague — do not reveal whether the key
        # exists or is inactive.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive activation key.",
        )

    session_result = create_session(
        db=db,
        access_key=result["access_key"],
    )

    return TokenResponse(
        token=session_result["token"],
        expires_at=session_result["expires_at"],
    )


# ---------------------------------------------------------
# POST /auth/logout — Invalidate current session
# ---------------------------------------------------------

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_endpoint(
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
):
    session = db.scalar(
        select(AuthSession).where(
            AuthSession.access_key_id == current_access_key.id,
        )
    )

    if session is not None:
        db.delete(session)
        db.commit()


# ---------------------------------------------------------
# GET /auth/me — Return caller identity
# ---------------------------------------------------------

@router.get("/me", response_model=MeResponse)
def me_endpoint(
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
):
    role = db.scalar(
        select(Role).where(Role.id == current_access_key.role_id)
    )

    return MeResponse(
        access_key_id=current_access_key.id,
        role=role.name if role else "UNKNOWN",
    )

# ---------------------------------------------------------
# GET /auth/version-check — Check app version
# ---------------------------------------------------------

@router.get("/version-check", response_model=VersionCheckResponse)
def version_check_endpoint(
    version: str,
    _: AccessKey = Depends(get_current_access_key),
):
    required_version = os.getenv("REQUIRED_APP_VERSION", "1.0.0")
    if version == required_version:
        return VersionCheckResponse(match=True)
    return VersionCheckResponse(match=False, required_version=required_version)


