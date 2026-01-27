from app.services.task_service import start_task, get_task_status
from app.services.identity_service import get_container_info
from flask import jsonify, request


def create_task_handler():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    operation = request.args.get('operation', type=str)

    task_id = start_task(a, b, operation)

    return jsonify({
        "task_id": task_id,
        "handled_by": get_container_info()
    }), 202


def check_status_handler(task_id):
    task_data = get_task_status(task_id)
    status = task_data["status"]

    response = {
        "status": status,
        "checked_by": task_data.get("checked_by", get_container_info())
    }

    if status == "complete":
        response["result"] = task_data["result"]
        response["handled_by"] = task_data.get("handled_by", "Unknown")
    elif status == "failed":
        response["error"] = task_data["result"]
        response["handled_by"] = task_data.get("handled_by", "Unknown")

    return jsonify(response), 200
