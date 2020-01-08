
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

from wwlib.rarc import RARC
from wwlib.yaz0 import Yaz0
from fs_helpers import *

class GCFTWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    self.ui.rarc_files_tree.setColumnWidth(0, 300)
    self.ui.export_rarc.setDisabled(True)
    
    self.ui.import_rarc.clicked.connect(self.import_rarc)
    self.ui.export_rarc.clicked.connect(self.export_rarc)
    
    self.ui.rarc_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.rarc_files_tree.customContextMenuRequested.connect(self.show_rarc_files_tree_context_menu)
    self.ui.actionExtractRARCFile.triggered.connect(self.extract_file_from_rarc)
    self.ui.actionReplaceRARCFile.triggered.connect(self.replace_file_in_rarc)
    
    self.ui.decompress_yaz0.clicked.connect(self.decompress_yaz0)
    self.ui.compress_yaz0.clicked.connect(self.compress_yaz0)
    
    self.load_settings()
    
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
  
  def save_rarc_by_path(self, rarc_path):
    self.rarc.save_changes()
    
    with open(rarc_path, "wb") as f:
      self.rarc.data.seek(0)
      f.write(self.rarc.data.read())
    
    QMessageBox.information(self, "RARC saved", "Successfully saved RARC.")
  
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
    item.setText(2, "0x%X" % data_len(file.data))
  
  
  def decompress_yaz0(self):
    default_dir = None
    if "last_used_folder_for_yaz0" in self.settings:
      default_dir = self.settings["last_used_folder_for_yaz0"]
    
    comp_path, selected_filter = QFileDialog.getOpenFileName(self, "Choose file to decompress", default_dir, "All files (*.arc)")
    if not comp_path:
      return
    
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
  
  
  def keyPressEvent(self, event):
    if event.matches(QKeySequence.Copy):
      if self.ui.rarc_files_tree.currentColumn() == 0:
        # When copying the filename, override the default behavior so it instead copies the whole path.
        item = self.ui.rarc_files_tree.currentItem()
        file_path = "%s/%s" % (item.parent().text(0), item.text(0))
        QApplication.instance().clipboard().setText(file_path)
  
  def closeEvent(self, event):
    self.save_settings()
