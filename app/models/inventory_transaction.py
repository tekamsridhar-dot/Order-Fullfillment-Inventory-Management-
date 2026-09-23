from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"),nullable=False,index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"),nullable=True,index=True)
    transaction_type: Mapped[str] = mapped_column(String(50),nullable=False,index=True)
    quantity: Mapped[int] = mapped_column(Integer,nullable=False)
    reference_entity: Mapped[str | None] = mapped_column(String(100),nullable=True)
    reference_id: Mapped[int | None] = mapped_column(nullable=True,index=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON,nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False,index=True)
    inventory = relationship("Inventory",back_populates="transactions")
    user = relationship("User")