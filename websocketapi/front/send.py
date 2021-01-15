import datetime
import time

from flask import jsonify
from flask import Blueprint

from oslo_config import cfg
from websocketapi.db.api import get_db_api
from websocketapi.common import constants as conts
from websocketapi.log import get_logger

CONF = cfg.CONF

db_api = get_db_api()
LOG = get_logger(__name__)


def str_to_utc_datetime(str_time):
	if '.' in str_time:
		return datetime.datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S.%f') if str_time else datetime.datetime.utcnow()
	else:
		return datetime.datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S') if str_time else datetime.datetime.utcnow()


def send_alarm_info(message, socketio):
	LOG.info('emit alarm: %s', message)
	try:
		utc_timestap_str = message.get('timestamp')
		utc_date_time = str_to_utc_datetime(utc_timestap_str)
		us_time = (utc_date_time + datetime.timedelta(hours=-5)).strftime('%Y-%m-%d %H:%M:%S')
		message['timestamp'] = us_time
		socketio.emit('alarm info', message)
	except Exception as e:
		LOG.error('push message failed %s', e.message)

	try:
		utc_timestap_str = message.get('timestamp')
		utc_date_time = str_to_utc_datetime(utc_timestap_str)
		value = {'content': message['info'], 'type': message['type'],
				 'timestamp': utc_date_time}
		db_api.create_alarm(value)
	except Exception as e:
		LOG.error('create alarm to db invalid %s', e.message)


def update_camera_status(message, socketio, alarm=False):
	camera_dict = {
		"id": None,
		"name": None,
		"ip": None,
		"state": None,
		"type": None,
		"position": None,
		"forkliftId": None
	}
	try:
		camera_id = message['id']
		camera = db_api.device_get_by_id(camera_id)
		if camera:
			camera_dict["id"] = camera.id
			camera_dict["name"] = camera.name
			camera_dict["ip"] = camera.ip
			camera_dict["type"] = "dynamic" if camera.type == 'd_camera' else 'static'
			camera_dict["position"] = camera.position
			camera_dict["forkliftId"] = camera.fork_id
			camera_dict["state"] = message['state']['reported']['status']
		else:
			return
	except Exception as e:
		LOG.error('update message %s invalid %s', str(message), e.message)
		return
	LOG.info('emit camera_dict: %s' % str(camera_dict))
	socketio.emit('update camera', camera_dict, broadcast=True)
	if alarm:

		# time_strf = utc_date_time.strftime("%Y-%m-%d %H:%M:%S")
		# socketio.emit('alarm info', {'info': alarm_message, 'type': 'Camera', 'timestamp': time_strf})
		try:
			alarm_message = 'Camera name:{name} ip:{ip} ' \
							'type:{type} position:{position} forkliftId:{forkliftId} state is {state}'.format(
				**camera_dict)
			# LOG.info('emit alarm: %s', alarm_message)
			timestamp = message.get('timestamp', time.time())
			utc_date_time = datetime.datetime.utcfromtimestamp(timestamp)
			us_time = (utc_date_time + datetime.timedelta(hours=-5)).strftime('%Y-%m-%d %H:%M:%S')
			value = {'content': alarm_message, 'type': 'Camera', 'timestamp': utc_date_time}
			socketio.emit('alarm info', {'info': alarm_message, 'type': 'Camera', 'timestamp': us_time})
			db_api.create_alarm(value)
		except Exception as e:
			LOG.error('create alarm to db invalid %s', e.message)


def update_forklift_status(message, socketio):
	LOG.info('update_forklift_status: %s' % str(message))
	forklift_dict = {
		"forkliftId": None,
		"name": None,
		'status': None,
		"pallets": [],
		"laneId": None,
	}

	try:
		if 'id' in message:
			forklift_dict["forkliftId"] = message['id']
		elif message['state']['desired'] and message['state']['desired']['MsgBody']:
			forklift_dict["forkliftId"] = message['state']['desired']['MsgBody']['ForkID']
		else:
			forklift_dict["forkliftId"] = message['state']['reported']['MsgBody']['ForkID']
		forklift_dict["name"] = 'forklift_%s' % str(forklift_dict.get("forkliftId"))
		status = conts.STATE_MAP_STATUS.get(message['state']['reported']['MsgType'])
		forklift_dict["status"] = status
		if status == conts.PUTAWAY:
			forklift_dict["pallets"] = \
				message['state']['reported']['MsgBody']['PalletIDs'] if message['state']['reported']['MsgBody'].get(
					'PalletIDs') else []
			forklift_dict["laneId"] = \
				message['state']['reported']['MsgBody']['LaneID'] if message['state']['reported']['MsgBody'].get(
					'LaneID') else None
		elif status == conts.STORAGE:
			forklift_dict["pallets"] = [item['pallet_id'] for item in
										message['state']['reported']['MsgBody']['PalletIDs']]
			forklift_dict['laneId'] = \
				message['state']['reported']['MsgBody'].get('ChechedLaneID')
	except Exception as e:
		LOG.error('update message %s invalid %s', str(message), e.message)
		return
	if forklift_dict.get('forkliftId'):
		LOG.info('emit forklift_dict %s' % str(forklift_dict))
		socketio.emit('update forklift', forklift_dict, broadcast=True)
