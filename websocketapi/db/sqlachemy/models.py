# Copyright 2019 Lenovo(Beijing) Technologies Co.,LTD.
# All Rights Reserved.
# Author:
# Date:
# Email:
import json
from datetime import datetime as cdatetime
from datetime import date, time
import sqlalchemy as sa
from sqlalchemy.ext import declarative
from oslo_db.sqlalchemy import models
from oslo_utils import uuidutils
from oslo_serialization import jsonutils as json
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy import DateTime, Numeric, Date, Time


def table_args():
	return {'mysql_engine': 'Innodb',
			'mysql_charset': "utf8"}


class JsonEncodedType(TypeDecorator):
	"""Abstract base type serialized as json-encoded string in db."""
	type = None
	impl = TEXT

	def process_bind_param(self, value, dialect):
		if value is None:
			# Save default value according to current type to keep the
			# interface the consistent.
			value = self.type()
		elif not isinstance(value, self.type):
			raise TypeError("%s supposes to store %s objects, but %s given"
							% (self.__class__.__name__,
							   self.type.__name__,
							   type(value).__name__))
		serialized_value = json.dump_as_bytes(value)
		return serialized_value

	def process_result_value(self, value, dialect):
		if value is not None:
			value = json.loads(value)
		return value


class JSONEncodedDict(TypeDecorator):
	"""Represents an immutable structure as a json-encoded string."""

	# impl = String
	impl = TEXT

	@staticmethod
	def process_bind_param(value, dialect):
		if value is not None:
			value = json.dumps(value)
		return value

	@staticmethod
	def process_result_value(value, dialect):
		if value is not None:
			value = json.loads(value)
		return value


class JSONEncodedList(JsonEncodedType):
	"""Represents list serialized as json-encoded string in db."""
	type = list


class PortalModelBase(models.ModelBase):
	"""Base class for VideoService Models."""

	__table_args__ = table_args()

	@declarative.declared_attr
	def __tablename__(cls):
		return cls.__name__.lower() + 's'

	def __repr__(self):
		"""sqlalchemy based automatic __repr__ method."""
		items = ['%s=%r' % (col.name, getattr(self, col.name))
				 for col in self.__table__.columns]
		return "<%s.%s[object at %x] {%s}>" % (self.__class__.__module__,
											   self.__class__.__name__,
											   id(self), ', '.join(items))

	def __str__(self):
		return self.__repr__()

	def _gen_tuple(self):
		def convert_datetime(value):
			if value:
				if (isinstance(value, (cdatetime, DateTime))):
					return value.strftime("%Y-%m-%d %H:%M:%S")
				elif (isinstance(value, (date, Date))):
					return value.strftime("%Y-%m-%d")
				elif isinstance(value, (Time, time)):
					return value.strftime("%H:%M:%S")
			else:
				return ""

		for col in self.__table__.columns:
			if isinstance(col.type, (DateTime, Date)):
				value = convert_datetime(getattr(self, col.name))
			elif isinstance(col.type, Numeric):
				value = float(getattr(self, col.name))
			else:
				value = getattr(self, col.name)
			yield (col.name, value)

	def to_dict(self):
		return dict(self._gen_tuple())

	def to_json(self):
		return json.dumps(self.to_dict())


Base = declarative.declarative_base(cls=PortalModelBase)


class CaptureLog(Base):
	"""Represents the logs of smart video capture."""

	__table_args__ = (
		sa.Index('capturelogs_cameraID_idx', 'cameraID'),
		sa.Index('capturelogs_forkID_idx', 'forkID'),
		sa.Index('capturelogs_palletID_idx', 'palletID'),
		sa.Index('capturelogs_taskID_idx', 'taskID'),
		table_args()
	)

	id = sa.Column(sa.Integer, primary_key=True)
	timestamp = sa.Column(sa.DateTime, nullable=False)
	type = sa.Column(sa.Integer, nullable=False)
	cameraID = sa.Column(sa.Integer,
						 sa.ForeignKey('devices.id', ondelete="RESTRICT"),
						 nullable=False)
	forkID = sa.Column(sa.String(36),
					   sa.ForeignKey('forklifts.id', ondelete="RESTRICT"),
					   nullable=True)
	palletID = sa.Column(sa.String(36),
						 sa.ForeignKey('pallets.pallet_number',
									   ondelete="RESTRICT"),
						 nullable=True)
	binID = sa.Column(sa.String(36), nullable=True)
	taskID = sa.Column(sa.String(36),
					   sa.ForeignKey('tasks.id', ondelete="RESTRICT"),
					   nullable=True)
	video_starttime = sa.Column(sa.DateTime, nullable=False)
	video_endtime = sa.Column(sa.DateTime, nullable=False)
	video_filename = sa.Column(sa.String(255), nullable=True)
	status = sa.Column(sa.String(36), nullable=True)


class Task(Base):
	""""""
	id = sa.Column(sa.String(36),
				   primary_key=True,
				   default=uuidutils.generate_uuid)

	status = sa.Column(sa.String(10), nullable=False)
	start_time = sa.Column(sa.DateTime, nullable=False)
	end_time = sa.Column(sa.DateTime, nullable=False)


class Pallet(Base):
	""""""
	pallet_number = sa.Column(sa.String(15), nullable=False, primary_key=True)
	status = sa.Column(sa.String(15), nullable=False)
	asn_file_id = sa.Column(sa.String(36), nullable=False)
	sap_sync_msg_type = sa.Column(sa.String(36), nullable=False)
	sap_sync_msg_text = sa.Column(sa.String(256), nullable=False)
	timestamp = sa.Column(sa.DateTime, nullable=False)


class Forklift(Base):
	""""""
	id = sa.Column(sa.String(36),
				   primary_key=True,
				   default=uuidutils.generate_uuid)
	status = sa.Column(sa.String(10), nullable=False)
	position = sa.Column(sa.String(10), nullable=False)
	timestamp = sa.Column(sa.DateTime, nullable=False)


class Device(Base):
	"""Represents the devices."""

	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String(255), nullable=True)
	type = sa.Column(sa.String(36), nullable=False)
	vendor = sa.Column(sa.String(255), nullable=True)
	ip = sa.Column(sa.String(36), nullable=False, unique=True)
	parent_ip = sa.Column(sa.String(36), nullable=True)
	rtsp_url = sa.Column(sa.String(255), nullable=False)
	position = sa.Column(sa.String(36), nullable=False)
	fork_id = sa.Column(sa.String(36), nullable=True)


class AsnAggregates(Base):
	""""""
	__tablename__ = 'asn_aggregates'
	MATNR = sa.Column(sa.String(18), nullable=False)
	ZPLTID = sa.Column(sa.String(20), nullable=False)
	SNCODE = sa.Column(sa.String(40), nullable=False, primary_key=True)
	MFGDATE = sa.Column(sa.String(10), nullable=True)
	CONTID = sa.Column(sa.String(20), nullable=True)
	ZCOODE = sa.Column(sa.String(2), nullable=True)
	LIFNR = sa.Column(sa.String(10), nullable=True)
	ASN_FILE_ID = sa.Column(sa.String(36), nullable=False)


class ASN_file(Base):
	id = sa.Column(sa.String(36),
				   primary_key=True,
				   default=uuidutils.generate_uuid)
	ASN_FILE_NAME = sa.Column(sa.String(256), nullable=False)
	timestamp = sa.Column(sa.DateTime, nullable=False)


class Mail_ID(Base):
	id = sa.Column(sa.String(100), primary_key=True)
	received_time = sa.Column(sa.DateTime, nullable=False)


class IllegalPallet(Base):
	__tablename__ = "illegal_pallets"

	pallet_id = sa.Column(sa.String(15), nullable=False, primary_key=True)
	status = sa.Column(sa.String(15), nullable=False, default='init')
	fork_id = sa.Column(sa.String(36), nullable=False)
	task_id = sa.Column(sa.String(36))
	origin = sa.Column(sa.String(15))
	sap_sync_msg_type = sa.Column(sa.String(36))
	sap_sync_msg_text = sa.Column(sa.String(256))
	create_time = sa.Column(sa.DateTime)
	update_time = sa.Column(sa.DateTime)


class Job(Base):
	id = sa.Column(sa.String(36),
				   primary_key=True,
				   default=uuidutils.generate_uuid)
	status = sa.Column(sa.String(36), nullable=False)
	task_id = sa.Column(sa.String(36), nullable=False)
	forklift_id = sa.Column(sa.String(36), nullable=False)
	pallet_id = sa.Column(sa.String(15), nullable=True)
	destination = sa.Column(sa.String(36), nullable=True)
	start_time = sa.Column(sa.DateTime, nullable=False)
	end_time = sa.Column(sa.DateTime, nullable=False)


class HistoryRecord(Base):
	id = sa.Column(sa.Integer, primary_key=True)
	name = sa.Column(sa.String(125), nullable=False)
	# default status is unknown
	status = sa.Column(sa.String(15), nullable=False)
	create_at = sa.Column(sa.DateTime)
	update_at = sa.Column(sa.DateTime)
	operation = sa.Column(sa.String(36), nullable=True)


class Dialogs(Base):
	__tablename__ = "dialogs"
	id = sa.Column(sa.Integer, primary_key=True, nullable=True)
	table_name = sa.Column(sa.String(36), nullable=False)
	title = sa.Column(sa.String(125), nullable=True)
	type = sa.Column(sa.String(15), nullable=False)
	column = sa.Column(JSONEncodedList)
	using = sa.Column(sa.Boolean(), nullable=False)
	user = sa.Column(sa.String(15), nullable=False)
	chart = sa.Column(sa.String(15), nullable=False)


class Alarm(Base):
	__tablename__ = "alarms"
	id = sa.Column(sa.Integer, primary_key=True)
	content = sa.Column(sa.String(255), nullable=True)
	timestamp = sa.Column(sa.DateTime, nullable=True)
	type = sa.Column(sa.String(20), nullable=True)

class StorageLane(Base):
	"""ecc available lane"""
	__tablename__ = "storage_lanes"

	id = sa.Column(sa.Integer, primary_key=True)
	lanes = sa.Column(JSONEncodedList)
	lane_number = sa.Column(sa.Integer, nullable=True)
	recommend_lane = sa.Column(sa.String(15))
	update_time = sa.Column(sa.DateTime)


class StatisticAnomaly(Base):
	"""record Abnormal disposition and Abnormal disposition of forklift
	"""
	__tablename__ = "statistic_anomaly"

	id = sa.Column(sa.Integer, primary_key=True)
	fork_id = sa.Column(sa.String(36), nullable=False)
	timestamp = sa.Column(sa.DateTime)
	anormaly = sa.Column(sa.String(125))
	task_id = sa.Column(sa.String(36), nullable=True)

	__mapper_args__ = {
		"order_by":timestamp.desc()
		}

class StatisticIdle(Base):
	"""
	record forklift idle time every day in a weekly
	keep month data
	"""
	__tablename__ = "statistic_idle"

	id = sa.Column(sa.Integer, primary_key=True)
	fork_id = sa.Column(sa.String(36), nullable=False)
	# use day
	unit = sa.Column(sa.Date, nullable=False)
	# use minute
	metric = sa.Column(sa.Integer, nullable=False)


class StatisticPallet(Base):
	"""
	record pallets every hour in day
	"""
	__tablename__ = "statistic_pallet"

	id = sa.Column(sa.Integer, primary_key=True)
	fork_id = sa.Column(sa.String(36), nullable=False)
	# use hour
	unit = sa.Column(sa.Integer, nullable=False)
	date = sa.Column(sa.Date, nullable=False)
	# use pallet number
	metric = sa.Column(sa.Integer, nullable=False)


class StatisticRecognitionRate(Base):

    """record normal task times and abnormal task times
    every day in weekly
    """
    __tablename__ = "statistic_recognition_rate"

    id = sa.Column(sa.Integer, primary_key=True)
    fork_id = sa.Column(sa.String(36), nullable=False)
    # use day
    unit = sa.Column(sa.Date, nullable=False)
    metric = sa.Column(sa.Integer, nullable=False)
    total_times = sa.Column(sa.Integer, nullable=False, default=0)
    abnormal_times = sa.Column(sa.Integer, nullable=False, default=0)


