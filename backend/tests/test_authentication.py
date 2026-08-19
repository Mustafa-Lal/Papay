import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import engine
from app.services.authentication import authenticate_activation_key


load_dotenv()

SECRET = os.getenv("AUTH_HASH_SECRET")

if not SECRET:
    raise RuntimeError("AUTH_HASH_SECRET is not configured.")

ADMIN_KEY = "PG-ADMIN-AC12E0-180B72-A55E6f"

with Session(engine) as db:
    result = authenticate_activation_key(
        db,
        ADMIN_KEY,
        SECRET,
    )

    if result is None:
        print("Authentication FAILED")
    else:
        print("Authentication SUCCESS")
        print("Role:", result["role"].name)
        print("Access key ID:", result["access_key"].id)