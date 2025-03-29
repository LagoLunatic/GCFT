import os
from io import BytesIO
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from gclib.bfn import BFN
from gclib.bmg import BMG, TEXT_BOX_TYPE_TO_MAX_LINE_LENGTH, Message

from gcft_ui.gcft_common import RecursiveFilterProxyModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from gcft_ui.main_window import GCFTWindow

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_bmg_tab import Ui_BMGTab
else:
  Ui_BMGTab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "bmg_tab.ui"))

class BMGTab(QWidget):
  gcft_window: 'GCFTWindow'
  
  def __init__(self):
    super().__init__()
    self.ui = Ui_BMGTab()
    self.ui.setupUi(self)
    
    self.bmg: BMG | None = None
    self.bmg_name = None
    self.preview_bfn: BFN | None = None
    
    self.column_names = [
      "Message No",
      "Message Index",
      "Text",
    ]
    
    self.model = QStandardItemModel()
    self.model.setHorizontalHeaderLabels(self.column_names)
    self.model.setColumnCount(len(self.column_names))
    self.proxy = RecursiveFilterProxyModel()
    self.proxy.setSourceModel(self.model)
    self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    
    self.ui.bmg_msgs_tree.setModel(self.proxy)
    self.selection_model = self.ui.bmg_msgs_tree.selectionModel()
    
    self.ui.export_bmg.setDisabled(True)
    
    self.ui.import_bmg.clicked.connect(self.import_bmg)
    self.ui.export_bmg.clicked.connect(self.export_bmg)
    self.ui.set_preview_font.clicked.connect(self.set_preview_font)
    
    self.selection_model.currentChanged.connect(self.widget_item_selected)
    self.ui.filter.textChanged.connect(self.filter_messages)
    
    self.ui.msg_string_text_edit.textChanged.connect(self.text_edited)
  
  
  def import_bmg(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.import_bmg_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="BMG messages", file_filters=["BMG Messages (*.bmg)"],
    )
  
  def export_bmg(self):
    bmg_name = self.bmg_name + ".bmg"
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_bmg_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="BMG messages", file_filters=["BMG Messages (*.bmg)"],
      default_file_name=bmg_name
    )
  
  def set_preview_font(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.set_preview_font_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="BFN", file_filters=["BFN Fonts (*.bfn)"],
    )
  
  
  def import_bmg_by_path(self, bmg_path):
    with open(bmg_path, "rb") as f:
      data = BytesIO(f.read())
    
    bmg_name = os.path.splitext(os.path.basename(bmg_path))[0]
    
    self.import_bmg_by_data(data, bmg_name)
  
  def import_bmg_by_data(self, data, bmg_name):
    self.bmg = BMG(data)
    
    self.bmg_name = bmg_name
    
    self.reload_bmg_msgs_tree()
    
    self.ui.export_bmg.setDisabled(False)
  
  def reload_bmg_msgs_tree(self):
    assert self.bmg is not None
    
    self.model.removeRows(0, self.model.rowCount())
    
    for msg_index, message in enumerate(self.bmg.messages):
        msg_no_str = self.gcft_window.stringify_number(message.message_id, min_hex_chars=4)
        msg_no_item = QStandardItem(msg_no_str)
        msg_index_str = self.gcft_window.stringify_number(msg_index, min_hex_chars=4)
        msg_index_item = QStandardItem(msg_index_str)
        truncated_string = self.truncate_message_string(message.string)
        msg_text_item = QStandardItem(truncated_string)
        self.model.appendRow([msg_no_item, msg_index_item, msg_text_item])
        self.set_object_for_model_index(msg_no_item.index(), message)
    
    self.filter_messages()
  
  def set_object_for_model_index(self, index: QModelIndex, obj: Message):
    chunk_type_index = index.siblingAtColumn(self.column_names.index("Message No"))
    item = self.model.itemFromIndex(chunk_type_index)
    item.setData(obj)
  
  def get_object_for_model_index(self, index: QModelIndex) -> Message:
    chunk_type_index = index.siblingAtColumn(self.column_names.index("Message No"))
    item = self.model.itemFromIndex(chunk_type_index)
    obj = item.data()
    assert obj is not None
    return obj
  
  def filter_messages(self):
    query = self.ui.filter.text()
    self.proxy.setFilterFixedString(query)
  
  def widget_item_selected(self, current_index: QModelIndex, previous_index: QModelIndex):
    if not current_index.isValid():
      return
    current_index = self.proxy.mapToSource(current_index)
    message = self.get_object_for_model_index(current_index)
    
    self.ui.msg_string_text_edit.setText(message.string)
    
    # Setting the text automatically triggers the preview to be edited, so no need to manually
    # refresh the preview.
  
  def export_bmg_by_path(self, bmg_path):
    assert self.bmg is not None
    
    self.bmg.save_changes()
    
    with open(bmg_path, "wb") as f:
      self.bmg.data.seek(0)
      f.write(self.bmg.data.read())
    
    self.bmg_name = os.path.splitext(os.path.basename(bmg_path))[0]
    
    QMessageBox.information(self, "BMG saved", "Successfully saved BMG.")
  
  
  def truncate_message_string(self, message_string: str) -> str:
    truncated_string = " ".join(message_string.split("\n"))
    return truncated_string
  
  def get_selected_message_item(self) -> QStandardItem | None:
    selected_index = self.selection_model.currentIndex()
    if not selected_index.isValid():
      return None
    selected_index = self.proxy.mapToSource(selected_index)
    item = self.model.itemFromIndex(selected_index)
    return item
  
  def text_edited(self):
    item = self.get_selected_message_item()
    if item is None:
      return
    message = self.get_object_for_model_index(item.index())
    
    new_value = self.ui.msg_string_text_edit.toPlainText()
    message.string = new_value
    
    truncated_string = self.truncate_message_string(message.string)
    msg_text_item = self.model.itemFromIndex(item.index().siblingAtColumn(self.column_names.index("Text")))
    msg_text_item.setText(truncated_string)
    
    self.update_message_preview()
  
  def update_message_preview(self):
    item = self.get_selected_message_item()
    if item is None:
      return
    message = self.get_object_for_model_index(item.index())
    
    if self.preview_bfn is None:
      self.try_load_preview_bfn()
    if self.preview_bfn is None:
      self.ui.msg_preview_label.setText(
        "Cannot render text preview, no BFN font has been specified.\n" +
        "Select 'Set Preview Font' to select the .bfn font file from the game."
      )
      return
    
    max_line_length = TEXT_BOX_TYPE_TO_MAX_LINE_LENGTH[message.text_box_type]
    message_image = self.preview_bfn.render_string(message.string, max_line_length)
    image_bytes = message_image.tobytes('raw', 'BGRA')
    qimage = QImage(image_bytes, message_image.width, message_image.height, QImage.Format.Format_ARGB32)
    pixmap = QPixmap.fromImage(qimage)
    self.ui.msg_preview_label.setPixmap(pixmap)
  
  def set_preview_font_by_path(self, bfn_path):
    self.gcft_window.settings["text_preview_bfn_path"] = bfn_path
    self.gcft_window.save_settings()
    
    self.try_load_preview_bfn()
    self.update_message_preview()
  
  def try_load_preview_bfn(self):
    if "text_preview_bfn_path" not in self.gcft_window.settings:
      return
    
    bfn_path = self.gcft_window.settings["text_preview_bfn_path"]
    
    try:
      self.preview_bfn = BFN(bfn_path)
    except Exception as e:
      print(f"Failed to load BFN from {bfn_path}")
      self.preview_bfn = None
