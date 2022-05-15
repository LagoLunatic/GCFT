
import traceback
import time
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
      last_update_time = time.time()
      while True:
        # Need to use a while loop to go through the generator instead of a for loop, as a for loop would silently exit if a StopIteration error ever happened for any reason.
        next_progress_text, progress_value = next(self.action_generator)
        if progress_value == -1:
          break
        if time.time()-last_update_time < 0.1:
          # Limit how frequently the signal is emitted to 10 times per second.
          # Extremely frequent updates (e.g. 1000 times per second) can cause the program to crash with no error message.
          continue
        self.update_progress.emit(next_progress_text, progress_value)
        last_update_time = time.time()
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message = "Error:\n" + str(e) + "\n\n" + stack_trace
      self.action_failed.emit(error_message)
      return
    
    self.action_complete.emit()
