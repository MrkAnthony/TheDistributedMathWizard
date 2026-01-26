import uuid
import threading
from app.services.adder_service import add_two_items
from app.services.exceptions import MathWizardError
from app.services.identity_service import get_container_info  # <--- Make sure this is imported

SERVICE_MAP = {
    "add": add_two_items
}

task_store = {}

def run_task_in_background(task_id, operation, a, b) -> None:
    result = None
    worker_identity = "Unknown"

    try:
        worker_identity = get_container_info() 
        service_function = SERVICE_MAP.get(operation)
        result = service_function(a, b)
        status = "complete"
    except Exception as e:
        status = 'failed'
        result = str(e)
        worker_identity = get_container_info() # Capture ID even on error

    if task_id in task_store:
        task_store[task_id]["status"] = status
        task_store[task_id]["result"] = result
        task_store[task_id]["handled_by"] = worker_identity


def start_task(a, b, operation):
    if operation not in SERVICE_MAP:
        raise MathWizardError(f"Unknown operation: {operation}", 400)

    task_id = str(uuid.uuid4())

    task_store[task_id] = {
        "status": "pending",
        "result": None,
        "handled_by": None 
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