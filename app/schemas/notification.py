from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import NotificationType

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    notification_type: NotificationType
    message: str
    is_read: bool
    created_at: datetime

class NotificationReadResponse(BaseModel):
    message: str = "Notification marked as read"