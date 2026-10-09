from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.auth import get_current_user
from app.schemas.payment import (PaymentConfirmRequest,PaymentResponse)
from app.services.payment_service import confirm_payment

router = APIRouter(prefix="/api/payments",
                   tags=["Payments"])

@router.post("/{order_id}/confirm",
             response_model=PaymentResponse)
def confirm_order_payment(
    order_id: int,
    payload: PaymentConfirmRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)):
    order = confirm_payment(
        db=db,
        order_id=order_id,
        payment_reference=payload.payment_reference)
    db.commit()
    return PaymentResponse(
        order_id=order.id,
        payment_status=order.payment_status,
        payment_reference=order.payment_reference,
        paid_at=order.paid_at)