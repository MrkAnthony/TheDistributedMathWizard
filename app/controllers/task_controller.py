from app.services.task_service import start_task, get_task_status
from flask import jsonify, request


def create_task_handler():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)
    operation = request.args.get('operation', type=str)

    task_id = start_task(a, b, operation)

    return jsonify({"task_id": task_id}), 202


def check_status_handler(task_id):
    task_status = get_task_status(task_id)

    if task_status["status"] == "complete":
        return jsonify({"status": "complete", "result": task_status["result"]}), 200
    elif task_status["status"] == "failed":
        return jsonify({"status": "failed", "error": task_status["result"]}), 200
    else:
        return jsonify({"status": "pending"}), 200
