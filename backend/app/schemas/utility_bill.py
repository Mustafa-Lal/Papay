from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


# --------------------------------------------------
# Utility Bill Type
# --------------------------------------------------

class UtilityBillType(str, Enum):
    ELECTRICITY = "ELECTRICITY"
    WATER = "WATER"
    INTERNET = "INTERNET"


# --------------------------------------------------
# Utility Bill Create
# --------------------------------------------------

class UtilityBillCreate(BaseModel):
    bill_type: UtilityBillType

    amount: Decimal = Field(
        ge=0,
    )

    year: int

    month: int = Field(
        ge=1,
        le=12,
    )


# --------------------------------------------------
# Utility Bill Update
# --------------------------------------------------

class UtilityBillUpdate(BaseModel):
    bill_type: UtilityBillType | None = None

    amount: Decimal | None = Field(
        default=None,
        ge=0,
    )

    year: int | None = None

    month: int | None = Field(
        default=None,
        ge=1,
        le=12,
    )


# --------------------------------------------------
# Utility Bill Response
# --------------------------------------------------

class UtilityBillResponse(BaseModel):
    id: int
    bill_type: UtilityBillType
    amount: Decimal
    year: int
    month: int


# --------------------------------------------------
# Utility Bills Response
# --------------------------------------------------

class UtilityBillsResponse(BaseModel):
    bills: list[UtilityBillResponse]