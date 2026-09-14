"""
Tests for GET /insurance/report

Covers:
  - No date params: all active records returned
  - Date range: only records within range returned
  - Invalid range (start > end): 400 error
  - Totals and net calculated correctly
  - Deleted (inactive) records excluded
  - Negative net when expenses exceed incomes
  - Empty result when no records exist
"""

import unittest
from datetime import date, datetime, timezone

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


def _make_expense(db: Session, description: str, price: str, created_at: datetime) -> InsuranceExpense:
    e = InsuranceExpense(description=description, price=price, created_by=1, created_at=created_at)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def _make_income(db: Session, description: str, price: str, created_at: datetime) -> InsuranceIncome:
    i = InsuranceIncome(description=description, price=price, created_by=1, created_at=created_at)
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


class InsuranceFinanceReportTests(unittest.TestCase):

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

    # ----------------------------------------------------------
    # Empty database
    # ----------------------------------------------------------

    def test_empty_report_returns_zeros(self):
        res = self.client.get("/insurance/report")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["expenses"], [])
        self.assertEqual(data["incomes"], [])
        self.assertEqual(data["total_expense"], "0.00")
        self.assertEqual(data["total_income"], "0.00")
        self.assertEqual(data["net"], "0.00")
        self.assertEqual(data["expense_count"], 0)
        self.assertEqual(data["income_count"], 0)
        self.assertIsNone(data["start_date"])
        self.assertIsNone(data["end_date"])

    # ----------------------------------------------------------
    # All records returned when no date params supplied
    # ----------------------------------------------------------

    def test_no_date_params_returns_all_records(self):
        with Session(engine) as db:
            _make_expense(db, "Towing", "350.00", datetime(2026, 1, 10, tzinfo=timezone.utc))
            _make_expense(db, "Parts recovery", "150.00", datetime(2026, 3, 5, tzinfo=timezone.utc))
            _make_income(db, "Claim payout", "1200.00", datetime(2026, 2, 14, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["expense_count"], 2)
        self.assertEqual(data["income_count"], 1)
        self.assertEqual(data["total_expense"], "500.00")
        self.assertEqual(data["total_income"], "1200.00")
        self.assertEqual(data["net"], "700.00")

    # ----------------------------------------------------------
    # Date range filtering
    # ----------------------------------------------------------

    def test_date_range_filters_correctly(self):
        with Session(engine) as db:
            # Inside range
            _make_expense(db, "Inside expense", "200.00", datetime(2026, 6, 15, tzinfo=timezone.utc))
            _make_income(db, "Inside income", "500.00", datetime(2026, 6, 20, tzinfo=timezone.utc))
            # Outside range -- before
            _make_expense(db, "Before expense", "999.00", datetime(2026, 5, 31, tzinfo=timezone.utc))
            # Outside range -- after
            _make_income(db, "After income", "999.00", datetime(2026, 7, 1, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report?start_date=2026-06-01&end_date=2026-06-30")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["expense_count"], 1)
        self.assertEqual(data["income_count"], 1)
        self.assertEqual(data["total_expense"], "200.00")
        self.assertEqual(data["total_income"], "500.00")
        self.assertEqual(data["net"], "300.00")
        self.assertEqual(data["start_date"], "2026-06-01")
        self.assertEqual(data["end_date"], "2026-06-30")

    def test_start_date_only_filter(self):
        with Session(engine) as db:
            _make_expense(db, "Old expense", "100.00", datetime(2026, 1, 1, tzinfo=timezone.utc))
            _make_expense(db, "New expense", "200.00", datetime(2026, 9, 1, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report?start_date=2026-09-01")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["expense_count"], 1)
        self.assertEqual(data["expenses"][0]["description"], "New expense")

    def test_end_date_only_filter(self):
        with Session(engine) as db:
            _make_income(db, "Early income", "300.00", datetime(2026, 1, 15, tzinfo=timezone.utc))
            _make_income(db, "Late income", "600.00", datetime(2026, 9, 15, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report?end_date=2026-06-30")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["income_count"], 1)
        self.assertEqual(data["incomes"][0]["description"], "Early income")

    # ----------------------------------------------------------
    # End date inclusive (record created ON end_date is included)
    # ----------------------------------------------------------

    def test_end_date_is_inclusive(self):
        with Session(engine) as db:
            _make_expense(db, "On end date", "100.00", datetime(2026, 6, 30, 23, 59, 59, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report?start_date=2026-06-01&end_date=2026-06-30")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["expense_count"], 1)

    # ----------------------------------------------------------
    # Invalid date range
    # ----------------------------------------------------------

    def test_start_date_after_end_date_returns_400(self):
        res = self.client.get("/insurance/report?start_date=2026-12-31&end_date=2026-01-01")
        self.assertEqual(res.status_code, 400)
        self.assertIn("Start date cannot be after end date", res.json()["detail"])

    def test_same_start_and_end_date_is_valid(self):
        with Session(engine) as db:
            _make_expense(db, "Same day expense", "50.00", datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report?start_date=2026-06-15&end_date=2026-06-15")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["expense_count"], 1)

    # ----------------------------------------------------------
    # Totals and net
    # ----------------------------------------------------------

    def test_net_is_negative_when_expenses_exceed_incomes(self):
        with Session(engine) as db:
            _make_expense(db, "Big expense", "1000.00", datetime(2026, 8, 1, tzinfo=timezone.utc))
            _make_income(db, "Small income", "200.00", datetime(2026, 8, 2, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_expense"], "1000.00")
        self.assertEqual(data["total_income"], "200.00")
        self.assertEqual(data["net"], "-800.00")

    def test_totals_with_multiple_records(self):
        with Session(engine) as db:
            _make_expense(db, "E1", "100.00", datetime(2026, 7, 1, tzinfo=timezone.utc))
            _make_expense(db, "E2", "250.00", datetime(2026, 7, 2, tzinfo=timezone.utc))
            _make_income(db, "I1", "500.00", datetime(2026, 7, 3, tzinfo=timezone.utc))
            _make_income(db, "I2", "75.50", datetime(2026, 7, 4, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_expense"], "350.00")
        self.assertEqual(data["total_income"], "575.50")
        self.assertEqual(data["net"], "225.50")
        self.assertEqual(data["expense_count"], 2)
        self.assertEqual(data["income_count"], 2)

    # ----------------------------------------------------------
    # Deleted (inactive) records excluded
    # ----------------------------------------------------------

    def test_inactive_records_excluded_from_report(self):
        with Session(engine) as db:
            active_exp = _make_expense(db, "Active expense", "300.00", datetime(2026, 8, 1, tzinfo=timezone.utc))
            inactive_exp = _make_expense(db, "Deleted expense", "999.00", datetime(2026, 8, 2, tzinfo=timezone.utc))
            # Deactivate
            inactive_exp.is_active = False
            db.commit()

            _make_income(db, "Active income", "400.00", datetime(2026, 8, 3, tzinfo=timezone.utc))
            inactive_inc = _make_income(db, "Deleted income", "999.00", datetime(2026, 8, 4, tzinfo=timezone.utc))
            inactive_inc.is_active = False
            db.commit()

        res = self.client.get("/insurance/report")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["expense_count"], 1)
        self.assertEqual(data["income_count"], 1)
        self.assertEqual(data["total_expense"], "300.00")
        self.assertEqual(data["total_income"], "400.00")

    # ----------------------------------------------------------
    # Records are ordered chronologically (ASC)
    # ----------------------------------------------------------

    def test_records_ordered_chronologically(self):
        with Session(engine) as db:
            _make_expense(db, "Third", "30.00", datetime(2026, 3, 1, tzinfo=timezone.utc))
            _make_expense(db, "First", "10.00", datetime(2026, 1, 1, tzinfo=timezone.utc))
            _make_expense(db, "Second", "20.00", datetime(2026, 2, 1, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report")
        self.assertEqual(res.status_code, 200)
        expenses = res.json()["expenses"]
        self.assertEqual(expenses[0]["description"], "First")
        self.assertEqual(expenses[1]["description"], "Second")
        self.assertEqual(expenses[2]["description"], "Third")

    # ----------------------------------------------------------
    # Response structure
    # ----------------------------------------------------------

    def test_response_includes_all_required_fields(self):
        with Session(engine) as db:
            _make_expense(db, "Structural test", "100.00", datetime(2026, 9, 1, tzinfo=timezone.utc))

        res = self.client.get("/insurance/report")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        for key in ["start_date", "end_date", "expenses", "incomes",
                    "total_expense", "total_income", "net",
                    "expense_count", "income_count"]:
            self.assertIn(key, data)

        expense = data["expenses"][0]
        for key in ["id", "description", "price", "created_at"]:
            self.assertIn(key, expense)


if __name__ == "__main__":
    unittest.main()
