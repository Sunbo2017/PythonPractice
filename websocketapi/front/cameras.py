from flask import jsonify
from flask import Blueprint


from oslo_config import cfg

from websocketapi.log import get_logger

CONF = cfg.CONF

camera = Blueprint('camera',__name__)

LOG = get_logger(__name__)


@camera.route('/',methods=['GET'])
def index():
    return 'index'
