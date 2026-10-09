def test_payment_requires_authentication(client):
    response = client.post(
        "/api/payments/1/confirm",
        json={
            "payment_reference": "PAY-TEST-001"
        },
        headers={
            "Idempotency-Key": "payment-test-001"
        }
    )

    assert response.status_code == 401

def test_payment_requires_idempotency_key(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.post(
        "/api/payments/1/confirm",
        json={ "payment_reference": "PAY-TEST-001"},
        headers=headers)
    assert response.status_code == 422