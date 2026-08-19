import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.profit import Profit

from app.services.profit import create_profit


class ProfitTests(unittest.TestCase):

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_create_profit_successfully(self):
        with Session(engine) as db:

            profit = create_profit(
                db=db,
                name="Vehicle Sale",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                profit.id
            )

            self.assertEqual(
                profit.name,
                "Vehicle Sale",
            )

            self.assertEqual(
                profit.amount,
                Decimal("5000.00"),
            )

            self.assertEqual(
                profit.created_by,
                1,
            )

            self.assertIsNotNone(
                profit.created_at
            )

            self.assertIsNotNone(
                profit.updated_at
            )

            db.rollback()

    # ---------------------------------------------------------
    # NAME
    # ---------------------------------------------------------

    def test_name_is_trimmed(self):
        with Session(engine) as db:

            profit = create_profit(
                db=db,
                name="  Vehicle Sale  ",
                amount=5000,
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                profit.name,
                "Vehicle Sale",
            )

            db.rollback()

    def test_empty_name_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "name is required",
            ):

                create_profit(
                    db=db,
                    name="",
                    amount=5000,
                    created_by=1,
                )

            db.rollback()

    def test_whitespace_name_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "name is required",
            ):

                create_profit(
                    db=db,
                    name="   ",
                    amount=5000,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # AMOUNT
    # ---------------------------------------------------------

    def test_zero_amount_is_allowed(self):
        with Session(engine) as db:

            profit = create_profit(
                db=db,
                name="Zero Profit",
                amount=0,
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                profit.amount,
                Decimal("0"),
            )

            db.rollback()

    def test_negative_amount_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "amount cannot be negative",
            ):

                create_profit(
                    db=db,
                    name="Invalid Profit",
                    amount=-100,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # DUPLICATES ARE ALLOWED
    # ---------------------------------------------------------

    def test_duplicate_profits_are_allowed(self):
        with Session(engine) as db:

            profit_1 = create_profit(
                db=db,
                name="Vehicle Sale",
                amount=5000,
                created_by=1,
            )

            profit_2 = create_profit(
                db=db,
                name="Vehicle Sale",
                amount=5000,
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                profit_1.id
            )

            self.assertIsNotNone(
                profit_2.id
            )

            self.assertNotEqual(
                profit_1.id,
                profit_2.id,
            )

            db.rollback()

    # ---------------------------------------------------------
    # MULTIPLE PROFITS
    # ---------------------------------------------------------

    def test_multiple_profits_can_be_created(self):
        with Session(engine) as db:

            profit_1 = create_profit(
                db=db,
                name="Vehicle Sale",
                amount=5000,
                created_by=1,
            )

            profit_2 = create_profit(
                db=db,
                name="Insurance Commission",
                amount=1000,
                created_by=1,
            )

            profit_3 = create_profit(
                db=db,
                name="Parts Sale",
                amount=750,
                created_by=1,
            )

            db.flush()

            ids = {
                profit_1.id,
                profit_2.id,
                profit_3.id,
            }

            self.assertEqual(
                len(ids),
                3,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_profit_is_saved_after_commit(self):
        with Session(engine) as db:

            profit = create_profit(
                db=db,
                name="Vehicle Sale",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            db.flush()

            profit_id = profit.id

            db.commit()

            saved_profit = db.scalar(
                select(Profit).where(
                    Profit.id == profit_id
                )
            )

            self.assertIsNotNone(
                saved_profit
            )

            self.assertEqual(
                saved_profit.name,
                "Vehicle Sale",
            )

            self.assertEqual(
                saved_profit.amount,
                Decimal("5000.00"),
            )

            # Clean up committed test data.
            db.delete(saved_profit)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_profit_can_be_rolled_back(self):
        with Session(engine) as db:

            profit = create_profit(
                db=db,
                name="Rollback Profit",
                amount=500,
                created_by=1,
            )

            db.flush()

            profit_id = profit.id

            db.rollback()

            saved_profit = db.scalar(
                select(Profit).where(
                    Profit.id == profit_id
                )
            )

            self.assertIsNone(
                saved_profit
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )