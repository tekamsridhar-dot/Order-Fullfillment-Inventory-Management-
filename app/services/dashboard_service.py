from app.repositories.dashboard_repository import (get_admin_dashboard, 
                                                   get_warehouse_dashboard,
                                                   get_customer_dashboard)

def admin_dashboard(db):
    return get_admin_dashboard(db)

def warehouse_dashboard(db, warehouse_id: int,):
    return get_warehouse_dashboard( db, warehouse_id )

def customer_dashboard(db,customer_id: int):
    return get_customer_dashboard(db,customer_id )