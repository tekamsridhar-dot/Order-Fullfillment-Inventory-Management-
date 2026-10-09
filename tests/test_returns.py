def test_return_requires_delivered_order(
    client,
    customer_token,
    order_id
):
    headers = {
        "Authorization": f"Bearer {customer_token}"
    }

    response = client.post(
        "/api/returns",
        json={
            "order_id": order_id,
            "items": [
                {
                    "order_item_id": 1,
                    "quantity": 1
                }
            ],
            "reason": "Damaged product"
        },
        headers=headers
    )

    assert response.status_code in [400, 409]