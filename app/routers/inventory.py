from fastapi import APIRouter, Depends, Query,HTTPException, status,Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.core.auth import get_current_user
from app.models.user import User
from app.dependencies import get_db
from app.schemas.inventory import (InventoryAdjustmentRequest,InventoryResponse,
                                   InventoryTransferRequest,InventoryReservationRequest)
from app.services.inventory_service import (adjust_inventory,get_inventory_item, 
                                            get_low_stock_inventory,
                                            release_inventory,reserve_inventory,
                                            transfer_inventory,list_inventory_paginated)
from app.repositories.idempotency_repository import check_idempotency_key,save_idempotency_key
from app.models.inventory import Inventory
from app.core.exceptions import ConflictException

router = APIRouter(prefix="/api/inventory",
                   tags=["Inventory"])

@router.get("")
def list_inventory_endpoint(
    warehouse_id: int | None = None,
    product_id: int | None = None,
    low_stock: bool = False,
    out_of_stock: bool = False,
    page: int = 1,
    page_size: int = 20,
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return list_inventory_paginated(
        db=db,
        warehouse_id=warehouse_id,
        product_id=product_id,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        page=page,
        page_size=page_size,
        sort_order=sort_order)

@router.get("/low-stock",response_model=list[InventoryResponse],)
def low_stock_inventory(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)):
     return get_low_stock_inventory(db)

@router.get("/{product_id}",response_model=list[InventoryResponse])
def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)):
    
    return db.scalars(select(Inventory).where(Inventory.product_id == product_id)).all()

@router.post("/adjust",response_model=InventoryResponse)
def adjust_inventory_endpoint(
    data: InventoryAdjustmentRequest,
    idempotency_key: str = Header(...,alias="Idempotency-Key",),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)):
    existing = check_idempotency_key(
    db=db,
    user_id=current_user.id,
    key=idempotency_key,
    endpoint="/api/inventory/adjust")

    if existing:
        if existing.response_body is not None:
            return existing.response_body

        raise ConflictException(code="DUPLICATE_IDEMPOTENCY_KEY",
                                message="This idempotency key has already been used")
    return adjust_inventory(
        db=db,
        data=data,
        user_id=current_user.id)

@router.post("/reserve",response_model=InventoryResponse)
def reserve_inventory_endpoint(data: InventoryReservationRequest,
                               db: Session = Depends(get_db),
                               current_user=Depends(get_current_user)):
    try:
        inventory = reserve_inventory(
            db=db,
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            quantity=data.quantity,
            user_id=current_user.id,
            reference_entity=data.reference_entity,
            reference_id=data.reference_id)
        db.commit()
        db.refresh(inventory)
        return inventory
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

@router.post("/release",response_model=InventoryResponse,)
def release_inventory_endpoint(
    data: InventoryReservationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)):
    try:
        inventory = release_inventory(
            db=db,
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            quantity=data.quantity,
            user_id=current_user.id,
            reference_entity=data.reference_entity,
            reference_id=data.reference_id,)
        db.commit()
        db.refresh(inventory)
        return inventory
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

@router.post("/transfer")
def transfer_inventory_endpoint(
    data: InventoryTransferRequest,
    idempotency_key: str = Header(...,alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)):
    try:
        existing = check_idempotency_key(
            db=db,
            user_id=current_user.id,
            key=idempotency_key,
            endpoint="/api/inventory/transfer")
        if existing:
            if existing.response_body is not None:
                return existing.response_body

            raise ConflictException(code="DUPLICATE_IDEMPOTENCY_KEY",
                                    message="This idempotency key has already been used")
        source, destination = transfer_inventory(
            db=db,
            product_id=data.product_id,
            source_warehouse_id=data.source_warehouse_id,
            destination_warehouse_id=data.destination_warehouse_id,
            quantity=data.quantity,
            user_id=current_user.id,
            reason=data.reason)
        response_body = {
            "message": "Inventory transferred successfully",
            "source_inventory": source,
            "destination_inventory": destination}
        save_idempotency_key(
            db=db,
            user_id=current_user.id,
            key=idempotency_key,
            endpoint="/api/inventory/transfer",
            response_body={
                "message": "Inventory transferred successfully",
                "source_inventory_id": source.id,
                "destination_inventory_id": destination.id})
        db.commit()
        db.refresh(source)
        db.refresh(destination)
        return response_body
    except IntegrityError:
        db.rollback()
        # Another simultaneous request may have created
        # the same idempotency key.
        existing = check_idempotency_key(
            db=db,
            user_id=current_user.id,
            key=idempotency_key,
            endpoint="/api/inventory/transfer")
        if existing:
            if existing.response_body is not None:
                return existing.response_body
        raise ConflictException(code="DUPLICATE_IDEMPOTENCY_KEY",
                                message="This idempotency key has already been used")
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer inventory")