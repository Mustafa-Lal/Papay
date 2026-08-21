from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_access_key, get_db
from app.dependencies.quota import require_db_quota
from app.models.access_key import AccessKey
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseUpdate,
)
from app.services.expense import create_expense
from app.services.expense_deletion import deactivate_expense
from app.services.expense_fetch import get_expenses
from app.services.expense_update import update_expense

router = APIRouter(prefix="/expenses")


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense_endpoint(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        expense = create_expense(
            db=db,
            description=payload.description,
            amount=payload.amount,
            created_by=current_access_key.id,
        )
        db.commit()
        db.refresh(expense)
        return expense
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("", response_model=ExpenseListResponse)
def list_expenses_endpoint(
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        return get_expenses(
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


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense_endpoint(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        expense = update_expense(
            db=db,
            expense_id=expense_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(expense)
        return expense
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Expense not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense_endpoint(
    expense_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        deactivate_expense(db=db, expense_id=expense_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
