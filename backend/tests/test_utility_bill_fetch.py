import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.utility_bill import (
    UtilityBill,
    UtilityBillType,
)

from app.services.utility_bill_fetch import (
    get_utility_bills,
)


class UtilityBillFetchTests(unittest.TestCase):

    def create_test_bill(
        self,
        db,
        bill_type,
        amount="100.00",
        year=2026,
        month=8,
    ):
        bill = UtilityBill(
            bill_type=bill_type,
            amount=Decimal(amount),
            year=year,
            month=month,
            created_by=1,
        )

        db.add(bill)
        db.flush()

        return bill

    def cleanup_bills(self, db):
        bills = db.scalars(
            select(UtilityBill)
        ).all()

        for bill in bills:
            db.delete(bill)

        db.commit()

    # ---------------------------------------------------------
    # ALL THREE BILL TYPES
    # ---------------------------------------------------------

    def test_all_utility_bills_are_returned_for_month(self):

        with Session(engine) as db:

            electricity = self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.ELECTRICITY,
                amount="500.00",
            )

            water = self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.WATER,
                amount="200.00",
            )

            internet = self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.INTERNET,
                amount="300.00",
            )

            db.commit()

            result = get_utility_bills(
                db=db,
                year=2026,
                month=8,
            )

            self.assertEqual(
                len(result),
                3,
            )

            returned_types = {
                bill.bill_type
                for bill in result
            }

            self.assertEqual(
                returned_types,
                {
                    UtilityBillType.ELECTRICITY,
                    UtilityBillType.WATER,
                    UtilityBillType.INTERNET,
                },
            )

            self.cleanup_bills(db)

    # ---------------------------------------------------------
    # AMOUNTS ARE CORRECT
    # ---------------------------------------------------------

    def test_bill_amounts_are_returned_correctly(self):

        with Session(engine) as db:

            electricity = self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.ELECTRICITY,
                amount="500.00",
            )

            water = self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.WATER,
                amount="200.00",
            )

            internet = self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.INTERNET,
                amount="300.00",
            )

            db.commit()

            result = get_utility_bills(
                db=db,
                year=2026,
                month=8,
            )

            amounts = {
                bill.bill_type: bill.amount
                for bill in result
            }

            self.assertEqual(
                amounts[
                    UtilityBillType.ELECTRICITY
                ],
                Decimal("500.00"),
            )

            self.assertEqual(
                amounts[
                    UtilityBillType.WATER
                ],
                Decimal("200.00"),
            )

            self.assertEqual(
                amounts[
                    UtilityBillType.INTERNET
                ],
                Decimal("300.00"),
            )

            self.cleanup_bills(db)

    # ---------------------------------------------------------
    # DIFFERENT MONTH IS NOT RETURNED
    # ---------------------------------------------------------

    def test_different_month_is_not_returned(self):

        with Session(engine) as db:

            self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.ELECTRICITY,
                year=2026,
                month=8,
            )

            db.commit()

            result = get_utility_bills(
                db=db,
                year=2026,
                month=7,
            )

            self.assertEqual(
                len(result),
                0,
            )

            self.cleanup_bills(db)

    # ---------------------------------------------------------
    # DIFFERENT YEAR IS NOT RETURNED
    # ---------------------------------------------------------

    def test_different_year_is_not_returned(self):

        with Session(engine) as db:

            self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.ELECTRICITY,
                year=2026,
                month=8,
            )

            db.commit()

            result = get_utility_bills(
                db=db,
                year=2025,
                month=8,
            )

            self.assertEqual(
                len(result),
                0,
            )

            self.cleanup_bills(db)

    # ---------------------------------------------------------
    # PARTIAL BILLS ARE ALLOWED
    # ---------------------------------------------------------

    def test_missing_bill_type_does_not_fail(self):

        with Session(engine) as db:

            self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.ELECTRICITY,
                amount="500.00",
            )

            self.create_test_bill(
                db=db,
                bill_type=UtilityBillType.WATER,
                amount="200.00",
            )

            db.commit()

            result = get_utility_bills(
                db=db,
                year=2026,
                month=8,
            )

            self.assertEqual(
                len(result),
                2,
            )

            returned_types = {
                bill.bill_type
                for bill in result
            }

            self.assertNotIn(
                UtilityBillType.INTERNET,
                returned_types,
            )

            self.cleanup_bills(db)

    # ---------------------------------------------------------
    # INVALID MONTH - ZERO
    # ---------------------------------------------------------

    def test_zero_month_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Month must be between 1 and 12",
            ):
                get_utility_bills(
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
                get_utility_bills(
                    db=db,
                    year=2026,
                    month=13,
                )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )