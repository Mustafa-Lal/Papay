import unittest
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.utility_bill import (
    UtilityBill,
    UtilityBillType,
)

from app.services.utility_bill import (
    create_utility_bill,
)


class UtilityBillTests(unittest.TestCase):

    def current_period(self):
        today = date.today()

        return today.year, today.month

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_create_internet_bill_successfully(self):
        with Session(engine) as db:

            year, month = self.current_period()

            bill = create_utility_bill(
                db=db,
                bill_type=UtilityBillType.INTERNET,
                amount=Decimal("500.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                bill.id
            )

            self.assertEqual(
                bill.bill_type,
                UtilityBillType.INTERNET,
            )

            self.assertEqual(
                bill.amount,
                Decimal("500.00"),
            )

            self.assertEqual(
                bill.year,
                year,
            )

            self.assertEqual(
                bill.month,
                month,
            )

            self.assertEqual(
                bill.created_by,
                1,
            )

            self.assertIsNotNone(
                bill.created_at
            )

            self.assertIsNotNone(
                bill.updated_at
            )

            db.rollback()

    def test_create_electricity_bill_successfully(self):
        with Session(engine) as db:

            year, month = self.current_period()

            bill = create_utility_bill(
                db=db,
                bill_type=UtilityBillType.ELECTRICITY,
                amount=Decimal("1200.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                bill.id
            )

            self.assertEqual(
                bill.bill_type,
                UtilityBillType.ELECTRICITY,
            )

            db.rollback()

    def test_create_water_bill_successfully(self):
        with Session(engine) as db:

            year, month = self.current_period()

            bill = create_utility_bill(
                db=db,
                bill_type=UtilityBillType.WATER,
                amount=Decimal("300.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                bill.id
            )

            self.assertEqual(
                bill.bill_type,
                UtilityBillType.WATER,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_bill_is_saved_after_commit(self):
        with Session(engine) as db:

            year, month = self.current_period()

            bill = create_utility_bill(
                db=db,
                bill_type=UtilityBillType.INTERNET,
                amount=Decimal("500.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            bill_id = bill.id

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
                Decimal("500.00"),
            )

            # Clean up committed test data.
            db.delete(saved_bill)
            db.commit()

    # ---------------------------------------------------------
    # DUPLICATE
    # ---------------------------------------------------------

    def test_same_bill_type_and_month_cannot_be_added_twice(self):
        with Session(engine) as db:

            year, month = self.current_period()

            create_utility_bill(
                db=db,
                bill_type=UtilityBillType.INTERNET,
                amount=Decimal("500.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            with self.assertRaisesRegex(
                ValueError,
                "already been added",
            ):

                create_utility_bill(
                    db=db,
                    bill_type=UtilityBillType.INTERNET,
                    amount=Decimal("600.00"),
                    year=year,
                    month=month,
                    created_by=1,
                )

            db.rollback()

    def test_different_bill_types_can_exist_for_same_month(self):
        with Session(engine) as db:

            year, month = self.current_period()

            internet = create_utility_bill(
                db=db,
                bill_type=UtilityBillType.INTERNET,
                amount=Decimal("500.00"),
                year=year,
                month=month,
                created_by=1,
            )

            electricity = create_utility_bill(
                db=db,
                bill_type=UtilityBillType.ELECTRICITY,
                amount=Decimal("1200.00"),
                year=year,
                month=month,
                created_by=1,
            )

            water = create_utility_bill(
                db=db,
                bill_type=UtilityBillType.WATER,
                amount=Decimal("300.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                internet.id
            )

            self.assertIsNotNone(
                electricity.id
            )

            self.assertIsNotNone(
                water.id
            )

            self.assertNotEqual(
                internet.id,
                electricity.id,
            )

            self.assertNotEqual(
                electricity.id,
                water.id,
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

                create_utility_bill(
                    db=db,
                    bill_type=UtilityBillType.INTERNET,
                    amount=Decimal("500.00"),
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

                create_utility_bill(
                    db=db,
                    bill_type=UtilityBillType.INTERNET,
                    amount=Decimal("500.00"),
                    year=2026,
                    month=0,
                    created_by=1,
                )

            db.rollback()

    def test_month_thirteen_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_utility_bill(
                    db=db,
                    bill_type=UtilityBillType.INTERNET,
                    amount=Decimal("500.00"),
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

                create_utility_bill(
                    db=db,
                    bill_type=UtilityBillType.INTERNET,
                    amount=Decimal("-100.00"),
                    year=year,
                    month=month,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # INVALID BILL TYPE
    # ---------------------------------------------------------

    def test_invalid_bill_type_is_rejected(self):
        with Session(engine) as db:

            year, month = self.current_period()

            with self.assertRaises(ValueError):

                create_utility_bill(
                    db=db,
                    bill_type="GAS",
                    amount=Decimal("100.00"),
                    year=year,
                    month=month,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_bill_can_be_rolled_back(self):
        with Session(engine) as db:

            year, month = self.current_period()

            bill = create_utility_bill(
                db=db,
                bill_type=UtilityBillType.WATER,
                amount=Decimal("300.00"),
                year=year,
                month=month,
                created_by=1,
            )

            db.flush()

            bill_id = bill.id

            db.rollback()

            saved_bill = db.scalar(
                select(UtilityBill).where(
                    UtilityBill.id == bill_id
                )
            )

            self.assertIsNone(
                saved_bill
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )