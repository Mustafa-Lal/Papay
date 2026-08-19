import unittest
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.rent import Rent

from app.services.rent import create_rent


class RentTests(unittest.TestCase):

    def current_period(self):
        today = date.today()

        return today.year, today.month

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_create_rent_successfully(self):
        with Session(engine) as db:

            year, month = self.current_period()

            rent = create_rent(
                db=db,
                amount=Decimal("5000.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                rent.id
            )

            self.assertEqual(
                rent.amount,
                Decimal("5000.00"),
            )

            self.assertEqual(
                rent.year,
                year,
            )

            self.assertEqual(
                rent.month,
                month,
            )

            self.assertEqual(
                rent.created_by,
                1,
            )

            self.assertIsNotNone(
                rent.created_at
            )

            self.assertIsNotNone(
                rent.updated_at
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_rent_is_saved_after_commit(self):
        with Session(engine) as db:

            year, month = self.current_period()

            rent = create_rent(
                db=db,
                amount=Decimal("5000.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            rent_id = rent.id

            db.commit()

            saved_rent = db.scalar(
                select(Rent).where(
                    Rent.id == rent_id
                )
            )

            self.assertIsNotNone(
                saved_rent
            )

            self.assertEqual(
                saved_rent.amount,
                Decimal("5000.00"),
            )

            # Clean up because this test committed.
            db.delete(saved_rent)
            db.commit()

    # ---------------------------------------------------------
    # DUPLICATE MONTH
    # ---------------------------------------------------------

    def test_same_month_and_year_cannot_be_added_twice(self):
        with Session(engine) as db:

            year, month = self.current_period()

            create_rent(
                db=db,
                amount=Decimal("5000.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            with self.assertRaisesRegex(
                ValueError,
                "Rent already added",
            ):

                create_rent(
                    db=db,
                    amount=Decimal("6000.00"),
                    year=year,
                    month=month,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # FUTURE MONTH
    # ---------------------------------------------------------

    def test_future_month_is_rejected(self):
        with Session(engine) as db:

            today = date.today()

            if today.month == 12:
                future_year = today.year + 1
                future_month = 1
            else:
                future_year = today.year
                future_month = today.month + 1

            with self.assertRaisesRegex(
                ValueError,
                "future month",
            ):

                create_rent(
                    db=db,
                    amount=Decimal("5000.00"),
                    year=future_year,
                    month=future_month,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # INVALID MONTH
    # ---------------------------------------------------------

    def test_month_zero_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_rent(
                    db=db,
                    amount=Decimal("5000.00"),
                    year=2026,
                    month=0,
                    created_by=1,
                )

            db.rollback()

    def test_month_thirteen_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_rent(
                    db=db,
                    amount=Decimal("5000.00"),
                    year=2026,
                    month=13,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # NEGATIVE AMOUNT
    # ---------------------------------------------------------

    def test_negative_amount_is_rejected(self):
        with Session(engine) as db:

            year, month = self.current_period()

            with self.assertRaises(ValueError):

                create_rent(
                    db=db,
                    amount=Decimal("-100.00"),
                    year=year,
                    month=month,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_rent_can_be_rolled_back(self):
        with Session(engine) as db:

            year, month = self.current_period()

            rent = create_rent(
                db=db,
                amount=Decimal("5000.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            rent_id = rent.id

            db.rollback()

            saved_rent = db.scalar(
                select(Rent).where(
                    Rent.id == rent_id
                )
            )

            self.assertIsNone(
                saved_rent
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )