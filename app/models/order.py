from datetime import datetime, timezone
from decimal import Decimal
from app.schemas.enums import PaymentStatus
from sqlalchemy import (DateTime,ForeignKey,Numeric,String,Enum)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    order_number: Mapped[str] = mapped_column(String(50),unique=True,nullable=False,index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False,index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"),nullable=False,index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2),nullable=False)
    status: Mapped[str] = mapped_column(String(30),nullable=False,index=True)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus,native_enum=False,
                                            values_callable=lambda enum_class:
                                            [e.value for e in enum_class],length=30,),
                                             default=PaymentStatus.PENDING,nullable=False)
    payment_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_delivery_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True),
                                                                    nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False,index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 onupdate=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    customer = relationship("User",back_populates="orders",foreign_keys=[customer_id])
    warehouse = relationship("Warehouse",back_populates="orders")
    items = relationship("OrderItem",back_populates="order",cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory",back_populates="order",cascade="all, delete-orphan")
    assignments = relationship("OrderAssignment",back_populates="order",cascade="all, delete-orphan")
    returns = relationship("Return",back_populates="order",cascade="all, delete-orphan")