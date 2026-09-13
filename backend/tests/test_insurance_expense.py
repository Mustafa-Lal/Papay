import unittest
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_expense import InsuranceExpense
from app.services.insurance_expense import create_insurance_expense


class InsuranceExpenseTests(unittest.TestCase):

    def test_create_insurance_expense_successfully(self):
        with Session(engine) as db:
            expense = create_insurance_expense(
                db=db,
                description="Towing service fee",
                price=Decimal("450.00"),
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(expense.id)
            self.assertEqual(expense.description, "Towing service fee")
            self.assertEqual(expense.price, Decimal("450.00"))
            self.assertEqual(expense.created_by, 1)
            self.assertTrue(expense.is_active)
            self.assertIsNotNone(expense.created_at)
            self.assertIsNotNone(expense.updated_at)

            db.rollback()

    def test_description_is_trimmed(self):
        with Session(engine) as db:
            expense = create_insurance_expense(
                db=db,
                description="   Inspection charges   ",
                price=Decimal("120.00"),
                created_by=1,
            )

            db.flush()
            self.assertEqual(expense.description, "Inspection charges")
            db.rollback()

    def test_empty_description_is_rejected(self):
        with Session(engine) as db:
            with self.assertRaisesRegex(ValueError, "description is required"):
                create_insurance_expense(
                    db=db,
                    description="",
                    price=Decimal("100.00"),
                    created_by=1,
                )
            db.rollback()

    def test_whitespace_description_is_rejected(self):
        with Session(engine) as db:
            with self.assertRaisesRegex(ValueError, "description is required"):
                create_insurance_expense(
                    db=db,
                    description="    ",
                    price=Decimal("100.00"),
                    created_by=1,
                )
            db.rollback()

    def test_zero_price_is_allowed(self):
        with Session(engine) as db:
            expense = create_insurance_expense(
                db=db,
                description="Free appraisal",
                price=Decimal("0.00"),
                created_by=1,
            )
            db.flush()
            self.assertEqual(expense.price, Decimal("0.00"))
            db.rollback()

    def test_negative_price_is_rejected(self):
        with Session(engine) as db:
            with self.assertRaisesRegex(ValueError, "price cannot be negative"):
                create_insurance_expense(
                    db=db,
                    description="Invalid fee",
                    price=Decimal("-10.00"),
                    created_by=1,
                )
            db.rollback()
