import os, time
import json
import paho.mqtt.client as paho
from websocketapi.common import constants
from websocketapi.front.send import update_camera_status, update_forklift_status, send_alarm_info
from websocketapi.log import get_logger

LOG = get_logger(__name__)


class MsgHandler(object):

	def __init__(self):
		self.forklifts_version_info = {'type': 'forklift',}
		self.cameras_version_info = {'type': 'camera'}

	def on_connect(self, client, userdata, flags, rc):
		LOG.info('Mosquitto connected...')
		try:
			client.subscribe([(constants.DEVICEMAPPING_DEFAULT_TOPIC,constants.DEFAULT_QOS_PRIORITY),
							(constants.WHITSETT_ALARM_TOPIC,constants.DEFAULT_QOS_PRIORITY)
							 ])

		except Exception as e:
			LOG.error("Subscribe to %s:%s failed, cause: %s",
					  constants.MQTT_HOST, constants.MQTT_PORT, e)

	def on_disconnect(self, client, userdata, rc):
		if rc != 0:
			LOG.warn('Mosquitto unexpected disconnection...')
		else:
			LOG.warn('Mosquitto disconnection...')

	def persistent_cameras_msg(self, client, userdata, message):
		msg = 'Get MQTT message, topic: %s and payload: %s' % (
			message.topic, message.payload)
		LOG.info(msg)
		payload = json.loads(message.payload)
		return payload

	def persistent_forklift_msg(self, client, userdata, message):
		msg = 'Get MQTT message, topic: %s and payload: %s' % (
			message.topic, message.payload)
		LOG.info(msg)
		payload = json.loads(message.payload)
		return payload

	def persistent_alarm_msg(self, client, userdata, message):
		pass

	def receive_msg(self):



		mqttc = paho.Client(client_id='websocketapi', clean_session=False)

		mqttc.message_callback_add(constants.DEVICEMAPPING_CAMERA,
								   self.persistent_cameras_msg)
		mqttc.message_callback_add(constants.DEVICEMAPPING_FORKLIFT,
								   self.persistent_forklift_msg)
		# alarm
		mqttc.message_callback_add(constants.WHITSETT_ALARM_TOPIC,
								   self.persistent_alarm_msg)

		mqttc.on_connect = self.on_connect
		mqttc.on_socket_close = self.on_disconnect

		try:
			mqttc.connect(constants.MQTT_HOST, constants.MQTT_PORT)
			mqttc.subscribe([(constants.DEVICEMAPPING_DEFAULT_TOPIC,constants.DEFAULT_QOS_PRIORITY),
							(constants.WHITSETT_ALARM_TOPIC,constants.DEFAULT_QOS_PRIORITY)
							 ])

		except Exception as e:
			LOG.error("Connection to %s:%s failed, cause: %s",
					  constants.MQTT_HOST, constants.MQTT_PORT, e)
			exit(-1)

		mqttc.loop_start()  # Non-blocking
	# mqttc.loop_forever()

	# while not mqtt_connected:
	# 	time.sleep(1)


class MQTTManager(MsgHandler):

	def __init__(self, socketio):
		self.socketio = socketio
		super(MQTTManager, self).__init__()

		self.init()

	def persistent_alarm_msg(self, client, userdata, message):

		try:
			msg = 'Get MQTT message, topic: %s and payload: %s' % (
				message.topic, message.payload)
			LOG.info(msg)
			payload = json.loads(message.payload)
		except Exception as e:
			LOG.error('Get MQTT message invalid %s', e.message)
			return
		send_alarm_info(payload, self.socketio )



	def persistent_cameras_msg(self, client, userdata, message):
		try:
			msg = 'Get MQTT message, topic: %s and payload: %s' % (
				message.topic, message.payload)
			LOG.info(msg)
			payload = json.loads(message.payload)
		except Exception as e:
			LOG.error('Get MQTT message invalid %s', e.message)
			return
		if self.check_version(payload,self.cameras_version_info):
			alarm = self.check_camera_abnormal(payload,self.cameras_version_info)
			update_camera_status(payload, self.socketio, alarm=alarm)

	def persistent_forklift_msg(self, client, userdata, message):
		try:
			msg = 'Get MQTT message, topic: %s and payload: %s' % (
				message.topic, message.payload)
			LOG.info(msg)
			payload = json.loads(message.payload)
		except Exception as e:
			LOG.error('Get MQTT message invalid %s', e.message)
			return
		if self.check_version(payload, self.forklifts_version_info):
			update_forklift_status(payload, self.socketio)

	def init(self):
		# p1 = Process(target=self.receive_msg)
		# p1.daemon = True
		# p1.start()
		self.receive_msg()
		LOG.info("Monitor mqtt service started ...")

	def check_version(self, payload, version_dict):
		'''
		Check that the received message version number is up to date, based on the first received version number
		:param payload:
		:param version_dict:
		:return:
		'''
		try:
			id = payload.get('id')
			version = int(payload.get('version'))
			if id in version_dict:
				if version > version_dict[id].get('version',0):
					version_dict[id]['version'] = version
					return True
				else:
					LOG.info( 'This message has been pushed type: %s id: %s version:%s' % (
					version_dict.get('type', ''), id, version))
					return False
			else:
				version_dict[id] = {'version':int(version)}
				return True
		except Exception as e:
			LOG.error(' error %s', e.message)
			return False

	def check_camera_abnormal(slef,payload,version_dict):
		'''
		Judge camera error warning information
		:param payload: Listen for camera MQTTX messages
		:param version_dict:
		:return:
		'''
		try:
			id = payload.get('id')
			camera_status = payload['state']['reported']['status']
			if 'status' in version_dict[id]:
				last_camera_status = version_dict[id]['status']
				version_dict[id]['status'] = camera_status
				if camera_status.lower() == constants.OFF and camera_status.lower() != last_camera_status.lower():
					return True
				else:return False
			else:
				version_dict[id]['status'] = camera_status
				if camera_status.lower() == constants.OFF:
					return True
				else:return False

		except Exception as e:
			LOG.error(' error %s', e.message)
			return False

