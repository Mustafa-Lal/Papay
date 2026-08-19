import unittest
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.product import Product

from app.services.product import create_product
from app.services.product_fetch import (
    get_products,
    get_products_this_month,
)


class ProductFetchTests(unittest.TestCase):

    def create_test_product(
        self,
        db,
        description="Engine Oil",
        quantity="5.00",
        unit_price="50.00",
    ):
        product = create_product(
            db=db,
            description=description,
            quantity=Decimal(quantity),
            unit_price=Decimal(unit_price),
            created_by=1,
        )

        db.flush()

        return product

    def cleanup_customer_products(self, db):
        products = db.scalars(
            select(Product)
        ).all()

        for product in products:
            db.delete(product)

        db.commit()

    # ---------------------------------------------------------
    # ALL TIME
    # ---------------------------------------------------------

    def test_get_all_active_products(self):

        with Session(engine) as db:

            product1 = self.create_test_product(
                db,
                description="Engine Oil",
            )

            product2 = self.create_test_product(
                db,
                description="Brake Pad",
            )

            db.commit()

            result = get_products(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                2,
            )

            self.assertEqual(
                len(result["products"]),
                2,
            )

            descriptions = {
                product["description"]
                for product in result["products"]
            }

            self.assertIn(
                "Engine Oil",
                descriptions,
            )

            self.assertIn(
                "Brake Pad",
                descriptions,
            )

            self.cleanup_customer_products(db)

    # ---------------------------------------------------------
    # INACTIVE PRODUCTS ARE NOT RETURNED
    # ---------------------------------------------------------

    def test_inactive_products_are_excluded(self):

        with Session(engine) as db:

            active_product = self.create_test_product(
                db,
                description="Active Product",
            )

            inactive_product = self.create_test_product(
                db,
                description="Deleted Product",
            )

            inactive_product.is_active = False

            db.commit()

            result = get_products(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                len(result["products"]),
                1,
            )

            self.assertEqual(
                result["products"][0]["id"],
                active_product.id,
            )

            self.cleanup_customer_products(db)

    # ---------------------------------------------------------
    # THIS MONTH
    # ---------------------------------------------------------

    def test_get_products_this_month(self):

        with Session(engine) as db:

            product = self.create_test_product(
                db,
                description="This Month Product",
            )

            db.commit()

            result = get_products_this_month(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["products"][0]["id"],
                product.id,
            )

            self.cleanup_customer_products(db)

    # ---------------------------------------------------------
    # DATE RANGE
    # ---------------------------------------------------------

    def test_date_range_returns_matching_products(self):

        with Session(engine) as db:

            product1 = self.create_test_product(
                db,
                description="July Product",
            )

            product2 = self.create_test_product(
                db,
                description="August Product",
            )

            product1.created_at = datetime(
                2026,
                7,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            )

            product2.created_at = datetime(
                2026,
                8,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            )

            db.commit()

            result = get_products(
                db=db,
                start_date=datetime(
                    2026,
                    7,
                    1,
                ).date(),
                end_date=datetime(
                    2026,
                    7,
                    31,
                ).date(),
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["products"][0]["id"],
                product1.id,
            )

            self.cleanup_customer_products(db)

    # ---------------------------------------------------------
    # END DATE IS INCLUSIVE
    # ---------------------------------------------------------

    def test_end_date_includes_entire_day(self):

        with Session(engine) as db:

            product = self.create_test_product(
                db,
                description="End Day Product",
            )

            product.created_at = datetime(
                2026,
                8,
                19,
                23,
                59,
                59,
                tzinfo=timezone.utc,
            )

            db.commit()

            result = get_products(
                db=db,
                start_date=datetime(
                    2026,
                    8,
                    19,
                ).date(),
                end_date=datetime(
                    2026,
                    8,
                    19,
                ).date(),
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["products"][0]["id"],
                product.id,
            )

            self.cleanup_customer_products(db)

    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    def test_pagination_works(self):

        with Session(engine) as db:

            for index in range(15):

                self.create_test_product(
                    db,
                    description=f"Product {index}",
                )

            db.commit()

            result = get_products(
                db=db,
                limit=10,
                offset=5,
            )

            self.assertEqual(
                len(result["products"]),
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

            self.cleanup_customer_products(db)

    # ---------------------------------------------------------
    # FEWER RECORDS THAN LIMIT
    # ---------------------------------------------------------

    def test_remaining_records_are_returned(self):

        with Session(engine) as db:

            for index in range(16):

                self.create_test_product(
                    db,
                    description=f"Product {index}",
                )

            db.commit()

            result = get_products(
                db=db,
                limit=10,
                offset=10,
            )

            # Only 6 records remain.
            self.assertEqual(
                len(result["products"]),
                6,
            )

            self.assertEqual(
                result["pagination"]["total"],
                16,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup_customer_products(db)

    # ---------------------------------------------------------
    # OFFSET BEYOND RECORDS
    # ---------------------------------------------------------

    def test_offset_beyond_records_returns_empty_list(self):

        with Session(engine) as db:

            for index in range(5):

                self.create_test_product(
                    db,
                    description=f"Product {index}",
                )

            db.commit()

            result = get_products(
                db=db,
                limit=10,
                offset=10,
            )

            self.assertEqual(
                len(result["products"]),
                0,
            )

            self.assertEqual(
                result["pagination"]["total"],
                5,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup_customer_products(db)

    # ---------------------------------------------------------
    # INVALID LIMIT
    # ---------------------------------------------------------

    def test_zero_limit_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Limit must be greater than zero",
            ):
                get_products(
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
                get_products(
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
                get_products(
                    db=db,
                    start_date=datetime(
                        2026,
                        8,
                        20,
                    ).date(),
                    end_date=datetime(
                        2026,
                        8,
                        1,
                    ).date(),
                )




from datetime import date


def get_products_this_month(
    db: Session,
    limit: int = 10,
    offset: int = 0,
) -> dict:

    today = date.today()

    start_date = today.replace(
        day=1
    )

    return get_products(
        db=db,
        start_date=start_date,
        end_date=today,
        limit=limit,
        offset=offset,
    )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )