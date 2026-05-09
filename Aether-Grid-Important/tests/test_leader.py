import pytest
from fastapi.testclient import TestClient
from aethergrid.leader import app
from aethergrid.models import Task, TaskCompletion

client = TestClient(app)

def test_leader_health():
    """Verify the status endpoint is functional."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "queue_size" in data
    assert "uptime" in data

def test_task_lifecycle():
    """Test enqueuing and polling a task."""
    task_id = "test-task-123"
    task_data = {"id": task_id, "data": "payload-content"}
    
    # Create task
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201
    assert response.json()["task_id"] == task_id
    
    # Poll task
    response = client.get("/tasks/poll")
    assert response.status_code == 200
    assert response.json()["id"] == task_id
    
    # Poll again (should be empty)
    response = client.get("/tasks/poll")
    assert response.status_code == 404

def test_task_completion():
    """Test submitting a task completion."""
    completion_data = {
        "id": "test-task-123",
        "data": "payload-content",
        "result": "processed-result",
        "processed_by": "test-worker"
    }
    response = client.post("/tasks/complete", json=completion_data)
    assert response.status_code == 200
    assert response.json()["status"] == "buffered"
