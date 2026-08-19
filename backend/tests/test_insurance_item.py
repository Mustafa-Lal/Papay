"""
Tests for the insurance item service.

Tests both valid and invalid item creation.
"""

import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem
from app.services.insurance_invoice import (
    create_insurance_invoice,
)
from app.services.insurance_item import (
    create_insurance_item,
)


class InsuranceItemTests(unittest.TestCase):

    def create_invoice(self, db):
        customer = InsuranceCustomer(
            customer_name="Test Customer"
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return create_insurance_invoice(
            db=db,
            customer_id=customer.id,
            plate_number="12345",
            created_by=1,
        )

    def test_create_item_successfully(self):
        """A valid item should be created."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            item = create_insurance_item(
                db=db,
                invoice_id=invoice.id,
                description="Brake Pad",
                quantity=Decimal("2"),
                unit_price=Decimal("100.00"),
            )

            self.assertIsNotNone(item.id)
            self.assertEqual(
                item.invoice_id,
                invoice.id,
            )
            self.assertEqual(
                item.description,
                "Brake Pad",
            )
            self.assertEqual(
                item.quantity,
                Decimal("2"),
            )
            self.assertEqual(
                item.unit_price,
                Decimal("100.00"),
            )

    def test_commission_defaults_to_zero(self):
        """Commission should default to 0.00."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            item = create_insurance_item(
                db=db,
                invoice_id=invoice.id,
                description="Oil Filter",
                quantity=Decimal("1"),
                unit_price=Decimal("50.00"),
            )

            self.assertEqual(
                item.commission,
                Decimal("0.00"),
            )

    def test_commission_can_be_provided(self):
        """A valid commission should be stored."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            item = create_insurance_item(
                db=db,
                invoice_id=invoice.id,
                description="Bumper",
                quantity=Decimal("1"),
                unit_price=Decimal("500.00"),
                commission=Decimal("50.00"),
            )

            self.assertEqual(
                item.commission,
                Decimal("50.00"),
            )

    def test_multiple_items_can_belong_to_same_invoice(self):
        """An invoice can contain multiple items."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            item_1 = create_insurance_item(
                db=db,
                invoice_id=invoice.id,
                description="Brake Pad",
                quantity=Decimal("2"),
                unit_price=Decimal("100.00"),
            )

            item_2 = create_insurance_item(
                db=db,
                invoice_id=invoice.id,
                description="Oil Filter",
                quantity=Decimal("1"),
                unit_price=Decimal("50.00"),
            )

            self.assertNotEqual(
                item_1.id,
                item_2.id,
            )

            items = db.scalars(
                select(InsuranceItem).where(
                    InsuranceItem.invoice_id == invoice.id
                )
            ).all()

            self.assertEqual(
                len(items),
                2,
            )

    def test_nonexistent_invoice_is_rejected(self):
        """An item cannot belong to a nonexistent invoice."""

        with Session(engine) as db:
            with self.assertRaises(ValueError):
                create_insurance_item(
                    db=db,
                    invoice_id=999999,
                    description="Brake Pad",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                )

    def test_empty_description_is_rejected(self):
        """Description is required."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):
                create_insurance_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                )

    def test_whitespace_description_is_rejected(self):
        """Whitespace-only description is invalid."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):
                create_insurance_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="   ",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                )

    def test_zero_quantity_is_rejected(self):
        """Quantity must be greater than zero."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):
                create_insurance_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="Brake Pad",
                    quantity=Decimal("0"),
                    unit_price=Decimal("100.00"),
                )

    def test_negative_quantity_is_rejected(self):
        """Negative quantity is invalid."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):
                create_insurance_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="Brake Pad",
                    quantity=Decimal("-1"),
                    unit_price=Decimal("100.00"),
                )

    def test_negative_unit_price_is_rejected(self):
        """Unit price cannot be negative."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):
                create_insurance_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="Brake Pad",
                    quantity=Decimal("1"),
                    unit_price=Decimal("-100.00"),
                )

    def test_negative_commission_is_rejected(self):
        """Commission cannot be negative."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):
                create_insurance_item(
                    db=db,
                    invoice_id=invoice.id,
                    description="Brake Pad",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                    commission=Decimal("-10.00"),
                )

    def test_description_is_trimmed(self):
        """Leading and trailing whitespace is removed."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            item = create_insurance_item(
                db=db,
                invoice_id=invoice.id,
                description="  Brake Pad  ",
                quantity=Decimal("1"),
                unit_price=Decimal("100.00"),
            )

            self.assertEqual(
                item.description,
                "Brake Pad",
            )

    def test_item_is_saved_to_database(self):
        """The item must persist in the database."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            item = create_insurance_item(
                db=db,
                invoice_id=invoice.id,
                description="Test Part",
                quantity=Decimal("1"),
                unit_price=Decimal("25.00"),
            )

            saved_item = db.scalar(
                select(InsuranceItem).where(
                    InsuranceItem.id == item.id
                )
            )

            self.assertIsNotNone(saved_item)

            self.assertEqual(
                saved_item.description,
                "Test Part",
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )