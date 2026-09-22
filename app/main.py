from fastapi import FastAPI

app = FastAPI(
    title="Order Fulfillment & Inventory Management Platform",
    description="""Backend API for order fulfillment and inventory management.
                    <br><br><b>Created by:</b> Sridhar Tekam""")


@app.get("/")
def root():
    return {"message": "Order Fulfillment & Inventory Management Platform API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}