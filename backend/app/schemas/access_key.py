from datetime import datetime

from pydantic import BaseModel, Field


# --------------------------------------------------
# Request: Admin creates a key
# --------------------------------------------------

class AccessKeyCreate(BaseModel):
    role_id: int = Field(ge=1)


# --------------------------------------------------
# Response: After creation — raw key shown once only
# --------------------------------------------------

class AccessKeyCreateResponse(BaseModel):
    access_key_id: int
    role: str
    key: str   # Raw key returned ONCE. Never stored.


# --------------------------------------------------
# Response: Single key in list (never exposes key_hash)
# --------------------------------------------------

class AccessKeyResponse(BaseModel):
    id: int
    role_id: int
    active: bool
    created_at: datetime


# --------------------------------------------------
# Request: Employee activates their session
# --------------------------------------------------

class ActivationRequest(BaseModel):
    activation_key: str = Field(min_length=1)


# --------------------------------------------------
# Response: Successful session token
# --------------------------------------------------

class TokenResponse(BaseModel):
    token: str
    expires_at: datetime


# --------------------------------------------------
# Response: /auth/me
# --------------------------------------------------

class MeResponse(BaseModel):
    access_key_id: int
    role: str
