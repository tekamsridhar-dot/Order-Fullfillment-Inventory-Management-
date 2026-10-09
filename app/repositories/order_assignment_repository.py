from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.order_assignment import OrderAssignment
from app.models.order import Order
from app.models.user import User
from app.schemas.enums import NotificationType
from app.services.notification_service import create_notification
from app.services.audit_service import record_audit


def create_assignment(
    db: Session,
    order_id: int,
    agent_id: int,
    assigned_by_id: int):
    # Get order
    order = db.scalar(select(Order).where(Order.id == order_id))
    if not order:
        raise ValueError("Order not found")
    # Get agent
    agent = db.scalar(select(User).where(User.id == agent_id))
    if not agent:
        raise ValueError("Agent not found")
    # Create assignment
    assignment = OrderAssignment(
        order_id=order_id,
        agent_id=agent_id,
        assigned_by_id=assigned_by_id)
    db.add(assignment)
    db.flush()
    create_notification(
        db=db,
        user_id=agent_id,
        message=f"Order {order.order_number} has been assigned to you.",
        notification_type=NotificationType.ORDER_ASSIGNED)
    record_audit(
    db=db,
    user_id=assigned_by_id,
    action="ORDER_ASSIGNED",
    entity="ORDER",
    entity_id=order_id,
    metadata={
        "agent_id": agent_id,
        "message": f"Order assigned to agent {agent_id}",
    },
)
    db.flush()
    return assignment

def get_current_assignment(
    db: Session,
    order_id: int):
    return (db.scalar(select(OrderAssignment)
            .where(OrderAssignment.order_id == order_id)
            .order_by(OrderAssignment.assigned_at.desc())))

def get_assignment_history(
    db: Session,
    order_id: int):
    return db.scalars(
            select(OrderAssignment)
            .where(OrderAssignment.order_id == order_id)
            .order_by(OrderAssignment.assigned_at.asc())).all()
    