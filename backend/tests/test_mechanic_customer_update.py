import unittest

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.mechanic_customer import MechanicCustomer

from app.services.mechanic_customer import (
    create_mechanic_customer,
)
from app.services.mechanic_customer_update import (
    update_mechanic_customer,
)


class MechanicCustomerUpdateTests(unittest.TestCase):

    def create_test_customer(self, db):
        customer = create_mechanic_customer(
            db=db,
            customer_name="Original Name",
            phone_number="11111111",
            qid="11111111111",
        )

        db.flush()

        return customer

    # ---------------------------------------------------------
    # UPDATE NAME
    # ---------------------------------------------------------

    def test_update_customer_name(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            update_mechanic_customer(
                db=db,
                customer_id=customer.id,
                customer_name="Updated Name",
            )

            self.assertEqual(
                customer.customer_name,
                "Updated Name",
            )

            self.assertEqual(
                customer.phone_number,
                "11111111",
            )

            self.assertEqual(
                customer.qid,
                "11111111111",
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE PHONE
    # ---------------------------------------------------------

    def test_update_customer_phone_number(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            update_mechanic_customer(
                db=db,
                customer_id=customer.id,
                phone_number="99999999",
            )

            self.assertEqual(
                customer.phone_number,
                "99999999",
            )

            self.assertEqual(
                customer.customer_name,
                "Original Name",
            )

            self.assertEqual(
                customer.qid,
                "11111111111",
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE QID
    # ---------------------------------------------------------

    def test_update_customer_qid(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            update_mechanic_customer(
                db=db,
                customer_id=customer.id,
                qid="99999999999",
            )

            self.assertEqual(
                customer.qid,
                "99999999999",
            )

            self.assertEqual(
                customer.customer_name,
                "Original Name",
            )

            self.assertEqual(
                customer.phone_number,
                "11111111",
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE ALL FIELDS
    # ---------------------------------------------------------

    def test_update_all_customer_fields(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            update_mechanic_customer(
                db=db,
                customer_id=customer.id,
                customer_name="New Name",
                phone_number="22222222",
                qid="22222222222",
            )

            self.assertEqual(
                customer.customer_name,
                "New Name",
            )

            self.assertEqual(
                customer.phone_number,
                "22222222",
            )

            self.assertEqual(
                customer.qid,
                "22222222222",
            )

            db.rollback()

    # ---------------------------------------------------------
    # PARTIAL UPDATE
    # ---------------------------------------------------------

    def test_partial_update_does_not_change_other_fields(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            update_mechanic_customer(
                db=db,
                customer_id=customer.id,
                customer_name="Only Name Changed",
            )

            self.assertEqual(
                customer.customer_name,
                "Only Name Changed",
            )

            self.assertEqual(
                customer.phone_number,
                "11111111",
            )

            self.assertEqual(
                customer.qid,
                "11111111111",
            )

            db.rollback()

    # ---------------------------------------------------------
    # NAME TRIMMING
    # ---------------------------------------------------------

    def test_updated_name_is_trimmed(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            update_mechanic_customer(
                db=db,
                customer_id=customer.id,
                customer_name="  Updated Name  ",
            )

            self.assertEqual(
                customer.customer_name,
                "Updated Name",
            )

            db.rollback()

    # ---------------------------------------------------------
    # EMPTY NAME
    # ---------------------------------------------------------

    def test_empty_name_is_rejected(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            with self.assertRaisesRegex(
                ValueError,
                "Customer name cannot be empty",
            ):
                update_mechanic_customer(
                    db=db,
                    customer_id=customer.id,
                    customer_name="",
                )

            self.assertEqual(
                customer.customer_name,
                "Original Name",
            )

            db.rollback()

    # ---------------------------------------------------------
    # WHITESPACE NAME
    # ---------------------------------------------------------

    def test_whitespace_name_is_rejected(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            with self.assertRaisesRegex(
                ValueError,
                "Customer name cannot be empty",
            ):
                update_mechanic_customer(
                    db=db,
                    customer_id=customer.id,
                    customer_name="   ",
                )

            self.assertEqual(
                customer.customer_name,
                "Original Name",
            )

            db.rollback()

    # ---------------------------------------------------------
    # CUSTOMER NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_customer_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Mechanic customer not found",
            ):
                update_mechanic_customer(
                    db=db,
                    customer_id=999999,
                    customer_name="Updated Name",
                )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            customer_id = customer.id

            update_mechanic_customer(
                db=db,
                customer_id=customer_id,
                customer_name="Persisted Name",
                phone_number="33333333",
                qid="33333333333",
            )

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
                "Persisted Name",
            )

            self.assertEqual(
                saved_customer.phone_number,
                "33333333",
            )

            self.assertEqual(
                saved_customer.qid,
                "33333333333",
            )

            # Clean up committed test data.
            db.delete(saved_customer)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            customer = self.create_test_customer(db)

            # Commit creation first so rollback only affects
            # the update transaction.
            db.commit()

            customer_id = customer.id

            update_mechanic_customer(
                db=db,
                customer_id=customer_id,
                customer_name="Temporary Name",
                phone_number="44444444",
                qid="44444444444",
            )

            db.rollback()

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
                "Original Name",
            )

            self.assertEqual(
                saved_customer.phone_number,
                "11111111",
            )

            self.assertEqual(
                saved_customer.qid,
                "11111111111",
            )

            # Clean up.
            db.delete(saved_customer)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )