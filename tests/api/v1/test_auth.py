import pytest

from app.models.users import UserCreate

AUTH_URL = "/api/v1/auth/token"
ME_URL = "/api/v1/users/me"


@pytest.fixture(scope="function")
def login_payload() -> dict:
    return {
        "username": "user-x",
        "password": "correct-password",
    }


@pytest.fixture(scope="function")
def user_ready_for_login(bear_client, login_payload, create_admin_user, admin_user: UserCreate):
    """
    Credentials for a user that should exist before login succeeds.
    Extend this fixture once you know how accounts and passwords are persisted.
    """
    name, password = admin_user.name, admin_user.password
    r = bear_client.post(AUTH_URL, data={'username': name, 'password': password})
    assert r.status_code == 200, r.json()
    token = r.json()['access_token']
    r = bear_client.post(
        "/api/v1/users",
        json={"name": login_payload["username"], "password": login_payload["password"], 'role': 'user'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert r.status_code == 200, r.json()
    return {
        'name': r.json()['name'],
        'username': r.json()['name'],
        'password': login_payload["password"]
    }


@pytest.fixture(scope="function")
def access_token(bear_client, user_ready_for_login) -> str:
    r = bear_client.post(AUTH_URL, data=user_ready_for_login)
    assert r.status_code == 200, r.json()
    body = r.json()
    assert "access_token" in body
    assert body.get("token_type") == "bearer"
    return body["access_token"]


def test_auth_login__empty_body__returns_422(bear_client):
    r = bear_client.post(AUTH_URL, data={})
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize("missing_field", ["username", "password"])
def test_auth_login__missing_required_field__returns_422(bear_client, login_payload, missing_field):
    payload = {k: v for k, v in login_payload.items() if k != missing_field}
    r = bear_client.post(AUTH_URL, data=payload)
    assert r.status_code == 422, r.json()


def test_auth_login__unknown_credentials__returns_error_with_code(bear_client, login_payload):
    r = bear_client.post(AUTH_URL, data=login_payload)
    assert r.status_code == 401, r.json()
    body = r.json()
    assert body.get("code") == "invalid_credentials"


def test_auth_login__wrong_password__returns_error_with_code(bear_client, user_ready_for_login):
    payload = dict(user_ready_for_login)
    payload["password"] = "wrong-password"
    r = bear_client.post(AUTH_URL, data=payload)
    assert r.status_code == 401, r.json()
    assert r.json().get("code") == "invalid_credentials"


def test_auth_login__valid_credentials__returns_200(bear_client, user_ready_for_login):
    r = bear_client.post(AUTH_URL, data=user_ready_for_login)
    assert r.status_code == 200, r.json()
    body = r.json()
    assert "access_token" in body
    assert body.get("token_type") == "bearer"


def test_auth_login__success__does_not_echo_password(bear_client, user_ready_for_login):
    r = bear_client.post(AUTH_URL, data=user_ready_for_login)
    assert r.status_code == 200, r.json()
    assert user_ready_for_login["password"] not in str(r.json())


def test_users_me__no_token__returns_401_with_code(bear_client):
    r = bear_client.get(ME_URL)
    assert r.status_code == 401, r.json()
    assert "code" in r.json()


def test_users_me__invalid_token__returns_401_invalid_token_code(bear_client):
    r = bear_client.get(ME_URL, headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401, r.json()
    assert r.json().get("code") == "authentication_error"


def test_users_me__valid_token__returns_current_user(bear_client, access_token, login_payload):
    r = bear_client.get(ME_URL, headers={"Authorization": f"Bearer {access_token}"})
    assert r.status_code == 200, r.json()
    body = r.json()
    assert body["name"] == login_payload["username"]
