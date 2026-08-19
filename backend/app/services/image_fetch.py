from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance_image import InsuranceImage


def get_insurance_image(
    db: Session,
    image_id: int,
) -> str:

    # --------------------------------------------------
    # Find image
    # --------------------------------------------------

    image = db.scalar(
        select(InsuranceImage).where(
            InsuranceImage.id == image_id
        )
    )

    if image is None:
        raise ValueError(
            "Insurance image not found."
        )

    # --------------------------------------------------
    # Verify file exists
    # --------------------------------------------------

    file_path = Path(image.file_path)

    if not file_path.is_file():
        raise ValueError(
            "Insurance image file not found."
        )

    # --------------------------------------------------
    # Return file path
    # --------------------------------------------------

    return image.file_path