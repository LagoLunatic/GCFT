
import os

try:
  from sys import _MEIPASS # @IgnoreException
  GCFT_ROOT_PATH = _MEIPASS
  IS_RUNNING_FROM_SOURCE = False
except ImportError:
  GCFT_ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
  IS_RUNNING_FROM_SOURCE = True

ASSETS_PATH = os.path.join(GCFT_ROOT_PATH, "assets")
