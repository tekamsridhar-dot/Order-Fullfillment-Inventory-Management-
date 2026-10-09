from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.warehouse_user import WarehouseUser

from app.services.notification_service import send_notification
from app.services.audit_service import record_audit

def check_low_stock(
    db: Session,
    inventory: Inventory,
    previous_available_quantity: int):
    current_quantity = inventory.available_quantity
    reorder_level = inventory.reorder_level

    crossed_threshold = (previous_available_quantity > reorder_level 
                         and current_quantity <= reorder_level)
    if not crossed_threshold:
        return False
    warehouse_users = (db.query(WarehouseUser)
                       .filter(WarehouseUser.warehouse_id == 
                               inventory.warehouse_id ).all())
    for warehouse_user in warehouse_users:
        send_notification(
            db=db,
            user_id=warehouse_user.user_id,
            notification_type="LOW_STOCK",
            message=(
                f"Product {inventory.product_id} "
                f"has reached the reorder level. "
                f"Available quantity: "
                f"{current_quantity}."))
    record_audit(
        db=db,
        user_id=None,
        action="LOW_STOCK",
        entity="inventory",
        entity_id=inventory.id,
        metadata={
            "product_id": inventory.product_id,
            "warehouse_id": inventory.warehouse_id,
            "previous_quantity": (previous_available_quantity),
            "available_quantity": current_quantity,
            "reorder_level": reorder_level,})
    return True