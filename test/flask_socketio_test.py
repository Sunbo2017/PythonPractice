from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app,  cors_allowed_origins='*')


@socketio.on('my event')
def test_message(message):
    print(message)
    emit('my response', {'data': 'test flask socketio...'})


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)


@socketio.on('connect')
def test_connect():
    print('connect successful')
    emit('test connect', {'data': 'connect successful...'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=9090)
