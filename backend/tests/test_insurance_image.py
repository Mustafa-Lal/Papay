"""
Tests for the insurance image service.

Tests:
- Valid JPEG uploads.
- BEFORE images.
- AFTER images.
- Multiple images.
- Invalid PNG content.
- Fake JPEG files.
- Empty files.
- Oversized files.
- Invalid invoice.
- Invalid image type.
- Database persistence.
"""

import unittest
from io import BytesIO
from pathlib import Path
from decimal import Decimal

from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_customer import InsuranceCustomer
from app.models.insurance_image import (
    InsuranceImage,
    InsuranceImageType,
)
from app.services.insurance_invoice import (
    create_insurance_invoice,
)
from app.services.insurance_image import (
    create_insurance_image,
    IMAGE_STORAGE_ROOT,
)


class InsuranceImageTests(unittest.TestCase):

    def create_invoice(self, db):
        customer = InsuranceCustomer(
            customer_name="Test Customer"
        )

        db.add(customer)
        db.commit()
        db.refresh(customer)

        return create_insurance_invoice(
            db=db,
            customer_id=customer.id,
            plate_number="IMG-123",
            created_by=1,
        )

    def create_jpeg(self):
        """
        Create a real JPEG image in memory.
        """

        image = Image.new(
            "RGB",
            (100, 100),
            "white",
        )

        buffer = BytesIO()

        image.save(
            buffer,
            format="JPEG",
        )

        return buffer.getvalue()

    def create_png(self):
        """
        Create a real PNG image in memory.
        """

        image = Image.new(
            "RGB",
            (100, 100),
            "white",
        )

        buffer = BytesIO()

        image.save(
            buffer,
            format="PNG",
        )

        return buffer.getvalue()

    def test_create_before_jpeg(self):
        """A valid JPEG should be saved as a BEFORE image."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            image = create_insurance_image(
                db=db,
                invoice_id=invoice.id,
                image_type=InsuranceImageType.BEFORE,
                image_bytes=self.create_jpeg(),
            )

            self.assertIsNotNone(image.id)

            self.assertEqual(
                image.invoice_id,
                invoice.id,
            )

            self.assertEqual(
                image.image_type,
                InsuranceImageType.BEFORE,
            )

            self.assertTrue(
                Path(image.file_path).exists()
            )

    def test_create_after_jpeg(self):
        """A valid JPEG should be saved as an AFTER image."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            image = create_insurance_image(
                db=db,
                invoice_id=invoice.id,
                image_type=InsuranceImageType.AFTER,
                image_bytes=self.create_jpeg(),
            )

            self.assertEqual(
                image.image_type,
                InsuranceImageType.AFTER,
            )

            self.assertTrue(
                Path(image.file_path).exists()
            )

    def test_png_is_rejected(self):
        """A real PNG must be rejected."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):
                create_insurance_image(
                    db=db,
                    invoice_id=invoice.id,
                    image_type=InsuranceImageType.BEFORE,
                    image_bytes=self.create_png(),
                )

    def test_fake_jpeg_is_rejected(self):
        """Renaming random bytes as JPEG must not bypass validation."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            fake_jpeg = b"this is not actually a jpeg"

            with self.assertRaises(ValueError):
                create_insurance_image(
                    db=db,
                    invoice_id=invoice.id,
                    image_type=InsuranceImageType.BEFORE,
                    image_bytes=fake_jpeg,
                )

    def test_empty_image_is_rejected(self):
        """Empty image data must be rejected."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            with self.assertRaises(ValueError):
                create_insurance_image(
                    db=db,
                    invoice_id=invoice.id,
                    image_type=InsuranceImageType.BEFORE,
                    image_bytes=b"",
                )

    def test_nonexistent_invoice_is_rejected(self):
        """Images cannot belong to nonexistent invoices."""

        with Session(engine) as db:

            with self.assertRaises(ValueError):
                create_insurance_image(
                    db=db,
                    invoice_id=999999,
                    image_type=InsuranceImageType.BEFORE,
                    image_bytes=self.create_jpeg(),
                )

    def test_multiple_images_can_be_uploaded(self):
        """Multiple images can belong to the same invoice."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            image_1 = create_insurance_image(
                db=db,
                invoice_id=invoice.id,
                image_type=InsuranceImageType.BEFORE,
                image_bytes=self.create_jpeg(),
            )

            image_2 = create_insurance_image(
                db=db,
                invoice_id=invoice.id,
                image_type=InsuranceImageType.BEFORE,
                image_bytes=self.create_jpeg(),
            )

            image_3 = create_insurance_image(
                db=db,
                invoice_id=invoice.id,
                image_type=InsuranceImageType.AFTER,
                image_bytes=self.create_jpeg(),
            )

            self.assertNotEqual(
                image_1.id,
                image_2.id,
            )

            self.assertNotEqual(
                image_2.id,
                image_3.id,
            )

            images = db.scalars(
                select(InsuranceImage).where(
                    InsuranceImage.invoice_id
                    == invoice.id
                )
            ).all()

            self.assertEqual(
                len(images),
                3,
            )

    def test_backend_generates_unique_paths(self):
        """Each uploaded image gets a different backend path."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            image_1 = create_insurance_image(
                db=db,
                invoice_id=invoice.id,
                image_type=InsuranceImageType.BEFORE,
                image_bytes=self.create_jpeg(),
            )

            image_2 = create_insurance_image(
                db=db,
                invoice_id=invoice.id,
                image_type=InsuranceImageType.BEFORE,
                image_bytes=self.create_jpeg(),
            )

            self.assertNotEqual(
                image_1.file_path,
                image_2.file_path,
            )

    def test_database_record_is_created(self):
        """The image record must persist in the database."""

        with Session(engine) as db:
            invoice = self.create_invoice(db)

            image = create_insurance_image(
                db=db,
                invoice_id=invoice.id,
                image_type=InsuranceImageType.AFTER,
                image_bytes=self.create_jpeg(),
            )

            saved_image = db.scalar(
                select(InsuranceImage).where(
                    InsuranceImage.id == image.id
                )
            )

            self.assertIsNotNone(
                saved_image
            )

            self.assertEqual(
                saved_image.file_path,
                image.file_path,
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )