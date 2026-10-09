from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.notification import Notification

def create_notification(
    db: Session,
    user_id: int,
    message: str,
    notification_type
):
    notification = Notification(
        user_id=user_id,
        message=message,
        notification_type=notification_type,
        is_read=False,
    )

    db.add(notification)
    db.flush()

    return notification

def get_user_notifications(
    db: Session,
    user_id: int):
    return (db.scalars(select(Notification)
                       .where(Notification.user_id == user_id)
                       .order_by(Notification.created_at.desc())).all())

def get_notification(
    db: Session,
    notification_id: int):
    return (db.scalars(select(Notification)
        .where(Notification.id == notification_id))
        .first())