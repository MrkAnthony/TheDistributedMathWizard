from flask import Flask, request, jsonify
from app.self_awareness import get_container_info
from app.adder_identity import add_with_identity

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/whoami')
def awareness():
    return jsonify(get_container_info())

@app.route('/add')
def add():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)

    if a is None or b is None:
        return {"error": "missing parameters"}, 400

    return jsonify(add_with_identity(a, b))
