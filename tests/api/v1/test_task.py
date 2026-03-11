from fastapi.testclient import TestClient

from app.api.v1.tasks import get_task_service
from app.main import app
from app.services.task_service import TaskService
from tests.test_db import TestingSessionLocal


client = TestClient(app)

def override_get_task_service():
    session = TestingSessionLocal()
    yield TaskService(session=session)

app.dependency_overrides[get_task_service] = override_get_task_service

def test_create_and_get_task():
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
