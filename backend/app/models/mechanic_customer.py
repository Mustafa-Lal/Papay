from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MechanicCustomer(Base):
    __tablename__ = "mechanic_customers"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    customer_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    qid: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
