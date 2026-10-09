from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import (get_current_user,require_admin,require_admin_or_warehouse_manager)
from app.dependencies import get_db
from app.schemas.warehouse import (WarehouseCreate,WarehouseUpdate,WarehouseResponse,
                                   WarehouseUserCreate)
from app.services.warehouse_service import (create_new_warehouse,list_warehouses,get_warehouse,
                                            update_warehouse,activate_warehouse,
                                            deactivate_warehouse,assign_user_to_warehouse,
                                            verify_warehouse_access)

from app.repositories.warehouse_repository import get_user_warehouses

router = APIRouter(prefix="/api/warehouses",
                   tags=["Warehouses"])

@router.post("",response_model=WarehouseResponse)
def create_warehouse_endpoint(data: WarehouseCreate,
                              db: Session = Depends(get_db),
                              current_user=Depends(require_admin)):
    return create_new_warehouse(db,data)

@router.get("",response_model=list[WarehouseResponse])
def list_warehouses_endpoint(
    page: int = Query(default=1,ge=1),
    page_size: int = Query(default=20,ge=1,le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_warehouse_manager)):
    if current_user.role.name == "admin":
        skip = (page - 1) * page_size
        return list_warehouses(db,
                               skip=skip,
                               limit=page_size)
    return get_user_warehouses(db,current_user.id)

@router.get("/{warehouse_id}",response_model=WarehouseResponse)
def get_warehouse_endpoint(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_warehouse_manager)):
    return verify_warehouse_access(db,
                                   current_user,
                                   warehouse_id)

@router.put("/{warehouse_id}",
            response_model=WarehouseResponse)
def update_warehouse_endpoint(
    warehouse_id: int,
    data: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_warehouse_manager)):
    verify_warehouse_access(
        db,
        current_user,
        warehouse_id)
    return update_warehouse(
        db,
        warehouse_id,
        data)

@router.patch("/{warehouse_id}/activate",
              response_model=WarehouseResponse)
def activate_warehouse_endpoint(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)):
    return activate_warehouse(db,
                              warehouse_id)

@router.patch("/{warehouse_id}/deactivate",
              response_model=WarehouseResponse)
def deactivate_warehouse_endpoint(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)):
    return deactivate_warehouse(db,warehouse_id)

@router.post("/{warehouse_id}/users")
def assign_user_endpoint(
    warehouse_id: int,
    data: WarehouseUserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)):
    if data.warehouse_id != warehouse_id:
        raise HTTPException(status_code=400,
            detail={"code": "WAREHOUSE_ID_MISMATCH",
                    "message": "Path warehouse_id and request warehouse_id must match",})
    assignment = assign_user_to_warehouse(db,user_id=data.user_id,warehouse_id=warehouse_id)
    return {"message": "User assigned to warehouse successfully",
            "assignment_id": assignment.id}
