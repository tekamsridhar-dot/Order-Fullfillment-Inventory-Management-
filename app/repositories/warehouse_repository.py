from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.warehouse import Warehouse
from app.models.warehouse_user import WarehouseUser


def get_warehouse_by_id(db: Session,
                        warehouse_id: int):
    return (db.scalar(select(Warehouse).where(Warehouse.id == warehouse_id)))


def get_warehouse_by_name(db: Session,
                          name: str):
    return (db.scalar(select(Warehouse).where(Warehouse.name == name)))

def get_warehouses(db: Session,
                   skip: int = 0,
                   limit: int = 20):
    return db.scalars(select(Warehouse).order_by(Warehouse.id.desc()).
                      offset(skip).limit(limit)).all()

def get_user_warehouse(db: Session,user_id: int,
                       warehouse_id: int):
    return (db.scalar(select(WarehouseUser).filter(
            WarehouseUser.user_id == user_id,
            WarehouseUser.warehouse_id == warehouse_id,)))

def get_user_warehouses(db: Session,
                        user_id: int):
    return db.scalars(select(Warehouse).join(WarehouseUser,
            WarehouseUser.warehouse_id == Warehouse.id)
        .filter(
            WarehouseUser.user_id == user_id)
        .order_by(Warehouse.id.desc())
        .all())

def get_user_warehouse_ids(
    db: Session,
    user_id: int,
):
    rows = (
        db.query(WarehouseUser.warehouse_id)
        .filter(
            WarehouseUser.user_id == user_id
        )
        .all()
    )

    return [row[0] for row in rows]