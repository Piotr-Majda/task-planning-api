
TASK = {
        "name": "Test Task", 
        "content": "description", 
        "deadline": "2026-03-20T10:00:00",
        "priority": "MAJOR",
        'project_id': 1
}

TASK_SECOND = {
        "name": "Test Task 2", 
        "content": "description", 
        "deadline": "2026-03-20T10:00:00",
        "priority": "MINOR"
}


TASK_THIRD = {
        "name": "Test Task 2", 
        "content": "description", 
        "deadline": "2026-03-20T10:00:00",
        "priority": "MINOR"
}


def test_create_and_get_task(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    assert created_task['name'] == TASK['name']
    assert "id" in created_task

    get_r = client.get(f"/api/v1/tasks/{created_task['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_task = get_r.json()
    assert fetched_task['id'] == created_task['id']
    assert fetched_task['name'] == TASK['name']
    assert fetched_task['content'] == TASK['content']
    assert fetched_task['deadline'] == TASK["deadline"]
    assert fetched_task['project_id'] == TASK["project_id"]
    assert fetched_task['priority'].upper() == TASK["priority"]
    assert fetched_task['project_id'] == TASK['project_id']


def test_create_children_task_parent_exist(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    assert created_task['name'] == TASK['name']
    assert "id" in created_task

    TASK_SECOND['parent_id'] = created_task['id']
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 200, s_r.json()
    created_children_task = s_r.json()
    assert created_children_task['name'] == TASK_SECOND['name']
    assert created_children_task['content'] == TASK_SECOND['content']
    assert created_children_task['deadline'] == TASK_SECOND["deadline"]
    assert created_children_task['priority'].upper() == TASK_SECOND["priority"]
    assert created_children_task['parent_id'] == created_task['id']
    assert created_children_task['project_id'] == created_task['project_id']


def test_create_children_task_parent_non_exist(client):
    TASK_SECOND['parent_id'] = '2'
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 404, s_r.json()

def test_create_children_task_parent_non_consistent_project_id(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    assert created_task['name'] == TASK['name']
    assert "id" in created_task
    TASK_SECOND['parent_id'] = created_task['id']
    TASK_SECOND['project_id'] = created_task['project_id'] + 1
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 400, s_r.json()


def test_create_two_children_task_same_parent(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    TASK_SECOND['parent_id'] = created_task['id']
    TASK_SECOND['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 200, s_r.json()

    TASK_THIRD['parent_id'] = created_task['id']
    TASK_THIRD['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 200, s_r.json()


def test_create_children_second_level(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    TASK_SECOND['parent_id'] = created_task['id']
    TASK_SECOND['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 200, s_r.json()

    TASK_THIRD['parent_id'] = s_r.json()['id']
    TASK_THIRD['project_id'] = s_r.json()['project_id']
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 200, s_r.json()


def test_patch_name_task(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'name': TASK['name'] + "."})
    assert r.status_code == 200, r.json()
    task = r.json()
    assert created_task['id'] == task['id']
    assert created_task['name'] != task['name']
    assert task['name'] == TASK['name'] + "."


def test_update_task_cycle_detected(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    TASK_SECOND['parent_id'] = created_task['id']
    TASK_SECOND['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 200, s_r.json()

    TASK_THIRD['parent_id'] = s_r.json()['id']
    TASK_THIRD['project_id'] = s_r.json()['project_id']
    s_r = client.post("/api/v1/tasks", json=TASK_SECOND)
    assert s_r.status_code == 200, s_r.json()

    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': s_r.json()['id']})
    assert r.status_code == 200, r.json()
