from fastapi import APIRouter, Depends, HTTPException, status,Header                                                                                
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from datetime import datetime
from app.schemas.common import PaginatedResponse
from app.dependencies import get_db
from app.core.auth import require_admin_or_customer, get_current_user
from app.core.exceptions import ConflictException,AppException
from app.models.user import User
from app.models.warehouse_user import WarehouseUser
from app.repositories.idempotency_repository import get_idempotency_key,save_idempotency_key
from app.repositories.order_assignment_repository import get_assignment_history
from app.repositories.order_repository import get_orders,get_order_by_id
from app.services.order_service import (create_customer_order,update_order_status,assign_order,
                                        cancel_order,list_customer_orders)
from app.services.idempotency_service import check_idempotency_key
from app.schemas.order import (OrderCreate,OrderResponse,OrderStatusUpdate,
                               OrderStatusHistoryResponse,OrderAssignmentRequest,
                               OrderAssignmentResponse)
from app.repositories.order_status_repository import get_order_status_history
from app.utils.idempotency import generate_request_hash

router = APIRouter(prefix="/api/orders",
                   tags=["Orders"])

@router.post("",response_model=OrderResponse,
             status_code=status.HTTP_201_CREATED)
def create_order(
    request: OrderCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_customer)
):
    request_hash = generate_request_hash(
        request.model_dump(mode="json")
    )

    try:
        existing = check_idempotency_key(
            db=db,
            user_id=current_user.id,
            key=idempotency_key,
            endpoint="/api/orders"
        )

        if existing:
            if existing.request_hash != request_hash:
                raise ConflictException(
                    code="IDEMPOTENCY_KEY_REUSED",
                    message=(
                        "Idempotency key cannot be reused "
                        "with a different request payload"
                    )
                )

            if existing.response_body is not None:
                return existing.response_body

            raise ConflictException(
                code="DUPLICATE_IDEMPOTENCY_KEY",
                message="This idempotency key has already been used"
            )

        order = create_customer_order(
            db=db,
            customer_id=current_user.id,
            warehouse_id=request.warehouse_id,
            items=request.items,
            current_user=current_user,
            expected_delivery_date=request.expected_delivery_date
        )

        db.flush()
        db.refresh(order)

        response_body = {
            "id": order.id,
            "order_number": order.order_number,
            "customer_id": order.customer_id,
            "warehouse_id": order.warehouse_id,
            "total_amount": str(order.total_amount),
            "status": order.status,
            "payment_status": order.payment_status,
            "expected_delivery_date": (
                order.expected_delivery_date.isoformat()
                if order.expected_delivery_date
                else None
            ),
            "created_at": (
                order.created_at.isoformat()
                if order.created_at
                else None
            ),
            "updated_at": (
                order.updated_at.isoformat()
                if order.updated_at
                else None
            )
        }

        save_idempotency_key(
            db=db,
            user_id=current_user.id,
            key=idempotency_key,
            endpoint="/api/orders",
            request_hash=request_hash,
            response_body=response_body
        )

        db.commit()

        return order

    except IntegrityError:
        db.rollback()

        existing = get_idempotency_key(
            db=db,
            user_id=current_user.id,
            key=idempotency_key,
            endpoint="/api/orders"
        )

        if existing:
            if existing.request_hash != request_hash:
                raise ConflictException(
                    code="IDEMPOTENCY_KEY_REUSED",
                    message=(
                        "Idempotency key cannot be reused "
                        "with a different request payload"
                    )
                )

            if existing.response_body:
                return existing.response_body

        raise ConflictException(
            code="DUPLICATE_IDEMPOTENCY_KEY",
            message="This idempotency key has already been used"
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print("ORDER CREATION ERROR:", repr(e))
        raise

@router.get("")
def list_orders(
    warehouse_id: int | None = None,
    status: str | None = None,
    payment_status: str | None = None,
    min_total: float | None = None,
    max_total: float | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    customer_id = None
    if current_user.role.name == "customer":
        customer_id = current_user.id
    return list_customer_orders(
        db=db,
        customer_id=customer_id,
        warehouse_id=warehouse_id,
        status=status,
        payment_status=payment_status,
        min_total=min_total,
        max_total=max_total,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order)

@router.patch("/{order_id}/status",response_model=OrderResponse)
def update_status(
    order_id: int,
    request: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        order = get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Order not found")
        if current_user.role.name == "customer":
            if order.customer_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not authorized to update this order")
        if current_user.role.name not in {
            "admin",
            "warehouse_manager",
            "fulfillment_agent"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to change order status")
        updated_order = update_order_status(
                        db=db,
                        order_id=order_id,
                        new_status=request.status.value,
                        changed_by_id=current_user.id,
                        current_user=current_user)
        db.commit()
        db.refresh(updated_order)
        return updated_order
    except HTTPException:
            db.rollback()
            raise
    except AppException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status")

@router.get("/{order_id}/history",response_model=list[OrderStatusHistoryResponse])
def get_status_history(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")
    if current_user.role.name == "customer":
        if order.customer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to view this order")
    return get_order_status_history(db=db,order_id=order_id)

@router.get("/{order_id}",response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):

    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")
    if current_user.role.name == "customer":
        if order.customer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to view this order")
    return order

@router.post("/{order_id}/assign",response_model=OrderAssignmentResponse)
def assign_order_to_agent(
    order_id: int,
    request: OrderAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        if current_user.role.name not in {"admin","warehouse_manager"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to assign orders")
        order = get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Order not found")
        if current_user.role.name == "warehouse_manager":
            warehouse_assignment = db.scalars(select(WarehouseUser).where(
                    WarehouseUser.user_id == current_user.id,
                    WarehouseUser.warehouse_id == order.warehouse_id,)).first()
            if not warehouse_assignment:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not authorized for this warehouse",)
        assignment = assign_order(
            db=db,
            order_id=order_id,
            agent_id=request.agent_id,
            assigned_by_id=current_user.id)
        db.commit()
        db.refresh(assignment)
        return assignment
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to assign order")

@router.get("/{order_id}/assignments",response_model=list[OrderAssignmentResponse])
def get_assignments(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Order not found")
    if current_user.role.name == "customer":
        if order.customer_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to view this order")
    return get_assignment_history(db=db,
                                  order_id=order_id)

@router.patch("/{order_id}/cancel",response_model=OrderResponse)
def cancel_customer_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    try:
        order = get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Order not found")
        if current_user.role.name == "customer":
            if order.customer_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="You are not authorized to cancel this order")
        elif current_user.role.name not in {
            "admin",
            "warehouse_manager",
            "fulfillment_agent",}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You are not authorized to cancel this order")
        cancelled_order = cancel_order(
            db=db,
            order_id=order_id,
            cancelled_by_id=current_user.id)
        db.commit()
        db.refresh(cancelled_order)
        return cancelled_order
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to cancel order")