import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.expense import Expense

from app.services.expense import create_expense


class ExpenseTests(unittest.TestCase):

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_create_expense_successfully(self):
        with Session(engine) as db:

            expense = create_expense(
                db=db,
                description="Office Supplies",
                amount=Decimal("250.00"),
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                expense.id
            )

            self.assertEqual(
                expense.description,
                "Office Supplies",
            )

            self.assertEqual(
                expense.amount,
                Decimal("250.00"),
            )

            self.assertEqual(
                expense.created_by,
                1,
            )

            self.assertIsNotNone(
                expense.created_at
            )

            self.assertIsNotNone(
                expense.updated_at
            )

            db.rollback()

    # ---------------------------------------------------------
    # DESCRIPTION
    # ---------------------------------------------------------

    def test_description_is_trimmed(self):
        with Session(engine) as db:

            expense = create_expense(
                db=db,
                description="  Office Supplies  ",
                amount=250,
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                expense.description,
                "Office Supplies",
            )

            db.rollback()

    def test_empty_description_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "description is required",
            ):

                create_expense(
                    db=db,
                    description="",
                    amount=250,
                    created_by=1,
                )

            db.rollback()

    def test_whitespace_description_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "description is required",
            ):

                create_expense(
                    db=db,
                    description="   ",
                    amount=250,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # AMOUNT
    # ---------------------------------------------------------

    def test_zero_amount_is_allowed(self):
        with Session(engine) as db:

            expense = create_expense(
                db=db,
                description="Free Service",
                amount=0,
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                expense.amount,
                Decimal("0"),
            )

            db.rollback()

    def test_negative_amount_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "amount cannot be negative",
            ):

                create_expense(
                    db=db,
                    description="Invalid Expense",
                    amount=-100,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # DUPLICATES ARE ALLOWED
    # ---------------------------------------------------------

    def test_duplicate_expenses_are_allowed(self):
        with Session(engine) as db:

            expense_1 = create_expense(
                db=db,
                description="Fuel",
                amount=Decimal("100.00"),
                created_by=1,
            )

            expense_2 = create_expense(
                db=db,
                description="Fuel",
                amount=Decimal("100.00"),
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                expense_1.id
            )

            self.assertIsNotNone(
                expense_2.id
            )

            self.assertNotEqual(
                expense_1.id,
                expense_2.id,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_expense_is_saved_after_commit(self):
        with Session(engine) as db:

            expense = create_expense(
                db=db,
                description="Repair Supplies",
                amount=Decimal("500.00"),
                created_by=1,
            )

            db.flush()

            expense_id = expense.id

            db.commit()

            saved_expense = db.scalar(
                select(Expense).where(
                    Expense.id == expense_id
                )
            )

            self.assertIsNotNone(
                saved_expense
            )

            self.assertEqual(
                saved_expense.description,
                "Repair Supplies",
            )

            self.assertEqual(
                saved_expense.amount,
                Decimal("500.00"),
            )

            # Clean up committed test data.
            db.delete(saved_expense)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_expense_can_be_rolled_back(self):
        with Session(engine) as db:

            expense = create_expense(
                db=db,
                description="Rollback Expense",
                amount=Decimal("500.00"),
                created_by=1,
            )

            db.flush()

            expense_id = expense.id

            db.rollback()

            saved_expense = db.scalar(
                select(Expense).where(
                    Expense.id == expense_id
                )
            )

            self.assertIsNone(
                saved_expense
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )