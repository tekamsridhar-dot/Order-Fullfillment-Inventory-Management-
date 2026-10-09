from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.exceptions import ForbiddenException
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_user import WarehouseUser
from app.repositories.warehouse_repository import (get_warehouse_by_id,get_warehouse_by_name,
                                                   get_warehouses,get_user_warehouse)
from app.schemas.warehouse import (WarehouseCreate,WarehouseUpdate)

def create_new_warehouse(db: Session,data: WarehouseCreate):
    existing = get_warehouse_by_name(db,data.name)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
            detail={"code": "DUPLICATE_WAREHOUSE",
                    "message": "Warehouse name already exists"})
    warehouse = Warehouse(
        name=data.name,
        location=data.location,
        capacity=data.capacity,
        is_active=True)
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse

def get_warehouse(db: Session,warehouse_id: int):
    warehouse = get_warehouse_by_id(db,warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": "WAREHOUSE_NOT_FOUND",
                                    "message": "Warehouse not found"})
    return warehouse

def list_warehouses(
    db: Session,
    skip: int = 0,
    limit: int = 20):
    return get_warehouses(
        db,
        skip=skip,
        limit=limit)

def update_warehouse(
    db: Session,
    warehouse_id: int,
    data: WarehouseUpdate):
    warehouse = get_warehouse(db,warehouse_id)
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        existing = get_warehouse_by_name(db,update_data["name"])
        if existing and existing.id != warehouse.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail={"code": "DUPLICATE_WAREHOUSE",
                        "message": "Warehouse name already exists",})
    for field, value in update_data.items():
        setattr(warehouse,field,value)
    db.commit()
    db.refresh(warehouse)
    return warehouse

def activate_warehouse(
    db: Session,
    warehouse_id: int):
    warehouse = get_warehouse(db,warehouse_id)
    warehouse.is_active = True
    db.commit()
    db.refresh(warehouse)
    return warehouse

def deactivate_warehouse(db: Session,warehouse_id: int):
    warehouse = get_warehouse(db,warehouse_id)
    warehouse.is_active = False
    db.commit()
    db.refresh(warehouse)
    return warehouse

def assign_user_to_warehouse(db: Session,
                             user_id: int,
                             warehouse_id: int):
    warehouse = get_warehouse(db,warehouse_id)
    existing = get_user_warehouse(db,user_id,warehouse_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"code": "ALREADY_ASSIGNED",
                                    "message": "User is already assigned to this warehouse"})
    assignment = WarehouseUser(user_id=user_id,warehouse_id=warehouse.id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

def verify_warehouse_access(db: Session,user: User,warehouse_id: int):
    # Admin has access to all warehouses
    if user.role.name == "admin":
        return get_warehouse(db,warehouse_id,)
    assignment = get_user_warehouse(db,user.id,warehouse_id,)
    if assignment is None:
        raise ForbiddenException(code="WAREHOUSE_ACCESS_DENIED",
                                 message="You are not authorized for this warehouse")
    return get_warehouse(db,warehouse_id)