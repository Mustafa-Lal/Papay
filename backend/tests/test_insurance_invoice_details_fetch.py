import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine

from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import PaymentStatus

from app.services.insurance_customer import (
    create_insurance_customer,
)
from app.services.insurance_invoice import (
    create_insurance_invoice,
)
from app.services.insurance_item import (
    create_insurance_item,
)
from app.services.insurance_invoice_details_fetch import (
    get_insurance_customer_details,
)

from app.models.insurance_image import (
    InsuranceImage,
    InsuranceImageType,
)

class InsuranceCustomerDetailsTests(unittest.TestCase):

    def create_test_customer(self, db):

        customer = create_insurance_customer(
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

        invoice = create_insurance_invoice(
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

        item = create_insurance_item(
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

            result = get_insurance_customer_details(
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

            result = get_insurance_customer_details(
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
                select(InsuranceInvoice).where(
                    InsuranceInvoice.customer_id
                    == customer.id
                )
            ).all()

            for invoice in invoices:

                items = db.scalars(
                    select(InsuranceItem).where(
                        InsuranceItem.invoice_id
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

            result = get_insurance_customer_details(
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

            result = get_insurance_customer_details(
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
                "Insurance customer not found",
            ):
                get_insurance_customer_details(
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
                "Insurance customer not found",
            ):
                get_insurance_customer_details(
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

            result = get_insurance_customer_details(
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
                select(InsuranceInvoice).where(
                    InsuranceInvoice.customer_id
                    == customer.id
                )
            ).all()

            for invoice in invoices:
                db.delete(invoice)

            db.delete(customer)
            db.commit()

    # ---------------------------------------------------------
    # INVALID LIMIT
    # ---------------------------------------------------------

    def test_zero_limit_is_rejected(self):

        with Session(engine) as db:

            customer = self.create_test_customer(db)

            with self.assertRaisesRegex(
                ValueError,
                "Limit must be greater than zero",
            ):
                get_insurance_customer_details(
                    db=db,
                    customer_id=customer.id,
                    limit=0,
                )

            db.rollback()

    # ---------------------------------------------------------
    # INVALID OFFSET
    # ---------------------------------------------------------

    def test_negative_offset_is_rejected(self):

        with Session(engine) as db:

            customer = self.create_test_customer(db)

            with self.assertRaisesRegex(
                ValueError,
                "Offset cannot be negative",
            ):
                get_insurance_customer_details(
                    db=db,
                    customer_id=customer.id,
                    offset=-1,
                )

            db.rollback()



# ---------------------------------------------------------
# INVOICE INCLUDES IMAGES
# ---------------------------------------------------------

def test_invoice_details_include_images(self):

    with Session(engine) as db:

        customer = self.create_test_customer(db)

        invoice = self.create_test_invoice(
            db=db,
            customer_id=customer.id,
            plate_number="IMG-123",
        )

        item = self.create_test_item(
            db=db,
            invoice_id=invoice.id,
            description="Body Repair",
            quantity="1.00",
            unit_price="500.00",
            commission="50.00",
        )

        before_image = InsuranceImage(
            invoice_id=invoice.id,
            image_type=InsuranceImageType.BEFORE,
            file_path=(
                "data/uploads/insurance/"
                f"{invoice.id}/before/before.jpg"
            ),
        )

        after_image = InsuranceImage(
            invoice_id=invoice.id,
            image_type=InsuranceImageType.AFTER,
            file_path=(
                "data/uploads/insurance/"
                f"{invoice.id}/after/after.jpg"
            ),
        )

        db.add(before_image)
        db.add(after_image)

        db.commit()

        result = get_insurance_customer_details(
            db=db,
            customer_id=customer.id,
        )

        # --------------------------------------------------
        # Verify invoice
        # --------------------------------------------------

        self.assertEqual(
            len(result["invoices"]),
            1,
        )

        returned_invoice = result["invoices"][0]

        self.assertEqual(
            returned_invoice["id"],
            invoice.id,
        )

        # --------------------------------------------------
        # Verify items
        # --------------------------------------------------

        self.assertEqual(
            len(returned_invoice["items"]),
            1,
        )

        self.assertEqual(
            returned_invoice["items"][0]["id"],
            item.id,
        )

        # --------------------------------------------------
        # Verify images
        # --------------------------------------------------

        self.assertEqual(
            len(returned_invoice["images"]),
            2,
        )

        images = returned_invoice["images"]

        before = next(
            image
            for image in images
            if image["type"] == "BEFORE"
        )

        after = next(
            image
            for image in images
            if image["type"] == "AFTER"
        )

        self.assertEqual(
            before["id"],
            before_image.id,
        )

        self.assertEqual(
            before["type"],
            "BEFORE",
        )

        self.assertEqual(
            before["file_path"],
            before_image.file_path,
        )

        self.assertEqual(
            after["id"],
            after_image.id,
        )

        self.assertEqual(
            after["type"],
            "AFTER",
        )

        self.assertEqual(
            after["file_path"],
            after_image.file_path,
        )

        # --------------------------------------------------
        # Clean up
        # --------------------------------------------------

        db.delete(before_image)
        db.delete(after_image)
        db.delete(item)
        db.delete(invoice)
        db.delete(customer)

        db.commit()

        
if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )