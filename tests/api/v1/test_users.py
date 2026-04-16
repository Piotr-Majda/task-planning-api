import pytest

def test_users_create__valid_payload__returns_created_user(client, user_payload):
    r = client.post("/api/v1/users", json=user_payload)
    assert r.status_code == 200, r.json()
    created_user = r.json()
    assert created_user['name'] == user_payload['name']
    assert "id" in created_user


def test_users_get__existing_user__returns_user(client, existing_user, user_payload):
    created_user = existing_user
    get_r = client.get(f"/api/v1/users/{created_user['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_user = get_r.json()
    assert fetched_user['id'] == created_user['id']
    assert fetched_user['name'] == user_payload['name']


def test_users_delete__existing_user__returns_204(client, existing_user):
    user = existing_user
    r = client.delete(f'/api/v1/users/{user['id']}')
    assert r.status_code == 204, r.json()


def test_users_delete__already_deleted_user__returns_404(client, existing_user):
    user = existing_user
    delete_r = client.delete(f'/api/v1/users/{user['id']}')
    assert delete_r.status_code == 204, delete_r.json()

    r = client.delete(f'/api/v1/users/{user['id']}')
    assert r.status_code == 404, r.json()
    assert "code" in r.json()


@pytest.mark.parametrize('create_project', [[{"name": "Project X"}] * 3], indirect=True)
def test_users_delete__owned_projects_owner_is_set_to_none(client, existing_user, create_project):
    for project in create_project:
        r = client.patch(f"/api/v1/projects/{project['id']}", json={'owner_id': existing_user['id']})
        assert r.status_code == 200, r.json()
        assert r.json()['owner_id'] == existing_user['id']
 
    r = client.delete(f"/api/v1/users/{existing_user['id']}")
    assert r.status_code == 204, r.json()

    for project in create_project:
        r = client.get(f"/api/v1/projects/{project['id']}")
        assert r.status_code == 200, r.json()
        assert r.json()['owner_id'] is None

def test_users_update__name_change__returns_updated_user(client, user_payload):
    r = client.post("/api/v1/users", json=user_payload)
    assert r.status_code == 200, r.json()
    created_user= r.json()

    r = client.patch(f"/api/v1/users/{created_user['id']}", json={'name': created_user['name'] + "."})
    assert r.status_code == 200, r.json()
    user = r.json()
    assert user['id'] == created_user['id']
    assert user['name'] != created_user['name']
    assert user['name'] == created_user['name'] + "."


def test_users_update__nonexistent_user__returns_404(client):
    r = client.patch(f"/api/v1/users/1", json={'name': "User X"})
    assert r.status_code == 404, r.json()
    assert "code" in r.json()


def test_users_update__empty_payload__returns_200(client, existing_user):
    r = client.patch(f"/api/v1/users/{existing_user['id']}", json={})
    assert r.status_code == 200, r.json()