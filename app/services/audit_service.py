from sqlalchemy.orm import Session
from app.repositories.audit_repository import create_audit_log

def record_audit(
    db: Session,
    user_id: int | None,
    action: str,
    entity: str,
    entity_id: int | None,
    ip_address: str | None = None,
    metadata: dict | None = None):
    return create_audit_log(
        db=db,
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        ip_address=ip_address,
        metadata=metadata)