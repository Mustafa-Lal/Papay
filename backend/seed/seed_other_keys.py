import os

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.access_key import AccessKey
from app.models.role import Role
from app.security.hash_generation import hash_activation_key


load_dotenv()
AUTH_HASH_SECRET = os.getenv("AUTH_HASH_SECRET")

if not AUTH_HASH_SECRET:
    raise RuntimeError("AUTH_HASH_SECRET is not configured.")

KEYS_TO_SEED = {
    "INSURANCE": "PG-INSURANCE-123",
    "MECHANIC": "PG-MECHANIC-123",
    "OWNER": "PG-OWNER-123",
}

with Session(engine) as db:
    for role_name, raw_key in KEYS_TO_SEED.items():
        role = db.scalar(
            select(Role).where(Role.name == role_name)
        )

        if role is None:
            print(f"Skipping {role_name}, role does not exist.")
            continue

        existing_key = db.scalar(
            select(AccessKey).where(
                AccessKey.role_id == role.id
            )
        )

        if existing_key:
            print(f"A key for {role_name} already exists.")
            continue

        key_hash = hash_activation_key(raw_key, AUTH_HASH_SECRET)

        db.add(
            AccessKey(
                key_hash=key_hash,
                role_id=role.id,
                active=True,
            )
        )
        print(f"Seeded key for {role_name}: {raw_key}")

    db.commit()

print("Other access keys seeded successfully.")
