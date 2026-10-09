from datetime import date, datetime
from decimal import Decimal
from app.schemas.enums import OrderStatus
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import OrderStatus, PaymentStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    discount: Decimal = Field(default=0, ge=0)
    tax: Decimal = Field(default=0, ge=0)

class OrderCreate(BaseModel):
    warehouse_id: int
    items: list[OrderItemCreate] = Field(min_length=1)
    expected_delivery_date: date | None = None

class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    customer_id: int
    warehouse_id: int
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    expected_delivery_date: date | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderAssignmentRequest(BaseModel):
    agent_id: int

class OrderAssignmentResponse(BaseModel):
    id: int
    order_id: int
    agent_id: int
    assigned_by_id: int
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderStatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    changed_by_id: int
    old_status: str
    new_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)