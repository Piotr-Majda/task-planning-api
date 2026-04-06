from typing import List
import pytest


@pytest.fixture(scope='function')
def create_task(client, request) -> List[int]:
    tasks = request.param
    if not isinstance(tasks, list):
        raise ValueError("Given value has incorrect format for creating task")
    created_ids = []
    for task in tasks:
        r = client.post("/api/v1/tasks", json=task)
        assert r.status_code == 200
        created_ids.append(r.json()['id'])
    return created_ids
