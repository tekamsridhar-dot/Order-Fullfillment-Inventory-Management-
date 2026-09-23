from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class OrderAssignment(Base):
    __tablename__ = "order_assignments"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"),
                                          nullable=False,index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False,index=True)
    assigned_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  default=lambda: datetime.now(timezone.utc),
                                                  nullable=False)
    order = relationship("Order",back_populates="assignments")
    agent = relationship("User",foreign_keys=[agent_id])
    assigned_by = relationship("User",foreign_keys=[assigned_by_id])