import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.rent import Rent

from app.services.rent_fetch import get_rent


class RentFetchTests(unittest.TestCase):

    def create_test_rent(
        self,
        db,
        year=2026,
        month=8,
        amount="5000.00",
    ):
        rent = Rent(
            amount=Decimal(amount),
            year=year,
            month=month,
            created_by=1,
        )

        db.add(rent)
        db.flush()

        return rent

    def cleanup_rents(self, db):
        rents = db.scalars(
            select(Rent)
        ).all()

        for rent in rents:
            db.delete(rent)

        db.commit()

    # ---------------------------------------------------------
    # FETCH RENT FOR MONTH
    # ---------------------------------------------------------

    def test_rent_is_returned_for_requested_month(self):

        with Session(engine) as db:

            rent = self.create_test_rent(
                db=db,
                year=2026,
                month=8,
                amount="5000.00",
            )

            db.commit()

            result = get_rent(
                db=db,
                year=2026,
                month=8,
            )

            self.assertEqual(
                result.id,
                rent.id,
            )

            self.assertEqual(
                result.amount,
                Decimal("5000.00"),
            )

            self.assertEqual(
                result.year,
                2026,
            )

            self.assertEqual(
                result.month,
                8,
            )

            self.cleanup_rents(db)

    # ---------------------------------------------------------
    # DIFFERENT MONTH
    # ---------------------------------------------------------

    def test_different_month_does_not_return_rent(self):

        with Session(engine) as db:

            rent = self.create_test_rent(
                db=db,
                year=2026,
                month=8,
            )

            db.commit()

            with self.assertRaisesRegex(
                ValueError,
                "Rent not found for the requested month",
            ):
                get_rent(
                    db=db,
                    year=2026,
                    month=7,
                )

            self.cleanup_rents(db)

    # ---------------------------------------------------------
    # DIFFERENT YEAR
    # ---------------------------------------------------------

    def test_different_year_does_not_return_rent(self):

        with Session(engine) as db:

            rent = self.create_test_rent(
                db=db,
                year=2026,
                month=8,
            )

            db.commit()

            with self.assertRaisesRegex(
                ValueError,
                "Rent not found for the requested month",
            ):
                get_rent(
                    db=db,
                    year=2025,
                    month=8,
                )

            self.cleanup_rents(db)

    # ---------------------------------------------------------
    # NONEXISTENT RENT
    # ---------------------------------------------------------

    def test_nonexistent_rent_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Rent not found for the requested month",
            ):
                get_rent(
                    db=db,
                    year=2026,
                    month=12,
                )

    # ---------------------------------------------------------
    # INVALID MONTH - ZERO
    # ---------------------------------------------------------

    def test_zero_month_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Month must be between 1 and 12",
            ):
                get_rent(
                    db=db,
                    year=2026,
                    month=0,
                )

    # ---------------------------------------------------------
    # INVALID MONTH - ABOVE 12
    # ---------------------------------------------------------

    def test_month_above_twelve_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Month must be between 1 and 12",
            ):
                get_rent(
                    db=db,
                    year=2026,
                    month=13,
                )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )