import json
from app.services.valkey_client import get_redis_client
from app.services.identity_service import get_container_info
from app.services.adder_service import add_two_items

TASK_QUEUE_KEY = "task_queue"
TASK_KEY_PREFIX = "task:"


def run_worker_process():
    # IMPORTANT: create Valkey connection inside the child process
    r = get_redis_client()

    while True:
        # BRPOP returns (queue_name, payload_string)
        queue_name, payload = r.brpop(TASK_QUEUE_KEY, timeout=0)
        task = json.loads(payload)

        task_id = task["id"]

        try:
            # If you later add more ops, switch on task["op"] here.
            result = add_two_items(task["a"], task["b"])
            status = "complete"
            error = None
        except Exception as e:
            result = None
            status = "failed"
            error = str(e)

        state = {
            "status": status,
            "result": result if status == "complete" else error,
            "handled_by": get_container_info()
        }

        r.set(f"{TASK_KEY_PREFIX}{task_id}", json.dumps(state))
