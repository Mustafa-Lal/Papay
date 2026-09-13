import unittest

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.insurance_expense import InsuranceExpense
from app.models.insurance_income import InsuranceIncome


def mock_get_current_access_key() -> AccessKey:
    return AccessKey(id=1, role_id=1, active=True)


class RouterInsuranceFinanceTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[get_current_access_key] = mock_get_current_access_key
        self.client = TestClient(app)
        self.cleanup()

    def tearDown(self):
        app.dependency_overrides.clear()
        self.cleanup()

    def cleanup(self):
        with Session(engine) as db:
            for e in db.scalars(select(InsuranceExpense)).all():
                db.delete(e)
            for i in db.scalars(select(InsuranceIncome)).all():
                db.delete(i)
            db.commit()

    # ---------------------------------------------------------
    # INSURANCE EXPENSE ENDPOINT
    # ---------------------------------------------------------

    def test_create_insurance_expense_success(self):
        payload = {"description": "Part recovery cost", "price": "350.00"}
        res = self.client.post("/insurance/expenses", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("id", data)
        self.assertEqual(data["description"], "Part recovery cost")
        self.assertEqual(data["price"], "350.00")
        self.assertIn("created_at", data)

    def test_create_insurance_expense_validation_error_negative_price(self):
        payload = {"description": "Invalid cost", "price": "-10.00"}
        res = self.client.post("/insurance/expenses", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_create_insurance_expense_validation_error_empty_description(self):
        payload = {"description": "", "price": "100.00"}
        res = self.client.post("/insurance/expenses", json=payload)
        self.assertEqual(res.status_code, 422)

    # ---------------------------------------------------------
    # INSURANCE INCOME ENDPOINT
    # ---------------------------------------------------------

    def test_create_insurance_income_success(self):
        payload = {"description": "Inspection fee received", "price": "500.00"}
        res = self.client.post("/insurance/incomes", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("id", data)
        self.assertEqual(data["description"], "Inspection fee received")
        self.assertEqual(data["price"], "500.00")
        self.assertIn("created_at", data)

    def test_create_insurance_income_validation_error_negative_price(self):
        payload = {"description": "Invalid fee", "price": "-5.00"}
        res = self.client.post("/insurance/incomes", json=payload)
        self.assertEqual(res.status_code, 422)

    def test_create_insurance_income_validation_error_empty_description(self):
        payload = {"description": "", "price": "200.00"}
        res = self.client.post("/insurance/incomes", json=payload)
        self.assertEqual(res.status_code, 422)
