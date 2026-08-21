from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access_key import AccessKey
from app.models.session import Session as AuthSession

def delete_access_key_by_id(db: Session, key_id: int) -> bool:
    """
    Delete an access key by its ID, and clean up any associated sessions.
    
    Returns:
        True if the key was found and deleted.
        False if the key was not found.
    """
    access_key = db.scalar(
        select(AccessKey).where(AccessKey.id == key_id)
    )

    if access_key is None:
        return False

    # Also delete any active sessions tied to this key
    sessions = db.scalars(
        select(AuthSession).where(AuthSession.access_key_id == key_id)
    ).all()

    for s in sessions:
        db.delete(s)

    db.delete(access_key)
    
    # We commit in the router
    return True
