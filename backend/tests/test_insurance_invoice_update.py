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
from app.services.insurance_invoice_update import (
    update_insurance_invoice,
)


class InsuranceInvoiceUpdateTests(unittest.TestCase):

    def create_test_invoice(self, db):
        customer = create_insurance_customer(
            db=db,
            customer_name="Test Customer",
            phone_number="11111111",
            qid="11111111111",
        )

        db.flush()

        invoice = create_insurance_invoice(
            db=db,
            customer_id=customer.id,
            plate_number="OLD-123",
            labor_charges=Decimal("100.00"),
            created_by=1,
        )

        db.flush()

        return invoice

    # ---------------------------------------------------------
    # PLATE NUMBER
    # ---------------------------------------------------------

    def test_update_plate_number(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            update_insurance_invoice(
                db=db,
                invoice_id=invoice.id,
                plate_number="NEW-456",
            )

            self.assertEqual(
                invoice.plate_number,
                "NEW-456",
            )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("100.00"),
            )

            db.rollback()

    def test_updated_plate_number_is_trimmed(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            update_insurance_invoice(
                db=db,
                invoice_id=invoice.id,
                plate_number="  NEW-456  ",
            )

            self.assertEqual(
                invoice.plate_number,
                "NEW-456",
            )

            db.rollback()

    def test_empty_plate_number_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            with self.assertRaisesRegex(
                ValueError,
                "Plate number cannot be empty",
            ):
                update_insurance_invoice(
                    db=db,
                    invoice_id=invoice.id,
                    plate_number="",
                )

            self.assertEqual(
                invoice.plate_number,
                "OLD-123",
            )

            db.rollback()

    def test_whitespace_plate_number_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            with self.assertRaisesRegex(
                ValueError,
                "Plate number cannot be empty",
            ):
                update_insurance_invoice(
                    db=db,
                    invoice_id=invoice.id,
                    plate_number="   ",
                )

            self.assertEqual(
                invoice.plate_number,
                "OLD-123",
            )

            db.rollback()

    # ---------------------------------------------------------
    # LABOR CHARGES
    # ---------------------------------------------------------

    def test_update_labor_charges(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            update_insurance_invoice(
                db=db,
                invoice_id=invoice.id,
                labor_charges=Decimal("500.00"),
            )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("500.00"),
            )

            self.assertEqual(
                invoice.plate_number,
                "OLD-123",
            )

            db.rollback()

    def test_zero_labor_charges_are_allowed(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            update_insurance_invoice(
                db=db,
                invoice_id=invoice.id,
                labor_charges=Decimal("0.00"),
            )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("0.00"),
            )

            db.rollback()

    def test_negative_labor_charges_are_rejected(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            with self.assertRaisesRegex(
                ValueError,
                "Labor charges cannot be negative",
            ):
                update_insurance_invoice(
                    db=db,
                    invoice_id=invoice.id,
                    labor_charges=Decimal("-50.00"),
                )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("100.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # PAYMENT STATUS
    # ---------------------------------------------------------

    def test_update_payment_status(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            update_insurance_invoice(
                db=db,
                invoice_id=invoice.id,
                payment_status=PaymentStatus.PAID,
            )

            self.assertEqual(
                invoice.payment_status,
                PaymentStatus.PAID,
            )

            db.rollback()

    def test_invalid_payment_status_is_rejected(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            with self.assertRaisesRegex(
                ValueError,
                "Invalid payment status",
            ):
                update_insurance_invoice(
                    db=db,
                    invoice_id=invoice.id,
                    payment_status="INVALID",
                )

            db.rollback()

    # ---------------------------------------------------------
    # ALL FIELDS
    # ---------------------------------------------------------

    def test_update_all_invoice_fields(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            update_insurance_invoice(
                db=db,
                invoice_id=invoice.id,
                plate_number="NEW-999",
                labor_charges=Decimal("750.00"),
                payment_status=PaymentStatus.PAID,
            )

            self.assertEqual(
                invoice.plate_number,
                "NEW-999",
            )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("750.00"),
            )

            self.assertEqual(
                invoice.payment_status,
                PaymentStatus.PAID,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PARTIAL UPDATE
    # ---------------------------------------------------------

    def test_partial_update_does_not_change_other_fields(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            update_insurance_invoice(
                db=db,
                invoice_id=invoice.id,
                plate_number="ONLY-PLATE",
            )

            self.assertEqual(
                invoice.plate_number,
                "ONLY-PLATE",
            )

            self.assertEqual(
                invoice.labor_charges,
                Decimal("100.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_invoice_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Insurance invoice not found",
            ):
                update_insurance_invoice(
                    db=db,
                    invoice_id=999999,
                    plate_number="NEW-123",
                )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            invoice_id = invoice.id

            update_insurance_invoice(
                db=db,
                invoice_id=invoice_id,
                plate_number="PERSISTED",
                labor_charges=Decimal("800.00"),
                payment_status=PaymentStatus.PAID,
            )

            db.commit()

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
                "PERSISTED",
            )

            self.assertEqual(
                saved_invoice.labor_charges,
                Decimal("800.00"),
            )

            self.assertEqual(
                saved_invoice.payment_status,
                PaymentStatus.PAID,
            )

            # Clean up the committed invoice and customer.
            customer = db.scalar(
                select(InsuranceCustomer).where(
                    InsuranceCustomer.id
                    == saved_invoice.customer_id
                )
            )

            db.delete(saved_invoice)

            if customer is not None:
                db.delete(customer)

            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            invoice = self.create_test_invoice(db)

            db.commit()

            invoice_id = invoice.id

            update_insurance_invoice(
                db=db,
                invoice_id=invoice_id,
                plate_number="TEMP-999",
                labor_charges=Decimal("999.00"),
                payment_status=PaymentStatus.PAID,
            )

            db.rollback()

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
                "OLD-123",
            )

            self.assertEqual(
                saved_invoice.labor_charges,
                Decimal("100.00"),
            )

            # Clean up.
            customer = db.scalar(
                select(InsuranceCustomer).where(
                    InsuranceCustomer.id
                    == saved_invoice.customer_id
                )
            )

            db.delete(saved_invoice)

            if customer is not None:
                db.delete(customer)

            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )