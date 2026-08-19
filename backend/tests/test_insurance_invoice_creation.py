"""
Tests for the complete insurance invoice creation transaction.

The transaction creates:

    Customer
        +
    Invoice
        +
    Items

Everything must commit together.

If anything fails, everything must roll back.
"""

import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem
from app.services.insurance_invoice import PaymentStatus
from app.services.insurance_invoice_creation import (
    InsuranceItemData,
    create_insurance_invoice_transaction,
)


class InsuranceInvoiceCreationTests(unittest.TestCase):

    def test_complete_invoice_creation(self):
        """
        Customer + invoice + multiple items should all
        be created successfully.
        """

        with Session(engine) as db:

            result = create_insurance_invoice_transaction(
                db=db,

                customer_name="Ahmed",
                phone_number="55555555",
                qid="123456789",

                plate_number="12345",

                labor_charges=Decimal("500.00"),

                payment_status=PaymentStatus.UNPAID,

                created_by=1,

                items=[
                    InsuranceItemData(
                        description="Front Bumper",
                        quantity=Decimal("1"),
                        unit_price=Decimal("800.00"),
                    ),
                    InsuranceItemData(
                        description="Headlight",
                        quantity=Decimal("2"),
                        unit_price=Decimal("300.00"),
                        commission=Decimal("50.00"),
                    ),
                ],
            )

            self.assertIsNotNone(
                result.customer.id
            )

            self.assertIsNotNone(
                result.invoice.id
            )

            self.assertEqual(
                len(result.items),
                2,
            )

            self.assertEqual(
                result.invoice.customer_id,
                result.customer.id,
            )

            for item in result.items:
                self.assertEqual(
                    item.invoice_id,
                    result.invoice.id,
                )

    def test_commission_defaults_to_zero(self):
        """Items without commission should receive 0.00."""

        with Session(engine) as db:

            result = create_insurance_invoice_transaction(
                db=db,

                plate_number="ZERO-COMMISSION",

                created_by=1,

                items=[
                    InsuranceItemData(
                        description="Mirror",
                        quantity=Decimal("1"),
                        unit_price=Decimal("100.00"),
                    )
                ],
            )

            self.assertEqual(
                result.items[0].commission,
                Decimal("0.00"),
            )

    def test_invalid_item_rolls_back_everything(self):
        """
        If one item fails, customer and invoice must
        also be rolled back.
        """

        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_insurance_invoice_transaction(
                    db=db,

                    customer_name="Rollback Customer",
                    phone_number="55555555",

                    plate_number="ROLLBACK-123",

                    created_by=1,

                    items=[
                        InsuranceItemData(
                            description="Valid Item",
                            quantity=Decimal("1"),
                            unit_price=Decimal("100.00"),
                        ),
                        InsuranceItemData(
                            description="",
                            quantity=Decimal("1"),
                            unit_price=Decimal("100.00"),
                        ),
                    ],
                )

            # Transaction was rolled back.

            customer = db.scalar(
                select(InsuranceCustomer).where(
                    InsuranceCustomer.customer_name
                    == "Rollback Customer"
                )
            )

            self.assertIsNone(customer)

            invoice = db.scalar(
                select(InsuranceInvoice).where(
                    InsuranceInvoice.plate_number
                    == "ROLLBACK-123"
                )
            )

            self.assertIsNone(invoice)

    def test_empty_plate_rolls_back_customer(self):
        """
        Invalid invoice data must prevent the customer
        from being persisted.
        """

        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_insurance_invoice_transaction(
                    db=db,

                    customer_name="Customer Should Rollback",

                    plate_number="",

                    created_by=1,

                    items=[
                        InsuranceItemData(
                            description="Bumper",
                            quantity=Decimal("1"),
                            unit_price=Decimal("100.00"),
                        )
                    ],
                )

            customer = db.scalar(
                select(InsuranceCustomer).where(
                    InsuranceCustomer.customer_name
                    == "Customer Should Rollback"
                )
            )

            self.assertIsNone(customer)

    def test_negative_labor_rolls_back_customer(self):
        """Negative labor charges should roll back the transaction."""

        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_insurance_invoice_transaction(
                    db=db,

                    customer_name="Labor Rollback",

                    plate_number="LABOR-123",

                    labor_charges=Decimal("-100.00"),

                    created_by=1,

                    items=[
                        InsuranceItemData(
                            description="Bumper",
                            quantity=Decimal("1"),
                            unit_price=Decimal("100.00"),
                        )
                    ],
                )

            customer = db.scalar(
                select(InsuranceCustomer).where(
                    InsuranceCustomer.customer_name
                    == "Labor Rollback"
                )
            )

            self.assertIsNone(customer)


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )