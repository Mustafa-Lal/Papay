import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.utility_bill import (
    UtilityBill,
    UtilityBillType,
)

from app.services.utility_bill import create_utility_bill
from app.services.utility_bill_update import update_utility_bill


class UtilityBillUpdateTests(unittest.TestCase):

    def create_test_bill(self, db):
        bill = create_utility_bill(
            db=db,
            bill_type=UtilityBillType.INTERNET,
            amount=Decimal("300.00"),
            year=2026,
            month=8,
            created_by=1,
        )

        db.flush()

        return bill

    # ---------------------------------------------------------
    # UPDATE AMOUNT
    # ---------------------------------------------------------

    def test_update_amount(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            update_utility_bill(
                db=db,
                bill_id=bill.id,
                amount=Decimal("350.00"),
            )

            self.assertEqual(
                bill.amount,
                Decimal("350.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # ZERO AMOUNT
    # ---------------------------------------------------------

    def test_zero_amount_is_allowed(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            update_utility_bill(
                db=db,
                bill_id=bill.id,
                amount=Decimal("0.00"),
            )

            self.assertEqual(
                bill.amount,
                Decimal("0.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NEGATIVE AMOUNT
    # ---------------------------------------------------------

    def test_negative_amount_is_rejected(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            with self.assertRaisesRegex(
                ValueError,
                "Utility bill amount cannot be negative",
            ):
                update_utility_bill(
                    db=db,
                    bill_id=bill.id,
                    amount=Decimal("-100.00"),
                )

            self.assertEqual(
                bill.amount,
                Decimal("300.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_bill_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Utility bill not found",
            ):
                update_utility_bill(
                    db=db,
                    bill_id=999999,
                    amount=Decimal("350.00"),
                )

            db.rollback()

    # ---------------------------------------------------------
    # IMMUTABLE FIELDS
    # ---------------------------------------------------------

    def test_bill_identity_remains_unchanged(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            original_bill_type = bill.bill_type
            original_year = bill.year
            original_month = bill.month

            update_utility_bill(
                db=db,
                bill_id=bill.id,
                amount=Decimal("400.00"),
            )

            self.assertEqual(
                bill.bill_type,
                original_bill_type,
            )

            self.assertEqual(
                bill.year,
                original_year,
            )

            self.assertEqual(
                bill.month,
                original_month,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            bill_id = bill.id

            update_utility_bill(
                db=db,
                bill_id=bill_id,
                amount=Decimal("450.00"),
            )

            db.commit()

            saved_bill = db.scalar(
                select(UtilityBill).where(
                    UtilityBill.id == bill_id
                )
            )

            self.assertIsNotNone(
                saved_bill
            )

            self.assertEqual(
                saved_bill.amount,
                Decimal("450.00"),
            )

            self.assertEqual(
                saved_bill.bill_type,
                UtilityBillType.INTERNET,
            )

            self.assertEqual(
                saved_bill.year,
                2026,
            )

            self.assertEqual(
                saved_bill.month,
                8,
            )

            # Clean up.
            db.delete(saved_bill)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            # Commit the original bill first.
            # Rollback must only undo the update.
            db.commit()

            bill_id = bill.id

            update_utility_bill(
                db=db,
                bill_id=bill_id,
                amount=Decimal("999.00"),
            )

            db.rollback()

            saved_bill = db.scalar(
                select(UtilityBill).where(
                    UtilityBill.id == bill_id
                )
            )

            self.assertIsNotNone(
                saved_bill
            )

            self.assertEqual(
                saved_bill.amount,
                Decimal("300.00"),
            )

            self.assertEqual(
                saved_bill.bill_type,
                UtilityBillType.INTERNET,
            )

            self.assertEqual(
                saved_bill.year,
                2026,
            )

            self.assertEqual(
                saved_bill.month,
                8,
            )

            # Clean up.
            db.delete(saved_bill)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )