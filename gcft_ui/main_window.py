
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import os
from io import BytesIO
from collections import OrderedDict
import traceback
import re
from PIL import Image

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

from gcft_ui.ui_main import Ui_MainWindow
from version import VERSION
from gcft_paths import ASSETS_PATH

from wwlib.rarc import RARC
from wwlib.yaz0 import Yaz0
from wwlib.gcm import GCM
from wwlib.jpc import JPC
from wwlib.bti import BTI, BTIFile, WrapMode, FilterMode
from wwlib.j3d import J3DFile
from wwlib.texture_utils import ImageFormat, PaletteFormat
from fs_helpers import *

from asset_dumper import AssetDumper

BTI_ENUM_FIELDS = [
  ("image_format", ImageFormat),
  ("palette_format", PaletteFormat),
  ("wrap_s", WrapMode),
  ("wrap_t", WrapMode),
  ("min_filter", FilterMode),
  ("mag_filter", FilterMode),
]

BTI_INTEGER_FIELDS = [
  ("alpha_setting", 1),
  ("min_lod", 1),
  ("max_lod", 1),
  ("lod_bias", 2),
]

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
    self.display_relative_dir_entries = False
    self.display_rarc_dir_indexes = False
    
    self.gcm = None
    self.rarc = None
    self.rarc_name = None
    self.jpc = None
    self.jpc_name = None
    self.bti = None
    self.bti_name = None
    self.j3d = None
    self.j3d_name = None
    
    self.ui.rarc_files_tree.setColumnWidth(0, 300)
    self.ui.gcm_files_tree.setColumnWidth(0, 300)
    self.ui.jpc_particles_tree.setColumnWidth(0, 100)
    
    self.rarc_col_name_to_index = {}
    for col in range(self.ui.rarc_files_tree.columnCount()):
      column_name = self.ui.rarc_files_tree.headerItem().text(col)
      self.rarc_col_name_to_index[column_name] = col
    
    self.gcm_col_name_to_index = {}
    for col in range(self.ui.gcm_files_tree.columnCount()):
      column_name = self.ui.gcm_files_tree.headerItem().text(col)
      self.gcm_col_name_to_index[column_name] = col
    
    self.j3d_col_name_to_index = {}
    for col in range(self.ui.j3d_chunks_tree.columnCount()):
      column_name = self.ui.j3d_chunks_tree.headerItem().text(col)
      self.j3d_col_name_to_index[column_name] = col
    
    self.ui.export_rarc.setDisabled(True)
    self.ui.import_folder_over_rarc.setDisabled(True)
    self.ui.export_rarc_folder.setDisabled(True)
    self.ui.dump_all_rarc_textures.setDisabled(True)
    self.ui.export_rarc_to_c_header.setDisabled(True)
    self.ui.export_gcm.setDisabled(True)
    self.ui.import_folder_over_gcm.setDisabled(True)
    self.ui.export_gcm_folder.setDisabled(True)
    self.ui.dump_all_gcm_textures.setDisabled(True)
    self.ui.export_jpc.setDisabled(True)
    self.ui.add_particles_from_folder.setDisabled(True)
    self.ui.export_jpc_folder.setDisabled(True)
    self.ui.export_bti.setDisabled(True)
    self.ui.import_bti_image.setDisabled(True)
    self.ui.export_bti_image.setDisabled(True)
    self.ui.export_j3d.setDisabled(True)
    
    self.ui.bti_file_size.setText("")
    self.ui.bti_resolution.setText("")
    
    checkerboard_path = os.path.join(ASSETS_PATH, "checkerboard.png")
    checkerboard_path = checkerboard_path.replace("\\", "/")
    self.ui.bti_image_label.setStyleSheet("border-image: url(%s) repeat;" % checkerboard_path)
    self.ui.bti_image_label.hide()
    
    self.ui.tabWidget.currentChanged.connect(self.save_last_used_tab)
    
    self.ui.import_rarc.clicked.connect(self.import_rarc)
    self.ui.create_rarc.clicked.connect(self.create_rarc)
    self.ui.create_rarc_from_folder.clicked.connect(self.create_rarc_from_folder)
    self.ui.export_rarc.clicked.connect(self.export_rarc)
    self.ui.import_folder_over_rarc.clicked.connect(self.import_folder_over_rarc)
    self.ui.export_rarc_folder.clicked.connect(self.export_rarc_folder)
    self.ui.dump_all_rarc_textures.clicked.connect(self.dump_all_rarc_textures)
    self.ui.export_rarc_to_c_header.clicked.connect(self.export_rarc_to_c_header)
    
    self.ui.rarc_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.rarc_files_tree.customContextMenuRequested.connect(self.show_rarc_files_tree_context_menu)
    self.ui.rarc_files_tree.itemDoubleClicked.connect(self.edit_rarc_files_tree_item_text)
    self.ui.rarc_files_tree.itemChanged.connect(self.rarc_file_tree_item_text_changed)
    self.ui.actionExtractRARCFile.triggered.connect(self.extract_file_from_rarc)
    self.ui.actionReplaceRARCFile.triggered.connect(self.replace_file_in_rarc)
    self.ui.actionDeleteRARCFile.triggered.connect(self.delete_file_in_rarc)
    self.ui.actionAddRARCFile.triggered.connect(self.add_file_to_rarc)
    self.ui.actionAddRARCFolder.triggered.connect(self.add_folder_to_rarc)
    self.ui.actionDeleteRARCFolder.triggered.connect(self.delete_folder_in_rarc)
    self.ui.actionOpenRARCImage.triggered.connect(self.open_image_in_rarc)
    self.ui.actionReplaceRARCImage.triggered.connect(self.replace_image_in_rarc)
    self.ui.actionOpenRARCJ3D.triggered.connect(self.open_j3d_in_rarc)
    
    self.ui.decompress_yaz0.clicked.connect(self.decompress_yaz0)
    self.ui.compress_yaz0.clicked.connect(self.compress_yaz0)
    
    self.ui.import_gcm.clicked.connect(self.import_gcm)
    self.ui.export_gcm.clicked.connect(self.export_gcm)
    self.ui.import_folder_over_gcm.clicked.connect(self.import_folder_over_gcm)
    self.ui.export_gcm_folder.clicked.connect(self.export_gcm_folder)
    self.ui.dump_all_gcm_textures.clicked.connect(self.dump_all_gcm_textures)
    
    self.ui.gcm_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.gcm_files_tree.customContextMenuRequested.connect(self.show_gcm_files_tree_context_menu)
    self.ui.actionExtractGCMFile.triggered.connect(self.extract_file_from_gcm)
    self.ui.actionReplaceGCMFile.triggered.connect(self.replace_file_in_gcm)
    self.ui.actionDeleteGCMFile.triggered.connect(self.delete_file_in_gcm)
    self.ui.actionAddGCMFile.triggered.connect(self.add_file_to_gcm)
    self.ui.actionOpenGCMRARC.triggered.connect(self.open_rarc_in_gcm)
    self.ui.actionReplaceGCMRARC.triggered.connect(self.replace_rarc_in_gcm)
    self.ui.actionOpenGCMImage.triggered.connect(self.open_image_in_gcm)
    self.ui.actionReplaceGCMImage.triggered.connect(self.replace_image_in_gcm)
    self.ui.actionOpenGCMJPC.triggered.connect(self.open_jpc_in_gcm)
    self.ui.actionReplaceGCMJPC.triggered.connect(self.replace_jpc_in_gcm)
    
    self.ui.import_jpc.clicked.connect(self.import_jpc)
    self.ui.export_jpc.clicked.connect(self.export_jpc)
    self.ui.add_particles_from_folder.clicked.connect(self.add_particles_from_folder)
    self.ui.export_jpc_folder.clicked.connect(self.export_jpc_folder)
    
    self.ui.jpc_particles_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.jpc_particles_tree.customContextMenuRequested.connect(self.show_jpc_particles_tree_context_menu)
    self.ui.actionOpenJPCImage.triggered.connect(self.open_image_in_jpc)
    self.ui.actionReplaceJPCImage.triggered.connect(self.replace_image_in_jpc)
    
    self.ui.import_bti.clicked.connect(self.import_bti)
    self.ui.export_bti.clicked.connect(self.export_bti)
    self.ui.import_bti_image.clicked.connect(self.import_bti_image)
    self.ui.export_bti_image.clicked.connect(self.export_bti_image)
    
    for field_name, field_enum in BTI_ENUM_FIELDS:
      widget_name = "bti_" + field_name
      combobox_widget = getattr(self.ui, widget_name)
      combobox_widget.setDisabled(True)
      
      for enum_value in field_enum:
        combobox_widget.addItem(enum_value.name)
      combobox_widget.currentIndexChanged.connect(self.bti_header_field_changed)
    
    for field_name, byte_size in BTI_INTEGER_FIELDS:
      widget_name = "bti_" + field_name
      line_edit_widget = getattr(self.ui, widget_name)
      line_edit_widget.setDisabled(True)
      
      value_str = self.stringify_number(0, min_hex_chars=2*byte_size)
      line_edit_widget.setText(value_str)
      line_edit_widget.editingFinished.connect(self.bti_header_field_changed)
    
    self.ui.import_j3d.clicked.connect(self.import_j3d)
    self.ui.export_j3d.clicked.connect(self.export_j3d)
    
    self.ui.j3d_chunks_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.j3d_chunks_tree.customContextMenuRequested.connect(self.show_j3d_chunks_tree_context_menu)
    self.ui.actionOpenJ3DImage.triggered.connect(self.open_image_in_j3d)
    self.ui.actionReplaceJ3DImage.triggered.connect(self.replace_image_in_j3d)
    
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
  
  def update_progress_dialog(self, next_progress_text, progress_value):
    self.progress_dialog.setLabelText(next_progress_text)
    self.progress_dialog.setValue(progress_value)
  
  def start_texture_dumper_thread(self, dumper_generator):
    self.dumper_thread = GCFTThread(dumper_generator)
    self.dumper_thread.update_progress.connect(self.update_progress_dialog)
    self.dumper_thread.action_complete.connect(self.dump_all_textures_complete)
    self.dumper_thread.action_failed.connect(self.dump_all_textures_failed)
    self.dumper_thread.start()
  
  def dump_all_textures_complete(self):
    self.progress_dialog.reset()
    
    failed_dump_message = ""
    if len(self.asset_dumper.failed_file_paths) > 0:
      failed_dump_message = "Failed to dump textures from %d files." % len(self.asset_dumper.failed_file_paths)
      failed_dump_message += "\nPaths of files that failed to dump:\n"
      for file_path in self.asset_dumper.failed_file_paths:
        failed_dump_message += file_path + "\n"
    
    if self.asset_dumper.succeeded_file_count == 0 and len(self.asset_dumper.failed_file_paths) == 0:
      QMessageBox.warning(self, "Failed to find textures", "Could not find any textures to dump.")
    elif self.asset_dumper.succeeded_file_count > 0:
      QMessageBox.information(self, "Textures dumped", "Successfully dumped %d textures.\n\n%s" % (self.asset_dumper.succeeded_file_count, failed_dump_message))
    else:
      QMessageBox.warning(self, "Failed to dump textures", failed_dump_message)
  
  def dump_all_textures_failed(self, error_message):
    self.progress_dialog.reset()
    
    print(error_message)
    QMessageBox.critical(
      self, "Failed to dump textures",
      error_message
    )
  
  
  
  def import_gcm(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="GCM", file_filter="GC ISO Files (*.iso *.gcm)"
    )
  
  def export_gcm(self):
    self.generic_do_gui_file_operation(
      op_callback=self.export_gcm_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="GCM", file_filter="GC ISO Files (*.iso *.gcm)"
    )
  
  def import_folder_over_gcm(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_folder_over_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="GCM"
    )
  
  def export_gcm_folder(self):
    self.generic_do_gui_file_operation(
      op_callback=self.export_gcm_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="GCM"
    )
  
  def dump_all_gcm_textures(self):
    self.generic_do_gui_file_operation(
      op_callback=self.dump_all_gcm_textures_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="all GCM texture"
    )
  
  def extract_file_from_gcm(self):
    file = self.ui.actionExtractGCMFile.data()
    self.generic_do_gui_file_operation(
      op_callback=self.extract_file_from_gcm_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def replace_file_in_gcm(self):
    file = self.ui.actionReplaceGCMFile.data()
    self.generic_do_gui_file_operation(
      op_callback=self.replace_file_in_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def add_file_to_gcm(self):
    self.generic_do_gui_file_operation(
      op_callback=self.add_file_to_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file"
    )
  
  def import_rarc(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="RARC", file_filter="RARC files (*.arc)"
    )
  
  def create_rarc_from_folder(self):
    self.generic_do_gui_file_operation(
      op_callback=self.create_rarc_from_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="RARC"
    )
  
  def export_rarc(self):
    rarc_name = self.rarc_name + ".arc"
    self.generic_do_gui_file_operation(
      op_callback=self.export_rarc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="RARC", file_filter="RARC files (*.arc)",
      default_file_name=rarc_name
    )
  
  def import_folder_over_rarc(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_folder_over_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="RARC"
    )
  
  def export_rarc_folder(self):
    self.generic_do_gui_file_operation(
      op_callback=self.export_rarc_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="RARC"
    )
  
  def dump_all_rarc_textures(self):
    self.generic_do_gui_file_operation(
      op_callback=self.dump_all_rarc_textures_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="all RARC texture"
    )
  
  def export_rarc_to_c_header(self):
    header_name = "res_%s.h" % self.rarc_name.lower()
    self.generic_do_gui_file_operation(
      op_callback=self.export_rarc_to_c_header_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="C header",
      default_file_name=header_name
    )
  
  def extract_file_from_rarc(self):
    file = self.ui.actionExtractRARCFile.data()
    self.generic_do_gui_file_operation(
      op_callback=self.extract_file_from_rarc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def replace_file_in_rarc(self):
    file = self.ui.actionReplaceRARCFile.data()
    self.generic_do_gui_file_operation(
      op_callback=self.replace_file_in_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def add_file_to_rarc(self):
    self.generic_do_gui_file_operation(
      op_callback=self.add_file_to_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file"
    )
  
  def import_bti(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_bti_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="BTI", file_filter="BTI files (*.bti)"
    )
  
  def export_bti(self):
    bti_name = self.bti_name + ".bti"
    self.generic_do_gui_file_operation(
      op_callback=self.export_bti_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="BTI", file_filter="BTI files (*.bti)",
      default_file_name=bti_name
    )
  
  def import_bti_image(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_bti_image_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="image", file_filter="PNG Files (*.png)"
    )
  
  def export_bti_image(self):
    png_name = self.bti_name + ".png"
    self.generic_do_gui_file_operation(
      op_callback=self.export_bti_image_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="image", file_filter="PNG Files (*.png)",
      default_file_name=png_name
    )
  
  def import_j3d(self):
    filters = [
      "Models and material tables (*.bmd *.bdl *.bmt)",
      "All J3D files (*.bmd *.bdl *.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)",
    ]
    
    self.generic_do_gui_file_operation(
      op_callback=self.import_j3d_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="J3D file", file_filter=";;".join(filters)
    )
  
  def export_j3d(self):
    filters = []
    current_filter = self.get_file_filter_by_current_j3d_file_type()
    if current_filter is not None:
      filters.append(current_filter)
    filters.append("All J3D files (*.bmd *.bdl *.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)")
    
    j3d_name = "%s.%s" % (self.j3d_name, self.j3d.file_type[:3])
    self.generic_do_gui_file_operation(
      op_callback=self.export_j3d_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="J3D file", file_filter=";;".join(filters),
      default_file_name=j3d_name
    )
  
  def import_jpc(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_jpc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="JPC", file_filter="JPC Files (*.jpc)"
    )
  
  def export_jpc(self):
    jpc_name = self.jpc_name + ".jpc"
    self.generic_do_gui_file_operation(
      op_callback=self.export_jpc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="JPC", file_filter="JPC Files (*.jpc)",
      default_file_name=jpc_name
    )
  
  def add_particles_from_folder(self):
    self.generic_do_gui_file_operation(
      op_callback=self.add_particles_from_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="JPC"
    )
  
  def export_jpc_folder(self):
    self.generic_do_gui_file_operation(
      op_callback=self.export_jpc_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="JPC"
    )
  
  def decompress_yaz0(self):
    self.generic_do_gui_file_operation(
      op_callback=self.decompress_yaz0_by_paths,
      is_opening=True, is_saving=True, is_folder=False,
      file_type="Yaz0", file_filter=""
    )
  
  def compress_yaz0(self):
    self.generic_do_gui_file_operation(
      op_callback=self.compress_yaz0_by_paths,
      is_opening=True, is_saving=True, is_folder=False,
      file_type="Yaz0", file_filter=""
    )
  
  
  def import_rarc_by_path(self, rarc_path):
    with open(rarc_path, "rb") as f:
      data = BytesIO(f.read())
    
    rarc_name = os.path.splitext(os.path.basename(rarc_path))[0]
    
    self.import_rarc_by_data(data, rarc_name)
  
  def import_rarc_by_data(self, data, rarc_name):
    self.rarc = RARC()
    self.rarc.read(data)
    
    self.rarc_name = rarc_name
    
    self.reload_rarc_files_tree()
  
  def create_rarc(self):
    self.rarc = RARC()
    self.rarc.add_root_directory()
    
    self.rarc_name = "archive"
    
    self.reload_rarc_files_tree()
  
  def create_rarc_from_folder_by_path(self, base_dir):
    self.rarc = RARC()
    self.rarc.add_root_directory()
    
    self.rarc_name = os.path.basename(base_dir)
    
    for dir_path, subdir_names, file_names in os.walk(base_dir):
      dir_relative_path = os.path.relpath(dir_path, base_dir).replace("\\", "/")
      dir_node = self.rarc.get_node_by_path(dir_relative_path)
      
      for subdir_name in subdir_names:
        node_type = subdir_name[:4].upper()
        dir_file_entry, node = self.rarc.add_new_directory(subdir_name, node_type, dir_node)
      
      for file_name in file_names:
        file_path = os.path.join(dir_path, file_name)
        with open(file_path, "rb") as f:
          file_data = BytesIO(f.read())
        file_entry = self.rarc.add_new_file(file_name, file_data, dir_node)
    
    self.reload_rarc_files_tree()
  
  def reload_rarc_files_tree(self):
    self.ui.rarc_files_tree.clear()
    
    self.rarc_node_to_tree_widget_item = {}
    self.rarc_tree_widget_item_to_node = {}
    self.rarc_file_entry_to_tree_widget_item = {}
    self.rarc_tree_widget_item_to_file_entry = {}
    
    root_node = self.rarc.nodes[0]
    root_item = QTreeWidgetItem([root_node.name, root_node.type, "", "", ""])
    root_item.setFlags(root_item.flags() | Qt.ItemIsEditable)
    self.ui.rarc_files_tree.addTopLevelItem(root_item)
    self.rarc_node_to_tree_widget_item[root_node] = root_item
    self.rarc_tree_widget_item_to_node[root_item] = root_node
    
    for file_entry in self.rarc.file_entries:
      self.add_rarc_file_entry_to_files_tree(file_entry)
    
    # Expand the root node by default.
    self.ui.rarc_files_tree.topLevelItem(0).setExpanded(True)
    
    self.ui.export_rarc.setDisabled(False)
    self.ui.import_folder_over_rarc.setDisabled(False)
    self.ui.export_rarc_folder.setDisabled(False)
    self.ui.dump_all_rarc_textures.setDisabled(False)
    self.ui.export_rarc_to_c_header.setDisabled(False)
  
  def add_rarc_file_entry_to_files_tree(self, file_entry):
    index_of_entry_in_parent_dir = file_entry.parent_node.files.index(file_entry)
    
    if file_entry.is_dir:
      dir_file_entry = file_entry
      if file_entry.name in [".", ".."] and not self.display_relative_dir_entries:
        return
      
      node = file_entry.node
      
      parent_item = self.rarc_node_to_tree_widget_item[dir_file_entry.parent_node]
      
      if self.display_rarc_dir_indexes:
        dir_file_index = self.rarc.file_entries.index(dir_file_entry)
        dir_file_index_str = self.stringify_number(dir_file_index, min_hex_chars=4)
      else:
        dir_file_index_str = ""
      
      if file_entry.name in [".", ".."]:
        item = QTreeWidgetItem([file_entry.name, "", dir_file_index_str, "", ""])
        parent_item.insertChild(index_of_entry_in_parent_dir, item)
      else:
        item = QTreeWidgetItem([node.name, node.type, dir_file_index_str, "", ""])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        parent_item.insertChild(index_of_entry_in_parent_dir, item)
        
        self.rarc_node_to_tree_widget_item[node] = item
        self.rarc_tree_widget_item_to_node[item] = node
      
      self.rarc_file_entry_to_tree_widget_item[dir_file_entry] = item
      self.rarc_tree_widget_item_to_file_entry[item] = dir_file_entry
    else:
      file_size_str = self.stringify_number(file_entry.data_size)
      file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
      file_index = self.rarc.file_entries.index(file_entry)
      file_index_str = self.stringify_number(file_index, min_hex_chars=4)
      
      parent_item = self.rarc_node_to_tree_widget_item[file_entry.parent_node]
      item = QTreeWidgetItem([file_entry.name, "", file_index_str, file_id_str, file_size_str])
      item.setFlags(item.flags() | Qt.ItemIsEditable)
      parent_item.insertChild(index_of_entry_in_parent_dir, item)
      self.rarc_file_entry_to_tree_widget_item[file_entry] = item
      self.rarc_tree_widget_item_to_file_entry[item] = file_entry
  
  def export_rarc_by_path(self, rarc_path):
    self.rarc.save_changes()
    
    with open(rarc_path, "wb") as f:
      self.rarc.data.seek(0)
      f.write(self.rarc.data.read())
    
    self.rarc_name = os.path.splitext(os.path.basename(rarc_path))[0]
    
    QMessageBox.information(self, "RARC saved", "Successfully saved RARC.")
  
  def import_folder_over_rarc_by_path(self, folder_path):
    num_files_overwritten = self.rarc.import_all_files_from_disk(folder_path)
    
    if num_files_overwritten == 0:
      QMessageBox.warning(self, "No matching files found", "The selected folder does not contain any files matching the name and directory structure of files in the currently loaded RARC. No files imported.")
      return
    
    QMessageBox.information(self, "Folder imported", "Successfully overwrote %d files in the RARC from \"%s\"." % (num_files_overwritten, folder_path))
  
  def export_rarc_folder_by_path(self, folder_path):
    self.rarc.extract_all_files_to_disk(output_directory=folder_path)
    
    QMessageBox.information(self, "RARC extracted", "Successfully extracted RARC contents to \"%s\"." % folder_path)
  
  def dump_all_rarc_textures_by_path(self, folder_path):
    self.asset_dumper = AssetDumper()
    
    dumper_generator = self.asset_dumper.dump_all_textures_in_rarc(self.rarc, folder_path)
    
    max_progress_val = len(self.asset_dumper.get_all_rarc_file_paths(self.rarc))
    self.progress_dialog = GCFTProgressDialog("Dumping textures", "Initializing...", max_progress_val)
    
    self.start_texture_dumper_thread(dumper_generator)
  
  def export_rarc_to_c_header_by_path(self, header_path):
    out_str = "#define %s_RES_NAME \"%s\"\n\n" % (self.rarc_name.upper(), self.rarc_name)
    out_str += "enum %s_RES_FILE_IDS {\n" % (self.rarc_name.upper())
    on_first_node = True
    for node in self.rarc.nodes:
      wrote_node_comment = False
      
      for file_entry in node.files:
        if file_entry.is_dir:
          continue
        
        if not wrote_node_comment:
          if not on_first_node:
            out_str += "  \n"
          out_str += "  /* %s */\n" % node.type.strip()
          wrote_node_comment = True
          on_first_node = False
        
        file_name, file_ext = os.path.splitext(file_entry.name)
        file_ext = file_ext[1:]
        
        # Try to prevent duplicate names.
        all_files_with_same_name = [f for f in self.rarc.file_entries if f.name == file_entry.name]
        if len(all_files_with_same_name) > 1:
          duplicate_index = all_files_with_same_name.index(file_entry)
          file_name = "%s_%d" % (file_name, duplicate_index+1)
        
        enum_val_name = "%s_%s_%s" % (self.rarc_name, file_ext, file_name)
        enum_val_name = re.sub(r"[\s@:\.,\-<>*%\"!&()|]", "_", enum_val_name) # Sanitize identifier
        enum_val_name = enum_val_name.upper()
        
        out_str += "  %s=0x%X,\n" % (enum_val_name, file_entry.id)
    out_str += "};\n"
    
    with open(header_path, "w") as f:
      f.write(out_str)
  
  
  def get_rarc_file_by_tree_item(self, item):
    if item not in self.rarc_tree_widget_item_to_file_entry:
      return None
    
    return self.rarc_tree_widget_item_to_file_entry[item]
  
  def get_rarc_tree_item_by_file(self, file):
    if file not in self.rarc_file_entry_to_tree_widget_item:
      return None
    
    return self.rarc_file_entry_to_tree_widget_item[file]
  
  def get_rarc_node_by_tree_item(self, item):
    if item not in self.rarc_tree_widget_item_to_node:
      return None
    
    return self.rarc_tree_widget_item_to_node[item]
  
  def get_rarc_tree_item_by_node(self, node):
    if node not in self.rarc_node_to_tree_widget_item:
      return None
    
    return self.rarc_node_to_tree_widget_item[node]
  
  def show_rarc_files_tree_context_menu(self, pos):
    if self.rarc is None:
      return
    
    item = self.ui.rarc_files_tree.itemAt(pos)
    if item is None:
      return
    
    node = self.get_rarc_node_by_tree_item(item)
    if node:
      # TODO: Implement extracting/replacing folders
      menu = QMenu(self)
      menu.addAction(self.ui.actionAddRARCFile)
      self.ui.actionAddRARCFile.setData(node)
      menu.addAction(self.ui.actionAddRARCFolder)
      self.ui.actionAddRARCFolder.setData(node)
      if node.dir_entry is not None:
        menu.addAction(self.ui.actionDeleteRARCFolder)
        self.ui.actionDeleteRARCFolder.setData(node)
      menu.exec_(self.ui.rarc_files_tree.mapToGlobal(pos))
    else:
      file = self.get_rarc_file_by_tree_item(item)
      if file is None:
        return
      
      if file.is_dir:
        # Selected a . or .. relative directory entry. Don't give any options for this..
        pass
      else:
        menu = QMenu(self)
        
        basename, file_ext = os.path.splitext(file.name)
        if file_ext == ".bti":
          menu.addAction(self.ui.actionOpenRARCImage)
          self.ui.actionOpenRARCImage.setData(file)
          
          menu.addAction(self.ui.actionReplaceRARCImage)
          self.ui.actionReplaceRARCImage.setData(file)
          if self.bti is None:
            self.ui.actionReplaceRARCImage.setDisabled(True)
          else:
            self.ui.actionReplaceRARCImage.setDisabled(False)
        elif file_ext in [".bdl", ".bmd", ".bmt", ".btk", ".bck", ".brk", ".btp"]:
          menu.addAction(self.ui.actionOpenRARCJ3D)
          self.ui.actionOpenRARCJ3D.setData(file)
        
        menu.addAction(self.ui.actionExtractRARCFile)
        self.ui.actionExtractRARCFile.setData(file)
        menu.addAction(self.ui.actionReplaceRARCFile)
        self.ui.actionReplaceRARCFile.setData(file)
        menu.addAction(self.ui.actionDeleteRARCFile)
        self.ui.actionDeleteRARCFile.setData(file)
        
        menu.exec_(self.ui.rarc_files_tree.mapToGlobal(pos))
  
  def extract_file_from_rarc_by_path(self, file_path):
    file = self.ui.actionExtractRARCFile.data()
    
    with open(file_path, "wb") as f:
      file.data.seek(0)
      f.write(file.data.read())
  
  def replace_file_in_rarc_by_path(self, file_path):
    file = self.ui.actionReplaceRARCFile.data()
    
    with open(file_path, "rb") as f:
      data = BytesIO(f.read())
    file.data = data
    
    # Update changed file size
    file_size_str = self.stringify_number(data_len(file.data))
    item = self.get_rarc_tree_item_by_file(file)
    item.setText(self.rarc_col_name_to_index["File Size"], file_size_str)
  
  def delete_file_in_rarc(self):
    file_entry = self.ui.actionDeleteRARCFile.data()
    
    if not self.confirm_delete(file_entry.name):
      return
    
    node = file_entry.parent_node
    
    self.rarc.delete_file(file_entry)
    
    file_item = self.get_rarc_tree_item_by_file(file_entry)
    dir_item = self.get_rarc_tree_item_by_node(node)
    dir_item.removeChild(file_item)
    del self.rarc_file_entry_to_tree_widget_item[file_entry]
    del self.rarc_tree_widget_item_to_file_entry[file_item]
  
  def open_image_in_rarc(self):
    file_entry = self.ui.actionOpenRARCImage.data()
    
    bti_name = os.path.splitext(file_entry.name)[0]
    
    data = make_copy_data(file_entry.data)
    self.import_bti_by_data(data, bti_name)
    
    self.set_tab_by_name("BTI Images")
  
  def replace_image_in_rarc(self):
    file = self.ui.actionReplaceRARCImage.data()
    
    self.bti.save_changes()
    
    file.data = make_copy_data(self.bti.data)
    
    # Update changed file size
    file_size_str = self.stringify_number(data_len(file.data))
    item = self.get_rarc_tree_item_by_file(file)
    item.setText(self.rarc_col_name_to_index["File Size"], file_size_str)
  
  def open_j3d_in_rarc(self):
    file_entry = self.ui.actionOpenRARCJ3D.data()
    
    j3d_name = os.path.splitext(file_entry.name)[0]
    
    data = make_copy_data(file_entry.data)
    self.import_j3d_by_data(data, j3d_name)
    
    self.set_tab_by_name("J3D Files")
  
  def add_file_to_rarc_by_path(self, file_path):
    parent_node = self.ui.actionAddRARCFile.data()
    
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
      file_data = BytesIO(f.read())
    file_size = data_len(file_data)
    file_size_str = self.stringify_number(file_size)
    
    existing_file_names_in_node = [fe.name for fe in parent_node.files]
    if file_name in existing_file_names_in_node:
      QMessageBox.warning(self, "File already exists", "Cannot add new file. The selected folder already contains a file named \"%s\".\n\nIf you wish to replace the existing file, right click on it in the files tree and select 'Replace File'." % file_name)
      return
    
    file_entry = self.rarc.add_new_file(file_name, file_data, parent_node)
    
    file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
    file_index = self.rarc.file_entries.index(file_entry)
    file_index_str = self.stringify_number(file_index, min_hex_chars=4)
    
    parent_dir_item = self.get_rarc_tree_item_by_node(parent_node)
    file_item = QTreeWidgetItem([file_entry.name, "", file_index_str, file_id_str, file_size_str])
    file_item.setFlags(file_item.flags() | Qt.ItemIsEditable)
    index_of_file_in_dir = parent_node.files.index(file_entry)
    parent_dir_item.insertChild(index_of_file_in_dir, file_item)
    
    self.rarc_file_entry_to_tree_widget_item[file_entry] = file_item
    self.rarc_tree_widget_item_to_file_entry[file_item] = file_entry
  
  def add_folder_to_rarc(self):
    parent_node = self.ui.actionAddRARCFolder.data()
    
    dir_name, confirmed = QInputDialog.getText(
      self, "Input Folder Name", "Write the name for the new folder:",
      flags=Qt.WindowSystemMenuHint | Qt.WindowTitleHint
    )
    if not confirmed:
      return
    if len(dir_name) == 0:
      QMessageBox.warning(self, "Invalid folder name", "Folder name cannot be empty.")
      return
    if dir_name in [".", ".."]:
      QMessageBox.warning(self, "Invalid folder name", "You cannot create folders named \".\" or \"..\".")
      return
    
    node_type, confirmed = QInputDialog.getText(
      self, "Input Folder Type", "Write the type of the new folder (maximum 4 characters):",
      flags=Qt.WindowSystemMenuHint | Qt.WindowTitleHint
    )
    if not confirmed:
      return
    if len(node_type) == 0:
      QMessageBox.warning(self, "Invalid folder type", "Folder type cannot be empty.")
      return
    if len(node_type) > 4:
      QMessageBox.warning(self, "Invalid folder type", "Folder types cannot be longer than 4 characters.")
      return
    
    dir_file_entry, node = self.rarc.add_new_directory(dir_name, node_type, parent_node)
    
    self.add_rarc_file_entry_to_files_tree(dir_file_entry)
    for child_file_entry in dir_file_entry.node.files:
      # Add the . and .. relative dir entries.
      self.add_rarc_file_entry_to_files_tree(child_file_entry)
    
    # Update all the displayed file indexes in case they got shuffled around by adding a new directory.
    for file_entry, item in self.rarc_file_entry_to_tree_widget_item.items():
      if file_entry.is_dir:
        continue
      file_index = self.rarc.file_entries.index(file_entry)
      file_index_str = self.stringify_number(file_index, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File Index"], file_index_str)
  
  def delete_folder_in_rarc(self):
    node = self.ui.actionDeleteRARCFolder.data()
    
    if not self.confirm_delete(node.name, is_folder=True):
      return
    
    dir_entry = node.dir_entry
    
    self.rarc.delete_directory(dir_entry)
    
    dir_item = self.get_rarc_tree_item_by_file(dir_entry)
    parent_dir_item = self.get_rarc_tree_item_by_node(dir_entry.parent_node)
    parent_dir_item.removeChild(dir_item)
    del self.rarc_file_entry_to_tree_widget_item[dir_entry]
    del self.rarc_tree_widget_item_to_file_entry[dir_item]
  
  
  def edit_rarc_files_tree_item_text(self, item, column):
    if (item.flags() & Qt.ItemIsEditable) == 0:
      return
    
    node = self.get_rarc_node_by_tree_item(item)
    
    # Allow editing only certain columns.
    if node is not None:
      if column in [self.rarc_col_name_to_index["File Name"], self.rarc_col_name_to_index["Folder Type"]]: 
        self.ui.rarc_files_tree.editItem(item, column)
    else:
      if column in [self.rarc_col_name_to_index["File Name"], self.rarc_col_name_to_index["File ID"]]: 
        self.ui.rarc_files_tree.editItem(item, column)
  
  def rarc_file_tree_item_text_changed(self, item, column):
    if column == self.rarc_col_name_to_index["File Name"]:
      self.change_rarc_file_name(item)
    elif column == self.rarc_col_name_to_index["Folder Type"]:
      self.change_rarc_node_type(item)
    elif column == self.rarc_col_name_to_index["File ID"]:
      self.change_rarc_file_id(item)
  
  def change_rarc_file_name(self, item):
    node = self.get_rarc_node_by_tree_item(item)
    file_entry = self.get_rarc_file_by_tree_item(item)
    new_file_name = item.text(self.rarc_col_name_to_index["File Name"])
    
    if node is not None:
      if len(new_file_name) == 0:
        QMessageBox.warning(self, "Invalid folder name", "Folder name cannot be empty.")
        item.setText(self.rarc_col_name_to_index["File Name"], node.name)
        return
      
      node.name = new_file_name
      if node.dir_entry is not None:
        node.dir_entry.name = new_file_name
    else:
      if len(new_file_name) == 0:
        QMessageBox.warning(self, "Invalid file name", "File name cannot be empty.")
        item.setText(self.rarc_col_name_to_index["File Name"], file_entry.name)
        return
      
      other_file_entry = next((fe for fe in self.rarc.file_entries if fe.name == new_file_name), None)
      
      if other_file_entry == file_entry:
        # File name not changed
        return
      
      if other_file_entry is not None:
        QMessageBox.warning(self, "Duplicate file name", "The file name you entered is already used by another file.\n\nNote that file names in RARCs must be unique - even if the other file is in a completely different folder.")
        item.setText(self.rarc_col_name_to_index["File Name"], file_entry.name)
        return
    
      file_entry.name = new_file_name
    
    item.setText(self.rarc_col_name_to_index["File Name"], new_file_name)
  
  def change_rarc_node_type(self, item):
    node = self.get_rarc_node_by_tree_item(item)
    new_node_type = item.text(self.rarc_col_name_to_index["Folder Type"])
    
    if len(new_node_type) == 0:
      QMessageBox.warning(self, "Invalid folder type", "Folder type cannot be empty.")
      item.setText(self.rarc_col_name_to_index["Folder Type"], node.type)
      return
    if len(new_node_type) > 4:
      QMessageBox.warning(self, "Invalid folder type", "Folder types cannot be longer than 4 characters.")
      item.setText(self.rarc_col_name_to_index["Folder Type"], node.type)
      return
    
    if len(new_node_type) < 4:
      spaces_to_add = 4-len(new_node_type)
      new_node_type += " "*spaces_to_add
    
    node.type = new_node_type
    
    item.setText(self.rarc_col_name_to_index["Folder Type"], new_node_type)
  
  def change_rarc_file_id(self, item):
    file_entry = self.get_rarc_file_by_tree_item(item)
    new_file_id_str = item.text(self.rarc_col_name_to_index["File ID"])
    
    if self.display_hexadecimal_numbers:
      hexadecimal_match = re.search(r"^\s*(?:0x)?([0-9a-f]+)\s*$", new_file_id_str, re.IGNORECASE)
      if hexadecimal_match:
        new_file_id = int(hexadecimal_match.group(1), 16)
      else:
        QMessageBox.warning(self, "Invalid file ID", "\"%s\" is not a valid hexadecimal number." % new_file_id_str)
        file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
        item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
        return
    else:
      decimal_match = re.search(r"^\s*(\d+)\s*$", new_file_id_str, re.IGNORECASE)
      if decimal_match:
        new_file_id = int(decimal_match.group(1))
      else:
        QMessageBox.warning(self, "Invalid file ID", "\"%s\" is not a valid decimal number." % new_file_id_str)
        file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
        item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
        return
    
    if new_file_id >= 0xFFFF:
      QMessageBox.warning(self, "Invalid file ID", "\"%s\" is too large to be a file ID. It must be in the range 0x0000-0xFFFE." % new_file_id_str)
      file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
      return
    
    other_file_entry = next((fe for fe in self.rarc.file_entries if fe.id == new_file_id), None)
    
    if other_file_entry == file_entry:
      # File ID not changed
      file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
      return
    
    if other_file_entry is not None:
      QMessageBox.warning(self, "Duplicate file ID", "The file ID you entered is already used by the file \"%s\"." % other_file_entry.name)
      file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
      return
    
    file_entry.id = new_file_id
    
    file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
    item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
  
  
  
  def decompress_yaz0_by_paths(self, comp_path, decomp_path):
    with open(comp_path, "rb") as f:
      comp_data = BytesIO(f.read())
    if try_read_str(comp_data, 0, 4) != "Yaz0":
      QMessageBox.warning(self, "Not Yaz0 compressed", "The selected file is not Yaz0 compressed. Cannot decompress.")
      return
    
    decomp_data = Yaz0.decompress(comp_data)
    
    with open(decomp_path, "wb") as f:
      decomp_data.seek(0)
      f.write(decomp_data.read())
    
    QMessageBox.information(self, "Decompressed file saved", "Successfully decompressed and saved file.")
  
  def compress_yaz0_by_paths(self, decomp_path, comp_path):
    with open(decomp_path, "rb") as f:
      decomp_data = BytesIO(f.read())
    if try_read_str(decomp_data, 0, 4) == "Yaz0":
      QMessageBox.warning(self, "Already Yaz0 compressed", "The selected file is already Yaz0 compressed. Cannot compress.")
      return
    
    # TODO: progress bar?
    comp_data = Yaz0.compress(decomp_data)
    
    with open(comp_path, "wb") as f:
      comp_data.seek(0)
      f.write(comp_data.read())
    
    QMessageBox.information(self, "Compressed file saved", "Successfully compressed and saved file.")
  
  
  def import_gcm_by_path(self, gcm_path):
    self.gcm = GCM(gcm_path)
    
    self.gcm.read_entire_disc()
    
    self.ui.gcm_files_tree.clear()
    
    self.gcm_file_entry_to_tree_widget_item = {}
    self.gcm_tree_widget_item_to_file_entry = {}
    
    # Add data files.
    for file_entry in self.gcm.file_entries:
      if file_entry.is_dir:
        file_size_str = ""
      else:
        file_size_str = self.stringify_number(file_entry.file_size)
      
      if file_entry.parent is None:
        # Root entry. Add as a top-level item.
        item = QTreeWidgetItem(["files", file_size_str])
        self.ui.gcm_files_tree.addTopLevelItem(item)
        self.gcm_file_entry_to_tree_widget_item[file_entry] = item
        self.gcm_tree_widget_item_to_file_entry[item] = file_entry
      else:
        parent_item = self.gcm_file_entry_to_tree_widget_item[file_entry.parent]
        item = QTreeWidgetItem([file_entry.name, file_size_str])
        parent_item.addChild(item)
        self.gcm_file_entry_to_tree_widget_item[file_entry] = item
        self.gcm_tree_widget_item_to_file_entry[item] = file_entry
    
    # Add system files.
    # (Note that the "sys" folder has no corresponding directory file entry because it is not really a directory.)
    sys_item = QTreeWidgetItem(["sys", ""])
    self.ui.gcm_files_tree.addTopLevelItem(sys_item)
    for file_entry in self.gcm.system_files:
      file_size_str = self.stringify_number(file_entry.file_size)
      parent_item = sys_item
      item = QTreeWidgetItem([file_entry.name, file_size_str])
      parent_item.addChild(item)
      self.gcm_file_entry_to_tree_widget_item[file_entry] = item
      self.gcm_tree_widget_item_to_file_entry[item] = file_entry
    
    # Expand the "files" and "sys" root entries by default.
    self.ui.gcm_files_tree.topLevelItem(0).setExpanded(True)
    self.ui.gcm_files_tree.topLevelItem(1).setExpanded(True)
    
    self.ui.export_gcm.setDisabled(False)
    self.ui.import_folder_over_gcm.setDisabled(False)
    self.ui.export_gcm_folder.setDisabled(False)
    self.ui.dump_all_gcm_textures.setDisabled(False)
  
  def export_gcm_by_path(self, gcm_path):
    if os.path.realpath(self.gcm.iso_path) == os.path.realpath(gcm_path):
      raise Exception("Cannot export an ISO over the currently opened ISO. Please choose a different path.")
    
    # TODO: progress bar?
    self.gcm.export_disc_to_iso_with_changed_files(gcm_path)
    
    QMessageBox.information(self, "GCM saved", "Successfully saved GCM.")
  
  def import_folder_over_gcm_by_path(self, folder_path):
    num_files_overwritten = self.gcm.import_all_files_from_disk(folder_path)
    
    if num_files_overwritten == 0:
      QMessageBox.warning(self, "No matching files found", "The selected folder does not contain any files matching the name and directory structure of files in the currently loaded GCM. No files imported.\n\nMake sure you're selecting the correct folder - it should be the folder with 'files' and 'sys' inside of it, not the 'files' folder itself.")
      return
    
    QMessageBox.information(self, "Folder imported", "Successfully overwrote %d files in the GCM from \"%s\"." % (num_files_overwritten, folder_path))
  
  def export_gcm_folder_by_path(self, folder_path):
    self.gcm.export_disc_to_folder_with_changed_files(folder_path)
    
    QMessageBox.information(self, "GCM extracted", "Successfully extracted GCM contents to \"%s\"." % folder_path)
  
  def dump_all_gcm_textures_by_path(self, folder_path):
    self.asset_dumper = AssetDumper()
    
    dumper_generator = self.asset_dumper.dump_all_textures_in_gcm(self.gcm, folder_path)
    
    max_progress_val = len(self.asset_dumper.get_all_gcm_file_paths(self.gcm))
    self.progress_dialog = GCFTProgressDialog("Dumping textures", "Initializing...", max_progress_val)
    
    self.start_texture_dumper_thread(dumper_generator)
  
  
  def get_gcm_file_by_tree_item(self, item):
    if item not in self.gcm_tree_widget_item_to_file_entry:
      return None
    
    return self.gcm_tree_widget_item_to_file_entry[item]
  
  def get_gcm_tree_item_by_file(self, file):
    if file not in self.gcm_file_entry_to_tree_widget_item:
      return None
    
    return self.gcm_file_entry_to_tree_widget_item[file]
  
  def show_gcm_files_tree_context_menu(self, pos):
    if self.gcm is None:
      return
    
    item = self.ui.gcm_files_tree.itemAt(pos)
    if item is None:
      return
    
    file = self.get_gcm_file_by_tree_item(item)
    if file is None:
      return
    
    if file.is_dir:
      # TODO: Implement extracting/replacing folders
      menu = QMenu(self)
      menu.addAction(self.ui.actionAddGCMFile)
      self.ui.actionAddGCMFile.setData(file)
      menu.exec_(self.ui.gcm_files_tree.mapToGlobal(pos))
    else:
      menu = QMenu(self)
      
      basename, file_ext = os.path.splitext(file.name)
      if file_ext == ".bti" or file.file_path == "files/opening.bnr":
        menu.addAction(self.ui.actionOpenGCMImage)
        self.ui.actionOpenGCMImage.setData(file)
        
        menu.addAction(self.ui.actionReplaceGCMImage)
        self.ui.actionReplaceGCMImage.setData(file)
        if self.bti is None:
          self.ui.actionReplaceGCMImage.setDisabled(True)
        else:
          self.ui.actionReplaceGCMImage.setDisabled(False)
      elif file_ext == ".arc":
        menu.addAction(self.ui.actionOpenGCMRARC)
        self.ui.actionOpenGCMRARC.setData(file)
        
        menu.addAction(self.ui.actionReplaceGCMRARC)
        self.ui.actionReplaceGCMRARC.setData(file)
        if self.rarc is None:
          self.ui.actionReplaceGCMRARC.setDisabled(True)
        else:
          self.ui.actionReplaceGCMRARC.setDisabled(False)
      elif file_ext == ".jpc":
        menu.addAction(self.ui.actionOpenGCMJPC)
        self.ui.actionOpenGCMJPC.setData(file)
        
        menu.addAction(self.ui.actionReplaceGCMJPC)
        self.ui.actionReplaceGCMJPC.setData(file)
        if self.jpc is None:
          self.ui.actionReplaceGCMJPC.setDisabled(True)
        else:
          self.ui.actionReplaceGCMJPC.setDisabled(False)
      
      menu.addAction(self.ui.actionExtractGCMFile)
      self.ui.actionExtractGCMFile.setData(file)
      if file.file_path != "sys/fst.bin": # Regenerated automatically
        menu.addAction(self.ui.actionReplaceGCMFile)
        self.ui.actionReplaceGCMFile.setData(file)
      if not file.is_system_file:
        menu.addAction(self.ui.actionDeleteGCMFile)
        self.ui.actionDeleteGCMFile.setData(file)
      
      menu.exec_(self.ui.gcm_files_tree.mapToGlobal(pos))
  
  def extract_file_from_gcm_by_path(self, file_path):
    file = self.ui.actionExtractGCMFile.data()
    
    if file.file_path in self.gcm.changed_files:
      data = self.gcm.changed_files[file.file_path]
      data.seek(0)
      data = data.read()
    else:
      # TODO: for very large files, don't read all at once
      try:
        data = self.gcm.read_file_raw_data(file.file_path)
      except FileNotFoundError:
        QMessageBox.critical(self, "Could not read file", "Failed to read file. The ISO \"%s\" has been moved or deleted." % self.gcm.iso_path)
        return
    with open(file_path, "wb") as f:
      f.write(data)
  
  def replace_file_in_gcm_by_path(self, file_path):
    file = self.ui.actionReplaceGCMFile.data()
    
    with open(file_path, "rb") as f:
      data = BytesIO(f.read())
    
    if file.file_path in ["sys/boot.bin", "sys/bi2.bin"] and data_len(data) != file.file_size:
      QMessageBox.warning(self, "Cannot change this file's size", "The size of boot.bin and bi2.bin cannot be changed.")
      return
    
    self.gcm.changed_files[file.file_path] = data
    
    # Update changed file size
    file_size_str = self.stringify_number(data_len(data))
    item = self.gcm_file_entry_to_tree_widget_item[file]
    item.setText(self.gcm_col_name_to_index["File Size"], file_size_str)
  
  def delete_file_in_gcm(self):
    file_entry = self.ui.actionDeleteGCMFile.data()
    
    if not self.confirm_delete(file_entry.name):
      return
    
    dir_entry = file_entry.parent
    
    self.gcm.delete_file(file_entry)
    
    dir_item = self.gcm_file_entry_to_tree_widget_item[dir_entry]
    file_item = self.gcm_file_entry_to_tree_widget_item[file_entry]
    dir_item.removeChild(file_item)
    del self.gcm_file_entry_to_tree_widget_item[file_entry]
    del self.gcm_tree_widget_item_to_file_entry[file_item]
  
  def open_rarc_in_gcm(self):
    file_entry = self.ui.actionOpenGCMRARC.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = make_copy_data(data)
    
    rarc_name = os.path.splitext(file_entry.name)[0]
    
    self.import_rarc_by_data(data, rarc_name)
    
    self.set_tab_by_name("RARC Archives")
  
  def replace_rarc_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMRARC.data()
    
    self.rarc.save_changes()
    data = make_copy_data(self.rarc.data)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    # Update changed file size
    file_size_str = self.stringify_number(data_len(data))
    item = self.gcm_file_entry_to_tree_widget_item[file_entry]
    item.setText(self.gcm_col_name_to_index["File Size"], file_size_str)
  
  def open_image_in_gcm(self):
    file_entry = self.ui.actionOpenGCMImage.data()
    
    bti_name = os.path.splitext(file_entry.name)[0]
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = make_copy_data(data)
    
    if file_entry.file_path == "files/opening.bnr":
      image_data = read_bytes(data, 0x20, 0x1800)
      data = BytesIO()
      write_bytes(data, 0x20, image_data)
      
      write_u8(data, 0x00, ImageFormat.RGB5A3.value) # Image format
      write_u16(data, 0x02, 96) # Width
      write_u16(data, 0x04, 32) # Height
      write_u32(data, 0x1C, 0x20) # Image data offset
      
      bti_name = "opening_bnr"
    
    self.import_bti_by_data(data, bti_name)
    
    self.set_tab_by_name("BTI Images")
  
  def replace_image_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMImage.data()
    
    self.bti.save_changes()
    data = make_copy_data(self.bti.data)
    
    if file_entry.file_path == "files/opening.bnr":
      if self.bti.image_format != ImageFormat.RGB5A3 or self.bti.width != 96 or self.bti.height != 32 or data_len(self.bti.image_data) != 0x1800:
        QMessageBox.warning(self, "Invalid banner image", "Invalid banner image. Banner images must be exactly 96x32 pixels in size and use the RGB5A3 image format.")
        return
      
      orig_banner_data = self.gcm.get_changed_file_data(file_entry.file_path)
      image_data_bytes = read_bytes(self.bti.image_data, 0x00, 0x1800)
      data = make_copy_data(orig_banner_data)
      write_bytes(data, 0x20, image_data_bytes)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    # Update changed file size
    file_size_str = self.stringify_number(data_len(data))
    item = self.gcm_file_entry_to_tree_widget_item[file_entry]
    item.setText(self.gcm_col_name_to_index["File Size"], file_size_str)
  
  def open_jpc_in_gcm(self):
    file_entry = self.ui.actionOpenGCMJPC.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = make_copy_data(data)
    
    jpc_name = os.path.splitext(file_entry.name)[0]
    
    self.import_jpc_by_data(data, jpc_name)
    
    self.set_tab_by_name("JPC Particle Archives")
  
  def replace_jpc_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMJPC.data()
    
    self.jpc.save_changes()
    data = make_copy_data(self.jpc.data)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    # Update changed file size
    file_size_str = self.stringify_number(data_len(data))
    item = self.gcm_file_entry_to_tree_widget_item[file_entry]
    item.setText(self.gcm_col_name_to_index["File Size"], file_size_str)
  
  def add_file_to_gcm_by_path(self, file_path):
    dir_entry = self.ui.actionAddGCMFile.data()
    
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
      file_data = BytesIO(f.read())
    file_size = data_len(file_data)
    file_size_str = self.stringify_number(file_size)
    
    gcm_file_path = dir_entry.dir_path + "/" + file_name
    if gcm_file_path.lower() in self.gcm.files_by_path_lowercase:
      QMessageBox.warning(self, "File already exists", "Cannot add new file. The selected folder already contains a file named \"%s\".\n\nIf you wish to replace the existing file, right click on it in the files tree and select 'Replace File'." % file_name)
      return
    file_entry = self.gcm.add_new_file(gcm_file_path, file_data)
    
    dir_item = self.gcm_file_entry_to_tree_widget_item[dir_entry]
    file_item = QTreeWidgetItem([file_name, file_size_str])
    dir_item.addChild(file_item)
    self.gcm_file_entry_to_tree_widget_item[file_entry] = file_item
    self.gcm_tree_widget_item_to_file_entry[file_item] = file_entry
  
  
  
  def import_jpc_by_path(self, jpc_path):
    with open(jpc_path, "rb") as f:
      data = BytesIO(f.read())
    
    jpc_name = os.path.splitext(os.path.basename(jpc_path))[0]
    
    self.import_jpc_by_data(data, jpc_name)
  
  def import_jpc_by_data(self, data, jpc_name):
    self.jpc = JPC(data)
    
    self.jpc_name = jpc_name
    
    self.reload_jpc_particles_tree()
    
    self.ui.export_jpc.setDisabled(False)
    self.ui.add_particles_from_folder.setDisabled(False)
    self.ui.export_jpc_folder.setDisabled(False)
  
  def reload_jpc_particles_tree(self):
    self.ui.jpc_particles_tree.clear()
    
    self.jpc_particle_to_tree_widget_item = {}
    self.jpc_tree_widget_item_to_particle = {}
    self.jpc_texture_to_tree_widget_item = {}
    self.jpc_tree_widget_item_to_texture = {}
    
    for particle in self.jpc.particles:
      particle_id_str = self.stringify_number(particle.particle_id, min_hex_chars=4)
      
      particle_item = QTreeWidgetItem([particle_id_str, ""])
      self.ui.jpc_particles_tree.addTopLevelItem(particle_item)
      
      self.jpc_particle_to_tree_widget_item[particle] = particle_item
      self.jpc_tree_widget_item_to_particle[particle_item] = particle
      
      for texture_filename in particle.tdb1.texture_filenames:
        texture_item = QTreeWidgetItem(["", texture_filename])
        particle_item.addChild(texture_item)
        
        texture = self.jpc.textures_by_filename[texture_filename]
        self.jpc_texture_to_tree_widget_item[texture] = texture_item
        self.jpc_tree_widget_item_to_texture[texture_item] = texture
  
  def export_jpc_by_path(self, jpc_path):
    self.jpc.save_changes()
    
    with open(jpc_path, "wb") as f:
      self.jpc.data.seek(0)
      f.write(self.jpc.data.read())
    
    self.jpc_name = os.path.splitext(os.path.basename(jpc_path))[0]
    
    QMessageBox.information(self, "JPC saved", "Successfully saved JPC.")
  
  def add_particles_from_folder_by_path(self, folder_path):
    num_particles_added, num_particles_overwritten, num_textures_added, num_textures_overwritten = self.jpc.import_particles_from_disk(folder_path)
    
    if num_particles_added == num_particles_overwritten == num_textures_added == num_textures_overwritten == 0:
      QMessageBox.warning(self, "No matching files found", "The selected folder does not contain any files with the extension .jpa. No particles imported.")
      return
    
    self.reload_jpc_particles_tree()
    
    QMessageBox.information(self, "Folder imported", "Successfully imported particles from \"%s\".\n\nStats:\nParticles added: %d\nParticles overwritten: %d\nTextures added: %d\nTextures overwritten: %d" % (folder_path, num_particles_added, num_particles_overwritten, num_textures_added, num_textures_overwritten))
  
  def export_jpc_folder_by_path(self, folder_path):
    self.jpc.extract_all_particles_to_disk(output_directory=folder_path)
    
    QMessageBox.information(self, "JPC extracted", "Successfully extracted all JPA particles from the JPC to \"%s\"." % folder_path)
  
  
  def get_jpc_particle_by_tree_item(self, item):
    if item not in self.jpc_tree_widget_item_to_particle:
      return None
    
    return self.jpc_tree_widget_item_to_particle[item]
  
  def get_jpc_tree_item_by_particle(self, particle):
    if particle not in self.jpc_particle_to_tree_widget_item:
      return None
    
    return self.jpc_particle_to_tree_widget_item[particle]
  
  def get_jpc_texture_by_tree_item(self, item):
    if item not in self.jpc_tree_widget_item_to_texture:
      return None
    
    return self.jpc_tree_widget_item_to_texture[item]
  
  def get_jpc_tree_item_by_texture(self, texture):
    if texture not in self.jpc_texture_to_tree_widget_item:
      return None
    
    return self.jpc_texture_to_tree_widget_item[texture]
  
  def show_jpc_particles_tree_context_menu(self, pos):
    if self.jpc is None:
      return
    
    item = self.ui.jpc_particles_tree.itemAt(pos)
    if item is None:
      return
    
    texture = self.get_jpc_texture_by_tree_item(item)
    if texture:
      menu = QMenu(self)
      
      menu.addAction(self.ui.actionOpenJPCImage)
      self.ui.actionOpenJPCImage.setData(texture)
        
      menu.addAction(self.ui.actionReplaceJPCImage)
      self.ui.actionReplaceJPCImage.setData(texture)
      if self.bti is None:
        self.ui.actionReplaceJPCImage.setDisabled(True)
      else:
        self.ui.actionReplaceJPCImage.setDisabled(False)
      
      menu.exec_(self.ui.jpc_particles_tree.mapToGlobal(pos))
  
  def open_image_in_jpc(self):
    texture = self.ui.actionOpenJPCImage.data()
    
    # Need to make a fake standalone BTI texture data so we can load it without it being the TEX1 format.
    data = BytesIO()
    bti_header_bytes = read_bytes(texture.bti.data, texture.bti.header_offset, 0x20)
    write_bytes(data, 0x00, bti_header_bytes)
    
    bti_image_data = read_all_bytes(texture.bti.image_data)
    write_bytes(data, 0x20, bti_image_data)
    image_data_offset = 0x20
    write_u32(data, 0x1C, image_data_offset)
    
    if data_len(texture.bti.palette_data) == 0:
      palette_data_offset = 0
    else:
      bti_palette_data = read_all_bytes(texture.bti.palette_data)
      write_bytes(data, 0x20 + data_len(texture.bti.image_data), bti_palette_data)
      palette_data_offset = 0x20 + data_len(texture.bti.image_data)
    write_u32(data, 0x0C, palette_data_offset)
    
    self.import_bti_by_data(data, texture.filename)
    
    self.set_tab_by_name("BTI Images")
  
  def replace_image_in_jpc(self):
    texture = self.ui.actionOpenJPCImage.data()
    
    self.bti.save_changes()
    
    # Need to make a fake BTI header for it to read from.
    data = BytesIO()
    bti_header_bytes = read_bytes(self.bti.data, self.bti.header_offset, 0x20)
    write_bytes(data, 0x00, bti_header_bytes)
    
    texture.bti.read_header(data)
    
    texture.bti.image_data = make_copy_data(self.bti.image_data)
    texture.bti.palette_data = make_copy_data(self.bti.palette_data)
    
    texture.bti.save_header_changes()
  
  
  
  def import_bti_by_path(self, bti_path):
    with open(bti_path, "rb") as f:
      data = BytesIO(f.read())
    
    bti_name = os.path.splitext(os.path.basename(bti_path))[0]
    
    self.import_bti_by_data(data, bti_name)
  
  def import_bti_by_data(self, data, bti_name):
    self.bti = BTIFile(data)
    
    self.bti_name = bti_name
    
    
    for field_name, field_enum in BTI_ENUM_FIELDS:
      widget_name = "bti_" + field_name
      combobox_widget = getattr(self.ui, widget_name)
      combobox_widget.setDisabled(False)
      
      current_enum_value = getattr(self.bti, field_name)
      current_enum_name = current_enum_value.name
      
      index_of_value = None
      for i in range(combobox_widget.count()):
        text = combobox_widget.itemText(i)
        if text == current_enum_name:
          index_of_value = i
          break
      if index_of_value is None:
        print("Cannot find value %s in combobox %s" % (current_enum_name, widget_name))
        index_of_value = 0
      
      combobox_widget.blockSignals(True)
      combobox_widget.setCurrentIndex(index_of_value)
      combobox_widget.blockSignals(False)
    
    
    for field_name, byte_size in BTI_INTEGER_FIELDS:
      widget_name = "bti_" + field_name
      line_edit_widget = getattr(self.ui, widget_name)
      line_edit_widget.setDisabled(False)
      
      value = getattr(self.bti, field_name)
      value_str = self.stringify_number(value, min_hex_chars=2*byte_size)
      combobox_widget.blockSignals(True)
      line_edit_widget.setText(value_str)
      combobox_widget.blockSignals(False)
    
    # Disable the palette format dropdown when the image format doesn't use palettes.
    if self.bti.needs_palettes():
      self.ui.bti_palette_format.setDisabled(False)
    else:
      self.ui.bti_palette_format.setDisabled(True)
    
    
    self.reload_bti_image()
    self.original_bti_image = self.bti_image
    
    self.ui.export_bti.setDisabled(False)
    self.ui.import_bti_image.setDisabled(False)
    self.ui.export_bti_image.setDisabled(False)
  
  def reload_bti_image(self):
    self.bti_image = self.bti.render()
    
    image_bytes = self.bti_image.tobytes('raw', 'BGRA')
    qimage = QImage(image_bytes, self.bti_image.width, self.bti_image.height, QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(qimage)
    self.ui.bti_image_label.setPixmap(pixmap)
    
    file_size_str = self.stringify_number(data_len(self.bti.data))
    resolution_str = "%dx%d" % (self.bti_image.width, self.bti_image.height)
    self.ui.bti_file_size.setText(file_size_str)
    self.ui.bti_resolution.setText(resolution_str)
    
    self.ui.bti_image_label.setFixedWidth(self.bti_image.width)
    self.ui.bti_image_label.setFixedHeight(self.bti_image.height)
    self.ui.bti_image_label.show()
  
  def export_bti_by_path(self, bti_path):
    self.bti.save_changes()
    
    with open(bti_path, "wb") as f:
      self.bti.data.seek(0)
      f.write(self.bti.data.read())
    
    self.bti_name = os.path.splitext(os.path.basename(bti_path))[0]
    
    QMessageBox.information(self, "BTI saved", "Successfully saved BTI.")
  
  def import_bti_image_by_path(self, image_path):
    try:
      self.original_bti_image = Image.open(image_path)
      
      self.bti.replace_image(self.original_bti_image)
      
      self.bti.save_changes()
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message_title = "Failed to import image"
      error_message = "Failed to import image with error:\n%s\n\n%s" % (str(e), stack_trace)
      QMessageBox.critical(self, error_message_title, error_message)
      return
    
    self.reload_bti_image()
  
  def export_bti_image_by_path(self, image_path):
    self.bti_image.save(image_path)
    
    QMessageBox.information(self, "BTI saved", "Successfully saved image.")
  
  def bti_header_field_changed(self):
    for field_name, field_enum in BTI_ENUM_FIELDS:
      widget_name = "bti_" + field_name
      combobox_widget = getattr(self.ui, widget_name)
      
      current_enum_name = combobox_widget.itemText(combobox_widget.currentIndex())
      current_enum_value = field_enum[current_enum_name]
      
      setattr(self.bti, field_name, current_enum_value)
    
    
    for field_name, byte_size in BTI_INTEGER_FIELDS:
      widget_name = "bti_" + field_name
      line_edit_widget = getattr(self.ui, widget_name)
      new_str_value = line_edit_widget.text()
      old_value = getattr(self.bti, field_name)
      
      line_edit_widget.blockSignals(True)
      
      if self.display_hexadecimal_numbers:
        hexadecimal_match = re.search(r"^\s*(?:0x)?([0-9a-f]+)\s*$", new_str_value, re.IGNORECASE)
        if hexadecimal_match:
          new_value = int(hexadecimal_match.group(1), 16)
        else:
          QMessageBox.warning(self, "Invalid value", "\"%s\" is not a valid hexadecimal number." % new_str_value)
          new_value = old_value
      else:
        decimal_match = re.search(r"^\s*(\d+)\s*$", new_str_value, re.IGNORECASE)
        if decimal_match:
          new_value = int(decimal_match.group(1))
        else:
          QMessageBox.warning(self, "Invalid value", "\"%s\" is not a valid decimal number." % new_str_value)
          new_value = old_value
      
      if new_value < 0:
        QMessageBox.warning(self, "Invalid value", "Value cannot be negative.")
        new_value = old_value
      if new_value >= 2**(byte_size*8):
        QMessageBox.warning(
          self, "Invalid value",
          "Value is too large to fit in field %s (maximum value: 0x%X)" % (field_name, (2**(byte_size*8))-1)
        )
        new_value = old_value
      
      setattr(self.bti, field_name, new_value)
      
      new_str_value = self.stringify_number(new_value, min_hex_chars=2*byte_size)
      line_edit_widget.setText(new_str_value)
      line_edit_widget.blockSignals(False)
    
    # Disable the palette format dropdown when the image format doesn't use palettes.
    if self.bti.needs_palettes():
      self.ui.bti_palette_format.setDisabled(False)
    else:
      self.ui.bti_palette_format.setDisabled(True)
    
    try:
      self.bti.replace_image(self.original_bti_image)
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message_title = "Failed to import image"
      error_message = "Failed to import image with error:\n%s\n\n%s" % (str(e), stack_trace)
      QMessageBox.critical(self, error_message_title, error_message)
      return
    
    self.bti.save_changes()
    
    self.reload_bti_image()
  
  
  
  def import_j3d_by_path(self, j3d_path):
    with open(j3d_path, "rb") as f:
      data = BytesIO(f.read())
    
    j3d_name = os.path.splitext(os.path.basename(j3d_path))[0]
    
    self.import_j3d_by_data(data, j3d_name)
  
  def import_j3d_by_data(self, data, j3d_name):
    self.j3d = J3DFile(data)
    
    self.j3d_name = j3d_name
    
    self.reload_j3d_chunks_tree()
    
    self.ui.export_j3d.setDisabled(False)
  
  def reload_j3d_chunks_tree(self):
    self.ui.j3d_chunks_tree.clear()
    
    self.j3d_chunk_to_tree_widget_item = {}
    self.j3d_tree_widget_item_to_chunk = {}
    self.j3d_texture_to_tree_widget_item = {}
    self.j3d_tree_widget_item_to_texture = {}
    
    for chunk in self.j3d.chunks:
      chunk_size_str = self.stringify_number(chunk.size, min_hex_chars=5)
      
      chunk_item = QTreeWidgetItem([chunk.magic, "", chunk_size_str])
      self.ui.j3d_chunks_tree.addTopLevelItem(chunk_item)
      
      self.j3d_chunk_to_tree_widget_item[chunk] = chunk_item
      self.j3d_tree_widget_item_to_chunk[chunk_item] = chunk
      
      if chunk.magic == "TEX1":
        # Expand TEX1 chunks by default.
        chunk_item.setExpanded(True)
        
        seen_image_data_offsets = []
        seen_palette_data_offsets = []
        
        for i, texture in enumerate(chunk.textures):
          texture_name = chunk.texture_names[i]
          
          # We don't display sizes for texture headers that use image/palette datas duplicated from an earlier tex header.
          # We also don't display the 0x20 byte size of any of the headers.
          texture_total_size = 0
          if texture.image_data_offset+texture.header_offset not in seen_image_data_offsets:
            texture_total_size += data_len(texture.image_data)
            seen_image_data_offsets.append(texture.image_data_offset+texture.header_offset)
          if texture.palette_data_offset+texture.header_offset not in seen_palette_data_offsets:
            texture_total_size += data_len(texture.palette_data)
            seen_palette_data_offsets.append(texture.palette_data_offset+texture.header_offset)
          
          if texture_total_size == 0:
            texture_size_str = ""
          else:
            texture_size_str = self.stringify_number(texture_total_size, min_hex_chars=5)
          
          texture_item = QTreeWidgetItem(["", texture_name, texture_size_str])
          chunk_item.addChild(texture_item)
          
          self.j3d_texture_to_tree_widget_item[texture] = texture_item
          self.j3d_tree_widget_item_to_texture[texture_item] = texture
  
  def export_j3d_by_path(self, j3d_path):
    self.j3d.save_changes()
    
    with open(j3d_path, "wb") as f:
      self.j3d.data.seek(0)
      f.write(self.j3d.data.read())
    
    self.j3d_name = os.path.splitext(os.path.basename(j3d_path))[0]
    
    QMessageBox.information(self, "J3D file saved", "Successfully saved J3D file.")
  
  def get_file_filter_by_current_j3d_file_type(self):
    if self.j3d.file_type == "bdl4":
      return "Binary Display List Models (*.bdl)"
    elif self.j3d.file_type == "bmd3":
      return "Binary Models (*.bmd)"
    elif self.j3d.file_type == "bmt3":
      return "Binary Material Tables (*.bmt)"
    elif self.j3d.file_type == "btk1":
      return "Texture SRT Animations (*.btk)"
    elif self.j3d.file_type == "bck1":
      return "Joint Animations (*.bck)"
    elif self.j3d.file_type == "brk1":
      return "Texture Register Animations (*.brk)"
    elif self.j3d.file_type == "btp1":
      return "Texture Swap Animations (*.btp)"
    else:
      return None
  
  def get_j3d_chunk_by_tree_item(self, item):
    if item not in self.j3d_tree_widget_item_to_chunk:
      return None
    
    return self.j3d_tree_widget_item_to_chunk[item]
  
  def get_j3d_tree_item_by_chunk(self, chunk):
    if chunk not in self.j3d_chunk_to_tree_widget_item:
      return None
    
    return self.j3d_chunk_to_tree_widget_item[chunk]
  
  def get_j3d_texture_by_tree_item(self, item):
    if item not in self.j3d_tree_widget_item_to_texture:
      return None
    
    return self.j3d_tree_widget_item_to_texture[item]
  
  def get_jpc_tree_item_by_texture(self, texture):
    if texture not in self.j3d_texture_to_tree_widget_item:
      return None
    
    return self.j3d_texture_to_tree_widget_item[texture]
  
  def show_j3d_chunks_tree_context_menu(self, pos):
    if self.j3d is None:
      return
    
    item = self.ui.j3d_chunks_tree.itemAt(pos)
    if item is None:
      return
    
    texture = self.get_j3d_texture_by_tree_item(item)
    if texture:
      menu = QMenu(self)
      
      menu.addAction(self.ui.actionOpenJ3DImage)
      self.ui.actionOpenJ3DImage.setData(texture)
      
      menu.addAction(self.ui.actionReplaceJ3DImage)
      self.ui.actionReplaceJ3DImage.setData(texture)
      if self.bti is None:
        self.ui.actionReplaceJ3DImage.setDisabled(True)
      else:
        self.ui.actionReplaceJ3DImage.setDisabled(False)
      
      menu.exec_(self.ui.j3d_chunks_tree.mapToGlobal(pos))
  
  def open_image_in_j3d(self):
    texture = self.ui.actionOpenJ3DImage.data()
    
    # Need to make a fake standalone BTI texture data so we can load it without it being the TEX1 format.
    data = BytesIO()
    bti_header_bytes = read_bytes(texture.data, texture.header_offset, 0x20)
    write_bytes(data, 0x00, bti_header_bytes)
    
    bti_image_data = read_all_bytes(texture.image_data)
    write_bytes(data, 0x20, bti_image_data)
    image_data_offset = 0x20
    write_u32(data, 0x1C, image_data_offset)
    
    if data_len(texture.palette_data) == 0:
      palette_data_offset = 0
    else:
      bti_palette_data = read_all_bytes(texture.palette_data)
      write_bytes(data, 0x20 + data_len(texture.image_data), bti_palette_data)
      palette_data_offset = 0x20 + data_len(texture.image_data)
    write_u32(data, 0x0C, palette_data_offset)
    
    texture_index = self.j3d.tex1.textures.index(texture)
    bti_name = self.j3d.tex1.texture_names[texture_index]
    
    self.import_bti_by_data(data, bti_name)
    
    self.set_tab_by_name("BTI Images")
  
  def replace_image_in_j3d(self):
    texture = self.ui.actionOpenJ3DImage.data()
    
    self.bti.save_changes()
    
    # Need to make a fake BTI header for it to read from.
    data = BytesIO()
    bti_header_bytes = read_bytes(self.bti.data, self.bti.header_offset, 0x20)
    write_bytes(data, 0x00, bti_header_bytes)
    
    texture.read_header(data)
    
    texture.image_data = make_copy_data(self.bti.image_data)
    texture.palette_data = make_copy_data(self.bti.palette_data)
    
    texture.save_header_changes()
    
    # Update texture size displayed in the UI.
    texture_total_size = 0
    texture_total_size += data_len(texture.image_data)
    texture_total_size += data_len(texture.palette_data)
    texture_size_str = self.stringify_number(texture_total_size, min_hex_chars=5)
    
    item = self.get_jpc_tree_item_by_texture(texture)
    item.setText(self.j3d_col_name_to_index["Size"], texture_size_str)
  
  
  
  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()
    elif event.matches(QKeySequence.Copy):
      curr_tab_text = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
      # When copying the filename in a RARC/GCM, override the default behavior so it instead copies the whole path.
      if curr_tab_text == "RARC Archives" and self.ui.rarc_files_tree.currentColumn() == self.rarc_col_name_to_index["File Name"]:
        item = self.ui.rarc_files_tree.currentItem()
        file_path = "%s/%s" % (item.parent().text(self.rarc_col_name_to_index["File Name"]), item.text(self.rarc_col_name_to_index["File Name"]))
        QApplication.instance().clipboard().setText(file_path)
      elif curr_tab_text == "GCM ISOs" and self.ui.gcm_files_tree.currentColumn() == self.gcm_col_name_to_index["File Name"]:
        item = self.ui.gcm_files_tree.currentItem()
        if item not in self.gcm_tree_widget_item_to_file_entry:
          # The sys folder is not real.
          return
        file_entry = self.gcm_tree_widget_item_to_file_entry[item]
        file_path = file_entry.file_path
        QApplication.instance().clipboard().setText(file_path)
  
  def closeEvent(self, event):
    self.save_settings()
  
  def get_drop_action_for_file_path(self, file_path):
    file_ext = os.path.splitext(file_path)[1]
    
    if file_ext in GCM_FILE_EXTS:
      return (self.import_gcm_by_path, "GCM ISOs")
    elif file_ext in RARC_FILE_EXTS:
      return (self.import_rarc_by_path, "RARC Archives")
    elif file_ext in BTI_FILE_EXTS:
      return (self.import_bti_by_path, "BTI Images")
    elif file_ext in [".png"] and self.bti is not None:
      return (self.import_bti_image_by_path, "BTI Images")
    elif file_ext in J3D_FILE_EXTS:
      return (self.import_j3d_by_path, "J3D Files")
    elif file_ext in JPC_FILE_EXTS:
      return (self.import_jpc_by_path, "JPC Particle Archives")
  
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
      while True:
        # Need to use a while loop to go through the generator instead of a for loop, as a for loop would silently exit if a StopIteration error ever happened for any reason.
        next_progress_text, progress_value = next(self.action_generator)
        if progress_value == -1:
          break
        self.update_progress.emit(next_progress_text, progress_value)
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message = "Error:\n" + str(e) + "\n\n" + stack_trace
      self.action_failed.emit(error_message)
      return
    
    self.action_complete.emit()
