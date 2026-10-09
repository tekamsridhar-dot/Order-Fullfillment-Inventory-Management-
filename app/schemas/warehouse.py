from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class WarehouseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    location: str = Field(min_length=2, max_length=255)
    capacity: int = Field(ge=0)

class WarehouseUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    capacity: int | None = Field(default=None, ge=0)

class WarehouseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str
    capacity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class WarehouseUserCreate(BaseModel):
    user_id: int
    warehouse_id: int