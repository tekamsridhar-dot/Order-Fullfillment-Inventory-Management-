from fastapi import HTTPException, status
from app.schemas.enums import ReturnStatus
from app.core.exceptions import BadRequestException,ConflictException

ALLOWED_RETURN_TRANSITIONS = {
    ReturnStatus.REQUESTED.value: {
        ReturnStatus.APPROVED.value,
        ReturnStatus.REJECTED.value,
    },

    ReturnStatus.APPROVED.value: {
        ReturnStatus.RECEIVED.value,
    },

    ReturnStatus.RECEIVED.value: {
        ReturnStatus.REFUNDED.value,
    },

    ReturnStatus.REJECTED.value: set(),

    ReturnStatus.REFUNDED.value: set(),
}

def validate_return_transition(
    current_status: str,
    new_status: str):
    if current_status == new_status:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Return is already in this status")
    allowed_statuses = ALLOWED_RETURN_TRANSITIONS.get(current_status,set())
    if new_status not in allowed_statuses:
        raise BadRequestException(code="INVALID_RETURN_STATUS",
                                  message=(f"Invalid return status transition: "
                                           f"{current_status} -> {new_status}"))

def validate_request_hash(
    existing,
    request_hash: str):
    if existing.request_hash != request_hash:
        raise ConflictException("Idempotency key was already used with a different request")