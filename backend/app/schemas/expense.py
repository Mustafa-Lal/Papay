from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# --------------------------------------------------
# Expense Create
# --------------------------------------------------

class ExpenseCreate(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=500,
    )

    amount: Decimal = Field(
        ge=0,
    )


# --------------------------------------------------
# Expense Update
# --------------------------------------------------

class ExpenseUpdate(BaseModel):
    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    amount: Decimal | None = Field(
        default=None,
        ge=0,
    )


# --------------------------------------------------
# Expense Response
# --------------------------------------------------

class ExpenseResponse(BaseModel):
    id: int
    description: str
    amount: Decimal
    created_at: datetime


# --------------------------------------------------
# Expense Pagination
# --------------------------------------------------

class ExpensePaginationResponse(BaseModel):
    limit: int
    offset: int
    total: int
    has_more: bool


# --------------------------------------------------
# Expense List Response
# --------------------------------------------------

class ExpenseListResponse(BaseModel):
    expenses: list[ExpenseResponse]
    pagination: ExpensePaginationResponse