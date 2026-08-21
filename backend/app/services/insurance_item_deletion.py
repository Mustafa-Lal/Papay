from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.insurance_item import InsuranceItem

def delete_insurance_item(db: Session, item_id: int) -> bool:
    item = db.scalar(select(InsuranceItem).where(InsuranceItem.id == item_id))
    
    if item is None:
        raise ValueError("Insurance item not found.")
        
    item.is_active = False
    return True
