import unittest
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.salary import Salary


def mock_get_current_access_key() -> AccessKey:
    return AccessKey(id=1, role_id=1, active=True)


class RouterSalaryTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.cleanup()

    def cleanup(self):
        with Session(engine) as db:
            for s in db.scalars(select(Salary)).all():
                db.delete(s)
            db.commit()

    def _current_year_month(self):
        now = datetime.now()
        return now.year, now.month

    def test_create_salary(self):
        payload = {"name": "Ahmed", "amount": "3000.00"}
        res = self.client.post("/salaries", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["name"], "Ahmed")
        self.assertEqual(data["amount"], "3000.00")

    def test_list_salaries_by_month(self):
        year, month = self._current_year_month()
        self.client.post("/salaries", json={"name": "Ahmed", "amount": "1000"})
        self.client.post("/salaries", json={"name": "Ali", "amount": "2000"})
        res = self.client.get(f"/salaries/{year}/{month}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["pagination"]["total"], 2)
        self.assertEqual(len(data["salaries"]), 2)

    def test_update_salary(self):
        create_res = self.client.post("/salaries", json={"name": "Ahmed", "amount": "3000"})
        salary_id = create_res.json()["id"]
        update_res = self.client.put(f"/salaries/{salary_id}", json={"name": "Ahmed Updated", "amount": "3500"})
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["name"], "Ahmed Updated")
        self.assertEqual(update_res.json()["amount"], "3500.00")

    def test_delete_salary(self):
        create_res = self.client.post("/salaries", json={"name": "Ahmed", "amount": "3000"})
        salary_id = create_res.json()["id"]
        delete_res = self.client.delete(f"/salaries/{salary_id}")
        self.assertEqual(delete_res.status_code, 204)


if __name__ == "__main__":
    unittest.main(verbosity=2)
