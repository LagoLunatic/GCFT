
import os
import re
import traceback
from io import BytesIO
from fs_helpers import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from wwlib.gcm import GCM
from wwlib.texture_utils import ImageFormat, PaletteFormat
from gcft_ui.uic.ui_gcm_tab import Ui_GCMTab
from asset_dumper import AssetDumper

class GCMTab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_GCMTab()
    self.ui.setupUi(self)
    
    self.gcm = None
    self.ui.gcm_files_tree.setColumnWidth(0, 300)
    
    self.gcm_col_name_to_index = {}
    for col in range(self.ui.gcm_files_tree.columnCount()):
      column_name = self.ui.gcm_files_tree.headerItem().text(col)
      self.gcm_col_name_to_index[column_name] = col
    
    self.ui.export_gcm.setDisabled(True)
    self.ui.import_folder_over_gcm.setDisabled(True)
    self.ui.export_gcm_folder.setDisabled(True)
    self.ui.dump_all_gcm_textures.setDisabled(True)
    
    self.ui.import_gcm.clicked.connect(self.import_gcm)
    self.ui.export_gcm.clicked.connect(self.export_gcm)
    self.ui.import_folder_over_gcm.clicked.connect(self.import_folder_over_gcm)
    self.ui.export_gcm_folder.clicked.connect(self.export_gcm_folder)
    self.ui.dump_all_gcm_textures.clicked.connect(self.dump_all_gcm_textures)
    
    self.ui.gcm_files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.gcm_files_tree.customContextMenuRequested.connect(self.show_gcm_files_tree_context_menu)
    self.ui.gcm_files_tree.itemDoubleClicked.connect(self.edit_gcm_files_tree_item_text)
    self.ui.gcm_files_tree.itemChanged.connect(self.gcm_file_tree_item_text_changed)
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
    self.ui.actionOpenGCMDOL.triggered.connect(self.open_dol_in_gcm)
    self.ui.actionReplaceGCMDOL.triggered.connect(self.replace_dol_in_gcm)
    self.ui.actionAddGCMFolder.triggered.connect(self.add_folder_to_gcm)
    self.ui.actionDeleteGCMFolder.triggered.connect(self.delete_folder_in_gcm)
  
  
  def import_gcm(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="GCM", file_filter="GC ISO Files (*.iso *.gcm)"
    )
  
  def export_gcm(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_gcm_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="GCM", file_filter="GC ISO Files (*.iso *.gcm)"
    )
  
  def import_folder_over_gcm(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_folder_over_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="GCM"
    )
  
  def export_gcm_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_gcm_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="GCM"
    )
  
  def dump_all_gcm_textures(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.dump_all_gcm_textures_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="all GCM texture"
    )
  
  def extract_file_from_gcm(self):
    file = self.ui.actionExtractGCMFile.data()
    self.window().generic_do_gui_file_operation(
      op_callback=self.extract_file_from_gcm_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def replace_file_in_gcm(self):
    file = self.ui.actionReplaceGCMFile.data()
    self.window().generic_do_gui_file_operation(
      op_callback=self.replace_file_in_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file",
      default_file_name=file.name
    )
  
  def add_file_to_gcm(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.add_file_to_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="file"
    )
  
  
  def import_gcm_by_path(self, gcm_path):
    self.gcm = GCM(gcm_path)
    
    self.gcm.read_entire_disc()
    
    self.reload_gcm_files_tree()
  
  def reload_gcm_files_tree(self):
    self.ui.gcm_files_tree.clear()
    
    self.gcm_file_entry_to_tree_widget_item = {}
    self.gcm_tree_widget_item_to_file_entry = {}
    
    root_entry = self.gcm.file_entries[0]
    assert root_entry.file_path == "files"
    root_item = QTreeWidgetItem(["files", ""])
    self.ui.gcm_files_tree.addTopLevelItem(root_item)
    self.gcm_file_entry_to_tree_widget_item[root_entry] = root_item
    self.gcm_tree_widget_item_to_file_entry[root_item] = root_entry
    
    # Add data files.
    for file_entry in self.gcm.file_entries[1:]:
      self.add_gcm_file_entry_to_files_tree(file_entry)
    
    # Add system files.
    # (Note that the "sys" folder has no corresponding directory file entry because it is not really a directory.)
    sys_item = QTreeWidgetItem(["sys", ""])
    self.ui.gcm_files_tree.addTopLevelItem(sys_item)
    for file_entry in self.gcm.system_files:
      self.add_gcm_file_entry_to_files_tree(file_entry)
    
    # Expand the "files" and "sys" root entries by default.
    self.ui.gcm_files_tree.topLevelItem(0).setExpanded(True)
    self.ui.gcm_files_tree.topLevelItem(1).setExpanded(True)
    
    self.ui.export_gcm.setDisabled(False)
    self.ui.import_folder_over_gcm.setDisabled(False)
    self.ui.export_gcm_folder.setDisabled(False)
    self.ui.dump_all_gcm_textures.setDisabled(False)
  
  def add_gcm_file_entry_to_files_tree(self, file_entry):
    if file_entry.is_dir:
      file_size_str = ""
    else:
      file_size_str = self.window().stringify_number(file_entry.file_size)
    
    if file_entry.is_system_file:
      parent_item = self.ui.gcm_files_tree.topLevelItem(1)
      assert parent_item.text(0) == "sys"
    else:
      parent_item = self.gcm_file_entry_to_tree_widget_item[file_entry.parent]
    
    item = QTreeWidgetItem([file_entry.name, file_size_str])
    item.setFlags(item.flags() | Qt.ItemIsEditable)
    parent_item.addChild(item)
    self.gcm_file_entry_to_tree_widget_item[file_entry] = item
    self.gcm_tree_widget_item_to_file_entry[item] = file_entry
  
  def export_gcm_by_path(self, gcm_path):
    if os.path.realpath(self.gcm.iso_path) == os.path.realpath(gcm_path):
      raise Exception("Cannot export an ISO over the currently opened ISO. Please choose a different path.")
    
    generator = self.gcm.export_disc_to_iso_with_changed_files(gcm_path)
    max_val = len(self.gcm.files_by_path)
    
    self.window().start_progress_thread(
      generator, "Saving ISO", max_val,
      self.export_gcm_by_path_complete
    )
  
  def export_gcm_by_path_complete(self):
    QMessageBox.information(self, "GCM saved", "Successfully saved GCM.")
  
  def import_folder_over_gcm_by_path(self, folder_path):
    num_files_overwritten = self.gcm.import_all_files_from_disk(folder_path)
    
    if num_files_overwritten == 0:
      QMessageBox.warning(self, "No matching files found", "The selected folder does not contain any files matching the name and directory structure of files in the currently loaded GCM. No files imported.\n\nMake sure you're selecting the correct folder - it should be the folder with 'files' and 'sys' inside of it, not the 'files' folder itself.")
      return
    
    QMessageBox.information(self, "Folder imported", "Successfully overwrote %d files in the GCM from \"%s\"." % (num_files_overwritten, folder_path))
  
  def export_gcm_folder_by_path(self, folder_path):
    generator = self.gcm.export_disc_to_folder_with_changed_files(folder_path)
    max_val = len(self.gcm.files_by_path)
    
    self.window().start_progress_thread(
      generator, "Extracting files", max_val,
      self.export_gcm_folder_by_path_complete
    )
  
  def export_gcm_folder_by_path_complete(self):
    QMessageBox.information(self, "GCM extracted", "Successfully extracted GCM contents.")
  
  def dump_all_gcm_textures_by_path(self, folder_path):
    asset_dumper = AssetDumper()
    dumper_generator = asset_dumper.dump_all_textures_in_gcm(self.gcm, folder_path)
    max_val = len(asset_dumper.get_all_gcm_file_paths(self.gcm))
    
    self.window().start_texture_dumper_thread(asset_dumper, dumper_generator, max_val)
  
  
  def show_gcm_files_tree_context_menu(self, pos):
    if self.gcm is None:
      return
    
    item = self.ui.gcm_files_tree.itemAt(pos)
    if item is None:
      return
    
    file = self.gcm_tree_widget_item_to_file_entry.get(item)
    if file is None:
      return
    
    if file.is_dir:
      # TODO: Implement extracting/replacing folders
      menu = QMenu(self)
      menu.addAction(self.ui.actionAddGCMFile)
      self.ui.actionAddGCMFile.setData(file)
      menu.addAction(self.ui.actionAddGCMFolder)
      self.ui.actionAddGCMFolder.setData(file)
      if file.file_path != "files":
        menu.addAction(self.ui.actionDeleteGCMFolder)
        self.ui.actionDeleteGCMFolder.setData(file)
      menu.exec_(self.ui.gcm_files_tree.mapToGlobal(pos))
    else:
      menu = QMenu(self)
      
      basename, file_ext = os.path.splitext(file.name)
      if file_ext == ".bti" or file.file_path == "files/opening.bnr":
        menu.addAction(self.ui.actionOpenGCMImage)
        self.ui.actionOpenGCMImage.setData(file)
        
        menu.addAction(self.ui.actionReplaceGCMImage)
        self.ui.actionReplaceGCMImage.setData(file)
        if self.bti_tab.bti is None:
          self.ui.actionReplaceGCMImage.setDisabled(True)
        else:
          self.ui.actionReplaceGCMImage.setDisabled(False)
      elif file_ext == ".arc":
        menu.addAction(self.ui.actionOpenGCMRARC)
        self.ui.actionOpenGCMRARC.setData(file)
        
        menu.addAction(self.ui.actionReplaceGCMRARC)
        self.ui.actionReplaceGCMRARC.setData(file)
        if self.rarc_tab.rarc is None:
          self.ui.actionReplaceGCMRARC.setDisabled(True)
        else:
          self.ui.actionReplaceGCMRARC.setDisabled(False)
      elif file_ext == ".jpc":
        menu.addAction(self.ui.actionOpenGCMJPC)
        self.ui.actionOpenGCMJPC.setData(file)
        
        menu.addAction(self.ui.actionReplaceGCMJPC)
        self.ui.actionReplaceGCMJPC.setData(file)
        if self.jpc_tab.jpc is None:
          self.ui.actionReplaceGCMJPC.setDisabled(True)
        else:
          self.ui.actionReplaceGCMJPC.setDisabled(False)
      elif file.file_path == "sys/main.dol":
        menu.addAction(self.ui.actionOpenGCMDOL)
        self.ui.actionOpenGCMDOL.setData(file)
        
        menu.addAction(self.ui.actionReplaceGCMDOL)
        self.ui.actionReplaceGCMDOL.setData(file)
        if self.dol_tab.dol is None:
          self.ui.actionReplaceGCMDOL.setDisabled(True)
        else:
          self.ui.actionReplaceGCMDOL.setDisabled(False)
      
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
  
  def update_changed_file_size_in_gcm(self, file):
    data = self.gcm.get_changed_file_data(file.file_path)
    file_size_str = self.window().stringify_number(data_len(data))
    item = self.gcm_file_entry_to_tree_widget_item[file]
    item.setText(self.gcm_col_name_to_index["File Size"], file_size_str)
  
  def replace_file_in_gcm_by_path(self, file_path):
    file = self.ui.actionReplaceGCMFile.data()
    
    with open(file_path, "rb") as f:
      data = BytesIO(f.read())
    
    if file.file_path in ["sys/boot.bin", "sys/bi2.bin"] and data_len(data) != file.file_size:
      QMessageBox.warning(self, "Cannot change this file's size", "The size of boot.bin and bi2.bin cannot be changed.")
      return
    
    self.gcm.changed_files[file.file_path] = data
    
    self.update_changed_file_size_in_gcm(file)
  
  def delete_file_in_gcm(self):
    file_entry = self.ui.actionDeleteGCMFile.data()
    
    if not self.window().confirm_delete(file_entry.name):
      return
    
    dir_entry = file_entry.parent
    
    self.gcm.delete_file(file_entry)
    
    dir_item = self.gcm_file_entry_to_tree_widget_item[dir_entry]
    file_item = self.gcm_file_entry_to_tree_widget_item[file_entry]
    dir_item.removeChild(file_item)
    del self.gcm_file_entry_to_tree_widget_item[file_entry]
    del self.gcm_tree_widget_item_to_file_entry[file_item]
  
  def delete_folder_in_gcm(self):
    dir_entry = self.ui.actionDeleteGCMFolder.data()
    
    if not self.window().confirm_delete(dir_entry.name):
      return
    
    parent_dir_entry = dir_entry.parent
    
    self.gcm.delete_directory(dir_entry)
    
    parent_dir_item = self.gcm_file_entry_to_tree_widget_item[parent_dir_entry]
    dir_item = self.gcm_file_entry_to_tree_widget_item[dir_entry]
    parent_dir_item.removeChild(dir_item)
    del self.gcm_file_entry_to_tree_widget_item[dir_entry]
    del self.gcm_tree_widget_item_to_file_entry[dir_item]
  
  def open_rarc_in_gcm(self):
    file_entry = self.ui.actionOpenGCMRARC.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = make_copy_data(data)
    
    rarc_name = os.path.splitext(file_entry.name)[0]
    
    self.rarc_tab.import_rarc_by_data(data, rarc_name)
    
    self.window().set_tab_by_name("RARC Archives")
  
  def replace_rarc_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMRARC.data()
    
    self.rarc_tab.rarc.save_changes()
    data = make_copy_data(self.rarc_tab.rarc.data)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    self.update_changed_file_size_in_gcm(file_entry)
  
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
    
    self.bti_tab.import_bti_by_data(data, bti_name)
    
    self.window().set_tab_by_name("BTI Images")
  
  def replace_image_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMImage.data()
    
    self.bti_tab.bti.save_changes()
    data = make_copy_data(self.bti_tab.bti.data)
    
    if file_entry.file_path == "files/opening.bnr":
      if self.bti_tab.bti.image_format != ImageFormat.RGB5A3 or self.bti_tab.bti.width != 96 or self.bti_tab.bti.height != 32 or data_len(self.bti_tab.bti.image_data) != 0x1800:
        QMessageBox.warning(self, "Invalid banner image", "Invalid banner image. Banner images must be exactly 96x32 pixels in size and use the RGB5A3 image format.")
        return
      
      orig_banner_data = self.gcm.get_changed_file_data(file_entry.file_path)
      image_data_bytes = read_bytes(self.bti_tab.bti.image_data, 0x00, 0x1800)
      data = make_copy_data(orig_banner_data)
      write_bytes(data, 0x20, image_data_bytes)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    self.update_changed_file_size_in_gcm(file_entry)
  
  def open_jpc_in_gcm(self):
    file_entry = self.ui.actionOpenGCMJPC.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = make_copy_data(data)
    
    jpc_name = os.path.splitext(file_entry.name)[0]
    
    self.jpc_tab.import_jpc_by_data(data, jpc_name)
    
    self.window().set_tab_by_name("JPC Particle Archives")
  
  def replace_jpc_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMJPC.data()
    
    self.jpc_tab.jpc.save_changes()
    data = make_copy_data(self.jpc_tab.jpc.data)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    self.update_changed_file_size_in_gcm(file_entry)
  
  def open_dol_in_gcm(self):
    file_entry = self.ui.actionOpenGCMDOL.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = make_copy_data(data)
    
    dol_name = os.path.splitext(file_entry.name)[0]
    
    self.dol_tab.import_dol_by_data(data, dol_name)
    
    self.window().set_tab_by_name("DOL Executables")
  
  def replace_dol_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMDOL.data()
    
    self.dol_tab.dol.save_changes()
    data = make_copy_data(self.dol_tab.dol.data)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    self.update_changed_file_size_in_gcm(file_entry)
  
  def add_file_to_gcm_by_path(self, file_path):
    dir_entry = self.ui.actionAddGCMFile.data()
    
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
      file_data = BytesIO(f.read())
    file_size = data_len(file_data)
    file_size_str = self.window().stringify_number(file_size)
    
    gcm_file_path = dir_entry.file_path + "/" + file_name
    if gcm_file_path.lower() in self.gcm.files_by_path_lowercase:
      QMessageBox.warning(self, "File already exists", "Cannot add new file. The selected folder already contains a file named \"%s\".\n\nIf you wish to replace the existing file, right click on it in the files tree and select 'Replace File'." % file_name)
      return
    file_entry = self.gcm.add_new_file(gcm_file_path, file_data)
    
    dir_item = self.gcm_file_entry_to_tree_widget_item[dir_entry]
    file_item = QTreeWidgetItem([file_name, file_size_str])
    dir_item.addChild(file_item)
    self.gcm_file_entry_to_tree_widget_item[file_entry] = file_item
    self.gcm_tree_widget_item_to_file_entry[file_item] = file_entry
  
  def add_folder_to_gcm(self):
    parent_dir_entry = self.ui.actionAddGCMFolder.data()
    
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
    
    gcm_dir_path = parent_dir_entry.file_path + "/" + dir_name
    if gcm_dir_path.lower() in self.gcm.dirs_by_path_lowercase:
      QMessageBox.warning(self, "Directory already exists", "Cannot add new folder. A folder named \"%s\" already exists in the specified location." % dir_name)
      return
    dir_entry = self.gcm.add_new_directory(gcm_dir_path)
    
    self.add_gcm_file_entry_to_files_tree(dir_entry)
  
  
  def edit_gcm_files_tree_item_text(self, item, column):
    if (item.flags() & Qt.ItemIsEditable) == 0:
      return
    
    file = self.gcm_tree_widget_item_to_file_entry.get(item)
    if file is None:
      return
    if file.is_system_file:
      return
    
    # Allow editing only certain columns.
    if column in [self.gcm_col_name_to_index["File Name"]]: 
      self.ui.gcm_files_tree.editItem(item, column)
  
  def gcm_file_tree_item_text_changed(self, item, column):
    if column == self.gcm_col_name_to_index["File Name"]:
      self.change_gcm_file_name(item)
  
  def change_gcm_file_name(self, item):
    file_entry = self.gcm_tree_widget_item_to_file_entry.get(item)
    new_file_name = item.text(self.gcm_col_name_to_index["File Name"])
    
    if len(new_file_name) == 0:
      QMessageBox.warning(self, "Invalid file name", "File name cannot be empty.")
      item.setText(self.gcm_col_name_to_index["File Name"], file_entry.name)
      return
    
    other_file_entry = next((fe for fe in file_entry.parent.children if fe.name == new_file_name), None)
    if other_file_entry == file_entry:
      # File name not changed
      return
    
    if other_file_entry is not None:
      QMessageBox.warning(self, "Duplicate file name", "The file name you entered is already used by another file or folder in this directory.")
      item.setText(self.gcm_col_name_to_index["File Name"], file_entry.name)
      return
  
    file_entry.name = new_file_name
    
    item.setText(self.gcm_col_name_to_index["File Name"], new_file_name)
  
  
  def keyPressEvent(self, event):
    event.ignore()
    if event.matches(QKeySequence.Copy):
      if self.ui.gcm_files_tree.currentColumn() == self.gcm_col_name_to_index["File Name"]:
        item = self.ui.gcm_files_tree.currentItem()
        if item not in self.gcm_tree_widget_item_to_file_entry:
          # The sys folder is not real.
          return
        file_entry = self.gcm_tree_widget_item_to_file_entry[item]
        file_path = file_entry.file_path
        QApplication.instance().clipboard().setText(file_path)
        event.accept()
