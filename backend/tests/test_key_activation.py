import os
import unittest

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.access_key import AccessKey
from app.models.role import Role
from app.security.hash_generation import hash_activation_key
from app.services.key_activation import (
    activate_access_key,
    deactivate_access_key,
)
from app.services.key_creation import create_access_key


load_dotenv()

SECRET = os.getenv("AUTH_HASH_SECRET")

if not SECRET:
    raise RuntimeError(
        "AUTH_HASH_SECRET is not configured."
    )


class KeyActivationTests(unittest.TestCase):

    def create_test_key(self, db):
        role = db.scalar(
            select(Role).where(
                Role.name == "MECHANIC"
            )
        )

        self.assertIsNotNone(role)

        result = create_access_key(
            db,
            role.id,
            SECRET,
        )

        self.assertIsNotNone(result)

        return result["key"], result["access_key_id"]

    def test_activate_key(self):
        """An inactive key should become active."""

        with Session(engine) as db:
            raw_key, access_key_id = (
                self.create_test_key(db)
            )

            access_key = db.scalar(
                select(AccessKey).where(
                    AccessKey.id == access_key_id
                )
            )

            access_key.active = 0
            db.commit()

            result = activate_access_key(
                db,
                raw_key,
                SECRET,
            )

            self.assertTrue(result)

            db.refresh(access_key)

            self.assertEqual(
                access_key.active,
                1,
            )

    def test_deactivate_key(self):
        """An active key should become inactive."""

        with Session(engine) as db:
            raw_key, access_key_id = (
                self.create_test_key(db)
            )

            result = deactivate_access_key(
                db,
                raw_key,
                SECRET,
            )

            self.assertTrue(result)

            access_key = db.scalar(
                select(AccessKey).where(
                    AccessKey.id == access_key_id
                )
            )

            self.assertEqual(
                access_key.active,
                0,
            )

    def test_wrong_key_cannot_activate(self):
        """A nonexistent key must not activate anything."""

        with Session(engine) as db:
            result = activate_access_key(
                db,
                "PG-this-is-not-a-real-key",
                SECRET,
            )

            self.assertFalse(result)

    def test_wrong_key_cannot_deactivate(self):
        """A nonexistent key must not deactivate anything."""

        with Session(engine) as db:
            result = deactivate_access_key(
                db,
                "PG-this-is-not-a-real-key",
                SECRET,
            )

            self.assertFalse(result)

    def test_activation_hash_matches_database(self):
        """
        The raw key should locate the correct database
        record through its HMAC hash.
        """

        with Session(engine) as db:
            raw_key, access_key_id = (
                self.create_test_key(db)
            )

            expected_hash = hash_activation_key(
                raw_key,
                SECRET,
            )

            access_key = db.scalar(
                select(AccessKey).where(
                    AccessKey.id == access_key_id
                )
            )

            self.assertEqual(
                access_key.key_hash,
                expected_hash,
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )