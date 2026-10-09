from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import ReturnStatus

class ReturnItemCreate(BaseModel):
    order_item_id: int
    quantity: int = Field(gt=0)

class ReturnCreate(BaseModel):
    order_id: int
    reason: str = Field(min_length=3, max_length=500)
    items: list[ReturnItemCreate] = Field(min_length=1)

class ReturnStatusUpdate(BaseModel):
    status: ReturnStatus

class ReturnItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    return_id: int
    order_item_id: int
    quantity: int

class ReturnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    customer_id: int
    status: ReturnStatus
    reason: str
    created_at: datetime
    updated_at: datetime
    items: list[ReturnItemResponse] = Field(default_factory=list)