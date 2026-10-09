from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import select
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction

def get_inventory(db: Session,
                  product_id: int,
                  warehouse_id: int):
    return db.scalar(select(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.warehouse_id == warehouse_id))

def get_inventory_by_id(db: Session,inventory_id: int):
    return db.scalar(select(Inventory).where(Inventory.id == inventory_id))


def get_inventory_list(
    db: Session,
    warehouse_id: int | None = None,
    product_id: int | None = None,
    low_stock: bool = False,
    out_of_stock: bool = False,
    page: int = 1,
    page_size: int = 20,
    sort_order: str = "asc"):
    query = db.query(Inventory)
    if warehouse_id is not None:
        query = query.filter(Inventory.warehouse_id == warehouse_id)
    if product_id is not None:
        query = query.filter(Inventory.product_id == product_id)
    # Low stock:
    # available <= reorder level
    if low_stock:
        query = query.filter(Inventory.available_quantity <= Inventory.reorder_level)
    # Out of stock
    if out_of_stock:
        query = query.filter(Inventory.available_quantity == 0)
    total = query.with_entities(func.count(Inventory.id)).scalar()
    if sort_order.lower() == "desc":
        query = query.order_by(Inventory.available_quantity.desc())
    else:
        query = query.order_by(Inventory.available_quantity.asc())
    offset = (page - 1) * page_size
    inventory = (query.offset(offset).limit(page_size).all())
    return inventory, total

def create_inventory(db: Session,
                     inventory: Inventory):
    db.add(inventory)
    db.flush()
    return inventory

def create_transaction( db: Session,
                       transaction: InventoryTransaction):
    db.add(transaction)
    db.flush()
    return transaction

def get_inventory_for_update(
    db: Session,
    product_id: int,
    warehouse_id: int):
    return db.scalar(select(Inventory).where(Inventory.product_id == product_id,
                                             Inventory.warehouse_id == warehouse_id)
                                             .with_for_update())