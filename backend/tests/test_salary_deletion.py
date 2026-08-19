import unittest
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.salary import Salary

from app.services.salary import create_salary
from app.services.salary_deletion import delete_salary


class SalaryDeleteTests(unittest.TestCase):

    def create_test_salary(
        self,
        db,
        name="John",
        amount=Decimal("5000.00"),
    ):
        salary = create_salary(
            db=db,
            name=name,
            amount=amount,
            created_by=1,
        )

        db.flush()

        return salary

    # ---------------------------------------------------------
    # DELETE SALARY
    # ---------------------------------------------------------

    def test_salary_is_deleted(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            salary_id = salary.id

            delete_salary(
                db=db,
                salary_id=salary_id,
            )

            db.commit()

            saved_salary = db.scalar(
                select(Salary).where(
                    Salary.id == salary_id
                )
            )

            self.assertIsNone(
                saved_salary
            )

    # ---------------------------------------------------------
    # NONEXISTENT SALARY
    # ---------------------------------------------------------

    def test_nonexistent_salary_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Salary not found",
            ):
                delete_salary(
                    db=db,
                    salary_id=999999,
                )

            db.rollback()

    # ---------------------------------------------------------
    # OTHER SALARY REMAINS
    # ---------------------------------------------------------

    def test_other_salary_remains(self):
        with Session(engine) as db:

            salary1 = self.create_test_salary(
                db=db,
                name="John",
                amount=Decimal("5000.00"),
            )

            db.commit()

            salary2 = self.create_test_salary(
                db=db,
                name="Ahmed",
                amount=Decimal("6000.00"),
            )

            db.flush()

            salary1_id = salary1.id
            salary2_id = salary2.id

            delete_salary(
                db=db,
                salary_id=salary1_id,
            )

            db.commit()

            deleted_salary = db.scalar(
                select(Salary).where(
                    Salary.id == salary1_id
                )
            )

            remaining_salary = db.scalar(
                select(Salary).where(
                    Salary.id == salary2_id
                )
            )

            self.assertIsNone(
                deleted_salary
            )

            self.assertIsNotNone(
                remaining_salary
            )

            self.assertEqual(
                remaining_salary.name,
                "Ahmed",
            )

            self.assertEqual(
                remaining_salary.amount,
                Decimal("6000.00"),
            )

            # Clean up.
            db.delete(remaining_salary)
            db.commit()

    # ---------------------------------------------------------
    # PERSISTENCE
    # ---------------------------------------------------------

    def test_delete_is_persisted_after_commit(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            salary_id = salary.id

            delete_salary(
                db=db,
                salary_id=salary_id,
            )

            db.commit()

        with Session(engine) as db:

            saved_salary = db.scalar(
                select(Salary).where(
                    Salary.id == salary_id
                )
            )

            self.assertIsNone(
                saved_salary
            )

    # ---------------------------------------------------------
    # ROLLBACK
    # ---------------------------------------------------------

    def test_delete_can_be_rolled_back(self):
        with Session(engine) as db:

            salary = self.create_test_salary(db)

            salary_id = salary.id

            # Commit original record first.
            db.commit()

            delete_salary(
                db=db,
                salary_id=salary_id,
            )

            # Undo deletion.
            db.rollback()

            restored_salary = db.scalar(
                select(Salary).where(
                    Salary.id == salary_id
                )
            )

            self.assertIsNotNone(
                restored_salary
            )

            self.assertEqual(
                restored_salary.name,
                "John",
            )

            self.assertEqual(
                restored_salary.amount,
                Decimal("5000.00"),
            )

            # Clean up.
            db.delete(restored_salary)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )