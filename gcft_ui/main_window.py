
import sys
import os
import traceback
import colorsys
from typing import Callable
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "gclib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "PyJ3DUltra", "build"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "PyJ3DUltra", "build", "Release"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "PyJ3DUltra", "build", "Debug"))

from gcft_ui.gcft_common import GCFTThread, GCFTProgressDialog
from gcft_ui.gcm_tab import GCMTab
from gcft_ui.rarc_tab import RARCTab
from gcft_ui.bti_tab import BTITab
from gcft_ui.j3d_tab import J3DTab
from gcft_ui.jpc_tab import JPCTab
from gcft_ui.bmg_tab import BMGTab
from gcft_ui.dol_tab import DOLTab
from gcft_ui.yaz0_yay0_tab import Yaz0Yay0Tab
from version import VERSION
from gcft_paths import ASSETS_PATH, SETTINGS_PATH

import yaml

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_main import Ui_MainWindow
else:
  Ui_MainWindow = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "main.ui"))

GCM_FILE_EXTS = [".iso", ".gcm"]
# RARC_FILE_EXTS = [".arc"] # Has special logic to check .szs and .szp in addition to .arc
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
BMG_FILE_EXTS = [".bmg"]
DOL_FILE_EXTS = [".dol"]

class GCFTWindow(QMainWindow):
  gcm_tab: GCMTab
  rarc_tab: RARCTab
  bti_tab: BTITab
  j3d_tab: J3DTab
  jpc_tab: JPCTab
  bmg_tab: BMGTab
  dol_tab: DOLTab
  yaz0_yay0_tab: Yaz0Yay0Tab
  
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    self.setAcceptDrops(True)
    
    self.display_hexadecimal_numbers = True # TODO hex/decimal setting
    
    self.ui.tabWidget.currentChanged.connect(self.save_last_used_tab)
    
    # Assign attributes to the main window and each tab to allow them to easily access the other tabs by name.
    # e.g. So you can do `self.bti_tab.bti` instead of `self.gcft_window.ui.bti_tab.bti`.
    tabs = list(map(self.ui.tabWidget.widget, range(self.ui.tabWidget.count())))
    for tab in tabs:
      setattr(tab, "gcft_window", self)
      setattr(self, tab.objectName(), tab)
      for other_tab in tabs:
        setattr(tab, other_tab.objectName(), other_tab)
    
    self.load_settings()
    
    if "last_used_tab_name" in self.settings:
      self.set_tab_by_name(self.settings["last_used_tab_name"])
    
    self.setWindowTitle("GameCube File Tools %s" % VERSION)
    
    icon_path = os.path.join(ASSETS_PATH, "icon.ico")
    self.setWindowIcon(QIcon(icon_path))
    
    self.show()
  
  def load_settings(self):
    if os.path.isfile(SETTINGS_PATH):
      with open(SETTINGS_PATH) as f:
        self.settings = yaml.safe_load(f)
      if self.settings is None:
        self.settings = {}
    else:
      self.settings = {}
  
  def save_settings(self):
    with open(SETTINGS_PATH, "w") as f:
      yaml.dump(self.settings, f, default_flow_style=False, sort_keys=False)
  
  def save_last_used_tab(self, tab_index):
    tab_name = self.ui.tabWidget.tabText(tab_index)
    self.settings["last_used_tab_name"] = tab_name
  
  def set_tab_by_name(self, tab_name):
    for i in range(self.ui.tabWidget.count()):
      if self.ui.tabWidget.tabText(i) == tab_name:
        self.ui.tabWidget.setCurrentIndex(i)
        return
    print("No tab with name %s found." % tab_name)
  
  def get_open_func_and_tab_name_for_file_path(self, file_path):
    file_ext = os.path.splitext(file_path)[1]
    
    if file_ext in GCM_FILE_EXTS:
      return (self.gcm_tab.import_gcm_by_path, "GCM ISOs")
    elif self.rarc_tab.check_file_path_is_rarc(file_path):
      return (self.rarc_tab.import_rarc_by_path, "RARC Archives")
    elif file_ext in BTI_FILE_EXTS:
      return (self.bti_tab.import_bti_by_path, "BTI Images")
    elif file_ext in [".png"]:
      return (self.bti_tab.import_bti_image_by_path, "BTI Images")
    elif file_ext in J3D_FILE_EXTS:
      return (self.j3d_tab.import_j3d_by_path, "J3D Files")
    elif file_ext in JPC_FILE_EXTS:
      return (self.jpc_tab.import_jpc_by_path, "JPC Particle Archives")
    elif file_ext in BMG_FILE_EXTS:
      return (self.bmg_tab.import_bmg_by_path, "BMG Messages")
    elif file_ext in DOL_FILE_EXTS:
      return (self.dol_tab.import_dol_by_path, "DOL Executables")
  
  def open_file_by_path(self, file_path):
    open_action = self.get_open_func_and_tab_name_for_file_path(file_path)
    if open_action is not None:
      func_to_call, tab_name = open_action
      func_to_call(file_path)
      self.set_tab_by_name(tab_name)
  
  
  
  def generic_do_gui_file_operation(
      self, op_callback: Callable, is_opening: bool, is_saving: bool, is_folder: bool,
      file_type: str, file_filters: list=[], default_file_name: str | None = None
    ):
    if "All files (*)" not in file_filters:
      file_filters.append("All files (*)")
    file_filters_str = ";;".join(file_filters)
    
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
        in_selected_path, selected_filter = QFileDialog.getOpenFileName(self, "Open %s" % file_type, default_dir, file_filters_str)
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
        out_selected_path, selected_filter = QFileDialog.getSaveFileName(self, "Save %s" % file_type, default_dir, file_filters_str)
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
      QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes,
      QMessageBox.StandardButton.Cancel
    )
    if response == QMessageBox.StandardButton.Yes:
      return True
    else:
      return False
  
  def stringify_number(self, num, min_hex_chars=1):
    if self.display_hexadecimal_numbers:
      format_string = "0x%%0%dX" % min_hex_chars
      return format_string % num
    else:
      return "%d" % num
  
  
  # TODO: remove all this color button stuff and use FieldEditor instead
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
    color_selector_button.setText("")
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
    color_dialog_options = QColorDialog.ColorDialogOption(0)
    if has_alpha:
      color_dialog_options |= QColorDialog.ColorDialogOption.ShowAlphaChannel
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
      color_selector_button.setText("#%02X%02X%02X" % color)
    elif len(color) == 4:
      r, g, b, a = color
      color_selector_button.setText("#%02X%02X%02X%02X" % color)
    else:
      QMessageBox.warning(self, "Unknown color format", "Color is neither RGB nor RGBA.")
      return
    
    # Depending on the value of the background color of the button, we need to make the text color either black or white for contrast.
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    if v > 0.7:
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
  
  
  def closeEvent(self, event: QCloseEvent):
    self.save_settings()
  
  def dragEnterEvent(self, event: QDragEnterEvent):
    mime_data = event.mimeData()
    if mime_data.hasUrls():
      url = mime_data.urls()[0]
      file_path = url.toLocalFile()
      if not file_path:
        return
      open_action = self.get_open_func_and_tab_name_for_file_path(file_path)
      if open_action is not None:
        event.acceptProposedAction()
  
  def dropEvent(self, event: QDropEvent):
    mime_data = event.mimeData()
    if mime_data.hasUrls():
      url = mime_data.urls()[0]
      file_path = url.toLocalFile()
      if not file_path:
        return
      try:
        self.open_file_by_path(file_path)
      except Exception as e:
        stack_trace = traceback.format_exc()
        error_message_title = "Failed to open file"
        error_message = "%s with error:\n%s\n\n%s" % (error_message_title, str(e), stack_trace)
        QMessageBox.critical(self, error_message_title, error_message)
        return
