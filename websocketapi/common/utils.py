import time
import warnings

import requests
import simplejson
from websocketapi.log import get_logger
from oslo_config import cfg

CONF = cfg.CONF
LOG = get_logger(__name__)

class DeviceAPIClient(object):
	def __init__(self):
		super(DeviceAPIClient, self).__init__()

	def _base_url(self):
		return "http://{ip}:{port}/{version}".format(
			ip=CONF.device_mapping.server_name,
			port=CONF.device_mapping.port,
			version=CONF.device_mapping.version)

	def request(self, method, path='/', timeout_dict=None, **kwargs):
		if timeout_dict is None:
			timeout_dict = {}
		_url = self._base_url() + path
		LOG.debug("request url %s", _url)
		try:
			r = requests.request(method, url=_url,**kwargs)
		except Exception as e:
			LOG.error('connect to Device api faild %s',e.message)
			raise
		return r.json()


	def get_forklifts(self):
		r = self.request('get',path='/forklifts')
		return r

	def get_cameras(self):
		r = self.request('get',path='/cameras')
		return r


if __name__ == '__main__':
	api_clinet = DeviceAPIClient()
	print api_clinet.get_cameras()