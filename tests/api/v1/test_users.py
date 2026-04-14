import pytest

USER = {
        "name": "User X", 
}

PROJECT = {
    "name": "Project X", 
}

def test_users_create__valid_payload__returns_created_user(client):
    r = client.post("/api/v1/users", json=USER)
    assert r.status_code == 200, r.json()
    created_user = r.json()
    assert created_user['name'] == USER['name']
    assert "id" in created_user


def test_users_get__existing_user__returns_user(client):
    create_r = client.post("/api/v1/users", json=USER)
    assert create_r.status_code == 200, create_r.json()
    created_user = create_r.json()

    get_r = client.get(f"/api/v1/users/{created_user['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_user = get_r.json()
    assert fetched_user['id'] == created_user['id']
    assert fetched_user['name'] == USER['name']


@pytest.mark.parametrize('create_user', [[USER] * 1], indirect=True)
def test_users_delete__existing_user__returns_204(client, create_user):
    user = create_user[0]
    r = client.delete(f'/api/v1/users/{user['id']}')
    assert r.status_code == 204, r.json()


@pytest.mark.parametrize('create_user', [[USER] * 1], indirect=True)
def test_users_delete__already_deleted_user__returns_404(client, create_user):
    user = create_user[0]
    delete_r = client.delete(f'/api/v1/users/{user['id']}')
    assert delete_r.status_code == 204, delete_r.json()

    r = client.delete(f'/api/v1/users/{user['id']}')
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_user', [[USER] * 1], indirect=True)
@pytest.mark.parametrize('create_project', [[PROJECT] * 3], indirect=True)
def test_users_delete__owned_projects_owner_is_set_to_none(client, create_user, create_project):
    for project in create_project:
        r = client.patch(f"/api/v1/projects/{project['id']}", json={'owner_id': create_user[0]['id']})
        assert r.status_code == 200, r.json()
        assert r.json()['owner_id'] == create_user[0]['id']
 
    r = client.delete(f"/api/v1/users/{create_user[0]['id']}")
    assert r.status_code == 204, r.json()

    for project in create_project:
        r = client.get(f"/api/v1/projects/{project['id']}")
        assert r.status_code == 200, r.json()
        assert r.json()['owner_id'] is None

def test_users_update__name_change__returns_updated_user(client):
    r = client.post("/api/v1/users", json=USER)
    assert r.status_code == 200, r.json()
    created_user= r.json()

    r = client.patch(f"/api/v1/users/{created_user['id']}", json={'name': created_user['name'] + "."})
    assert r.status_code == 200, r.json()
    user = r.json()
    assert user['id'] == created_user['id']
    assert user['name'] != created_user['name']
    assert user['name'] == created_user['name'] + "."


def test_users_update__nonexistent_user__returns_404(client):
    r = client.patch(f"/api/v1/users/1", json={'name': USER['name']})
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_user', [[USER] * 1], indirect=True)
def test_users_update__empty_payload__returns_200(client, create_user):
    r = client.patch(f"/api/v1/users/{create_user[0]['id']}", json={})
    assert r.status_code == 200, r.json()