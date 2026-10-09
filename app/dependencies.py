from typing import Generator
from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.warehouse_user import WarehouseUser
from app.schemas.enums import UserRole

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_warehouse_access(
    db: Session,
    current_user,
    warehouse_id: int,
):
    if current_user.role.name == UserRole.ADMIN:
        return True

    assignment = (
        db.query(WarehouseUser)
        .filter(
            WarehouseUser.user_id == current_user.id,
            WarehouseUser.warehouse_id == warehouse_id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Warehouse access denied",
        )

    return True