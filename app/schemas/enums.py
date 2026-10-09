from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    WAREHOUSE_MANAGER = "warehouse_manager"
    FULFILLMENT_AGENT = "fulfillment_agent"
    CUSTOMER = "customer"

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class WarehouseStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class InventoryTransactionType(str, Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    RESERVATION = "RESERVATION"
    RELEASE = "RELEASE"
    ADJUSTMENT = "ADJUSTMENT"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    RETURN = "RETURN"
    DAMAGE = "DAMAGE"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"
    RETURNED = "returned"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class ReturnStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    RECEIVED = "received"
    REFUNDED = "refunded"

class NotificationType(str, Enum):
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    ORDER_ASSIGNED = "ORDER_ASSIGNED"
    ORDER_SHIPPED = "ORDER_SHIPPED"
    ORDER_DELIVERED = "ORDER_DELIVERED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    RETURN_REQUESTED = "RETURN_REQUESTED"
    RETURN_APPROVED = "RETURN_APPROVED"
    LOW_STOCK = "LOW_STOCK"
    INVENTORY_TRANSFER = "INVENTORY_TRANSFER"
    FAILED_ORDER_PROCESSING = "FAILED_ORDER_PROCESSING"