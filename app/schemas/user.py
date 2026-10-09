from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role_id: int

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    role_id: int | None = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime