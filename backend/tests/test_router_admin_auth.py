"""
Tests for /admin/access-keys and /auth/* routes.

Strategy:
- Mock get_current_access_key for admin tests using an AccessKey that
  has role_id pointing to a real ADMIN role in the DB.
- Mock AUTH_HASH_SECRET via os.environ so the secret is available.
- Each test class cleans up the access_keys and sessions it creates.
"""

import os
import unittest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.role import Role
from app.models.session import Session as AuthSession

# Use a fixed test secret
TEST_SECRET = "test-secret-for-router-tests"


def _ensure_roles(db: Session):
    """Ensure ADMIN and EMPLOYEE roles exist."""
    for name in ("ADMIN", "EMPLOYEE"):
        existing = db.scalar(select(Role).where(Role.name == name))
        if existing is None:
            db.add(Role(name=name))
    db.commit()


def _get_admin_role_id(db: Session) -> int:
    return db.scalar(select(Role.id).where(Role.name == "ADMIN"))


def _get_employee_role_id(db: Session) -> int:
    return db.scalar(select(Role.id).where(Role.name == "EMPLOYEE"))


class AdminAccessKeyTests(unittest.TestCase):
    """Tests for POST/GET/PATCH /admin/access-keys"""

    def setUp(self):
        os.environ["AUTH_HASH_SECRET"] = TEST_SECRET

        with Session(engine) as db:
            _ensure_roles(db)
            self._admin_role_id = _get_admin_role_id(db)
            self._employee_role_id = _get_employee_role_id(db)

        # Mock authentication: pretend the caller is an admin
        def mock_admin_key() -> AccessKey:
            return AccessKey(id=999, role_id=self._admin_role_id, active=1)

        app.dependency_overrides[get_current_access_key] = mock_admin_key
        self.client = TestClient(app)
        self._cleanup()

    def tearDown(self):
        app.dependency_overrides.clear()
        self._cleanup()
        os.environ.pop("AUTH_HASH_SECRET", None)

    def _cleanup(self):
        with Session(engine) as db:
            # Delete sessions for test keys, then keys
            for key in db.scalars(
                select(AccessKey).where(AccessKey.id != 999)
            ).all():
                session = db.scalar(
                    select(AuthSession).where(
                        AuthSession.access_key_id == key.id
                    )
                )
                if session:
                    db.delete(session)
                db.delete(key)
            db.commit()

    # ---------------------------------------------------------
    # POST /admin/access-keys
    # ---------------------------------------------------------

    def test_create_key_returns_raw_key(self):
        res = self.client.post(
            "/admin/access-keys",
            json={"role_id": self._employee_role_id},
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("key", data)
        self.assertIn("access_key_id", data)
        self.assertEqual(data["role"], "EMPLOYEE")
        # Key should start with the prefix
        self.assertTrue(data["key"].startswith("PG-"))

    def test_create_key_starts_inactive(self):
        res = self.client.post(
            "/admin/access-keys",
            json={"role_id": self._employee_role_id},
        )
        key_id = res.json()["access_key_id"]

        with Session(engine) as db:
            key = db.scalar(select(AccessKey).where(AccessKey.id == key_id))
            self.assertIsNotNone(key)
            self.assertEqual(key.active, 0)

    def test_create_admin_key_rejected(self):
        res = self.client.post(
            "/admin/access-keys",
            json={"role_id": self._admin_role_id},
        )
        self.assertEqual(res.status_code, 400)

    def test_create_key_invalid_role(self):
        res = self.client.post(
            "/admin/access-keys",
            json={"role_id": 99999},
        )
        self.assertEqual(res.status_code, 400)

    # ---------------------------------------------------------
    # GET /admin/access-keys
    # ---------------------------------------------------------

    def test_list_keys(self):
        self.client.post("/admin/access-keys", json={"role_id": self._employee_role_id})
        self.client.post("/admin/access-keys", json={"role_id": self._employee_role_id})

        res = self.client.get("/admin/access-keys")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)
        # key_hash must never appear in the response
        for item in data:
            self.assertNotIn("key_hash", item)

    # ---------------------------------------------------------
    # PATCH /admin/access-keys/{id}/activate
    # ---------------------------------------------------------

    def test_activate_key(self):
        create_res = self.client.post(
            "/admin/access-keys",
            json={"role_id": self._employee_role_id},
        )
        key_id = create_res.json()["access_key_id"]

        activate_res = self.client.patch(f"/admin/access-keys/{key_id}/activate")
        self.assertEqual(activate_res.status_code, 200)
        self.assertTrue(activate_res.json()["active"])

    def test_activate_nonexistent_key(self):
        res = self.client.patch("/admin/access-keys/99999/activate")
        self.assertEqual(res.status_code, 404)

    # ---------------------------------------------------------
    # PATCH /admin/access-keys/{id}/deactivate
    # ---------------------------------------------------------

    def test_deactivate_key(self):
        create_res = self.client.post(
            "/admin/access-keys",
            json={"role_id": self._employee_role_id},
        )
        key_id = create_res.json()["access_key_id"]

        # Activate first
        self.client.patch(f"/admin/access-keys/{key_id}/activate")

        # Then deactivate
        deactivate_res = self.client.patch(f"/admin/access-keys/{key_id}/deactivate")
        self.assertEqual(deactivate_res.status_code, 200)
        self.assertFalse(deactivate_res.json()["active"])

    def test_deactivate_nonexistent_key(self):
        res = self.client.patch("/admin/access-keys/99999/deactivate")
        self.assertEqual(res.status_code, 404)


class AuthEndpointTests(unittest.TestCase):
    """Tests for POST /auth/activate, POST /auth/logout, GET /auth/me"""

    def setUp(self):
        os.environ["AUTH_HASH_SECRET"] = TEST_SECRET

        with Session(engine) as db:
            _ensure_roles(db)
            self._employee_role_id = _get_employee_role_id(db)

        self.client = TestClient(app)
        self._cleanup()

    def tearDown(self):
        app.dependency_overrides.clear()
        self._cleanup()
        os.environ.pop("AUTH_HASH_SECRET", None)

    def _cleanup(self):
        with Session(engine) as db:
            for key in db.scalars(select(AccessKey)).all():
                sess = db.scalar(
                    select(AuthSession).where(AuthSession.access_key_id == key.id)
                )
                if sess:
                    db.delete(sess)
                db.delete(key)
            db.commit()

    def _create_active_key(self) -> str:
        """Helper: create a key via service layer, activate it, return raw key."""
        from app.services.key_creation import create_access_key
        from app.services.key_activation import activate_access_key_by_id

        with Session(engine) as db:
            result = create_access_key(
                db=db,
                role_id=self._employee_role_id,
                secret=TEST_SECRET,
            )
            activate_access_key_by_id(db=db, key_id=result["access_key_id"])
            db.commit()
            return result["key"]

    def _create_inactive_key(self) -> str:
        """Helper: create a key but do NOT activate it."""
        from app.services.key_creation import create_access_key

        with Session(engine) as db:
            result = create_access_key(
                db=db,
                role_id=self._employee_role_id,
                secret=TEST_SECRET,
            )
            # Leave it inactive (active=0)
            return result["key"]

    # ---------------------------------------------------------
    # POST /auth/activate
    # ---------------------------------------------------------

    def test_activate_with_valid_active_key(self):
        raw_key = self._create_active_key()
        res = self.client.post(
            "/auth/activate",
            json={"activation_key": raw_key},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)
        self.assertIn("expires_at", data)
        self.assertGreater(len(data["token"]), 10)

    def test_activate_with_inactive_key_rejected(self):
        raw_key = self._create_inactive_key()
        res = self.client.post(
            "/auth/activate",
            json={"activation_key": raw_key},
        )
        self.assertEqual(res.status_code, 401)

    def test_activate_with_wrong_key_rejected(self):
        res = self.client.post(
            "/auth/activate",
            json={"activation_key": "PG-totally-wrong-key"},
        )
        self.assertEqual(res.status_code, 401)

    # ---------------------------------------------------------
    # GET /auth/me (requires valid token)
    # ---------------------------------------------------------

    def test_me_returns_identity(self):
        raw_key = self._create_active_key()
        login_res = self.client.post(
            "/auth/activate",
            json={"activation_key": raw_key},
        )
        token = login_res.json()["token"]

        me_res = self.client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_res.status_code, 200)
        data = me_res.json()
        self.assertEqual(data["role"], "EMPLOYEE")
        self.assertIn("access_key_id", data)

    def test_me_without_token_rejected(self):
        res = self.client.get("/auth/me")
        self.assertEqual(res.status_code, 401)

    # ---------------------------------------------------------
    # POST /auth/logout
    # ---------------------------------------------------------

    def test_logout_invalidates_session(self):
        raw_key = self._create_active_key()
        login_res = self.client.post(
            "/auth/activate",
            json={"activation_key": raw_key},
        )
        token = login_res.json()["token"]

        # Logout
        logout_res = self.client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(logout_res.status_code, 204)

        # Token should now be invalid
        me_res = self.client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(me_res.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
