import unittest
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.dependencies.auth import get_current_access_key
from app.main import app
from app.models.access_key import AccessKey
from app.models.insurance_expense import InsuranceExpense
from app.models.insurance_income import InsuranceIncome
from app.services.insurance_expense import (
    create_insurance_expense,
    deactivate_insurance_expense,
    get_insurance_expenses,
    update_insurance_expense,
)
from app.services.insurance_income import (
    create_insurance_income,
    deactivate_insurance_income,
    get_insurance_incomes,
    update_insurance_income,
)


def mock_get_current_access_key() -> AccessKey:
    return AccessKey(id=1, role_id=1, active=True)


class InsuranceFinanceFullTests(unittest.TestCase):
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
    # EXPENSES ROUTER TESTS
    # ---------------------------------------------------------

    def test_list_and_paginate_insurance_expenses(self):
        # Create 3 expenses
        for i in range(3):
            self.client.post(
                "/insurance/expenses",
                json={"description": f"Expense {i}", "price": f"{(i+1)*10}.00"},
            )

        # List with limit 2
        res = self.client.get("/insurance/expenses?limit=2&offset=0")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["expenses"]), 2)
        self.assertEqual(data["pagination"]["total"], 3)
        self.assertEqual(data["pagination"]["has_more"], True)

        # List next page
        res2 = self.client.get("/insurance/expenses?limit=2&offset=2")
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(len(data2["expenses"]), 1)
        self.assertEqual(data2["pagination"]["has_more"], False)

    def test_update_insurance_expense(self):
        res_create = self.client.post(
            "/insurance/expenses",
            json={"description": "Original", "price": "50.00"},
        )
        expense_id = res_create.json()["id"]

        # Update description and price
        res_update = self.client.put(
            f"/insurance/expenses/{expense_id}",
            json={"description": "Updated", "price": "75.00"},
        )
        self.assertEqual(res_update.status_code, 200)
        updated_data = res_update.json()
        self.assertEqual(updated_data["description"], "Updated")
        self.assertEqual(updated_data["price"], "75.00")

    def test_delete_insurance_expense(self):
        res_create = self.client.post(
            "/insurance/expenses",
            json={"description": "To delete", "price": "20.00"},
        )
        expense_id = res_create.json()["id"]

        # Delete
        res_delete = self.client.delete(f"/insurance/expenses/{expense_id}")
        self.assertEqual(res_delete.status_code, 200)

        # Verify excluded from list
        res_list = self.client.get("/insurance/expenses")
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(len(res_list.json()["expenses"]), 0)

    # ---------------------------------------------------------
    # INCOMES ROUTER TESTS
    # ---------------------------------------------------------

    def test_list_and_paginate_insurance_incomes(self):
        # Create 3 incomes
        for i in range(3):
            self.client.post(
                "/insurance/incomes",
                json={"description": f"Income {i}", "price": f"{(i+1)*20}.00"},
            )

        # List with limit 2
        res = self.client.get("/insurance/incomes?limit=2&offset=0")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["incomes"]), 2)
        self.assertEqual(data["pagination"]["total"], 3)
        self.assertEqual(data["pagination"]["has_more"], True)

        # List next page
        res2 = self.client.get("/insurance/incomes?limit=2&offset=2")
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(len(data2["incomes"]), 1)
        self.assertEqual(data2["pagination"]["has_more"], False)

    def test_update_insurance_income(self):
        res_create = self.client.post(
            "/insurance/incomes",
            json={"description": "Original Claim", "price": "150.00"},
        )
        income_id = res_create.json()["id"]

        # Update description and price
        res_update = self.client.put(
            f"/insurance/incomes/{income_id}",
            json={"description": "Settled Claim", "price": "200.00"},
        )
        self.assertEqual(res_update.status_code, 200)
        updated_data = res_update.json()
        self.assertEqual(updated_data["description"], "Settled Claim")
        self.assertEqual(updated_data["price"], "200.00")

    def test_delete_insurance_income(self):
        res_create = self.client.post(
            "/insurance/incomes",
            json={"description": "To delete", "price": "60.00"},
        )
        income_id = res_create.json()["id"]

        # Delete
        res_delete = self.client.delete(f"/insurance/incomes/{income_id}")
        self.assertEqual(res_delete.status_code, 200)

        # Verify excluded from list
        res_list = self.client.get("/insurance/incomes")
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(len(res_list.json()["incomes"]), 0)


if __name__ == "__main__":
    unittest.main()
