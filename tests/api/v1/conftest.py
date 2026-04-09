from typing import List
import pytest


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
