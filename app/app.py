from flask import Flask, render_template, jsonify
import multiprocessing
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.controllers.identity_controller import identity_handler
from app.controllers.math_controller import add_handler
from app.controllers.task_controller import create_task_handler, check_status_handler
from app.services.identity_service import get_container_info
from app.services.exceptions import MathWizardError
from app.controllers.valkey_controller import valkey_test_handler
from app.services.worker_service import run_worker_process

app = Flask(__name__)
# Uses the same Valkey Instance but they will coexist
storage_uri = f"redis://{os.getenv('VALKEY_HOST', 'localhost')}:{os.getenv('VALKEY_PORT', '6379')}"
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri=storage_uri
)

_worker = None  # module-level so we don’t spawn multiple


def maybe_start_worker():
    """
    Start exactly one worker process per container.
    Avoids double-start when Flask's debug reloader is enabled.
    """
    global _worker

    # If the Werkzeug reloader is on, Flask starts twice:
    # - parent process: WERKZEUG_RUN_MAIN is not "true"
    # - child process:  WERKZEUG_RUN_MAIN == "true"
    # We only want to start the worker in the reloader child.
    if os.getenv("FLASK_DEBUG") == "1" and os.getenv("WERKZEUG_RUN_MAIN") != "true":
        return

    if _worker is None or not _worker.is_alive():
        _worker = multiprocessing.Process(target=run_worker_process, daemon=True)
        _worker.start()


@app.errorhandler(MathWizardError)
def handle_mathwizard_error(err: MathWizardError):
    return jsonify({
        "error": err.message,
        "handled_by": get_container_info()
    }), err.status_code


@app.errorhandler(404)
def handle_not_found(err):
    return jsonify({
        "error": "Route not found",
        "handled_by": get_container_info()
    }), 404


@app.errorhandler(Exception)
def handle_unexpected_error(err):
    return jsonify({
        "error": "Internal server error",
        "handled_by": get_container_info()
    }), 500


@app.errorhandler(429)
def handle_too_many_request(e):
    return "", 429

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/whoami')
def awareness():
    return identity_handler()


@app.route('/add')
def add():
    return add_handler()


@app.route('/tasks/<task_id>/status', methods=['GET'])
def check_status(task_id):
    return check_status_handler(task_id)


@app.route('/task', methods=['POST'])
@limiter.limit("100 per minute")
def create_task():
    return create_task_handler()


@app.route('/valkey_test')
def valkey_test():
    return valkey_test_handler()


# Start the worker once per container (works with `flask run` too)
maybe_start_worker()

if __name__ == "__main__":
    # If you run `python app/app.py`, Flask will start here
    app.run(host="0.0.0.0", port=5000)
