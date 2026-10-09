from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.return_schema import (ReturnCreate,ReturnResponse,ReturnStatusUpdate)
from app.services.return_service import (create_customer_return,update_return_status)
from app.repositories.return_repository import (get_return_by_id,get_returns)

router = APIRouter(prefix="/api/returns",
                   tags=["Returns"])

@router.post("",response_model=ReturnResponse,
             status_code=status.HTTP_201_CREATED)
def create_return_request(
    request: ReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        if current_user.role.name not in ["customer", "admin"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only customers and admins can request returns")
        return_obj = create_customer_return(
            db=db,
            customer_id=current_user.id,
            order_id=request.order_id,
            reason=request.reason,
            items=request.items)
        db.commit()
        db.refresh(return_obj)
        return return_obj
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print("RETURN ERROR:", repr(e))
        raise

@router.get("/{return_id}",response_model=ReturnResponse)
def get_return(
    return_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return_obj = get_return_by_id(db=db,
                                  return_id=return_id)
    if not return_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Return not found")
    if current_user.role.name == "customer" or current_user.role.name == "admin":
        if return_obj.customer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to view this return")
    return return_obj

@router.get("",response_model=list[ReturnResponse])
def list_returns(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    customer_id = None
    if current_user.role.name == "customer":
        customer_id = current_user.id
    return get_returns(
        db=db,
        customer_id=customer_id,
        status_filter=status_filter)

@router.patch("/{return_id}/status",response_model=ReturnResponse)
def change_return_status(
    return_id: int,
    request: ReturnStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        if current_user.role.name not in {"admin","warehouse_manager","fulfillment_agent",}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to update returns")
        return_obj = update_return_status(
            db=db,
            return_id=return_id,
            new_status=request.status.value)
        db.commit()
        db.refresh(return_obj)
        return return_obj
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to update return status")