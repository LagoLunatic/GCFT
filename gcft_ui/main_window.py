
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

import os
from io import BytesIO
from collections import OrderedDict

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

from wwlib.rarc import RARC
from wwlib.yaz0 import Yaz0
from wwlib.gcm import GCM
from fs_helpers import *

class GCFTWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    self.ui.rarc_files_tree.setColumnWidth(0, 300)
    self.ui.gcm_files_tree.setColumnWidth(0, 300)
    self.ui.export_rarc.setDisabled(True)
    #self.ui.import_rarc_folder.setDisabled(True)
    self.ui.export_rarc_folder.setDisabled(True)
    self.ui.export_gcm.setDisabled(True)
    #self.ui.import_gcm_folder.setDisabled(True)
    self.ui.export_gcm_folder.setDisabled(True)
    
    self.ui.tabWidget.currentChanged.connect(self.save_last_used_tab)
    
    self.ui.import_rarc.clicked.connect(self.import_rarc)
    self.ui.export_rarc.clicked.connect(self.export_rarc)
    self.ui.export_rarc_folder.clicked.connect(self.export_rarc_folder)
    
    self.ui.rarc_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.rarc_files_tree.customContextMenuRequested.connect(self.show_rarc_files_tree_context_menu)
    self.ui.actionExtractRARCFile.triggered.connect(self.extract_file_from_rarc)
    self.ui.actionReplaceRARCFile.triggered.connect(self.replace_file_in_rarc)
    
    self.ui.decompress_yaz0.clicked.connect(self.decompress_yaz0)
    self.ui.compress_yaz0.clicked.connect(self.compress_yaz0)
    
    self.ui.import_gcm.clicked.connect(self.import_gcm)
    self.ui.export_gcm.clicked.connect(self.export_gcm)
    self.ui.export_gcm_folder.clicked.connect(self.export_gcm_folder)
    
    self.ui.gcm_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.gcm_files_tree.customContextMenuRequested.connect(self.show_gcm_files_tree_context_menu)
    self.ui.actionExtractGCMFile.triggered.connect(self.extract_file_from_gcm)
    self.ui.actionReplaceGCMFile.triggered.connect(self.replace_file_in_gcm)
    
    self.load_settings()
    
    if "last_used_tab_index" in self.settings:
      self.ui.tabWidget.setCurrentIndex(self.settings["last_used_tab_index"])
    
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
    self.settings["last_used_tab_index"] = tab_index
  
  
  def import_rarc(self):
    default_dir = None
    if "last_used_folder_for_rarcs" in self.settings:
      default_dir = self.settings["last_used_folder_for_rarcs"]
    
    rarc_path, selected_filter = QFileDialog.getOpenFileName(self, "Open RARC", default_dir, "RARC files (*.arc)")
    if not rarc_path:
      return
    
    self.open_rarc_by_path(rarc_path)
  
  def export_rarc(self):
    default_dir = None
    if "last_used_folder_for_rarcs" in self.settings:
      default_dir = self.settings["last_used_folder_for_rarcs"]
    
    rarc_path, selected_filter = QFileDialog.getSaveFileName(self, "Save RARC", default_dir, "RARC files (*.arc)")
    if not rarc_path:
      return
    
    self.save_rarc_by_path(rarc_path)
  
  def open_rarc_by_path(self, rarc_path):
    if not os.path.isfile(rarc_path):
      raise Exception("RARC file not found: %s" % rarc_path)
    
    with open(rarc_path, "rb") as f:
      data = BytesIO(f.read())
    self.rarc = RARC(data)
    
    self.settings["last_used_folder_for_rarcs"] = os.path.dirname(rarc_path)
    
    self.ui.rarc_files_tree.clear()
    
    assert len(self.rarc.nodes) == len(self.rarc.nodes[0].files) + 1 - 2
    
    top_level_items = []
    for dir in self.rarc.nodes[0].files:
      if dir.name in [".", ".."]:
        continue
      item = QTreeWidgetItem([dir.name, "", ""])
      top_level_items.append(item)
      self.ui.rarc_files_tree.addTopLevelItem(item)
    
    for i in range(len(top_level_items)):
      top_level_item = top_level_items[i]
      node = self.rarc.nodes[i+1]
      for file in node.files:
        if file.name in [".", ".."]:
          continue
        item = QTreeWidgetItem([file.name, "%d" % file.id, "0x%X" % file.data_size])
        top_level_item.addChild(item)
    
    self.ui.export_rarc.setDisabled(False)
    #self.ui.import_rarc_folder.setDisabled(False)
    self.ui.export_rarc_folder.setDisabled(False)
  
  def save_rarc_by_path(self, rarc_path):
    self.rarc.save_changes()
    
    with open(rarc_path, "wb") as f:
      self.rarc.data.seek(0)
      f.write(self.rarc.data.read())
    
    self.settings["last_used_folder_for_rarcs"] = os.path.dirname(rarc_path)
    
    QMessageBox.information(self, "RARC saved", "Successfully saved RARC.")
  
  def export_rarc_folder(self):
    default_dir = None
    if "last_used_folder_for_rarc_folders" in self.settings:
      default_dir = self.settings["last_used_folder_for_rarc_folders"]
    
    folder_path = QFileDialog.getExistingDirectory(self, "Select folder to extract RARC contents to", default_dir)
    if not folder_path:
      return
    
    self.rarc.extract_all_files_to_disk(output_directory=folder_path)
    
    self.settings["last_used_folder_for_rarc_folders"] = os.path.dirname(folder_path)
    
    QMessageBox.information(self, "RARC extracted", "Successfully extracted RARC contents to \"%s\"." % folder_path)
  
  def get_file_by_tree_item(self, item):
    file_id = item.text(1)
    if file_id == "":
      return None
    file_id = int(file_id)
    file = next((file for file in self.rarc.file_entries if file.id == file_id), None)
    return file
  
  def get_tree_item_by_file(self, file):
    file_id_string = "%d" % file.id
    for i in range(self.ui.rarc_files_tree.topLevelItemCount()):
      top_level_item = self.ui.rarc_files_tree.topLevelItem(i)
      for j in range(top_level_item.childCount()):
        item = top_level_item.child(j)
        if item.text(1) == file_id_string:
          return item
    return None
  
  def show_rarc_files_tree_context_menu(self, pos):
    item = self.ui.rarc_files_tree.itemAt(pos)
    if item is None:
      return
    
    file = self.get_file_by_tree_item(item)
    if file is None:
      return
    
    menu = QMenu(self)
    menu.addAction(self.ui.actionExtractRARCFile)
    self.ui.actionExtractRARCFile.setData(file)
    menu.addAction(self.ui.actionReplaceRARCFile)
    self.ui.actionReplaceRARCFile.setData(file)
    menu.exec_(self.ui.rarc_files_tree.mapToGlobal(pos))
  
  def extract_file_from_rarc(self):
    file = self.ui.actionExtractRARCFile.data()
    
    default_dir = None
    if "last_used_folder_for_files" in self.settings:
      default_dir = self.settings["last_used_folder_for_files"]
    if default_dir is None:
      default_dir = file.name
    else:
      default_dir = os.path.join(default_dir, file.name)
    
    file_path, selected_filter = QFileDialog.getSaveFileName(self, "Save file", default_dir, "All files (*.*)")
    if not file_path:
      return
    
    with open(file_path, "wb") as f:
      file.data.seek(0)
      f.write(file.data.read())
    
    self.settings["last_used_folder_for_files"] = os.path.dirname(file_path)
  
  def replace_file_in_rarc(self):
    file = self.ui.actionReplaceRARCFile.data()
    
    default_dir = None
    if "last_used_folder_for_files" in self.settings:
      default_dir = self.settings["last_used_folder_for_files"]
    
    file_path, selected_filter = QFileDialog.getOpenFileName(self, "Choose File", default_dir, "All files (*.*)")
    if not file_path:
      return
    
    with open(file_path, "rb") as f:
      data = BytesIO(f.read())
    file.data = data
    
    self.settings["last_used_folder_for_files"] = os.path.dirname(file_path)
    
    item = self.get_tree_item_by_file(file)
    item.setText(2, "0x%X" % data_len(file.data)) # Update changed file size
  
  
  def decompress_yaz0(self):
    default_dir = None
    if "last_used_folder_for_yaz0" in self.settings:
      default_dir = self.settings["last_used_folder_for_yaz0"]
    
    comp_path, selected_filter = QFileDialog.getOpenFileName(self, "Choose file to decompress", default_dir, "All files (*.arc)")
    if not comp_path:
      return
    
    self.settings["last_used_folder_for_yaz0"] = os.path.dirname(comp_path)
    default_dir = self.settings["last_used_folder_for_yaz0"]
    
    with open(comp_path, "rb") as f:
      comp_data = BytesIO(f.read())
    if try_read_str(comp_data, 0, 4) != "Yaz0":
      QMessageBox.warning(self, "Not Yaz0 compressed", "The selected file is not Yaz0 compressed. Cannot decompress.")
      return
    
    decomp_path, selected_filter = QFileDialog.getSaveFileName(self, "Choose where to save decompressed file", default_dir, "All files (*.arc)")
    if not decomp_path:
      return
    
    decomp_data = Yaz0.decompress(comp_data)
    
    with open(decomp_path, "wb") as f:
      decomp_data.seek(0)
      f.write(decomp_data.read())
    
    self.settings["last_used_folder_for_yaz0"] = os.path.dirname(decomp_path)
    
    QMessageBox.information(self, "Decompressed file saved", "Successfully decompressed and saved file.")
  
  def compress_yaz0(self):
    default_dir = None
    if "last_used_folder_for_yaz0" in self.settings:
      default_dir = self.settings["last_used_folder_for_yaz0"]
    
    decomp_path, selected_filter = QFileDialog.getOpenFileName(self, "Choose file to compress", default_dir, "All files (*.arc)")
    if not decomp_path:
      return
    
    with open(decomp_path, "rb") as f:
      decomp_data = BytesIO(f.read())
    if try_read_str(decomp_data, 0, 4) == "Yaz0":
      QMessageBox.warning(self, "Already Yaz0 compressed", "The selected file is already Yaz0 compressed. Cannot compress.")
      return
    
    comp_path, selected_filter = QFileDialog.getSaveFileName(self, "Choose where to save compressed file", default_dir, "All files (*.arc)")
    if not comp_path:
      return
    
    # TODO: progress bar?
    comp_data = Yaz0.compress(decomp_data)
    
    with open(comp_path, "wb") as f:
      comp_data.seek(0)
      f.write(comp_data.read())
    
    self.settings["last_used_folder_for_yaz0"] = os.path.dirname(comp_path)
    
    QMessageBox.information(self, "Compressed file saved", "Successfully compressed and saved file.")
  
  
  def import_gcm(self):
    default_dir = None
    if "last_used_folder_for_gcm" in self.settings:
      default_dir = self.settings["last_used_folder_for_gcm"]
    
    gcm_path, selected_filter = QFileDialog.getOpenFileName(self, "Open GCM", default_dir, "GC ISO Files (*.iso *.gcm)")
    if not gcm_path:
      return
    
    self.open_gcm_by_path(gcm_path)
  
  def export_gcm(self):
    default_dir = None
    if "last_used_folder_for_gcm" in self.settings:
      default_dir = self.settings["last_used_folder_for_gcm"]
    
    gcm_path, selected_filter = QFileDialog.getSaveFileName(self, "Save GCM", default_dir, "GC ISO Files (*.iso *.gcm)")
    if not gcm_path:
      return
    
    self.save_gcm_by_path(gcm_path)
  
  def open_gcm_by_path(self, gcm_path):
    if not os.path.isfile(gcm_path):
      raise Exception("GCM file not found: %s" % gcm_path)
    
    self.gcm = GCM(gcm_path)
    
    self.settings["last_used_folder_for_gcm"] = os.path.dirname(gcm_path)
    
    self.gcm.read_entire_disc()
    self.gcm_changed_files = {}
    
    self.ui.gcm_files_tree.clear()
    
    root_entry = self.gcm.file_entries[0]
    self.gcm_file_entry_to_tree_widget_item = {}
    self.gcm_tree_widget_item_to_file_entry = {}
    for file_entry in self.gcm.file_entries:
      if file_entry.is_dir:
        file_size_str = ""
      else:
        file_size_str = "0x%X" % file_entry.file_size
      if file_entry.parent is None:
        # Root entry. Don't add to the tree.
        continue
      elif file_entry.parent == root_entry:
        item = QTreeWidgetItem([file_entry.name, file_size_str])
        self.ui.gcm_files_tree.addTopLevelItem(item)
        self.gcm_file_entry_to_tree_widget_item[file_entry] = item
        self.gcm_tree_widget_item_to_file_entry[item] = file_entry
      else:
        parent_item = self.gcm_file_entry_to_tree_widget_item[file_entry.parent]
        item = QTreeWidgetItem([file_entry.name, file_size_str])
        parent_item.addChild(item)
        self.gcm_file_entry_to_tree_widget_item[file_entry] = item
        self.gcm_tree_widget_item_to_file_entry[item] = file_entry
    
    self.ui.export_gcm.setDisabled(False)
    #self.ui.import_gcm_folder.setDisabled(False)
    self.ui.export_gcm_folder.setDisabled(False)
  
  def save_gcm_by_path(self, gcm_path):
    # TODO: progress bar?
    try:
      self.gcm.export_disc_to_iso_with_changed_files(gcm_path, self.gcm_changed_files)
    except FileNotFoundError:
      QMessageBox.critical(self, "Could not save ISO", "Failed to save a new ISO. The original ISO \"%s\" has been moved or deleted." % self.gcm.iso_path)
      return
    
    # Update the ISO path we read from in case the user tries to read another file after exporting the ISO.
    self.gcm.iso_path = gcm_path
    
    self.settings["last_used_folder_for_gcm"] = os.path.dirname(gcm_path)
    
    QMessageBox.information(self, "GCM saved", "Successfully saved GCM.")
  
  def export_gcm_folder(self):
    default_dir = None
    if "last_used_folder_for_gcm_folders" in self.settings:
      default_dir = self.settings["last_used_folder_for_gcm_folders"]
    
    folder_path = QFileDialog.getExistingDirectory(self, "Select folder to extract GCM contents to", default_dir)
    if not folder_path:
      return
    
    # TODO: this errors out when hitting a file over the size limit to read all at once
    # need to refactor changed_files to not be a bytesio anymore, ideally
    self.gcm.export_disc_to_folder_with_changed_files(folder_path, self.gcm_changed_files)
    
    self.settings["last_used_folder_for_gcm_folders"] = os.path.dirname(folder_path)
    
    QMessageBox.information(self, "GCM extracted", "Successfully extracted GCM contents to \"%s\"." % folder_path)
  
  def show_gcm_files_tree_context_menu(self, pos):
    item = self.ui.gcm_files_tree.itemAt(pos)
    if item is None:
      return
    
    file = self.gcm_tree_widget_item_to_file_entry[item]
    if file is None:
      return
    
    menu = QMenu(self)
    menu.addAction(self.ui.actionExtractGCMFile)
    self.ui.actionExtractGCMFile.setData(file)
    menu.addAction(self.ui.actionReplaceGCMFile)
    self.ui.actionReplaceGCMFile.setData(file)
    menu.exec_(self.ui.gcm_files_tree.mapToGlobal(pos))
  
  def extract_file_from_gcm(self):
    file = self.ui.actionExtractGCMFile.data()
    
    default_dir = None
    if "last_used_folder_for_files" in self.settings:
      default_dir = self.settings["last_used_folder_for_files"]
    if default_dir is None:
      default_dir = file.name
    else:
      default_dir = os.path.join(default_dir, file.name)
    
    file_path, selected_filter = QFileDialog.getSaveFileName(self, "Save file", default_dir, "All files (*.*)")
    if not file_path:
      return
    
    if file.file_path in self.gcm_changed_files:
      data = self.gcm_changed_files[file.file_path]
      data.seek(0)
      data = data
    else:
      try:
        data = self.gcm.read_file_raw_data(file.file_path)
      except FileNotFoundError:
        QMessageBox.critical(self, "Could not read file", "Failed to read file. The ISO \"%s\" has been moved or deleted." % self.gcm.iso_path)
        return
    with open(file_path, "wb") as f:
      f.write(data)
    
    self.settings["last_used_folder_for_files"] = os.path.dirname(file_path)
  
  def replace_file_in_gcm(self):
    file = self.ui.actionReplaceGCMFile.data()
    
    default_dir = None
    if "last_used_folder_for_files" in self.settings:
      default_dir = self.settings["last_used_folder_for_files"]
    
    file_path, selected_filter = QFileDialog.getOpenFileName(self, "Choose File", default_dir, "All files (*.*)")
    if not file_path:
      return
    
    with open(file_path, "rb") as f:
      data = BytesIO(f.read())
    self.gcm_changed_files[file.file_path] = data
    
    self.settings["last_used_folder_for_files"] = os.path.dirname(file_path)
    
    item = self.gcm_file_entry_to_tree_widget_item[file]
    item.setText(1, "0x%X" % data_len(data)) # Update changed file size
  
  
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
