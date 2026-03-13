

def test_create_and_get_task(client):
    r = client.post("/api/v1/tasks", json={"name": "Test Task"})
    assert r.status_code == 200
    created_task = r.json()
    assert created_task['name'] == 'Test Task'
    assert "id" in created_task

    get_r = client.get(f"/api/v1/tasks/{created_task['id']}")
    assert get_r.status_code == 200
    fetched_task = get_r.json()
    assert fetched_task['id'] == created_task['id']
    assert fetched_task['name'] == "Test Task"
