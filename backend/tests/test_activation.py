import os

from dotenv import load_dotenv

from backend.app.security.hash_generation import (
    hash_activation_key,
)


load_dotenv()

SECRET = os.getenv("AUTH_HASH_SECRET")

if not SECRET:
    raise RuntimeError("AUTH_HASH_SECRET is not configured.")


ADMIN_KEY = "PG-ADMIN-AC12E0-180B72-A55E6F"

stored_hash = hash_activation_key(
    ADMIN_KEY,
    SECRET,
)

correct_hash = hash_activation_key(
    ADMIN_KEY,
    SECRET,
)

wrong_hash = hash_activation_key(
    "WRONG-KEY",
    SECRET,
)

print("Correct key:", stored_hash == correct_hash)
print("Wrong key:", stored_hash == wrong_hash)