# -*- coding: utf-8 -*-

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
