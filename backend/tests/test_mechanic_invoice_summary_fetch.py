import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine

from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice
from app.models.insurance_invoice import PaymentStatus

from app.services.mechanic_customer import (
    create_mechanic_customer,
)
from app.services.mechanic_invoice import (
    create_mechanic_invoice,
)
from app.services.mechanic_invoice_summary_fetch import (
    get_mechanic_customer_invoices,
)


class MechanicCustomerInvoicesTests(unittest.TestCase):

    def create_test_customer(self, db):
        customer = create_mechanic_customer(
            db=db,
            customer_name="Ahmed Ali",
            phone_number="55555555",
            qid="12345678901",
        )

        db.flush()

        return customer

    def create_test_invoice(
        self,
        db,
        customer_id,
        plate_number,
    ):
        invoice = create_mechanic_invoice(
            db=db,
            customer_id=customer_id,
            plate_number=plate_number,
            labor_charges=Decimal("100.00"),
            created_by=1,
        )

        db.flush()

        return invoice

    # ---------------------------------------------------------
    # CUSTOMER AND INVOICE SUMMARY
    # ---------------------------------------------------------

    def test_customer_and_invoice_summary_are_returned(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            invoice = self.create_test_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="ABC-123",
            )

            db.commit()

            result = get_mechanic_customer_invoices(
                db=db,
                customer_id=customer.id,
            )

            # Customer
            self.assertEqual(
                result["customer"]["id"],
                customer.id,
            )

            self.assertEqual(
                result["customer"]["name"],
                "Ahmed Ali",
            )

            self.assertEqual(
                result["customer"]["phone_number"],
                "55555555",
            )

            # Invoice
            self.assertEqual(
                len(result["invoices"]),
                1,
            )

            returned_invoice = result["invoices"][0]

            self.assertEqual(
                returned_invoice["id"],
                invoice.id,
            )

            self.assertEqual(
                returned_invoice["plate_number"],
                "ABC-123",
            )

            self.assertEqual(
                returned_invoice["invoice_date"],
                invoice.created_at,
            )

            self.assertEqual(
                returned_invoice["payment_status"],
                PaymentStatus.UNPAID.value,
            )

            # Clean up
            db.delete(invoice)
            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # DEFAULT LIMIT
    # ---------------------------------------------------------

    def test_default_limit_returns_at_most_ten_invoices(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            for index in range(15):
                self.create_test_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number=f"CAR-{index}",
                )

            db.commit()

            result = get_mechanic_customer_invoices(
                db=db,
                customer_id=customer.id,
            )

            self.assertEqual(
                len(result["invoices"]),
                10,
            )

            self.assertEqual(
                result["pagination"]["limit"],
                10,
            )

            self.assertEqual(
                result["pagination"]["offset"],
                0,
            )

            self.assertEqual(
                result["pagination"]["total"],
                15,
            )

            self.assertTrue(
                result["pagination"]["has_more"]
            )

            # Clean up
            invoices = db.scalars(
                select(MechanicInvoice).where(
                    MechanicInvoice.customer_id
                    == customer.id
                )
            ).all()

            for invoice in invoices:
                db.delete(invoice)

            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # CUSTOM LIMIT AND OFFSET
    # ---------------------------------------------------------

    def test_limit_and_offset_work_correctly(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            for index in range(15):
                self.create_test_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number=f"CAR-{index}",
                )

            db.commit()

            result = get_mechanic_customer_invoices(
                db=db,
                customer_id=customer.id,
                limit=5,
                offset=5,
            )

            self.assertEqual(
                len(result["invoices"]),
                5,
            )

            self.assertEqual(
                result["pagination"]["limit"],
                5,
            )

            self.assertEqual(
                result["pagination"]["offset"],
                5,
            )

            self.assertEqual(
                result["pagination"]["total"],
                15,
            )

            self.assertTrue(
                result["pagination"]["has_more"]
            )

            # Clean up
            invoices = db.scalars(
                select(MechanicInvoice).where(
                    MechanicInvoice.customer_id
                    == customer.id
                )
            ).all()

            for invoice in invoices:
                db.delete(invoice)

            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # FEWER RECORDS THAN LIMIT
    # ---------------------------------------------------------

    def test_returns_remaining_records_when_less_than_limit(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            for index in range(16):
                self.create_test_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number=f"CAR-{index}",
                )

            db.commit()

            result = get_mechanic_customer_invoices(
                db=db,
                customer_id=customer.id,
                limit=10,
                offset=10,
            )

            # Only 6 remain.
            self.assertEqual(
                len(result["invoices"]),
                6,
            )

            self.assertEqual(
                result["pagination"]["total"],
                16,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            # Clean up
            invoices = db.scalars(
                select(MechanicInvoice).where(
                    MechanicInvoice.customer_id
                    == customer.id
                )
            ).all()

            for invoice in invoices:
                db.delete(invoice)

            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # OFFSET BEYOND RECORDS
    # ---------------------------------------------------------

    def test_offset_beyond_records_returns_empty_list(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            for index in range(5):
                self.create_test_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number=f"CAR-{index}",
                )

            db.commit()

            result = get_mechanic_customer_invoices(
                db=db,
                customer_id=customer.id,
                limit=10,
                offset=10,
            )

            self.assertEqual(
                len(result["invoices"]),
                0,
            )

            self.assertEqual(
                result["pagination"]["total"],
                5,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            # Clean up
            invoices = db.scalars(
                select(MechanicInvoice).where(
                    MechanicInvoice.customer_id
                    == customer.id
                )
            ).all()

            for invoice in invoices:
                db.delete(invoice)

            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # INACTIVE CUSTOMER
    # ---------------------------------------------------------

    def test_inactive_customer_is_rejected(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            customer.is_active = False

            db.commit()

            with self.assertRaisesRegex(
                ValueError,
                "Mechanic customer not found",
            ):
                get_mechanic_customer_invoices(
                    db=db,
                    customer_id=customer.id,
                )

            # Clean up
            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # NONEXISTENT CUSTOMER
    # ---------------------------------------------------------

    def test_nonexistent_customer_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Mechanic customer not found",
            ):
                get_mechanic_customer_invoices(
                    db=db,
                    customer_id=999999,
                )

    # ---------------------------------------------------------
    # ZERO LIMIT
    # ---------------------------------------------------------

    def test_zero_limit_is_rejected(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            with self.assertRaisesRegex(
                ValueError,
                "Limit must be greater than zero",
            ):
                get_mechanic_customer_invoices(
                    db=db,
                    customer_id=customer.id,
                    limit=0,
                )

            db.rollback()

    # ---------------------------------------------------------
    # NEGATIVE OFFSET
    # ---------------------------------------------------------

    def test_negative_offset_is_rejected(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            with self.assertRaisesRegex(
                ValueError,
                "Offset cannot be negative",
            ):
                get_mechanic_customer_invoices(
                    db=db,
                    customer_id=customer.id,
                    offset=-1,
                )

            db.rollback()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )