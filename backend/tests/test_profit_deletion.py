import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.profit import Profit

from app.services.profit import create_profit
from app.services.profit_deletion import deactivate_profit


class ProfitDeleteTests(unittest.TestCase):

    def create_test_profit(
        self,
        db,
        name="Original Profit",
        amount=Decimal("500.00"),
    ):
        profit = create_profit(
            db=db,
            name=name,
            amount=amount,
            created_by=1,
        )

        db.flush()

        return profit

    # ---------------------------------------------------------
    # PROFIT IS DEACTIVATED
    # ---------------------------------------------------------

    def test_profit_is_deactivated(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            profit_id = profit.id

            self.assertTrue(
                profit.is_active
            )

            deactivate_profit(
                db=db,
                profit_id=profit_id,
            )

            self.assertFalse(
                profit.is_active
            )

            db.rollback()

    # ---------------------------------------------------------
    # DEACTIVATION IS PERSISTED
    # ---------------------------------------------------------

    def test_deactivation_is_persisted_after_commit(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            profit_id = profit.id

            deactivate_profit(
                db=db,
                profit_id=profit_id,
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

            self.assertFalse(
                saved_profit.is_active
            )

            # Clean up.
            db.delete(saved_profit)
            db.commit()

    # ---------------------------------------------------------
    # NONEXISTENT PROFIT
    # ---------------------------------------------------------

    def test_nonexistent_profit_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Profit not found",
            ):
                deactivate_profit(
                    db=db,
                    profit_id=999999,
                )

            db.rollback()

    # ---------------------------------------------------------
    # OTHER PROFIT REMAINS ACTIVE
    # ---------------------------------------------------------

    def test_other_profit_remains_active(self):
        with Session(engine) as db:

            profit1 = self.create_test_profit(
                db=db,
                name="Profit One",
                amount=Decimal("500.00"),
            )

            db.commit()

            profit2 = self.create_test_profit(
                db=db,
                name="Profit Two",
                amount=Decimal("700.00"),
            )

            db.flush()

            profit1_id = profit1.id
            profit2_id = profit2.id

            deactivate_profit(
                db=db,
                profit_id=profit1_id,
            )

            db.commit()

            deactivated_profit = db.scalar(
                select(Profit).where(
                    Profit.id == profit1_id
                )
            )

            remaining_profit = db.scalar(
                select(Profit).where(
                    Profit.id == profit2_id
                )
            )

            self.assertIsNotNone(
                deactivated_profit
            )

            self.assertFalse(
                deactivated_profit.is_active
            )

            self.assertIsNotNone(
                remaining_profit
            )

            self.assertTrue(
                remaining_profit.is_active
            )

            # Clean up.
            db.delete(deactivated_profit)
            db.delete(remaining_profit)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_deactivation_can_be_rolled_back(self):
        with Session(engine) as db:

            profit = self.create_test_profit(db)

            profit_id = profit.id

            # Commit original active profit.
            db.commit()

            deactivate_profit(
                db=db,
                profit_id=profit_id,
            )

            self.assertFalse(
                profit.is_active
            )

            # Undo deactivation.
            db.rollback()

            restored_profit = db.scalar(
                select(Profit).where(
                    Profit.id == profit_id
                )
            )

            self.assertIsNotNone(
                restored_profit
            )

            self.assertTrue(
                restored_profit.is_active
            )

            # Clean up.
            db.delete(restored_profit)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )