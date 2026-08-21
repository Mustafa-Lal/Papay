from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.mechanic_item import MechanicItem

def delete_mechanic_item(db: Session, item_id: int) -> bool:
    item = db.scalar(select(MechanicItem).where(MechanicItem.id == item_id))
    
    if item is None:
        raise ValueError("Mechanic item not found.")
        
    item.is_active = False
    return True
