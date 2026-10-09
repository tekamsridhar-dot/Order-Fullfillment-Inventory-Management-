from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.warehouse_user import WarehouseUser


def check_warehouse_access(
    db: Session,
    user,
    warehouse_id: int,
):
    if user.role.name == "admin":
        return

    assignment = (
        db.query(WarehouseUser)
        .filter(
            WarehouseUser.user_id == user.id,
            WarehouseUser.warehouse_id == warehouse_id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Warehouse access denied",
        )