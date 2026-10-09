def test_reservation_cannot_exceed_available_inventory(
    client,
    customer_token
):
    headers = {
        "Authorization": f"Bearer {customer_token}"
    }

    response = client.post("/api/inventory/reserve",
    json={
        "product_id": 1,
        "warehouse_id": 1,
        "quantity": 999999,
        "reference_id": 1
    },
    headers=headers)
    assert response.status_code == 409