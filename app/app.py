from flask import Flask
from self_awareness import get_container_info

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/whoami')
def awareness():
    return get_container_info()


if __name__ == '__main__':
    app.run()
