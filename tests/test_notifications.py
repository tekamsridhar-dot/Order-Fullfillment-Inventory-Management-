def test_notification_requires_authentication(client):
    response = client.get(
        "/api/notifications"
    )

    assert response.status_code == 401

def test_mark_notification_as_read(
    client,
    customer_token,
):
    headers = {
        "Authorization": f"Bearer {customer_token}"
    }

    response = client.patch(
        "/api/notifications/1/read",
        headers=headers,
    )

    assert response.status_code in [200, 404]