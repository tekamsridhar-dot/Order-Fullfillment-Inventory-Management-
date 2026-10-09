from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def create_audit_log(
    db: Session,
    user_id: int | None,
    action: str,
    entity: str,
    entity_id: int | None,
    ip_address: str | None = None,
    metadata: dict | None = None):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        ip_address=ip_address,
        metadata_json=metadata)
    db.add(audit_log)
    db.flush()
    return audit_log

def get_audit_logs(
    db: Session):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()