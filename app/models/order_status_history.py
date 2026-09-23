from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"),
                                          nullable=False,index=True)
    changed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"),nullable=True)
    old_status: Mapped[str | None] = mapped_column(String(30),nullable=True)
    new_status: Mapped[str] = mapped_column(String(30),nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),nullable=False)
    order = relationship("Order",back_populates="status_history")
    changed_by = relationship("User")