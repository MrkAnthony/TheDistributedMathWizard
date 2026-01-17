from flask import Flask
from app.controllers.identity_controller import identity_handler
from app.controllers.math_controller import add_handler

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/whoami')
def awareness():
    return identity_handler()

# Route delegates to the controller
@app.route('/add')
def add():
    return add_handler()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
