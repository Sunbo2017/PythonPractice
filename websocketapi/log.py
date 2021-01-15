import logging
from oslo_config import cfg


def prepare_log():
	CONF = cfg.CONF
	_log_file = CONF.log.file
	_log_level_param = CONF.log.level.upper()
	_log_leve_dict = {
		'DEBUG': logging.DEBUG,
		'INFO': logging.INFO,
		'WARNING': logging.WARNING,
		'ERROR': logging.ERROR,
		'CRITICAL': logging.CRITICAL,
		'DEFAULT': logging.WARNING
	}
	_log_level = _log_leve_dict.get(_log_level_param, logging.WARNING)
	_log_format = '%(asctime)s - %(name)s %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
	logging.basicConfig(filename=_log_file, level=_log_level, format=_log_format)
	# print(_log_file,str(_log_level_param),str(_log_level))
	engineio_server_logger = logging.getLogger('engineio.server')

	engineio_server_logger.setLevel(logging.WARNING)


def get_logger(name):
	return logging.getLogger(name)
