import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.rent import Rent

from app.services.rent import create_rent
from app.services.rent_deletion import delete_rent


class RentDeleteTests(unittest.TestCase):

    def create_test_rent(
        self,
        db,
        amount=Decimal("2000.00"),
        year=2026,
        month=8,
    ):
        rent = create_rent(
            db=db,
            amount=amount,
            year=year,
            month=month,
            created_by=1,
        )

        db.flush()

        return rent

    # ---------------------------------------------------------
    # DELETE RENT
    # ---------------------------------------------------------

    def test_rent_is_deleted(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            rent_id = rent.id

            delete_rent(
                db=db,
                rent_id=rent_id,
            )

            db.commit()

            saved_rent = db.scalar(
                select(Rent).where(
                    Rent.id == rent_id
                )
            )

            self.assertIsNone(
                saved_rent
            )

    # ---------------------------------------------------------
    # NONEXISTENT RENT
    # ---------------------------------------------------------

    def test_nonexistent_rent_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Rent not found",
            ):
                delete_rent(
                    db=db,
                    rent_id=999999,
                )

            db.rollback()

    # ---------------------------------------------------------
    # OTHER RENT REMAINS
    # ---------------------------------------------------------

    def test_other_rent_remains(self):
        with Session(engine) as db:

            rent1 = self.create_test_rent(
                db=db,
                amount=Decimal("2000.00"),
                year=2026,
                month=8,
            )

            db.commit()

            rent2 = self.create_test_rent(
                db=db,
                amount=Decimal("2500.00"),
                year=2026,
                month=7,
            )

            db.flush()

            rent1_id = rent1.id
            rent2_id = rent2.id

            delete_rent(
                db=db,
                rent_id=rent1_id,
            )

            db.commit()

            deleted_rent = db.scalar(
                select(Rent).where(
                    Rent.id == rent1_id
                )
            )

            remaining_rent = db.scalar(
                select(Rent).where(
                    Rent.id == rent2_id
                )
            )

            self.assertIsNone(
                deleted_rent
            )

            self.assertIsNotNone(
                remaining_rent
            )

            self.assertEqual(
                remaining_rent.amount,
                Decimal("2500.00"),
            )

            # Clean up.
            db.delete(remaining_rent)
            db.commit()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_delete_is_persisted_after_commit(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            rent_id = rent.id

            delete_rent(
                db=db,
                rent_id=rent_id,
            )

            db.commit()

        # New session verifies that the deletion
        # really persisted to the database.
        with Session(engine) as db:

            saved_rent = db.scalar(
                select(Rent).where(
                    Rent.id == rent_id
                )
            )

            self.assertIsNone(
                saved_rent
            )

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_delete_can_be_rolled_back(self):
        with Session(engine) as db:

            rent = self.create_test_rent(db)

            rent_id = rent.id

            # Commit original record first.
            db.commit()

            delete_rent(
                db=db,
                rent_id=rent_id,
            )

            # Undo deletion.
            db.rollback()

            restored_rent = db.scalar(
                select(Rent).where(
                    Rent.id == rent_id
                )
            )

            self.assertIsNotNone(
                restored_rent
            )

            self.assertEqual(
                restored_rent.amount,
                Decimal("2000.00"),
            )

            self.assertEqual(
                restored_rent.year,
                2026,
            )

            self.assertEqual(
                restored_rent.month,
                8,
            )

            # Clean up.
            db.delete(restored_rent)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )