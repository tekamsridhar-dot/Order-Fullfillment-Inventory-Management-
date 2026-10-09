def test_product_requires_admin(client):
    response = client.post(
        "/api/products",
        json={
            "sku": "SKU-TEST-001",
            "name": "Test Product",
            "description": "Test product",
            "category_id": 1,
            "price": 100,
            "cost_price": 50
        }
    )

    assert response.status_code in [401, 403]