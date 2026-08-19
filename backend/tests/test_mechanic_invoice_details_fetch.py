import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine

from app.models.mechanic_customer import MechanicCustomer
from app.models.mechanic_invoice import MechanicInvoice
from app.models.mechanic_item import MechanicItem
from app.models.insurance_invoice import PaymentStatus

from app.services.mechanic_customer import (
    create_mechanic_customer,
)
from app.services.mechanic_invoice import (
    create_mechanic_invoice,
)
from app.services.mechanic_item import (
    create_mechanic_item,
)
from app.services.mechanic_invoice_details_fetch import (
    get_mechanic_customer_details,
)


class MechanicCustomerDetailsTests(unittest.TestCase):

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

    def create_test_item(
        self,
        db,
        invoice_id,
        description,
        quantity,
        unit_price,
        commission,
    ):
        item = create_mechanic_item(
            db=db,
            invoice_id=invoice_id,
            description=description,
            quantity=Decimal(quantity),
            unit_price=Decimal(unit_price),
            commission=Decimal(commission),
        )

        db.flush()

        return item

    # ---------------------------------------------------------
    # CUSTOMER + INVOICE + ITEMS
    # ---------------------------------------------------------

    def test_customer_details_include_invoices_and_items(self):

        with Session(engine) as db:

            customer = self.create_test_customer(db)

            invoice = self.create_test_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="ABC-123",
            )

            item1 = self.create_test_item(
                db=db,
                invoice_id=invoice.id,
                description="Oil Filter",
                quantity="1.00",
                unit_price="50.00",
                commission="5.00",
            )

            item2 = self.create_test_item(
                db=db,
                invoice_id=invoice.id,
                description="Brake Pad",
                quantity="2.00",
                unit_price="100.00",
                commission="10.00",
            )

            db.commit()

            result = get_mechanic_customer_details(
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

            self.assertEqual(
                result["customer"]["qid"],
                "12345678901",
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
                returned_invoice["labor_charges"],
                Decimal("100.00"),
            )

            self.assertEqual(
                returned_invoice["payment_status"],
                PaymentStatus.UNPAID.value,
            )

            self.assertEqual(
                returned_invoice["invoice_date"],
                invoice.created_at,
            )

            # Items
            self.assertEqual(
                len(returned_invoice["items"]),
                2,
            )

            returned_item1 = returned_invoice["items"][0]

            self.assertEqual(
                returned_item1["id"],
                item1.id,
            )

            self.assertEqual(
                returned_item1["description"],
                "Oil Filter",
            )

            self.assertEqual(
                returned_item1["quantity"],
                Decimal("1.00"),
            )

            self.assertEqual(
                returned_item1["unit_price"],
                Decimal("50.00"),
            )

            self.assertEqual(
                returned_item1["commission"],
                Decimal("5.00"),
            )

            # Clean up
            db.delete(item1)
            db.delete(item2)
            db.delete(invoice)
            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # MULTIPLE INVOICES
    # ---------------------------------------------------------

    def test_customer_returns_multiple_invoices(self):

        with Session(engine) as db:

            customer = self.create_test_customer(db)

            invoice1 = self.create_test_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="CAR-111",
            )

            invoice2 = self.create_test_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="CAR-222",
            )

            self.create_test_item(
                db=db,
                invoice_id=invoice1.id,
                description="Oil Filter",
                quantity="1.00",
                unit_price="50.00",
                commission="5.00",
            )

            self.create_test_item(
                db=db,
                invoice_id=invoice2.id,
                description="Brake Pad",
                quantity="2.00",
                unit_price="100.00",
                commission="10.00",
            )

            db.commit()

            result = get_mechanic_customer_details(
                db=db,
                customer_id=customer.id,
            )

            self.assertEqual(
                len(result["invoices"]),
                2,
            )

            returned_invoice_ids = {
                invoice["id"]
                for invoice in result["invoices"]
            }

            self.assertIn(
                invoice1.id,
                returned_invoice_ids,
            )

            self.assertIn(
                invoice2.id,
                returned_invoice_ids,
            )

            # Clean up
            invoices = db.scalars(
                select(MechanicInvoice).where(
                    MechanicInvoice.customer_id
                    == customer.id
                )
            ).all()

            for invoice in invoices:

                items = db.scalars(
                    select(MechanicItem).where(
                        MechanicItem.invoice_id
                        == invoice.id
                    )
                ).all()

                for item in items:
                    db.delete(item)

                db.delete(invoice)

            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # INVOICE WITHOUT ITEMS
    # ---------------------------------------------------------

    def test_invoice_without_items_returns_empty_items(self):

        with Session(engine) as db:

            customer = self.create_test_customer(db)

            invoice = self.create_test_invoice(
                db=db,
                customer_id=customer.id,
                plate_number="NO-ITEMS",
            )

            db.commit()

            result = get_mechanic_customer_details(
                db=db,
                customer_id=customer.id,
            )

            self.assertEqual(
                len(result["invoices"]),
                1,
            )

            self.assertEqual(
                result["invoices"][0]["id"],
                invoice.id,
            )

            self.assertEqual(
                result["invoices"][0]["items"],
                [],
            )

            # Clean up
            db.delete(invoice)
            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # CUSTOMER WITH NO INVOICES
    # ---------------------------------------------------------

    def test_customer_with_no_invoices_returns_empty_list(self):

        with Session(engine) as db:

            customer = self.create_test_customer(db)

            db.commit()

            result = get_mechanic_customer_details(
                db=db,
                customer_id=customer.id,
            )

            self.assertEqual(
                result["customer"]["id"],
                customer.id,
            )

            self.assertEqual(
                result["invoices"],
                [],
            )

            # Clean up
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
                get_mechanic_customer_details(
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
                get_mechanic_customer_details(
                    db=db,
                    customer_id=999999,
                )

    # ---------------------------------------------------------
    # PAGINATION
    # ---------------------------------------------------------

    def test_invoice_pagination_works(self):

        with Session(engine) as db:

            customer = self.create_test_customer(db)

            for index in range(15):

                self.create_test_invoice(
                    db=db,
                    customer_id=customer.id,
                    plate_number=f"CAR-{index}",
                )

            db.commit()

            result = get_mechanic_customer_details(
                db=db,
                customer_id=customer.id,
                limit=10,
                offset=10,
            )

            # Only 5 invoices remain.
            self.assertEqual(
                len(result["invoices"]),
                5,
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
    # ZERO LIMIT
    # ---------------------------------------------------------

    def test_zero_limit_is_rejected(self):

        with Session(engine) as db:

            customer = self.create_test_customer(db)

            with self.assertRaisesRegex(
                ValueError,
                "Limit must be greater than zero",
            ):
                get_mechanic_customer_details(
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
                get_mechanic_customer_details(
                    db=db,
                    customer_id=customer.id,
                    offset=-1,
                )

            db.rollback()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )