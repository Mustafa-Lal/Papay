import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.product import Product

from app.services.product import create_product
from app.services.product_update import update_product


class ProductUpdateTests(unittest.TestCase):

    def create_test_product(self, db):
        product = create_product(
            db=db,
            description="Original Product",
            quantity=Decimal("10.00"),
            unit_price=Decimal("50.00"),
            created_by=1,
        )

        db.flush()

        return product

    # ---------------------------------------------------------
    # DESCRIPTION
    # ---------------------------------------------------------

    def test_update_description(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            update_product(
                db=db,
                product_id=product.id,
                description="Updated Product",
            )

            self.assertEqual(
                product.description,
                "Updated Product",
            )

            self.assertEqual(
                product.quantity,
                Decimal("10.00"),
            )

            self.assertEqual(
                product.unit_price,
                Decimal("50.00"),
            )

            db.rollback()

    def test_updated_description_is_trimmed(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            update_product(
                db=db,
                product_id=product.id,
                description="  Updated Product  ",
            )

            self.assertEqual(
                product.description,
                "Updated Product",
            )

            db.rollback()

    def test_empty_description_is_rejected(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            with self.assertRaisesRegex(
                ValueError,
                "Product description cannot be empty",
            ):
                update_product(
                    db=db,
                    product_id=product.id,
                    description="",
                )

            self.assertEqual(
                product.description,
                "Original Product",
            )

            db.rollback()

    def test_whitespace_description_is_rejected(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            with self.assertRaisesRegex(
                ValueError,
                "Product description cannot be empty",
            ):
                update_product(
                    db=db,
                    product_id=product.id,
                    description="   ",
                )

            self.assertEqual(
                product.description,
                "Original Product",
            )

            db.rollback()

    # ---------------------------------------------------------
    # QUANTITY
    # ---------------------------------------------------------

    def test_update_quantity(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            update_product(
                db=db,
                product_id=product.id,
                quantity=Decimal("25.00"),
            )

            self.assertEqual(
                product.quantity,
                Decimal("25.00"),
            )

            self.assertEqual(
                product.unit_price,
                Decimal("50.00"),
            )

            db.rollback()

    def test_zero_quantity_is_rejected(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            with self.assertRaisesRegex(
                ValueError,
                "quantity must be greater than zero",
            ):
                update_product(
                    db=db,
                    product_id=product.id,
                    quantity=Decimal("0.00"),
                )

            self.assertEqual(
                product.quantity,
                Decimal("10.00"),
            )

            db.rollback()

    def test_negative_quantity_is_rejected(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            with self.assertRaisesRegex(
                ValueError,
                "quantity must be greater than zero",
            ):
                update_product(
                    db=db,
                    product_id=product.id,
                    quantity=Decimal("-5.00"),
                )

            self.assertEqual(
                product.quantity,
                Decimal("10.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # UNIT PRICE
    # ---------------------------------------------------------

    def test_update_unit_price(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            update_product(
                db=db,
                product_id=product.id,
                unit_price=Decimal("75.00"),
            )

            self.assertEqual(
                product.unit_price,
                Decimal("75.00"),
            )

            self.assertEqual(
                product.quantity,
                Decimal("10.00"),
            )

            db.rollback()

    def test_zero_unit_price_is_allowed(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            update_product(
                db=db,
                product_id=product.id,
                unit_price=Decimal("0.00"),
            )

            self.assertEqual(
                product.unit_price,
                Decimal("0.00"),
            )

            db.rollback()

    def test_negative_unit_price_is_rejected(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            with self.assertRaisesRegex(
                ValueError,
                "unit price cannot be negative",
            ):
                update_product(
                    db=db,
                    product_id=product.id,
                    unit_price=Decimal("-10.00"),
                )

            self.assertEqual(
                product.unit_price,
                Decimal("50.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # ALL FIELDS
    # ---------------------------------------------------------

    def test_update_all_product_fields(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            update_product(
                db=db,
                product_id=product.id,
                description="New Product",
                quantity=Decimal("20.00"),
                unit_price=Decimal("80.00"),
            )

            self.assertEqual(
                product.description,
                "New Product",
            )

            self.assertEqual(
                product.quantity,
                Decimal("20.00"),
            )

            self.assertEqual(
                product.unit_price,
                Decimal("80.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # PARTIAL UPDATE
    # ---------------------------------------------------------

    def test_partial_update_does_not_change_other_fields(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            update_product(
                db=db,
                product_id=product.id,
                quantity=Decimal("30.00"),
            )

            self.assertEqual(
                product.description,
                "Original Product",
            )

            self.assertEqual(
                product.quantity,
                Decimal("30.00"),
            )

            self.assertEqual(
                product.unit_price,
                Decimal("50.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_product_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Product not found",
            ):
                update_product(
                    db=db,
                    product_id=999999,
                    description="New Product",
                )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            product_id = product.id

            update_product(
                db=db,
                product_id=product_id,
                description="Persisted Product",
                quantity=Decimal("40.00"),
                unit_price=Decimal("90.00"),
            )

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
                "Persisted Product",
            )

            self.assertEqual(
                saved_product.quantity,
                Decimal("40.00"),
            )

            self.assertEqual(
                saved_product.unit_price,
                Decimal("90.00"),
            )

            # Clean up committed test data.
            db.delete(saved_product)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            # Commit the original product first.
            # Rollback must only undo the update.
            db.commit()

            product_id = product.id

            update_product(
                db=db,
                product_id=product_id,
                description="Temporary Product",
                quantity=Decimal("99.00"),
                unit_price=Decimal("999.00"),
            )

            db.rollback()

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
                "Original Product",
            )

            self.assertEqual(
                saved_product.quantity,
                Decimal("10.00"),
            )

            self.assertEqual(
                saved_product.unit_price,
                Decimal("50.00"),
            )

            # Clean up.
            db.delete(saved_product)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )