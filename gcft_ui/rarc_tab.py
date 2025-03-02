
import os
import re
from io import BytesIO
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.rarc import RARC, RARCFileAttrType, RARCFileEntry, RARCNode
from gclib.yaz0_yay0 import Yaz0, Yay0

from gcft_ui.gcft_common import RecursiveFilterProxyModel
from gcft_ui.custom_widgets import ComboBoxDelegate, ReadOnlyDelegate
from asset_dumper import AssetDumper

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from gcft_ui.main_window import GCFTWindow

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_rarc_tab import Ui_RARCTab
else:
  Ui_RARCTab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "rarc_tab.ui"))

class RARCTab(QWidget):
  gcft_window: 'GCFTWindow'
  
  FILE_ENTRY_ROLE = Qt.ItemDataRole.UserRole + 0
  NODE_ROLE = Qt.ItemDataRole.UserRole + 1
  
  def __init__(self):
    super().__init__()
    self.ui = Ui_RARCTab()
    self.ui.setupUi(self)
    
    self.rarc = None
    self.rarc_name = None
    self.display_rarc_relative_dir_entries = False # TODO: add option for this to the GUI
    self.display_rarc_dir_indexes = False # TODO: add option for this to the GUI
    
    self.column_names = [
      "File Name",
      "Folder Type",
      "File Index",
      "File ID",
      "File Size",
      "Compression",
      "Preload",
    ]
    
    self.model = QStandardItemModel()
    self.model.setHorizontalHeaderLabels(self.column_names)
    self.model.setColumnCount(len(self.column_names))
    self.proxy = RecursiveFilterProxyModel()
    self.proxy.setSourceModel(self.model)
    self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    
    self.ui.rarc_files_tree.setModel(self.proxy)
    self.selection_model = self.ui.rarc_files_tree.selectionModel()
    
    read_only_delegate = ReadOnlyDelegate(self.ui.rarc_files_tree)
    self.ui.rarc_files_tree.setItemDelegateForColumn(self.column_names.index("File Index"), read_only_delegate)
    self.ui.rarc_files_tree.setItemDelegateForColumn(self.column_names.index("File Size"), read_only_delegate)
    comp_delegate = ComboBoxDelegate(self.ui.rarc_files_tree)
    comp_delegate.set_items(["None", "Yaz0", "Yay0"])
    self.ui.rarc_files_tree.setItemDelegateForColumn(self.column_names.index("Compression"), comp_delegate)
    preload_delegate = ComboBoxDelegate(self.ui.rarc_files_tree)
    preload_delegate.set_items(["None", "MRAM", "ARAM"])
    self.ui.rarc_files_tree.setItemDelegateForColumn(self.column_names.index("Preload"), preload_delegate)
    
    self.ui.filter.textChanged.connect(self.filter_rows)
    
    self.ui.export_rarc.setDisabled(True)
    self.ui.replace_all_files_in_rarc.setDisabled(True)
    self.ui.extract_all_files_from_rarc.setDisabled(True)
    self.ui.dump_all_rarc_textures.setDisabled(True)
    self.ui.export_rarc_to_c_header.setDisabled(True)
    self.ui.sync_file_ids_and_indexes.setDisabled(True)
    
    self.ui.import_rarc.clicked.connect(self.import_rarc)
    self.ui.create_rarc.clicked.connect(self.create_rarc)
    self.ui.create_rarc_from_folder.clicked.connect(self.create_rarc_from_folder)
    self.ui.export_rarc.clicked.connect(self.export_rarc)
    self.ui.replace_all_files_in_rarc.clicked.connect(self.replace_all_files_in_rarc)
    self.ui.extract_all_files_from_rarc.clicked.connect(self.extract_all_files_from_rarc)
    self.ui.dump_all_rarc_textures.clicked.connect(self.dump_all_rarc_textures)
    self.ui.export_rarc_to_c_header.clicked.connect(self.export_rarc_to_c_header)
    
    self.ui.sync_file_ids_and_indexes.clicked.connect(self.sync_file_ids_and_indexes_changed)
    
    self.ui.rarc_files_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.ui.rarc_files_tree.customContextMenuRequested.connect(self.show_rarc_files_tree_context_menu)
    self.model.dataChanged.connect(self.rarc_file_tree_item_changed)
    self.ui.actionExtractRARCFile.triggered.connect(self.extract_file_from_rarc)
    self.ui.actionReplaceRARCFile.triggered.connect(self.replace_file_in_rarc)
    self.ui.actionDeleteRARCFile.triggered.connect(self.delete_file_in_rarc)
    self.ui.actionAddRARCFile.triggered.connect(self.add_file_to_rarc)
    self.ui.actionAddRARCFolder.triggered.connect(self.add_folder_to_rarc)
    self.ui.actionDeleteRARCFolder.triggered.connect(self.delete_folder_in_rarc)
    self.ui.actionExtractAllFilesFromRARCFolder.triggered.connect(self.extract_all_files_from_rarc_folder)
    self.ui.actionReplaceAllFilesInRARCFolder.triggered.connect(self.replace_all_files_in_rarc_folder)
    self.ui.actionOpenRARCImage.triggered.connect(self.open_image_in_rarc)
    self.ui.actionReplaceRARCImage.triggered.connect(self.replace_image_in_rarc)
    self.ui.actionOpenRARCJ3D.triggered.connect(self.open_j3d_in_rarc)
    self.ui.actionReplaceRARCJ3D.triggered.connect(self.replace_j3d_in_rarc)
    self.ui.actionLoadJ3DAnim.triggered.connect(self.load_j3d_anim)
  
  
  def import_rarc(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.import_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="RARC", file_filters=["RARC files (*.arc)"],
    )
  
  def create_rarc_from_folder(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.create_rarc_from_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="RARC"
    )
  
  def export_rarc(self):
    rarc_name = self.rarc_name + ".arc"
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_rarc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="RARC", file_filters=["RARC files (*.arc)"],
      default_file_name=rarc_name
    )
  
  def replace_all_files_in_rarc(self):
    root_node = self.rarc.nodes[0]
    self.ui.actionReplaceAllFilesInRARCFolder.setData(root_node)
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.replace_all_files_in_rarc_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="RARC"
    )
  
  def replace_all_files_in_rarc_folder(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.replace_all_files_in_rarc_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="RARC"
    )
  
  def extract_all_files_from_rarc(self):
    root_node = self.rarc.nodes[0]
    self.ui.actionExtractAllFilesFromRARCFolder.setData(root_node)
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.extract_all_files_from_rarc_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="RARC"
    )
  
  def extract_all_files_from_rarc_folder(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.extract_all_files_from_rarc_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="RARC"
    )
  
  def dump_all_rarc_textures(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.dump_all_rarc_textures_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="all RARC texture"
    )
  
  def export_rarc_to_c_header(self):
    header_name = "res_%s.h" % self.rarc_name.lower()
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_rarc_to_c_header_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="C header",
      default_file_name=header_name
    )
  
  def extract_file_from_rarc(self):
    file: RARCFileEntry = self.ui.actionExtractRARCFile.data()
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.extract_file_from_rarc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def replace_file_in_rarc(self):
    file: RARCFileEntry = self.ui.actionReplaceRARCFile.data()
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.replace_file_in_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def add_file_to_rarc(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.add_file_to_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file"
    )
  
  
  def import_rarc_by_path(self, rarc_path):
    with open(rarc_path, "rb") as f:
      data = BytesIO(f.read())
    
    rarc_name = os.path.splitext(os.path.basename(rarc_path))[0]
    
    self.import_rarc_by_data(data, rarc_name)
  
  def import_rarc_by_data(self, data, rarc_name):
    self.rarc = RARC(data)
    self.rarc.read()
    
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
      # Sort files and folders so they are in the same order as they originally were (and have the same indexes).
      # This is necessary because os.listdir (and os.walk by extension) return names in arbitrary order.
      # Note: We sort these lists in place. This is intentional so the recursion order of os.walk is affected as well.
      file_names.sort()
      subdir_names.sort()
      
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
    self.model.removeRows(0, self.model.rowCount())
    
    root_node = self.rarc.nodes[0]
    root_name_item = QStandardItem(root_node.name)
    root_node_type_item = QStandardItem(root_node.type)
    file_id_item = QStandardItem()
    file_id_item.setEditable(False)
    compression_item = QStandardItem()
    compression_item.setEditable(False)
    preload_item = QStandardItem()
    preload_item.setEditable(False)
    self.model.appendRow([root_name_item, root_node_type_item, QStandardItem(), file_id_item, QStandardItem(), compression_item, preload_item])
    self.set_node_for_model_index(root_name_item.index(), root_node)
    
    for file_entry in self.rarc.file_entries:
      self.add_new_tree_row_for_file_or_dir_entry(file_entry)
    
    self.ui.sync_file_ids_and_indexes.setChecked(self.rarc.keep_file_ids_synced_with_indexes != 0)
    
    self.ui.export_rarc.setDisabled(False)
    self.ui.replace_all_files_in_rarc.setDisabled(False)
    self.ui.extract_all_files_from_rarc.setDisabled(False)
    self.ui.dump_all_rarc_textures.setDisabled(False)
    self.ui.export_rarc_to_c_header.setDisabled(False)
    self.ui.sync_file_ids_and_indexes.setDisabled(False)
    
    self.ui.rarc_files_tree.setColumnWidth(self.column_names.index("File Name"), 300)
    
    self.filter_rows()
    self.expand_item(root_name_item)
  
  def add_new_tree_row_for_file_or_dir_entry(self, file_entry: RARCFileEntry):
    parent_item = self.find_item_by_node(file_entry.parent_node)
    assert parent_item is not None
    
    if file_entry.is_dir:
      self.add_new_tree_row_for_dir_entry(file_entry, parent_item)
    else:
      self.add_new_tree_row_for_file_entry(file_entry, parent_item)
  
  def add_new_tree_row_for_dir_entry(self, dir_entry: RARCFileEntry, parent_item: QStandardItem):
    if dir_entry.name in [".", ".."] and not self.display_rarc_relative_dir_entries:
      return
    
    if self.display_rarc_dir_indexes:
      dir_file_index = self.rarc.file_entries.index(dir_entry)
      dir_file_index_str = self.gcft_window.stringify_number(dir_file_index, min_hex_chars=4)
    else:
      dir_file_index_str = ""
    
    if dir_entry.name in [".", ".."]:
      name_item = QStandardItem(dir_entry.name)
      name_item.setEditable(False)
      node_type_item = QStandardItem()
      node_type_item.setEditable(False)
    else:
      name_item = QStandardItem(dir_entry.node.name)
      node_type_item = QStandardItem(dir_entry.node.type)
    
    file_index_item = QStandardItem(dir_file_index_str)
    file_index_item.setEditable(False)
    file_id_item = QStandardItem()
    file_id_item.setEditable(False)
    compression_item = QStandardItem()
    compression_item.setEditable(False)
    preload_item = QStandardItem()
    preload_item.setEditable(False)
    
    parent_item.appendRow([name_item, node_type_item, file_index_item, file_id_item, QStandardItem(), compression_item, preload_item])
    
    if dir_entry.name not in [".", ".."]:
      self.set_file_entry_for_model_index(name_item.index(), dir_entry)
      self.set_node_for_model_index(name_item.index(), dir_entry.node)
  
  def add_new_tree_row_for_file_entry(self, file_entry: RARCFileEntry, parent_item: QStandardItem):
    file_size_str = self.gcft_window.stringify_number(file_entry.data_size)
    file_id_str = self.gcft_window.stringify_number(file_entry.id, min_hex_chars=4)
    file_index = self.rarc.file_entries.index(file_entry)
    file_index_str = self.gcft_window.stringify_number(file_index, min_hex_chars=4)
    
    name_item = QStandardItem(file_entry.name)
    
    parent_item.appendRow([name_item, QStandardItem(), QStandardItem(file_index_str), QStandardItem(file_id_str), QStandardItem(file_size_str), QStandardItem(), QStandardItem()])
    
    name_index = self.model.indexFromItem(name_item)
    self.set_file_entry_for_model_index(name_index, file_entry)
    
    if file_entry.is_dir:
      return
    
    self.update_file_size_and_compression_and_preload_in_ui(file_entry)
  
  def get_compression_type_string_for_file_entry(self, file_entry: RARCFileEntry):
    if file_entry.type & RARCFileAttrType.COMPRESSED:
      if file_entry.type & RARCFileAttrType.YAZ0_COMPRESSED:
        return "Yaz0"
      else:
        return "Yay0"
    else:
      return "None"
  
  def get_preload_type_string_for_file_entry(self, file_entry: RARCFileEntry):
    if file_entry.type & RARCFileAttrType.PRELOAD_TO_MRAM:
      return "MRAM"
    elif file_entry.type & RARCFileAttrType.PRELOAD_TO_ARAM:
      return "ARAM"
    elif file_entry.type & RARCFileAttrType.LOAD_FROM_DVD:
      return "None"
    else:
      return None
  
  def expand_item(self, item: QStandardItem):
    self.ui.rarc_files_tree.expand(self.proxy.mapFromSource(item.index()))
  
  def find_item_by_file_entry(self, file_entry: RARCFileEntry):
    matched_indexes = self.model.match(
      self.model.index(0, 0),
      self.FILE_ENTRY_ROLE,
      file_entry,
      1,
      Qt.MatchFlag.MatchRecursive
    )
    assert len(matched_indexes) == 1
    return self.model.itemFromIndex(matched_indexes[0])
  
  def find_item_by_node(self, node: RARCNode):
    matched_indexes = self.model.match(
      self.model.index(0, 0),
      self.NODE_ROLE,
      node,
      1,
      Qt.MatchFlag.MatchRecursive
    )
    assert len(matched_indexes) == 1
    return self.model.itemFromIndex(matched_indexes[0])
  
  def set_file_entry_for_model_index(self, index: QModelIndex, file_entry: RARCFileEntry):
    name_index = index.siblingAtColumn(self.column_names.index("File Name"))
    self.model.setData(name_index, file_entry, self.FILE_ENTRY_ROLE)
  
  def set_node_for_model_index(self, index: QModelIndex, node: RARCNode):
    name_index = index.siblingAtColumn(self.column_names.index("File Name"))
    self.model.setData(name_index, node, self.NODE_ROLE)
  
  def get_file_entry_for_model_index(self, index: QModelIndex):
    name_index = index.siblingAtColumn(self.column_names.index("File Name"))
    file_entry: RARCFileEntry = self.model.data(name_index, self.FILE_ENTRY_ROLE)
    return file_entry
  
  def get_node_for_model_index(self, index: QModelIndex):
    name_index = index.siblingAtColumn(self.column_names.index("File Name"))
    node: RARCNode = self.model.data(name_index, self.NODE_ROLE)
    return node
  
  def filter_rows(self):
    query = self.ui.filter.text()
    self.proxy.setFilterFixedString(query)
  
  def each_model_row_index(self, parent: QModelIndex = QModelIndex()):
    # Recursively iterates over each row in the model.
    for row in range(self.model.rowCount(parent)):
      index = self.model.index(row, self.column_names.index("File Name"), parent=parent)
      yield index
      yield from self.each_model_row_index(parent=index)
  
  
  def update_file_size_and_compression_and_preload_in_ui(self, file_entry: RARCFileEntry):
    if file_entry.is_dir:
      return
    
    name_item = self.find_item_by_file_entry(file_entry)
    name_index = name_item.index()
    file_size_item = self.model.itemFromIndex(name_index.siblingAtColumn(self.column_names.index("File Size")))
    
    self.ui.rarc_files_tree.blockSignals(True)
    
    file_size_str = self.gcft_window.stringify_number(fs.data_len(file_entry.data))
    file_size_item.setText(file_size_str)
    
    comp_index = name_index.siblingAtColumn(self.column_names.index("Compression"))
    self.model.setData(comp_index, self.get_compression_type_string_for_file_entry(file_entry), Qt.ItemDataRole.EditRole)
    
    preload_index = name_index.siblingAtColumn(self.column_names.index("Preload"))
    self.model.setData(preload_index, self.get_preload_type_string_for_file_entry(file_entry), Qt.ItemDataRole.EditRole)
    
    self.ui.rarc_files_tree.blockSignals(False)
  
  def update_all_displayed_file_indexes_and_ids(self):
    # Update all the displayed file indexes in case they got shuffled around by adding/removing files/directories.
    for index in self.each_model_row_index():
      file_entry = self.get_file_entry_for_model_index(index)
      if file_entry is None or file_entry.is_dir:
        continue
      
      file_index = self.rarc.file_entries.index(file_entry)
      file_index_str = self.gcft_window.stringify_number(file_index, min_hex_chars=4)
      self.model.setData(index.siblingAtColumn(self.column_names.index("File Index")), file_index_str)
      
      file_id_str = self.gcft_window.stringify_number(file_entry.id, min_hex_chars=4)
      self.model.setData(index.siblingAtColumn(self.column_names.index("File ID")), file_id_str)
  
  def export_rarc_by_path(self, rarc_path):
    self.rarc.save_changes()
    
    with open(rarc_path, "wb") as f:
      self.rarc.data.seek(0)
      f.write(self.rarc.data.read())
    
    self.rarc_name = os.path.splitext(os.path.basename(rarc_path))[0]
    
    QMessageBox.information(self, "RARC saved", "Successfully saved RARC.")
  
  def extract_all_files_from_rarc_folder_by_path(self, folder_path):
    node: RARCNode = self.ui.actionExtractAllFilesFromRARCFolder.data()
    self.rarc.extract_node_to_disk(node, folder_path)
    
    QMessageBox.information(self, "Folder extracted", "Successfully extracted RARC folder contents to \"%s\"." % folder_path)
  
  def replace_all_files_in_rarc_folder_by_path(self, folder_path):
    node: RARCNode = self.ui.actionReplaceAllFilesInRARCFolder.data()
    num_files_overwritten = self.rarc.import_node_from_disk(node, folder_path)
    
    if num_files_overwritten == 0:
      QMessageBox.warning(self, "No matching files found", "The selected folder does not contain any files matching the name and directory structure of files in the selected RARC folder. No files imported.")
      return
    
    QMessageBox.information(self, "Folder imported", "Successfully overwrote %d files in the RARC folder from \"%s\"." % (num_files_overwritten, folder_path))
    
    for file_entry in self.rarc.file_entries:
      self.update_file_size_and_compression_and_preload_in_ui(file_entry)
  
  def dump_all_rarc_textures_by_path(self, folder_path):
    asset_dumper = AssetDumper()
    dumper_generator = asset_dumper.dump_all_textures_in_rarc(self.rarc, folder_path)
    max_val = len(asset_dumper.get_all_rarc_file_paths(self.rarc))
    
    self.gcft_window.start_texture_dumper_thread(asset_dumper, dumper_generator, max_val)
  
  def export_rarc_to_c_header_by_path(self, header_path):
    out_str = ""
    out_str += f"#ifndef RES_{self.rarc_name.upper()}_H\n"
    out_str += f"#define RES_{self.rarc_name.upper()}_H\n\n"
    
    if self.rarc.keep_file_ids_synced_with_indexes:
      out_str += self.get_c_enum_for_rarc(id=True, index=True)
    else:
      out_str += self.get_c_enum_for_rarc(id=True)
      out_str += "\n"
      out_str += self.get_c_enum_for_rarc(index=True)
    
    out_str += f"\n"
    out_str += f"#endif /* RES_{self.rarc_name.upper()}_H */\n"
    
    with open(header_path, "w") as f:
      f.write(out_str)
  
  def get_c_enum_for_rarc(self, id=False, index=False):
    assert id or index
    
    out_str = "enum "
    if id and index:
      out_str += "%s_RES_FILE_ID { // IDs and indexes are synced" % (self.rarc_name.upper())
    elif id:
      out_str += "%s_RES_FILE_ID {" % (self.rarc_name.upper())
    elif index:
      out_str += "%s_RES_FILE_INDEX {" % (self.rarc_name.upper())
    out_str += "\n"
    
    indentation = "    "
    on_first_node = True
    for node in self.rarc.nodes:
      wrote_node_comment = False
      
      for file_entry in node.files:
        if file_entry.is_dir:
          continue
        
        if not wrote_node_comment:
          if not on_first_node:
            out_str += f"{indentation}\n"
          out_str += f"{indentation}/* %s */\n" % node.type.strip()
          wrote_node_comment = True
          on_first_node = False
        
        file_name, file_ext = os.path.splitext(file_entry.name)
        file_ext = file_ext[1:]
        
        # Try to prevent duplicate names.
        all_files_with_same_name = [f for f in self.rarc.file_entries if f.name == file_entry.name]
        if len(all_files_with_same_name) > 1:
          duplicate_index = all_files_with_same_name.index(file_entry)
          file_name = "%s_%d" % (file_name, duplicate_index+1)
        
        enum_val_name = self.rarc_name
        if index and not id:
          enum_val_name += "_INDEX"
        enum_val_name += "_%s_%s" % (file_ext, file_name)
        enum_val_name = re.sub(r"[\s@:\.,\-<>*%\"!&()|]", "_", enum_val_name) # Sanitize identifier
        enum_val_name = enum_val_name.upper()
        
        val = file_entry.id
        if index:
          val = self.rarc.file_entries.index(file_entry)
        out_str += f"{indentation}%s=0x%X,\n" % (enum_val_name, val)
    out_str += "};\n"
    return out_str
  
  def sync_file_ids_and_indexes_changed(self, checked):
    self.rarc.keep_file_ids_synced_with_indexes = 1 if checked else 0
    
    # Update the displayed file IDs to visually sync them.
    self.rarc.regenerate_all_file_entries_list()
    self.update_all_displayed_file_indexes_and_ids()
  
  
  def show_rarc_files_tree_context_menu(self, pos: QPoint):
    if self.rarc is None:
      return
    
    index = self.ui.rarc_files_tree.indexAt(pos)
    if not index.isValid():
      return
    item = self.model.itemFromIndex(self.proxy.mapToSource(index))
    if item is None:
      return
    
    file_entry = self.get_file_entry_for_model_index(item.index())
    node = self.get_node_for_model_index(item.index())
    
    if node:
      menu = QMenu(self)
      menu.addAction(self.ui.actionAddRARCFile)
      self.ui.actionAddRARCFile.setData(node)
      menu.addAction(self.ui.actionAddRARCFolder)
      self.ui.actionAddRARCFolder.setData(node)
      if node.dir_entry is not None:
        menu.addAction(self.ui.actionDeleteRARCFolder)
        self.ui.actionDeleteRARCFolder.setData(node)
      menu.addAction(self.ui.actionExtractAllFilesFromRARCFolder)
      self.ui.actionExtractAllFilesFromRARCFolder.setData(node)
      menu.addAction(self.ui.actionReplaceAllFilesInRARCFolder)
      self.ui.actionReplaceAllFilesInRARCFolder.setData(node)
      menu.exec_(self.ui.rarc_files_tree.mapToGlobal(pos))
    elif file_entry:
      if file_entry.is_dir:
        # Selected a . or .. relative directory entry. Don't give any options for this.
        pass
      else:
        menu = QMenu(self)
        
        basename, file_ext = os.path.splitext(file_entry.name)
        image_selected = False
        j3d_selected = False
        j3d_anim_selected = False
        if file_ext == ".bti":
          image_selected = True
        elif file_ext in [".bdl", ".bmd"]:
          j3d_selected = True
        elif file_ext in [".bmt", ".btk", ".bck", ".brk", ".btp", ".bca", ".bva"]:
          j3d_selected = True
          j3d_anim_selected = True
        
        if image_selected:
          menu.addAction(self.ui.actionOpenRARCImage)
          self.ui.actionOpenRARCImage.setData(file_entry)
          
          menu.addAction(self.ui.actionReplaceRARCImage)
          self.ui.actionReplaceRARCImage.setData(file_entry)
          if self.bti_tab.bti is None:
            self.ui.actionReplaceRARCImage.setDisabled(True)
          else:
            self.ui.actionReplaceRARCImage.setDisabled(False)
        
        if j3d_anim_selected:
          menu.addAction(self.ui.actionLoadJ3DAnim)
          self.ui.actionLoadJ3DAnim.setData(file_entry)
          if not self.j3d_tab.model_loaded:
            self.ui.actionLoadJ3DAnim.setDisabled(True)
          else:
            self.ui.actionLoadJ3DAnim.setDisabled(False)
        
        if j3d_selected:
          menu.addAction(self.ui.actionOpenRARCJ3D)
          self.ui.actionOpenRARCJ3D.setData(file_entry)
          
          menu.addAction(self.ui.actionReplaceRARCJ3D)
          self.ui.actionReplaceRARCJ3D.setData(file_entry)
          if self.j3d_tab.j3d is None:
            self.ui.actionReplaceRARCJ3D.setDisabled(True)
          else:
            self.ui.actionReplaceRARCJ3D.setDisabled(False)
        
        menu.addAction(self.ui.actionExtractRARCFile)
        self.ui.actionExtractRARCFile.setData(file_entry)
        menu.addAction(self.ui.actionReplaceRARCFile)
        self.ui.actionReplaceRARCFile.setData(file_entry)
        menu.addAction(self.ui.actionDeleteRARCFile)
        self.ui.actionDeleteRARCFile.setData(file_entry)
        
        menu.exec_(self.ui.rarc_files_tree.mapToGlobal(pos))
  
  def extract_file_from_rarc_by_path(self, file_path):
    file_entry: RARCFileEntry = self.ui.actionExtractRARCFile.data()
    
    with open(file_path, "wb") as f:
      file_entry.data.seek(0)
      f.write(file_entry.data.read())
  
  def replace_file_in_rarc_by_path(self, file_path):
    file_entry: RARCFileEntry = self.ui.actionReplaceRARCFile.data()
    
    with open(file_path, "rb") as f:
      data = BytesIO(f.read())
    file_entry.data = data
    file_entry.update_compression_flags_from_data()
    
    self.update_file_size_and_compression_and_preload_in_ui(file_entry)
    
    self.gcft_window.ui.statusbar.showMessage("Replaced %s." % file_entry.name, 3000)
  
  def delete_file_in_rarc(self):
    file_entry: RARCFileEntry = self.ui.actionDeleteRARCFile.data()
    
    if not self.gcft_window.confirm_delete(file_entry.name):
      return
    
    self.rarc.delete_file(file_entry)
    
    file_item = self.find_item_by_file_entry(file_entry)
    dir_item = self.find_item_by_node(file_entry.parent_node)
    dir_item.removeRow(file_item.index().row())
    
    self.update_all_displayed_file_indexes_and_ids()
  
  def open_image_in_rarc(self):
    file_entry: RARCFileEntry = self.ui.actionOpenRARCImage.data()
    
    bti_name = os.path.splitext(file_entry.name)[0]
    
    data = fs.make_copy_data(file_entry.data)
    self.bti_tab.import_bti_by_data(data, bti_name)
    
    self.gcft_window.set_tab_by_name("BTI Images")
  
  def replace_image_in_rarc(self):
    file_entry: RARCFileEntry = self.ui.actionReplaceRARCImage.data()
    
    self.bti_tab.bti.save_changes()
    
    file_entry.data = fs.make_copy_data(self.bti_tab.bti.data)
    file_entry.update_compression_flags_from_data()
    
    self.update_file_size_and_compression_and_preload_in_ui(file_entry)
    
    self.gcft_window.ui.statusbar.showMessage("Replaced %s." % file_entry.name, 3000)
  
  def open_j3d_in_rarc(self):
    file_entry: RARCFileEntry = self.ui.actionOpenRARCJ3D.data()
    
    j3d_name = os.path.splitext(file_entry.name)[0]
    
    data = fs.make_copy_data(file_entry.data)
    self.j3d_tab.import_j3d_by_data(data, j3d_name)
    
    self.gcft_window.set_tab_by_name("J3D Files")
  
  def replace_j3d_in_rarc(self):
    file_entry: RARCFileEntry = self.ui.actionReplaceRARCJ3D.data()
    
    self.j3d_tab.j3d.save()
    
    file_entry.data = fs.make_copy_data(self.j3d_tab.j3d.data)
    file_entry.update_compression_flags_from_data()
    
    self.update_file_size_and_compression_and_preload_in_ui(file_entry)
    
    self.gcft_window.ui.statusbar.showMessage("Replaced %s." % file_entry.name, 3000)
  
  def load_j3d_anim(self):
    file_entry: RARCFileEntry = self.ui.actionLoadJ3DAnim.data()
    
    j3d_name = os.path.splitext(file_entry.name)[0]
    
    data = fs.make_copy_data(file_entry.data)
    self.j3d_tab.load_anim_by_data(data, j3d_name)
    
    self.gcft_window.set_tab_by_name("J3D Files")
  
  def add_file_to_rarc_by_path(self, file_path):
    parent_node: RARCNode = self.ui.actionAddRARCFile.data()
    
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
      file_data = BytesIO(f.read())
    
    existing_file_names = [fe.name for fe in self.rarc.file_entries if not fe.is_dir]
    if file_name in existing_file_names:
      QMessageBox.warning(self, "File already exists", "Cannot add new file. The archive already contains a file named \"%s\".\n\nIf you wish to replace the existing file, right click on it in the files tree and select 'Replace File'." % file_name)
      return
    
    file_entry = self.rarc.add_new_file(file_name, file_data, parent_node)
    
    parent_item = self.find_item_by_node(parent_node)
    
    self.add_new_tree_row_for_file_entry(file_entry, parent_item)
    
    self.update_all_displayed_file_indexes_and_ids()
  
  def add_folder_to_rarc(self):
    parent_node: RARCNode = self.ui.actionAddRARCFolder.data()
    
    dir_name, confirmed = QInputDialog.getText(
      self, "Input Folder Name", "Write the name for the new folder:",
      flags=Qt.WindowType.WindowSystemMenuHint | Qt.WindowType.WindowTitleHint
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
      flags=Qt.WindowType.WindowSystemMenuHint | Qt.WindowType.WindowTitleHint
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
    
    self.add_new_tree_row_for_file_or_dir_entry(dir_file_entry)
    for child_file_entry in dir_file_entry.node.files:
      # Add the . and .. relative dir entries.
      self.add_new_tree_row_for_file_or_dir_entry(child_file_entry)
    
    self.update_all_displayed_file_indexes_and_ids()
  
  def delete_folder_in_rarc(self):
    node: RARCNode = self.ui.actionDeleteRARCFolder.data()
    
    if not self.gcft_window.confirm_delete(node.name, is_folder=True):
      return
    
    dir_entry = node.dir_entry
    
    self.rarc.delete_directory(dir_entry)
    
    self.remove_folder_from_files_tree(dir_entry)
    
    self.update_all_displayed_file_indexes_and_ids()
  
  def remove_folder_from_files_tree(self, dir_entry: RARCFileEntry):
    dir_item = self.find_item_by_file_entry(dir_entry)
    parent_dir_item = self.find_item_by_node(dir_entry.parent_node)
    # When removing one row, the model automatically takes care of recursively deleting all children.
    parent_dir_item.removeRow(dir_item.index().row())
  
  # See: GCM.check_file_is_rarc
  def check_file_path_is_rarc(self, file_path: str) -> bool:
    try:
      _, file_ext = os.path.splitext(os.path.basename(file_path))
      if file_ext == ".arc":
        with open(file_path, "rb") as f:
          file_data = BytesIO(f.read(4))
        if RARC.check_file_is_rarc(file_data):
          return True
      elif file_ext == ".szs":
        with open(file_path, "rb") as f:
          file_data = BytesIO(f.read(0x15))
        if Yaz0.check_is_compressed(file_data):
          magic = fs.read_str(file_data, 0x11, 4)
          if magic == "RARC":
            return True
      elif file_ext == ".szp":
        with open(file_path, "rb") as f:
          file_data = BytesIO(f.read())
        if Yay0.check_is_compressed(file_data):
          chunk_offset = fs.read_u32(file_data, 0xC)
          magic = fs.read_str(file_data, chunk_offset, 4)
          if magic == "RARC":
            return True
    except Exception as e:
      pass
    return False
  
  
  def rarc_file_tree_item_changed(self, top_left_index: QModelIndex, bottom_right_index: QModelIndex):
    if top_left_index != bottom_right_index:
      raise Exception("Multi-cell editing not supported")
    column = top_left_index.column()
    if column == self.column_names.index("File Name"):
      self.change_rarc_file_name(top_left_index)
    elif column == self.column_names.index("Folder Type"):
      self.change_rarc_node_type(top_left_index)
    elif column == self.column_names.index("File ID"):
      self.change_rarc_file_id(top_left_index)
    elif column == self.column_names.index("Compression"):
      self.change_rarc_file_compression_type(top_left_index)
    elif column == self.column_names.index("Preload"):
      self.change_rarc_file_preload_type(top_left_index)
  
  def change_rarc_file_name(self, name_index: QModelIndex):
    new_file_name = name_index.model().data(name_index, Qt.ItemDataRole.EditRole)
    file_entry = self.get_file_entry_for_model_index(name_index)
    node = self.get_node_for_model_index(name_index)
    
    if node is not None:
      if len(new_file_name) == 0:
        QMessageBox.warning(self, "Invalid folder name", "Folder name cannot be empty.")
        self.model.setData(name_index, node.name)
        return
      
      node.name = new_file_name
      if node.dir_entry is not None:
        node.dir_entry.name = new_file_name
    else:
      if len(new_file_name) == 0:
        QMessageBox.warning(self, "Invalid file name", "File name cannot be empty.")
        self.model.setData(name_index, file_entry.name)
        return
      
      other_file_entry = next((
        fe for fe in self.rarc.file_entries
        if fe.name == new_file_name
        and fe.parent_node == file_entry.parent_node
        and not fe.is_dir
      ), None)
      
      if other_file_entry == file_entry:
        # File name not changed
        return
      
      if other_file_entry is not None:
        QMessageBox.warning(self, "Duplicate file name", "The file name you entered is already used by another file in this directory.")
        self.model.setData(name_index, file_entry.name)
        return
    
      file_entry.name = new_file_name
    
    self.model.setData(name_index, new_file_name)
  
  def change_rarc_node_type(self, node_type_index: QModelIndex):
    new_node_type = node_type_index.model().data(node_type_index, Qt.ItemDataRole.EditRole)
    node = self.get_node_for_model_index(node_type_index)
    
    if len(new_node_type) == 0:
      QMessageBox.warning(self, "Invalid folder type", "Folder type cannot be empty.")
      self.model.setData(node_type_index, node.type)
      return
    if len(new_node_type) > 4:
      QMessageBox.warning(self, "Invalid folder type", "Folder types cannot be longer than 4 characters.")
      self.model.setData(node_type_index, node.type)
      return
    
    if len(new_node_type) < 4:
      spaces_to_add = 4-len(new_node_type)
      new_node_type += " "*spaces_to_add
    
    node.type = new_node_type
    
    self.model.setData(node_type_index, node.type)
  
  def change_rarc_file_id(self, file_id_index: QModelIndex):
    new_file_id_str = file_id_index.model().data(file_id_index, Qt.ItemDataRole.EditRole)
    file_entry = self.get_file_entry_for_model_index(file_id_index)
    
    if self.gcft_window.display_hexadecimal_numbers:
      hexadecimal_match = re.search(r"^\s*(?:0x)?([0-9a-f]+)\s*$", new_file_id_str, re.IGNORECASE)
      if hexadecimal_match:
        new_file_id = int(hexadecimal_match.group(1), 16)
      else:
        QMessageBox.warning(self, "Invalid file ID", "\"%s\" is not a valid hexadecimal number." % new_file_id_str)
        file_id_str = self.gcft_window.stringify_number(file_entry.id, min_hex_chars=4)
        self.model.setData(file_id_index, file_id_str)
        return
    else:
      decimal_match = re.search(r"^\s*(\d+)\s*$", new_file_id_str, re.IGNORECASE)
      if decimal_match:
        new_file_id = int(decimal_match.group(1))
      else:
        QMessageBox.warning(self, "Invalid file ID", "\"%s\" is not a valid decimal number." % new_file_id_str)
        file_id_str = self.gcft_window.stringify_number(file_entry.id, min_hex_chars=4)
        self.model.setData(file_id_index, file_id_str)
        return
    
    if new_file_id >= 0xFFFF:
      QMessageBox.warning(self, "Invalid file ID", "\"%s\" is too large to be a file ID. It must be in the range 0x0000-0xFFFE." % new_file_id_str)
      file_id_str = self.gcft_window.stringify_number(file_entry.id, min_hex_chars=4)
      self.model.setData(file_id_index, file_id_str)
      return
    
    other_file_entry = next((fe for fe in self.rarc.file_entries if fe.id == new_file_id), None)
    
    if other_file_entry == file_entry:
      # File ID not changed
      file_id_str = self.gcft_window.stringify_number(file_entry.id, min_hex_chars=4)
      self.model.setData(file_id_index, file_id_str)
      return
    
    if other_file_entry is not None:
      QMessageBox.warning(self, "Duplicate file ID", "The file ID you entered is already used by the file \"%s\"." % other_file_entry.name)
      file_id_str = self.gcft_window.stringify_number(file_entry.id, min_hex_chars=4)
      self.model.setData(file_id_index, file_id_str)
      return
    
    file_entry.id = new_file_id
    
    file_id_str = self.gcft_window.stringify_number(file_entry.id, min_hex_chars=4)
    self.model.setData(file_id_index, file_id_str)
  
  def change_rarc_file_compression_type(self, comp_index: QModelIndex):
    comp_value_str = comp_index.model().data(comp_index, Qt.ItemDataRole.EditRole)
    file_entry = self.get_file_entry_for_model_index(comp_index)
    
    file_entry.update_compression_flags_from_data()
    
    is_yaz0_compressed = bool((file_entry.type & RARCFileAttrType.COMPRESSED) and (file_entry.type & RARCFileAttrType.YAZ0_COMPRESSED))
    is_yay0_compressed = bool((file_entry.type & RARCFileAttrType.COMPRESSED) and not (file_entry.type & RARCFileAttrType.YAZ0_COMPRESSED))
    
    yaz0_selected = comp_value_str == "Yaz0"
    yay0_selected = comp_value_str == "Yay0"
    
    if is_yaz0_compressed and not yaz0_selected:
      file_entry.data = Yaz0.decompress(file_entry.data)
      file_entry.update_compression_flags_from_data()
    elif is_yay0_compressed and not yay0_selected:
      file_entry.data = Yay0.decompress(file_entry.data)
      file_entry.update_compression_flags_from_data()
    
    if yaz0_selected and not is_yaz0_compressed:
      search_depth, should_pad_data = self.yaz0_yay0_tab.get_search_depth_and_should_pad()
      file_entry.data = Yaz0.compress(file_entry.data, search_depth=search_depth, should_pad_data=should_pad_data)
      file_entry.update_compression_flags_from_data()
    elif yay0_selected and not is_yay0_compressed:
      search_depth, should_pad_data = self.yaz0_yay0_tab.get_search_depth_and_should_pad()
      file_entry.data = Yay0.compress(file_entry.data, search_depth=search_depth, should_pad_data=should_pad_data)
      file_entry.update_compression_flags_from_data()
    
    # Update the UI to match the new file data's size.
    self.update_file_size_and_compression_and_preload_in_ui(file_entry)
  
  def change_rarc_file_preload_type(self, preload_index: QModelIndex):
    preload_value_str = preload_index.model().data(preload_index, Qt.ItemDataRole.EditRole)
    file_entry = self.get_file_entry_for_model_index(preload_index)
    
    file_entry.type &= ~RARCFileAttrType.PRELOAD_TO_MRAM
    file_entry.type &= ~RARCFileAttrType.PRELOAD_TO_ARAM
    file_entry.type &= ~RARCFileAttrType.LOAD_FROM_DVD
    
    if preload_value_str == "MRAM":
      file_entry.type |= RARCFileAttrType.PRELOAD_TO_MRAM
    elif preload_value_str == "ARAM":
      file_entry.type |= RARCFileAttrType.PRELOAD_TO_ARAM
    else:
      file_entry.type |= RARCFileAttrType.LOAD_FROM_DVD
  
  
  def keyPressEvent(self, event):
    event.ignore()
    if event.matches(QKeySequence.StandardKey.Copy):
      selected_index = self.selection_model.currentIndex()
      if not selected_index.isValid():
        return
      selected_index = self.proxy.mapToSource(selected_index)
      if selected_index.column() != self.column_names.index("File Name"):
        return
      item = self.model.itemFromIndex(selected_index)
      if item is None:
        return
      file_entry = self.get_file_entry_for_model_index(item.index())
      if not isinstance(file_entry, RARCFileEntry):
        return
      
      file_path = file_entry.name
      dir_entry: RARCFileEntry = file_entry.parent_node.dir_entry
      while dir_entry is not None:
        file_path = dir_entry.name + "/" + file_path
        dir_entry = dir_entry.parent_node.dir_entry
      
      QApplication.clipboard().setText(file_path)
      event.accept()
