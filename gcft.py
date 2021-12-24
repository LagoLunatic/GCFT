#!/usr/bin/python3.9

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import sys

sys.path.insert(0, "./wwrando")

from gcft_ui.main_window import GCFTWindow

# Allow keyboard interrupts on the command line to instantly close the program.
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

try:
  from sys import _MEIPASS
except ImportError:
  # Setting the app user model ID is necessary for Windows to display a custom taskbar icon when running from source.
  import ctypes
  app_id = "LagoLunatic.GameCubeFileTools"
  try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
  except AttributeError:
    # Versions of Windows before Windows 7 don't support SetCurrentProcessExplicitAppUserModelID, so just swallow the error.
    pass

qApp = QApplication(sys.argv)
window = GCFTWindow()
if len(sys.argv) == 2:
  file_path = sys.argv[1]
  window.open_file_by_path(file_path)
sys.exit(qApp.exec_())
