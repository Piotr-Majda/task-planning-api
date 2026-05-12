from collections import Counter
import datetime
import pytest
import random

def generate_task_data() -> dict:
    dt = datetime.datetime(2026, 5, 1) + random.random() * datetime.timedelta(days=30)
    return {
        "name": " ".join([random.choice(['Add', 'Refactor', 'Test']), random.choice(['Feature', 'Docs']), str(random.randint(1, 100))]),
        "content": "description", 
        "deadline": str(dt),
        "priority": random.choice(['MINOR', 'MAJOR', 'CRITICAL', 'BLOCKER'])
}


def _task_batch(count: int) -> list[dict]:
    return [{
        "name": "Test Task",
        "content": "description",
        "deadline": "2026-03-20T00:00:00",
        "priority": "MAJOR",
    } for _ in range(count)]


def test_tasks_create__valid_payload__returns_created_task(client, task_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    assert created_task['name'] == task_payload['name']
    assert "id" in created_task


def test_tasks_get__existing_task__returns_task(client, existing_task, task_payload):
    created_task = existing_task
    get_r = client.get(f"/api/v1/tasks/{created_task['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_task = get_r.json()
    assert fetched_task['id'] == created_task['id']
    assert fetched_task['name'] == task_payload['name']
    assert fetched_task['content'] == task_payload['content']
    assert fetched_task['deadline'] == task_payload['deadline']
    assert fetched_task['priority'].upper() == task_payload["priority"]


def test_tasks_create__missing_name__returns_422(client, task_payload):
    task = task_payload
    task['name'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__missing_content__returns_422(client, task_payload):
    task = task_payload
    task['content'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__missing_priority__returns_422(client, task_payload):
    task = task_payload
    task['priority'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__missing_deadline__returns_422(client, task_payload):
    task = task_payload
    task['deadline'] = None
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__invalid_priority__returns_422(client, task_payload):
    task = task_payload
    task['priority'] = 'not minor'
    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__hour_only_deadline__normalizes_to_full_time(client, task_payload):
    task = task_payload
    task['deadline'] = '2026-03-20T10'

    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 200, r.json()

    created_task = r.json()
    assert created_task['deadline'].startswith("2026-03-20T10:00:00")


def test_tasks_create__invalid_deadline_format__returns_422(client, task_payload):
    task = task_payload
    task['deadline'] = '2026/03/20'

    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 422, r.json()


def test_tasks_create__existing_parent_id__creates_child_task(client, task_payload, task_second_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    assert created_task['name'] == task_payload['name']
    assert "id" in created_task

    task_second = task_second_payload

    task_second['parent_id'] = created_task['id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()
    created_children_task = s_r.json()
    assert created_children_task['name'] == task_second_payload['name']
    assert created_children_task['content'] == task_second_payload['content']
    assert created_children_task['deadline'] == task_second_payload["deadline"]
    assert created_children_task['priority'].upper() == task_second_payload["priority"]
    assert created_children_task['parent_id'] == created_task['id']
    assert created_children_task['project_id'] == created_task['project_id']


def test_tasks_create__nonexistent_parent_id__returns_400(client, task_second_payload):
    task_second = task_second_payload
    task_second['parent_id'] = '2'
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 400, s_r.json()
    assert s_r.json()["code"] == "reference_parent_task_not_found"

def test_tasks_create__parent_project_mismatch__returns_400(client, task_with_project_assignment, task_second_payload):
    task, project = task_with_project_assignment['task'], task_with_project_assignment['project']

    task_second = task_second_payload

    task_second['parent_id'] = task['id']
    task_second['project_id'] = project['id'] + 1
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 400, s_r.json()


def test_tasks_create__same_parent_for_two_children__returns_200(client, task_payload, task_second_payload, task_third_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = task_second_payload
    
    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    task_third = task_third_payload

    task_third['parent_id'] = created_task['id']
    task_third['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_third)
    assert s_r.status_code == 200, s_r.json()


def test_tasks_create__second_level_child__returns_200(client, task_payload, task_second_payload, task_third_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = task_second_payload

    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    task_third = task_third_payload

    task_third['parent_id'] = s_r.json()['id']
    task_third['project_id'] = s_r.json()['project_id']
    s_r = client.post("/api/v1/tasks", json=task_third)
    assert s_r.status_code == 200, s_r.json()


def test_tasks_update__name_change__returns_updated_task(client, existing_task, task_payload):
    created_task = existing_task
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'name': task_payload['name'] + "."})
    assert r.status_code == 200, r.json()
    task = r.json()
    assert created_task['id'] == task['id']
    assert created_task['name'] != task['name']
    assert task['name'] == task_payload['name'] + "."


def test_tasks_update__nonexistent_task__returns_404(client):
    r = client.patch(f"/api/v1/tasks/1", json={'name': "Test Task"})
    assert r.status_code == 404, r.json()
    assert "code" in r.json()


def test_tasks_update__empty_payload__returns_200(client, existing_task):
    created_task = existing_task
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={})
    assert r.status_code == 200, r.json()


def test_tasks_update__priority_none__returns_422(client, existing_task):
    created_task = existing_task
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': None})
    assert r.status_code == 422, r.json()


def test_tasks_update__priority_empty_string__returns_422(client, existing_task):
    created_task = existing_task
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': ""})
    assert r.status_code == 422, r.json()


def test_tasks_update__priority_invalid_value__returns_422(client, existing_task):
    created_task = existing_task
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': "is minor"})
    assert r.status_code == 422, r.json()


def test_tasks_update__deadline_none__returns_422(client, existing_task):
    created_task = existing_task
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'deadline': None})
    assert r.status_code == 422, r.json()


def test_tasks_update__deadline_invalid_value__returns_422(client, existing_task):
    created_task = existing_task
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'deadline': "invalid-date"})
    assert r.status_code == 422, r.json()


def test_tasks_update__self_parent_assignment__returns_400(client, task_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    s_r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': created_task['id']})
    assert s_r.status_code == 400, s_r.json()


def test_tasks_update__nonexistent_parent_id__returns_400(client, task_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    s_r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': created_task['id'] + 1})
    assert s_r.status_code == 400, s_r.json()
    assert s_r.json()["code"] == "reference_parent_task_not_found"


def test_tasks_update__remove_parent__keeps_project_id_unchanged(client, task_payload, task_second_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = task_second_payload
    task_second['parent_id'] = created_task['id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    s_r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': None})
    assert s_r.status_code == 200, s_r.json()
    assert s_r.json()['parent_id'] == None
    assert s_r.json()['project_id'] == created_task['project_id']


def test_tasks_update__set_parent_without_project_id__inherits_parent_project_id(client, task_payload, task_second_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = task_second_payload
    task_second['parent_id'] = created_task['id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    s_r = client.patch(f"/api/v1/tasks/{s_r.json()['id']}", json={'parent_id': created_task['id']})
    assert s_r.status_code == 200, s_r.json()
    assert s_r.json()['project_id'] == created_task['project_id']


def test_tasks_update__parent_with_different_project__returns_400(client, task_with_project_assignment, task_second_payload):
    task = task_with_project_assignment['task']

    task_second = task_second_payload
    task_second['parent_id'] = task['id']
    task_second['project_id'] = task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    s_r = client.patch(f"/api/v1/tasks/{s_r.json()['id']}", json={'parent_id': task['project_id'] + 1})
    assert s_r.status_code == 400, s_r.json()


def test_tasks_update__direct_cycle_in_parent_chain__returns_400(client, task_payload, task_second_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = task_second_payload
    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': s_r.json()['id']})
    assert r.status_code == 400, r.json()


def test_tasks_update__deep_cycle_in_parent_chain__returns_400(client, task_payload, task_second_payload, task_third_payload):
    r = client.post("/api/v1/tasks", json=task_payload)
    assert r.status_code == 200, r.json()
    created_task = r.json()

    task_second = task_second_payload
    task_second['parent_id'] = created_task['id']
    task_second['project_id'] = created_task['project_id']
    s_r = client.post("/api/v1/tasks", json=task_second)
    assert s_r.status_code == 200, s_r.json()

    task_third = task_third_payload
    task_third['parent_id'] = s_r.json()['id']
    task_third['project_id'] = s_r.json()['project_id']
    s_r = client.post("/api/v1/tasks", json=task_third)
    assert s_r.status_code == 200, s_r.json()

    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'parent_id': s_r.json()['id']})
    assert r.status_code == 400, r.json()

def test_tasks_update__leaf_task_status_change_to_done__returns_200(client, existing_task):
    task_id = existing_task['id']
    r = client.patch(f"/api/v1/tasks/{task_id}", json={'status': 'done'})
    assert r.status_code == 200
    returned_task = r.json()
    assert returned_task['status'] == 'done'

def test_tasks_update__parent_with_todo_child_status_change_to_done__returns_400(client, existing_task, existing_child_task):
    task_id = existing_task['id']
    r = client.patch(f"/api/v1/tasks/{task_id}", json={'status': 'done'})
    assert r.status_code == 400
    assert r.json()['code'] == 'child_task_not_done'

def test_tasks_update__parent_with_all_children_done_status_change_to_done__returns_200(client, existing_task, existing_child_task_status_done):
    task_id = existing_task['id']
    r = client.patch(f"/api/v1/tasks/{task_id}", json={'status': 'done'})
    assert r.status_code == 200
    assert r.json()['status'] == 'done'

def test_tasks_update__parent_with_one_unfinished_child_status_change_to_done__returns_400(client, existing_task, existing_child_task_status_done, existing_second_child_task_status_in_progress):
    task_id = existing_task['id']
    r = client.patch(f"/api/v1/tasks/{task_id}", json={'status': 'done'})
    assert r.status_code == 400
    assert r.json()['code'] == 'child_task_not_done'

def test_tasks_update__parent_status_change_to_in_progress_with_todo_child__returns_200(client, existing_task, existing_child_task):
    task_id = existing_task['id']
    r = client.patch(f"/api/v1/tasks/{task_id}", json={'status': 'in_progress'})
    assert r.status_code == 200
    assert r.json()['status'] == 'in_progress'

def test_tasks_create__todo_child_with_done_parent__returns_400(client, existing_task_status_done, task_payload):
    payload = dict(task_payload)
    payload['parent_id'] = existing_task_status_done['id']

    r = client.post("/api/v1/tasks", json=payload)
    assert r.status_code == 400
    assert r.json()['code'] == 'new_subtask_not_allowed'

def test_tasks_update__todo_task_parent_change_to_done_parent__returns_400(client, existing_task_status_done, existing_task_second):
    r = client.patch(f'/api/v1/tasks/{existing_task_second['id']}', json={'parent_id': existing_task_status_done['id']})
    assert r.status_code == 400
    assert r.json()['code'] == 'new_subtask_not_allowed'

def test_tasks_update__done_child_with_done_parent_status_change_to_in_progress__returns_400(client, done_parent_with_done_child):
    child = done_parent_with_done_child["child"]
    r = client.patch(f"/api/v1/tasks/{child['id']}", json={'status': 'in_progress'})
    assert r.status_code == 400
    assert r.json()['code'] == 'change_finished_task_status_not_allowed'

def test_tasks_list__no_tasks_exist__returns_empty_list(client):
    r = client.get("/api/v1/tasks")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [_task_batch(10)], indirect=True)
def test_tasks_list__second_page_without_remaining_items__returns_empty_list(client, create_task):
    r = client.get("/api/v1/tasks?page=2")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [_task_batch(30)], indirect=True)
def test_tasks_list__thirty_tasks_page_three__returns_ten_items(client, create_task):
    r = client.get("/api/v1/tasks?page=3")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 10
    expected_ids = [task['id'] for task in create_task[20:30]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [_task_batch(30)], indirect=True)
def test_tasks_list__thirty_tasks_page_four__returns_empty_list(client, create_task):
    r = client.get("/api/v1/tasks?page=4")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [_task_batch(10)], indirect=True)
def test_tasks_list__limit_hundred_with_ten_tasks__returns_ten_items(client, create_task):
    r = client.get("/api/v1/tasks?limit=100")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 10
    expected_ids = [task['id'] for task in create_task[0:10]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)

@pytest.mark.parametrize('create_task', [_task_batch(30)], indirect=True)
def test_tasks_list__page_two_limit_five__returns_five_items(client, create_task):
    r = client.get("/api/v1/tasks?page=2&limit=5")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 5
    expected_ids = [task['id'] for task in create_task[5:10]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [_task_batch(30)], indirect=True)
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


@pytest.mark.parametrize('create_task', [_task_batch(10)], indirect=True)
def test_tasks_delete__existing_task__returns_204(client, create_task):
    task = create_task[0]
    r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert r.status_code == 204, r.json()


@pytest.mark.parametrize('create_task', [_task_batch(10)], indirect=True)
def test_tasks_delete__already_deleted_task__returns_404(client, create_task):
    task = create_task[0]
    delete_r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert delete_r.status_code == 204, delete_r.json()

    r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert r.status_code == 404, r.json()
    assert r.json()["code"] == "task_not_found"


@pytest.mark.parametrize('create_task', [_task_batch(10)], indirect=True)
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


@pytest.mark.parametrize('create_task', [_task_batch(10)], indirect=True)
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

def test_task_owner_assignment__owner_change_to_existing_membership__returns_200(client, task_with_project_assignment_and_member):
    task_id = task_with_project_assignment_and_member['task']['id']
    new_owner_id = task_with_project_assignment_and_member['user']['id']
    r = client.patch(f"/api/v1/tasks/{task_id}", json={'owner_id': new_owner_id})
    assert r.status_code == 200, r.json()
    assert r.json()['owner_id'] == new_owner_id

def test_task_owner_assignment__owner_change_to_existing_user_but_without_membership__returns_400(client, task_with_project_assignment, existing_user):
    task_id = task_with_project_assignment['task']['id']
    new_owner_id = existing_user['id']
    r = client.patch(f"/api/v1/tasks/{task_id}", json={'owner_id': new_owner_id})
    assert r.status_code == 400, r.json()
    assert r.json()['code'] == "membership_not_found"

def test_task_owner_assignment__owner_change_to_nonexistent_user__returns_400(client, task_with_project_assignment):
    task = task_with_project_assignment['task']
    r = client.patch(f"/api/v1/tasks/{task['id']}", json={'owner_id': 1})
    assert r.status_code == 400, r.json()
    assert r.json()['code'] == 'owner_not_found'

def test_task_owner_assignment__project_change_to_nonexistent_project__returns_400(client, task_with_project_assignment):
    task, project = task_with_project_assignment['task'], task_with_project_assignment['project']
    r = client.patch(f"/api/v1/tasks/{task['id']}", json={'project_id': project['id'] + 1})
    assert r.status_code == 400, r.json()
    assert r.json()['code'] == 'project_not_found'

def test_task_owner_assignment__owner_set_to_none__returns_200_and_owner_none(client, task_with_project_assignment):
    task = task_with_project_assignment['task']
    r = client.patch(f"/api/v1/tasks/{task['id']}", json={'owner_id': None})
    assert r.status_code == 200, r.json()
    assert r.json()['owner_id'] is None

def test_task_owner_assignment__project_change_to_where_owner_is_not_member__returns_400(client, task_with_project_and_owner_assignment, existing_project_2):
    task= task_with_project_and_owner_assignment['task']
    r = client.patch(f"/api/v1/tasks/{task['id']}", json={'project_id': existing_project_2['id']})
    assert r.status_code == 400, r.json()
    assert r.json()['code'] == 'membership_not_found'

def test_task_owner_assignment__owner_set_to_none_and_project_change__returns_200(client, task_with_project_and_owner_assignment, existing_project_2):
    task = task_with_project_and_owner_assignment["task"]
    new_project_id = existing_project_2["id"]
    r = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"owner_id": None, "project_id": new_project_id},
    )
    assert r.status_code == 200, r.json()
    body = r.json()
    assert body["owner_id"] is None
    assert body["project_id"] == new_project_id


def test_task_owner_assignment__project_change_without_owner_in_payload__owner_not_member__returns_400(client, task_with_project_and_owner_assignment, existing_project_2):
    task = task_with_project_and_owner_assignment["task"]
    r = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"project_id": existing_project_2["id"]},
    )
    assert r.status_code == 400, r.json()
    assert r.json()["code"] == "membership_not_found"


def test_task_owner_assignment__create_task_owner_without_membership__returns_400(client, existing_project, existing_user, task_payload):
    payload = dict(task_payload)
    payload["project_id"] = existing_project["id"]
    payload["owner_id"] = existing_user["id"]
    r = client.post("/api/v1/tasks", json=payload)
    assert r.status_code == 400, r.json()
    assert r.json()["code"] == "membership_not_found"

def test_task_owner_assignment__create_task_nonexistent_owner__returns_400(client, existing_project, task_payload):
    payload = dict(task_payload)
    payload["project_id"] = existing_project["id"]
    payload["owner_id"] = 999_999
    r = client.post("/api/v1/tasks", json=payload)
    assert r.status_code == 400, r.json()
    assert r.json()["code"] in {"owner_not_found", "user_not_found"}

def test_task_owner_assignment__create_task_without_project_and_existing_owner__returns_200(client, existing_user, task_payload):
    payload = dict(task_payload)
    payload["owner_id"] = existing_user["id"]
    r = client.post("/api/v1/tasks", json=payload)
    assert r.status_code == 200, r.json()
    assert r.json()["owner_id"] == existing_user["id"]
    assert r.json()["project_id"] is None

def test_task_owner_assignment__create_task_without_project_and_nonexistent_owner__returns_400(client, task_payload):
    payload = dict(task_payload)
    payload["owner_id"] = 999_999
    r = client.post("/api/v1/tasks", json=payload)
    assert r.status_code == 400, r.json()
    assert r.json()["code"] in {"owner_not_found", "user_not_found"}

def test_task_owner_assignment__task_with_project_fixture__returns_consistent_project_id(task_with_project_assignment):
    task = task_with_project_assignment["task"]
    project = task_with_project_assignment["project"]
    assert task["project_id"] == project["id"]
