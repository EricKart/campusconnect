from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Notification, User
from ..schemas import NotificationOut
from ..security import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationOut])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notes = (
        db.query(Notification)
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    # Reading the list marks everything as read -- simplest possible model,
    # matching how a lot of real notification bells behave on open.
    unread = [n for n in notes if not n.is_read]
    for note in unread:
        note.is_read = True
    if unread:
        db.commit()
    return notes
