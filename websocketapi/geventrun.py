from websocketapi.server import portal_app
from websocketapi.server import socketio
from oslo_config import cfg
from websocketapi.log import get_logger

from multiprocessing import Process
import gunicorn.app.base
from gunicorn.config import Config

CONF = cfg.CONF
LOG = get_logger(__name__)


class WebsocketApp(gunicorn.app.base.Application):
	def __init__(self, app, options=None):
		self.options = options or {}
		self.application = app
		super(WebsocketApp, self).__init__()

	def load_config(self):
		# init configuration
		self.cfg = Config(self.usage, prog=self.prog)

		config = dict(
			[(key, value) for key, value in self.options.items()
			 if key in self.cfg.settings and value is not None]
		)

		for key, value in config.items():
			self.cfg.set(key.lower(), value)

	def load(self):
		return self.application


def main():
	MQTTManager()
	bind_ip_port = '{}:{}'.format(CONF.api.host_ip, CONF.api.port)
	options = {
		'bind': bind_ip_port,
		'workers': CONF.api.works,
		'timeout': 20,
		'preload_app': True,
		'loglevel': 'debug',
		'worker_class': 'gunicorn.workers.ggevent.GeventWorker',
		'errorlog': '/var/log/gunicorn/error.log',
		'accesslog': '/var/log/gunicorn/access.log'
	}
	WebsocketApp(portal_app, options).run()


if __name__ == '__main__':
	main()
