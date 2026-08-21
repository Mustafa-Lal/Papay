"""
Insurance invoice model.

Represents an invoice created through the insurance workflow.

The invoice belongs to an insurance customer and contains
vehicle, labor, payment, and creator information.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"


class InsuranceInvoice(Base):
    __tablename__ = "insurance_invoices"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey(
            "insurance_customers.id"
        ),
        nullable=False,
    )

    plate_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    labor_charges: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.UNPAID,
    )

    created_by: Mapped[int] = mapped_column(
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )