from fastapi import HTTPException, status
from app.core.exceptions import BadRequestException
from app.schemas.enums import OrderStatus
from app.core.exceptions import ConflictException

ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING.value: {
        OrderStatus.CONFIRMED.value,
        OrderStatus.CANCELLED.value,
        OrderStatus.FAILED.value,
    },

    OrderStatus.CONFIRMED.value: {
        OrderStatus.PROCESSING.value,
        OrderStatus.CANCELLED.value,
        OrderStatus.FAILED.value,
    },

    OrderStatus.PROCESSING.value: {
        OrderStatus.PACKED.value,
        OrderStatus.CANCELLED.value,
        OrderStatus.FAILED.value,
    },

    OrderStatus.PACKED.value: {
        OrderStatus.SHIPPED.value,
    },

    OrderStatus.SHIPPED.value: {
        OrderStatus.DELIVERED.value,
        OrderStatus.RETURNED.value,
    },

    OrderStatus.DELIVERED.value: {
        OrderStatus.RETURNED.value,
    },

    OrderStatus.CANCELLED.value: set(),

    OrderStatus.FAILED.value: set(),

    OrderStatus.RETURNED.value: set(),
}


def validate_order_transition(
    current_status: str,
    new_status: str
):
    print("STATE TRANSITION DEBUG:")
    print("CURRENT:", repr(current_status))
    print("NEW:", repr(new_status))
    if current_status == new_status:
        raise BadRequestException(
            code="INVALID_ORDER_STATUS",
            message=(
                f"Invalid order status transition: "
                f"{current_status} -> {new_status}"
            )
        )

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        set()
    )

    if new_status not in allowed_statuses:
        raise ConflictException(
            code="INVALID_ORDER_STATUS_TRANSITION",
            message="Invalid order status transition"
        )