import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select,delete
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies import get_db

from app.models.role import Role
from app.models.category import Category
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.idempotency_key import IdempotencyKey

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:Rockstar1@localhost:5432/order_fulfillment_test_db"
)

engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    echo=True)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():

    # Start every pytest session with a clean database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:

        # -------------------------------------------------
        # Seed Roles
        # -------------------------------------------------

        roles = [
            "admin",
            "warehouse_manager",
            "fulfillment_agent",
            "customer",
        ]

        for role_name in roles:

            existing_role = db.scalar(
                select(Role).where(
                    Role.name == role_name
                )
            )

            if not existing_role:
                db.add(
                    Role(name=role_name)
                )

        db.flush()

        # -------------------------------------------------
        # Seed Category
        # -------------------------------------------------

        category = db.scalar(
            select(Category).where(
                Category.name == "Test Category"
            )
        )

        if not category:
            category = Category(
                name="Test Category",
                description="Category for automated tests",
            )

            db.add(category)
            db.flush()

        # -------------------------------------------------
        # Seed Warehouse
        # -------------------------------------------------

        warehouse = db.scalar(
            select(Warehouse).where(
                Warehouse.name == "Test Warehouse"
            )
        )

        if not warehouse:
            warehouse = Warehouse(
                name="Test Warehouse",
                location="Test Location",
                capacity=1000,
                is_active=True,
            )

            db.add(warehouse)
            db.flush()

        # -------------------------------------------------
        # Seed Product
        # -------------------------------------------------

        product = db.scalar(
            select(Product).where(
                Product.sku == "TEST-SKU-001"
            )
        )

        if not product:
            product = Product(
                sku="TEST-SKU-001",
                name="Test Product",
                description="Product for automated tests",
                category_id=category.id,
                price=100.00,
                cost_price=70.00,
                is_active=True,
            )

            db.add(product)
            db.flush()

        # -------------------------------------------------
        # Seed Inventory
        # -------------------------------------------------

        inventory = db.scalar(
            select(Inventory).where(
                Inventory.product_id == product.id,
                Inventory.warehouse_id == warehouse.id,
            )
        )

        if not inventory:
            inventory = Inventory(
                product_id=product.id,
                warehouse_id=warehouse.id,
                available_quantity=100,
                reserved_quantity=0,
                damaged_quantity=0,
                reorder_level=10,
            )

            db.add(inventory)
            db.flush()

        db.commit()
        existing_keys = db.scalars(select(IdempotencyKey)).all()
        
        print("IDEMPOTENCY RECORDS BEFORE TEST:", existing_keys)
        yield

    finally:
        db.close()

    # Clean up after the complete pytest session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def customer_token(client):

    email = "fixture_customer@test.com"
    password = "Test@12345"

    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Fixture Customer",
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code in [200, 201, 400, 409]

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]

@pytest.fixture
def order_id(client, customer_token):

    headers = {
        "Authorization": f"Bearer {customer_token}",
        "Idempotency-Key": "fixture-order-001"
    }

    payload = {
        "warehouse_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "discount": 0,
                "tax": 0
            }
        ]
    }

    response = client.post(
        "/api/orders",
        json=payload,
        headers=headers
    )

    assert response.status_code == 201

    return response.json()["id"]


@pytest.fixture
def manager_token(client):

    email = "fixture_manager@test.com"
    password = "Test@12345"

    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Fixture Manager",
            "email": email,
            "password": password,
            "role": "warehouse_manager",
        },
    )

    assert register_response.status_code in [200, 201, 400, 409]

    login_response = client.post(
        "/api/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


@pytest.fixture
def customer_headers(customer_token):

    return {
        "Authorization": f"Bearer {customer_token}"
    }