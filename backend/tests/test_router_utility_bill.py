import unittest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.utility_bill import UtilityBill


def mock_get_current_access_key() -> AccessKey:
    return AccessKey(id=1, role_id=1, active=True)


class RouterUtilityBillTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.cleanup()

    def cleanup(self):
        with Session(engine) as db:
            for b in db.scalars(select(UtilityBill)).all():
                db.delete(b)
            db.commit()

    def test_create_utility_bill(self):
        payload = {"bill_type": "ELECTRICITY", "amount": "250.00", "year": 2024, "month": 1}
        res = self.client.post("/utility-bills", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["bill_type"], "ELECTRICITY")
        self.assertEqual(data["amount"], "250.00")

    def test_get_utility_bills_by_period(self):
        self.client.post("/utility-bills", json={"bill_type": "ELECTRICITY", "amount": "100", "year": 2024, "month": 1})
        self.client.post("/utility-bills", json={"bill_type": "WATER", "amount": "50", "year": 2024, "month": 1})
        res = self.client.get("/utility-bills/2024/1")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["bills"]), 2)

    def test_update_utility_bill(self):
        create_res = self.client.post("/utility-bills", json={"bill_type": "ELECTRICITY", "amount": "100", "year": 2024, "month": 1})
        bill_id = create_res.json()["id"]
        update_res = self.client.put(f"/utility-bills/{bill_id}", json={"amount": "150"})
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["amount"], "150.00")

    def test_delete_utility_bill(self):
        create_res = self.client.post("/utility-bills", json={"bill_type": "ELECTRICITY", "amount": "100", "year": 2024, "month": 1})
        bill_id = create_res.json()["id"]
        delete_res = self.client.delete(f"/utility-bills/{bill_id}")
        self.assertEqual(delete_res.status_code, 204)
        # After deletion the bill should be gone from the list
        list_res = self.client.get("/utility-bills/2024/1")
        self.assertEqual(len(list_res.json()["bills"]), 0)

    def test_duplicate_bill_rejected(self):
        self.client.post("/utility-bills", json={"bill_type": "ELECTRICITY", "amount": "100", "year": 2024, "month": 1})
        res = self.client.post("/utility-bills", json={"bill_type": "ELECTRICITY", "amount": "200", "year": 2024, "month": 1})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
