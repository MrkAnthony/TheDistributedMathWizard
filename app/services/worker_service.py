import json
from app.services.valkey_client import get_redis_client
from app.services.identity_service import get_container_info
from app.services.adder_service import add_two_items

TASK_QUEUE_KEY = "task_queue"
DLQ_KEY = "dead_letter_queue"
TASK_KEY_PREFIX = "task:"


def run_worker_process():
    # IMPORTANT: create Valkey connection inside the child process
    r = get_redis_client()

    while True:
        # BRPOP returns (queue_name, payload_string)
        queue_name, payload = r.brpop(TASK_QUEUE_KEY, timeout=0)
        task = json.loads(payload)
        task_id = task["id"]
        task_retry = int(r.get(f"task:retry:{task_id}") or 0)

        try:
            # If you later add more ops, switch on task["op"] here.
            result = add_two_items(task["a"], task["b"])

            state = {
                "status": "complete",
                "result": result,
                "handled_by": get_container_info()
            }

            r.delete(f"task:retry:{task_id}")
        except Exception as e:
            # Task failed but still has retries remaining
            if task_retry < 3:
                task_retry += 1
                r.set(f"task:retry:{task_id}", task_retry)
                r.rpush(TASK_QUEUE_KEY, json.dumps(task))
                continue
            else:
                # Task has exhausted all 3 retries send to Dead Letter Queue
                r.rpush(DLQ_KEY, json.dumps(task))
                r.delete(f"task:retry:{task_id}")
                state = {
                    "status": "failed",
                    "result": str(e),
                    "handled_by": get_container_info()
                }
        r.set(f"{TASK_KEY_PREFIX}{task_id}", json.dumps(state))
