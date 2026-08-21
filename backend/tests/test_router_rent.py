import unittest
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.rent import Rent


def mock_get_current_access_key() -> AccessKey:
    """Mock the current access key dependency to avoid needing real tokens."""
    return AccessKey(id=1, role_id=1, active=True)


class RouterRentTests(unittest.TestCase):
    def setUp(self):
        # Override the auth dependency for all tests
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup_rent()

    def tearDown(self):
        # Clean up dependency overrides and database
        app.dependency_overrides.clear()
        self.cleanup_rent()

    def cleanup_rent(self):
        with Session(engine) as db:
            rents = db.scalars(select(Rent)).all()
            for r in rents:
                db.delete(r)
            db.commit()

    def test_create_rent(self):
        payload = {
            "amount": "1000.50",
            "year": 2024,
            "month": 1
        }
        response = self.client.post("/rent", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["amount"], "1000.50")
        self.assertEqual(data["year"], 2024)
        self.assertEqual(data["month"], 1)

    def test_list_rents(self):
        self.client.post("/rent", json={"amount": "100", "year": 2024, "month": 1})
        self.client.post("/rent", json={"amount": "200", "year": 2024, "month": 2})

        response = self.client.get("/rent")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

    def test_get_rent_by_period(self):
        self.client.post("/rent", json={"amount": "100", "year": 2024, "month": 5})

        response = self.client.get("/rent/2024/5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["amount"], "100.00")

    def test_update_rent(self):
        create_res = self.client.post("/rent", json={"amount": "100", "year": 2024, "month": 1})
        rent_id = create_res.json()["id"]

        update_res = self.client.put(f"/rent/{rent_id}", json={"amount": "150"})
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["amount"], "150.00")

    def test_delete_rent(self):
        create_res = self.client.post("/rent", json={"amount": "100", "year": 2024, "month": 1})
        rent_id = create_res.json()["id"]

        delete_res = self.client.delete(f"/rent/{rent_id}")
        self.assertEqual(delete_res.status_code, 204)

        get_res = self.client.get("/rent/2024/1")
        self.assertEqual(get_res.status_code, 404)

if __name__ == "__main__":
    unittest.main(verbosity=2)
