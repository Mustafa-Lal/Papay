import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_invoice import InsuranceInvoice
from app.models.insurance_item import InsuranceItem

from app.services.insurance_customer import (
    create_insurance_customer,
)
from app.services.insurance_invoice import (
    create_insurance_invoice,
)
from app.services.insurance_item import (
    create_insurance_item,
)
from app.services.insurance_item_update import (
    update_insurance_item,
)


class InsuranceItemUpdateTests(unittest.TestCase):

    def create_test_item(self, db):
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
            plate_number="ABC-123",
            labor_charges=Decimal("100.00"),
            created_by=1,
        )

        db.flush()

        item = create_insurance_item(
            db=db,
            invoice_id=invoice.id,
            description="Original Item",
            quantity=Decimal("10.00"),
            unit_price=Decimal("50.00"),
            commission=Decimal("5.00"),
        )

        db.flush()

        return item

    # ---------------------------------------------------------
    # DESCRIPTION
    # ---------------------------------------------------------

    def test_update_description(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                description="Updated Item",
            )

            self.assertEqual(
                item.description,
                "Updated Item",
            )

            self.assertEqual(
                item.quantity,
                Decimal("10.00"),
            )

            self.assertEqual(
                item.unit_price,
                Decimal("50.00"),
            )

            self.assertEqual(
                item.commission,
                Decimal("5.00"),
            )

            db.rollback()

    def test_updated_description_is_trimmed(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                description="  Updated Item  ",
            )

            self.assertEqual(
                item.description,
                "Updated Item",
            )

            db.rollback()

    def test_empty_description_is_rejected(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            with self.assertRaisesRegex(
                ValueError,
                "Item description cannot be empty",
            ):
                update_insurance_item(
                    db=db,
                    item_id=item.id,
                    description="",
                )

            self.assertEqual(
                item.description,
                "Original Item",
            )

            db.rollback()

    def test_whitespace_description_is_rejected(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            with self.assertRaisesRegex(
                ValueError,
                "Item description cannot be empty",
            ):
                update_insurance_item(
                    db=db,
                    item_id=item.id,
                    description="   ",
                )

            self.assertEqual(
                item.description,
                "Original Item",
            )

            db.rollback()

    # ---------------------------------------------------------
    # QUANTITY
    # ---------------------------------------------------------

    def test_update_quantity(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                quantity=Decimal("25.00"),
            )

            self.assertEqual(
                item.quantity,
                Decimal("25.00"),
            )

            self.assertEqual(
                item.unit_price,
                Decimal("50.00"),
            )

            db.rollback()

    def test_zero_quantity_is_rejected(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            with self.assertRaisesRegex(
                ValueError,
                "quantity must be greater than zero",
            ):
                update_insurance_item(
                    db=db,
                    item_id=item.id,
                    quantity=Decimal("0.00"),
                )

            self.assertEqual(
                item.quantity,
                Decimal("10.00"),
            )

            db.rollback()

    def test_negative_quantity_is_rejected(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            with self.assertRaisesRegex(
                ValueError,
                "quantity must be greater than zero",
            ):
                update_insurance_item(
                    db=db,
                    item_id=item.id,
                    quantity=Decimal("-5.00"),
                )

            self.assertEqual(
                item.quantity,
                Decimal("10.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # UNIT PRICE
    # ---------------------------------------------------------

    def test_update_unit_price(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                unit_price=Decimal("75.00"),
            )

            self.assertEqual(
                item.unit_price,
                Decimal("75.00"),
            )

            self.assertEqual(
                item.quantity,
                Decimal("10.00"),
            )

            db.rollback()

    def test_zero_unit_price_is_allowed(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                unit_price=Decimal("0.00"),
            )

            self.assertEqual(
                item.unit_price,
                Decimal("0.00"),
            )

            db.rollback()

    def test_negative_unit_price_is_rejected(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            with self.assertRaisesRegex(
                ValueError,
                "unit price cannot be negative",
            ):
                update_insurance_item(
                    db=db,
                    item_id=item.id,
                    unit_price=Decimal("-10.00"),
                )

            self.assertEqual(
                item.unit_price,
                Decimal("50.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # COMMISSION
    # ---------------------------------------------------------

    def test_update_commission(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                commission=Decimal("10.00"),
            )

            self.assertEqual(
                item.commission,
                Decimal("10.00"),
            )

            db.rollback()

    def test_zero_commission_is_allowed(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                commission=Decimal("0.00"),
            )

            self.assertEqual(
                item.commission,
                Decimal("0.00"),
            )

            db.rollback()

    def test_negative_commission_is_rejected(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            with self.assertRaisesRegex(
                ValueError,
                "commission cannot be negative",
            ):
                update_insurance_item(
                    db=db,
                    item_id=item.id,
                    commission=Decimal("-5.00"),
                )

            self.assertEqual(
                item.commission,
                Decimal("5.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # ALL FIELDS
    # ---------------------------------------------------------

    def test_update_all_item_fields(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                description="New Item",
                quantity=Decimal("20.00"),
                unit_price=Decimal("80.00"),
                commission=Decimal("12.00"),
            )

            self.assertEqual(
                item.description,
                "New Item",
            )

            self.assertEqual(
                item.quantity,
                Decimal("20.00"),
            )

            self.assertEqual(
                item.unit_price,
                Decimal("80.00"),
            )

            self.assertEqual(
                item.commission,
                Decimal("12.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # PARTIAL UPDATE
    # ---------------------------------------------------------

    def test_partial_update_does_not_change_other_fields(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            update_insurance_item(
                db=db,
                item_id=item.id,
                quantity=Decimal("30.00"),
            )

            self.assertEqual(
                item.description,
                "Original Item",
            )

            self.assertEqual(
                item.quantity,
                Decimal("30.00"),
            )

            self.assertEqual(
                item.unit_price,
                Decimal("50.00"),
            )

            self.assertEqual(
                item.commission,
                Decimal("5.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_item_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Insurance item not found",
            ):
                update_insurance_item(
                    db=db,
                    item_id=999999,
                    description="New Item",
                )

            db.rollback()

    # ---------------------------------------------------------
    # INVOICE RELATIONSHIP DOES NOT CHANGE
    # ---------------------------------------------------------

    def test_update_does_not_change_invoice(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            original_invoice_id = item.invoice_id

            update_insurance_item(
                db=db,
                item_id=item.id,
                description="Updated Item",
                quantity=20,
                unit_price=100,
                commission=10,
            )

            self.assertEqual(
                item.invoice_id,
                original_invoice_id,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            item_id = item.id

            db.commit()

            update_insurance_item(
                db=db,
                item_id=item_id,
                description="Persisted Item",
                quantity=Decimal("40.00"),
                unit_price=Decimal("90.00"),
                commission=Decimal("15.00"),
            )

            db.commit()

            saved_item = db.scalar(
                select(InsuranceItem).where(
                    InsuranceItem.id == item_id
                )
            )

            self.assertIsNotNone(
                saved_item
            )

            self.assertEqual(
                saved_item.description,
                "Persisted Item",
            )

            self.assertEqual(
                saved_item.quantity,
                Decimal("40.00"),
            )

            self.assertEqual(
                saved_item.unit_price,
                Decimal("90.00"),
            )

            self.assertEqual(
                saved_item.commission,
                Decimal("15.00"),
            )

            # Clean up.
            invoice = db.scalar(
                select(InsuranceInvoice).where(
                    InsuranceInvoice.id
                    == saved_item.invoice_id
                )
            )

            customer = None

            if invoice is not None:
                customer = db.scalar(
                    select(InsuranceCustomer).where(
                        InsuranceCustomer.id
                        == invoice.customer_id
                    )
                )

            db.delete(saved_item)

            if invoice is not None:
                db.delete(invoice)

            if customer is not None:
                db.delete(customer)

            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            item = self.create_test_item(db)

            db.commit()

            item_id = item.id

            update_insurance_item(
                db=db,
                item_id=item_id,
                description="Temporary Item",
                quantity=Decimal("99.00"),
                unit_price=Decimal("999.00"),
                commission=Decimal("99.00"),
            )

            db.rollback()

            saved_item = db.scalar(
                select(InsuranceItem).where(
                    InsuranceItem.id == item_id
                )
            )

            self.assertIsNotNone(
                saved_item
            )

            self.assertEqual(
                saved_item.description,
                "Original Item",
            )

            self.assertEqual(
                saved_item.quantity,
                Decimal("10.00"),
            )

            self.assertEqual(
                saved_item.unit_price,
                Decimal("50.00"),
            )

            self.assertEqual(
                saved_item.commission,
                Decimal("5.00"),
            )

            # Clean up.
            invoice = db.scalar(
                select(InsuranceInvoice).where(
                    InsuranceInvoice.id
                    == saved_item.invoice_id
                )
            )

            customer = None

            if invoice is not None:
                customer = db.scalar(
                    select(InsuranceCustomer).where(
                        InsuranceCustomer.id
                        == invoice.customer_id
                    )
                )

            db.delete(saved_item)

            if invoice is not None:
                db.delete(invoice)

            if customer is not None:
                db.delete(customer)

            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )