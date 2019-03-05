# -*- coding: utf-8 -*-

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
				# If combining character in beginning of the line alone
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
