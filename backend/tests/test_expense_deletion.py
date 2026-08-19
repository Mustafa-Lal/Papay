import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.expense import Expense

from app.services.expense import create_expense
from app.services.expense_deletion import deactivate_expense


class ExpenseDeleteTests(unittest.TestCase):

    def create_test_expense(
        self,
        db,
        description="Original Expense",
        amount=Decimal("500.00"),
    ):
        expense = create_expense(
            db=db,
            description=description,
            amount=amount,
            created_by=1,
        )

        db.flush()

        return expense

    # ---------------------------------------------------------
    # EXPENSE IS DEACTIVATED
    # ---------------------------------------------------------

    def test_expense_is_deactivated(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            expense_id = expense.id

            self.assertTrue(
                expense.is_active
            )

            deactivate_expense(
                db=db,
                expense_id=expense_id,
            )

            self.assertFalse(
                expense.is_active
            )

            db.rollback()

    # ---------------------------------------------------------
    # DEACTIVATION IS PERSISTED
    # ---------------------------------------------------------

    def test_deactivation_is_persisted_after_commit(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            expense_id = expense.id

            deactivate_expense(
                db=db,
                expense_id=expense_id,
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

            self.assertFalse(
                saved_expense.is_active
            )

            # Clean up.
            db.delete(saved_expense)
            db.commit()

    # ---------------------------------------------------------
    # NONEXISTENT EXPENSE
    # ---------------------------------------------------------

    def test_nonexistent_expense_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Expense not found",
            ):
                deactivate_expense(
                    db=db,
                    expense_id=999999,
                )

            db.rollback()

    # ---------------------------------------------------------
    # OTHER EXPENSE REMAINS ACTIVE
    # ---------------------------------------------------------

    def test_other_expense_remains_active(self):
        with Session(engine) as db:

            expense1 = self.create_test_expense(
                db=db,
                description="Expense One",
                amount=Decimal("500.00"),
            )

            db.commit()

            expense2 = self.create_test_expense(
                db=db,
                description="Expense Two",
                amount=Decimal("700.00"),
            )

            db.flush()

            expense1_id = expense1.id
            expense2_id = expense2.id

            deactivate_expense(
                db=db,
                expense_id=expense1_id,
            )

            db.commit()

            deactivated_expense = db.scalar(
                select(Expense).where(
                    Expense.id == expense1_id
                )
            )

            remaining_expense = db.scalar(
                select(Expense).where(
                    Expense.id == expense2_id
                )
            )

            self.assertIsNotNone(
                deactivated_expense
            )

            self.assertFalse(
                deactivated_expense.is_active
            )

            self.assertIsNotNone(
                remaining_expense
            )

            self.assertTrue(
                remaining_expense.is_active
            )

            # Clean up.
            db.delete(deactivated_expense)
            db.delete(remaining_expense)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_deactivation_can_be_rolled_back(self):
        with Session(engine) as db:

            expense = self.create_test_expense(db)

            expense_id = expense.id

            # Commit original active expense.
            db.commit()

            deactivate_expense(
                db=db,
                expense_id=expense_id,
            )

            self.assertFalse(
                expense.is_active
            )

            # Undo deactivation.
            db.rollback()

            restored_expense = db.scalar(
                select(Expense).where(
                    Expense.id == expense_id
                )
            )

            self.assertIsNotNone(
                restored_expense
            )

            self.assertTrue(
                restored_expense.is_active
            )

            # Clean up.
            db.delete(restored_expense)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )