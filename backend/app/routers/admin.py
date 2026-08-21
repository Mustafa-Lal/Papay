"""
Admin access-key management router.

Routes:
    POST   /admin/access-keys              — Create a new key (active=0)
    GET    /admin/access-keys              — List all keys (no key_hash)
    PATCH  /admin/access-keys/{id}/activate   — Activate a key
    PATCH  /admin/access-keys/{id}/deactivate — Deactivate a key

All routes require an authenticated ADMIN session.
"""

import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies.auth import get_db, require_admin
from app.models.access_key import AccessKey
from app.models.role import Role
from app.schemas.access_key import (
    AccessKeyCreate,
    AccessKeyCreateResponse,
    AccessKeyResponse,
)
from app.services.key_activation import (
    activate_access_key_by_id,
    deactivate_access_key_by_id,
)
from app.services.key_creation import create_access_key

router = APIRouter(prefix="/admin/access-keys")


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
# POST /admin/access-keys — Create key (active=0)
# ---------------------------------------------------------

@router.post(
    "",
    response_model=AccessKeyCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_key_endpoint(
    payload: AccessKeyCreate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(require_admin),
):
    secret = _get_secret()

    result = create_access_key(
        db=db,
        role_id=payload.role_id,
        secret=secret,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Could not create access key. "
                "The role may not exist or may be restricted (e.g. ADMIN)."
            ),
        )

    return AccessKeyCreateResponse(
        access_key_id=result["access_key_id"],
        role=result["role"],
        key=result["key"],
    )


# ---------------------------------------------------------
# GET /admin/access-keys — List all keys
# ---------------------------------------------------------

@router.get("", response_model=list[AccessKeyResponse])
def list_keys_endpoint(
    db: Session = Depends(get_db),
    _: AccessKey = Depends(require_admin),
):
    keys = db.scalars(
        select(AccessKey).order_by(AccessKey.id.desc())
    ).all()
    return keys


# ---------------------------------------------------------
# PATCH /admin/access-keys/{key_id}/activate
# ---------------------------------------------------------

@router.patch(
    "/{key_id}/activate",
    response_model=AccessKeyResponse,
)
def activate_key_endpoint(
    key_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(require_admin),
):
    key = activate_access_key_by_id(db=db, key_id=key_id)

    if key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access key not found.",
        )

    try:
        db.commit()
        db.refresh(key)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate access key.",
        )

    return key


# ---------------------------------------------------------
# PATCH /admin/access-keys/{key_id}/deactivate
# ---------------------------------------------------------

@router.patch(
    "/{key_id}/deactivate",
    response_model=AccessKeyResponse,
)
def deactivate_key_endpoint(
    key_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(require_admin),
):
    key = deactivate_access_key_by_id(db=db, key_id=key_id)

    if key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access key not found.",
        )

    try:
        db.commit()
        db.refresh(key)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate access key.",
        )

    return key

# ---------------------------------------------------------
# DELETE /admin/access-keys/{key_id}
# ---------------------------------------------------------

from app.services.key_deletion import delete_access_key_by_id

@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_key_endpoint(
    key_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(require_admin),
):
    # Prevent the admin from deleting themselves (e.g. role_id 4)
    # But since there might be multiple admins, maybe just prevent deleting the key_id making the request?
    # For now, let's just delete the key.
    
    success = delete_access_key_by_id(db=db, key_id=key_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access key not found.",
        )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete access key.",
        )
