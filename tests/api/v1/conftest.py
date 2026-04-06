import pytest


@pytest.fixture(scope='function')
def create_task(client, request):
    tasks = request.param
    if not isinstance(tasks, list):
        raise ValueError("Given value has incorrect format for creating task")

    for task in tasks:
        r = client.post("/api/v1/tasks", json=task)
        assert r.status_code == 200
