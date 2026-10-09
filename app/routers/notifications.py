from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import (list_notifications,mark_notification_read,
                                               mark_all_notifications_read)

router = APIRouter(prefix="/api/notifications",
                   tags=["Notifications"])

@router.get("",response_model=list[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return list_notifications(db=db,user_id=current_user.id)

@router.patch("/{notification_id}/read",response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        notification = mark_notification_read(
            db=db,
            notification_id=notification_id,
            user_id=current_user.id)
        db.commit()
        db.refresh(notification)
        return notification
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to mark notification as read")

@router.patch("/read-all",)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        mark_all_notifications_read(
            db=db,
            user_id=current_user.id)
        db.commit()
        return {"message": "All notifications marked as read"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to update notifications")