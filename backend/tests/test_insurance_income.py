import unittest
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_income import InsuranceIncome
from app.services.insurance_income import create_insurance_income


class InsuranceIncomeTests(unittest.TestCase):

    def test_create_insurance_income_successfully(self):
        with Session(engine) as db:
            income = create_insurance_income(
                db=db,
                description="Claim processing payout",
                price=Decimal("1250.00"),
                created_by=1,
            )

            db.flush()

            self.assertIsNotNone(income.id)
            self.assertEqual(income.description, "Claim processing payout")
            self.assertEqual(income.price, Decimal("1250.00"))
            self.assertEqual(income.created_by, 1)
            self.assertTrue(income.is_active)
            self.assertIsNotNone(income.created_at)
            self.assertIsNotNone(income.updated_at)

            db.rollback()

    def test_description_is_trimmed(self):
        with Session(engine) as db:
            income = create_insurance_income(
                db=db,
                description="   Consultation revenue   ",
                price=Decimal("350.00"),
                created_by=1,
            )

            db.flush()
            self.assertEqual(income.description, "Consultation revenue")
            db.rollback()

    def test_empty_description_is_rejected(self):
        with Session(engine) as db:
            with self.assertRaisesRegex(ValueError, "description is required"):
                create_insurance_income(
                    db=db,
                    description="",
                    price=Decimal("100.00"),
                    created_by=1,
                )
            db.rollback()

    def test_whitespace_description_is_rejected(self):
        with Session(engine) as db:
            with self.assertRaisesRegex(ValueError, "description is required"):
                create_insurance_income(
                    db=db,
                    description="    ",
                    price=Decimal("100.00"),
                    created_by=1,
                )
            db.rollback()

    def test_zero_price_is_allowed(self):
        with Session(engine) as db:
            income = create_insurance_income(
                db=db,
                description="Zero fee service",
                price=Decimal("0.00"),
                created_by=1,
            )
            db.flush()
            self.assertEqual(income.price, Decimal("0.00"))
            db.rollback()

    def test_negative_price_is_rejected(self):
        with Session(engine) as db:
            with self.assertRaisesRegex(ValueError, "price cannot be negative"):
                create_insurance_income(
                    db=db,
                    description="Invalid revenue",
                    price=Decimal("-25.00"),
                    created_by=1,
                )
            db.rollback()
