from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"),
                                          nullable=False,index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"),nullable=False,index=True)
    quantity: Mapped[int] = mapped_column(Integer,nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2),nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2),default=0,nullable=False)
    tax: Mapped[Decimal] = mapped_column(Numeric(12, 2),default=0,nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2),nullable=False)
    order = relationship("Order",back_populates="items")
    product = relationship("Product",back_populates="order_items")