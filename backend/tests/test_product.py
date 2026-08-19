import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.product import Product

from app.services.product import create_product


class ProductTests(unittest.TestCase):

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_create_product_successfully(self):
        with Session(engine) as db:

            product = create_product(
                db=db,
                description="Brake Pad",
                quantity=20,
                unit_price=150,
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                product.id
            )

            self.assertEqual(
                product.description,
                "Brake Pad",
            )

            self.assertEqual(
                product.quantity,
                Decimal("20"),
            )

            self.assertEqual(
                product.unit_price,
                Decimal("150"),
            )

            self.assertEqual(
                product.created_by,
                1,
            )

            self.assertIsNotNone(
                product.created_at
            )

            self.assertIsNotNone(
                product.updated_at
            )

            db.rollback()

    # ---------------------------------------------------------
    # DESCRIPTION
    # ---------------------------------------------------------

    def test_description_is_trimmed(self):
        with Session(engine) as db:

            product = create_product(
                db=db,
                description="  Brake Pad  ",
                quantity=20,
                unit_price=150,
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                product.description,
                "Brake Pad",
            )

            db.rollback()

    def test_empty_description_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "description is required",
            ):

                create_product(
                    db=db,
                    description="",
                    quantity=20,
                    unit_price=150,
                    created_by=1,
                )

            db.rollback()

    def test_whitespace_description_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "description is required",
            ):

                create_product(
                    db=db,
                    description="   ",
                    quantity=20,
                    unit_price=150,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # QUANTITY
    # ---------------------------------------------------------

    def test_zero_quantity_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "quantity must be greater than zero",
            ):

                create_product(
                    db=db,
                    description="Brake Pad",
                    quantity=0,
                    unit_price=150,
                    created_by=1,
                )

            db.rollback()

    def test_negative_quantity_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "quantity must be greater than zero",
            ):

                create_product(
                    db=db,
                    description="Brake Pad",
                    quantity=-5,
                    unit_price=150,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # UNIT PRICE
    # ---------------------------------------------------------

    def test_zero_unit_price_is_allowed(self):
        with Session(engine) as db:

            product = create_product(
                db=db,
                description="Free Item",
                quantity=10,
                unit_price=0,
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                product.unit_price,
                Decimal("0"),
            )

            db.rollback()

    def test_negative_unit_price_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "unit price cannot be negative",
            ):

                create_product(
                    db=db,
                    description="Brake Pad",
                    quantity=20,
                    unit_price=-150,
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # DUPLICATES ARE ALLOWED
    # ---------------------------------------------------------

    def test_duplicate_products_are_allowed(self):
        with Session(engine) as db:

            product_1 = create_product(
                db=db,
                description="Brake Pad",
                quantity=20,
                unit_price=150,
                created_by=1,
            )

            product_2 = create_product(
                db=db,
                description="Brake Pad",
                quantity=20,
                unit_price=150,
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                product_1.id
            )

            self.assertIsNotNone(
                product_2.id
            )

            self.assertNotEqual(
                product_1.id,
                product_2.id,
            )

            db.rollback()

    # ---------------------------------------------------------
    # MULTIPLE PRODUCTS
    # ---------------------------------------------------------

    def test_multiple_products_can_be_created(self):
        with Session(engine) as db:

            product_1 = create_product(
                db=db,
                description="Brake Pad",
                quantity=20,
                unit_price=150,
                created_by=1,
            )

            product_2 = create_product(
                db=db,
                description="Oil Filter",
                quantity=10,
                unit_price=75,
                created_by=1,
            )

            product_3 = create_product(
                db=db,
                description="Air Filter",
                quantity=15,
                unit_price=100,
                created_by=1,
            )

            db.flush()

            ids = {
                product_1.id,
                product_2.id,
                product_3.id,
            }

            self.assertEqual(
                len(ids),
                3,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_product_is_saved_after_commit(self):
        with Session(engine) as db:

            product = create_product(
                db=db,
                description="Brake Pad",
                quantity=20,
                unit_price=150,
                created_by=1,
            )

            db.flush()

            product_id = product.id

            db.commit()

            saved_product = db.scalar(
                select(Product).where(
                    Product.id == product_id
                )
            )

            self.assertIsNotNone(
                saved_product
            )

            self.assertEqual(
                saved_product.description,
                "Brake Pad",
            )

            self.assertEqual(
                saved_product.quantity,
                Decimal("20"),
            )

            self.assertEqual(
                saved_product.unit_price,
                Decimal("150"),
            )

            # Clean up committed test data.
            db.delete(saved_product)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_product_can_be_rolled_back(self):
        with Session(engine) as db:

            product = create_product(
                db=db,
                description="Rollback Product",
                quantity=10,
                unit_price=100,
                created_by=1,
            )

            db.flush()

            product_id = product.id

            db.rollback()

            saved_product = db.scalar(
                select(Product).where(
                    Product.id == product_id
                )
            )

            self.assertIsNone(
                saved_product
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )