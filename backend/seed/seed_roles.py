from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.role import Role


ROLES = [
    "INSURANCE",
    "MECHANIC",
    "OWNER",
    "ADMIN",
]


with Session(engine) as db:
    for role_name in ROLES:
        existing_role = db.scalar(
            select(Role).where(Role.name == role_name)
        )

        if existing_role is None:
            db.add(Role(name=role_name))

    db.commit()

print("Roles seeded successfully.")