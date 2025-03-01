
import traceback
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

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

class RecursiveFilterProxyModel(QSortFilterProxyModel):
  def __init__(self, always_show_children=False):
    super().__init__()
    self.always_show_children = always_show_children
  
  def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
    if self.always_show_children and source_parent.isValid():
      # Always show child rows if their top-level parent is shown.
      return True
    
    # For the top-level rows (the particles), check if any of their children match the filter, recursively.
    return self.check_row_recursive(source_row, source_parent)
  
  def check_row_recursive(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
    if super().filterAcceptsRow(source_row, source_parent):
      # The current row itself matches the filter.
      return True
    
    source_index = self.sourceModel().index(source_row, 0, source_parent)
    for child_row in range(self.sourceModel().rowCount(source_index)):
      if self.check_row_recursive(child_row, source_index):
        # One of the current row's children (recursive) matches the filter.
        return True
    
    return False
