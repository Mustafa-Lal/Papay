import os

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.session import Session as AuthSession
from app.security.tokens import hash_token
from app.services.authentication import (
    authenticate_activation_key,
    create_session,
)


load_dotenv()

SECRET = os.getenv("AUTH_HASH_SECRET")

if not SECRET:
    raise RuntimeError("AUTH_HASH_SECRET is not configured.")

ADMIN_KEY = "PG-ADMIN-AC12E0-180B72-A55E6F"


with Session(engine) as db:

    # 1. Authenticate using the activation key
    authentication = authenticate_activation_key(
        db,
        ADMIN_KEY,
        SECRET,
    )

    if authentication is None:
        print("Authentication failed.")
        raise SystemExit(1)

    print("Authentication successful.")
    print("Role:", authentication["role"].name)

    # 2. Generate the session/token
    result = create_session(
        db,
        authentication["access_key"],
    )

    returned_token = result["token"]

    print("\nToken returned by authentication:")
    print(returned_token)

    # 3. Get the session from the database
    session = db.scalar(
        select(AuthSession).where(
            AuthSession.access_key_id
            == authentication["access_key"].id
        )
    )

    if session is None:
        print("\nERROR: No session found.")
        raise SystemExit(1)

    print("\nToken hash stored in database:")
    print(session.token_hash)

    # 4. Hash the returned token
    calculated_hash = hash_token(returned_token)

    print("\nHash calculated from returned token:")
    print(calculated_hash)

    # 5. Compare
    if calculated_hash == session.token_hash:
        print("\n✓ TOKEN MATCHES DATABASE")
    else:
        print("\n✗ TOKEN DOES NOT MATCH DATABASE")
        raise SystemExit(1)