def test_audit_logs_require_authentication(client):
    response = client.get(
        "/api/audit-logs"
    )

    assert response.status_code == 401

def test_customer_cannot_view_audit_logs(
    client,
    customer_token,
):
    headers = {
        "Authorization": f"Bearer {customer_token}"
    }

    response = client.get(
        "/api/audit-logs",
        headers=headers,
    )

    assert response.status_code == 403