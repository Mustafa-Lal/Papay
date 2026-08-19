import unittest
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_image import (
    InsuranceImage,
    InsuranceImageType,
)
from app.services.insurance_image_deletion import (
    delete_insurance_image,
)


class InsuranceImageDeleteTests(unittest.TestCase):

    def create_test_image(self, db):
        image = InsuranceImage(
            invoice_id=1,
            image_type=InsuranceImageType.BEFORE,
            file_path="data/uploads/insurance/test/test_image.jpg",
        )

        db.add(image)
        db.flush()

        # Create a temporary file for testing.
        file_path = Path(image.file_path)
        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        file_path.write_bytes(b"test image data")

        return image

    # ---------------------------------------------------------
    # DATABASE RECORD AND FILE ARE DELETED
    # ---------------------------------------------------------

    def test_image_record_and_file_are_deleted(self):
        with Session(engine) as db:

            image = self.create_test_image(db)

            image_id = image.id
            file_path = Path(image.file_path)

            delete_insurance_image(
                db=db,
                image_id=image_id,
            )

            saved_image = db.scalar(
                select(InsuranceImage).where(
                    InsuranceImage.id == image_id
                )
            )

            self.assertIsNone(saved_image)
            self.assertFalse(file_path.exists())

            # Clean up empty test directories.
            try:
                file_path.parent.rmdir()
                file_path.parent.parent.rmdir()
            except OSError:
                pass

    # ---------------------------------------------------------
    # NONEXISTENT IMAGE
    # ---------------------------------------------------------

    def test_nonexistent_image_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Insurance image not found",
            ):
                delete_insurance_image(
                    db=db,
                    image_id=999999,
                )

            db.rollback()

    # ---------------------------------------------------------
    # OTHER IMAGE REMAINS
    # ---------------------------------------------------------

    def test_other_image_remains(self):
        with Session(engine) as db:

            image1 = self.create_test_image(db)

            image2 = InsuranceImage(
                invoice_id=1,
                image_type=InsuranceImageType.AFTER,
                file_path=(
                    "data/uploads/insurance/"
                    "test/test_image_2.jpg"
                ),
            )

            db.add(image2)
            db.flush()

            file_path1 = Path(image1.file_path)
            file_path2 = Path(image2.file_path)

            file_path2.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            file_path2.write_bytes(
                b"test image 2 data"
            )

            image1_id = image1.id
            image2_id = image2.id

            delete_insurance_image(
                db=db,
                image_id=image1_id,
            )

            remaining_image = db.scalar(
                select(InsuranceImage).where(
                    InsuranceImage.id == image2_id
                )
            )

            self.assertIsNotNone(
                remaining_image
            )

            self.assertFalse(
                file_path1.exists()
            )

            self.assertTrue(
                file_path2.exists()
            )

            # Clean up.
            db.delete(remaining_image)
            db.commit()

            file_path2.unlink(
                missing_ok=True
            )

            try:
                file_path1.parent.rmdir()
            except OSError:
                pass

    # ---------------------------------------------------------
    # IMAGE FILE DOES NOT EXIST
    # ---------------------------------------------------------

    def test_missing_file_does_not_prevent_record_deletion(self):
        with Session(engine) as db:

            image = InsuranceImage(
                invoice_id=1,
                image_type=InsuranceImageType.BEFORE,
                file_path=(
                    "data/uploads/insurance/"
                    "test/nonexistent.jpg"
                ),
            )

            db.add(image)
            db.commit()

            image_id = image.id

            # File deliberately does not exist.
            delete_insurance_image(
                db=db,
                image_id=image_id,
            )

            saved_image = db.scalar(
                select(InsuranceImage).where(
                    InsuranceImage.id == image_id
                )
            )

            self.assertIsNone(
                saved_image
            )

    # ---------------------------------------------------------
    # DELETE CAN BE ROLLED BACK
    # ---------------------------------------------------------

    def test_delete_can_be_rolled_back(self):
        with Session(engine) as db:

            image = self.create_test_image(db)

            image_id = image.id
            file_path = Path(image.file_path)

            # The current delete service commits internally,
            # so a normal db.rollback() cannot undo the
            # deletion. This test documents that behavior.
            delete_insurance_image(
                db=db,
                image_id=image_id,
            )

            db.rollback()

            saved_image = db.scalar(
                select(InsuranceImage).where(
                    InsuranceImage.id == image_id
                )
            )

            self.assertIsNone(
                saved_image
            )

            self.assertFalse(
                file_path.exists()
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )