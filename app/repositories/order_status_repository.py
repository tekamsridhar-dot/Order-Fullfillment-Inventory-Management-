from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.order_status_history import OrderStatusHistory

def create_status_history(
    db: Session,
    order_id: int,
    changed_by_id: int,
    old_status: str,
    new_status: str):
    history = OrderStatusHistory(
        order_id=order_id,
        changed_by_id=changed_by_id,
        old_status=old_status,
        new_status=new_status)
    db.add(history)
    db.flush()
    return history

def get_order_status_history(
    db: Session,
    order_id: int):
    return (db.scalars(select(OrderStatusHistory)
            .where(OrderStatusHistory.order_id == order_id)
            .order_by(OrderStatusHistory.created_at.asc())).all())