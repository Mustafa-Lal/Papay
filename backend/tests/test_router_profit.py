import unittest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.profit import Profit


def mock_get_current_access_key() -> AccessKey:
    return AccessKey(id=1, role_id=1, active=True)


class RouterProfitTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.cleanup()

    def cleanup(self):
        with Session(engine) as db:
            for p in db.scalars(select(Profit)).all():
                db.delete(p)
            db.commit()

    def test_create_profit(self):
        payload = {"name": "Insurance commission", "amount": "500.00"}
        res = self.client.post("/profits", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["name"], "Insurance commission")
        self.assertEqual(data["amount"], "500.00")

    def test_list_profits(self):
        self.client.post("/profits", json={"name": "Profit A", "amount": "100"})
        self.client.post("/profits", json={"name": "Profit B", "amount": "200"})
        res = self.client.get("/profits")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["pagination"]["total"], 2)
        self.assertEqual(len(data["profits"]), 2)

    def test_update_profit(self):
        create_res = self.client.post("/profits", json={"name": "Profit A", "amount": "100"})
        profit_id = create_res.json()["id"]
        update_res = self.client.put(f"/profits/{profit_id}", json={"name": "Updated Profit", "amount": "150"})
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["name"], "Updated Profit")
        self.assertEqual(update_res.json()["amount"], "150.00")

    def test_delete_profit(self):
        create_res = self.client.post("/profits", json={"name": "Profit A", "amount": "100"})
        profit_id = create_res.json()["id"]
        delete_res = self.client.delete(f"/profits/{profit_id}")
        self.assertEqual(delete_res.status_code, 204)
        # After soft delete, should not appear in active list
        list_res = self.client.get("/profits")
        self.assertEqual(list_res.json()["pagination"]["total"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
