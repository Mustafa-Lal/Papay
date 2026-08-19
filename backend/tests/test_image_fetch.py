import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy.orm import Session

from app.database import engine
from app.models.insurance_image import (
    InsuranceImage,
    InsuranceImageType,
)

from app.services.image_fetch import (
    get_insurance_image,
)


class InsuranceImageFetchTests(unittest.TestCase):

    # ---------------------------------------------------------
    # IMAGE PATH IS RETURNED
    # ---------------------------------------------------------

    def test_image_path_is_returned(self):
        with TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "before.jpg"

            # Create a fake image file.
            image_path.write_bytes(
                b"test image data"
            )

            with Session(engine) as db:

                image = InsuranceImage(
                    invoice_id=1,
                    image_type=InsuranceImageType.BEFORE,
                    file_path=str(image_path),
                )

                db.add(image)
                db.commit()

                image_id = image.id

                result = get_insurance_image(
                    db=db,
                    image_id=image_id,
                )

                self.assertEqual(
                    result,
                    str(image_path),
                )

                # Clean up database record.
                db.delete(image)
                db.commit()

    # ---------------------------------------------------------
    # NONEXISTENT IMAGE
    # ---------------------------------------------------------

    def test_nonexistent_image_is_rejected(self):
        with Session(engine) as db:

            with self.assertRaisesRegex(
                ValueError,
                "Insurance image not found",
            ):
                get_insurance_image(
                    db=db,
                    image_id=999999,
                )

    # ---------------------------------------------------------
    # IMAGE RECORD EXISTS BUT FILE DOES NOT
    # ---------------------------------------------------------

    def test_missing_file_is_rejected(self):
        with Session(engine) as db:

            image = InsuranceImage(
                invoice_id=1,
                image_type=InsuranceImageType.AFTER,
                file_path=(
                    "data/uploads/insurance/"
                    "does-not-exist.jpg"
                ),
            )

            db.add(image)
            db.commit()

            image_id = image.id

            with self.assertRaisesRegex(
                ValueError,
                "Insurance image file not found",
            ):
                get_insurance_image(
                    db=db,
                    image_id=image_id,
                )

            # Clean up.
            db.delete(image)
            db.commit()


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )