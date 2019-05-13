# -*- coding: utf-8 -*-

#############
# Singleton #
#############
class Singleton(type):
	""" A metaclass that creates a Singleton base class when called. """
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class cls_testing(metaclass=Singleton):
	def __init__(self):
		self.__test_str = "Singleton test FAILED!!!"
	def set_str(self, str):
		self.__test_str = str
	def get_str(self):
		return self.__test_str

def singleton_test():
	a = cls_testing()
	b = cls_testing()
	a.set_str("Singleton test SUCCESS!!!")
	result = b.get_str()
	print(result)

#############
# Alignment #
#############

from sys import platform as _platform
import unicodedata
#import re


def is_wide(ch):
	"""Check is the character wide or not.

	Parameters
	----------
	ch : character
	    The character to be checked.
	"""
	res = unicodedata.east_asian_width(ch)
	if res == 'A':
		# Ambiguous
		if _platform.startswith('linux'):
			# Linux
			return False
		elif _platform.startswith('win') or \
			_platform.startswith('cygwin'):
			# Windows
			return True
		elif _platform.startswith('darwin'):
			# Mac OS X
			return False
		else:
			# Other OS
			return False
	elif res == 'F':
		# Fullwidth
		return True
	elif res == "H":
		# Halfwidth
		return False
	elif res == "N":
		# Neutral (Not East Asian)
		return False
	elif res == "Na":
		# Narrow
		return False
	elif res == 'W':
		# Wide
		return True
	else:
		# No such case
		return False

def get_width(string):
	"""Get width of string.

	Parameters
	----------
	string : str
	    Target string.
	"""
	width = 0
	#combining_char = u'[?([\u0300-\u036F]'
	for i in range(len(string)):
		# Combining character
		#if re.match(combining_char, string[i]):
		if unicodedata.combining(string[i]):
			if i == 0:
				# If combining character is at beginning of the line alone
				ch_width = 1
			else:
				ch_width = 0
		# Fullwidth character
		elif (is_wide(string[i])):
			ch_width = 2
		# Neutral character
		else:
			ch_width = 1

		width += ch_width

	return width


def align(string, dir='l', length=12):
	"""Align string in given length.

	Parameters
	----------
	string : str
	    Target string.
	dir : str
	    'l' means left, 'r' means right.
	length : int
	    Align length.
	"""
	diff = length - get_width(string)

	if diff < 0:
		#print("Error: alighment length smaller than actual string length")
		#return None
		diff = 1

	if dir == 'l':
		ret_str = string + ' ' * diff
	elif dir == 'r':
		ret_str = ' ' * diff + string
	else:
		# No such direction
		return None

	return ret_str

def align_test():
	print("Alignment test")
	print("1. English characters (Halfwidth)")
	print("2. Chinese characters (Fullwidth)")
	print("3. Combining characters (Ambiguous)")
	print("=" * 48)
	print("Built-in alignment method")
	print("{:<12}{:<12}{:<12}".format(
				"I",
				"am",
				"Wayne!"))
	print("{:<12}{:<12}{:<12}".format(
				"我",
				"是",
				"偉恩！"))
	print("{0}{1}{2}".format(
				u"I\u0304\u0304".ljust(12),
				u"am\u0304\u0304".ljust(12),
				u"W\u0304ayne\u0304!".ljust(12)))
	print("=" * 48)
	print("Custom alignment method")
	print("{0}{1}{2}".format(
				align("I"),
				align("am"),
				align("Wayne!")))
	
	print("{0}{1}{2}".format(
				align("我"),
				align("是"),
				align("偉恩！")))
	
	print("{0}{1}{2}".format(
				align(u"I\u0304\u0304"),
				align(u"am\u0304\u0304"),
				align("W\u0304ayne\u0304!")))


############
# Datetime #
############

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
		rounded_str = "{0} 週".format(int(tdelta.days/7))
	elif tdelta > timedelta(days=1):
		rounded_str = "{0} 天".format(tdelta.days)
	elif tdelta > timedelta(hours=1):
		rounded_str = "{0} 時".format(int(tdelta.seconds/3600))
	elif tdelta > timedelta(minutes=1):
		rounded_str = "{0} 分".format(int(tdelta.seconds/60))
	else:
		rounded_str = "{0} 秒".format(tdelta.seconds)

	return rounded_str