auth_prefix = f"/api/v1/auth"


def test_user_creation(fake_session, fake_user_service, test_client):
    signup_data = {
        "username": "pavan",
        "email": "beyblade4dmaan@gmail.com",
        "password": "pavandudam",
        "firstname": "string",
        "lastname": "string"
    }

    response = test_client.post(url=f"{auth_prefix}/signup", json=signup_data)

    # Proper way to assert
    assert fake_user_service.user_exists.assert_called_once()