from flask import Flask, render_template, jsonify
from app.controllers.identity_controller import identity_handler
from app.controllers.math_controller import add_handler
from app.services.identity_service import get_container_info
from app.services.exceptions import MathWizardError

app = Flask(__name__)

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


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/whoami')
def awareness():
    return identity_handler()

# Route delegates to the controller
@app.route('/add')
def add():
    return add_handler()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
