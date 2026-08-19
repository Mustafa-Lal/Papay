import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine

from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem

from app.services.mechanic_customer import (
    create_mechanic_customer,
)

from app.services.mechanic_invoice import (
    create_mechanic_invoice,
)

from app.services.mechanic_item import (
    create_mechanic_item,
)


class MechanicItemTests(unittest.TestCase):

    def create_invoice(
        self,
        db: Session,
    ) -> MechanicInvoice:

        customer = create_mechanic_customer(
            db=db,
            customer_name="Test Customer",
        )

        db.flush()

        invoice = create_mechanic_invoice(
            db=db,
            customer_id=customer.id,
            plate_number="TEST-123",
            created_by=1,
        )

        db.flush()

        return invoice

    # ---------------------------------------------------------
    # VALID CREATION
    # ---------------------------------------------------------

    def test_create_item_successfully(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            item = create_mechanic_item(
                db=db,
                invoice_id=invoice.id,
                description="Brake Pad",
                quantity=2,
                unit_price=150,
                commission=20,
            )

            db.flush()

            self.assertIsNotNone(item.id)

            self.assertEqual(
                item.invoice_id,
                invoice.id,
            )

            self.assertEqual(
                item.description,
                "Brake Pad",
            )

            self.assertEqual(
                item.quantity,
                Decimal("2"),
            )

            self.assertEqual(
                item.unit_price,
                Decimal("150"),
            )

            self.assertEqual(
                item.commission,
                Decimal("20"),
            )

            db.rollback()

    def test_item_is_saved_to_database(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            item = create_mechanic_item(
                db=db,
                invoice_id=invoice.id,
                description="Oil Filter",
                quantity=1,
                unit_price=75,
            )

            db.flush()

            item_id = item.id

            db.commit()

            saved_item = db.scalar(
                select(MechanicItem).where(
                    MechanicItem.id == item_id
                )
            )

            self.assertIsNotNone(
                saved_item
            )

            self.assertEqual(
                saved_item.description,
                "Oil Filter",
            )

    # ---------------------------------------------------------
    # COMMISSION
    # ---------------------------------------------------------

    def test_commission_defaults_to_zero(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            item = create_mechanic_item(
                db=db,
                invoice_id=invoice.id,
                description="Mirror",
                quantity=1,
                unit_price=100,
            )

            db.flush()

            self.assertEqual(
                item.commission,
                Decimal("0.00"),
            )

            db.rollback()

    def test_commission_can_be_provided(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            item = create_mechanic_item(
                db=db,
                invoice_id=invoice.id,
                description="Mirror",
                quantity=1,
                unit_price=100,
                commission=25,
            )

            db.flush()

            self.assertEqual(
                item.commission,
                Decimal("25"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # DESCRIPTION
    # ---------------------------------------------------------

    def test_description_is_trimmed(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            item = create_mechanic_item(
                db=db,
                invoice_id=invoice.id,
                description="  Brake Pad  ",
                quantity=1,
                unit_price=100,
            )

            db.flush()

            self.assertEqual(
                item.description,
                "Brake Pad",
            )

            db.rollback()

    def test_empty_description_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):

                create_mechanic_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="",
                    quantity=1,
                    unit_price=100,
                )

            db.rollback()

    def test_whitespace_description_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):

                create_mechanic_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="   ",
                    quantity=1,
                    unit_price=100,
                )

            db.rollback()

    # ---------------------------------------------------------
    # QUANTITY
    # ---------------------------------------------------------

    def test_zero_quantity_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):

                create_mechanic_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="Brake Pad",
                    quantity=0,
                    unit_price=100,
                )

            db.rollback()

    def test_negative_quantity_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):

                create_mechanic_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="Brake Pad",
                    quantity=-1,
                    unit_price=100,
                )

            db.rollback()

    # ---------------------------------------------------------
    # UNIT PRICE
    # ---------------------------------------------------------

    def test_negative_unit_price_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):

                create_mechanic_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="Brake Pad",
                    quantity=1,
                    unit_price=-100,
                )

            db.rollback()

    # ---------------------------------------------------------
    # COMMISSION VALIDATION
    # ---------------------------------------------------------

    def test_negative_commission_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):

                create_mechanic_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="Brake Pad",
                    quantity=1,
                    unit_price=100,
                    commission=-10,
                )

            db.rollback()

    # ---------------------------------------------------------
    # INVOICE VALIDATION
    # ---------------------------------------------------------

    def test_nonexistent_invoice_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_mechanic_item(
                    db=db,
                    invoice_id=999999,
                    description="Brake Pad",
                    quantity=1,
                    unit_price=100,
                )

    # ---------------------------------------------------------
    # MULTIPLE ITEMS
    # ---------------------------------------------------------

    def test_multiple_items_can_belong_to_same_invoice(self):
        with Session(engine) as db:

            invoice = self.create_invoice(db)

            item_1 = create_mechanic_item(
                db=db,
                invoice_id=invoice.id,
                description="Brake Pad",
                quantity=2,
                unit_price=150,
            )

            item_2 = create_mechanic_item(
                db=db,
                invoice_id=invoice.id,
                description="Oil Filter",
                quantity=1,
                unit_price=75,
            )

            db.flush()

            self.assertNotEqual(
                item_1.id,
                item_2.id,
            )

            self.assertEqual(
                item_1.invoice_id,
                invoice.id,
            )

            self.assertEqual(
                item_2.invoice_id,
                invoice.id,
            )

            db.rollback()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )