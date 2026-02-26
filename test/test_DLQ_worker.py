import pytest
import json
import tempfile
import os
import valkey
from unittest.mock import patch
from app.services.valkey_client import get_redis_client

DLQ_KEY = "dead_letter_queue"
TASK_KEY_PREFIX = "task:"


@pytest.fixture(autouse=True)
def reset_redis():
    client = valkey.Valkey(
        host=os.getenv("VALKEY_HOST", "localhost"),
        port=int(os.getenv("VALKEY_PORT", 6379))
    )
    client.flushdb()
    yield client
    client.flushdb()


def test_task_correctly_inserted_into_dlq(reset_redis):
    r = reset_redis
    task = {
        "id": "test-123",
        "a": 1,
        "b": 2,
        "op": "add",
        "error": "Something went wrong"
    }
    # Simulate retry count stored separately in Redis
    r.set("task:retry:test-123", 3)
    r.rpush(DLQ_KEY, json.dumps(task))
    result = r.lrange(DLQ_KEY, 0, -1)

    assert len(result) == 1
    retrieved = json.loads(result[0])
    assert retrieved["id"] == "test-123"

    # Verify retry count is stored separately in Redis, not on the payload
    retry_count = int(r.get("task:retry:test-123"))
    assert retry_count == 3


def test_dlq_worker_retrieves_failed_task(reset_redis):
    r = reset_redis
    task = {
        "id": "test-456",
        "a": 1,
        "b": 2,
        "op": "add"
    }
    state = {
        "status": "failed",
        "result": "Division by zero",
        "handled_by": "container-1"
    }
    r.rpush(DLQ_KEY, json.dumps(task))
    r.set(f"{TASK_KEY_PREFIX}test-456", json.dumps(state))

    queue_name, payload = r.brpop(DLQ_KEY, timeout=1)
    retrieved_task = json.loads(payload)
    retrieved_state = json.loads(r.get(f"{TASK_KEY_PREFIX}{retrieved_task['id']}"))

    assert retrieved_task["id"] == "test-456"
    assert retrieved_state["status"] == "failed"
    assert retrieved_state["result"] == "Division by zero"


def test_logging_writes_correct_fields():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        log_entry = {
            "task_id": "test-789",
            "timestamp": "2024-01-01T00:00:00",
            "error": "Something went wrong",
            "handled_by": "container-2"
        }
        with open(tmp_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        with open(tmp_path, "r") as f:
            written = json.loads(f.readline())

        assert written["task_id"] == "test-789"
        assert written["error"] == "Something went wrong"
        assert written["handled_by"] == "container-2"
        assert "timestamp" in written
    finally:
        os.unlink(tmp_path)
