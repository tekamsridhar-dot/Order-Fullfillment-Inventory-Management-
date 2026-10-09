from decimal import Decimal
from uuid import uuid4
import math

from fastapi import HTTPException, status,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.dependencies import get_db
from app.core.exceptions import (BadRequestException,NotFoundException)
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.user import User
from app.models.warehouse_user import WarehouseUser
from app.models.order_item import OrderItem
from app.schemas.enums import NotificationType,OrderStatus
from app.services.notification_service import send_notification,create_notification
from app.services.audit_service import record_audit
from app.services.inventory_service import release_inventory,reserve_inventory
from app.repositories.order_assignment_repository import (create_assignment,
                                                          get_current_assignment,
                                                          get_assignment_history)
from app.repositories.order_repository import (create_order,get_order_by_id,get_orders)
from app.repositories.order_status_repository import create_status_history,get_order_status_history
from app.services.order_state_machine import validate_order_transition

def generate_order_number() -> str:
    return f"ORD-{uuid4().hex[:12].upper()}"

def create_customer_order(
    db: Session,
    customer_id: int,
    warehouse_id: int,
    items,
    current_user=None,
    expected_delivery_date=None,
):
    warehouse = db.scalar(
        select(Warehouse).where(
            Warehouse.id == warehouse_id
        )
    )

    if not warehouse:
        raise NotFoundException(
            code="WAREHOUSE_NOT_FOUND",
            message="Warehouse not found",
        )

    if not warehouse.is_active:
        raise BadRequestException(
            code="WAREHOUSE_INACTIVE",
            message=f"Warehouse {warehouse.name} is inactive",
        )

    product_ids = [item.product_id for item in items]

    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate products are not allowed in the same order",
        )

    order = Order(
        order_number=generate_order_number(),
        customer_id=customer_id,
        warehouse_id=warehouse_id,
        total_amount=Decimal("0.00"),
        status="pending",
        payment_status="pending",
        expected_delivery_date=expected_delivery_date,
    )

    create_order(db, order)

    total_amount = Decimal("0.00")

    for item in items:

        product = db.scalar(
            select(Product).where(
                Product.id == item.product_id
            )
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found",
            )

        if not product.is_active:
            raise BadRequestException(
                code="PRODUCT_INACTIVE",
                message=f"Product {product.sku} is inactive",
            )

        unit_price = Decimal(str(product.price))
        quantity = item.quantity

        discount = Decimal(str(item.discount))
        tax = Decimal(str(item.tax))

        line_total = (
            unit_price * quantity
        ) - discount + tax

        reserve_inventory(
    db=db,
    product_id=product.id,
    warehouse_id=warehouse_id,
    quantity=quantity,
    order_id=order.id,
    user_id=current_user.id,
    reference_entity="order",
    reference_id=order.id,)

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            discount=discount,
            tax=tax,
            total=line_total,
        )

        db.add(order_item)

        total_amount += line_total

    order.total_amount = total_amount

    create_notification(
        db=db,
        user_id=customer_id,
        message=(
            f"Your order {order.order_number} "
            "has been created successfully."
        ),
        notification_type=NotificationType.ORDER_CREATED,
    )

    record_audit(
    db=db,
    user_id=customer_id,
    action="ORDER_CREATED",
    entity="ORDER",
    entity_id=order.id,
    metadata={
        "message": f"Order {order.order_number} created",
        "order_number": order.order_number,
        "total_amount": str(order.total_amount),
    },
)
    db.flush()
    return order

def update_order_status(
    db: Session,
    order_id: int,
    new_status: str,
    changed_by_id: int,
    current_user:None
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    old_status = order.status

    validate_order_transition(
        current_status=old_status,
        new_status=new_status,
    )

    order.status = new_status

    create_status_history(
        db=db,
        order_id=order.id,
        changed_by_id=changed_by_id,
        old_status=old_status,
        new_status=new_status,
    )

    notification_map = {
        OrderStatus.CONFIRMED: (
            "Order Confirmed",
            f"Order {order.order_number} has been confirmed.",
            NotificationType.ORDER_CONFIRMED,
        ),
        OrderStatus.SHIPPED: (
            "Order Shipped",
            f"Order {order.order_number} has been shipped.",
            NotificationType.ORDER_SHIPPED,
        ),
        OrderStatus.DELIVERED: (
            "Order Delivered",
            f"Order {order.order_number} has been delivered.",
            NotificationType.ORDER_DELIVERED,
        ),
    }

    if new_status in notification_map:
        title, message, notification_type = notification_map[
            new_status
        ]

        create_notification(
            db=db,
            user_id=order.customer_id,
            message=message,
            notification_type=notification_type,
        )
        record_audit(
    db=db,
    user_id=current_user.id,
    action="ORDER_STATUS_CHANGED",
    entity="ORDER",
    entity_id=order.id,
    metadata={
        "old_status": old_status,
        "new_status": new_status,
        "message": (
            f"Order status changed "
            f"from {old_status} to {new_status}")})

    db.flush()

    return order

def assign_order(
    db: Session,
    order_id: int,
    agent_id: int,
    assigned_by_id: int):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")
    agent = db.scalar(select(User).where(User.id == agent_id))
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Fulfillment agent not found")
    if not agent.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Inactive agent cannot receive orders")
    if agent.role.name != "fulfillment_agent":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Selected user is not a fulfillment agent")
    warehouse_assignment = db.scalar(select(WarehouseUser).where(
            WarehouseUser.user_id == agent_id,
            WarehouseUser.warehouse_id == order.warehouse_id))
    if not warehouse_assignment:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Agent is not authorized for this warehouse")
    current_assignment = get_current_assignment(db,order_id)
    if (current_assignment
        and current_assignment.agent_id == agent_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Order is already assigned to this agent")
    assignment = create_assignment(
        db=db,
        order_id=order_id,
        agent_id=agent_id,
        assigned_by_id=assigned_by_id)
    send_notification(
    db=db,
    user_id=agent_id,
    notification_type="ORDER_ASSIGNED",
    message=f"Order {order.order_number} has been assigned to you.")
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

def cancel_order(
    db: Session,
    order_id: int,
    cancelled_by_id: int):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")
    cancellable_statuses = {
        "pending",
        "confirmed",
        "processing"}
    if order.status not in cancellable_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=(f"Order cannot be cancelled "
                                    f"from status '{order.status}'"))
    for item in order.items:
        release_inventory(
            db=db,
            product_id=item.product_id,
            warehouse_id=order.warehouse_id,
            quantity=item.quantity,
            reference_entity="order",
            reference_id=order.id)
    old_status = order.status
    order.status = "cancelled"
    create_status_history(
        db=db,
        order_id=order.id,
        changed_by_id=cancelled_by_id,
        old_status=old_status,
        new_status="cancelled")
    create_notification(
    db=db,
    user_id=order.customer_id,
    message=f"Order {order.order_number} has been cancelled.",
    notification_type=NotificationType.ORDER_CANCELLED)
    send_notification(
    db=db,
    user_id=order.customer_id,
    notification_type="ORDER_CANCELLED",
    message=f"Your order {order.order_number} has been cancelled.")
    record_audit(
    db=db,
    user_id=cancelled_by_id,
    action="ORDER_CANCELLED",
    entity="order",
    entity_id=order.id,
    metadata={
        "order_number": order.order_number,
        "previous_status": old_status})
    db.flush()
    return order

def list_customer_orders(
    db: Session,
    customer_id: int,
    warehouse_id: int | None = None,
    status: str | None = None,
    payment_status: str | None = None,
    min_total: float | None = None,
    max_total: float | None = None,
    date_from=None,
    date_to=None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc"):
    orders, total = get_orders(
        db=db,
        customer_id=customer_id,
        warehouse_id=warehouse_id,
        status=status,
        payment_status=payment_status,
        min_total=min_total,
        max_total=max_total,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order)
    total_pages = math.ceil(total / page_size) if total else 0
    return {
        "items": orders,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages}}