from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.repositories.notification_repository import (create_notification,
                                                      get_user_notifications,
                                                      get_notification)

def send_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    message: str):
    return create_notification(
        db=db,
        user_id=user_id,
        notification_type=notification_type,
        message=message)

def list_notifications(
    db: Session,
    user_id: int):
    return get_user_notifications(
        db=db,
        user_id=user_id)

def mark_notification_read(
    db: Session,
    notification_id: int,
    user_id: int):
    notification = get_notification(
        db=db,
        notification_id=notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Notification not found")
    if notification.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to update this notification",)
    notification.is_read = True
    db.flush()
    return notification

def mark_all_notifications_read(
    db: Session,
    user_id: int):
    db.scalars(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,).update(
            {Notification.is_read: True},synchronize_session=False,)
    db.flush()


def create_notification(
    db: Session,
    user_id: int,
    message: str,
    notification_type):
    notification = Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
        is_read=False)
    db.add(notification)
    db.flush()
    return notification