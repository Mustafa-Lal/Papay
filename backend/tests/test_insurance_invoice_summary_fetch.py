import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import InsuranceInvoice, PaymentStatus

from app.services.insurance_invoice_summary_fetch import (
    get_insurance_customers,
    get_insurance_customers_this_month,
)


class InsuranceCustomerFetchTests(unittest.TestCase):

    def create_customer(
        self,
        db,
        name="Ahmed Ali",
        phone="55555555",
    ):
        customer = InsuranceCustomer(
            customer_name=name,
            phone_number=phone,
            qid="12345678901",
            is_active=True,
        )

        db.add(customer)
        db.flush()

        return customer

    def create_invoice(
        self,
        db,
        customer_id,
        plate_number="ABC-123",
    ):
        invoice = InsuranceInvoice(
            customer_id=customer_id,
            plate_number=plate_number,
            labor_charges=Decimal("100.00"),
            payment_status=PaymentStatus.UNPAID,
            created_by=1,
        )

        db.add(invoice)
        db.flush()

        return invoice

    def cleanup(self, db):
        invoices = db.scalars(
            select(InsuranceInvoice)
        ).all()

        for invoice in invoices:
            db.delete(invoice)

        customers = db.scalars(
            select(InsuranceCustomer)
        ).all()

        for customer in customers:
            db.delete(customer)

        db.commit()

    # ---------------------------------------------------------
    # CUSTOMER + INVOICE SUMMARY
    # ---------------------------------------------------------

    def test_customer_and_invoice_are_returned(self):

        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = self.create_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="ABC-123",
            )

            db.commit()

            result = get_insurance_customers(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                len(result["customers"]),
                1,
            )

            returned = result["customers"][0]

            self.assertEqual(
                returned["customer_id"],
                customer.id,
            )

            self.assertEqual(
                returned["name"],
                "Ahmed Ali",
            )

            self.assertEqual(
                returned["phone_number"],
                "55555555",
            )

            self.assertEqual(
                returned["invoice_id"],
                invoice.id,
            )

            self.assertEqual(
                returned["plate_number"],
                "ABC-123",
            )

            self.assertEqual(
                returned["payment_status"],
                PaymentStatus.UNPAID.value,
            )

            self.assertEqual(
                returned["invoice_date"],
                invoice.created_at,
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # THIS MONTH
    # ---------------------------------------------------------

    def test_this_month_returns_current_month_invoice(self):

        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = self.create_invoice(
                db=db,
                customer_id=customer.id,
            )

            db.commit()

            result = get_insurance_customers_this_month(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["customers"][0]["invoice_id"],
                invoice.id,
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # DATE RANGE
    # ---------------------------------------------------------

    def test_date_range_returns_matching_invoices(self):

        with Session(engine) as db:

            customer = self.create_customer(db)

            july_invoice = self.create_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="JULY-123",
            )

            august_invoice = self.create_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="AUG-123",
            )

            july_invoice.created_at = datetime(
                2026,
                7,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            )

            august_invoice.created_at = datetime(
                2026,
                8,
                15,
                10,
                0,
                tzinfo=timezone.utc,
            )

            db.commit()

            result = get_insurance_customers(
                db=db,
                start_date=date(2026, 7, 1),
                end_date=date(2026, 7, 31),
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["customers"][0]["invoice_id"],
                july_invoice.id,
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # END DATE IS INCLUSIVE
    # ---------------------------------------------------------

    def test_end_date_includes_entire_day(self):

        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice = self.create_invoice(
                db=db,
                customer_id=customer.id,
            )

            invoice.created_at = datetime(
                2026,
                8,
                19,
                23,
                59,
                59,
                tzinfo=timezone.utc,
            )

            db.commit()

            result = get_insurance_customers(
                db=db,
                start_date=date(2026, 8, 19),
                end_date=date(2026, 8, 19),
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["customers"][0]["invoice_id"],
                invoice.id,
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # MULTIPLE INVOICES
    # ---------------------------------------------------------

    def test_multiple_invoices_are_returned(self):

        with Session(engine) as db:

            customer = self.create_customer(db)

            invoice1 = self.create_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="CAR-111",
            )

            invoice2 = self.create_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="CAR-222",
            )

            db.commit()

            result = get_insurance_customers(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                2,
            )

            returned_invoice_ids = {
                row["invoice_id"]
                for row in result["customers"]
            }

            self.assertIn(
                invoice1.id,
                returned_invoice_ids,
            )

            self.assertIn(
                invoice2.id,
                returned_invoice_ids,
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # INACTIVE CUSTOMER IS EXCLUDED
    # ---------------------------------------------------------

    def test_inactive_customer_is_excluded(self):

        with Session(engine) as db:

            active_customer = self.create_customer(
                db,
                name="Active Customer",
            )

            inactive_customer = self.create_customer(
                db,
                name="Inactive Customer",
            )

            self.create_invoice(
                db=db,
                customer_id=active_customer.id,
            )

            self.create_invoice(
                db=db,
                customer_id=inactive_customer.id,
            )

            inactive_customer.is_active = False

            db.commit()

            result = get_insurance_customers(
                db=db,
            )

            self.assertEqual(
                result["pagination"]["total"],
                1,
            )

            self.assertEqual(
                result["customers"][0]["customer_id"],
                active_customer.id,
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    def test_pagination_works(self):

        with Session(engine) as db:

            customer = self.create_customer(db)

            for index in range(15):

                self.create_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number=f"CAR-{index}",
                )

            db.commit()

            result = get_insurance_customers(
                db=db,
                limit=10,
                offset=5,
            )

            self.assertEqual(
                len(result["customers"]),
                10,
            )

            self.assertEqual(
                result["pagination"]["total"],
                15,
            )

            self.assertEqual(
                result["pagination"]["limit"],
                10,
            )

            self.assertEqual(
                result["pagination"]["offset"],
                5,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # REMAINING RECORDS
    # ---------------------------------------------------------

    def test_remaining_records_are_returned(self):

        with Session(engine) as db:

            customer = self.create_customer(db)

            for index in range(16):

                self.create_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number=f"CAR-{index}",
                )

            db.commit()

            result = get_insurance_customers(
                db=db,
                limit=10,
                offset=10,
            )

            self.assertEqual(
                len(result["customers"]),
                6,
            )

            self.assertEqual(
                result["pagination"]["total"],
                16,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # OFFSET BEYOND RECORDS
    # ---------------------------------------------------------

    def test_offset_beyond_records_returns_empty_list(self):

        with Session(engine) as db:

            customer = self.create_customer(db)

            for index in range(5):

                self.create_invoice(
                    db=db,
                    customer_id=customer.id,
                )

            db.commit()

            result = get_insurance_customers(
                db=db,
                limit=10,
                offset=10,
            )

            self.assertEqual(
                len(result["customers"]),
                0,
            )

            self.assertEqual(
                result["pagination"]["total"],
                5,
            )

            self.assertFalse(
                result["pagination"]["has_more"]
            )

            self.cleanup(db)

    # ---------------------------------------------------------
    # ZERO LIMIT
    # ---------------------------------------------------------

    def test_zero_limit_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Limit must be greater than zero",
            ):
                get_insurance_customers(
                    db=db,
                    limit=0,
                )

    # ---------------------------------------------------------
    # NEGATIVE OFFSET
    # ---------------------------------------------------------

    def test_negative_offset_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Offset cannot be negative",
            ):
                get_insurance_customers(
                    db=db,
                    offset=-1,
                )

    # ---------------------------------------------------------
    # INVALID DATE RANGE
    # ---------------------------------------------------------

    def test_invalid_date_range_is_rejected(self):

        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Start date cannot be after end date",
            ):
                get_insurance_customers(
                    db=db,
                    start_date=date(2026, 8, 20),
                    end_date=date(2026, 8, 1),
                )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )