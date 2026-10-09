from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import AppException
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.categories import router as categories_router
from app.routers.warehouses import router as warehouses_router
from app.routers.inventory import router as inventory_router
from app.routers.orders import router as orders_router
from app.routers.returns import router as returns_router
from app.routers.notifications import router as notifications_router
from app.routers.audit import router as audit_router
from app.routers.dashboard import router as dashboard_router
from app.routers.payments import router as payment_router

app = FastAPI(
    title="Order Fulfillment & Inventory Management Platform",
    description="""Backend API for order fulfillment and inventory management.
                    <br><br><b>Created by:</b> Sridhar Tekam""")

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(warehouses_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(returns_router)
app.include_router(notifications_router)
app.include_router(audit_router)
app.include_router(dashboard_router)
app.include_router(payment_router)

@app.get("/")
def root():
    return {"message": "Order Fulfillment & Inventory Management Platform API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            },
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("VALIDATION ERRORS:", exc.errors())

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )