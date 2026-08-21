import unittest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.expense import Expense


def mock_get_current_access_key() -> AccessKey:
    return AccessKey(id=1, role_id=1, active=True)


class RouterExpenseTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.cleanup()

    def cleanup(self):
        with Session(engine) as db:
            for e in db.scalars(select(Expense)).all():
                db.delete(e)
            db.commit()

    def test_create_expense(self):
        payload = {"description": "Office supplies", "amount": "150.00"}
        res = self.client.post("/expenses", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["description"], "Office supplies")
        self.assertEqual(data["amount"], "150.00")

    def test_list_expenses(self):
        self.client.post("/expenses", json={"description": "Supply A", "amount": "100"})
        self.client.post("/expenses", json={"description": "Supply B", "amount": "200"})
        res = self.client.get("/expenses")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["pagination"]["total"], 2)
        self.assertEqual(len(data["expenses"]), 2)

    def test_update_expense(self):
        create_res = self.client.post("/expenses", json={"description": "Supply A", "amount": "100"})
        expense_id = create_res.json()["id"]
        update_res = self.client.put(f"/expenses/{expense_id}", json={"description": "Updated supply", "amount": "120"})
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["description"], "Updated supply")
        self.assertEqual(update_res.json()["amount"], "120.00")

    def test_delete_expense(self):
        create_res = self.client.post("/expenses", json={"description": "Supply A", "amount": "100"})
        expense_id = create_res.json()["id"]
        delete_res = self.client.delete(f"/expenses/{expense_id}")
        self.assertEqual(delete_res.status_code, 204)
        # After soft delete, should not appear in active list
        list_res = self.client.get("/expenses")
        self.assertEqual(list_res.json()["pagination"]["total"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
