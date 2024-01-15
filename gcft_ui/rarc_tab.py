
import os
import re
import traceback
from io import BytesIO
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.rarc import RARC, RARCFileAttrType
from gclib.yaz0 import Yaz0
from gcft_ui.uic.ui_rarc_tab import Ui_RARCTab
from asset_dumper import AssetDumper

class RARCTab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_RARCTab()
    self.ui.setupUi(self)
    
    self.rarc = None
    self.rarc_name = None
    self.display_rarc_relative_dir_entries = False
    self.display_rarc_dir_indexes = False
    
    # This should be in the .ui file, but PySide6 doesn't compile it correctly.
    self.ui.rarc_files_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    self.rarc_col_name_to_index = {}
    for col in range(self.ui.rarc_files_tree.columnCount()):
      column_name = self.ui.rarc_files_tree.headerItem().text(col)
      self.rarc_col_name_to_index[column_name] = col
    
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
    
    self.ui.rarc_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.rarc_files_tree.customContextMenuRequested.connect(self.show_rarc_files_tree_context_menu)
    self.ui.rarc_files_tree.itemDoubleClicked.connect(self.edit_rarc_files_tree_item_text)
    self.ui.rarc_files_tree.itemChanged.connect(self.rarc_file_tree_item_changed)
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
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="RARC", file_filter="RARC files (*.arc)"
    )
  
  def create_rarc_from_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.create_rarc_from_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="RARC"
    )
  
  def export_rarc(self):
    rarc_name = self.rarc_name + ".arc"
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_rarc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="RARC", file_filter="RARC files (*.arc)",
      default_file_name=rarc_name
    )
  
  def replace_all_files_in_rarc(self):
    root_node = self.rarc.nodes[0]
    self.ui.actionReplaceAllFilesInRARCFolder.setData(root_node)
    self.window().generic_do_gui_file_operation(
      op_callback=self.replace_all_files_in_rarc_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="RARC"
    )
  
  def replace_all_files_in_rarc_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.replace_all_files_in_rarc_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="RARC"
    )
  
  def extract_all_files_from_rarc(self):
    root_node = self.rarc.nodes[0]
    self.ui.actionExtractAllFilesFromRARCFolder.setData(root_node)
    self.window().generic_do_gui_file_operation(
      op_callback=self.extract_all_files_from_rarc_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="RARC"
    )
  
  def extract_all_files_from_rarc_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.extract_all_files_from_rarc_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="RARC"
    )
  
  def dump_all_rarc_textures(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.dump_all_rarc_textures_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="all RARC texture"
    )
  
  def export_rarc_to_c_header(self):
    header_name = "res_%s.h" % self.rarc_name.lower()
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_rarc_to_c_header_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="C header",
      default_file_name=header_name
    )
  
  def extract_file_from_rarc(self):
    file = self.ui.actionExtractRARCFile.data()
    self.window().generic_do_gui_file_operation(
      op_callback=self.extract_file_from_rarc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def replace_file_in_rarc(self):
    file = self.ui.actionReplaceRARCFile.data()
    self.window().generic_do_gui_file_operation(
      op_callback=self.replace_file_in_rarc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def add_file_to_rarc(self):
    self.window().generic_do_gui_file_operation(
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
    self.ui.rarc_files_tree.clear()
    
    self.rarc_node_to_tree_widget_item = {}
    self.rarc_tree_widget_item_to_node = {}
    self.rarc_file_entry_to_tree_widget_item = {}
    self.rarc_tree_widget_item_to_file_entry = {}
    
    root_node = self.rarc.nodes[0]
    root_item = QTreeWidgetItem([root_node.name, root_node.type, "", "", "", ""])
    root_item.setFlags(root_item.flags() | Qt.ItemIsEditable)
    self.ui.rarc_files_tree.addTopLevelItem(root_item)
    self.rarc_node_to_tree_widget_item[root_node] = root_item
    self.rarc_tree_widget_item_to_node[root_item] = root_node
    
    for file_entry in self.rarc.file_entries:
      self.add_rarc_file_entry_to_files_tree(file_entry)
    
    # Expand the root node by default.
    self.ui.rarc_files_tree.topLevelItem(0).setExpanded(True)
    
    self.ui.sync_file_ids_and_indexes.setChecked(self.rarc.keep_file_ids_synced_with_indexes != 0)
    
    self.ui.export_rarc.setDisabled(False)
    self.ui.replace_all_files_in_rarc.setDisabled(False)
    self.ui.extract_all_files_from_rarc.setDisabled(False)
    self.ui.dump_all_rarc_textures.setDisabled(False)
    self.ui.export_rarc_to_c_header.setDisabled(False)
    self.ui.sync_file_ids_and_indexes.setDisabled(False)
    
    self.ui.rarc_files_tree.setColumnWidth(0, 300)
  
  def add_rarc_file_entry_to_files_tree(self, file_entry):
    index_of_entry_in_parent_dir = file_entry.parent_node.files.index(file_entry)
    
    if file_entry.is_dir:
      dir_file_entry = file_entry
      if file_entry.name in [".", ".."] and not self.display_rarc_relative_dir_entries:
        return
      
      node = file_entry.node
      
      parent_item = self.rarc_node_to_tree_widget_item[dir_file_entry.parent_node]
      
      if self.display_rarc_dir_indexes:
        dir_file_index = self.rarc.file_entries.index(dir_file_entry)
        dir_file_index_str = self.window().stringify_number(dir_file_index, min_hex_chars=4)
      else:
        dir_file_index_str = ""
      
      if file_entry.name in [".", ".."]:
        item = QTreeWidgetItem([file_entry.name, "", dir_file_index_str, "", "", ""])
        parent_item.insertChild(index_of_entry_in_parent_dir, item)
      else:
        item = QTreeWidgetItem([node.name, node.type, dir_file_index_str, "", "", ""])
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        parent_item.insertChild(index_of_entry_in_parent_dir, item)
        
        self.rarc_node_to_tree_widget_item[node] = item
        self.rarc_tree_widget_item_to_node[item] = node
      
      self.rarc_file_entry_to_tree_widget_item[dir_file_entry] = item
      self.rarc_tree_widget_item_to_file_entry[item] = dir_file_entry
    else:
      file_size_str = self.window().stringify_number(file_entry.data_size)
      file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
      file_index = self.rarc.file_entries.index(file_entry)
      file_index_str = self.window().stringify_number(file_index, min_hex_chars=4)
      
      parent_item = self.rarc_node_to_tree_widget_item[file_entry.parent_node]
      item = QTreeWidgetItem([file_entry.name, "", file_index_str, file_id_str, file_size_str, ""])
      item.setFlags(item.flags() | Qt.ItemIsEditable)
      parent_item.insertChild(index_of_entry_in_parent_dir, item)
      self.rarc_file_entry_to_tree_widget_item[file_entry] = item
      self.rarc_tree_widget_item_to_file_entry[item] = file_entry
      self.update_file_size_and_compression_in_ui(file_entry)
  
  def update_file_size_and_compression_in_ui(self, file_entry):
    if file_entry.is_dir:
      return
    
    item = self.rarc_file_entry_to_tree_widget_item.get(file_entry)
    
    self.ui.rarc_files_tree.blockSignals(True)
    
    file_size_str = self.window().stringify_number(fs.data_len(file_entry.data))
    item.setText(self.rarc_col_name_to_index["File Size"], file_size_str)
    
    # TODO: Add a Yay0 checkbox and update it here once Yay0 compression is supported.
    if file_entry.type & RARCFileAttrType.COMPRESSED:
      if file_entry.type & RARCFileAttrType.YAZ0_COMPRESSED:
        item.setCheckState(self.rarc_col_name_to_index["Yaz0 Compressed"], Qt.Checked)
      else:
        item.setCheckState(self.rarc_col_name_to_index["Yaz0 Compressed"], Qt.Unchecked)
    else:
      item.setCheckState(self.rarc_col_name_to_index["Yaz0 Compressed"], Qt.Unchecked)
    
    self.ui.rarc_files_tree.blockSignals(False)
  
  def update_all_displayed_file_indexes_and_ids(self):
    # Update all the displayed file indexes in case they got shuffled around by adding/removing files/directories.
    for file_entry, item in self.rarc_file_entry_to_tree_widget_item.items():
      if file_entry.is_dir:
        continue
      
      file_index = self.rarc.file_entries.index(file_entry)
      file_index_str = self.window().stringify_number(file_index, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File Index"], file_index_str)
      
      file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
  
  def export_rarc_by_path(self, rarc_path):
    self.rarc.save_changes()
    
    with open(rarc_path, "wb") as f:
      self.rarc.data.seek(0)
      f.write(self.rarc.data.read())
    
    self.rarc_name = os.path.splitext(os.path.basename(rarc_path))[0]
    
    QMessageBox.information(self, "RARC saved", "Successfully saved RARC.")
  
  def extract_all_files_from_rarc_folder_by_path(self, folder_path):
    node = self.ui.actionExtractAllFilesFromRARCFolder.data()
    self.rarc.extract_node_to_disk(node, folder_path)
    
    QMessageBox.information(self, "Folder extracted", "Successfully extracted RARC folder contents to \"%s\"." % folder_path)
  
  def replace_all_files_in_rarc_folder_by_path(self, folder_path):
    node = self.ui.actionReplaceAllFilesInRARCFolder.data()
    num_files_overwritten = self.rarc.import_node_from_disk(node, folder_path)
    
    if num_files_overwritten == 0:
      QMessageBox.warning(self, "No matching files found", "The selected folder does not contain any files matching the name and directory structure of files in the selected RARC folder. No files imported.")
      return
    
    QMessageBox.information(self, "Folder imported", "Successfully overwrote %d files in the RARC folder from \"%s\"." % (num_files_overwritten, folder_path))
    
    for file_entry in self.rarc.file_entries:
      self.update_file_size_and_compression_in_ui(file_entry)
  
  def dump_all_rarc_textures_by_path(self, folder_path):
    asset_dumper = AssetDumper()
    dumper_generator = asset_dumper.dump_all_textures_in_rarc(self.rarc, folder_path)
    max_val = len(asset_dumper.get_all_rarc_file_paths(self.rarc))
    
    self.window().start_texture_dumper_thread(asset_dumper, dumper_generator, max_val)
  
  def export_rarc_to_c_header_by_path(self, header_path):
    out_str = "#define %s_RES_NAME \"%s\"\n\n" % (self.rarc_name.upper(), self.rarc_name)
    
    if self.rarc.keep_file_ids_synced_with_indexes:
      out_str += self.get_c_enum_for_rarc(id=True, index=True)
    else:
      out_str += self.get_c_enum_for_rarc(id=True)
      out_str += "\n"
      out_str += self.get_c_enum_for_rarc(index=True)
    
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
  
  
  def show_rarc_files_tree_context_menu(self, pos):
    if self.rarc is None:
      return
    
    item = self.ui.rarc_files_tree.itemAt(pos)
    if item is None:
      return
    
    node = self.rarc_tree_widget_item_to_node.get(item)
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
    else:
      file = self.rarc_tree_widget_item_to_file_entry.get(item)
      if file is None:
        return
      
      if file.is_dir:
        # Selected a . or .. relative directory entry. Don't give any options for this..
        pass
      else:
        menu = QMenu(self)
        
        basename, file_ext = os.path.splitext(file.name)
        image_selected = False
        j3d_selected = False
        j3d_anim_selected = False
        if file_ext == ".bti":
          image_selected = True
        elif file_ext in [".bdl", ".bmd"]:
          j3d_selected = True
        elif file_ext in [".bmt", ".btk", ".bck", ".brk", ".btp"]:
          j3d_selected = True
          j3d_anim_selected = True
        
        if image_selected:
          menu.addAction(self.ui.actionOpenRARCImage)
          self.ui.actionOpenRARCImage.setData(file)
          
          menu.addAction(self.ui.actionReplaceRARCImage)
          self.ui.actionReplaceRARCImage.setData(file)
          if self.bti_tab.bti is None:
            self.ui.actionReplaceRARCImage.setDisabled(True)
          else:
            self.ui.actionReplaceRARCImage.setDisabled(False)
        
        if j3d_anim_selected:
          menu.addAction(self.ui.actionLoadJ3DAnim)
          self.ui.actionLoadJ3DAnim.setData(file)
          if not self.j3d_tab.model_loaded:
            self.ui.actionLoadJ3DAnim.setDisabled(True)
          else:
            self.ui.actionLoadJ3DAnim.setDisabled(False)
        
        if j3d_selected:
          menu.addAction(self.ui.actionOpenRARCJ3D)
          self.ui.actionOpenRARCJ3D.setData(file)
          
          menu.addAction(self.ui.actionReplaceRARCJ3D)
          self.ui.actionReplaceRARCJ3D.setData(file)
          if self.j3d_tab.j3d is None:
            self.ui.actionReplaceRARCJ3D.setDisabled(True)
          else:
            self.ui.actionReplaceRARCJ3D.setDisabled(False)
        
        menu.addAction(self.ui.actionExtractRARCFile)
        self.ui.actionExtractRARCFile.setData(file)
        menu.addAction(self.ui.actionReplaceRARCFile)
        self.ui.actionReplaceRARCFile.setData(file)
        menu.addAction(self.ui.actionDeleteRARCFile)
        self.ui.actionDeleteRARCFile.setData(file)
        
        menu.exec_(self.ui.rarc_files_tree.mapToGlobal(pos))
  
  def extract_file_from_rarc_by_path(self, file_path):
    file_entry = self.ui.actionExtractRARCFile.data()
    
    with open(file_path, "wb") as f:
      file_entry.data.seek(0)
      f.write(file_entry.data.read())
  
  def replace_file_in_rarc_by_path(self, file_path):
    file_entry = self.ui.actionReplaceRARCFile.data()
    
    with open(file_path, "rb") as f:
      data = BytesIO(f.read())
    file_entry.data = data
    file_entry.update_compression_flags_from_data()
    
    self.update_file_size_and_compression_in_ui(file_entry)
    
    self.window().ui.statusbar.showMessage("Replaced %s." % file_entry.name, 3000)
  
  def delete_file_in_rarc(self):
    file_entry = self.ui.actionDeleteRARCFile.data()
    
    if not self.window().confirm_delete(file_entry.name):
      return
    
    node = file_entry.parent_node
    
    self.rarc.delete_file(file_entry)
    
    file_item = self.rarc_file_entry_to_tree_widget_item.get(file_entry)
    dir_item = self.rarc_node_to_tree_widget_item.get(node)
    dir_item.removeChild(file_item)
    del self.rarc_file_entry_to_tree_widget_item[file_entry]
    del self.rarc_tree_widget_item_to_file_entry[file_item]
    
    self.update_all_displayed_file_indexes_and_ids()
  
  def open_image_in_rarc(self):
    file_entry = self.ui.actionOpenRARCImage.data()
    
    bti_name = os.path.splitext(file_entry.name)[0]
    
    data = fs.make_copy_data(file_entry.data)
    self.bti_tab.import_bti_by_data(data, bti_name)
    
    self.window().set_tab_by_name("BTI Images")
  
  def replace_image_in_rarc(self):
    file_entry = self.ui.actionReplaceRARCImage.data()
    
    self.bti_tab.bti.save_changes()
    
    file_entry.data = fs.make_copy_data(self.bti_tab.bti.data)
    file_entry.update_compression_flags_from_data()
    
    self.update_file_size_and_compression_in_ui(file_entry)
    
    self.window().ui.statusbar.showMessage("Replaced %s." % file_entry.name, 3000)
  
  def open_j3d_in_rarc(self):
    file_entry = self.ui.actionOpenRARCJ3D.data()
    
    j3d_name = os.path.splitext(file_entry.name)[0]
    
    data = fs.make_copy_data(file_entry.data)
    self.j3d_tab.import_j3d_by_data(data, j3d_name)
    
    self.window().set_tab_by_name("J3D Files")
  
  def replace_j3d_in_rarc(self):
    file_entry = self.ui.actionReplaceRARCJ3D.data()
    
    self.j3d_tab.j3d.save()
    
    file_entry.data = fs.make_copy_data(self.j3d_tab.j3d.data)
    file_entry.update_compression_flags_from_data()
    
    self.update_file_size_and_compression_in_ui(file_entry)
    
    self.window().ui.statusbar.showMessage("Replaced %s." % file_entry.name, 3000)
  
  def load_j3d_anim(self):
    file_entry = self.ui.actionLoadJ3DAnim.data()
    
    j3d_name = os.path.splitext(file_entry.name)[0]
    
    data = fs.make_copy_data(file_entry.data)
    self.j3d_tab.load_anim_by_data(data, j3d_name)
    
    self.window().set_tab_by_name("J3D Files")
  
  def add_file_to_rarc_by_path(self, file_path):
    parent_node = self.ui.actionAddRARCFile.data()
    
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
      file_data = BytesIO(f.read())
    file_size = fs.data_len(file_data)
    file_size_str = self.window().stringify_number(file_size)
    
    existing_file_names = [fe.name for fe in self.rarc.file_entries if not fe.is_dir]
    if file_name in existing_file_names:
      QMessageBox.warning(self, "File already exists", "Cannot add new file. The archive already contains a file named \"%s\".\n\nIf you wish to replace the existing file, right click on it in the files tree and select 'Replace File'." % file_name)
      return
    
    file_entry = self.rarc.add_new_file(file_name, file_data, parent_node)
    
    file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
    file_index = self.rarc.file_entries.index(file_entry)
    file_index_str = self.window().stringify_number(file_index, min_hex_chars=4)
    
    parent_dir_item = self.rarc_node_to_tree_widget_item.get(parent_node)
    file_item = QTreeWidgetItem([file_entry.name, "", file_index_str, file_id_str, file_size_str, ""])
    file_item.setFlags(file_item.flags() | Qt.ItemIsEditable)
    index_of_file_in_dir = parent_node.files.index(file_entry)
    parent_dir_item.insertChild(index_of_file_in_dir, file_item)
    
    self.rarc_file_entry_to_tree_widget_item[file_entry] = file_item
    self.rarc_tree_widget_item_to_file_entry[file_item] = file_entry
    
    self.update_file_size_and_compression_in_ui(file_entry)
    
    self.update_all_displayed_file_indexes_and_ids()
  
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
    
    self.update_all_displayed_file_indexes_and_ids()
  
  def delete_folder_in_rarc(self):
    node = self.ui.actionDeleteRARCFolder.data()
    
    if not self.window().confirm_delete(node.name, is_folder=True):
      return
    
    dir_entry = node.dir_entry
    
    self.rarc.delete_directory(dir_entry)
    
    self.remove_folder_from_files_tree(dir_entry)
    
    self.update_all_displayed_file_indexes_and_ids()
  
  def remove_folder_from_files_tree(self, dir_entry):
    dir_item = self.rarc_file_entry_to_tree_widget_item.get(dir_entry)
    parent_dir_item = self.rarc_node_to_tree_widget_item.get(dir_entry.parent_node)
    parent_dir_item.removeChild(dir_item)
    del self.rarc_file_entry_to_tree_widget_item[dir_entry]
    del self.rarc_tree_widget_item_to_file_entry[dir_item]
    
    # Recursively delete children from the dictionaries.
    for child_item in dir_item.takeChildren():
      child_file_entry = self.rarc_tree_widget_item_to_file_entry[child_item]
      if child_file_entry.is_dir:
        self.remove_folder_from_files_tree(child_file_entry)
      else:
        dir_item.removeChild(child_item)
        del self.rarc_file_entry_to_tree_widget_item[child_file_entry]
        del self.rarc_tree_widget_item_to_file_entry[child_item]
  
  
  def edit_rarc_files_tree_item_text(self, item, column):
    if (item.flags() & Qt.ItemIsEditable) == 0:
      return
    
    node = self.rarc_tree_widget_item_to_node.get(item)
    
    # Allow editing only certain columns.
    allowed_column_indexes = []
    allowed_column_indexes.append(self.rarc_col_name_to_index["File Name"])
    if node is not None:
      allowed_column_indexes.append(self.rarc_col_name_to_index["Folder Type"])
    else:
      if not self.rarc.keep_file_ids_synced_with_indexes:
        allowed_column_indexes.append(self.rarc_col_name_to_index["File ID"])
    if column in allowed_column_indexes: 
      self.ui.rarc_files_tree.editItem(item, column)
  
  def rarc_file_tree_item_changed(self, item, column):
    if column == self.rarc_col_name_to_index["File Name"]:
      self.change_rarc_file_name(item)
    elif column == self.rarc_col_name_to_index["Folder Type"]:
      self.change_rarc_node_type(item)
    elif column == self.rarc_col_name_to_index["File ID"]:
      self.change_rarc_file_id(item)
    elif column == self.rarc_col_name_to_index["Yaz0 Compressed"]:
      self.change_rarc_file_yaz0_compressed(item)
  
  def change_rarc_file_name(self, item):
    node = self.rarc_tree_widget_item_to_node.get(item)
    file_entry = self.rarc_tree_widget_item_to_file_entry.get(item)
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
      
      other_file_entry = next((fe for fe in self.rarc.file_entries if fe.name == new_file_name and not fe.is_dir), None)
      
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
    node = self.rarc_tree_widget_item_to_node.get(item)
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
    file_entry = self.rarc_tree_widget_item_to_file_entry.get(item)
    new_file_id_str = item.text(self.rarc_col_name_to_index["File ID"])
    
    if self.window().display_hexadecimal_numbers:
      hexadecimal_match = re.search(r"^\s*(?:0x)?([0-9a-f]+)\s*$", new_file_id_str, re.IGNORECASE)
      if hexadecimal_match:
        new_file_id = int(hexadecimal_match.group(1), 16)
      else:
        QMessageBox.warning(self, "Invalid file ID", "\"%s\" is not a valid hexadecimal number." % new_file_id_str)
        file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
        item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
        return
    else:
      decimal_match = re.search(r"^\s*(\d+)\s*$", new_file_id_str, re.IGNORECASE)
      if decimal_match:
        new_file_id = int(decimal_match.group(1))
      else:
        QMessageBox.warning(self, "Invalid file ID", "\"%s\" is not a valid decimal number." % new_file_id_str)
        file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
        item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
        return
    
    if new_file_id >= 0xFFFF:
      QMessageBox.warning(self, "Invalid file ID", "\"%s\" is too large to be a file ID. It must be in the range 0x0000-0xFFFE." % new_file_id_str)
      file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
      return
    
    other_file_entry = next((fe for fe in self.rarc.file_entries if fe.id == new_file_id), None)
    
    if other_file_entry == file_entry:
      # File ID not changed
      file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
      return
    
    if other_file_entry is not None:
      QMessageBox.warning(self, "Duplicate file ID", "The file ID you entered is already used by the file \"%s\"." % other_file_entry.name)
      file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
      item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
      return
    
    file_entry.id = new_file_id
    
    file_id_str = self.window().stringify_number(file_entry.id, min_hex_chars=4)
    item.setText(self.rarc_col_name_to_index["File ID"], file_id_str)
  
  def change_rarc_file_yaz0_compressed(self, item):
    file_entry = self.rarc_tree_widget_item_to_file_entry.get(item)
    checkstate = item.checkState(self.rarc_col_name_to_index["Yaz0 Compressed"])
    
    file_entry.update_compression_flags_from_data()
    if checkstate == Qt.Unchecked:
      if file_entry.type & RARCFileAttrType.COMPRESSED:
        if file_entry.type & RARCFileAttrType.YAZ0_COMPRESSED:
          file_entry.data = Yaz0.decompress(file_entry.data)
          file_entry.update_compression_flags_from_data()
        else: # Yay0
          QMessageBox.warning(self, "Yay0 not supported", "This file is currently Yay0 compressed. GCFT does not currently support decompressing Yay0.")
      else:
        # Already uncompressed. Do nothing.
        pass
    else: # Checked
      if file_entry.type & RARCFileAttrType.COMPRESSED:
        if file_entry.type & RARCFileAttrType.YAZ0_COMPRESSED:
          # Already Yaz0 compressed. Do nothing.
          pass
        else: # Yay0
          QMessageBox.warning(self, "Yay0 not supported", "This file is currently Yay0 compressed. GCFT does not currently support decompressing Yay0.")
      else:
        search_depth, should_pad_data = self.yaz0_tab.get_search_depth_and_should_pad()
        file_entry.data = Yaz0.compress(file_entry.data, search_depth=search_depth, should_pad_data=should_pad_data)
        file_entry.update_compression_flags_from_data()
    
    # Update the UI to match the file data.
    self.update_file_size_and_compression_in_ui(file_entry)
  
  
  def keyPressEvent(self, event):
    event.ignore()
    if event.matches(QKeySequence.Copy):
      if self.ui.rarc_files_tree.currentColumn() == self.rarc_col_name_to_index["File Name"]:
        item = self.ui.rarc_files_tree.currentItem()
        file_path = "%s/%s" % (item.parent().text(self.rarc_col_name_to_index["File Name"]), item.text(self.rarc_col_name_to_index["File Name"]))
        QApplication.instance().clipboard().setText(file_path)
        event.accept()
