import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.profit import Profit

from app.services.profit_fetch import (
    get_profits,
    get_profits_this_month,
)


class ProfitFetchTests(unittest.TestCase):

    def create_test_profit(
        self,
        db,
        name="Insurance Commission",
        amount="100.00",
    ):
        profit = Profit(
            name=name,
            amount=Decimal(amount),
            created_by=1,
        )

        db.add(profit)
        db.flush()

        return profit

    def cleanup_profits(self, db):
        profits = db.scalars(
            select(Profit)
        ).all()

        for profit in profits:
            db.delete(profit)

        db.commit()

    # ---------------------------------------------------------
    # ALL TIME
    # ---------------------------------------------------------

    def test_get_all_active_profits(self):

        with Session(engine) as db:

            profit1 = self.create_test_profit(
                db,
                name="Insurance Commission",
                amount="100.00",
            )

            profit2 = self.create_test_profit(
                db,
                name="Service Commission",
                amount="200.00",
            )

            db.commit()

            result = get_profits(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                2,
            )

            self.assertEqual(
                len(result["profits"]),
                2,
            )

            names = {
                profit["name"]
                for profit in result["profits"]
            }

            self.assertIn(
                "Insurance Commission",
                names,
            )

            self.assertIn(
                "Service Commission",
                names,
            )

            self.cleanup_profits(db)

    # ---------------------------------------------------------
    # INACTIVE PROFITS ARE EXCLUDED
    # ---------------------------------------------------------

    def test_inactive_profits_are_excluded(self):

        with Session(engine) as db:

            active_profit = self.create_test_profit(
                db,
                name="Active Profit",
            )

            inactive_profit = self.create_test_profit(
                db,
                name="Deleted Profit",
            )

            inactive_profit.is_active = False

            db.commit()

            result = get_profits(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                len(result["profits"]),
                1,
            )

            self.assertEqual(
                result["profits"][0]["id"],
                active_profit.id,
            )

            self.cleanup_profits(db)

    # ---------------------------------------------------------
    # THIS MONTH
    # ---------------------------------------------------------

    def test_get_profits_this_month(self):

        with Session(engine) as db:

            profit = self.create_test_profit(
                db,
                name="This Month Profit",
            )

            db.commit()

            result = get_profits_this_month(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["profits"][0]["id"],
                profit.id,
            )

            self.cleanup_profits(db)

    # ---------------------------------------------------------
    # DATE RANGE
    # ---------------------------------------------------------

    def test_date_range_returns_matching_profits(self):

        with Session(engine) as db:

            profit1 = self.create_test_profit(
                db,
                name="July Profit",
            )

            profit2 = self.create_test_profit(
                db,
                name="August Profit",
            )

            profit1.created_at = datetime(
                2026,
                7,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            )

            profit2.created_at = datetime(
                2026,
                8,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            )

            db.commit()

            result = get_profits(
                db=db,
                start_date=date(2026, 7, 1),
                end_date=date(2026, 7, 31),
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["profits"][0]["id"],
                profit1.id,
            )

            self.cleanup_profits(db)

    # ---------------------------------------------------------
    # END DATE IS INCLUSIVE
    # ---------------------------------------------------------

    def test_end_date_includes_entire_day(self):

        with Session(engine) as db:

            profit = self.create_test_profit(
                db,
                name="End Day Profit",
            )

            profit.created_at = datetime(
                2026,
                8,
                19,
                23,
                59,
                59,
                tzinfo=timezone.utc,
            )

            db.commit()

            result = get_profits(
                db=db,
                start_date=date(2026, 8, 19),
                end_date=date(2026, 8, 19),
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["profits"][0]["id"],
                profit.id,
            )

            self.cleanup_profits(db)

    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    def test_pagination_works(self):

        with Session(engine) as db:

            for index in range(15):

                self.create_test_profit(
                    db,
                    name=f"Profit {index}",
                )

            db.commit()

            result = get_profits(
                db=db,
                limit=10,
                offset=5,
            )

            self.assertEqual(
                len(result["profits"]),
                10,
            )

            self.assertEqual(
                result["pagination"]["limit"],
                10,
            )

            self.assertEqual(
                result["pagination"]["offset"],
                5,
            )

            self.assertEqual(
                result["pagination"]["total"],
                15,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup_profits(db)

    # ---------------------------------------------------------
    # FEWER RECORDS THAN LIMIT
    # ---------------------------------------------------------

    def test_remaining_records_are_returned(self):

        with Session(engine) as db:

            for index in range(16):

                self.create_test_profit(
                    db,
                    name=f"Profit {index}",
                )

            db.commit()

            result = get_profits(
                db=db,
                limit=10,
                offset=10,
            )

            self.assertEqual(
                len(result["profits"]),
                6,
            )

            self.assertEqual(
                result["pagination"]["total"],
                16,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup_profits(db)

    # ---------------------------------------------------------
    # OFFSET BEYOND RECORDS
    # ---------------------------------------------------------

    def test_offset_beyond_records_returns_empty_list(self):

        with Session(engine) as db:

            for index in range(5):

                self.create_test_profit(
                    db,
                    name=f"Profit {index}",
                )

            db.commit()

            result = get_profits(
                db=db,
                limit=10,
                offset=10,
            )

            self.assertEqual(
                len(result["profits"]),
                0,
            )

            self.assertEqual(
                result["pagination"]["total"],
                5,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup_profits(db)

    # ---------------------------------------------------------
    # ZERO LIMIT
    # ---------------------------------------------------------

    def test_zero_limit_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Limit must be greater than zero",
            ):
                get_profits(
                    db=db,
                    limit=0,
                )

    # ---------------------------------------------------------
    # NEGATIVE OFFSET
    # ---------------------------------------------------------

    def test_negative_offset_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Offset cannot be negative",
            ):
                get_profits(
                    db=db,
                    offset=-1,
                )

    # ---------------------------------------------------------
    # INVALID DATE RANGE
    # ---------------------------------------------------------

    def test_invalid_date_range_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Start date cannot be after end date",
            ):
                get_profits(
                    db=db,
                    start_date=date(2026, 8, 20),
                    end_date=date(2026, 8, 1),
                )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )