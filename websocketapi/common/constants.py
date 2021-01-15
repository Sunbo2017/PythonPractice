# camera status
OFF = 'off'
ON = 'on'

# forklift position info

STAGE = 'stage'
GATE = 'gate'
SHELVES = 'shelves'

PUTAWAY = 'putaway'
STORAGE = 'storage'

# state_map_position
STATE_MAP_POSITION = {
	'WISForkUnregister': 'back',
	'WISForkStorage': 'shelves',
	'WISForkPutAway': 'gate',
	'WISForkregister': 'stage'
}

STATE_MAP_STATUS = {
	'WISForkUnregister': 'unregister',
	'WISForkStorage': 'storage',
	'WISForkPutAway': 'putaway',
	'WISForkregister': 'register',
	'UnRegister': 'unregister',
	'Unregister': 'unregister',
	'Storage': 'storage',
	'Putaway': 'putaway',
	'Register': 'register'
}

#  Topics for devicemapping
DEVICEMAPPING_CAMERA = 'devicemapping/notify/camera/#'
DEVICEMAPPING_FORKLIFT = 'devicemapping/notify/forklift/#'
DEVICEMAPPING_DEFAULT_TOPIC = "devicemapping/notify/#"

#  Topics for alarm
WHITSETT_ALARM_DEFAULT_TOPIC = "whitsett/infomation/#"
WHITSETT_ALARM_TOPIC = "whitsett/infomation/alarm"


# Mqtt server
MQTT_HOST = "mosquitto"
MQTT_PORT = 1883

DEFAULT_QOS_PRIORITY = 2
