from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import PaymentStatus

class PaymentConfirmRequest(BaseModel):
    payment_reference: str

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    payment_status: PaymentStatus
    payment_reference: str | None = None
    paid_at: datetime | None = None