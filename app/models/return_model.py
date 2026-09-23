from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Return(Base):
    __tablename__ = "returns"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"),nullable=False,index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False,index=True)
    status: Mapped[str] = mapped_column(String(30),nullable=False,index=True)
    reason: Mapped[str | None] = mapped_column(String(500),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 onupdate=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    order = relationship("Order",back_populates="returns")
    customer = relationship("User")
    items = relationship("ReturnItem",back_populates="return_request",cascade="all, delete-orphan")