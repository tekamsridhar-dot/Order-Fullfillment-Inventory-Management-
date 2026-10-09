from sqlalchemy.orm import Session
import hashlib
import json
from sqlalchemy.exc import IntegrityError
from app.repositories.idempotency_repository import (get_idempotency_key,create_idempotency_key)
from app.core.exceptions import ConflictException

def start_idempotent_operation(
    db: Session,
    user_id: int,
    key: str,
    endpoint: str):
    existing = get_idempotency_key(
        db,
        user_id,
        key,
        endpoint)
    if existing:
        return existing, True
    try:
        record = create_idempotency_key(
            db,
            user_id,
            key,
            endpoint)
        return record, False
    except IntegrityError:
        db.rollback()
        existing = get_idempotency_key(
            db,
            user_id,
            key,
            endpoint)
        if existing:
            return existing, True
        raise ConflictException(
            "Unable to process idempotency key")


def check_idempotency_key(
    db: Session,
    user_id: int,
    key: str,
    endpoint: str):
    return get_idempotency_key(
        db=db,
        user_id=user_id,
        key=key,
        endpoint=endpoint)



def generate_request_hash(payload) -> str:
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()