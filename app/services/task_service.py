import uuid
import json
from app.services.adder_service import add_two_items
from app.services.exceptions import MathWizardError
from app.services.identity_service import get_container_info
from app.services.valkey_client import get_redis_client

SERVICE_MAP = {
    "add": add_two_items
}

TASK_QUEUE_KEY = "task_queue"
TASK_KEY_PREFIX = "task:"


def start_task(a, b, operation):
    if operation not in SERVICE_MAP:
        raise MathWizardError(f"Unknown operation: {operation}", 400)

    if a is None or b is None:
        raise MathWizardError("Missing query params: a and b are required", 400)

    task_id = str(uuid.uuid4())
    r = get_redis_client()

    # 1) write initial state
    initial_state = {
        "status": "pending",
        "result": None,
        "handled_by": None,
        "checked_by": get_container_info()
    }
    r.set(f"{TASK_KEY_PREFIX}{task_id}", json.dumps(initial_state))

    # 2) enqueue job
    payload = {
        "id": task_id,
        "a": a,
        "b": b,
        "op": operation
    }
    r.lpush(TASK_QUEUE_KEY, json.dumps(payload))

    return task_id


def get_task_status(task_id):
    r = get_redis_client()
    raw = r.get(f"{TASK_KEY_PREFIX}{task_id}")

    if raw is None:
        raise MathWizardError(f"No Task_ID to check status {task_id}", 404)

    data = json.loads(raw)

    # Update checked_by each time status is requested (proves load balancing)
    data["checked_by"] = get_container_info()
    r.set(f"{TASK_KEY_PREFIX}{task_id}", json.dumps(data))

    return data
