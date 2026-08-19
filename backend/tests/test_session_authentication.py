import os
import unittest
from datetime import timedelta

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.access_key import AccessKey
from app.models.session import Session as AuthSession
from app.services.authentication import authenticate_activation_key
from app.services.session import (
    authenticate_token,
    create_session,
    utc_now,
)
from app.security.tokens import hash_token


load_dotenv()

SECRET = os.getenv("AUTH_HASH_SECRET")

if not SECRET:
    raise RuntimeError(
        "AUTH_HASH_SECRET is not configured."
    )

ADMIN_KEY = "PG-ADMIN-AC12E0-180B72-A55E6F"


class SessionAuthenticationTests(unittest.TestCase):

    def get_access_key(self, db):
        authentication = authenticate_activation_key(
            db,
            ADMIN_KEY,
            SECRET,
        )

        self.assertIsNotNone(authentication)

        return authentication["access_key"]

    def test_valid_token_is_authenticated(self):
        with Session(engine) as db:
            access_key = self.get_access_key(db)

            session_result = create_session(
                db,
                access_key,
            )

            result = authenticate_token(
                db,
                session_result["token"],
            )

            self.assertIsNotNone(result)

            self.assertEqual(
                result["access_key"].id,
                access_key.id,
            )

            self.assertEqual(
                result["role"].name,
                "ADMIN",
            )

            self.assertIsNone(
                result["new_token"],
            )

    def test_wrong_token_is_rejected(self):
        with Session(engine) as db:
            result = authenticate_token(
                db,
                "this-is-not-a-real-token",
            )

            self.assertIsNone(result)

    def test_empty_token_is_rejected(self):
        with Session(engine) as db:
            result = authenticate_token(
                db,
                "",
            )

            self.assertIsNone(result)

    def test_expired_token_is_renewed(self):
        with Session(engine) as db:
            access_key = self.get_access_key(db)

            session_result = create_session(
                db,
                access_key,
            )

            old_token = session_result["token"]

            auth_session = db.scalar(
                select(AuthSession).where(
                    AuthSession.access_key_id
                    == access_key.id
                )
            )

            # Force the token to be expired.
            auth_session.expires_at = (
                utc_now() - timedelta(seconds=1)
            )

            db.commit()

            result = authenticate_token(
                db,
                old_token,
            )

            self.assertIsNotNone(result)

            # A new token must have been generated.
            self.assertIsNotNone(
                result["new_token"],
            )

            self.assertNotEqual(
                result["new_token"],
                old_token,
            )

            # New expiration must be in the future.
            self.assertGreater(
                result["expires_at"],
                utc_now(),
            )

            # Database must contain the new token hash.
            self.assertEqual(
                auth_session.token_hash,
                hash_token(
                    result["new_token"],
                ),
            )

    def test_expired_token_request_is_still_authenticated(self):
        """
        Expired token + active access key should authenticate
        and return a new token instead of failing the request.
        """

        with Session(engine) as db:
            access_key = self.get_access_key(db)

            session_result = create_session(
                db,
                access_key,
            )

            auth_session = db.scalar(
                select(AuthSession).where(
                    AuthSession.access_key_id
                    == access_key.id
                )
            )

            auth_session.expires_at = (
                utc_now() - timedelta(seconds=1)
            )

            db.commit()

            result = authenticate_token(
                db,
                session_result["token"],
            )

            self.assertIsNotNone(result)

            self.assertIsNotNone(
                result["new_token"],
            )

            self.assertEqual(
                result["role"].name,
                "ADMIN",
            )

    def test_inactive_access_key_is_rejected(self):
        with Session(engine) as db:
            access_key = self.get_access_key(db)

            session_result = create_session(
                db,
                access_key,
            )

            original_active = access_key.active

            try:
                access_key.active = 0
                db.commit()

                result = authenticate_token(
                    db,
                    session_result["token"],
                )

                self.assertIsNone(result)

            finally:
                access_key.active = original_active
                db.commit()

    def test_expired_token_with_inactive_key_is_rejected(self):
        """
        An expired token must NOT be renewed if the
        associated access key has been disabled.
        """

        with Session(engine) as db:
            access_key = self.get_access_key(db)

            session_result = create_session(
                db,
                access_key,
            )

            auth_session = db.scalar(
                select(AuthSession).where(
                    AuthSession.access_key_id
                    == access_key.id
                )
            )

            auth_session.expires_at = (
                utc_now() - timedelta(seconds=1)
            )

            access_key.active = 0

            db.commit()

            result = authenticate_token(
                db,
                session_result["token"],
            )

            self.assertIsNone(result)

            # Restore for other tests.
            access_key.active = 1
            db.commit()


if __name__ == "__main__":
    unittest.main(verbosity=2)