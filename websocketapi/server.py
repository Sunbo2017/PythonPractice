import json
import logging
import sys
from multiprocessing import Process
import eventlet

eventlet.monkey_patch()
from flask import Flask
from flask_socketio import SocketIO, emit
from oslo_config import cfg
from config import parse_args
from log import prepare_log, get_logger
from front import cameras
from mqtt_message import MsgHandler, MQTTManager


def prepare_server():
	parse_args(sys.argv)
	prepare_log()


prepare_server()

CONF = cfg.CONF

LOG = get_logger(__name__)


portal_app = Flask(__name__)
portal_app.register_blueprint(cameras.camera)

# socketio = SocketIO(portal_app,cors_allowed_origins='*',message_queue='redis://:whitsett@10.121.11.166:6379')

socketio = SocketIO(portal_app, cors_allowed_origins='*')

@socketio.on('my event')
def dest_message(message):
	emit('my response', {'data': message['data']})





def main():
	MQTTManager(socketio)
	socketio.run(portal_app, host=CONF.api.host_ip, port=CONF.api.port)


if __name__ == '__main__':
	main()
