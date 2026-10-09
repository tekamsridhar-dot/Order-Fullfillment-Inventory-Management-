from sqlalchemy.orm import Session

from app.models.order import Order

def get_order(
    db: Session,
    order_id: int,
    for_update: bool = False):
    query = db.query(Order).filter( Order.id == order_id)
    if for_update:
        query = query.with_for_update()
    return query.first()