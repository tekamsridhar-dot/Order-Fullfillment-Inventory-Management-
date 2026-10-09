from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.idempotency_key import IdempotencyKey

def get_idempotency_key(
    db: Session,
    user_id: int,
    key: str,
    endpoint: str,):
    return (db.query(IdempotencyKey).filter(
            IdempotencyKey.user_id == user_id,
            IdempotencyKey.key == key,
            IdempotencyKey.endpoint == endpoint,).first() )

def create_idempotency_key(
    db: Session,
    user_id: int,
    key: str,
    endpoint: str,):
    record = IdempotencyKey(
        user_id=user_id,
        key=key,
        endpoint=endpoint)
    db.add(record)
    db.flush()
    return record

def save_idempotency_key(
    db: Session,
    user_id: int,
    key: str,
    endpoint: str,
    request_hash: str,
    response_body: dict):
    record = IdempotencyKey(
        user_id=user_id,
        key=key,
        endpoint=endpoint,
        request_hash=request_hash,
        response_body=response_body)
    db.add(record)
    db.flush()
    return record

def check_idempotency_key(
    db: Session,
    user_id: int,
    key: str,
    endpoint: str):
    return db.scalar(select(IdempotencyKey).where(
            IdempotencyKey.user_id == user_id,
            IdempotencyKey.key == key,
            IdempotencyKey.endpoint == endpoint))