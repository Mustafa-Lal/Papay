import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.expense import Expense

from app.services.expense import create_expense
from app.services.expense_update import update_expense


class ExpenseUpdateTests(unittest.TestCase):

    def create_test_expense(self, db):
        expense = create_expense(
            db=db,
            description="Original Expense",
            amount=Decimal("500.00"),
            created_by=1,
        )

        db.flush()

        return expense

    # ---------------------------------------------------------
    # UPDATE DESCRIPTION
    # ---------------------------------------------------------

    def test_update_description(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            update_expense(
                db=db,
                expense_id=expense.id,
                description="Updated Expense",
            )

            self.assertEqual(
                expense.description,
                "Updated Expense",
            )

            self.assertEqual(
                expense.amount,
                Decimal("500.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE AMOUNT
    # ---------------------------------------------------------

    def test_update_amount(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            update_expense(
                db=db,
                expense_id=expense.id,
                amount=Decimal("750.00"),
            )

            self.assertEqual(
                expense.amount,
                Decimal("750.00"),
            )

            self.assertEqual(
                expense.description,
                "Original Expense",
            )

            db.rollback()

    # ---------------------------------------------------------
    # ZERO AMOUNT
    # ---------------------------------------------------------

    def test_zero_amount_is_allowed(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            update_expense(
                db=db,
                expense_id=expense.id,
                amount=Decimal("0.00"),
            )

            self.assertEqual(
                expense.amount,
                Decimal("0.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NEGATIVE AMOUNT
    # ---------------------------------------------------------

    def test_negative_amount_is_rejected(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            with self.assertRaisesRegex(
                ValueError,
                "Expense amount cannot be negative",
            ):
                update_expense(
                    db=db,
                    expense_id=expense.id,
                    amount=Decimal("-100.00"),
                )

            self.assertEqual(
                expense.amount,
                Decimal("500.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # EMPTY DESCRIPTION
    # ---------------------------------------------------------

    def test_empty_description_is_rejected(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            with self.assertRaisesRegex(
                ValueError,
                "Expense description cannot be empty",
            ):
                update_expense(
                    db=db,
                    expense_id=expense.id,
                    description="",
                )

            self.assertEqual(
                expense.description,
                "Original Expense",
            )

            db.rollback()

    # ---------------------------------------------------------
    # WHITESPACE DESCRIPTION
    # ---------------------------------------------------------

    def test_whitespace_description_is_rejected(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            with self.assertRaisesRegex(
                ValueError,
                "Expense description cannot be empty",
            ):
                update_expense(
                    db=db,
                    expense_id=expense.id,
                    description="   ",
                )

            self.assertEqual(
                expense.description,
                "Original Expense",
            )

            db.rollback()

    # ---------------------------------------------------------
    # DESCRIPTION TRIMMING
    # ---------------------------------------------------------

    def test_updated_description_is_trimmed(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            update_expense(
                db=db,
                expense_id=expense.id,
                description="  Updated Expense  ",
            )

            self.assertEqual(
                expense.description,
                "Updated Expense",
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE ALL FIELDS
    # ---------------------------------------------------------

    def test_update_all_expense_fields(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            update_expense(
                db=db,
                expense_id=expense.id,
                description="New Expense",
                amount=Decimal("900.00"),
            )

            self.assertEqual(
                expense.description,
                "New Expense",
            )

            self.assertEqual(
                expense.amount,
                Decimal("900.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # PARTIAL UPDATE
    # ---------------------------------------------------------

    def test_partial_update_does_not_change_other_fields(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            update_expense(
                db=db,
                expense_id=expense.id,
                description="Only Description Changed",
            )

            self.assertEqual(
                expense.description,
                "Only Description Changed",
            )

            self.assertEqual(
                expense.amount,
                Decimal("500.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_expense_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Expense not found",
            ):
                update_expense(
                    db=db,
                    expense_id=999999,
                    description="New Expense",
                )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            expense_id = expense.id

            update_expense(
                db=db,
                expense_id=expense_id,
                description="Persisted Expense",
                amount=Decimal("1000.00"),
            )

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
                "Persisted Expense",
            )

            self.assertEqual(
                saved_expense.amount,
                Decimal("1000.00"),
            )

            # Clean up.
            db.delete(saved_expense)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            # Commit the original expense first.
            # Rollback must only undo the update.
            db.commit()

            expense_id = expense.id

            update_expense(
                db=db,
                expense_id=expense_id,
                description="Temporary Expense",
                amount=Decimal("9999.00"),
            )

            db.rollback()

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
                "Original Expense",
            )

            self.assertEqual(
                saved_expense.amount,
                Decimal("500.00"),
            )

            # Clean up.
            db.delete(saved_expense)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )