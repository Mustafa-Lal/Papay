import os

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.access_key import AccessKey
from app.models.role import Role
from backend.app.security.hash_generation import hash_activation_key


load_dotenv()

ADMIN_KEY = "PG-ADMIN-AC12E0-180B72-A55E6F"
AUTH_HASH_SECRET = os.getenv("AUTH_HASH_SECRET")

if not AUTH_HASH_SECRET:
    raise RuntimeError("AUTH_HASH_SECRET is not configured.")


with Session(engine) as db:
    admin_role = db.scalar(
        select(Role).where(Role.name == "ADMIN")
    )

    if admin_role is None:
        raise RuntimeError("ADMIN role does not exist.")

    existing_admin = db.scalar(
        select(AccessKey).where(
            AccessKey.role_id == admin_role.id
        )
    )

    if existing_admin:
        raise RuntimeError("An ADMIN access key already exists.")

    key_hash = hash_activation_key(
        ADMIN_KEY,
        AUTH_HASH_SECRET,
    )

    db.add(
        AccessKey(
            key_hash=key_hash,
            role_id=admin_role.id,
            active=True,
        )
    )

    db.commit()

print("ADMIN access key seeded successfully.")