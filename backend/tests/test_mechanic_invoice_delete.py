import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem

from app.services.mechanic_customer import create_mechanic_customer
from app.services.mechanic_invoice import create_mechanic_invoice
from app.services.mechanic_item import create_mechanic_item
from app.services.mechanic_invoice_deletion import delete_mechanic_invoice


class MechanicInvoiceDeleteTests(unittest.TestCase):

    def create_invoice_with_items(self, db, plate_number="ABC-123"):
        customer = create_mechanic_customer(
            db=db,
            customer_name="Test Customer",
            phone_number="11111111",
            qid="11111111111",
        )

        db.flush()

        invoice = create_mechanic_invoice(
            db=db,
            customer_id=customer.id,
            plate_number=plate_number,
            labor_charges=Decimal("100.00"),
            created_by=1,
        )

        db.flush()

        item1 = create_mechanic_item(
            db=db,
            invoice_id=invoice.id,
            description="Oil Filter",
            quantity=Decimal("1.00"),
            unit_price=Decimal("50.00"),
            commission=Decimal("5.00"),
        )

        item2 = create_mechanic_item(
            db=db,
            invoice_id=invoice.id,
            description="Brake Pad",
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            commission=Decimal("10.00"),
        )

        db.flush()

        return customer, invoice, item1, item2

    # ---------------------------------------------------------
    # INVOICE AND ITEMS ARE DELETED
    # ---------------------------------------------------------

    def test_invoice_and_items_are_deleted(self):
        with Session(engine) as db:

            customer, invoice, item1, item2 = (
                self.create_invoice_with_items(db)
            )

            invoice_id = invoice.id
            item1_id = item1.id
            item2_id = item2.id

            delete_mechanic_invoice(
                db=db,
                invoice_id=invoice_id,
            )

            db.commit()

            saved_invoice = db.scalar(
                select(MechanicInvoice).where(
                    MechanicInvoice.id == invoice_id
                )
            )

            saved_item1 = db.scalar(
                select(MechanicItem).where(
                    MechanicItem.id == item1_id
                )
            )

            saved_item2 = db.scalar(
                select(MechanicItem).where(
                    MechanicItem.id == item2_id
                )
            )

            self.assertIsNone(saved_invoice)
            self.assertIsNone(saved_item1)
            self.assertIsNone(saved_item2)

            # Customer is NOT deleted.
            saved_customer = db.scalar(
                select(MechanicCustomer).where(
                    MechanicCustomer.id == customer.id
                )
            )

            self.assertIsNotNone(saved_customer)

            db.delete(saved_customer)
            db.commit()

    # ---------------------------------------------------------
    # NONEXISTENT INVOICE
    # ---------------------------------------------------------

    def test_nonexistent_invoice_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Mechanic invoice not found",
            ):
                delete_mechanic_invoice(
                    db=db,
                    invoice_id=999999,
                )

            db.rollback()

    # ---------------------------------------------------------
    # OTHER INVOICE REMAINS
    # ---------------------------------------------------------

    def test_other_invoice_and_items_remain(self):
        with Session(engine) as db:

            customer, invoice1, item1, item2 = (
                self.create_invoice_with_items(
                    db,
                    plate_number="FIRST-123",
                )
            )

            db.flush()

            invoice2 = create_mechanic_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="SECOND-456",
                labor_charges=Decimal("200.00"),
                created_by=1,
            )

            db.flush()

            item3 = create_mechanic_item(
                db=db,
                invoice_id=invoice2.id,
                description="Tire",
                quantity=Decimal("4.00"),
                unit_price=Decimal("20.00"),
                commission=Decimal("2.00"),
            )

            db.flush()

            invoice2_id = invoice2.id
            item3_id = item3.id

            delete_mechanic_invoice(
                db=db,
                invoice_id=invoice1.id,
            )

            db.commit()

            remaining_invoice = db.scalar(
                select(MechanicInvoice).where(
                    MechanicInvoice.id == invoice2_id
                )
            )

            remaining_item = db.scalar(
                select(MechanicItem).where(
                    MechanicItem.id == item3_id
                )
            )

            self.assertIsNotNone(remaining_invoice)
            self.assertIsNotNone(remaining_item)

            # Clean up.
            db.delete(remaining_item)
            db.delete(remaining_invoice)
            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_delete_can_be_rolled_back(self):
        with Session(engine) as db:

            customer, invoice, item1, item2 = (
                self.create_invoice_with_items(db)
            )

            invoice_id = invoice.id
            item1_id = item1.id
            item2_id = item2.id

            # Commit original records first.
            db.commit()

            delete_mechanic_invoice(
                db=db,
                invoice_id=invoice_id,
            )

            # Undo deletion.
            db.rollback()

            restored_invoice = db.scalar(
                select(MechanicInvoice).where(
                    MechanicInvoice.id == invoice_id
                )
            )

            restored_item1 = db.scalar(
                select(MechanicItem).where(
                    MechanicItem.id == item1_id
                )
            )

            restored_item2 = db.scalar(
                select(MechanicItem).where(
                    MechanicItem.id == item2_id
                )
            )

            self.assertIsNotNone(restored_invoice)
            self.assertIsNotNone(restored_item1)
            self.assertIsNotNone(restored_item2)

            # Clean up.
            db.delete(restored_item1)
            db.delete(restored_item2)
            db.delete(restored_invoice)
            db.delete(customer)
            db.commit()


if __name__ == "__main__":
    unittest.main(verbosity=2)