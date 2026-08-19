import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.profit import Profit

from app.services.profit import create_profit
from app.services.profit_update import update_profit


class ProfitUpdateTests(unittest.TestCase):

    def create_test_profit(self, db):
        profit = create_profit(
            db=db,
            name="Original Profit",
            amount=Decimal("500.00"),
            created_by=1,
        )

        db.flush()

        return profit

    # ---------------------------------------------------------
    # UPDATE NAME
    # ---------------------------------------------------------

    def test_update_name(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            update_profit(
                db=db,
                profit_id=profit.id,
                name="Updated Profit",
            )

            self.assertEqual(
                profit.name,
                "Updated Profit",
            )

            self.assertEqual(
                profit.amount,
                Decimal("500.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE AMOUNT
    # ---------------------------------------------------------

    def test_update_amount(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            update_profit(
                db=db,
                profit_id=profit.id,
                amount=Decimal("750.00"),
            )

            self.assertEqual(
                profit.amount,
                Decimal("750.00"),
            )

            self.assertEqual(
                profit.name,
                "Original Profit",
            )

            db.rollback()

    # ---------------------------------------------------------
    # ZERO AMOUNT
    # ---------------------------------------------------------

    def test_zero_amount_is_allowed(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            update_profit(
                db=db,
                profit_id=profit.id,
                amount=Decimal("0.00"),
            )

            self.assertEqual(
                profit.amount,
                Decimal("0.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NEGATIVE AMOUNT
    # ---------------------------------------------------------

    def test_negative_amount_is_rejected(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            with self.assertRaisesRegex(
                ValueError,
                "Profit amount cannot be negative",
            ):
                update_profit(
                    db=db,
                    profit_id=profit.id,
                    amount=Decimal("-100.00"),
                )

            self.assertEqual(
                profit.amount,
                Decimal("500.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # EMPTY NAME
    # ---------------------------------------------------------

    def test_empty_name_is_rejected(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            with self.assertRaisesRegex(
                ValueError,
                "Profit name cannot be empty",
            ):
                update_profit(
                    db=db,
                    profit_id=profit.id,
                    name="",
                )

            self.assertEqual(
                profit.name,
                "Original Profit",
            )

            db.rollback()

    # ---------------------------------------------------------
    # WHITESPACE NAME
    # ---------------------------------------------------------

    def test_whitespace_name_is_rejected(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            with self.assertRaisesRegex(
                ValueError,
                "Profit name cannot be empty",
            ):
                update_profit(
                    db=db,
                    profit_id=profit.id,
                    name="   ",
                )

            self.assertEqual(
                profit.name,
                "Original Profit",
            )

            db.rollback()

    # ---------------------------------------------------------
    # NAME TRIMMING
    # ---------------------------------------------------------

    def test_updated_name_is_trimmed(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            update_profit(
                db=db,
                profit_id=profit.id,
                name="  Updated Profit  ",
            )

            self.assertEqual(
                profit.name,
                "Updated Profit",
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE ALL FIELDS
    # ---------------------------------------------------------

    def test_update_all_profit_fields(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            update_profit(
                db=db,
                profit_id=profit.id,
                name="New Profit",
                amount=Decimal("900.00"),
            )

            self.assertEqual(
                profit.name,
                "New Profit",
            )

            self.assertEqual(
                profit.amount,
                Decimal("900.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # PARTIAL UPDATE
    # ---------------------------------------------------------

    def test_partial_update_does_not_change_other_fields(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            update_profit(
                db=db,
                profit_id=profit.id,
                name="Only Name Changed",
            )

            self.assertEqual(
                profit.name,
                "Only Name Changed",
            )

            self.assertEqual(
                profit.amount,
                Decimal("500.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_profit_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Profit not found",
            ):
                update_profit(
                    db=db,
                    profit_id=999999,
                    name="New Profit",
                )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            profit_id = profit.id

            update_profit(
                db=db,
                profit_id=profit_id,
                name="Persisted Profit",
                amount=Decimal("1000.00"),
            )

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
                "Persisted Profit",
            )

            self.assertEqual(
                saved_profit.amount,
                Decimal("1000.00"),
            )

            # Clean up.
            db.delete(saved_profit)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            # Commit the original profit first.
            # Rollback must only undo the update.
            db.commit()

            profit_id = profit.id

            update_profit(
                db=db,
                profit_id=profit_id,
                name="Temporary Profit",
                amount=Decimal("9999.00"),
            )

            db.rollback()

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
                "Original Profit",
            )

            self.assertEqual(
                saved_profit.amount,
                Decimal("500.00"),
            )

            # Clean up.
            db.delete(saved_profit)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )