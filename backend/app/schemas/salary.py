from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# --------------------------------------------------
# Salary Create
# --------------------------------------------------

class SalaryCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    amount: Decimal = Field(
        ge=0,
    )


# --------------------------------------------------
# Salary Update
# --------------------------------------------------

class SalaryUpdate(BaseModel):
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
# Salary Response
# --------------------------------------------------

class SalaryResponse(BaseModel):
    id: int
    name: str
    amount: Decimal
    created_at: datetime


# --------------------------------------------------
# Salary Pagination
# --------------------------------------------------

class SalaryPaginationResponse(BaseModel):
    limit: int
    offset: int
    total: int
    has_more: bool


# --------------------------------------------------
# Salary List Response
# --------------------------------------------------

class SalaryListResponse(BaseModel):
    salaries: list[SalaryResponse]
    pagination: SalaryPaginationResponse