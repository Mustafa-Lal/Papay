import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.product import Product

from app.services.product import create_product
from app.services.product_deletion import deactivate_product


class ProductDeleteTests(unittest.TestCase):

    def create_test_product(
        self,
        db,
        description="Oil Filter",
        quantity=Decimal("10.00"),
        unit_price=Decimal("50.00"),
    ):
        product = create_product(
            db=db,
            description=description,
            quantity=quantity,
            unit_price=unit_price,
            created_by=1,
        )

        db.flush()

        return product

    # ---------------------------------------------------------
    # PRODUCT IS DEACTIVATED
    # ---------------------------------------------------------

    def test_product_is_deactivated(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            product_id = product.id

            self.assertTrue(
                product.is_active
            )

            deactivate_product(
                db=db,
                product_id=product_id,
            )

            self.assertFalse(
                product.is_active
            )

            db.rollback()

    # ---------------------------------------------------------
    # DEACTIVATION IS PERSISTED
    # ---------------------------------------------------------

    def test_deactivation_is_persisted_after_commit(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            product_id = product.id

            deactivate_product(
                db=db,
                product_id=product_id,
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

            self.assertFalse(
                saved_product.is_active
            )

            # Clean up.
            db.delete(saved_product)
            db.commit()

    # ---------------------------------------------------------
    # NONEXISTENT PRODUCT
    # ---------------------------------------------------------

    def test_nonexistent_product_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Product not found",
            ):
                deactivate_product(
                    db=db,
                    product_id=999999,
                )

            db.rollback()

    # ---------------------------------------------------------
    # OTHER PRODUCT REMAINS ACTIVE
    # ---------------------------------------------------------

    def test_other_product_remains_active(self):
        with Session(engine) as db:

            product1 = self.create_test_product(
                db=db,
                description="Oil Filter",
            )

            db.commit()

            product2 = self.create_test_product(
                db=db,
                description="Brake Pad",
            )

            db.flush()

            product1_id = product1.id
            product2_id = product2.id

            deactivate_product(
                db=db,
                product_id=product1_id,
            )

            db.commit()

            deleted_product = db.scalar(
                select(Product).where(
                    Product.id == product1_id
                )
            )

            remaining_product = db.scalar(
                select(Product).where(
                    Product.id == product2_id
                )
            )

            self.assertIsNotNone(
                deleted_product
            )

            self.assertFalse(
                deleted_product.is_active
            )

            self.assertIsNotNone(
                remaining_product
            )

            self.assertTrue(
                remaining_product.is_active
            )

            # Clean up.
            db.delete(deleted_product)
            db.delete(remaining_product)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_deactivation_can_be_rolled_back(self):
        with Session(engine) as db:

            product = self.create_test_product(db)

            product_id = product.id

            # Original state is active.
            db.commit()

            deactivate_product(
                db=db,
                product_id=product_id,
            )

            self.assertFalse(
                product.is_active
            )

            # Undo deactivation.
            db.rollback()

            restored_product = db.scalar(
                select(Product).where(
                    Product.id == product_id
                )
            )

            self.assertIsNotNone(
                restored_product
            )

            self.assertTrue(
                restored_product.is_active
            )

            # Clean up.
            db.delete(restored_product)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )