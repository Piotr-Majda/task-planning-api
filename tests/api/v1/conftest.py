from typing import List
import pytest


@pytest.fixture(scope='function')
def project_payload() -> dict:
    return {
        "name": "Project X",
    }


@pytest.fixture(scope='function')
def user_payload() -> dict:
    return {
        "name": "User X",
    }


@pytest.fixture(scope='function')
def task_payload() -> dict:
    return {
        "name": "Test Task",
        "content": "description",
        "deadline": "2026-03-20T00:00:00",
        "priority": "MAJOR",
    }


@pytest.fixture(scope='function')
def task_second_payload() -> dict:
    return {
        "name": "Test Task 2",
        "content": "description",
        "deadline": "2026-03-20T00:00:00",
        "priority": "MINOR",
    }


@pytest.fixture(scope='function')
def task_third_payload() -> dict:
    return {
        "name": "Test Task 2",
        "content": "description",
        "deadline": "2026-03-20T00:00:00",
        "priority": "MINOR",
    }


@pytest.fixture(scope='function')
def create_task(client, request) -> List[dict]:
    tasks = request.param
    if not isinstance(tasks, list):
        raise ValueError("Given value has incorrect format for creating task")
    created = []
    for task in tasks:
        r = client.post("/api/v1/tasks", json=task)
        assert r.status_code == 200
        created.append(r.json())
    return created


@pytest.fixture(scope='function')
def create_project(client, request) -> List[dict]:
    projects = request.param
    if not isinstance(projects, list):
        raise ValueError("Given value has incorrect format for creating project")
    created = []
    for p in projects:
        r = client.post("/api/v1/projects", json=p)
        assert r.status_code == 200
        created.append(r.json())
    return created


@pytest.fixture(scope='function')
def create_user(client, request) -> List[dict]:
    users = request.param
    if not isinstance(users, list):
        raise ValueError("Given value has incorrect format for creating user")
    created = []
    for p in users:
        r = client.post("/api/v1/users", json=p)
        assert r.status_code == 200
        created.append(r.json())
    return created


@pytest.fixture(scope='function')
def create_project_member(client):
    def _create(project_id: int, user_id: int) -> dict:
        r = client.post(f"/api/v1/projects/{project_id}/members", json={"user_id": user_id})
        assert r.status_code == 200, r.json()
        return r.json()
    return _create


@pytest.fixture(scope='function')
def existing_project(client, project_payload):
    r = client.post("/api/v1/projects", json=project_payload)
    assert r.status_code == 200, r.json()
    return r.json()


@pytest.fixture(scope='function')
def existing_project_2(client, project_payload):
    r = client.post("/api/v1/projects", json=project_payload)
    assert r.status_code == 200, r.json()
    return r.json()


@pytest.fixture(scope='function')
def existing_user(client, user_payload):
    r = client.post("/api/v1/users", json=user_payload)
    assert r.status_code == 200, r.json()
    return r.json()


@pytest.fixture(scope='function')
def existing_task(client, task_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    return r.json()


@pytest.fixture(scope='function')
def project_with_member(existing_project, existing_user, create_project_member):
    membership = create_project_member(existing_project["id"], existing_user["id"])
    return {
        "project": existing_project,
        "user": existing_user,
        "membership": membership,
    }

@pytest.fixture()
def assign_task_to_project(client):
    def assign(task_id: int, project_id: int):
        r = client.patch(f"/api/v1/tasks/{task_id}", json={'project_id': project_id})
        assert r.status_code == 200, r.json()
        return r.json()
    return assign


@pytest.fixture()
def task_with_project_assignment(existing_project, existing_task, assign_task_to_project):
    task = assign_task_to_project(existing_task["id"], existing_project['id'])
    return {
        "project": existing_project,
        "task": task,
    }

@pytest.fixture(scope='function')
def task_with_project_assignment_and_member(project_with_member, existing_task, assign_task_to_project):
    task = assign_task_to_project(existing_task["id"], project_with_member["project"]['id'])
    return {
        "project": project_with_member['project'],
        "user": project_with_member['user'],
        "task": task,
    }

@pytest.fixture()
def assign_owner_to_task(client):
    def assign(user_id: int, task_id: int):
        r = client.patch(f"/api/v1/tasks/{task_id}", json={'owner_id': user_id})
        assert r.status_code == 200, r.json()
        return r.json()
    return assign

@pytest.fixture(scope='function')
def task_with_project_and_owner_assignment(task_with_project_assignment_and_member, assign_owner_to_task):
    task = task_with_project_assignment_and_member['task']
    user = task_with_project_assignment_and_member['user']
    project = task_with_project_assignment_and_member['project']

    task = assign_owner_to_task(user_id=user['id'], task_id=task["id"])
    return {
        "project": project,
        "user": user,
        "task": task,
    }
