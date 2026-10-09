from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    category_id: int
    price: Decimal = Field(ge=0)
    cost_price: Decimal = Field(ge=0)

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    price: Decimal | None = Field(default=None, ge=0)
    cost_price: Decimal | None = Field(default=None, ge=0)

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    description: str | None
    category_id: int
    price: Decimal
    cost_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime