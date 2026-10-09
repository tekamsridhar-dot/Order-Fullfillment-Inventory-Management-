from datetime import datetime, time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.inventory import Inventory

def count_orders(
    db: Session,
    status: str | None = None):
    query = select(func.count(Order.id))
    if status:
        query = query.where( Order.status == status)
    return db.scalar(query) or 0

def calculate_revenue(db: Session):
    query = select(
        func.coalesce(
            func.sum(Order.total_amount),
            0
        )
    ).where(
        Order.status == "delivered"
    )

    return db.scalar(query) or 0

def count_low_stock(db: Session):
    query = select(
        func.count(Inventory.id)
    ).where(
        Inventory.available_quantity
        <= Inventory.reorder_level
    )
    return db.scalar(query) or 0

def count_out_of_stock(db: Session):
    query = select(
        func.count(Inventory.id)
    ).where(
        Inventory.available_quantity == 0
    )
    return db.scalar(query) or 0

def get_admin_dashboard(db: Session):
    return {
        "total_orders": count_orders(db),

        "pending_orders": count_orders(
            db,
            "pending",
        ),

        "processing_orders": count_orders(
            db,
            "processing",
        ),

        "completed_orders": count_orders(
            db,
            "delivered",
        ),

        "cancelled_orders": count_orders(
            db,
            "cancelled",
        ),

        "total_revenue": calculate_revenue(db),

        "low_stock_products": count_low_stock(db),

        "out_of_stock_products": count_out_of_stock(db),
    }

def count_todays_shipments(
    db: Session,
    warehouse_id: int,
):
    today = datetime.now().date()

    start = datetime.combine(
        today,
        time.min,
    )

    end = datetime.combine(
        today,
        time.max,
    )

    query = select(
        func.count(Order.id)
    ).where(
        Order.warehouse_id == warehouse_id,
        Order.status == "shipped",
        Order.updated_at >= start,
        Order.updated_at <= end,
    )

    return db.scalar(query) or 0

def get_warehouse_dashboard(
    db: Session,
    warehouse_id: int):

    warehouse_inventory = db.scalar(
        select(func.count(Inventory.id))
        .where(
            Inventory.warehouse_id == warehouse_id
        )
    ) or 0
    pending_fulfillment = db.scalar(
        select(func.count(Order.id))
        .where(
            Order.warehouse_id == warehouse_id,
            Order.status == "confirmed",
        )
    ) or 0
    processing_orders = db.scalar(
        select(func.count(Order.id))
        .where(
            Order.warehouse_id == warehouse_id,
            Order.status == "processing",
        )
    ) or 0
    low_stock_items = db.scalar(
        select(func.count(Inventory.id))
        .where(
            Inventory.warehouse_id == warehouse_id,
            Inventory.available_quantity
            <= Inventory.reorder_level,
        )
    ) or 0
    todays_shipments = count_todays_shipments(db,warehouse_id)

    return {
        "warehouse_id": warehouse_id,
        "inventory_items": warehouse_inventory,
        "pending_fulfillment": pending_fulfillment,
        "processing_orders": processing_orders,
        "low_stock_items": low_stock_items,
        "todays_shipments": todays_shipments,
    }

def get_customer_dashboard(
    db: Session,
    customer_id: int,
):
    total_orders = db.scalar(
        select(func.count(Order.id))
        .where(
            Order.customer_id == customer_id
        )
    ) or 0
    active_orders = db.scalar(
        select(func.count(Order.id))
        .where(
            Order.customer_id == customer_id,
            Order.status.in_([
                "pending",
                "confirmed",
                "allocated",
                "processing",
                "packed",
                "shipped",
            ]),
        )
    ) or 0

    completed_orders = db.scalar(
        select(func.count(Order.id))
        .where(
            Order.customer_id == customer_id,
            Order.status == "delivered",
        )
    ) or 0

    cancelled_orders = db.scalar(
        select(func.count(Order.id))
        .where(
            Order.customer_id == customer_id,
            Order.status == "cancelled",
        )
    ) or 0

    total_spending = db.scalar(
        select(
            func.coalesce(
                func.sum(Order.total_amount),
                0,
            )
        )
        .where(
            Order.customer_id == customer_id,
            Order.status == "delivered",
        )
    ) or 0

    return {
        "total_orders": total_orders,
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "total_spending": total_spending,
    }