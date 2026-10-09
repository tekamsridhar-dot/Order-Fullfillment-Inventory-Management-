def test_same_idempotency_key_returns_same_order(
    client,
    customer_token,
):
    headers = {
        "Authorization": f"Bearer {customer_token}",
        "Idempotency-Key": "order-test-001",
    }

    payload = {
        "warehouse_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "discount": 0,
                "tax": 0,
            }
        ],
    }

    response1 = client.post(
        "/api/orders",
        json=payload,
        headers=headers,
    )

    response2 = client.post(
        "/api/orders",
        json=payload,
        headers=headers,
    )

    assert response1.status_code in [200, 201]
    assert response2.status_code in [200, 201]

    assert response1.json()["id"] == response2.json()["id"]

def test_same_key_different_payload_is_rejected(
    client,
    customer_token,
):
    headers = {
        "Authorization": f"Bearer {customer_token}",
        "Idempotency-Key": "order-test-002",
    }

    payload1 = {
        "warehouse_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "discount": 0,
                "tax": 0,
            }
        ],
    }

    payload2 = {
        "warehouse_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 5,
                "discount": 0,
                "tax": 0,
            }
        ],
    }

    response1 = client.post(
        "/api/orders",
        json=payload1,
        headers=headers,
    )

    assert response1.status_code in [200, 201]

    response2 = client.post(
        "/api/orders",
        json=payload2,
        headers=headers,
    )

    assert response2.status_code == 409