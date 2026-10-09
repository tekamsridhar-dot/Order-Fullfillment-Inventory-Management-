from fastapi import (APIRouter,Depends,HTTPException,status,)
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import (AdminDashboardResponse,
                                   WarehouseDashboardResponse,
                                   CustomerDashboardResponse)
from app.core.auth import require_admin_or_customer
from app.services.dashboard_service import (admin_dashboard,warehouse_dashboard,customer_dashboard)
from app.services.warehouse_service import verify_warehouse_access

router = APIRouter(prefix="/api/dashboard",
                   tags=["Dashboard"])

@router.get( "/admin", response_model=AdminDashboardResponse)
def get_admin_dashboard_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin access required")
    return admin_dashboard(db)

@router.get(
    "/warehouse/{warehouse_id}",
    response_model=WarehouseDashboardResponse,
)
def get_warehouse_dashboard_endpoint(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    if current_user.role.name not in { "admin","warehouse_manager"}:
        raise HTTPException( status_code=status.HTTP_403_FORBIDDEN,
                             detail="Warehouse dashboard access denied" )
    if current_user.role.name == "warehouse_manager":
        verify_warehouse_access(
            db=db,
            user=current_user,
            warehouse_id=warehouse_id)
    return warehouse_dashboard( db, warehouse_id)

@router.get(
    "/customer",
    response_model=CustomerDashboardResponse
)
def get_customer_dashboard_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_customer)
):
    return customer_dashboard(
        db,
        current_user.id
    )