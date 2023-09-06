
import traceback
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

class GCFTProgressDialog(QProgressDialog):
  def __init__(self, title, description, max_val):
    QProgressDialog.__init__(self)
    self.setWindowTitle(title)
    self.setLabelText(description)
    self.setMaximum(max_val)
    self.setWindowModality(Qt.ApplicationModal)
    self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
    self.setFixedSize(self.size())
    self.setAutoReset(False)
    self.setCancelButton(None)
    self.show()

class GCFTThread(QThread):
  update_progress = Signal(str, int)
  action_complete = Signal()
  action_failed = Signal(str)
  
  def __init__(self, action_generator):
    QThread.__init__(self)
    
    self.action_generator = action_generator
  
  def run(self):
    try:
      for next_progress_text, progress_value in self.action_generator:
        self.update_progress.emit(next_progress_text, progress_value)
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message = "Error:\n" + str(e) + "\n\n" + stack_trace
      self.action_failed.emit(error_message)
      return
    
    self.action_complete.emit()
