from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class WarehouseUser(Base):
    __tablename__ = "warehouse_users"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"),
                                         nullable=False,index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="CASCADE"),
                                              nullable=False,index=True)
    warehouse = relationship("Warehouse",back_populates="users")
    user = relationship("User")
    __table_args__ = (
    UniqueConstraint(
        "user_id",
        "warehouse_id",
        name="uq_user_warehouse"),)