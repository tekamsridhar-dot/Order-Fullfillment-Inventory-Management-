from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import InventoryTransactionType

class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    warehouse_id: int
    available_quantity: int
    reserved_quantity: int
    damaged_quantity: int
    reorder_level: int
    updated_at: datetime

class InventoryAdjustmentRequest(BaseModel):
    product_id: int
    warehouse_id: int
    adjustment_quantity: int
    reason: str = Field(min_length=3, max_length=255)

class InventoryTransferRequest(BaseModel):
    product_id: int
    source_warehouse_id: int
    destination_warehouse_id: int
    quantity: int = Field(gt=0)
    reason: str | None = Field(default=None, max_length=255)

class InventoryTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_id: int
    user_id: int | None
    transaction_type: InventoryTransactionType
    quantity: int
    reference_entity: str | None
    reference_id: int | None
    metadata_json: dict | None
    created_at: datetime

class InventoryReservationRequest(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int = Field(gt=0)
    reference_entity: str = "order"
    reference_id: int