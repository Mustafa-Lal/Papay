import unittest
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import engine

from app.models.insurance_invoice import PaymentStatus
from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem

from app.services.mechanic_invoice_creation import (
    create_mechanic_invoice_transaction,
)


class MechanicInvoiceCreationTests(unittest.TestCase):

    def test_complete_invoice_creation(self):
        """
        Customer + invoice + multiple items should all
        be created successfully.
        """

        with Session(engine) as db:

            invoice = create_mechanic_invoice_transaction(
                db=db,
                customer_name="Ahmed",
                phone_number="55555555",
                qid="12345678901",
                plate_number="ABC-123",
                created_by=1,
                labor_charges=Decimal("500.00"),
                payment_status=PaymentStatus.UNPAID,
                items=[
                    {
                        "description": "Brake Pad",
                        "quantity": Decimal("2"),
                        "unit_price": Decimal("150.00"),
                        "commission": Decimal("20.00"),
                    },
                    {
                        "description": "Oil Filter",
                        "quantity": Decimal("1"),
                        "unit_price": Decimal("75.00"),
                    },
                ],
            )

            self.assertIsNotNone(invoice.id)

            saved_invoice = db.scalar(
                select(MechanicInvoice).where(
                    MechanicInvoice.id == invoice.id
                )
            )

            self.assertIsNotNone(
                saved_invoice
            )

            customer = db.scalar(
                select(MechanicCustomer).where(
                    MechanicCustomer.id
                    == saved_invoice.customer_id
                )
            )

            self.assertIsNotNone(
                customer
            )

            items = db.scalars(
                select(MechanicItem).where(
                    MechanicItem.invoice_id
                    == invoice.id
                )
            ).all()

            self.assertEqual(
                len(items),
                2,
            )

    def test_commission_defaults_to_zero(self):
        """
        Items without commission should receive 0.00.
        """

        with Session(engine) as db:

            invoice = create_mechanic_invoice_transaction(
                db=db,
                customer_name="Ahmed",
                phone_number=None,
                qid=None,
                plate_number="COM-123",
                created_by=1,
                items=[
                    {
                        "description": "Mirror",
                        "quantity": Decimal("1"),
                        "unit_price": Decimal("100.00"),
                    }
                ],
            )

            item = db.scalar(
                select(MechanicItem).where(
                    MechanicItem.invoice_id
                    == invoice.id
                )
            )

            self.assertIsNotNone(item)

            self.assertEqual(
                item.commission,
                Decimal("0.00"),
            )

    def test_empty_plate_rolls_back_customer(self):
        """
        Invalid invoice data must prevent the customer
        from being persisted.
        """

        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_mechanic_invoice_transaction(
                    db=db,
                    customer_name="Rollback Customer",
                    phone_number="55555555",
                    qid=None,
                    plate_number="",
                    created_by=1,
                    items=[],
                )

            customer_count = db.scalar(
                select(
                    func.count(MechanicCustomer.id)
                ).where(
                    MechanicCustomer.customer_name
                    == "Rollback Customer"
                )
            )

            self.assertEqual(
                customer_count,
                0,
            )

    def test_negative_labor_rolls_back_customer(self):
        """
        Negative labor charges should roll back the
        entire transaction.
        """

        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_mechanic_invoice_transaction(
                    db=db,
                    customer_name="Labor Rollback",
                    phone_number="55555555",
                    qid=None,
                    plate_number="LABOR-123",
                    created_by=1,
                    labor_charges=Decimal("-100.00"),
                    items=[],
                )

            customer_count = db.scalar(
                select(
                    func.count(MechanicCustomer.id)
                ).where(
                    MechanicCustomer.customer_name
                    == "Labor Rollback"
                )
            )

            self.assertEqual(
                customer_count,
                0,
            )

    def test_invalid_item_rolls_back_everything(self):
        """
        If one item fails, customer, invoice, and previous
        items must all be rolled back.
        """

        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_mechanic_invoice_transaction(
                    db=db,
                    customer_name="Item Rollback",
                    phone_number="55555555",
                    qid=None,
                    plate_number="ITEM-123",
                    created_by=1,
                    items=[
                        {
                            "description": "Valid Item",
                            "quantity": Decimal("1"),
                            "unit_price": Decimal("100.00"),
                        },
                        {
                            "description": "Invalid Item",
                            "quantity": Decimal("0"),
                            "unit_price": Decimal("100.00"),
                        },
                    ],
                )

            customer_count = db.scalar(
                select(
                    func.count(MechanicCustomer.id)
                ).where(
                    MechanicCustomer.customer_name
                    == "Item Rollback"
                )
            )

            self.assertEqual(
                customer_count,
                0,
            )

            invoice_count = db.scalar(
                select(
                    func.count(MechanicInvoice.id)
                ).where(
                    MechanicInvoice.plate_number
                    == "ITEM-123"
                )
            )

            self.assertEqual(
                invoice_count,
                0,
            )

    def test_multiple_items_belong_to_same_invoice(self):
        """
        Multiple items should be associated with the same
        invoice.
        """

        with Session(engine) as db:

            invoice = create_mechanic_invoice_transaction(
                db=db,
                customer_name="Multiple Items",
                phone_number=None,
                qid=None,
                plate_number="MULTI-123",
                created_by=1,
                items=[
                    {
                        "description": "Item 1",
                        "quantity": Decimal("1"),
                        "unit_price": Decimal("100"),
                    },
                    {
                        "description": "Item 2",
                        "quantity": Decimal("2"),
                        "unit_price": Decimal("200"),
                    },
                    {
                        "description": "Item 3",
                        "quantity": Decimal("3"),
                        "unit_price": Decimal("300"),
                    },
                ],
            )

            items = db.scalars(
                select(MechanicItem).where(
                    MechanicItem.invoice_id
                    == invoice.id
                )
            ).all()

            self.assertEqual(
                len(items),
                3,
            )

            for item in items:
                self.assertEqual(
                    item.invoice_id,
                    invoice.id,
                )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )