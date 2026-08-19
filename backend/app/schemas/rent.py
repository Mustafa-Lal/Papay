from decimal import Decimal

from pydantic import BaseModel, Field


# --------------------------------------------------
# Rent Create
# --------------------------------------------------

class RentCreate(BaseModel):
    amount: Decimal = Field(
        ge=0,
    )

    year: int = Field(
        ge=2000,
    )

    month: int = Field(
        ge=1,
        le=12,
    )


# --------------------------------------------------
# Rent Update
# --------------------------------------------------

class RentUpdate(BaseModel):
    amount: Decimal | None = Field(
        default=None,
        ge=0,
    )

    year: int | None = Field(
        default=None,
        ge=2000,
    )

    month: int | None = Field(
        default=None,
        ge=1,
        le=12,
    )


# --------------------------------------------------
# Rent Response
# --------------------------------------------------

class RentResponse(BaseModel):
    id: int
    amount: Decimal
    year: int
    month: int