def test_register_customer(client):
    payload = {
        "name": "Test Customer",
        "email": "customer@test.com",
        "password": "Test@12345"
    }

    response = client.post(
        "/api/auth/register",
        json=payload
    )

    print(response.json())

    assert response.status_code in [200, 201]
def test_login_customer(client):
    register_payload = {
        "name": "Login Customer",
        "email": "login@test.com",
        "password": "Test@12345"
    }

    register_response = client.post(
        "/api/auth/register",
        json=register_payload
    )

    print("Register:", register_response.status_code)
    print("Register body:", register_response.json())

    response = client.post(
        "/api/auth/login",
        data={
            "username": "login@test.com",
            "password": "Test@12345"
        }
    )

    print("Login:", response.status_code)
    print("Login body:", response.json())

    assert response.status_code == 200
    
def test_login_invalid_password(client):
    payload = {
        "username": "unknown@test.com",
        "password": "WrongPassword"
    }

    response = client.post(
        "/api/auth/login",
        data=payload
    )

    assert response.status_code in [401, 403]