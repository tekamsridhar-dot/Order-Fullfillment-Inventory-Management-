from decimal import Decimal
from pydantic import BaseModel

class AdminDashboardResponse(BaseModel):
    total_orders: int
    pending_orders: int
    processing_orders: int
    completed_orders: int
    cancelled_orders: int
    total_revenue: Decimal
    low_stock_products: int
    out_of_stock_products: int

class WarehouseDashboardResponse(BaseModel):
    warehouse_id: int
    inventory_items: int
    pending_fulfillment: int
    processing_orders: int
    low_stock_items: int
    todays_shipments: int

class CustomerDashboardResponse(BaseModel):
    total_orders: int
    active_orders: int
    completed_orders: int
    cancelled_orders: int
    total_spending: Decimal