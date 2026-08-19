import os
import unittest
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.access_key import AccessKey
from app.models.session import Session as AuthSession
from app.services.authentication import (
    authenticate_activation_key,
    create_session,
)
from app.security.tokens import hash_token


load_dotenv()

SECRET = os.getenv("AUTH_HASH_SECRET")

if not SECRET:
    raise RuntimeError("AUTH_HASH_SECRET is not configured.")

ADMIN_KEY = "PG-ADMIN-AC12E0-180B72-A55E6F"
WRONG_KEY = "WRONG-ADMIN-KEY"


class AuthenticationTests(unittest.TestCase):

    def test_correct_activation_key(self):
        """Correct active key should authenticate."""

        with Session(engine) as db:
            result = authenticate_activation_key(
                db,
                ADMIN_KEY,
                SECRET,
            )

            self.assertIsNotNone(result)
            self.assertEqual(result["role"].name, "ADMIN")
            self.assertEqual(result["access_key"].id, 1)

    def test_wrong_activation_key(self):
        """Wrong key must be rejected."""

        with Session(engine) as db:
            result = authenticate_activation_key(
                db,
                WRONG_KEY,
                SECRET,
            )

            self.assertIsNone(result)

    def test_empty_activation_key(self):
        """Empty key must be rejected."""

        with Session(engine) as db:
            result = authenticate_activation_key(
                db,
                "",
                SECRET,
            )

            self.assertIsNone(result)

    def test_inactive_key_is_rejected(self):
        """A key with active = 0 must not authenticate."""

        with Session(engine) as db:
            access_key = db.scalar(
                select(AccessKey).where(
                    AccessKey.key_hash == (
                        # Find the ADMIN key using the authentication
                        # function before temporarily disabling it.
                        authenticate_activation_key(
                            db,
                            ADMIN_KEY,
                            SECRET,
                        )["access_key"].key_hash
                    )
                )
            )

            original_active = access_key.active

            try:
                access_key.active = 0
                db.commit()

                result = authenticate_activation_key(
                    db,
                    ADMIN_KEY,
                    SECRET,
                )

                self.assertIsNone(result)

            finally:
                access_key.active = original_active
                db.commit()

    def test_token_is_generated(self):
        """Valid activation should create a token."""

        with Session(engine) as db:
            authentication = authenticate_activation_key(
                db,
                ADMIN_KEY,
                SECRET,
            )

            self.assertIsNotNone(authentication)

            result = create_session(
                db,
                authentication["access_key"],
            )

            self.assertIsNotNone(result["token"])
            self.assertTrue(len(result["token"]) > 20)

    def test_token_is_hashed_in_database(self):
        """Raw token must not be stored in the database."""

        with Session(engine) as db:
            authentication = authenticate_activation_key(
                db,
                ADMIN_KEY,
                SECRET,
            )

            result = create_session(
                db,
                authentication["access_key"],
            )

            raw_token = result["token"]

            session = db.scalar(
                select(AuthSession).where(
                    AuthSession.access_key_id
                    == authentication["access_key"].id
                )
            )

            self.assertIsNotNone(session)

            # Raw token must NOT be stored.
            self.assertNotEqual(
                session.token_hash,
                raw_token,
            )

            # The stored hash must correspond to the token.
            self.assertEqual(
                session.token_hash,
                hash_token(raw_token),
            )

    def test_token_expires_in_seven_days(self):
        """Session expiration should be approximately seven days."""

        with Session(engine) as db:
            authentication = authenticate_activation_key(
                db,
                ADMIN_KEY,
                SECRET,
            )

            before = datetime.now(timezone.utc).replace(tzinfo=None)

            result = create_session(
                db,
                authentication["access_key"],
            )

            after = datetime.now(timezone.utc).replace(tzinfo=None)

            expected_min = before + timedelta(days=7)
            expected_max = after + timedelta(days=7)

            expires_at = result["expires_at"]

            self.assertGreaterEqual(
                expires_at,
                expected_min,
            )

            self.assertLessEqual(
                expires_at,
                expected_max,
            )

    def test_only_one_session_per_access_key(self):
        """Repeated activation should replace the existing session."""

        with Session(engine) as db:
            authentication = authenticate_activation_key(
                db,
                ADMIN_KEY,
                SECRET,
            )

            access_key_id = authentication["access_key"].id

            first = create_session(
                db,
                authentication["access_key"],
            )

            first_token = first["token"]

            second = create_session(
                db,
                authentication["access_key"],
            )

            second_token = second["token"]

            sessions = db.scalars(
                select(AuthSession).where(
                    AuthSession.access_key_id == access_key_id
                )
            ).all()

            self.assertEqual(len(sessions), 1)

            self.assertNotEqual(
                first_token,
                second_token,
            )

            self.assertEqual(
                sessions[0].token_hash,
                hash_token(second_token),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)