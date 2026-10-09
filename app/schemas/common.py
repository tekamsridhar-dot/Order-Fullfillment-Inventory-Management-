from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")

class MessageResponse(BaseModel):
    message: str

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class PaginationResponse(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationResponse