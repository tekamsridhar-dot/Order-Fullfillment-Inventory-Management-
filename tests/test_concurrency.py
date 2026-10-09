import os

import pytest
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.inventory_service import reserve_inventory
from app.database import Base
from app.models.inventory import Inventory


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/order_fulfillment_test_db",
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def reserve_stock(
    product_id: int,
    warehouse_id: int,
    quantity: int,
    user_id: int,
):
    db = TestSessionLocal()

    try:
        reserve_inventory(
            db=db,
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
            user_id=user_id,
        )

        db.commit()

        return "success"

    except Exception:
        db.rollback()
        return "failed"

    finally:
        db.close()


def test_inventory_cannot_become_negative(
    client,
    manager_token,
):
    headers = {
        "Authorization": f"Bearer {manager_token}",
        "Idempotency-Key": "inventory-negative-test-001",
    }

    response = client.post(
        "/api/inventory/adjust",
        json={
            "product_id": 1,
            "warehouse_id": 1,
            "adjustment_quantity": -999999,
            "reason": "Invalid adjustment",
        },
        headers=headers,
    )

    assert response.status_code in [400, 409]