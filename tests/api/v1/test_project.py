import pytest

def test_projects_create__without_owner__returns_project_with_owner_none(client, project_payload):
    r = client.post("/api/v1/projects", json=project_payload)
    assert r.status_code == 200, r.json()
    created_project = r.json()
    assert created_project['name'] == project_payload['name']
    assert "id" in created_project


def test_projects_create__existing_owner_id__returns_project_with_owner(client, existing_user, project_payload):
    project_payload.update({"owner_id": existing_user['id']})
    r = client.post("/api/v1/projects", json=project_payload)
    assert r.status_code == 200, r.json()
    created_project = r.json()
    assert created_project['name'] == project_payload['name']
    assert created_project['owner_id'] == project_payload['owner_id']
    assert "id" in created_project


def test_projects_create__nonexistent_owner_id__returns_400(client, project_payload):
    project_payload.update({'owner_id': 1})
    r = client.post("/api/v1/projects", json=project_payload)
    assert r.status_code == 400, r.json()


def test_projects_get__existing_project__returns_project(client, existing_project):
    created_project = existing_project
    get_r = client.get(f"/api/v1/projects/{created_project['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_project = get_r.json()
    assert fetched_project['id'] == created_project['id']
    assert fetched_project['name'] == created_project['name']
    assert fetched_project['owner_id'] == created_project['owner_id']


def test_projects_delete__existing_project__returns_204(client, existing_project):
    project = existing_project
    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 204, r.json()


def test_projects_delete__already_deleted_project__returns_404(client, existing_project):
    project = existing_project
    delete_r = client.delete(f'/api/v1/projects/{project['id']}')
    assert delete_r.status_code == 204, delete_r.json()

    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_task', [[{
        "name": "Test Task",
        "content": "description",
        "deadline": "2026-03-20T00:00:00",
        "priority": "MAJOR",
        "project_id": 1
}] * 10], indirect=True)
def test_projects_delete__tasks_assigned_to_project__orphans_task_project_id(client, existing_project, create_task):
    project = existing_project

    r = client.delete(f'/api/v1/projects/{project['id']}')
    assert r.status_code == 204, r.json()

    r = client.get(f'/api/v1/tasks')
    assert r.status_code == 200, r.json()
    tasks = r.json()
    assert all(task['project_id'] == None for task in tasks), tasks


def test_projects_update__name_change__returns_updated_project(client, existing_project, project_payload):
    created_project = existing_project

    r = client.patch(f"/api/v1/projects/{created_project['id']}", json={'name': project_payload['name'] + "."})
    assert r.status_code == 200, r.json()
    task = r.json()
    assert created_project['id'] == task['id']
    assert created_project['name'] != task['name']
    assert task['name'] == project_payload['name'] + "."


def test_projects_update__owner_change_to_existing_user__returns_200(client, existing_project, existing_user):
    project_id = existing_project['id']
    new_owner_id = existing_user['id']
    r = client.patch(f"/api/v1/projects/{project_id}", json={'owner_id': new_owner_id})
    assert r.status_code == 200, r.json()
    assert r.json()['owner_id'] == new_owner_id

def test_projects_update__owner_change_to_nonexistent_user__returns_400(client, existing_project):
    project = existing_project
    r = client.patch(f"/api/v1/projects/{project['id']}", json={'owner_id': 1})
    assert r.status_code == 400, r.json()


def test_projects_update__owner_set_to_none__returns_200_and_owner_none(client, existing_project):
    project = existing_project
    r = client.patch(f"/api/v1/projects/{project['id']}", json={'owner_id': None})
    assert r.status_code == 200, r.json()
    assert r.json()['owner_id'] is None

def test_projects_update__nonexistent_project__returns_404(client):
    r = client.patch(f"/api/v1/projects/1", json={'name': "Project X"})
    assert r.status_code == 404, r.json()


def test_projects_update__empty_payload__returns_200(client, existing_project):
    r = client.patch(f"/api/v1/projects/{existing_project['id']}", json={})
    assert r.status_code == 200, r.json()


def test_project_add_member__valid_payload__returns_200(client, existing_project, existing_user):
    project_id = existing_project['id']
    new_member_id = existing_user['id']
    r = client.post(f"/api/v1/projects/{project_id}/members", json={'user_id': new_member_id})
    assert r.status_code == 200, r.json()
    assert r.json()['user_id'] == new_member_id
    assert r.json()['project_id'] == project_id


def test_project_add_member__add_member_twice__second_call_returns_409(client, project_with_member):
    project_id = project_with_member['project']['id']
    new_member_id = project_with_member['user']['id']

    r = client.post(f"/api/v1/projects/{project_id}/members", json={'user_id': new_member_id})
    assert r.status_code == 409, r.json()


def test_project_add_member__user_not_exist__returns_404(client, existing_project):
    project_id = existing_project['id']
    r = client.post(f"/api/v1/projects/{project_id}/members", json={'user_id': 1})
    assert r.status_code == 404, r.json()


def test_project_add_member__project_not_exist__returns_404(client, existing_user):
    new_member_id = existing_user['id']
    r = client.post(f"/api/v1/projects/1/members", json={'user_id': new_member_id})
    assert r.status_code == 404, r.json()


def factory_users_payload(number: int):
    return [{"name": f"User {i}", 'password': 'password-correct'} for i in range(1, number + 1)]


@pytest.mark.parametrize('create_users', [factory_users_payload(11)], indirect=True)
def test_project_list_members__eleven_members_given__returns_11_members(client, existing_project, create_users):
    project_id = existing_project['id']
    for member in create_users:
        r = client.post(f"/api/v1/projects/{project_id}/members", json={'user_id': member['id']})
        assert r.status_code == 200, r.json()
    expected_members = sorted([m['id'] for m in create_users])

    r = client.get(f"/api/v1/projects/{project_id}/members")
    assert r.status_code == 200, r.json()
    present_members = [m['user_id'] for m in r.json()]
    assert present_members == expected_members


def test_project_list_members__zero_given__returns_0_members(client, existing_project):
    project_id = existing_project['id']
    r = client.get(f"/api/v1/projects/{project_id}/members")
    assert r.status_code == 200, r.json()
    present_members = [m['user_id'] for m in r.json()]
    assert present_members == []


def test_project_list_members__project_nonexists__returns_404(client):
    r = client.get(f"/api/v1/projects/1/members")
    assert r.status_code == 404, r.json()


def test_project_remove_membership__one_member_present__returns_204(client, project_with_member):
    project_id = project_with_member['project']['id']
    user_id = project_with_member['user']['id']

    r = client.delete(f"/api/v1/projects/{project_id}/members/{user_id}")
    assert r.status_code == 204, r.json()


def test_project_remove_membership__zero_member_present__returns_404(client, existing_project, existing_user):
    project_id = existing_project['id']
    user_id = existing_user['id']

    r = client.delete(f"/api/v1/projects/{project_id}/members/{user_id}")
    assert r.status_code == 404, r.json()
    assert r.json()['code'] == 'membership_not_found'


def test_project_remove_membership__project_nonexists__returns_404(client, existing_user):
    user_id = existing_user['id']

    r = client.delete(f"/api/v1/projects/1/members/{user_id}")
    assert r.status_code == 404, r.json()
    assert r.json()['code'] == 'project_not_found'
