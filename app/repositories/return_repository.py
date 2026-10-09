from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.return_model import Return
from app.models.return_item import ReturnItem

def create_return(db: Session,
                  return_obj: Return):
    db.add(return_obj)
    db.flush()
    return return_obj

def create_return_item(db: Session,
                       return_item: ReturnItem):
    db.add(return_item)
    db.flush()
    return return_item

def get_return_by_id(db: Session,
                     return_id: int):
    return db.scalars(select(Return).where(Return.id == return_id)).first()

def get_returns(
    db: Session,
    customer_id: int | None = None,
    status_filter: str | None = None):

    query = select(Return)

    if customer_id is not None:
        query = query.where(Return.customer_id == customer_id)
    if status_filter is not None:
        query = query.where(Return.status == status_filter)
    query = query.order_by(Return.id.desc())
    return db.scalars(query).all()