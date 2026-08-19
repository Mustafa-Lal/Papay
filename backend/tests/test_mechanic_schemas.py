import unittest
from datetime import datetime
from decimal import Decimal

from pydantic import ValidationError

from app.models.insurance_invoice import PaymentStatus
from app.schemas.mechanic_invoice import (
    MechanicCustomerCreate,
    MechanicCustomerResponse,
    MechanicCustomerUpdate,
    MechanicInvoiceCreate,
    MechanicInvoiceResponse,
    MechanicInvoiceSummaryListResponse,
    MechanicInvoiceSummaryResponse,
    MechanicInvoiceUpdate,
    MechanicItemCreate,
    MechanicItemResponse,
    MechanicItemUpdate,
)
from app.schemas.product import PaginationResponse


class MechanicSchemaTests(unittest.TestCase):

    # ==========================================================
    # CUSTOMER CREATE
    # ==========================================================

    def test_valid_customer_create(self):

        customer = MechanicCustomerCreate(
            customer_name="Ahmed Ali",
            phone_number="55555555",
            qid="12345678901",
        )

        self.assertEqual(
            customer.customer_name,
            "Ahmed Ali",
        )

        self.assertEqual(
            customer.phone_number,
            "55555555",
        )

        self.assertEqual(
            customer.qid,
            "12345678901",
        )

    # ==========================================================
    # EMPTY CUSTOMER STRINGS
    # ==========================================================

    def test_empty_customer_strings_become_none(self):

        customer = MechanicCustomerCreate(
            customer_name="   ",
            phone_number="",
            qid="   ",
        )

        self.assertIsNone(
            customer.customer_name
        )

        self.assertIsNone(
            customer.phone_number
        )

        self.assertIsNone(
            customer.qid
        )

    # ==========================================================
    # ITEM CREATE
    # ==========================================================

    def test_valid_item_create(self):

        item = MechanicItemCreate(
            description="Engine Oil",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50.00"),
            commission=Decimal("5.00"),
        )

        self.assertEqual(
            item.description,
            "Engine Oil",
        )

        self.assertEqual(
            item.quantity,
            Decimal("2.00"),
        )

        self.assertEqual(
            item.unit_price,
            Decimal("50.00"),
        )

        self.assertEqual(
            item.commission,
            Decimal("5.00"),
        )

    # ==========================================================
    # ITEM DESCRIPTION
    # ==========================================================

    def test_empty_item_description_is_rejected(self):

        with self.assertRaises(ValidationError):

            MechanicItemCreate(
                description="   ",
                quantity=Decimal("1.00"),
                unit_price=Decimal("10.00"),
            )

    # ==========================================================
    # ITEM QUANTITY
    # ==========================================================

    def test_zero_item_quantity_is_rejected(self):

        with self.assertRaises(ValidationError):

            MechanicItemCreate(
                description="Engine Oil",
                quantity=Decimal("0.00"),
                unit_price=Decimal("10.00"),
            )

    def test_negative_item_quantity_is_rejected(self):

        with self.assertRaises(ValidationError):

            MechanicItemCreate(
                description="Engine Oil",
                quantity=Decimal("-1.00"),
                unit_price=Decimal("10.00"),
            )

    # ==========================================================
    # ITEM PRICE
    # ==========================================================

    def test_negative_item_price_is_rejected(self):

        with self.assertRaises(ValidationError):

            MechanicItemCreate(
                description="Engine Oil",
                quantity=Decimal("1.00"),
                unit_price=Decimal("-10.00"),
            )

    # ==========================================================
    # ITEM COMMISSION
    # ==========================================================

    def test_negative_item_commission_is_rejected(self):

        with self.assertRaises(ValidationError):

            MechanicItemCreate(
                description="Engine Oil",
                quantity=Decimal("1.00"),
                unit_price=Decimal("10.00"),
                commission=Decimal("-5.00"),
            )

    # ==========================================================
    # INVOICE CREATE
    # ==========================================================

    def test_valid_invoice_create(self):

        invoice = MechanicInvoiceCreate(
            customer=MechanicCustomerCreate(
                customer_name="Ahmed Ali",
                phone_number="55555555",
                qid="12345678901",
            ),
            plate_number="ABC-123",
            labor_charges=Decimal("100.00"),
            payment_status=PaymentStatus.UNPAID,
            items=[
                MechanicItemCreate(
                    description="Engine Oil",
                    quantity=Decimal("2.00"),
                    unit_price=Decimal("50.00"),
                    commission=Decimal("5.00"),
                )
            ],
        )

        self.assertEqual(
            invoice.plate_number,
            "ABC-123",
        )

        self.assertEqual(
            invoice.labor_charges,
            Decimal("100.00"),
        )

        self.assertEqual(
            invoice.payment_status,
            PaymentStatus.UNPAID,
        )

        self.assertEqual(
            len(invoice.items),
            1,
        )

    # ==========================================================
    # PLATE NUMBER
    # ==========================================================

    def test_empty_plate_number_is_rejected(self):

        with self.assertRaises(ValidationError):

            MechanicInvoiceCreate(
                customer=MechanicCustomerCreate(
                    customer_name="Ahmed",
                ),
                plate_number="   ",
                items=[
                    MechanicItemCreate(
                        description="Oil",
                        quantity=Decimal("1.00"),
                        unit_price=Decimal("10.00"),
                    )
                ],
            )

    # ==========================================================
    # LABOR CHARGES
    # ==========================================================

    def test_negative_labor_charges_are_rejected(self):

        with self.assertRaises(ValidationError):

            MechanicInvoiceCreate(
                customer=MechanicCustomerCreate(
                    customer_name="Ahmed",
                ),
                plate_number="ABC-123",
                labor_charges=Decimal("-10.00"),
                items=[
                    MechanicItemCreate(
                        description="Oil",
                        quantity=Decimal("1.00"),
                        unit_price=Decimal("10.00"),
                    )
                ],
            )

    # ==========================================================
    # INVOICE ITEMS
    # ==========================================================

    def test_empty_invoice_items_are_rejected(self):

        with self.assertRaises(ValidationError):

            MechanicInvoiceCreate(
                customer=MechanicCustomerCreate(
                    customer_name="Ahmed",
                ),
                plate_number="ABC-123",
                items=[],
            )

    # ==========================================================
    # CUSTOMER UPDATE
    # ==========================================================

    def test_valid_customer_update(self):

        customer = MechanicCustomerUpdate(
            customer_name="Updated Name",
            phone_number="99999999",
        )

        self.assertEqual(
            customer.customer_name,
            "Updated Name",
        )

        self.assertEqual(
            customer.phone_number,
            "99999999",
        )

        self.assertIsNone(
            customer.qid
        )

    # ==========================================================
    # ITEM UPDATE
    # ==========================================================

    def test_valid_item_update(self):

        item = MechanicItemUpdate(
            unit_price=Decimal("75.00"),
        )

        self.assertIsNone(
            item.description
        )

        self.assertIsNone(
            item.quantity
        )

        self.assertEqual(
            item.unit_price,
            Decimal("75.00"),
        )

    # ==========================================================
    # INVOICE UPDATE
    # ==========================================================

    def test_valid_invoice_update(self):

        invoice = MechanicInvoiceUpdate(
            plate_number="XYZ-999",
            labor_charges=Decimal("150.00"),
            payment_status=PaymentStatus.PAID,
        )

        self.assertEqual(
            invoice.plate_number,
            "XYZ-999",
        )

        self.assertEqual(
            invoice.labor_charges,
            Decimal("150.00"),
        )

        self.assertEqual(
            invoice.payment_status,
            PaymentStatus.PAID,
        )

    # ==========================================================
    # EMPTY UPDATE
    # ==========================================================

    def test_empty_updates_are_allowed(self):

        customer = MechanicCustomerUpdate()
        item = MechanicItemUpdate()
        invoice = MechanicInvoiceUpdate()

        self.assertIsNone(
            customer.customer_name
        )

        self.assertIsNone(
            item.description
        )

        self.assertIsNone(
            invoice.plate_number
        )

    # ==========================================================
    # SUMMARY RESPONSE
    # ==========================================================

    def test_valid_invoice_summary_response(self):

        summary = MechanicInvoiceSummaryResponse(
            customer_id=1,
            name="Ahmed Ali",
            phone_number="55555555",
            invoice_id=10,
            plate_number="ABC-123",
            payment_status=PaymentStatus.PAID,
            invoice_date=datetime(
                2026,
                8,
                19,
                10,
                30,
            ),
        )

        self.assertEqual(
            summary.customer_id,
            1,
        )

        self.assertEqual(
            summary.invoice_id,
            10,
        )

        self.assertEqual(
            summary.plate_number,
            "ABC-123",
        )

        self.assertEqual(
            summary.payment_status,
            PaymentStatus.PAID,
        )

    # ==========================================================
    # SUMMARY LIST RESPONSE
    # ==========================================================

    def test_valid_invoice_summary_list_response(self):

        summary = MechanicInvoiceSummaryResponse(
            customer_id=1,
            name="Ahmed Ali",
            phone_number="55555555",
            invoice_id=10,
            plate_number="ABC-123",
            payment_status=PaymentStatus.PAID,
            invoice_date=datetime(
                2026,
                8,
                19,
                10,
                30,
            ),
        )

        pagination = PaginationResponse(
            limit=10,
            offset=0,
            total=1,
            has_more=False,
        )

        response = MechanicInvoiceSummaryListResponse(
            customers=[summary],
            pagination=pagination,
        )

        self.assertEqual(
            len(response.customers),
            1,
        )

        self.assertEqual(
            response.customers[0].invoice_id,
            10,
        )

        self.assertEqual(
            response.pagination.total,
            1,
        )

        self.assertFalse(
            response.pagination.has_more
        )

    # ==========================================================
    # FULL CUSTOMER RESPONSE
    # ==========================================================

    def test_valid_customer_response(self):

        customer = MechanicCustomerResponse(
            id=1,
            customer_name="Ahmed Ali",
            phone_number="55555555",
            qid="12345678901",
        )

        self.assertEqual(
            customer.id,
            1,
        )

        self.assertEqual(
            customer.customer_name,
            "Ahmed Ali",
        )

    # ==========================================================
    # FULL ITEM RESPONSE
    # ==========================================================

    def test_valid_item_response(self):

        item = MechanicItemResponse(
            id=1,
            invoice_id=10,
            description="Engine Oil",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50.00"),
            commission=Decimal("5.00"),
        )

        self.assertEqual(
            item.id,
            1,
        )

        self.assertEqual(
            item.invoice_id,
            10,
        )

        self.assertEqual(
            item.quantity,
            Decimal("2.00"),
        )

    # ==========================================================
    # FULL INVOICE RESPONSE
    # ==========================================================

    def test_valid_full_invoice_response(self):

        customer = MechanicCustomerResponse(
            id=1,
            customer_name="Ahmed Ali",
            phone_number="55555555",
            qid="12345678901",
        )

        item = MechanicItemResponse(
            id=1,
            invoice_id=10,
            description="Engine Oil",
            quantity=Decimal("2.00"),
            unit_price=Decimal("50.00"),
            commission=Decimal("5.00"),
        )

        invoice = MechanicInvoiceResponse(
            id=10,
            customer_id=1,
            plate_number="ABC-123",
            labor_charges=Decimal("100.00"),
            payment_status=PaymentStatus.PAID,
            created_by=5,
            created_at=datetime(
                2026,
                8,
                19,
                10,
                30,
            ),
            customer=customer,
            items=[item],
        )

        self.assertEqual(
            invoice.id,
            10,
        )

        self.assertEqual(
            invoice.customer.id,
            1,
        )

        self.assertEqual(
            len(invoice.items),
            1,
        )

        self.assertEqual(
            invoice.items[0].id,
            1,
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )