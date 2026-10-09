from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.return_model import Return
from app.models.return_item import ReturnItem
from app.schemas.enums import NotificationType
from app.services.notification_service import send_notification,create_notification
from app.services.audit_service import record_audit
from app.repositories.return_repository import (create_return,create_return_item,
                                                get_return_by_id,get_returns)
from app.services.return_state_machine import validate_return_transition
from app.core.exceptions import ConflictException

def create_customer_return(
    db: Session,
    customer_id: int,
    order_id: int,
    reason: str,
    items):
    order = db.scalar(select(Order).where(Order.id == order_id))
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")
    if order.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized for this order")
    if order.status != "delivered":
        raise ConflictException(code="RETURN_NOT_ALLOWED",
                            message="Return can only be requested for delivered orders")
    return_obj = Return(
        order_id=order.id,
        customer_id=customer_id,
        status="requested",
        reason=reason)
    db.add(return_obj)
    db.flush()
    for item in items:
        order_item = db.scalar(
            select(OrderItem).where(
                OrderItem.id == item.order_item_id,
                OrderItem.order_id == order.id))
        if not order_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Order item {item.order_item_id} not found")
        if item.quantity > order_item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail=(f"Return quantity cannot exceed "
                        f"ordered quantity for item {order_item.id}"))
        return_item = ReturnItem(
            return_id=return_obj.id,
            order_item_id=order_item.id,
            quantity=item.quantity)
        db.add(return_item)
    create_notification(
    db=db,
    user_id=order.customer_id,
    message=f"Return requested for order {order.order_number}.",
    notification_type=NotificationType.RETURN_REQUESTED)
    send_notification(
        db=db,
        user_id=customer_id,
        notification_type="RETURN_REQUESTED",
        message=f"Return request {return_obj.id} has been created.")
    record_audit(
        db=db,
        user_id=customer_id,
        action="RETURN_CREATED",
        entity="return",
        entity_id=return_obj.id,
        metadata={"order_id": order_id,
                  "reason": reason})
    db.commit()
    db.refresh(return_obj)
    return return_obj

def update_return_status(
    db: Session,
    return_id: int,
    new_status: str,
    current_user):
    return_obj = get_return_by_id(db=db,return_id=return_id)
    if not return_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Return not found")
    old_status = return_obj.status
    validate_return_transition(current_status=old_status,
                               new_status=new_status)
    return_obj.status = new_status
    create_notification(
    db=db,
    user_id=return_obj.order.customer_id,
    message="Your return request has been approved.",
    notification_type=NotificationType.RETURN_APPROVED,)
    record_audit(
    db=db,
    user_id=current_user.id,
    action="RETURN_APPROVED",
    entity="RETURN",
    entity_id=return_obj.id,
    metadata={
        "message": "Return request approved"
    },
)
    db.flush()
    return return_obj