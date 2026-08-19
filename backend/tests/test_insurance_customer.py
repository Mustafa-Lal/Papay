"""
Tests for the insurance customer service.

These tests verify:
- Creating a customer with all fields.
- Creating a customer with optional fields omitted.
- Creating multiple independent customers.
- Persisting the customer correctly in the database.
"""

import unittest

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_customer import InsuranceCustomer
from app.services.insurance_customer import (
    create_insurance_customer,
)


class InsuranceCustomerTests(unittest.TestCase):

    def test_create_customer_with_all_fields(self):
        """A customer can be created with all available information."""

        with Session(engine) as db:
            customer = create_insurance_customer(
                db=db,
                customer_name="Ahmed Ali",
                phone_number="55555555",
                qid="12345678901",
            )

            self.assertIsNotNone(customer.id)
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

    def test_create_customer_with_only_name(self):
        """Phone number and QID are optional."""

        with Session(engine) as db:
            customer = create_insurance_customer(
                db=db,
                customer_name="Ahmed",
            )

            self.assertIsNotNone(customer.id)
            self.assertEqual(
                customer.customer_name,
                "Ahmed",
            )
            self.assertIsNone(
                customer.phone_number
            )
            self.assertIsNone(
                customer.qid
            )

    def test_create_customer_without_optional_fields(self):
        """
        A customer can be created even when name,
        phone number, and QID are not provided.
        """

        with Session(engine) as db:
            customer = create_insurance_customer(
                db=db,
            )

            self.assertIsNotNone(customer.id)
            self.assertIsNone(
                customer.customer_name
            )
            self.assertIsNone(
                customer.phone_number
            )
            self.assertIsNone(
                customer.qid
            )

    def test_customers_are_independent(self):
        """
        Two customers with the same information are
        still separate customer records.
        """

        with Session(engine) as db:
            customer_1 = create_insurance_customer(
                db=db,
                customer_name="Ahmed",
                phone_number="55555555",
                qid="12345678901",
            )

            customer_2 = create_insurance_customer(
                db=db,
                customer_name="Ahmed",
                phone_number="55555555",
                qid="12345678901",
            )

            self.assertNotEqual(
                customer_1.id,
                customer_2.id,
            )

    def test_customer_is_saved_in_database(self):
        """The created customer must actually persist in the database."""

        with Session(engine) as db:
            customer = create_insurance_customer(
                db=db,
                customer_name="Test Customer",
                phone_number="55555555",
                qid="987654321",
            )

            customer_id = customer.id

            saved_customer = db.scalar(
                select(InsuranceCustomer).where(
                    InsuranceCustomer.id == customer_id
                )
            )

            self.assertIsNotNone(
                saved_customer
            )

            self.assertEqual(
                saved_customer.customer_name,
                "Test Customer",
            )

    def test_empty_strings_are_stored_as_values(self):
        """
        Empty strings are different from NULL.

        This test documents the current behavior.
        Validation for empty strings should eventually
        be handled by the API/request layer.
        """

        with Session(engine) as db:
            customer = create_insurance_customer(
                db=db,
                customer_name="",
                phone_number="",
                qid="",
            )

            self.assertIsNotNone(customer.id)

            self.assertEqual(
                customer.customer_name,
                "",
            )

            self.assertEqual(
                customer.phone_number,
                "",
            )

            self.assertEqual(
                customer.qid,
                "",
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )