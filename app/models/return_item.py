from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class ReturnItem(Base):
    __tablename__ = "return_items"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    return_id: Mapped[int] = mapped_column(ForeignKey("returns.id", ondelete="CASCADE"),
                                           nullable=False,index=True)
    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id"),nullable=False,index=True)
    quantity: Mapped[int] = mapped_column(Integer,nullable=False)
    return_request = relationship("Return",back_populates="items")
    order_item = relationship("OrderItem")