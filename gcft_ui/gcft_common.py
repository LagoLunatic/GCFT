
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
  def __init__(self):
    super().__init__()
    
    # The default filter key column is 0 (only look at the first column).
    # We switch it to -1 so it searches all columns.
    # In the future we may want to consider searching all columns except numbers (file size, file
    # index, etc). But QSortFilterProxyModel doesn't provide an easy way to do that.
    self.setFilterKeyColumn(-1)
  
  def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
    # Consider a row matching if any of itself or any of its parents or children directly match the filter.
    # Note that when the current row doesn't directly match and neither do its parents, but one of the parents
    # indirectly matches because a *different* child matches, we do not want that to be included.
    if self.check_row_parents_recursive(source_row, source_parent):
      return True
    if self.check_row_children_recursive(source_row, source_parent):
      return True
    return False
  
  def check_row_parents_recursive(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
    if super().filterAcceptsRow(source_row, source_parent):
      # The current row itself matches the filter.
      return True
    
    if source_parent == QModelIndex():
      # No parent, top-level row.
      return False
    
    # If the row doesn't match but does have a parent, check if any of its parents match.
    return self.check_row_parents_recursive(source_parent.row(), source_parent.parent())

  def check_row_children_recursive(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
    if super().filterAcceptsRow(source_row, source_parent):
      # The current row itself matches the filter.
      return True
    
    source_index = self.sourceModel().index(source_row, 0, source_parent)
    for child_row in range(self.sourceModel().rowCount(source_index)):
      if self.check_row_children_recursive(child_row, source_index):
        # One of the current row's children (recursive) matches the filter.
        return True
    
    return False
