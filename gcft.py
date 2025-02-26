#!/usr/bin/env python3

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
  from sys import _MEIPASS # pyright: ignore [reportAttributeAccessIssue]
except ImportError:
  # Setting the app user model ID is necessary for Windows to display a custom taskbar icon when running from source.
  import ctypes
  app_id = "LagoLunatic.GameCubeFileTools"
  try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
  except AttributeError:
    # Versions of Windows before Windows 7 don't support SetCurrentProcessExplicitAppUserModelID, so just swallow the error.
    pass

def get_dark_mode_palette(app) :
  from PySide6.QtGui import QPalette, QColor
  pal = app.palette()

  pal.setColor(QPalette.ColorRole.Window, QColor("#353535"))
  pal.setColor(QPalette.ColorRole.WindowText, QColor("#D9D9D9"))
  pal.setColor(QPalette.ColorRole.Base, QColor("#2A2A2A"))
  pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#424242"))
  pal.setColor(QPalette.ColorRole.ToolTipBase, QColor("#353535"))
  pal.setColor(QPalette.ColorRole.ToolTipText, QColor("#D9D9D9"))
  pal.setColor(QPalette.ColorRole.Text, QColor("#D9D9D9"))
  pal.setColor(QPalette.ColorRole.Dark, QColor("#232323"))
  pal.setColor(QPalette.ColorRole.Shadow, QColor("#141414"))
  pal.setColor(QPalette.ColorRole.Button, QColor("#353535"))
  pal.setColor(QPalette.ColorRole.ButtonText, QColor("#D9D9D9"))
  pal.setColor(QPalette.ColorRole.BrightText, QColor("#D90000"))
  pal.setColor(QPalette.ColorRole.Link, QColor("#2A82DA"))
  pal.setColor(QPalette.ColorRole.Highlight, QColor("#2A82DA"))
  pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#D9D9D9"))

  pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#7F7F7F"))
  pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#7F7F7F"))
  pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#7F7F7F"))
  pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor("#505050"))
  pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor("#7F7F7F"))

  return pal

if __name__ == "__main__":
  qApp = QApplication(sys.argv)
  
  # Use the Qt Fusion style on all platforms for consistency to avoid parts of the UI breaking on certain OSes.
  qApp.setStyle("Fusion")
  
  qt_version_tuple = (6, 6, 0)#tuple(int(num) for num in QT_VERSION.split("."))
  if qt_version_tuple >= (6, 5, 0) and qApp.styleHints().colorScheme() == Qt.ColorScheme.Dark:
    qApp.setPalette(get_dark_mode_palette(qApp))
  
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
