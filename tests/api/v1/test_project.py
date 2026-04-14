import pytest

PROJECT = {
        "name": "Project X", 
}


PROJECT_1 = {
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

USER = {
        "name": "User X", 
}

def test_projects_create__without_owner__returns_project_with_owner_none(client):
    r = client.post("/api/v1/projects", json=PROJECT)
    assert r.status_code == 200, r.json()
    created_project = r.json()
    assert created_project['name'] == PROJECT['name']
    assert "id" in created_project


@pytest.mark.parametrize('create_user', [[USER] * 1], indirect=True)
def test_projects_create__existing_owner_id__returns_project_with_owner(client, create_user):
    project_payload = PROJECT.copy()
    project_payload.update({"owner_id": create_user[0]['id']})
    r = client.post("/api/v1/projects", json=project_payload)
    assert r.status_code == 200, r.json()
    created_project = r.json()
    assert created_project['name'] == project_payload['name']
    assert created_project['owner_id'] == project_payload['owner_id']
    assert "id" in created_project


def test_projects_create__nonexistent_owner_id__returns_400(client):
    r = client.post("/api/v1/projects", json=PROJECT_1)
    assert r.status_code == 400, r.json()


def test_projects_get__existing_project__returns_project(client):
    create_r = client.post("/api/v1/projects", json=PROJECT)
    assert create_r.status_code == 200, create_r.json()
    created_project = create_r.json()

    get_r = client.get(f"/api/v1/projects/{created_project['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_project = get_r.json()
    assert fetched_project['id'] == created_project['id']
    assert fetched_project['name'] == created_project['name']
    assert fetched_project['owner_id'] == created_project['owner_id']


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_projects_delete__existing_project__returns_204(client, create_project):
    project = create_project[0]
    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 204, r.json()


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_projects_delete__already_deleted_project__returns_404(client, create_project):
    project = create_project[0]
    delete_r = client.delete(f'/api/v1/projects/{project['id']}')
    assert delete_r.status_code == 204, delete_r.json()

    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_projects_delete__tasks_assigned_to_project__orphans_task_project_id(client, create_project, create_task):
    project = create_project[0]

    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 204, r.json()

    r = client.get(f'/api/v1/tasks')
    assert r.status_code == 200, r.json()
    tasks = r.json()
    assert all(task['project_id'] == None for task in tasks), tasks


def test_projects_update__name_change__returns_updated_project(client):
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
@pytest.mark.parametrize('create_user', [[USER] * 1], indirect=True)
def test_projects_update__owner_change_to_existing_user__returns_200(client, create_project, create_user):
    project_id = create_project[0]['id']
    new_owner_id = create_user[0]['id']
    r = client.patch(f"/api/v1/projects/{project_id}", json={'owner_id': new_owner_id})
    assert r.status_code == 200, r.json()
    assert r.json()['owner_id'] == new_owner_id

@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_projects_update__owner_change_to_nonexistent_user__returns_400(client, create_project):
    project = create_project[0]
    r = client.patch(f"/api/v1/projects/{project['id']}", json={'owner_id': 1})
    assert r.status_code == 400, r.json()


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_projects_update__owner_set_to_none__returns_200_and_owner_none(client, create_project):
    project = create_project[0]
    r = client.patch(f"/api/v1/projects/{project['id']}", json={'owner_id': None})
    assert r.status_code == 200, r.json()
    assert r.json()['owner_id'] is None

def test_projects_update__nonexistent_project__returns_404(client):
    r = client.patch(f"/api/v1/projects/1", json={'name': PROJECT['name']})
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_project', [[PROJECT] * 1], indirect=True)
def test_projects_update__empty_payload__returns_200(client, create_project):
    r = client.patch(f"/api/v1/projects/{create_project[0]['id']}", json={})
    assert r.status_code == 200, r.json()
