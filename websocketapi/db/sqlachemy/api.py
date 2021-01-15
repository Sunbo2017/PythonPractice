# Copyright 2019 Lenovo(Beijing) Technologies Co.,LTD.
# All Rights Reserved.
# Author:
# Date:
# Email:

"""SQLAlchemy storage backend."""

import copy
import threading
from oslo_db import api as oslo_db_api
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import utils as sqlalchemyutils
from oslo_utils import strutils
from oslo_utils import uuidutils
from websocketapi.db.sqlachemy import models
from websocketapi.log import get_logger

LOG = get_logger(__name__)


@enginefacade.transaction_context_provider
class websocketapiDBContext(object):
	pass


CONTEXT = websocketapiDBContext()

main_context_manager = enginefacade.transaction_context()


def get_backend():
	"""The backend is this module itself."""
	return PortalDBApi()


def session_for_read():
	return enginefacade.reader.using(CONTEXT)


def session_for_write():
	return enginefacade.writer.using(CONTEXT)


def get_session(use_slave=False, **kwargs):
	return main_context_manager._factory.get_legacy_facade().get_session(use_slave=use_slave, **kwargs)


def model_query(session, model, *args, **kwargs):
	query = sqlalchemyutils.model_query(
		model, session, args, **kwargs)
	return query


def add_identity_filter(query, value):
	if strutils.is_int_like(value):
		return query.filter_by(id=value)
	elif uuidutils.is_uuid_like(value):
		return query.filter_by(uuid=value)
	else:
		LOG.warning('%s is not id or uuid. ' % value)
		return query


class PortalDBApi(object):
	"""SqlAlchemy connection."""

	def __init__(self):
		pass

	def capturelog_get_by_filters(self, filters, sort_dir='desc', limit=None, marker=None):
		if limit == 0:
			return []
		sort_keys = ['id']
		repository = CaptureLogRepository()
		return repository.paginate_all_by_filters(CONTEXT, limit, sort_keys, marker=marker, sort_dir=sort_dir,
												  **filters)

	def device_get_by_id(self, camera_id):
		repository = DeviceRepository()
		return repository.get_one_by_identity(CONTEXT, camera_id)

	def get_all_devices(self, **filters):
		repository = DeviceRepository()
		return repository.get_all_by_filters(CONTEXT, **filters)

	def get_all_forklifts(self, **filters):
		repository = ForkliftRepository()
		return repository.get_all_by_filters(CONTEXT, **filters)

	def create_alarm(self, value):
		repository = AlarmRepository()
		return repository.create(CONTEXT, value)


class BasicRepository(object):
	def __init__(self, model_class):
		self.model_class = model_class

	@main_context_manager.reader
	def get_one_by_identity(self, context, identity):
		query = model_query(context.session, self.model_class)
		query = add_identity_filter(query, identity)
		return query.one_or_none()

	@main_context_manager.reader
	def get_one_by_filters(self, context, **filters):
		query = model_query(context.session, self.model_class)
		query = query.filter_by(**filters)
		return query.one_or_none()

	@main_context_manager.reader
	def get_all_by_filters(self, context, **filters):
		query = model_query(context.session, self.model_class)
		query = query.filter_by(**filters)
		return query.all()

	@main_context_manager.reader
	def paginate_all_by_filters(self, context, limit, sort_keys, marker=None,
								sort_dir=None, sort_dirs=None, **filters):
		query = model_query(context.session, self.model_class)
		query = query.filter_by(**filters)
		query = sqlalchemyutils.paginate_query(query, self.model_class, limit, sort_keys,
											   marker=marker, sort_dir=sort_dir, sort_dirs=sort_dirs)
		return query.all()

	@main_context_manager.writer
	def update_one_by_identity(self, context, identity, **values):
		query = model_query(context.session, self.model_class)
		query = add_identity_filter(query, identity)
		count = query.with_lockmode('update').update(values)
		return count

	@main_context_manager.writer
	def update_all_by_filters(self, context, filters, **values):
		query = model_query(context.session, self.model_class)
		query = query.filter_by(**filters)
		count = query.with_lockmode('update').update(values)
		return count

	@main_context_manager.writer
	def delete_one_by_identity(self, context, identity):
		query = model_query(context.session, self.model_class)
		query = add_identity_filter(query, identity)
		count = query.with_lockmode('update').delete()
		return count

	@main_context_manager.writer
	def delete_all_by_filters(self, context, **filters):
		query = model_query(context.session, self.model_class)
		query = query.filter_by(**filters)
		count = query.with_lockmode('update').delete()
		return count

	def create(self, context, values):
		model = self.model_class()
		with main_context_manager.writer.using(context) as session:
			model.update(values)
			session.add(model)
		return model


class CaptureLogRepository(BasicRepository):
	def __init__(self):
		super(CaptureLogRepository, self).__init__(models.CaptureLog)


class DeviceRepository(BasicRepository):
	def __init__(self):
		super(DeviceRepository, self).__init__(models.Device)


class ForkliftRepository(BasicRepository):
	def __init__(self):
		super(ForkliftRepository, self).__init__(models.Forklift)


class AlarmRepository(BasicRepository):
	def __init__(self):
		super(AlarmRepository, self).__init__(models.Alarm)
