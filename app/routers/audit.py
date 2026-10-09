from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.core.auth import require_admin
from app.models.user import User
from app.repositories.audit_repository import get_audit_logs

router = APIRouter(prefix="/api/audit-logs",
                   tags=["Audit Logs"])

@router.get("")
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)):
    return get_audit_logs(db)