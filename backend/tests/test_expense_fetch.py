import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.expense import Expense

from app.services.expense_fetch import (
    get_expenses,
    get_expenses_this_month,
)


class ExpenseFetchTests(unittest.TestCase):

    def create_test_expense(
        self,
        db,
        description="Office Supplies",
        amount="100.00",
    ):
        expense = Expense(
            description=description,
            amount=Decimal(amount),
            created_by=1,
        )

        db.add(expense)
        db.flush()

        return expense

    def cleanup_expenses(self, db):
        expenses = db.scalars(
            select(Expense)
        ).all()

        for expense in expenses:
            db.delete(expense)

        db.commit()

    # ---------------------------------------------------------
    # ALL TIME
    # ---------------------------------------------------------

    def test_get_all_active_expenses(self):

        with Session(engine) as db:

            expense1 = self.create_test_expense(
                db,
                description="Office Supplies",
                amount="100.00",
            )

            expense2 = self.create_test_expense(
                db,
                description="Car Wash",
                amount="200.00",
            )

            db.commit()

            result = get_expenses(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                2,
            )

            self.assertEqual(
                len(result["expenses"]),
                2,
            )

            descriptions = {
                expense["description"]
                for expense in result["expenses"]
            }

            self.assertIn(
                "Office Supplies",
                descriptions,
            )

            self.assertIn(
                "Car Wash",
                descriptions,
            )

            self.cleanup_expenses(db)

    # ---------------------------------------------------------
    # INACTIVE EXPENSES ARE EXCLUDED
    # ---------------------------------------------------------

    def test_inactive_expenses_are_excluded(self):

        with Session(engine) as db:

            active_expense = self.create_test_expense(
                db,
                description="Active Expense",
            )

            inactive_expense = self.create_test_expense(
                db,
                description="Deleted Expense",
            )

            inactive_expense.is_active = False

            db.commit()

            result = get_expenses(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                len(result["expenses"]),
                1,
            )

            self.assertEqual(
                result["expenses"][0]["id"],
                active_expense.id,
            )

            self.cleanup_expenses(db)

    # ---------------------------------------------------------
    # THIS MONTH
    # ---------------------------------------------------------

    def test_get_expenses_this_month(self):

        with Session(engine) as db:

            expense = self.create_test_expense(
                db,
                description="This Month Expense",
            )

            db.commit()

            result = get_expenses_this_month(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["expenses"][0]["id"],
                expense.id,
            )

            self.cleanup_expenses(db)

    # ---------------------------------------------------------
    # DATE RANGE
    # ---------------------------------------------------------

    def test_date_range_returns_matching_expenses(self):

        with Session(engine) as db:

            expense1 = self.create_test_expense(
                db,
                description="July Expense",
            )

            expense2 = self.create_test_expense(
                db,
                description="August Expense",
            )

            expense1.created_at = datetime(
                2026,
                7,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            )

            expense2.created_at = datetime(
                2026,
                8,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            )

            db.commit()

            result = get_expenses(
                db=db,
                start_date=date(2026, 7, 1),
                end_date=date(2026, 7, 31),
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["expenses"][0]["id"],
                expense1.id,
            )

            self.cleanup_expenses(db)

    # ---------------------------------------------------------
    # END DATE IS INCLUSIVE
    # ---------------------------------------------------------

    def test_end_date_includes_entire_day(self):

        with Session(engine) as db:

            expense = self.create_test_expense(
                db,
                description="End Day Expense",
            )

            expense.created_at = datetime(
                2026,
                8,
                19,
                23,
                59,
                59,
                tzinfo=timezone.utc,
            )

            db.commit()

            result = get_expenses(
                db=db,
                start_date=date(2026, 8, 19),
                end_date=date(2026, 8, 19),
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["expenses"][0]["id"],
                expense.id,
            )

            self.cleanup_expenses(db)

    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    def test_pagination_works(self):

        with Session(engine) as db:

            for index in range(15):

                self.create_test_expense(
                    db,
                    description=f"Expense {index}",
                )

            db.commit()

            result = get_expenses(
                db=db,
                limit=10,
                offset=5,
            )

            self.assertEqual(
                len(result["expenses"]),
                10,
            )

            self.assertEqual(
                result["pagination"]["limit"],
                10,
            )

            self.assertEqual(
                result["pagination"]["offset"],
                5,
            )

            self.assertEqual(
                result["pagination"]["total"],
                15,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup_expenses(db)

    # ---------------------------------------------------------
    # FEWER RECORDS THAN LIMIT
    # ---------------------------------------------------------

    def test_remaining_records_are_returned(self):

        with Session(engine) as db:

            for index in range(16):

                self.create_test_expense(
                    db,
                    description=f"Expense {index}",
                )

            db.commit()

            result = get_expenses(
                db=db,
                limit=10,
                offset=10,
            )

            self.assertEqual(
                len(result["expenses"]),
                6,
            )

            self.assertEqual(
                result["pagination"]["total"],
                16,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup_expenses(db)

    # ---------------------------------------------------------
    # OFFSET BEYOND RECORDS
    # ---------------------------------------------------------

    def test_offset_beyond_records_returns_empty_list(self):

        with Session(engine) as db:

            for index in range(5):

                self.create_test_expense(
                    db,
                    description=f"Expense {index}",
                )

            db.commit()

            result = get_expenses(
                db=db,
                limit=10,
                offset=10,
            )

            self.assertEqual(
                len(result["expenses"]),
                0,
            )

            self.assertEqual(
                result["pagination"]["total"],
                5,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup_expenses(db)

    # ---------------------------------------------------------
    # ZERO LIMIT
    # ---------------------------------------------------------

    def test_zero_limit_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Limit must be greater than zero",
            ):
                get_expenses(
                    db=db,
                    limit=0,
                )

    # ---------------------------------------------------------
    # NEGATIVE OFFSET
    # ---------------------------------------------------------

    def test_negative_offset_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Offset cannot be negative",
            ):
                get_expenses(
                    db=db,
                    offset=-1,
                )

    # ---------------------------------------------------------
    # INVALID DATE RANGE
    # ---------------------------------------------------------

    def test_invalid_date_range_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Start date cannot be after end date",
            ):
                get_expenses(
                    db=db,
                    start_date=date(2026, 8, 20),
                    end_date=date(2026, 8, 1),
                )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )