def test_protected_endpoint_requires_authentication(client):
    response = client.get("/api/orders")

    assert response.status_code == 401

def test_order_creation_is_idempotent(
    client,
    customer_token
):
    headers = {
        "Authorization": f"Bearer {customer_token}",
        "Idempotency-Key": "test-order-001"
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

    response1 = client.post(
        "/api/orders",
        json=payload,
        headers=headers
    )

    response2 = client.post(
        "/api/orders",
        json=payload,
        headers=headers
    )

    assert response1.status_code in [200, 201]
    assert response2.status_code in [200, 201]

    assert response1.json()["id"] == response2.json()["id"]