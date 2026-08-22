from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_access_key, get_db
from app.dependencies.quota import require_db_quota
from app.models.access_key import AccessKey
from app.models.utility_bill import UtilityBillType as ModelUtilityBillType
from app.schemas.utility_bill import (
    UtilityBillCreate,
    UtilityBillResponse,
    UtilityBillUpdate,
    UtilityBillsResponse,
)
from app.services.utility_bill import create_utility_bill
from app.services.utility_bill_deletion import delete_utility_bill
from app.services.utility_bill_fetch import get_utility_bills
from app.services.utility_bill_update import update_utility_bill

router = APIRouter(prefix="/utility-bills")


@router.post(
    "",
    response_model=UtilityBillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_utility_bill_endpoint(
    payload: UtilityBillCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        # Convert schema enum to model enum
        bill_type = ModelUtilityBillType(payload.bill_type.value)
        bill = create_utility_bill(
            db=db,
            bill_type=bill_type,
            amount=payload.amount,
            year=payload.year,
            month=payload.month,
            created_by=current_access_key.id,
        )
        db.commit()
        db.refresh(bill)
        return bill
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/{year}/{month}", response_model=UtilityBillsResponse)
def get_utility_bills_endpoint(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        bills = get_utility_bills(db=db, year=year, month=month)
        return {"bills": bills}
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.put("/{bill_id}", response_model=UtilityBillResponse)
def update_utility_bill_endpoint(
    bill_id: int,
    payload: UtilityBillUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        update_data = payload.model_dump(exclude_unset=True)
        # Convert schema bill_type to model bill_type if present
        if "bill_type" in update_data:
            update_data["bill_type"] = ModelUtilityBillType(update_data["bill_type"])
        bill = update_utility_bill(db=db, bill_id=bill_id, **update_data)
        db.commit()
        db.refresh(bill)
        return bill
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Utility bill not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{bill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_utility_bill_endpoint(
    bill_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        delete_utility_bill(db=db, bill_id=bill_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
