
import json


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


def test_create_without_name(client):
    task = TASK.copy()
    task['name'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_create_without_content(client):
    task = TASK.copy()
    task['content'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_create_without_priority(client):
    task = TASK.copy()
    task['priority'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_create_without_deadline(client):
    task = TASK.copy()
    task['deadline'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_create_invalid_priority(client):
    task = TASK.copy()
    task['priority'] = 'not minor'
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_create_invalid_deadline_format(client):
    task = TASK.copy()
    task['deadline'] = '2026-03-20T10'
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_create_children_task_parent_exist(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    assert created_task['name'] == TASK['name']
    assert "id" in created_task

    task_second = TASK_SECOND.copy()

    task_second['parent_id'] = created_task['id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()
    created_children_task = s_r.json()
    assert created_children_task['name'] == TASK_SECOND['name']
    assert created_children_task['content'] == TASK_SECOND['content']
    assert created_children_task['deadline'] == TASK_SECOND["deadline"]
    assert created_children_task['priority'].upper() == TASK_SECOND["priority"]
    assert created_children_task['parent_id'] == created_task['id']
    assert created_children_task['project_id'] == created_task['project_id']


def test_create_children_task_parent_non_exist(client):
    task_second = TASK_SECOND.copy()
    task_second['parent_id'] = '2'
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 404, s_r.json()

def test_create_children_task_parent_non_consistent_project_id(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    assert created_task['name'] == TASK['name']
    assert "id" in created_task

    task_second = TASK_SECOND.copy()

    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id'] + 1
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 400, s_r.json()


def test_create_two_children_task_same_parent(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK_SECOND.copy()
    
    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    task_third = TASK_THIRD.copy()

    task_third['parent_id'] = created_task['id']
    task_third['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_third)
    assert s_r.status_code == 200, s_r.json()


def test_create_children_second_level(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK_SECOND.copy()

    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    task_third = TASK_THIRD.copy()

    task_third['parent_id'] = s_r.json()['id']
    task_third['project_id'] = s_r.json()['project_id']
    s_r = client.post("/api/v1/tasks", json=task_third)
    assert s_r.status_code == 200, s_r.json()


def test_update_name_task(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'name': TASK['name'] + "."})
    assert r.status_code == 200, r.json()
    task = r.json()
    assert created_task['id'] == task['id']
    assert created_task['name'] != task['name']
    assert task['name'] == TASK['name'] + "."


def test_update_task_not_exist(client):
    r = client.patch(f"/api/v1/tasks/1", json={'name': TASK['name']})
    assert r.status_code == 404, r.json()


def test_update_task_none_params(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={})
    assert r.status_code == 200, r.json()


def test_update_task_priority_to_none_is_not_allowed(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': None})
    assert r.status_code == 422, r.json()


def test_update_task_priority_invalid_data(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': "is minor"})
    assert r.status_code == 422, r.json()


def test_update_task_deadline_to_none_deadline_stay_same(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'deadline': None})
    assert r.status_code == 200, r.json()
    assert r.json()['deadline'] == created_task['deadline']


def test_update_task_deadline_invalid_data(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'deadline': "invalid-date"})
    assert r.status_code == 422, r.json()


def test_update_task_parent_id_to_self(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK.copy()

    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id'] + 1
    s_r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': created_task['id']})
    assert s_r.status_code == 400, s_r.json()


def test_update_task_parent_id_to_not_existing_task(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    s_r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': created_task['id'] + 1})
    assert s_r.status_code == 404, s_r.json()


def test_update_change_parent_to_non_project_id_stay_untouched(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK_SECOND.copy()

    task_second['parent_id'] = created_task['id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    s_r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': None})
    assert s_r.status_code == 200, s_r.json()
    assert s_r.json()['parent_id'] == None
    assert s_r.json()['project_id'] == created_task['project_id']


def test_update_task_change_parent_without_project_id_valid_children_inherence_project_id_from_parent(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK_SECOND.copy()

    task_second['parent_id'] = created_task['id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    s_r = client.patch(f"/api/v1/tasks/{s_r.json()['id']}", json={'parent_id': created_task['id']})
    assert s_r.status_code == 200, s_r.json()
    assert s_r.json()['project_id'] == created_task['project_id']


def test_update_task_parent_diffrent_project_id(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK_SECOND.copy()

    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    s_r = client.patch(f"/api/v1/tasks/{s_r.json()['id']}", json={'parent_id': created_task['project_id'] + 1})
    assert s_r.status_code == 400, s_r.json()


def test_update_parent_cycle_detected(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK_SECOND.copy()

    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': s_r.json()['id']})
    assert r.status_code == 400, r.json()


def test_update_task_deep_cycle_detected(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK_SECOND.copy()

    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    task_third = TASK_THIRD.copy()

    task_third['parent_id'] = s_r.json()['id']
    task_third['project_id'] = s_r.json()['project_id']
    s_r = client.post("/api/v1/tasks", json=task_third)
    assert s_r.status_code == 200, s_r.json()

    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': s_r.json()['id']})
    assert r.status_code == 400, r.json()
