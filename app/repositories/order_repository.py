from sqlalchemy.orm import Session
from app.models.order import Order
from sqlalchemy import select
from sqlalchemy import func

def create_order(db: Session, order: Order):
    db.add(order)
    db.flush()
    return order

def get_order_by_id(db: Session, order_id: int):
    return db.scalar(select(Order).where(Order.id == order_id))

def get_orders(
    db: Session,
    customer_id: int | None = None,
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
    query = db.query(Order)

    # Customer filter
    if customer_id is not None:
        query = query.filter(Order.customer_id == customer_id)
    # Warehouse filter
    if warehouse_id is not None:
        query = query.filter(Order.warehouse_id == warehouse_id)
    # Status filter
    if status is not None:
        query = query.filter(Order.status == status)
    # Payment status
    if payment_status is not None:
        query = query.filter(Order.payment_status == payment_status)
    # Minimum total
    if min_total is not None:
        query = query.filter(Order.total_amount >= min_total)
    # Maximum total
    if max_total is not None:
        query = query.filter(Order.total_amount <= max_total)
    # Date range
    if date_from is not None:
        query = query.filter(Order.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Order.created_at <= date_to)
    # Total before pagination
    total = query.with_entities(func.count(Order.id)).scalar()
    # Sorting
    allowed_sort_fields = {
        "created_at": Order.created_at,
        "total_amount": Order.total_amount,
        "status": Order.status,}
    sort_column = allowed_sort_fields.get(
        sort_by,
        Order.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    # Pagination
    offset = (page - 1) * page_size
    orders = (
        query
        .offset(offset)
        .limit(page_size)
        .all())
    return orders, total