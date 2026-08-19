"""
Tests for insurance invoice Pydantic schemas.

These tests verify API-level validation before data reaches
the service layer.
"""

import unittest
from decimal import Decimal

from pydantic import ValidationError

from app.models.insurance_invoice import PaymentStatus
from app.schemas.insurance_invoice import (
    InsuranceCustomerCreate,
    InsuranceInvoiceCreate,
    InsuranceItemCreate,
)


class InsuranceSchemaTests(unittest.TestCase):

    # ---------------------------------------------------------
    # VALID CUSTOMER TESTS
    # ---------------------------------------------------------

    def test_customer_with_all_fields(self):
        customer = InsuranceCustomerCreate(
            customer_name="Ahmed",
            phone_number="55555555",
            qid="123456789",
        )

        self.assertEqual(
            customer.customer_name,
            "Ahmed",
        )

        self.assertEqual(
            customer.phone_number,
            "55555555",
        )

        self.assertEqual(
            customer.qid,
            "123456789",
        )

    def test_customer_with_no_fields(self):
        """
        All customer fields are optional.
        """

        customer = InsuranceCustomerCreate()

        self.assertIsNone(
            customer.customer_name
        )

        self.assertIsNone(
            customer.phone_number
        )

        self.assertIsNone(
            customer.qid
        )

    def test_empty_customer_strings_become_none(self):
        """
        Empty strings should be treated as missing information.
        """

        customer = InsuranceCustomerCreate(
            customer_name="",
            phone_number="   ",
            qid="",
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

    # ---------------------------------------------------------
    # VALID ITEM TESTS
    # ---------------------------------------------------------

    def test_valid_item(self):
        item = InsuranceItemCreate(
            description="Bumper",
            quantity=Decimal("2"),
            unit_price=Decimal("500.00"),
            commission=Decimal("50.00"),
        )

        self.assertEqual(
            item.description,
            "Bumper",
        )

        self.assertEqual(
            item.quantity,
            Decimal("2"),
        )

        self.assertEqual(
            item.unit_price,
            Decimal("500.00"),
        )

        self.assertEqual(
            item.commission,
            Decimal("50.00"),
        )

    def test_item_commission_defaults_to_zero(self):
        item = InsuranceItemCreate(
            description="Bumper",
            quantity=Decimal("1"),
            unit_price=Decimal("500.00"),
        )

        self.assertEqual(
            item.commission,
            Decimal("0.00"),
        )

    def test_item_description_is_trimmed(self):
        item = InsuranceItemCreate(
            description="  Bumper  ",
            quantity=Decimal("1"),
            unit_price=Decimal("500.00"),
        )

        self.assertEqual(
            item.description,
            "Bumper",
        )

    # ---------------------------------------------------------
    # INVALID ITEM TESTS
    # ---------------------------------------------------------

    def test_empty_item_description_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceItemCreate(
                description="",
                quantity=Decimal("1"),
                unit_price=Decimal("100"),
            )

    def test_whitespace_item_description_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceItemCreate(
                description="   ",
                quantity=Decimal("1"),
                unit_price=Decimal("100"),
            )

    def test_zero_quantity_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceItemCreate(
                description="Bumper",
                quantity=Decimal("0"),
                unit_price=Decimal("100"),
            )

    def test_negative_quantity_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceItemCreate(
                description="Bumper",
                quantity=Decimal("-1"),
                unit_price=Decimal("100"),
            )

    def test_negative_unit_price_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceItemCreate(
                description="Bumper",
                quantity=Decimal("1"),
                unit_price=Decimal("-100"),
            )

    def test_negative_commission_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceItemCreate(
                description="Bumper",
                quantity=Decimal("1"),
                unit_price=Decimal("100"),
                commission=Decimal("-10"),
            )

    # ---------------------------------------------------------
    # VALID INVOICE TESTS
    # ---------------------------------------------------------

    def test_complete_invoice(self):
        invoice = InsuranceInvoiceCreate(
            customer={
                "customer_name": "Ahmed",
                "phone_number": "55555555",
                "qid": "123456789",
            },
            plate_number="ABC-123",
            labor_charges=Decimal("500.00"),
            payment_status=PaymentStatus.UNPAID,
            items=[
                {
                    "description": "Bumper",
                    "quantity": Decimal("1"),
                    "unit_price": Decimal("800.00"),
                    "commission": Decimal("50.00"),
                },
                {
                    "description": "Headlight",
                    "quantity": Decimal("2"),
                    "unit_price": Decimal("300.00"),
                },
            ],
        )

        self.assertEqual(
            invoice.plate_number,
            "ABC-123",
        )

        self.assertEqual(
            len(invoice.items),
            2,
        )

    def test_invoice_defaults_labor_to_zero(self):
        invoice = InsuranceInvoiceCreate(
            customer={},
            plate_number="ABC-123",
            items=[
                {
                    "description": "Bumper",
                    "quantity": 1,
                    "unit_price": 100,
                }
            ],
        )

        self.assertEqual(
            invoice.labor_charges,
            Decimal("0.00"),
        )

    def test_invoice_defaults_payment_status_to_unpaid(self):
        invoice = InsuranceInvoiceCreate(
            customer={},
            plate_number="ABC-123",
            items=[
                {
                    "description": "Bumper",
                    "quantity": 1,
                    "unit_price": 100,
                }
            ],
        )

        self.assertEqual(
            invoice.payment_status,
            PaymentStatus.UNPAID,
        )

    def test_plate_number_is_trimmed(self):
        invoice = InsuranceInvoiceCreate(
            customer={},
            plate_number="  ABC-123  ",
            items=[
                {
                    "description": "Bumper",
                    "quantity": 1,
                    "unit_price": 100,
                }
            ],
        )

        self.assertEqual(
            invoice.plate_number,
            "ABC-123",
        )

    # ---------------------------------------------------------
    # INVALID INVOICE TESTS
    # ---------------------------------------------------------

    def test_empty_plate_number_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceInvoiceCreate(
                customer={},
                plate_number="",
                items=[
                    {
                        "description": "Bumper",
                        "quantity": 1,
                        "unit_price": 100,
                    }
                ],
            )

    def test_whitespace_plate_number_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceInvoiceCreate(
                customer={},
                plate_number="   ",
                items=[
                    {
                        "description": "Bumper",
                        "quantity": 1,
                        "unit_price": 100,
                    }
                ],
            )

    def test_negative_labor_charges_are_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceInvoiceCreate(
                customer={},
                plate_number="ABC-123",
                labor_charges=Decimal("-100"),
                items=[
                    {
                        "description": "Bumper",
                        "quantity": 1,
                        "unit_price": 100,
                    }
                ],
            )

    def test_empty_items_are_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceInvoiceCreate(
                customer={},
                plate_number="ABC-123",
                items=[],
            )

    def test_invalid_payment_status_is_rejected(self):
        with self.assertRaises(ValidationError):
            InsuranceInvoiceCreate(
                customer={},
                plate_number="ABC-123",
                payment_status="INVALID_STATUS",
                items=[
                    {
                        "description": "Bumper",
                        "quantity": 1,
                        "unit_price": 100,
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )