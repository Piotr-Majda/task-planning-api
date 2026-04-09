import pytest

PROJECT = {
        "name": "Project X", 
        'owner_id': 1
}

TASK = {
        "name": "Test Task", 
        "content": "description", 
        "deadline": "2026-03-20T00:00:00",
        "priority": "MAJOR",
        'project_id': 1
}

def test_create_and_get_project(client):
    r = client.post("/api/v1/projects", json=PROJECT)
    assert r.status_code == 200, r.json()
    created_project = r.json()
    assert created_project['name'] == PROJECT['name']
    assert "id" in created_project

    get_r = client.get(f"/api/v1/projects/{created_project['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_project = get_r.json()
    assert fetched_project['id'] == created_project['id']
    assert fetched_project['name'] == PROJECT['name']
    assert fetched_project['owner_id'] == PROJECT['owner_id']


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_delete_task(client, create_project):
    project = create_project[0]
    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 204, r.json()

    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_delete_task_valid_task_with_this_project_has_updated_project_id(client, create_project, create_task):
    project = create_project[0]

    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 204, r.json()

    r = client.get(f'/api/v1/tasks')
    assert r.status_code == 200, r.json()
    tasks = r.json()
    assert all(task['project_id'] == None for task in tasks), tasks


def test_update_name_project(client):
    r = client.post("/api/v1/projects", json=PROJECT)
    assert r.status_code == 200, r.json()
    created_project = r.json()

    r = client.patch(f"/api/v1/projects/{created_project['id']}", json={'name': PROJECT['name'] + "."})
    assert r.status_code == 200, r.json()
    task = r.json()
    assert created_project['id'] == task['id']
    assert created_project['name'] != task['name']
    assert task['name'] == PROJECT['name'] + "."


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_update_change_owner(client, create_project):
    project = create_project[0]
    new_owner_id = PROJECT['owner_id'] + 1
    r = client.patch(f"/api/v1/projects/{project['id']}", json={'owner_id': new_owner_id})
    assert r.status_code == 200, r.json()
    assert r.json()['owner_id'] == new_owner_id


def test_update_project_not_exist(client):
    r = client.patch(f"/api/v1/projects/1", json={'name': PROJECT['name']})
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_update_project_none_params(client, create_project):
    r = client.patch(f"/api/v1/projects/{create_project['id']}", json={})
    assert r.status_code == 200, r.json()

@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_update_project_add_member(client, create_project):
    r = client.patch(f"/api/v1/projects/{create_project['id']}", json={})
    assert r.status_code == 200, r.json()