
def test_create_order(client, customer_token):
    headers = {
    "Authorization": f"Bearer {customer_token}",
    "Idempotency-Key": "test-create-order-001"}
    payload = {
        "warehouse_id": 1,
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "discount": 0,
                "tax": 0
            }
        ]
    }

    response = client.post(
    "/api/orders",
    json=payload,
    headers=headers)

    print("ORDER STATUS:", response.status_code)
    print("ORDER RESPONSE:", response.json())

    assert response.status_code == 201

    data = response.json()

    assert data["id"] >= 1
    assert data["order_number"].startswith("ORD-")
    assert data["status"] == "pending"
    assert float(data["total_amount"]) == 200.00

def test_invalid_order_status_transition(client, order_id, manager_token):
    headers = {
        "Authorization": f"Bearer {manager_token}"
    }

    response = client.patch(
        f"/api/orders/{order_id}/status",
        json={
            "status": "delivered"
        },
        headers=headers
    )
    print("STATUS RESPONSE:", response.status_code)
    print("STATUS BODY:", response.json())
    assert response.status_code == 409