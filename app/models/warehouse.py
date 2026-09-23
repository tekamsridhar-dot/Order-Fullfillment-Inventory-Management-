from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str] = mapped_column(String(150),nullable=False,unique=True)
    location: Mapped[str] = mapped_column(String(255),nullable=False)
    capacity: Mapped[int] = mapped_column(Integer,nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 onupdate=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    inventory_items = relationship("Inventory",back_populates="warehouse")
    users = relationship("WarehouseUser",back_populates="warehouse",cascade="all, delete-orphan")
    orders = relationship("Order",back_populates="warehouse")