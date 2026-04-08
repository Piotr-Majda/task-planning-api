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
    assert fetched_task['deadline'] == TASK['deadline']
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


def test_create_deadline_without_minutes_and_seconds(client):
    task = TASK.copy()
    task['deadline'] = '2026-03-20T10'

    r = client.post("/api/v1/tasks", json=task)
    assert r.status_code == 200, r.json()

    created_task = r.json()
    assert created_task['deadline'].startswith("2026-03-20T10:00:00")


def test_create_deadline_invalid_format(client):
    task = TASK.copy()
    task['deadline'] = '2026/03/20'

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
    assert s_r.status_code == 400, s_r.json()

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


def test_update_task_priority_to_none_no_brings_effect(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': None})
    assert r.status_code == 200, r.json()
    assert r.json()['priority'] == created_task['priority']


def test_update_task_priority_to_empty_string_is_not_allowed(client):
    r = client.post("/api/v1/tasks", json=TASK)
    assert r.status_code == 200, r.json()
    created_task = r.json()
    
    r = client.patch(f"/api/v1/tasks/{created_task['id']}", json={'priority': ""})
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


def test_update_parent_self_assignment_is_not_allowed(client):
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
    assert s_r.status_code == 400, s_r.json()


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


def test_get_tasks_no_task_present(client):
    r = client.get("/api/v1/tasks")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_get_tasks_ten_task_present_ten_return(client, create_task):
    r = client.get("/api/v1/tasks")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 10


@pytest.mark.parametrize('create_task', [[TASK] * 11], indirect=True)
def test_get_tasks_eleven_task_present_ten_return_valid_default_pagination_number(client, create_task):
    r = client.get("/api/v1/tasks")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 10
    expected_ids = [task['id'] for task in create_task[:10]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_get_tasks_ten_task_present_try_get_from_page_0_validate_is_not_allowed(client, create_task):
    r = client.get("/api/v1/tasks?page=0")
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_get_tasks_ten_task_present_get_zero_tasks_from_page_2(client, create_task):
    r = client.get("/api/v1/tasks?page=2")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [[TASK] * 30], indirect=True)
def test_get_tasks_threeten_task_present_get_10_task_from_page_3(client, create_task):
    r = client.get("/api/v1/tasks?page=3")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 10
    expected_ids = [task['id'] for task in create_task[20:30]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [[TASK] * 30], indirect=True)
def test_get_tasks_threeten_task_present_get_0_task_from_page_4(client, create_task):
    r = client.get("/api/v1/tasks?page=4")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 0


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_get_tasks_ten_task_try_get_with_limit_zero_validate_is_not_allowed(client, create_task):
    r = client.get("/api/v1/tasks?limit=0")
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_get_tasks_ten_task_ge_ten_tasks_with_limit_100(client, create_task):
    r = client.get("/api/v1/tasks?limit=100")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 10
    expected_ids = [task['id'] for task in create_task[0:10]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)

@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_get_tasks_ten_task_try_get_task_with_limit_101_validate_is_not_allowed(client, create_task):
    r = client.get("/api/v1/tasks?limit=101")
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize('create_task', [[TASK] * 30], indirect=True)
def test_get_tasks_threeten_task_present_get_5_task_from_page_2_with_limit_5(client, create_task):
    r = client.get("/api/v1/tasks?page=2&limit=5")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 5
    expected_ids = [task['id'] for task in create_task[5:10]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [[TASK] * 30], indirect=True)
def test_get_tasks_threeten_task_present_get_8_task_from_page_3_with_limit_11(client, create_task):
    r = client.get("/api/v1/tasks?page=3&limit=11")
    assert r.status_code == 200, r.json()
    assert len(r.json()) == 8
    expected_ids = [task['id'] for task in create_task[22:30]]
    present_ids = [task['id'] for task in r.json()]
    assert present_ids == sorted(expected_ids)


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_with_validate_sort_by_name_by_default(client, create_task):
    r = client.get("/api/v1/tasks")
    assert r.status_code == 200, r.json()
    excepted_names = [task['name'] for task in create_task]
    present_names = [task['name'] for task in r.json()]
    assert present_names == sorted(excepted_names)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_with_validate_sort_by_deadline(client, create_task):
    r = client.get("/api/v1/tasks?sort=deadline")
    assert r.status_code == 200, r.json()
    excepted = [task['deadline'] for task in create_task]
    present = [task['deadline'] for task in r.json()]
    assert present == sorted(excepted)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_with_validate_sort_by_created_at(client, create_task):
    r = client.get("/api/v1/tasks?sort=created_at")
    assert r.status_code == 200, r.json()
    excepted = [task['created_at'] for task in create_task]
    present = [task['created_at'] for task in r.json()]
    assert present == sorted(excepted)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_with_validate_invalid_sort_value(client, create_task):
    r = client.get("/api/v1/tasks?sort=deedline")
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_with_validate_not_allowed_empty_sort_value(client, create_task):
    r = client.get("/api/v1/tasks?sort=")
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_with_validate_sort_descendense(client, create_task):
    r = client.get("/api/v1/tasks?sort=deadline&order=desc")
    assert r.status_code == 200, r.json()
    excepted = [task['deadline'] for task in create_task]
    present = [task['deadline'] for task in r.json()]
    assert present == sorted(excepted, reverse=True)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_with_validate_sort_asc(client, create_task):
    r = client.get("/api/v1/tasks?sort=deadline&order=asc")
    assert r.status_code == 200, r.json()
    excepted = [task['deadline'] for task in create_task]
    present = [task['deadline'] for task in r.json()]
    assert present == sorted(excepted)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_with_validate_sort_invalid_value(client, create_task):
    r = client.get("/api/v1/tasks?sort=deadline&order=invalid")
    assert r.status_code == 422, r.json()


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_search_by_most_common_word(client, create_task):
    excepted_names = [task['name'] for task in create_task]

    words = [word for name in excepted_names for word in name.split()]
    
    word = Counter(words).most_common(1)[0][0]
    excepted_names = [name for name in excepted_names if word in name]

    r = client.get(f"/api/v1/tasks?search={word}")
    assert r.status_code == 200, r.json()

    present_names = [task['name'] for task in r.json()]
    assert present_names == sorted(excepted_names)[:10]


@pytest.mark.parametrize('create_task', [[generate_task_data() for t in range(30)]], indirect=True)
def test_get_tasks_threeten_task_search_by_most_common_word_and_sort_by_deadline_order_desc(client, create_task):
    excepted_names = [task['name'] for task in create_task]

    words = [word for name in excepted_names for word in name.split()]
    
    word = Counter(words).most_common(1)[0][0]
    excepted_tasks = [task for task in create_task if word in task['name']]
    excepted_tasks.sort(key=lambda t: t['deadline'], reverse=True)
    excepted_names = [task['name'] for task in excepted_tasks]

    r = client.get(f"/api/v1/tasks?search={word}&sort=deadline&order=desc")
    assert r.status_code == 200, r.json()

    present_names = [task['name'] for task in r.json()]

    assert present_names == excepted_names[:10]


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_delete_task_(client, create_task):
    task = create_task[0]
    r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert r.status_code == 204, r.json()

    r = client.delete(f'/api/v1/tasks/{task['id']}')
    assert r.status_code == 404, r.json()


@pytest.mark.parametrize('create_task', [[TASK] * 10], indirect=True)
def test_delete_task_patch_task_as_parent_delete_validate_if_patched_task_has_none_parent(client, create_task):
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
def test_delete_task_patch_task_as_parent_delete_validate_if_patched_tasks_has_none_parent(client, create_task):
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
