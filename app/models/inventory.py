from datetime import datetime, timezone

from sqlalchemy import (CheckConstraint,DateTime,ForeignKey,Integer,UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"),nullable=False,index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"),
                                              nullable=False,index=True)
    available_quantity: Mapped[int] = mapped_column(Integer,default=0,nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer,default=0,nullable=False)
    damaged_quantity: Mapped[int] = mapped_column(Integer, default=0,nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer,default=0,nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 onupdate=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    product = relationship("Product",back_populates="inventory_items")
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    transactions = relationship("InventoryTransaction",back_populates="inventory")
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "warehouse_id",
            name="uq_product_warehouse_inventory"),
        CheckConstraint(
            "available_quantity >= 0",
            name="ck_inventory_available_non_negative"
        ),
        CheckConstraint(
            "reserved_quantity >= 0",
            name="ck_inventory_reserved_non_negative"
        ),
        CheckConstraint(
            "damaged_quantity >= 0",
            name="ck_inventory_damaged_non_negative"
        ),
        CheckConstraint(
            "reorder_level >= 0",
            name="ck_inventory_reorder_non_negative"
        ),
    )