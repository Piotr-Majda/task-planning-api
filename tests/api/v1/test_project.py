PROJECT = {
        "name": "Project X", 
        'owner_id': 1
}

def test_create_and_get_project(client):
    r = client.post("/api/v1/projects", json=PROJECT)
    assert r.status_code == 200, r.json()
    created_project = r.json()
    assert created_project['name'] == PROJECT['name']
    assert "id" in created_project

    get_r = client.get(f"/api/v1/projects/{created_project['id']}")
    assert get_r.status_code == 200, get_r.json()
    fetched_project = get_r.json()
    assert fetched_project['id'] == created_project['id']
    assert fetched_project['name'] == PROJECT['name']
    assert fetched_project['owner_id'] == PROJECT['owner_id']
