import uuid
from app.services.adder_service import add_two_items
from app.services.exceptions import MathWizardError
import threading

# If we decide to add more services they would go here
SERVICE_MAP = {
    "add": add_two_items
}

task_store = {}


def run_task_in_background(task_id, operation, a, b) -> None:
    result = None
    try:
        service_function = SERVICE_MAP.get(operation)
        result = service_function(a, b)
        status = "complete"
    except Exception as e:
        status = 'failed'
        result = str(e)

    task_store[task_id]["status"] = status
    task_store[task_id]["result"] = result


def start_task(a, b, operation):
    # Validate that the requested math operation exists in our service registry
    if operation not in SERVICE_MAP:
        raise MathWizardError(f"Unknown operation: {operation}", 400)

    task_id = str(uuid.uuid4())

    task_store[task_id] = {
        "status": "pending",
        "result": None
    }

    background_thread = threading.Thread(
        target=run_task_in_background,
        args=(task_id, operation, a, b)
    )

    background_thread.start()

    return task_id


def get_task_status(task_id):
    if task_id not in task_store:
        raise MathWizardError(f"No Task_ID to check status {task_id}", 404)
    return task_store[task_id]
