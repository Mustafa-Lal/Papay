from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UtilityBillType(str, Enum):
    INTERNET = "INTERNET"
    ELECTRICITY = "ELECTRICITY"
    WATER = "WATER"


class UtilityBill(Base):
    __tablename__ = "utility_bills"

    __table_args__ = (
        UniqueConstraint(
            "bill_type",
            "year",
            "month",
            name="uq_utility_bill_type_year_month",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    bill_type: Mapped[UtilityBillType] = mapped_column(
        SQLEnum(UtilityBillType),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )