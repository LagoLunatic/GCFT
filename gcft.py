#!/usr/bin/python3

import sys
import traceback
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from gcft_ui.main_window import GCFTWindow

def signal_handler(sig, frame):
  print("Interrupt")
  sys.exit(0)

# Allow keyboard interrupts on the command line to instantly close the program.
import signal
signal.signal(signal.SIGINT, signal_handler)

try:
  from sys import _MEIPASS # @IgnoreException
except ImportError:
  # Setting the app user model ID is necessary for Windows to display a custom taskbar icon when running from source.
  import ctypes
  app_id = "LagoLunatic.GameCubeFileTools"
  try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
  except AttributeError:
    # Versions of Windows before Windows 7 don't support SetCurrentProcessExplicitAppUserModelID, so just swallow the error.
    pass

if __name__ == "__main__":
  qApp = QApplication(sys.argv)
  
  def show_unhandled_exception(excepttype, exception, tb):
    sys.__excepthook__(excepttype, exception, tb)
    error_message_title = "Encountered an unhandled error"
    stack_trace = traceback.format_exception(excepttype, exception, tb)
    error_message = "GCFT encountered an unhandled error.\n"
    error_message += "Please report this issue with a screenshot of this message.\n\n"
    error_message += f"{exception}\n\n"
    error_message += "\n".join(stack_trace)
    QMessageBox.critical(None, error_message_title, error_message)
  sys.excepthook = show_unhandled_exception
  
  # Have a timer updated frequently so keyboard interrupts always work.
  # 499 milliseconds seems to be the maximum value that works here, but use 100 to be safe.
  timer = QTimer()
  timer.start(100)
  timer.timeout.connect(lambda: None)
  
  window = GCFTWindow()
  if len(sys.argv) == 2:
    file_path = sys.argv[1]
    window.open_file_by_path(file_path)
  sys.exit(qApp.exec())
