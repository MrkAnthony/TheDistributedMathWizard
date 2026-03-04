import json
import datetime
from app.services.valkey_client import get_redis_client
from app.services.identity_service import get_container_info

r = get_redis_client()
DLQ_KEY = "dead_letter_queue"
TASK_KEY_PREFIX = "task:"


def logging_task_failure() -> None:
    while True:
        queue_name, payload = r.brpop(DLQ_KEY, timeout=0)
        task = json.loads(payload)
        task_id = task["id"]

        raw_state = r.set(f"{TASK_KEY_PREFIX}{task_id}")
        state = json.load(raw_state)

        log_entry = {
            "task_id": task_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "error": state["result"],
            "handled_by": state["handled_by"]
        }

        with open("/app/logs/dlq_log.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    logging_task_failure()
