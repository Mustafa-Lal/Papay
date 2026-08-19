from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# --------------------------------------------------
# Profit Create
# --------------------------------------------------

class ProfitCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    amount: Decimal = Field(
        ge=0,
    )


# --------------------------------------------------
# Profit Update
# --------------------------------------------------

class ProfitUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    amount: Decimal | None = Field(
        default=None,
        ge=0,
    )


# --------------------------------------------------
# Profit Response
# --------------------------------------------------

class ProfitResponse(BaseModel):
    id: int
    name: str
    amount: Decimal
    created_at: datetime


# --------------------------------------------------
# Profit Pagination
# --------------------------------------------------

class ProfitPaginationResponse(BaseModel):
    limit: int
    offset: int
    total: int
    has_more: bool


# --------------------------------------------------
# Profit List Response
# --------------------------------------------------

class ProfitListResponse(BaseModel):
    profits: list[ProfitResponse]
    pagination: ProfitPaginationResponse