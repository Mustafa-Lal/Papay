from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dependencies.auth import get_current_access_key, get_db
from app.dependencies.quota import require_db_quota
from app.models.access_key import AccessKey
from app.models.rent import Rent
from app.schemas.rent import RentCreate, RentResponse, RentUpdate
from app.services.rent import create_rent
from app.services.rent_deletion import delete_rent
from app.services.rent_fetch import get_rent
from app.services.rent_update import update_rent

router = APIRouter(prefix="/rent")

@router.post(
    "",
    response_model=RentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rent_endpoint(
    payload: RentCreate,
    db: Session = Depends(get_db),
    current_access_key: AccessKey = Depends(get_current_access_key),
    _quota: None = Depends(require_db_quota),
):
    try:
        rent = create_rent(
            db=db,
            amount=payload.amount,
            year=payload.year,
            month=payload.month,
            created_by=current_access_key.id,
        )
        db.commit()
        db.refresh(rent)
        return rent
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

@router.get("", response_model=list[RentResponse])
def list_rents_endpoint(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    rents = db.scalars(
        select(Rent)
        .order_by(Rent.year.desc(), Rent.month.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return rents

@router.get("/{year}/{month}", response_model=RentResponse)
def get_rent_endpoint(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        return get_rent(db=db, year=year, month=month)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

@router.put("/{rent_id}", response_model=RentResponse)
def update_rent_endpoint(
    rent_id: int,
    payload: RentUpdate,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        rent = update_rent(
            db=db,
            rent_id=rent_id,
            **payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(rent)
        return rent
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
            if str(error) == "Rent not found."
            else status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

@router.delete("/{rent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rent_endpoint(
    rent_id: int,
    db: Session = Depends(get_db),
    _: AccessKey = Depends(get_current_access_key),
):
    try:
        delete_rent(db=db, rent_id=rent_id)
        db.commit()
    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
