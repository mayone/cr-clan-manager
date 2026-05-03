import inspect
import os
import sys

if not hasattr(sys.modules[__name__], "__file__"):
    __file__ = inspect.getfile(inspect.currentframe())

dir_path: str = os.path.dirname(os.path.realpath(__file__))

CLIENT_SECRET_PATH: str = f"{dir_path}/client_secret.json"
