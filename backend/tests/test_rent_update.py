import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.rent import Rent

from app.services.rent import create_rent
from app.services.rent_update import update_rent


class RentUpdateTests(unittest.TestCase):

    def create_test_rent(self, db):
        rent = create_rent(
            db=db,
            amount=Decimal("2000.00"),
            year=2026,
            month=8,
            created_by=1,
        )

        db.flush()

        return rent

    # ---------------------------------------------------------
    # UPDATE AMOUNT
    # ---------------------------------------------------------

    def test_update_amount(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            update_rent(
                db=db,
                rent_id=rent.id,
                amount=Decimal("2500.00"),
            )

            self.assertEqual(
                rent.amount,
                Decimal("2500.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # ZERO AMOUNT
    # ---------------------------------------------------------

    def test_zero_amount_is_allowed(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            update_rent(
                db=db,
                rent_id=rent.id,
                amount=Decimal("0.00"),
            )

            self.assertEqual(
                rent.amount,
                Decimal("0.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NEGATIVE AMOUNT
    # ---------------------------------------------------------

    def test_negative_amount_is_rejected(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            with self.assertRaisesRegex(
                ValueError,
                "Rent amount cannot be negative",
            ):
                update_rent(
                    db=db,
                    rent_id=rent.id,
                    amount=Decimal("-500.00"),
                )

            self.assertEqual(
                rent.amount,
                Decimal("2000.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_rent_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Rent not found",
            ):
                update_rent(
                    db=db,
                    rent_id=999999,
                    amount=Decimal("2500.00"),
                )

            db.rollback()

    # ---------------------------------------------------------
    # YEAR AND MONTH REMAIN UNCHANGED
    # ---------------------------------------------------------

    def test_year_and_month_remain_unchanged(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            original_year = rent.year
            original_month = rent.month

            update_rent(
                db=db,
                rent_id=rent.id,
                amount=Decimal("3000.00"),
            )

            self.assertEqual(
                rent.year,
                original_year,
            )

            self.assertEqual(
                rent.month,
                original_month,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            rent_id = rent.id

            update_rent(
                db=db,
                rent_id=rent_id,
                amount=Decimal("3000.00"),
            )

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
                Decimal("3000.00"),
            )

            self.assertEqual(
                saved_rent.year,
                2026,
            )

            self.assertEqual(
                saved_rent.month,
                8,
            )

            # Clean up.
            db.delete(saved_rent)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            # Commit the original rent first.
            # Rollback must only undo the update.
            db.commit()

            rent_id = rent.id

            update_rent(
                db=db,
                rent_id=rent_id,
                amount=Decimal("5000.00"),
            )

            db.rollback()

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
                Decimal("2000.00"),
            )

            self.assertEqual(
                saved_rent.year,
                2026,
            )

            self.assertEqual(
                saved_rent.month,
                8,
            )

            # Clean up.
            db.delete(saved_rent)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )