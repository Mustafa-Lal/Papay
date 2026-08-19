from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.insurance_image import InsuranceImage


def delete_insurance_image(
    db: Session,
    image_id: int,
) -> None:

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
    # Keep the file path before deleting DB record
    # --------------------------------------------------

    file_path = Path(image.file_path)

    # --------------------------------------------------
    # Delete database record
    # --------------------------------------------------

    db.delete(image)

    # --------------------------------------------------
    # Commit database deletion
    # --------------------------------------------------

    try:
        db.commit()

    except Exception:
        db.rollback()
        raise

    # --------------------------------------------------
    # Delete physical file
    # --------------------------------------------------

    try:
        file_path.unlink(missing_ok=True)

    except OSError as exc:
        raise ValueError(
            "Image record was deleted, but the image file "
            "could not be deleted."
        ) from exc