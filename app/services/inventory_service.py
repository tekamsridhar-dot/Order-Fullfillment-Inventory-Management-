from fastapi import HTTPException, status
import math
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.exceptions import (BadRequestException,NotFoundException)
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.services.inventory_alert_service import check_low_stock
from app.repositories.inventory_repository import (get_inventory,get_inventory_list,
                                                   get_inventory_for_update,create_inventory,create_transaction)
from app.schemas.inventory import InventoryAdjustmentRequest
from app.schemas.enums import NotificationType
from app.repositories.notification_repository import create_notification
from app.services.audit_service import record_audit

def get_inventory_item(
    db: Session,
    product_id: int,
    warehouse_id: int):
    inventory = get_inventory(
        db,
        product_id,
        warehouse_id)
    if inventory is None:
        raise NotFoundException(code="INVENTORY_NOT_FOUND",
                                message="Inventory record not found")
    return inventory

def list_inventory_paginated(
    db: Session,
    warehouse_id: int | None = None,
    product_id: int | None = None,
    low_stock: bool = False,
    out_of_stock: bool = False,
    page: int = 1,
    page_size: int = 20,
    sort_order: str = "asc"):
    inventory, total = get_inventory_list(
        db=db,
        warehouse_id=warehouse_id,
        product_id=product_id,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        page=page,
        page_size=page_size,
        sort_order=sort_order)

    total_pages = math.ceil(total / page_size) if total else 0
    return {
        "items": inventory,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages}}

def adjust_inventory(
    db: Session,
    data: InventoryAdjustmentRequest,
    user_id: int):
    inventory = get_inventory(db,data.product_id,data.warehouse_id)
    if inventory is None:
        inventory = Inventory(
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            available_quantity=0,
            reserved_quantity=0,
            damaged_quantity=0,
            reorder_level=0)
        db.add(inventory)
        db.flush()
    previous_quantity = inventory.available_quantity
    new_quantity = (previous_quantity + data.adjustment_quantity)
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "INSUFFICIENT_INVENTORY",
                    "message": "Inventory cannot become negative"})
    inventory.available_quantity = new_quantity
    previous_available_quantity = (inventory.available_quantity)
    check_low_stock(db=db,
                    inventory=inventory,
                    previous_available_quantity=(previous_available_quantity))
    transaction = InventoryTransaction(
        inventory_id=inventory.id,
        user_id=user_id,
        transaction_type="ADJUSTMENT",
        quantity=data.adjustment_quantity,
        reference_entity="inventory",
        reference_id=inventory.id,
        metadata_json={"previous_quantity": previous_quantity,
                       "new_quantity": new_quantity,
                       "reason": data.reason})
    db.add(transaction)
    db.commit()
    db.refresh(inventory)
    return inventory

def get_low_stock_inventory(db: Session):
    return db.scalars(select(Inventory).where(Inventory.available_quantity 
                                              <= Inventory.reorder_level)).all()

def reserve_inventory(
    db: Session,
    product_id: int,
    warehouse_id: int,
    quantity: int,
    user_id: int | None = None,
    reference_entity: str = "order",
    reference_id: int | None = None,
    order_id: int | None = None,
):
    if quantity <= 0:
        raise BadRequestException(code="INSUFFICIENT_INVENTORY",
                                  message="Insufficient inventory")
    inventory = get_inventory_for_update(db,product_id,warehouse_id)
    if inventory is None:
        raise NotFoundException(code="INVENTORY_NOT_FOUND",
                                message="Inventory record not found")
    if inventory.available_quantity < quantity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"code": "INSUFFICIENT_INVENTORY",
                                    "message": "Insufficient inventory",})
    previous_available_quantity = (inventory.available_quantity)
    inventory.available_quantity -= quantity
    inventory.reserved_quantity += quantity
    check_low_stock(db=db,
                    inventory=inventory,
                    previous_available_quantity=(previous_available_quantity))
    transaction = InventoryTransaction(
        inventory_id=inventory.id,
        user_id=user_id,
        transaction_type="RESERVATION",
        quantity=quantity,
        reference_entity=reference_entity,
        reference_id=reference_id,
        metadata_json={
            "available_before": (inventory.available_quantity + quantity),
            "available_after": inventory.available_quantity,
            "reserved_after": inventory.reserved_quantity})
    record_audit(
    db=db,
    user_id=user_id,
    action="INVENTORY_RESERVED",
    entity="INVENTORY",
    entity_id=inventory.id,
    metadata={
        "message": (
            f"Reserved {quantity} units "
            f"for order {order_id}"
            if order_id
            else f"Reserved {quantity} units"
        ),
        "order_id": order_id,
        "quantity": quantity,
    },
)
    db.add(transaction)
    return inventory

def release_inventory(
    db: Session,
    product_id: int,
    warehouse_id: int,
    quantity: int,
    order_id:int,
    current_user,
    user_id: int | None = None,
    reference_entity: str = "order",
    reference_id: int | None = None):
    if quantity <= 0:
        raise BadRequestException(code="INSUFFICIENT_INVENTORY",
                                  message="Insufficient inventory")
    inventory = get_inventory_for_update(db,product_id,warehouse_id)
    if inventory is None:
        raise NotFoundException(code="INVENTORY_NOT_FOUND",
                                message="Inventory record not found",)
    if inventory.reserved_quantity < quantity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"code": "INVALID_INVENTORY_RELEASE",
                                    "message": "Cannot release more inventory than reserved",})
    inventory.available_quantity += quantity
    inventory.reserved_quantity -= quantity
    transaction = InventoryTransaction(
        inventory_id=inventory.id,
        user_id=user_id,
        transaction_type="RELEASE",
        quantity=quantity,
        reference_entity=reference_entity,
        reference_id=reference_id,
        metadata_json={"available_after": inventory.available_quantity,
                       "reserved_after": inventory.reserved_quantity,})
    record_audit(
    db=db,
    user_id=current_user.id,
    action="INVENTORY_RELEASED",
    entity="INVENTORY",
    entity_id=inventory.id,
    metadata={
        "message": (
            f"Released {quantity} units "
            f"from order {order_id}"
        ),
        "order_id": order_id,
        "quantity": quantity,
    },
)
    db.add(transaction)
    return inventory

def transfer_inventory(
    db: Session,
    product_id: int,
    source_warehouse_id: int,
    destination_warehouse_id: int,
    quantity: int,
    user_id: int,
    current_user,
    reason: str | None = None,):
    if source_warehouse_id == destination_warehouse_id:
        raise BadRequestException(code="INSUFFICIENT_INVENTORY",
                                  message="Insufficient inventory")
    if quantity <= 0:
        raise BadRequestException(code="INSUFFICIENT_INVENTORY",
                                  message="Insufficient inventory")
    # Lock source inventory row
    source_inventory = get_inventory_for_update(db,product_id,source_warehouse_id)
    if source_inventory is None:
        raise NotFoundException(code="INVENTORY_NOT_FOUND",
                                message="Inventory record not found")
    if source_inventory.available_quantity < quantity:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"code": "INSUFFICIENT_INVENTORY",
                                    "message": "Insufficient inventory for transfer",})
    check_low_stock(db=db,inventory=source_inventory)
    # Lock destination if it already exists
    destination_inventory = get_inventory_for_update(db,product_id,destination_warehouse_id)
    if destination_inventory is None:
        destination_inventory = Inventory(
            product_id=product_id,
            warehouse_id=destination_warehouse_id,
            available_quantity=0,
            reserved_quantity=0,
            damaged_quantity=0,
            reorder_level=0,)
        db.add(destination_inventory)
        db.flush()
    # Move stock
    previous_source_quantity = (source_inventory.available_quantity)
    source_inventory.available_quantity -= quantity
    destination_inventory.available_quantity += quantity
    check_low_stock(db=db,
                    inventory=source_inventory,
                    previous_available_quantity=(previous_source_quantity))
    # TRANSFER_OUT
    transfer_out = InventoryTransaction(
        inventory_id=source_inventory.id,
        user_id=user_id,
        transaction_type="TRANSFER_OUT",
        quantity=quantity,
        reference_entity="warehouse_transfer",
        reference_id=None,
        metadata_json={
            "source_warehouse_id": source_warehouse_id,
            "destination_warehouse_id": destination_warehouse_id,
            "reason": reason,})
    # TRANSFER_IN
    transfer_in = InventoryTransaction(
        inventory_id=destination_inventory.id,
        user_id=user_id,
        transaction_type="TRANSFER_IN",
        quantity=quantity,
        reference_entity="warehouse_transfer",
        reference_id=None,
        metadata_json={
            "source_warehouse_id": source_warehouse_id,
            "destination_warehouse_id": destination_warehouse_id,
            "reason": reason})
    
    create_notification(
    db=db,
    user_id=current_user.id,
    message=(
        f"{quantity} units transferred from "
        f"warehouse {source_warehouse_id} "
        f"to warehouse {destination_warehouse_id}."
    ),
    notification_type=NotificationType.INVENTORY_TRANSFER)
    
    record_audit(
    db=db,
    user_id=current_user.id,
    action="INVENTORY_TRANSFER",
    entity="INVENTORY",
    entity_id=source_inventory.id,
    metadata={
        "message": (
            f"Transferred {quantity} units from "
            f"warehouse {source_warehouse_id} "
            f"to warehouse {destination_warehouse_id}"
        ),
        "quantity": quantity,
        "source_warehouse_id": source_warehouse_id,
        "destination_warehouse_id": destination_warehouse_id,
    },
)
    db.add(transfer_out)
    db.add(transfer_in)
    return (source_inventory,
            destination_inventory)
