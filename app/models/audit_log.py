from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"),
                                                nullable=True,index=True)
    action: Mapped[str] = mapped_column(String(100),nullable=False,index=True)
    entity: Mapped[str] = mapped_column(String(100),nullable=False,index=True)
    entity_id: Mapped[int | None] = mapped_column(nullable=True,index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45),nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON,nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                default=lambda: datetime.now(timezone.utc),
                                                nullable=False,index=True)
    user = relationship("User",back_populates="audit_logs")