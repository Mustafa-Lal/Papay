"""
Insurance invoice image model.

Stores references to images associated with an insurance invoice.

Actual JPEG files are stored outside the database.
Only the file path is stored in the database.

Image types:
- BEFORE
- AFTER
"""

from enum import Enum

from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InsuranceImageType(str, Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"


class InsuranceImage(Base):
    __tablename__ = "insurance_images"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey(
            "insurance_invoices.id"
        ),
        nullable=False,
    )

    image_type: Mapped[InsuranceImageType] = mapped_column(
        SQLEnum(InsuranceImageType),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )