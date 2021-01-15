from oslo_config import cfg
from oslo_db import api as db_api


_BACKEND_MAPPING = {'sqlalchemy': 'websocketapi.db.sqlachemy.api'}
_IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING, lazy=True)

def get_db_api():
    """Return a DB API instance."""
    return _IMPL
