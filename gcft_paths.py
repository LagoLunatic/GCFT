
import os
import platform

import appdirs

import sys
if getattr(sys, 'frozen', False) and hasattr(sys, "_MEIPASS"):
  from sys import _MEIPASS # pyright: ignore [reportAttributeAccessIssue]
  GCFT_ROOT_PATH = _MEIPASS
  IS_RUNNING_FROM_SOURCE = False
  if platform.system() == "Darwin":
    userdata_path = appdirs.user_data_dir("gcft", "gcft")
    if not os.path.isdir(userdata_path):
      os.mkdir(userdata_path)
    SETTINGS_PATH = os.path.join(userdata_path, "settings.txt")
  else:
    SETTINGS_PATH = os.path.join(".", "settings.txt")
else:
  GCFT_ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
  IS_RUNNING_FROM_SOURCE = True
  SETTINGS_PATH = os.path.join(GCFT_ROOT_PATH, "settings.txt")

ASSETS_PATH = os.path.join(GCFT_ROOT_PATH, "assets")
