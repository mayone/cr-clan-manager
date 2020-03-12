# -*- coding: utf-8 -*-

import time
from datetime import datetime, timezone, timedelta


# ISO 8601 compact format
iso8061comp_fmt = "%Y%m%dT%H%M%S.%fZ"

def get_now():
	now = datetime.now()
	return now

def get_utcnow():
	now = datetime.now(timezone.utc)
	return now

def get_utcnow_str(fmt=iso8061comp_fmt):
	now_str = datetime.now(timezone.utc).strftime(fmt)
	return now_str

def dt_to_str(dt, fmt=iso8061comp_fmt):
	dt_str = dt.strftime(fmt)
	return dt_str

def datetime_from_str(iso8061comp_str):
	dt = datetime.strptime(iso8061comp_str, iso8061comp_fmt).replace(tzinfo=timezone.utc)
	return dt

def utc_to_local(dt):
	epoch = time.mktime(dt.timetuple())
	offset = datetime.fromtimestamp(epoch) - datetime.utcfromtimestamp(epoch)
	return dt.replace(tzinfo=None) + offset

def utc_shift_tz(dt, hours=8):
	dt = dt.astimezone(timezone(offset = timedelta(hours = hours))).replace(tzinfo=None)
	return dt

def get_date_str(dt):
	return dt.strftime("%Y%m%d")

def get_rounded_str(tdelta):
	if tdelta > timedelta(weeks=1):
		rounded_str = "{0} 週".format(tdelta.days // 7)
	elif tdelta > timedelta(days=1):
		rounded_str = "{0} 天".format(tdelta.days)
	elif tdelta > timedelta(hours=1):
		rounded_str = "{0} 時".format(tdelta.seconds // 3600)
	elif tdelta > timedelta(minutes=1):
		rounded_str = "{0} 分".format(tdelta.seconds // 60)
	else:
		rounded_str = "{0} 秒".format(tdelta.seconds)

	return rounded_str
