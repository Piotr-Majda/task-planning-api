import pytest

USER = {
        "name": "Project X", 
}

def test_create_and_get_user(client):
    r = client.post("/api/v1/users", json=USER)
    assert r.status_code == 200, r.json()
    created_user = r.json()
    assert created_user['name'] == USER['name']
    assert "id" in created_user

    get_r = client.get(f"/api/v1/users/{created_user['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_user = get_r.json()
    assert fetched_user['id'] == created_user['id']
    assert fetched_user['name'] == USER['name']


@pytest.mark.parametrize('create_user', [[USER] * 1], indirect=True)
def test_delete_user(client, create_user):
    user = create_user[0]
    r = client.delete(f'/api/v1/users/{user['id']}')
    assert r.status_code == 204, r.json()

    r = client.delete(f'/api/v1/users/{user['id']}')
    assert r.status_code == 404, r.json()


def test_update_name_user(client):
    r = client.post("/api/v1/users", json=USER)
    assert r.status_code == 200, r.json()
    created_user= r.json()

    r = client.patch(f"/api/v1/users/{created_user['id']}", json={'name': created_user['name'] + "."})
    assert r.status_code == 200, r.json()
    user = r.json()
    assert user['id'] == created_user['id']
    assert user['name'] != created_user['name']
    assert user['name'] == created_user['name'] + "."


def test_update_user_not_exist(client):
    r = client.patch(f"/api/v1/users/1", json={'name': USER['name']})
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_user', [[USER] * 1], indirect=True)
def test_update_user_none_params(client, create_user):
    r = client.patch(f"/api/v1/users/{create_user[0]['id']}", json={})
    assert r.status_code == 200, r.json()
