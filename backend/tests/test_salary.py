import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.salary import Salary

from app.services.salary import create_salary


class SalaryTests(unittest.TestCase):

    # ---------------------------------------------------------
    # CREATE
    # ---------------------------------------------------------

    def test_create_salary_successfully(self):
        with Session(engine) as db:

            salary = create_salary(
                db=db,
                name="Ahmed",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                salary.id
            )

            self.assertEqual(
                salary.name,
                "Ahmed",
            )

            self.assertEqual(
                salary.amount,
                Decimal("5000.00"),
            )

            self.assertEqual(
                salary.created_by,
                1,
            )

            self.assertIsNotNone(
                salary.created_at
            )

            self.assertIsNotNone(
                salary.updated_at
            )

            db.rollback()

    # ---------------------------------------------------------
    # NAME TRIMMING
    # ---------------------------------------------------------

    def test_name_is_trimmed(self):
        with Session(engine) as db:

            salary = create_salary(
                db=db,
                name="  Ahmed  ",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                salary.name,
                "Ahmed",
            )

            db.rollback()

    # ---------------------------------------------------------
    # EMPTY NAME
    # ---------------------------------------------------------

    def test_empty_name_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "name is required",
            ):

                create_salary(
                    db=db,
                    name="",
                    amount=Decimal("5000.00"),
                    created_by=1,
                )

            db.rollback()

    def test_whitespace_name_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "name is required",
            ):

                create_salary(
                    db=db,
                    name="   ",
                    amount=Decimal("5000.00"),
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # AMOUNT
    # ---------------------------------------------------------

    def test_zero_salary_is_allowed(self):
        with Session(engine) as db:

            salary = create_salary(
                db=db,
                name="Ahmed",
                amount=Decimal("0.00"),
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                salary.amount,
                Decimal("0.00"),
            )

            db.rollback()

    def test_negative_salary_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "cannot be negative",
            ):

                create_salary(
                    db=db,
                    name="Ahmed",
                    amount=Decimal("-500.00"),
                    created_by=1,
                )

            db.rollback()

    # ---------------------------------------------------------
    # DUPLICATES ARE ALLOWED
    # ---------------------------------------------------------

    def test_duplicate_people_are_allowed(self):
        with Session(engine) as db:

            salary_1 = create_salary(
                db=db,
                name="Ahmed",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            salary_2 = create_salary(
                db=db,
                name="Ahmed",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(
                salary_1.id
            )

            self.assertIsNotNone(
                salary_2.id
            )

            self.assertNotEqual(
                salary_1.id,
                salary_2.id,
            )

            db.rollback()

    # ---------------------------------------------------------
    # DIFFERENT SALARIES
    # ---------------------------------------------------------

    def test_multiple_salary_records_can_be_created(self):
        with Session(engine) as db:

            salary_1 = create_salary(
                db=db,
                name="Ahmed",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            salary_2 = create_salary(
                db=db,
                name="Ali",
                amount=Decimal("6000.00"),
                created_by=1,
            )

            salary_3 = create_salary(
                db=db,
                name="Omar",
                amount=Decimal("4500.00"),
                created_by=1,
            )

            db.flush()

            self.assertEqual(
                len(
                    {
                        salary_1.id,
                        salary_2.id,
                        salary_3.id,
                    }
                ),
                3,
            )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_salary_is_saved_after_commit(self):
        with Session(engine) as db:

            salary = create_salary(
                db=db,
                name="Ahmed",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            db.flush()

            salary_id = salary.id

            db.commit()

            saved_salary = db.scalar(
                select(Salary).where(
                    Salary.id == salary_id
                )
            )

            self.assertIsNotNone(
                saved_salary
            )

            self.assertEqual(
                saved_salary.name,
                "Ahmed",
            )

            self.assertEqual(
                saved_salary.amount,
                Decimal("5000.00"),
            )

            # Clean up committed test data.
            db.delete(saved_salary)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_salary_can_be_rolled_back(self):
        with Session(engine) as db:

            salary = create_salary(
                db=db,
                name="Rollback Person",
                amount=Decimal("5000.00"),
                created_by=1,
            )

            db.flush()

            salary_id = salary.id

            db.rollback()

            saved_salary = db.scalar(
                select(Salary).where(
                    Salary.id == salary_id
                )
            )

            self.assertIsNone(
                saved_salary
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )