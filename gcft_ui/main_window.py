
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import os
from io import BytesIO
from collections import OrderedDict
import traceback
import re

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
from wwlib.bti import BTIFile
from wwlib.j3d import J3DFile
from fs_helpers import *

class GCFTWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    self.gcm = None
    self.rarc = None
    
    self.ui.rarc_files_tree.setColumnWidth(0, 300)
    self.ui.gcm_files_tree.setColumnWidth(0, 300)
    self.ui.jpc_particles_tree.setColumnWidth(0, 100)
    
    self.ui.export_rarc.setDisabled(True)
    self.ui.import_folder_over_rarc.setDisabled(True)
    self.ui.export_rarc_folder.setDisabled(True)
    self.ui.export_gcm.setDisabled(True)
    self.ui.import_folder_over_gcm.setDisabled(True)
    self.ui.export_gcm_folder.setDisabled(True)
    self.ui.export_jpc.setDisabled(True)
    self.ui.add_particles_from_folder.setDisabled(True)
    self.ui.export_jpc_folder.setDisabled(True)
    self.ui.export_bti.setDisabled(True)
    self.ui.import_bti_image.setDisabled(True)
    self.ui.export_bti_image.setDisabled(True)
    self.ui.export_j3d.setDisabled(True)
    
    checkerboard_path = os.path.join(ASSETS_PATH, "checkerboard.png")
    checkerboard_path = checkerboard_path.replace("\\", "/")
    self.ui.bti_image_label.setStyleSheet("border-image: url(%s) repeat;" % checkerboard_path)
    self.ui.bti_image_label.hide()
    
    self.ui.tabWidget.currentChanged.connect(self.save_last_used_tab)
    
    self.ui.import_rarc.clicked.connect(self.import_rarc)
    self.ui.export_rarc.clicked.connect(self.export_rarc)
    self.ui.import_folder_over_rarc.clicked.connect(self.import_folder_over_rarc)
    self.ui.export_rarc_folder.clicked.connect(self.export_rarc_folder)
    
    self.ui.rarc_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.rarc_files_tree.customContextMenuRequested.connect(self.show_rarc_files_tree_context_menu)
    self.ui.rarc_files_tree.itemDoubleClicked.connect(self.edit_rarc_files_tree_item_text)
    self.ui.rarc_files_tree.itemChanged.connect(self.rarc_file_tree_item_text_changed)
    self.ui.actionExtractRARCFile.triggered.connect(self.extract_file_from_rarc)
    self.ui.actionReplaceRARCFile.triggered.connect(self.replace_file_in_rarc)
    self.ui.actionDeleteRARCFile.triggered.connect(self.delete_file_in_rarc)
    self.ui.actionAddRARCFile.triggered.connect(self.add_file_to_rarc)
    self.ui.actionOpenRARCImage.triggered.connect(self.open_image_in_rarc)
    
    self.ui.decompress_yaz0.clicked.connect(self.decompress_yaz0)
    self.ui.compress_yaz0.clicked.connect(self.compress_yaz0)
    
    self.ui.import_gcm.clicked.connect(self.import_gcm)
    self.ui.export_gcm.clicked.connect(self.export_gcm)
    self.ui.import_folder_over_gcm.clicked.connect(self.import_folder_over_gcm)
    self.ui.export_gcm_folder.clicked.connect(self.export_gcm_folder)
    
    self.ui.gcm_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.gcm_files_tree.customContextMenuRequested.connect(self.show_gcm_files_tree_context_menu)
    self.ui.actionExtractGCMFile.triggered.connect(self.extract_file_from_gcm)
    self.ui.actionReplaceGCMFile.triggered.connect(self.replace_file_in_gcm)
    self.ui.actionDeleteGCMFile.triggered.connect(self.delete_file_in_gcm)
    self.ui.actionAddGCMFile.triggered.connect(self.add_file_to_gcm)
    self.ui.actionOpenGCMImage.triggered.connect(self.open_image_in_gcm)
    
    self.ui.import_jpc.clicked.connect(self.import_jpc)
    self.ui.export_jpc.clicked.connect(self.export_jpc)
    self.ui.add_particles_from_folder.clicked.connect(self.add_particles_from_folder)
    self.ui.export_jpc_folder.clicked.connect(self.export_jpc_folder)
    
    self.ui.jpc_particles_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.jpc_particles_tree.customContextMenuRequested.connect(self.show_jpc_particles_tree_context_menu)
    self.ui.actionOpenJPCImage.triggered.connect(self.open_image_in_jpc)
    
    self.ui.import_bti.clicked.connect(self.import_bti)
    self.ui.export_bti.clicked.connect(self.export_bti)
    self.ui.import_bti_image.clicked.connect(self.import_bti_image)
    self.ui.export_bti_image.clicked.connect(self.export_bti_image)
    
    self.ui.import_j3d.clicked.connect(self.import_j3d)
    self.ui.export_j3d.clicked.connect(self.export_j3d)
    
    self.ui.j3d_chunks_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.j3d_chunks_tree.customContextMenuRequested.connect(self.show_j3d_chunks_tree_context_menu)
    self.ui.actionOpenJ3DImage.triggered.connect(self.open_image_in_j3d)
    
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
  
  def confirm_delete_file(self, file_name):
    response = QMessageBox.question(self, 
      "Confirm delete",
      "Are you sure you want to delete \"%s\"?" % file_name,
      QMessageBox.Cancel | QMessageBox.Yes,
      QMessageBox.Cancel
    )
    if response == QMessageBox.Yes:
      return True
    else:
      return False
  
  def stringify_number(self, num, min_hex_chars=1):
    if True: # TODO setting
      format_string = "0x%%0%dX" % min_hex_chars
      return format_string % num
    else:
      return "%d" % num
  
  
  
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
  
  def export_rarc(self):
    self.generic_do_gui_file_operation(
      op_callback=self.export_rarc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="RARC", file_filter="RARC files (*.arc)"
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
    self.generic_do_gui_file_operation(
      op_callback=self.export_bti_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="BTI", file_filter="BTI files (*.bti)"
    )
  
  def import_bti_image(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_bti_image_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="image", file_filter="PNG Files (*.png)"
    )
  
  def export_bti_image(self):
    self.generic_do_gui_file_operation(
      op_callback=self.export_bti_image_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="image", file_filter="PNG Files (*.png)"
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
    
    self.generic_do_gui_file_operation(
      op_callback=self.export_j3d_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="J3D file", file_filter=";;".join(filters)
    )
  
  def import_jpc(self):
    self.generic_do_gui_file_operation(
      op_callback=self.import_jpc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="JPC", file_filter="JPC Files (*.jpc)"
    )
  
  def export_jpc(self):
    self.generic_do_gui_file_operation(
      op_callback=self.export_jpc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="JPC", file_filter="JPC Files (*.jpc)"
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
    self.rarc = RARC(data)
    
    self.ui.rarc_files_tree.clear()
    
    self.rarc_node_to_tree_widget_item = {}
    self.rarc_tree_widget_item_to_node = {}
    self.rarc_file_entry_to_tree_widget_item = {}
    self.rarc_tree_widget_item_to_file_entry = {}
    
    root_node = self.rarc.nodes[0]
    root_item = QTreeWidgetItem([root_node.name, "", "", ""])
    self.ui.rarc_files_tree.addTopLevelItem(root_item)
    self.rarc_node_to_tree_widget_item[root_node] = root_item
    self.rarc_tree_widget_item_to_node[root_item] = root_node
    
    for node in self.rarc.nodes[1:]:
      item = QTreeWidgetItem([node.name, "", "", ""])
      root_item.addChild(item)
      
      self.rarc_node_to_tree_widget_item[node] = item
      self.rarc_tree_widget_item_to_node[item] = node
      
      dir_file_entry = next(fe for fe in self.rarc.file_entries if fe.is_dir and fe.name == node.name)
      assert dir_file_entry.is_dir
      
      self.rarc_file_entry_to_tree_widget_item[dir_file_entry] = item
      self.rarc_tree_widget_item_to_file_entry[item] = dir_file_entry
    
    for file_entry in self.rarc.file_entries:
      if file_entry.is_dir:
        if file_entry.name not in [".", ".."]:
          assert file_entry in self.rarc_file_entry_to_tree_widget_item
        continue
      
      file_size_str = self.stringify_number(file_entry.data_size)
      file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
      file_index = self.rarc.file_entries.index(file_entry)
      file_index_str = self.stringify_number(file_index, min_hex_chars=4)
      
      parent_item = self.rarc_node_to_tree_widget_item[file_entry.parent_node]
      item = QTreeWidgetItem([file_entry.name, file_index_str, file_id_str, file_size_str])
      item.setFlags(item.flags() | Qt.ItemIsEditable)
      parent_item.addChild(item)
      self.rarc_file_entry_to_tree_widget_item[file_entry] = item
      self.rarc_tree_widget_item_to_file_entry[item] = file_entry
    
    # Expand the root node by default.
    self.ui.rarc_files_tree.topLevelItem(0).setExpanded(True)
    
    self.ui.export_rarc.setDisabled(False)
    self.ui.import_folder_over_rarc.setDisabled(False)
    self.ui.export_rarc_folder.setDisabled(False)
  
  def export_rarc_by_path(self, rarc_path):
    self.rarc.save_changes()
    
    with open(rarc_path, "wb") as f:
      self.rarc.data.seek(0)
      f.write(self.rarc.data.read())
    
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
      menu.exec_(self.ui.rarc_files_tree.mapToGlobal(pos))
    else:
      file = self.get_rarc_file_by_tree_item(item)
      if file is None:
        return
      
      if file.is_dir:
        print(file.name)
        # TODO: when is there a dir with no node?
        pass
      else:
        menu = QMenu(self)
        menu.addAction(self.ui.actionExtractRARCFile)
        self.ui.actionExtractRARCFile.setData(file)
        menu.addAction(self.ui.actionReplaceRARCFile)
        self.ui.actionReplaceRARCFile.setData(file)
        menu.addAction(self.ui.actionDeleteRARCFile)
        self.ui.actionDeleteRARCFile.setData(file)
        if file.name.endswith(".bti"):
          menu.addAction(self.ui.actionOpenRARCImage)
          self.ui.actionOpenRARCImage.setData(file)
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
    item.setText(2, file_size_str)
  
  def delete_file_in_rarc(self):
    file_entry = self.ui.actionDeleteRARCFile.data()
    
    if not self.confirm_delete_file(file_entry.name):
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
    
    data = make_copy_data(file_entry.data)
    self.import_bti_by_data(data)
    
    self.set_tab_by_name("BTI Images")
  
  def add_file_to_rarc_by_path(self, file_path):
    node = self.ui.actionAddRARCFile.data()
    
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
      file_data = BytesIO(f.read())
    file_size = data_len(file_data)
    file_size_str = self.stringify_number(file_size)
    
    existing_file_names_in_node = [fe.name for fe in node.files]
    if file_name in existing_file_names_in_node:
      QMessageBox.warning(self, "File already exists", "Cannot add new file. The selected folder already contains a file named \"%s\".\n\nIf you wish to replace the existing file, right click on it in the files tree and select 'Replace File'." % file_name)
      return
    
    file_entry = self.rarc.add_new_file(file_name, file_data, node)
    file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
    file_index = self.rarc.file_entries.index(file_entry)
    file_index_str = self.stringify_number(file_index, min_hex_chars=4)
    
    dir_item = self.get_rarc_tree_item_by_node(node)
    file_item = QTreeWidgetItem([file_entry.name, file_index_str, file_id_str, file_size_str])
    file_item.setFlags(file_item.flags() | Qt.ItemIsEditable)
    dir_item.addChild(file_item)
    self.rarc_file_entry_to_tree_widget_item[file_entry] = file_item
    self.rarc_tree_widget_item_to_file_entry[file_item] = file_entry
  
  
  def edit_rarc_files_tree_item_text(self, item, column):
    if (item.flags() & Qt.ItemIsEditable) != 0 and column == 2: # Allow editing the file IDs column only.
      self.ui.rarc_files_tree.editItem(item, column)
  
  def rarc_file_tree_item_text_changed(self, item, column):
    if column == 2:
      self.change_rarc_file_id(item)
  
  def change_rarc_file_id(self, item):
    file_entry = self.get_rarc_file_by_tree_item(item)
    new_file_id_str = item.text(2)
    
    if True: # TODO hex/decimal setting
      hexadecimal_match = re.search(r"^\s*(?:0x)?([0-9a-f]+)\s*$", new_file_id_str, re.IGNORECASE)
      if hexadecimal_match:
        new_file_id = int(hexadecimal_match.group(1), 16)
      else:
        QMessageBox.warning(self, "Invalid file ID", "\"%s\" is not a valid hexadecimal number." % new_file_id_str)
        file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
        item.setText(2, file_id_str)
        return
    else:
      decimal_match = re.search(r"^\s*(\d+)\s*$", new_file_id_str, re.IGNORECASE)
      if decimal_match:
        new_file_id = int(decimal_match.group(1))
      else:
        QMessageBox.warning(self, "Invalid file ID", "\"%s\" is not a valid decimal number." % new_file_id_str)
        file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
        item.setText(2, file_id_str)
        return
    
    if new_file_id >= 0xFFFF:
      QMessageBox.warning(self, "Invalid file ID", "\"%s\" is too large to be a file ID. It must be in the range 0x0000-0xFFFE." % new_file_id_str)
      file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(2, file_id_str)
      return
    
    other_file_entry = next((fe for fe in self.rarc.file_entries if fe.id == new_file_id), None)
    
    if other_file_entry == file_entry:
      # File ID not changed
      file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(2, file_id_str)
      return
    
    if other_file_entry is not None:
      QMessageBox.warning(self, "Duplicate file ID", "The file ID you entered is already used by the file \"%s\"." % other_file_entry.name)
      file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(2, file_id_str)
      return
    
    file_entry.id = new_file_id
    
    file_id_str = self.stringify_number(file_entry.id, min_hex_chars=4)
    item.setText(2, file_id_str)
  
  
  
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
      menu.addAction(self.ui.actionExtractGCMFile)
      self.ui.actionExtractGCMFile.setData(file)
      if file.file_path != "sys/fst.bin": # Regenerated automatically
        menu.addAction(self.ui.actionReplaceGCMFile)
        self.ui.actionReplaceGCMFile.setData(file)
      if not file.is_system_file:
        menu.addAction(self.ui.actionDeleteGCMFile)
        self.ui.actionDeleteGCMFile.setData(file)
      if file.name.endswith(".bti"):
        menu.addAction(self.ui.actionOpenGCMImage)
        self.ui.actionOpenGCMImage.setData(file)
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
    item.setText(1, file_size_str)
  
  def delete_file_in_gcm(self):
    file_entry = self.ui.actionDeleteGCMFile.data()
    
    if not self.confirm_delete_file(file_entry.name):
      return
    
    dir_entry = file_entry.parent
    
    self.gcm.delete_file(file_entry)
    
    dir_item = self.gcm_file_entry_to_tree_widget_item[dir_entry]
    file_item = self.gcm_file_entry_to_tree_widget_item[file_entry]
    dir_item.removeChild(file_item)
    del self.gcm_file_entry_to_tree_widget_item[file_entry]
    del self.gcm_tree_widget_item_to_file_entry[file_item]
  
  def open_image_in_gcm(self):
    file_entry = self.ui.actionOpenGCMImage.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = make_copy_data(data)
    self.import_bti_by_data(data)
    
    self.set_tab_by_name("BTI Images")
  
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
    self.jpc = JPC(data)
    
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
      menu.exec_(self.ui.jpc_particles_tree.mapToGlobal(pos))
  
  def open_image_in_jpc(self):
    texture = self.ui.actionOpenJPCImage.data()
    
    data = make_copy_data(texture.bti.data)
    self.import_bti_by_data(data)
    
    self.set_tab_by_name("BTI Images")
  
  
  
  def import_bti_by_path(self, bti_path):
    with open(bti_path, "rb") as f:
      data = BytesIO(f.read())
    
    self.bti = BTIFile(data)
    
    self.reload_bti_image()
    
    self.ui.export_bti.setDisabled(False)
    self.ui.import_bti_image.setDisabled(False)
    self.ui.export_bti_image.setDisabled(False)
  
  def import_bti_by_data(self, data):
    self.bti = BTIFile(data)
    
    self.reload_bti_image()
    
    self.ui.export_bti.setDisabled(False)
    self.ui.import_bti_image.setDisabled(False)
    self.ui.export_bti_image.setDisabled(False)
  
  def reload_bti_image(self):
    self.bti_image = self.bti.render()
    
    image_bytes = self.bti_image.tobytes('raw', 'BGRA')
    qimage = QImage(image_bytes, self.bti_image.width, self.bti_image.height, QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(qimage)
    self.ui.bti_image_label.setPixmap(pixmap)
    
    self.ui.bti_image_label.setFixedWidth(self.bti_image.width)
    self.ui.bti_image_label.setFixedHeight(self.bti_image.height)
    self.ui.bti_image_label.show()
  
  def export_bti_by_path(self, bti_path):
    self.bti.save_changes()
    
    with open(bti_path, "wb") as f:
      self.bti.data.seek(0)
      f.write(self.bti.data.read())
    
    QMessageBox.information(self, "BTI saved", "Successfully saved BTI.")
  
  def import_bti_image_by_path(self, image_path):
    self.bti.replace_image_from_path(image_path)
    
    self.bti.save_changes()
    
    self.reload_bti_image()
  
  def export_bti_image_by_path(self, image_path):
    self.bti_image.save(image_path)
    
    QMessageBox.information(self, "BTI saved", "Successfully saved image.")
  
  
  
  def import_j3d_by_path(self, j3d_path):
    with open(j3d_path, "rb") as f:
      data = BytesIO(f.read())
    
    self.j3d = J3DFile(data)
    
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
    
    self.import_bti_by_data(data)
    
    self.set_tab_by_name("BTI Images")
  
  
  
  def keyPressEvent(self, event):
    if event.key() == Qt.Key_Escape:
      self.close()
    elif event.matches(QKeySequence.Copy):
      curr_tab_text = self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
      # When copying the filename in a RARC/GCM, override the default behavior so it instead copies the whole path.
      if curr_tab_text == "RARC Archives" and self.ui.rarc_files_tree.currentColumn() == 0:
        item = self.ui.rarc_files_tree.currentItem()
        file_path = "%s/%s" % (item.parent().text(0), item.text(0))
        QApplication.instance().clipboard().setText(file_path)
      elif curr_tab_text == "GCM ISOs" and self.ui.gcm_files_tree.currentColumn() == 0:
        item = self.ui.gcm_files_tree.currentItem()
        file_entry = self.gcm_tree_widget_item_to_file_entry[item]
        file_path = file_entry.file_path
        QApplication.instance().clipboard().setText(file_path)
  
  def closeEvent(self, event):
    self.save_settings()
