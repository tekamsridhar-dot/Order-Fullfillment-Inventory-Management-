from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.exceptions import (BadRequestException,ConflictException,NotFoundException)
from app.schemas.enums import PaymentStatus
from app.repositories.payment_repository import get_order

def confirm_payment(
    db: Session,
    order_id: int,
    payment_reference: str):
    order = get_order(db,order_id,for_update=True)
    if not order:
        raise NotFoundException("Order not found")
    if order.payment_status == PaymentStatus.PAID:
        if order.payment_reference == payment_reference:
            return order
        raise ConflictException("Order has already been paid")
    if order.payment_status == PaymentStatus.REFUNDED:
        raise ConflictException("Refunded order cannot be paid again")
    if order.payment_status == PaymentStatus.FAILED:
        raise BadRequestException("Payment is in failed state")
    order.payment_status = PaymentStatus.PAID
    order.payment_reference = payment_reference
    order.paid_at = datetime.now(timezone.utc)
    db.flush()
    return order