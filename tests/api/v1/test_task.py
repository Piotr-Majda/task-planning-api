from collections import Counter
import datetime
import pytest
import random


TASK = {
        "name": "Test Task", 
        "content": "description", 
        "deadline": "2026-03-20T00:00:00",
        "priority": "MAJOR",
        'project_id': 1
}

TASK_SECOND = {
        "name": "Test Task 2", 
        "content": "description", 
        "deadline": "2026-03-20T00:00:00",
        "priority": "MINOR"
}


TASK_THIRD = {
        "name": "Test Task 2", 
        "content": "description", 
        "deadline": "2026-03-20T00:00:00",
        "priority": "MINOR"
}


def generate_task_data() -> dict:
    dt = datetime.datetime(2026, 5, 1) + random.random() * datetime.timedelta(days=30)
    return {
        "name": " ".join([random.choice(['Add', 'Refactor', 'Test']), random.choice(['Feature', 'Docs']), str(random.randint(1, 100))]),
        "content": "description", 
        "deadline": str(dt),
        "priority": random.choice(['MINOR', 'MAJOR', 'CRITICAL', 'BLOCKER'])
}


def test_tasks_create__valid_payload__returns_created_task(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    assert created_task['name'] == TASK['name']
    assert "id" in created_task


def test_tasks_get__existing_task__returns_task(client):
    create_r = client.post("/api/v1/tasks", json=TASK)
    assert create_r.status_code == 200, create_r.json()
    created_task = create_r.json()

    get_r = client.get(f"/api/v1/tasks/{created_task['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_task = get_r.json()
    assert fetched_task['id'] == created_task['id']
    assert fetched_task['name'] == TASK['name']
    assert fetched_task['content'] == TASK['content']
    assert fetched_task['deadline'] == TASK['deadline']
    assert fetched_task['project_id'] == TASK["project_id"]
    assert fetched_task['priority'].upper() == TASK["priority"]
    assert fetched_task['project_id'] == TASK['project_id']


def test_tasks_create__missing_name__returns_422(client):
    task = TASK.copy()
    task['name'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__missing_content__returns_422(client):
    task = TASK.copy()
    task['content'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__missing_priority__returns_422(client):
    task = TASK.copy()
    task['priority'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__missing_deadline__returns_422(client):
    task = TASK.copy()
    task['deadline'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__invalid_priority__returns_422(client):
    task = TASK.copy()
    task['priority'] = 'not minor'
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__hour_only_deadline__normalizes_to_full_time(client):
    task = TASK.copy()
    task['deadline'] = '2026-03-20T10'

    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 200, r.json()

    created_task = r.json()
    assert created_task['deadline'].startswith("2026-03-20T10:00:00")


def test_tasks_create__invalid_deadline_format__returns_422(client):
    task = TASK.copy()
    task['deadline'] = '2026/03/20'

    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__existing_parent_id__creates_child_task(client):
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


def test_tasks_create__nonexistent_parent_id__returns_400(client):
    task_second = TASK_SECOND.copy()
    task_second['parent_id'] = '2'
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 400, s_r.json()

def test_tasks_create__parent_project_mismatch__returns_400(client):
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


def test_tasks_create__same_parent_for_two_children__returns_200(client):
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


def test_tasks_create__second_level_child__returns_200(client):
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


def test_tasks_update__name_change__returns_updated_task(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'name': TASK['name'] + "."})
    assert r.status_code == 200, r.json()
    task = r.json()
    assert created_task['id'] == task['id']
    assert created_task['name'] != task['name']
    assert task['name'] == TASK['name'] + "."


def test_tasks_update__nonexistent_task__returns_404(client):
    r = client.patch(f"/api/v1/tasks/1", json={'name': TASK['name']})
    assert r.status_code == 404, r.json()


def test_tasks_update__empty_payload__returns_200(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={})
    assert r.status_code == 200, r.json()


def test_tasks_update__priority_none__keeps_existing_priority(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': None})
    assert r.status_code == 200, r.json()
    assert r.json()['priority'] == created_task['priority']


def test_tasks_update__priority_empty_string__returns_422(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': ""})
    assert r.status_code == 422, r.json()


def test_tasks_update__priority_invalid_value__returns_422(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': "is minor"})
    assert r.status_code == 422, r.json()


def test_tasks_update__deadline_none__keeps_existing_deadline(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'deadline': None})
    assert r.status_code == 200, r.json()
    assert r.json()['deadline'] == created_task['deadline']


def test_tasks_update__deadline_invalid_value__returns_422(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'deadline': "invalid-date"})
    assert r.status_code == 422, r.json()


def test_tasks_update__self_parent_assignment__returns_400(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = TASK.copy()

    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id'] + 1
    s_r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': created_task['id']})
    assert s_r.status_code == 400, s_r.json()


def test_tasks_update__nonexistent_parent_id__returns_400(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    s_r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': created_task['id'] + 1})
    assert s_r.status_code == 400, s_r.json()


def test_tasks_update__remove_parent__keeps_project_id_unchanged(client):
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


def test_tasks_update__set_parent_without_project_id__inherits_parent_project_id(client):
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


def test_tasks_update__parent_with_different_project__returns_400(client):
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


def test_tasks_update__direct_cycle_in_parent_chain__returns_400(client):
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


def test_tasks_update__deep_cycle_in_parent_chain__returns_400(client):
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


def test_tasks_list__no_tasks_exist__returns_empty_list(client):
    r = client.get("/api/v1/tasks")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_tasks_list__second_page_without_remaining_items__returns_empty_list(client, create_task):
    r = client.get("/api/v1/tasks?page=2")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [[TASK] * 30], indirect=True)
def test_tasks_list__thirty_tasks_page_three__returns_ten_items(client, create_task):
    r = client.get("/api/v1/tasks?page=3")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 10
    expected_ids = [task['id'] for task in create_task[20:30]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [[TASK] * 30], indirect=True)
def test_tasks_list__thirty_tasks_page_four__returns_empty_list(client, create_task):
    r = client.get("/api/v1/tasks?page=4")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_tasks_list__limit_hundred_with_ten_tasks__returns_ten_items(client, create_task):
    r = client.get("/api/v1/tasks?limit=100")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 10
    expected_ids = [task['id'] for task in create_task[0:10]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)

@pytest.mark.parametrize('create_task', [[TASK] * 30], indirect=True)
def test_tasks_list__page_two_limit_five__returns_five_items(client, create_task):
    r = client.get("/api/v1/tasks?page=2&limit=5")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 5
    expected_ids = [task['id'] for task in create_task[5:10]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [[TASK] * 30], indirect=True)
def test_tasks_list__page_three_limit_eleven__returns_eight_items(client, create_task):
    r = client.get("/api/v1/tasks?page=3&limit=11")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 8
    expected_ids = [task['id'] for task in create_task[22:30]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_tasks_list__sort_by_deadline__returns_first_ten_sorted(client, create_task):
    r = client.get("/api/v1/tasks?sort=deadline")
    assert r.status_code == 200, r.json()
    expected = [task['deadline'] for task in create_task]
    present = [task['deadline'] for task in r.json()]
    assert present == sorted(expected)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_tasks_list__sort_by_created_at__returns_first_ten_sorted(client, create_task):
    r = client.get("/api/v1/tasks?sort=created_at")
    assert r.status_code == 200, r.json()
    expected = [task['created_at'] for task in create_task]
    present = [task['created_at'] for task in r.json()]
    assert present == sorted(expected)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_tasks_list__invalid_sort_value__returns_422(client, create_task):
    r = client.get("/api/v1/tasks?sort=deedline")
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_tasks_list__empty_sort_value__returns_422(client, create_task):
    r = client.get("/api/v1/tasks?sort=")
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_tasks_list__sort_deadline_desc__returns_first_ten_sorted_desc(client, create_task):
    r = client.get("/api/v1/tasks?sort=deadline&order=desc")
    assert r.status_code == 200, r.json()
    expected = [task['deadline'] for task in create_task]
    present = [task['deadline'] for task in r.json()]
    assert present == sorted(expected, reverse=True)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_tasks_list__sort_deadline_asc__returns_first_ten_sorted_asc(client, create_task):
    r = client.get("/api/v1/tasks?sort=deadline&order=asc")
    assert r.status_code == 200, r.json()
    expected = [task['deadline'] for task in create_task]
    present = [task['deadline'] for task in r.json()]
    assert present == sorted(expected)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_tasks_list__search_with_deadline_desc_sort__returns_matching_sorted_names(client, create_task):
    expected_names = [task['name'] for task in create_task]

    words = [word for name in expected_names for word in name.split()]
    
    word = Counter(words).most_common(1)[0][0]
    expected_tasks = [task for task in create_task if word in task['name']]
    expected_tasks.sort(key=lambda t: t['deadline'], reverse=True)
    expected_names = [task['name'] for task in expected_tasks]

    r = client.get(f"/api/v1/tasks?search={word}&sort=deadline&order=desc")
    assert r.status_code == 200, r.json()

    present_names = [task['name'] for task in r.json()]

    assert present_names == expected_names[:10]


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_tasks_delete__existing_task__returns_204(client, create_task):
    task = create_task[0]
    r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert r.status_code == 204, r.json()


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_tasks_delete__already_deleted_task__returns_404(client, create_task):
    task = create_task[0]
    delete_r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert delete_r.status_code == 204, delete_r.json()

    r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_tasks_delete__parent_deleted_single_child__child_parent_becomes_none(client, create_task):
    task, task_second = create_task[0:2]
    r= client.patch(f'/api/v1/tasks/{task_second['id']}', json={'parent_id': task['id']})
    assert r.status_code == 200, r.json()
    assert r.json()['parent_id'] == task['id']

    r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert r.status_code == 204, r.json()

    r = client.get(f"/api/v1/tasks/{task_second['id']}")
    assert r.status_code == 200, r.json()
    assert r.json()['parent_id'] == None


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_tasks_delete__parent_deleted_two_children__children_parent_becomes_none(client, create_task):
    task, task_second, task_third = create_task[0:3]
    r= client.patch(f'/api/v1/tasks/{task_second['id']}', json={'parent_id': task['id']})
    assert r.status_code == 200, r.json()
    assert r.json()['parent_id'] == task['id']

    r= client.patch(f'/api/v1/tasks/{task_third['id']}', json={'parent_id': task['id']})
    assert r.status_code == 200, r.json()
    assert r.json()['parent_id'] == task['id']

    r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert r.status_code == 204, r.json()

    r = client.get(f"/api/v1/tasks/{task_second['id']}")
    assert r.status_code == 200, r.json()
    assert r.json()['parent_id'] == None

    r = client.get(f"/api/v1/tasks/{task_third['id']}")
    assert r.status_code == 200, r.json()
    assert r.json()['parent_id'] == None
