from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255),unique=True,nullable=False,index=True)
    password_hash: Mapped[str] = mapped_column(String(255),nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"),nullable=False,index=True)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc),
                                                 nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                default=lambda: datetime.now(timezone.utc),
                                                onupdate=lambda: datetime.now(timezone.utc),
                                                nullable=False)
    role = relationship("Role",back_populates="users")
    orders = relationship("Order",back_populates="customer",foreign_keys="Order.customer_id")
    warehouse_assignments = relationship("WarehouseUser",back_populates="user",
                                             cascade="all, delete-orphan")
    order_assignments = relationship("OrderAssignment",foreign_keys="OrderAssignment.agent_id")
    refresh_tokens = relationship("RefreshToken",back_populates="user",cascade="all, delete-orphan")
    notifications = relationship("Notification",back_populates="user",cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog",back_populates="user")
    