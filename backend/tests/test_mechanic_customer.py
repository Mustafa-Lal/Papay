import unittest

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.mechanic_customer import MechanicCustomer

from app.services.mechanic_customer import (
    create_mechanic_customer,
)


class MechanicCustomerTests(unittest.TestCase):

    def test_create_customer_with_all_fields(self):
        with Session(engine) as db:

            customer = create_mechanic_customer(
                db=db,
                customer_name="Ahmed Ali",
                phone_number="55555555",
                qid="12345678901",
            )

            db.flush()

            self.assertIsNotNone(
                customer.id
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

            db.rollback()

    def test_create_customer_with_only_name(self):
        with Session(engine) as db:

            customer = create_mechanic_customer(
                db=db,
                customer_name="Ahmed",
            )

            db.flush()

            self.assertIsNotNone(
                customer.id
            )

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

            db.rollback()

    def test_create_customer_without_optional_fields(self):
        with Session(engine) as db:

            customer = create_mechanic_customer(
                db=db,
            )

            db.flush()

            self.assertIsNotNone(
                customer.id
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

            db.rollback()

    def test_customers_are_independent(self):
        with Session(engine) as db:

            customer_1 = create_mechanic_customer(
                db=db,
                customer_name="Ahmed",
                phone_number="55555555",
                qid="12345678901",
            )

            customer_2 = create_mechanic_customer(
                db=db,
                customer_name="Ahmed",
                phone_number="55555555",
                qid="12345678901",
            )

            db.flush()

            self.assertIsNotNone(
                customer_1.id
            )

            self.assertIsNotNone(
                customer_2.id
            )

            self.assertNotEqual(
                customer_1.id,
                customer_2.id,
            )

            db.rollback()

    def test_customer_is_persisted_after_commit(self):
        with Session(engine) as db:

            customer = create_mechanic_customer(
                db=db,
                customer_name="Test Customer",
            )

            db.flush()

            customer_id = customer.id

            db.commit()

            saved_customer = db.scalar(
                select(MechanicCustomer).where(
                    MechanicCustomer.id == customer_id
                )
            )

            self.assertIsNotNone(
                saved_customer
            )

            self.assertEqual(
                saved_customer.customer_name,
                "Test Customer",
            )

    def test_customer_is_rolled_back(self):
        with Session(engine) as db:

            customer = create_mechanic_customer(
                db=db,
                customer_name="Rollback Customer",
            )

            db.flush()

            customer_id = customer.id

            db.rollback()

            saved_customer = db.scalar(
                select(MechanicCustomer).where(
                    MechanicCustomer.id == customer_id
                )
            )

            self.assertIsNone(
                saved_customer
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )