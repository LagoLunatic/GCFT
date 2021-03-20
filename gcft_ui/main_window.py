
import os
import re
import traceback
import colorsys
from io import BytesIO
from fs_helpers import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from collections import OrderedDict
from gcft_ui.uic.ui_main import Ui_MainWindow
from gcft_ui.gcft_common import GCFTThread, GCFTProgressDialog
from version import VERSION

import yaml
try:
  from yaml import CDumper as Dumper
except ImportError:
  from yaml import Dumper
# Allow yaml to load and dump OrderedDicts.
yaml.SafeLoader.add_constructor(
  yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
  lambda loader, node: OrderedDict(loader.construct_pairs(node))
)
yaml.Dumper.add_representer(
  OrderedDict,
  lambda dumper, data: dumper.represent_dict(data.items())
)

GCM_FILE_EXTS = [".iso", ".gcm"]
RARC_FILE_EXTS = [".arc"]
BTI_FILE_EXTS = [".bti"]
J3D_FILE_EXTS = [
  ".bmd",
  ".bdl",
  ".bmt",
  ".bls",
  ".btk",
  ".bck",
  ".brk",
  ".bpk",
  ".btp",
  ".bca",
  ".bva",
  ".bla",
]
JPC_FILE_EXTS = [".jpc"]

class GCFTWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    self.setAcceptDrops(True)
    
    self.display_hexadecimal_numbers = True # TODO hex/decimal setting
    
    self.ui.tabWidget.currentChanged.connect(self.save_last_used_tab)
    
    # Assign attributes to the main window and each tab to allow them to easily access the other tabs by name.
    # e.g. So you can do `self.bti_tab.bti` instead of `self.window().ui.bti_tab.bti`.
    tabs = list(map(self.ui.tabWidget.widget, range(self.ui.tabWidget.count())))
    for tab in tabs:
      setattr(self, tab.objectName(), tab)
      for other_tab in tabs:
        setattr(tab, other_tab.objectName(), other_tab)
    
    self.load_settings()
    
    if "last_used_tab_name" in self.settings:
      self.set_tab_by_name(self.settings["last_used_tab_name"])
    
    self.setWindowTitle("GameCube File Tools %s" % VERSION)
    
    self.show()
  
  def load_settings(self):
    self.settings_path = "settings.txt"
    if os.path.isfile(self.settings_path):
      with open(self.settings_path) as f:
        self.settings = yaml.safe_load(f)
      if self.settings is None:
        self.settings = OrderedDict()
    else:
      self.settings = OrderedDict()
  
  def save_settings(self):
    with open(self.settings_path, "w") as f:
      yaml.dump(self.settings, f, default_flow_style=False, Dumper=yaml.Dumper)
  
  def save_last_used_tab(self, tab_index):
    tab_name = self.ui.tabWidget.tabText(tab_index)
    self.settings["last_used_tab_name"] = tab_name
  
  def set_tab_by_name(self, tab_name):
    for i in range(self.ui.tabWidget.count()):
      if self.ui.tabWidget.tabText(i) == tab_name:
        self.ui.tabWidget.setCurrentIndex(i)
        return
    print("No tab with name %s found." % tab_name)
  
  
  def generic_do_gui_file_operation(self, op_callback, is_opening, is_saving, is_folder, file_type, file_filter="", default_file_name=None):
    if not is_opening and not is_saving:
      raise Exception("Tried to perform a file operation without opening or saving")
    
    if is_folder:
      last_used_input_folder_key_name = "last_used_input_folder_for_%s_folders" % (file_type.lower())
      last_used_output_folder_key_name = "last_used_output_folder_for_%s_folders" % (file_type.lower())
    else:
      last_used_input_folder_key_name = "last_used_input_folder_for_%s" % (file_type.lower())
      last_used_output_folder_key_name = "last_used_output_folder_for_%s" % (file_type.lower())
    
    if is_saving:
      op_type = "save"
    else:
      op_type = "open"
    
    if is_opening:
      default_dir = None
      if last_used_input_folder_key_name in self.settings:
        default_dir = self.settings[last_used_input_folder_key_name]
      
      if default_file_name is not None:
        if default_dir is None:
          default_dir = default_file_name
        else:
          default_dir = os.path.join(default_dir, default_file_name)
      
      if is_folder:
        in_selected_path = QFileDialog.getExistingDirectory(self, "Select source folder to import from", default_dir)
      else:
        in_selected_path, selected_filter = QFileDialog.getOpenFileName(self, "Open %s" % file_type, default_dir, file_filter)
      if not in_selected_path:
        return
      
      if is_folder and not os.path.isdir(in_selected_path):
        raise Exception("%s folder not found: %s" % (file_type, in_selected_path))
      if not is_folder and not os.path.isfile(in_selected_path):
        raise Exception("%s file not found: %s" % (file_type, in_selected_path))
    
    if is_saving:
      default_dir = None
      if last_used_output_folder_key_name in self.settings:
        default_dir = self.settings[last_used_output_folder_key_name]
      
      if default_file_name is not None:
        if default_dir is None:
          default_dir = default_file_name
        else:
          default_dir = os.path.join(default_dir, default_file_name)
      
      if is_folder:
        out_selected_path = QFileDialog.getExistingDirectory(self, "Select destination folder to export to", default_dir)
      else:
        out_selected_path, selected_filter = QFileDialog.getSaveFileName(self, "Save %s" % file_type, default_dir, file_filter)
      if not out_selected_path:
        return
    
    try:
      if is_opening and is_saving:
        op_callback(in_selected_path, out_selected_path)
      elif is_opening:
        op_callback(in_selected_path)
      else:
        op_callback(out_selected_path)
    # TODO: more specific exceptions, like read permission, FileNotFoundError, etc
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message_title = "Failed to %s %s" % (op_type, file_type)
      if is_folder:
        error_message_title += " folder"
      error_message = "%s with error:\n%s\n\n%s" % (error_message_title, str(e), stack_trace)
      QMessageBox.critical(self, error_message_title, error_message)
      return
    
    if is_opening:
      self.settings[last_used_input_folder_key_name] = os.path.dirname(in_selected_path)
    if is_saving:
      self.settings[last_used_output_folder_key_name] = os.path.dirname(out_selected_path)
    self.save_settings()
  
  def confirm_delete(self, file_name, is_folder=False):
    message = "Are you sure you want to delete \"%s\"" % file_name
    if is_folder:
      message += " and all of its children"
    message += "?"
    
    response = QMessageBox.question(self, 
      "Confirm delete",
      message,
      QMessageBox.Cancel | QMessageBox.Yes,
      QMessageBox.Cancel
    )
    if response == QMessageBox.Yes:
      return True
    else:
      return False
  
  def stringify_number(self, num, min_hex_chars=1):
    if self.display_hexadecimal_numbers:
      format_string = "0x%%0%dX" % min_hex_chars
      return format_string % num
    else:
      return "%d" % num
  
  
  def make_color_selector_button(self, color_owner_object, color_attribute_name, display_name, layout):
    row_widget = QWidget()
    row_layout = QHBoxLayout()
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_widget.setLayout(row_layout)
    layout.addWidget(row_widget)
    
    label = QLabel()
    label.setText(display_name)
    row_layout.addWidget(label)
    
    color_selector_button = QPushButton()
    color_selector_button.setText("Click to set color")
    row_layout.addWidget(color_selector_button)
    
    color_selector_button.setProperty("color_owner_object", color_owner_object)
    color_selector_button.setProperty("color_attribute_name", color_attribute_name)
    
    color_selector_button.clicked.connect(self.open_color_chooser)
    
    color = getattr(color_owner_object, color_attribute_name)
    self.set_background_for_color_selector_button(color_selector_button, color)
  
  def open_color_chooser(self):
    color_selector_button = self.sender()
    
    color_owner_object = color_selector_button.property("color_owner_object")
    color_attribute_name = color_selector_button.property("color_attribute_name")
    
    color = getattr(color_owner_object, color_attribute_name)
    has_alpha = False
    if len(color) == 3:
      r, g, b = color
      a = 255
    elif len(color) == 4:
      r, g, b, a = color
      has_alpha = True
    else:
      QMessageBox.warning(self, "Unknown color format", "Color is neither RGB nor RGBA.")
      return
    
    initial_color = QColor(r, g, b, a)
    color_dialog_options = 0
    if has_alpha:
      color_dialog_options |= QColorDialog.ShowAlphaChannel
    color = QColorDialog.getColor(initial_color, self, "Select color", options=color_dialog_options)
    if not color.isValid():
      return
    r = color.red()
    g = color.green()
    b = color.blue()
    a = color.alpha()
    
    if has_alpha:
      setattr(color_owner_object, color_attribute_name, (r, g, b, a))
    else:
      setattr(color_owner_object, color_attribute_name, (r, g, b))
    
    self.set_background_for_color_selector_button(color_selector_button, (r, g, b, a))
  
  def set_background_for_color_selector_button(self, color_selector_button, color):
    if len(color) == 3:
      r, g, b = color
      a = 255
    elif len(color) == 4:
      r, g, b, a = color
    else:
      QMessageBox.warning(self, "Unknown color format", "Color is neither RGB nor RGBA.")
      return
    
    # Depending on the value of the background color of the button, we need to make the text color either black or white for contrast.
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    if v > 0.5:
      text_color = (0, 0, 0)
    else:
      text_color = (255, 255, 255)
    
    color_selector_button.setStyleSheet(
      "background-color: rgb(%d, %d, %d);" % (r, g, b) + \
      "color: rgb(%d, %d, %d);" % text_color,
    )
  
  
  def start_progress_thread(self, generator, title, max_val, completed_callback):
    self.progress_dialog = GCFTProgressDialog(title, "Initializing...", max_val)
    
    self.progress_thread = GCFTThread(generator)
    self.progress_thread.update_progress.connect(self.update_progress_dialog)
    self.progress_thread.action_complete.connect(completed_callback)
    self.progress_thread.action_failed.connect(self.progress_thread_failed)
    self.progress_thread.action_complete.connect(self.reset_progress_dialog)
    self.progress_thread.action_failed.connect(self.reset_progress_dialog)
    self.progress_thread.start()
  
  def update_progress_dialog(self, next_progress_text, progress_value):
    self.progress_dialog.setLabelText(next_progress_text)
    self.progress_dialog.setValue(progress_value)
  
  def reset_progress_dialog(self):
    self.progress_dialog.reset()
  
  def progress_thread_failed(self, error_message):
    print(error_message)
    QMessageBox.critical(
      self, "Failed",
      error_message
    )
  
  def start_texture_dumper_thread(self, asset_dumper, dumper_generator, max_val):
    self.asset_dumper = asset_dumper
    
    self.start_progress_thread(
      dumper_generator, "Dumping textures", max_val,
      self.dump_all_textures_complete
    )
  
  def dump_all_textures_complete(self):
    failed_dump_message = ""
    if len(self.asset_dumper.failed_file_paths) > 0:
      failed_dump_message = "Failed to dump textures from %d files." % len(self.asset_dumper.failed_file_paths)
      failed_dump_message += "\nPaths of files that failed to dump:\n"
      for file_path in self.asset_dumper.failed_file_paths:
        failed_dump_message += file_path + "\n"
    
    if self.asset_dumper.succeeded_file_count == 0 and len(self.asset_dumper.failed_file_paths) == 0:
      QMessageBox.warning(self, "Failed to find textures", "Could not find any textures to dump.")
    elif self.asset_dumper.succeeded_file_count > 0:
      message = "Successfully dumped %d textures." % self.asset_dumper.succeeded_file_count
      if failed_dump_message:
        message += "\n\n" + failed_dump_message
      QMessageBox.information(self, "Textures dumped", message)
    else:
      QMessageBox.warning(self, "Failed to dump textures", failed_dump_message)
  
  
  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()
  
  def closeEvent(self, event):
    self.save_settings()
  
  def get_drop_action_for_file_path(self, file_path):
    file_ext = os.path.splitext(file_path)[1]
    
    if file_ext in GCM_FILE_EXTS:
      return (self.gcm_tab.import_gcm_by_path, "GCM ISOs")
    elif file_ext in RARC_FILE_EXTS:
      return (self.rarc_tab.import_rarc_by_path, "RARC Archives")
    elif file_ext in BTI_FILE_EXTS:
      return (self.bti_tab.import_bti_by_path, "BTI Images")
    elif file_ext in [".png"]:
      return (self.bti_tab.import_bti_image_by_path, "BTI Images")
    elif file_ext in J3D_FILE_EXTS:
      return (self.j3d_tab.import_j3d_by_path, "J3D Files")
    elif file_ext in JPC_FILE_EXTS:
      return (self.jpc_tab.import_jpc_by_path, "JPC Particle Archives")
  
  def dragEnterEvent(self, event):
    mime_data = event.mimeData()
    if mime_data.hasUrls:
      url = mime_data.urls()[0]
      file_path = url.toLocalFile()
      drop_action = self.get_drop_action_for_file_path(file_path)
      if drop_action is not None:
        event.acceptProposedAction()
  
  def dropEvent(self, event):
    mime_data = event.mimeData()
    if mime_data.hasUrls:
      url = mime_data.urls()[0]
      file_path = url.toLocalFile()
      drop_action = self.get_drop_action_for_file_path(file_path)
      if drop_action is not None:
        func_to_call, tab_name = drop_action
        func_to_call(file_path)
        self.set_tab_by_name(tab_name)
