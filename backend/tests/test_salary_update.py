import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.salary import Salary

from app.services.salary import create_salary
from app.services.salary_update import update_salary


class SalaryUpdateTests(unittest.TestCase):

    def create_test_salary(self, db):
        salary = create_salary(
            db=db,
            name="John",
            amount=Decimal("5000.00"),
            created_by=1,
        )

        db.flush()

        return salary

    # ---------------------------------------------------------
    # UPDATE NAME
    # ---------------------------------------------------------

    def test_update_name(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            update_salary(
                db=db,
                salary_id=salary.id,
                name="Ahmed",
            )

            self.assertEqual(
                salary.name,
                "Ahmed",
            )

            self.assertEqual(
                salary.amount,
                Decimal("5000.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE AMOUNT
    # ---------------------------------------------------------

    def test_update_amount(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            update_salary(
                db=db,
                salary_id=salary.id,
                amount=Decimal("6000.00"),
            )

            self.assertEqual(
                salary.amount,
                Decimal("6000.00"),
            )

            self.assertEqual(
                salary.name,
                "John",
            )

            db.rollback()

    # ---------------------------------------------------------
    # ZERO AMOUNT
    # ---------------------------------------------------------

    def test_zero_amount_is_allowed(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            update_salary(
                db=db,
                salary_id=salary.id,
                amount=Decimal("0.00"),
            )

            self.assertEqual(
                salary.amount,
                Decimal("0.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NEGATIVE AMOUNT
    # ---------------------------------------------------------

    def test_negative_amount_is_rejected(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            with self.assertRaisesRegex(
                ValueError,
                "Salary amount cannot be negative",
            ):
                update_salary(
                    db=db,
                    salary_id=salary.id,
                    amount=Decimal("-500.00"),
                )

            self.assertEqual(
                salary.amount,
                Decimal("5000.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # EMPTY NAME
    # ---------------------------------------------------------

    def test_empty_name_is_rejected(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            with self.assertRaisesRegex(
                ValueError,
                "Salary name cannot be empty",
            ):
                update_salary(
                    db=db,
                    salary_id=salary.id,
                    name="",
                )

            self.assertEqual(
                salary.name,
                "John",
            )

            db.rollback()

    # ---------------------------------------------------------
    # WHITESPACE NAME
    # ---------------------------------------------------------

    def test_whitespace_name_is_rejected(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            with self.assertRaisesRegex(
                ValueError,
                "Salary name cannot be empty",
            ):
                update_salary(
                    db=db,
                    salary_id=salary.id,
                    name="   ",
                )

            self.assertEqual(
                salary.name,
                "John",
            )

            db.rollback()

    # ---------------------------------------------------------
    # NAME TRIMMING
    # ---------------------------------------------------------

    def test_updated_name_is_trimmed(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            update_salary(
                db=db,
                salary_id=salary.id,
                name="  Ahmed  ",
            )

            self.assertEqual(
                salary.name,
                "Ahmed",
            )

            db.rollback()

    # ---------------------------------------------------------
    # UPDATE ALL FIELDS
    # ---------------------------------------------------------

    def test_update_all_salary_fields(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            update_salary(
                db=db,
                salary_id=salary.id,
                name="Ahmed",
                amount=Decimal("7000.00"),
            )

            self.assertEqual(
                salary.name,
                "Ahmed",
            )

            self.assertEqual(
                salary.amount,
                Decimal("7000.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # PARTIAL UPDATE
    # ---------------------------------------------------------

    def test_partial_update_does_not_change_other_fields(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            update_salary(
                db=db,
                salary_id=salary.id,
                name="Ahmed",
            )

            self.assertEqual(
                salary.name,
                "Ahmed",
            )

            self.assertEqual(
                salary.amount,
                Decimal("5000.00"),
            )

            db.rollback()

    # ---------------------------------------------------------
    # NOT FOUND
    # ---------------------------------------------------------

    def test_nonexistent_salary_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Salary not found",
            ):
                update_salary(
                    db=db,
                    salary_id=999999,
                    name="Ahmed",
                )

            db.rollback()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_update_is_persisted_after_commit(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            salary_id = salary.id

            update_salary(
                db=db,
                salary_id=salary_id,
                name="Persisted Name",
                amount=Decimal("8000.00"),
            )

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
                "Persisted Name",
            )

            self.assertEqual(
                saved_salary.amount,
                Decimal("8000.00"),
            )

            # Clean up.
            db.delete(saved_salary)
            db.commit()

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_update_can_be_rolled_back(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            # Commit the original salary first.
            # Rollback must only undo the update.
            db.commit()

            salary_id = salary.id

            update_salary(
                db=db,
                salary_id=salary_id,
                name="Temporary Name",
                amount=Decimal("9999.00"),
            )

            db.rollback()

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
                "John",
            )

            self.assertEqual(
                saved_salary.amount,
                Decimal("5000.00"),
            )

            # Clean up.
            db.delete(saved_salary)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )