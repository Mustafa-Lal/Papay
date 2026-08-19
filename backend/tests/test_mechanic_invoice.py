import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_invoice import PaymentStatus
from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice

from app.services.mechanic_customer import (
    create_mechanic_customer,
)

from app.services.mechanic_invoice import (
    create_mechanic_invoice,
)


class MechanicInvoiceTests(unittest.TestCase):

    def create_customer(
        self,
        db: Session,
    ) -> MechanicCustomer:

        customer = create_mechanic_customer(
            db=db,
            customer_name="Test Customer",
            phone_number="55555555",
            qid="12345678901",
        )

        db.flush()

        return customer

    # ---------------------------------------------------------
    # VALID CREATION
    # ---------------------------------------------------------

    def test_create_invoice_successfully(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = create_mechanic_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="ABC-123",
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(invoice.id)

            self.assertEqual(
                invoice.customer_id,
                customer.id,
            )

            self.assertEqual(
                invoice.plate_number,
                "ABC-123",
            )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("0.00"),
            )

            self.assertEqual(
                invoice.payment_status,
                PaymentStatus.UNPAID,
            )

            self.assertIsNotNone(
                invoice.created_at
            )

            self.assertIsNotNone(
                invoice.updated_at
            )

            db.rollback()

    def test_invoice_is_saved_to_database(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = create_mechanic_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="SAVE-123",
                created_by=1,
            )

            db.flush()

            invoice_id = invoice.id

            db.commit()

            saved_invoice = db.scalar(
                select(MechanicInvoice).where(
                    MechanicInvoice.id == invoice_id
                )
            )

            self.assertIsNotNone(
                saved_invoice
            )

            self.assertEqual(
                saved_invoice.plate_number,
                "SAVE-123",
            )

    # ---------------------------------------------------------
    # LABOR CHARGES
    # ---------------------------------------------------------

    def test_labor_charges_can_be_provided(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = create_mechanic_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="LABOR-123",
                created_by=1,
                labor_charges=Decimal("750.00"),
            )

            db.flush()

            self.assertEqual(
                invoice.labor_charges,
                Decimal("750.00"),
            )

            db.rollback()

    def test_labor_charges_default_to_zero(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = create_mechanic_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="ZERO-123",
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                invoice.labor_charges,
                Decimal("0.00"),
            )

            db.rollback()

    def test_negative_labor_charges_are_rejected(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            with self.assertRaises(ValueError):

                create_mechanic_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number="NEGATIVE-123",
                    created_by=1,
                    labor_charges=Decimal("-100.00"),
                )

            db.rollback()

    # ---------------------------------------------------------
    # PAYMENT STATUS
    # ---------------------------------------------------------

    def test_payment_status_can_be_changed(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = create_mechanic_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="PAID-123",
                created_by=1,
                payment_status=PaymentStatus.PAID,
            )

            db.flush()

            self.assertEqual(
                invoice.payment_status,
                PaymentStatus.PAID,
            )

            db.rollback()

    # ---------------------------------------------------------
    # CUSTOMER VALIDATION
    # ---------------------------------------------------------

    def test_nonexistent_customer_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaises(ValueError):

                create_mechanic_invoice(
                    db=db,
                    customer_id=999999,
                    plate_number="INVALID-123",
                    created_by=1,
                )

    # ---------------------------------------------------------
    # PLATE NUMBER VALIDATION
    # ---------------------------------------------------------

    def test_empty_plate_number_is_rejected(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            with self.assertRaises(ValueError):

                create_mechanic_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number="",
                    created_by=1,
                )

            db.rollback()

    def test_whitespace_plate_number_is_rejected(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            with self.assertRaises(ValueError):

                create_mechanic_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number="   ",
                    created_by=1,
                )

            db.rollback()

    def test_plate_number_is_trimmed(self):
        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = create_mechanic_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="  ABC-123  ",
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                invoice.plate_number,
                "ABC-123",
            )

            db.rollback()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )