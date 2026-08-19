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
from app.services.utility_bill_deletion import delete_utility_bill


class UtilityBillDeleteTests(unittest.TestCase):

    def create_test_bill(
        self,
        db,
        bill_type=UtilityBillType.INTERNET,
        amount=Decimal("300.00"),
        year=2026,
        month=8,
    ):
        bill = create_utility_bill(
            db=db,
            bill_type=bill_type,
            amount=amount,
            year=year,
            month=month,
            created_by=1,
        )

        db.flush()

        return bill

    # ---------------------------------------------------------
    # DELETE BILL
    # ---------------------------------------------------------

    def test_bill_is_deleted(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            bill_id = bill.id

            delete_utility_bill(
                db=db,
                bill_id=bill_id,
            )

            db.commit()

            saved_bill = db.scalar(
                select(UtilityBill).where(
                    UtilityBill.id == bill_id
                )
            )

            self.assertIsNone(
                saved_bill
            )

    # ---------------------------------------------------------
    # NONEXISTENT BILL
    # ---------------------------------------------------------

    def test_nonexistent_bill_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Utility bill not found",
            ):
                delete_utility_bill(
                    db=db,
                    bill_id=999999,
                )

            db.rollback()

    # ---------------------------------------------------------
    # OTHER BILL REMAINS
    # ---------------------------------------------------------

    def test_other_bill_remains(self):
        with Session(engine) as db:

            internet_bill = self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.INTERNET,
            )

            db.commit()

            electricity_bill = self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.ELECTRICITY,
                amount=Decimal("500.00"),
            )

            db.flush()

            internet_id = internet_bill.id
            electricity_id = electricity_bill.id

            delete_utility_bill(
                db=db,
                bill_id=internet_id,
            )

            db.commit()

            deleted_bill = db.scalar(
                select(UtilityBill).where(
                    UtilityBill.id == internet_id
                )
            )

            remaining_bill = db.scalar(
                select(UtilityBill).where(
                    UtilityBill.id == electricity_id
                )
            )

            self.assertIsNone(
                deleted_bill
            )

            self.assertIsNotNone(
                remaining_bill
            )

            self.assertEqual(
                remaining_bill.bill_type,
                UtilityBillType.ELECTRICITY,
            )

            self.assertEqual(
                remaining_bill.amount,
                Decimal("500.00"),
            )

            # Clean up.
            db.delete(remaining_bill)
            db.commit()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_delete_is_persisted_after_commit(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            bill_id = bill.id

            delete_utility_bill(
                db=db,
                bill_id=bill_id,
            )

            db.commit()

        with Session(engine) as db:

            saved_bill = db.scalar(
                select(UtilityBill).where(
                    UtilityBill.id == bill_id
                )
            )

            self.assertIsNone(
                saved_bill
            )

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_delete_can_be_rolled_back(self):
        with Session(engine) as db:

            bill = self.create_test_bill(db)

            bill_id = bill.id

            # Commit original record first.
            db.commit()

            delete_utility_bill(
                db=db,
                bill_id=bill_id,
            )

            # Undo deletion.
            db.rollback()

            restored_bill = db.scalar(
                select(UtilityBill).where(
                    UtilityBill.id == bill_id
                )
            )

            self.assertIsNotNone(
                restored_bill
            )

            self.assertEqual(
                restored_bill.bill_type,
                UtilityBillType.INTERNET,
            )

            self.assertEqual(
                restored_bill.amount,
                Decimal("300.00"),
            )

            self.assertEqual(
                restored_bill.year,
                2026,
            )

            self.assertEqual(
                restored_bill.month,
                8,
            )

            # Clean up.
            db.delete(restored_bill)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )