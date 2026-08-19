import os
import unittest

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.access_key import AccessKey
from app.models.role import Role
from app.security.hash_generation import hash_activation_key
from app.services.key_creation import create_access_key


load_dotenv()

SECRET = os.getenv("AUTH_HASH_SECRET")

if not SECRET:
    raise RuntimeError(
        "AUTH_HASH_SECRET is not configured."
    )


class KeyCreationTests(unittest.TestCase):

    def test_create_mechanic_key(self):
        """A MECHANIC key should be created successfully."""

        with Session(engine) as db:
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
            self.assertTrue(result["success"])
            self.assertEqual(
                result["role"],
                "MECHANIC",
            )

            self.assertIsNotNone(
                result["key"]
            )

    def test_create_owner_key(self):
        """An OWNER key should be created successfully."""

        with Session(engine) as db:
            role = db.scalar(
                select(Role).where(
                    Role.name == "OWNER"
                )
            )

            self.assertIsNotNone(role)

            result = create_access_key(
                db,
                role.id,
                SECRET,
            )

            self.assertIsNotNone(result)
            self.assertTrue(result["success"])
            self.assertEqual(
                result["role"],
                "OWNER",
            )

            self.assertIsNotNone(
                result["key"]
            )

    def test_create_insurance_key(self):
        """An INSURANCE key should be created successfully."""

        with Session(engine) as db:
            role = db.scalar(
                select(Role).where(
                    Role.name == "INSURANCE"
                )
            )

            self.assertIsNotNone(role)

            result = create_access_key(
                db,
                role.id,
                SECRET,
            )

            self.assertIsNotNone(result)
            self.assertTrue(result["success"])
            self.assertEqual(
                result["role"],
                "INSURANCE",
            )

            self.assertIsNotNone(
                result["key"]
            )

    def test_admin_key_creation_is_rejected(self):
        """Additional ADMIN keys must be rejected."""

        with Session(engine) as db:
            role = db.scalar(
                select(Role).where(
                    Role.name == "ADMIN"
                )
            )

            self.assertIsNotNone(role)

            result = create_access_key(
                db,
                role.id,
                SECRET,
            )

            self.assertIsNone(result)

    def test_nonexistent_role_is_rejected(self):
        """A nonexistent role must be rejected."""

        with Session(engine) as db:
            result = create_access_key(
                db,
                999999,
                SECRET,
            )

            self.assertIsNone(result)

    def test_raw_key_is_returned(self):
        """
        The raw key should be returned to the caller,
        while only its hash is stored in the database.
        """

        with Session(engine) as db:
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

            raw_key = result["key"]

            self.assertIsNotNone(raw_key)
            self.assertTrue(
                raw_key.startswith("PG-")
            )

    def test_database_stores_hash_not_raw_key(self):
        """
        The raw key returned to the admin must never
        be stored directly in the database.
        """

        with Session(engine) as db:
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

            raw_key = result["key"]
            access_key_id = result["access_key_id"]

            stored_key = db.scalar(
                select(AccessKey).where(
                    AccessKey.id == access_key_id
                )
            )

            self.assertIsNotNone(stored_key)

            expected_hash = hash_activation_key(
                raw_key,
                SECRET,
            )

            self.assertEqual(
                stored_key.key_hash,
                expected_hash,
            )

            self.assertNotEqual(
                stored_key.key_hash,
                raw_key,
            )

            self.assertEqual(
                stored_key.active,
                1,
            )

    def test_returned_key_can_authenticate(self):
        """
        The raw key returned during creation should
        be usable for activation authentication.
        """

        from app.services.authentication import (
            authenticate_activation_key,
        )

        with Session(engine) as db:
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

            raw_key = result["key"]

            authentication = (
                authenticate_activation_key(
                    db,
                    raw_key,
                    SECRET,
                )
            )

            self.assertIsNotNone(
                authentication
            )

            self.assertEqual(
                authentication["role"].name,
                "MECHANIC",
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )