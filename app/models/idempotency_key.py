from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),
                                         nullable=False,index=True)
    key: Mapped[str] = mapped_column(String(255),nullable=False)
    endpoint: Mapped[str] = mapped_column(String(255),nullable=False)
    response_status: Mapped[int | None] = mapped_column(Integer,nullable=True)
    response_body: Mapped[dict | None] = mapped_column(JSON,nullable=True)
    request_hash: Mapped[str] = mapped_column(String(64),nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    user = relationship("User")
    __table_args__ = (UniqueConstraint("user_id","key","endpoint",
                                       name="uq_idempotency_user_key_endpoint"),)