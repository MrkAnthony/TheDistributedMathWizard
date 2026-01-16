from flask import Flask, request
import socket

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return '''
    <h2>Math Wizard</h2>
    <p>Use the add endpoint like this:</p>
    <p><code>/add?a=&lt;number&gt;&amp;b=&lt;number&gt;</code></p>
    <p>Example:</p>
    <p><code>/add?a=10&amp;b=5</code></p>
    <p>You can change <b>a</b> and <b>b</b> in the URL to test other values.</p>
    '''


@app.route('/add')
def add():
    a = request.args.get('a', type=float)
    b = request.args.get('b', type=float)

    if a is None or b is None:
        return '''
        <h2>Missing parameters</h2>
        <p>Use: <code>/add?a=&lt;number&gt;&amp;b=&lt;number&gt;</code></p>
        <p>Example:</p>
        <p><code>/add?a=10&amp;b=5</code></p>
        <p>You can edit the <b>a</b> and <b>b</b> values directly in the URL.</p>
        ''', 400

    result = a + b
    hostname = socket.gethostname()

    return f'Sum: {result} | Server: {hostname}'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
