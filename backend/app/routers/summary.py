"""
Monthly financial summary router.

Routes:
    GET /summary/{year}/{month}  — Returns a full financial breakdown for
                                   the given month. Owner-only.

Only OWNER-role sessions are allowed to access this endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_db, require_owner
from app.models.access_key import AccessKey
from app.schemas.summary import MonthlySummaryResponse
from app.services.monthly_summary import get_monthly_summary

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get(
    "/{year}/{month}",
    response_model=MonthlySummaryResponse,
)
def monthly_summary_endpoint(
    year: int = Path(..., ge=2000, le=2100, description="4-digit year, e.g. 2026"),
    month: int = Path(..., ge=1, le=12, description="Month number 1–12"),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(require_owner),
):
    """
    Return a full financial summary for the specified month.

    Includes:
    - Insurance invoice profit (paid/unpaid split)
    - Mechanic invoice profit (labor + commissions only; paid/unpaid split)
    - Parts profit from garage records
    - Product expense
    - Rent expense
    - Utility bill expense (per type + total)
    - Salary expense (per employee + total)
    - Garage expense from garage records
    - Grand totals and net figure
    """
    try:
        return get_monthly_summary(db=db, year=year, month=month)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute summary: {exc}",
        ) from exc
