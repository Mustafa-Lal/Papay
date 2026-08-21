from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_access_key, get_db
from app.dependencies.quota import require_db_quota
from app.models.access_key import AccessKey
from app.schemas.profit import (
    ProfitCreate,
    ProfitListResponse,
    ProfitResponse,
    ProfitUpdate,
)
from app.services.profit import create_profit
from app.services.profit_deletion import deactivate_profit
from app.services.profit_fetch import get_profits
from app.services.profit_update import update_profit

router = APIRouter(prefix="/profits")


@router.post(
    "",
    response_model=ProfitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profit_endpoint(
    payload: ProfitCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        profit = create_profit(
            db=db,
            name=payload.name,
            amount=payload.amount,
            created_by=current_access_key.id,
        )
        db.commit()
        db.refresh(profit)
        return profit
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("", response_model=ProfitListResponse)
def list_profits_endpoint(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        return get_profits(
            db=db,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put("/{profit_id}", response_model=ProfitResponse)
def update_profit_endpoint(
    profit_id: int,
    payload: ProfitUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        profit = update_profit(
            db=db,
            profit_id=profit_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(profit)
        return profit
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Profit not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{profit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profit_endpoint(
    profit_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        deactivate_profit(db=db, profit_id=profit_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
