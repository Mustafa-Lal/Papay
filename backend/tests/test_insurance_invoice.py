"""
Tests for the insurance invoice service.

Tests both valid and invalid invoice creation.
"""

import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import (
    InsuranceInvoice,
    PaymentStatus,
)
from app.services.insurance_customer import (
    create_insurance_customer,
)
from app.services.insurance_invoice import (
    create_insurance_invoice,
)


class InsuranceInvoiceTests(unittest.TestCase):

    def create_customer(self, db):
        return create_insurance_customer(
            db=db,
            customer_name="Test Customer",
        )

    def test_create_invoice_successfully(self):
        """A valid customer and plate should create an invoice."""

        with Session(engine) as db:
            customer = self.create_customer(db)

            invoice = create_insurance_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="12345",
                created_by=1,
            )

            self.assertIsNotNone(invoice.id)

            self.assertEqual(
                invoice.customer_id,
                customer.id,
            )

            self.assertEqual(
                invoice.plate_number,
                "12345",
            )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("0.00"),
            )

            self.assertEqual(
                invoice.payment_status,
                PaymentStatus.UNPAID,
            )

            self.assertEqual(
                invoice.created_by,
                1,
            )

    def test_labor_charges_can_be_provided(self):
        """Labor charges should be stored correctly."""

        with Session(engine) as db:
            customer = self.create_customer(db)

            invoice = create_insurance_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="54321",
                created_by=1,
                labor_charges=Decimal("250.50"),
            )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("250.50"),
            )

    def test_payment_status_can_be_changed(self):
        """A valid payment status should be stored."""

        with Session(engine) as db:
            customer = self.create_customer(db)

            invoice = create_insurance_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="11111",
                created_by=1,
                payment_status=PaymentStatus.PAID,
            )

            self.assertEqual(
                invoice.payment_status,
                PaymentStatus.PAID,
            )

    def test_nonexistent_customer_is_rejected(self):
        """An invoice cannot reference a nonexistent customer."""

        with Session(engine) as db:
            with self.assertRaises(ValueError):
                create_insurance_invoice(
                    db=db,
                    customer_id=999999,
                    plate_number="12345",
                    created_by=1,
                )

    def test_empty_plate_number_is_rejected(self):
        """Plate number is mandatory."""

        with Session(engine) as db:
            customer = self.create_customer(db)

            with self.assertRaises(ValueError):
                create_insurance_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number="",
                    created_by=1,
                )

    def test_whitespace_plate_number_is_rejected(self):
        """Whitespace-only plate numbers are invalid."""

        with Session(engine) as db:
            customer = self.create_customer(db)

            with self.assertRaises(ValueError):
                create_insurance_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number="   ",
                    created_by=1,
                )

    def test_negative_labor_charges_are_rejected(self):
        """Labor charges cannot be negative."""

        with Session(engine) as db:
            customer = self.create_customer(db)

            with self.assertRaises(ValueError):
                create_insurance_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number="12345",
                    created_by=1,
                    labor_charges=Decimal("-10.00"),
                )

    def test_plate_number_is_trimmed(self):
        """Leading/trailing whitespace should be removed."""

        with Session(engine) as db:
            customer = self.create_customer(db)

            invoice = create_insurance_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="  ABC-123  ",
                created_by=1,
            )

            self.assertEqual(
                invoice.plate_number,
                "ABC-123",
            )

    def test_invoice_is_saved_to_database(self):
        """The invoice must persist after creation."""

        with Session(engine) as db:
            customer = self.create_customer(db)

            invoice = create_insurance_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="99999",
                created_by=1,
            )

            invoice_id = invoice.id

            saved_invoice = db.scalar(
                select(InsuranceInvoice).where(
                    InsuranceInvoice.id == invoice_id
                )
            )

            self.assertIsNotNone(
                saved_invoice
            )

            self.assertEqual(
                saved_invoice.plate_number,
                "99999",
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )