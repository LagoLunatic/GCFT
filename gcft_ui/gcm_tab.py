
import os
import re
from io import BytesIO
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.gcm import GCM, GCMBaseFile
from gclib.texture_utils import ImageFormat

from gcft_ui.gcft_common import RecursiveFilterProxyModel
from asset_dumper import AssetDumper

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_gcm_tab import Ui_GCMTab
else:
  Ui_GCMTab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "uic", "ui_gcm_tab.ui"))

class GCMTab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_GCMTab()
    self.ui.setupUi(self)
    
    self.gcm = None
    
    self.column_names = [
      "File Name",
      "File Size",
    ]
    
    self.model = QStandardItemModel()
    self.model.setHorizontalHeaderLabels(self.column_names)
    self.model.setColumnCount(len(self.column_names))
    self.proxy = RecursiveFilterProxyModel()
    self.proxy.setSourceModel(self.model)
    self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    
    self.ui.gcm_files_tree.setModel(self.proxy)
    self.selection_model = self.ui.gcm_files_tree.selectionModel()
    
    self.ui.filter.textChanged.connect(self.filter_rows)
    
    self.ui.export_gcm.setDisabled(True)
    self.ui.replace_all_files_in_gcm.setDisabled(True)
    self.ui.extract_all_files_from_gcm.setDisabled(True)
    self.ui.dump_all_gcm_textures.setDisabled(True)
    self.ui.add_replace_files_from_folder.setDisabled(True)
    
    self.ui.import_gcm.clicked.connect(self.import_gcm)
    self.ui.export_gcm.clicked.connect(self.export_gcm)
    self.ui.replace_all_files_in_gcm.clicked.connect(self.replace_all_files_in_gcm)
    self.ui.extract_all_files_from_gcm.clicked.connect(self.extract_all_files_from_gcm)
    self.ui.dump_all_gcm_textures.clicked.connect(self.dump_all_gcm_textures)
    self.ui.add_replace_files_from_folder.clicked.connect(self.add_replace_gcm_files_from_folder)
    
    self.ui.gcm_files_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.ui.gcm_files_tree.customContextMenuRequested.connect(self.show_gcm_files_tree_context_menu)
    self.model.dataChanged.connect(self.gcm_file_tree_item_text_changed)
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
    self.ui.actionExtractAllFilesFromGCMFolder.triggered.connect(self.extract_all_files_from_gcm_folder)
    self.ui.actionReplaceAllFilesInGCMFolder.triggered.connect(self.replace_all_files_in_gcm_folder)
    self.ui.actionAddReplaceFilesForFolder.triggered.connect(self.add_replace_gcm_folder_files_from_folder)
  
  
  def import_gcm(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_gcm_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="GCM", file_filters=["GC ISO Files (*.iso *.gcm)"],
    )
  
  def export_gcm(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_gcm_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="GCM", file_filters=["GC ISO Files (*.iso *.gcm)"],
    )
  
  def replace_all_files_in_gcm(self):
    self.ui.actionReplaceAllFilesInGCMFolder.setData(None) # All files
    self.window().generic_do_gui_file_operation(
      op_callback=self.replace_all_files_in_gcm_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="GCM"
    )
  
  def replace_all_files_in_gcm_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.replace_all_files_in_gcm_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="GCM"
    )
  
  def extract_all_files_from_gcm(self):
    self.ui.actionExtractAllFilesFromGCMFolder.setData(None) # All files
    self.window().generic_do_gui_file_operation(
      op_callback=self.extract_all_files_from_gcm_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="GCM"
    )
  
  def extract_all_files_from_gcm_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.extract_all_files_from_gcm_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="GCM"
    )
  
  def dump_all_gcm_textures(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.dump_all_gcm_textures_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="all GCM texture"
    )
  
  def add_replace_gcm_files_from_folder(self):
    self.ui.actionAddReplaceFilesForFolder.setData(None) # All files
    self.window().generic_do_gui_file_operation(
      op_callback=self.add_replace_files_from_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="GCM"
    )
  
  def add_replace_gcm_folder_files_from_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.add_replace_files_from_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="GCM"
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
    self.model.removeRows(0, self.model.rowCount())
    
    root_entry = self.gcm.file_entries[0]
    assert root_entry.file_path == "files"
    root_item = QStandardItem("files")
    root_item.setData(root_entry)
    root_item.setEditable(False)
    self.model.appendRow(root_item)
    
    # Add data files.
    for file_entry in self.gcm.file_entries[1:]:
      self.add_gcm_file_entry_to_files_tree(file_entry)
    
    # Add system files.
    # (Note that the "sys" folder has no corresponding directory file entry because it is not really a directory.)
    sys_item = QStandardItem("sys")
    sys_item.setData("__systemfile")
    sys_item.setEditable(False)
    self.model.appendRow(sys_item)
    
    # Add system files.
    for file_entry in self.gcm.system_files:
      self.add_gcm_file_entry_to_files_tree(file_entry)
    
    self.ui.export_gcm.setDisabled(False)
    self.ui.replace_all_files_in_gcm.setDisabled(False)
    self.ui.extract_all_files_from_gcm.setDisabled(False)
    self.ui.dump_all_gcm_textures.setDisabled(False)
    self.ui.add_replace_files_from_folder.setDisabled(False)
    
    self.ui.gcm_files_tree.setColumnWidth(0, 300)
    
    self.filter_rows()
    self.expand_item(root_item)
    self.expand_item(sys_item)
  
  def add_gcm_file_entry_to_files_tree(self, file_entry: GCMBaseFile):
    if file_entry.is_system_file:
      match_value = "__systemfile"
    else:
      match_value = file_entry.parent
    parent_item = self.find_item_by_data(0, match_value)
    assert parent_item is not None
    
    name_item = QStandardItem(file_entry.name)
    name_item.setData(file_entry)
    if file_entry.is_system_file:
      name_item.setEditable(False)
    else:
      name_item.setEditable(True)
    
    if file_entry.is_dir:
      file_size_str = ""
    else:
      file_size = self.gcm.get_changed_file_size(file_entry.file_path)
      file_size_str = self.window().stringify_number(file_size)
    
    size_item = QStandardItem(file_size_str)
    size_item.setData(file_entry)
    size_item.setEditable(False)
    
    parent_item.appendRow([name_item, size_item])
    
    return name_item
  
  def expand_item(self, item: QStandardItem):
    self.ui.gcm_files_tree.expand(self.proxy.mapFromSource(item.index()))
  
  def find_item_by_data(self, column, value):
    matched_indexes = self.model.match(
      self.model.index(0, column),
      Qt.ItemDataRole.UserRole + 1, # Equivalent to item.data()
      value,
      1,
      Qt.MatchFlag.MatchRecursive
    )
    assert len(matched_indexes) == 1
    return self.model.itemFromIndex(matched_indexes[0])
  
  def filter_rows(self):
    query = self.ui.filter.text()
    self.proxy.setFilterFixedString(query)
  
  
  def is_banner_filename(self, filename):
    match = re.search(r"\.bnr(?:$| |\.)", filename, re.I)
    if match:
      return True
    return False
  
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
  
  def replace_all_files_in_gcm_folder_by_path(self, folder_path):
    base_dir = self.ui.actionReplaceAllFilesInGCMFolder.data()
    replace_paths, add_paths = self.gcm.collect_files_to_replace_and_add_from_disk(folder_path, base_dir=base_dir)
    
    if len(replace_paths) == 0:
      if base_dir is None:
        error_message = ("The selected folder does not contain any files matching the name and directory structure of files in the currently loaded GCM. No files imported.\n\n"
          "Make sure you're selecting the correct folder - it should be the folder with 'files' and 'sys' inside of it, not the 'files' folder itself.")
      else:
        error_message = ("The selected folder does not contain any files matching the name and directory structure of files in the currently selected GCM folder. No files imported.\n\n"
          f"Make sure you're selecting the correct folder.")
      QMessageBox.warning(self, "No matching files found", error_message)
      return
    
    message = "Importing files from this folder will replace %d existing files in the GCM.\n\nAre you sure you want to proceed?" % (len(replace_paths))
    response = QMessageBox.question(self, 
      "Confirm replace files",
      message,
      QMessageBox.Cancel | QMessageBox.Yes,
      QMessageBox.Cancel
    )
    if response != QMessageBox.Yes:
      return
    
    generator = self.gcm.import_files_from_disk_by_paths(folder_path, replace_paths, [], base_dir=base_dir)
    max_val = len(replace_paths)
    
    self.window().start_progress_thread(
      generator, "Replacing files", max_val,
      self.replace_all_files_in_gcm_by_path_complete
    )
  
  def replace_all_files_in_gcm_by_path_complete(self):
    QMessageBox.information(self, "Files replaced", "Successfully overwrote all matching files in the GCM.")
    
    for file_path in self.gcm.changed_files:
      file = self.gcm.files_by_path[file_path]
      self.update_changed_file_size_in_gcm(file)
  
  def extract_all_files_from_gcm_folder_by_path(self, folder_path):
    base_dir = self.ui.actionExtractAllFilesFromGCMFolder.data()
    generator = self.gcm.export_disc_to_folder_with_changed_files(folder_path, base_dir=base_dir)
    max_val = self.gcm.get_num_files(base_dir)
    
    self.window().start_progress_thread(
      generator, "Extracting files", max_val,
      self.extract_all_files_from_gcm_by_path_complete
    )
  
  def extract_all_files_from_gcm_by_path_complete(self):
    QMessageBox.information(self, "GCM extracted", "Successfully extracted GCM contents.")
  
  def dump_all_gcm_textures_by_path(self, folder_path):
    asset_dumper = AssetDumper()
    dumper_generator = asset_dumper.dump_all_textures_in_gcm(self.gcm, folder_path)
    max_val = len(asset_dumper.get_all_gcm_file_paths(self.gcm))
    
    self.window().start_texture_dumper_thread(asset_dumper, dumper_generator, max_val)
  
  def add_replace_files_from_folder_by_path(self, folder_path):
    base_dir = self.ui.actionExtractAllFilesFromGCMFolder.data()
    
    root_names = set(os.listdir(folder_path))
    if len(root_names) == 0:
      QMessageBox.warning(self, "Invalid folder structure", "Input folder is empty. No files to import.")
      return
    
    if base_dir is None:
      # If we're importing over the GCM root, first ensure the input folder's directory structure is correct.
      if root_names & set(["files", "sys"]) != root_names:
        QMessageBox.warning(self, "Invalid folder structure", "Input folder contains unknown files or folders in its root directory.\n\nMake sure you're selecting the correct folder - it should be the folder with 'files' and 'sys' inside of it, not the 'files' folder itself.")
        return
      if not all(os.path.isdir(os.path.join(folder_path, name)) for name in root_names):
        QMessageBox.warning(self, "Invalid folder structure", "Input folder contains files in place of folders in its root directory.\n\nMake sure you're selecting the correct folder - it should be the folder with 'files' and 'sys' inside of it, not the 'files' folder itself.")
        return
    
    replace_paths, add_paths = self.gcm.collect_files_to_replace_and_add_from_disk(folder_path, base_dir=base_dir)
    
    if len(replace_paths) == 0 and len(add_paths) == 0:
      error_message = ("The selected folder does not contain any files, only directories.")
      QMessageBox.warning(self, "No matching files found", error_message)
      return
    
    message = "Importing files from this folder will replace %d existing files and add %d new files.\n\nAre you sure you want to proceed?" % (len(replace_paths), len(add_paths))
    response = QMessageBox.question(self, 
      "Confirm import files",
      message,
      QMessageBox.Cancel | QMessageBox.Yes,
      QMessageBox.Cancel
    )
    if response != QMessageBox.Yes:
      return
    
    generator = self.gcm.import_files_from_disk_by_paths(folder_path, replace_paths, add_paths, base_dir=base_dir)
    max_val = len(replace_paths) + len(add_paths)
    
    self.window().start_progress_thread(
      generator, "Importing files", max_val,
      self.add_replace_files_from_folder_by_path_complete
    )
  
  def add_replace_files_from_folder_by_path_complete(self):
    QMessageBox.information(self, "Files imported", "Successfully imported all files from the input folder.\n\nDon't forget to use 'Export GCM' to save the modified GCM.")
    
    # Refresh the UI so that new and changed files are reflected visually.
    # Need to recalculate the file entries list first so any newly added files actually appear in it.
    self.gcm.recalculate_file_entry_indexes()
    # Then refresh the tree in the UI.
    self.reload_gcm_files_tree()
  
  
  def show_gcm_files_tree_context_menu(self, pos):
    if self.gcm is None:
      return
    
    index = self.ui.gcm_files_tree.indexAt(pos)
    if not index.isValid():
      return
    item = self.model.itemFromIndex(self.proxy.mapToSource(index))
    if item is None:
      return
    file = item.data()
    if not isinstance(file, GCMBaseFile):
      return
    
    if file.is_dir:
      menu = QMenu(self)
      
      menu.addAction(self.ui.actionAddGCMFile)
      self.ui.actionAddGCMFile.setData(file)
      menu.addAction(self.ui.actionAddGCMFolder)
      self.ui.actionAddGCMFolder.setData(file)
      if file.file_path != "files":
        menu.addAction(self.ui.actionDeleteGCMFolder)
        self.ui.actionDeleteGCMFolder.setData(file)
      menu.addAction(self.ui.actionExtractAllFilesFromGCMFolder)
      self.ui.actionExtractAllFilesFromGCMFolder.setData(file)
      menu.addAction(self.ui.actionReplaceAllFilesInGCMFolder)
      self.ui.actionReplaceAllFilesInGCMFolder.setData(file)
      menu.addAction(self.ui.actionAddReplaceFilesForFolder)
      self.ui.actionAddReplaceFilesForFolder.setData(file)
      
      menu.exec_(self.ui.gcm_files_tree.mapToGlobal(pos))
    else:
      menu = QMenu(self)
      
      basename, file_ext = os.path.splitext(file.name)
      
      if file_ext == ".bti" or self.is_banner_filename(file.name):
        menu.addAction(self.ui.actionOpenGCMImage)
        self.ui.actionOpenGCMImage.setData(file)
        
        menu.addAction(self.ui.actionReplaceGCMImage)
        self.ui.actionReplaceGCMImage.setData(file)
        if self.bti_tab.bti is None:
          self.ui.actionReplaceGCMImage.setDisabled(True)
        else:
          self.ui.actionReplaceGCMImage.setDisabled(False)
      elif self.gcm.check_file_is_rarc(file.file_path):
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
    file: GCMBaseFile = self.ui.actionExtractGCMFile.data()
    
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
    file_size = self.gcm.get_changed_file_size(file.file_path)
    file_size_str = self.window().stringify_number(file_size)
    item = self.find_item_by_data(self.column_names.index("File Size"), file)
    item.setText(file_size_str)
  
  def replace_file_in_gcm_by_path(self, file_path):
    file = self.ui.actionReplaceGCMFile.data()
    
    with open(file_path, "rb") as f:
      data = BytesIO(f.read())
    
    if file.file_path in ["sys/boot.bin", "sys/bi2.bin"] and fs.data_len(data) != file.file_size:
      QMessageBox.warning(self, "Cannot change this file's size", "The size of boot.bin and bi2.bin cannot be changed.")
      return
    
    self.gcm.changed_files[file.file_path] = data
    
    self.update_changed_file_size_in_gcm(file)
    
    self.window().ui.statusbar.showMessage("Replaced %s." % file.file_path, 3000)
  
  def delete_file_in_gcm(self):
    file_entry = self.ui.actionDeleteGCMFile.data()
    
    if not self.window().confirm_delete(file_entry.name):
      return
    
    self.gcm.delete_file(file_entry)
    
    item = self.find_item_by_data(0, file_entry)
    assert self.model.removeRow(item.row(), item.parent().index())
  
  def delete_folder_in_gcm(self):
    dir_entry = self.ui.actionDeleteGCMFolder.data()
    
    if not self.window().confirm_delete(dir_entry.name):
      return
    
    parent_dir_entry = dir_entry.parent
    
    self.gcm.delete_directory(dir_entry)
    
    item = self.find_item_by_data(0, dir_entry)
    assert self.model.removeRow(item.row(), item.parent().index())
  
  def open_rarc_in_gcm(self):
    file_entry = self.ui.actionOpenGCMRARC.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = fs.make_copy_data(data)
    
    rarc_name = os.path.splitext(file_entry.name)[0]
    
    self.rarc_tab.import_rarc_by_data(data, rarc_name)
    
    self.window().set_tab_by_name("RARC Archives")
  
  def replace_rarc_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMRARC.data()
    
    self.rarc_tab.rarc.save_changes()
    data = fs.make_copy_data(self.rarc_tab.rarc.data)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    self.update_changed_file_size_in_gcm(file_entry)
    
    self.window().ui.statusbar.showMessage("Replaced %s." % file_entry.file_path, 3000)
  
  def open_image_in_gcm(self):
    file_entry = self.ui.actionOpenGCMImage.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = fs.make_copy_data(data)
    
    if self.is_banner_filename(file_entry.name):
      bti_name = file_entry.name
      self.bti_tab.import_bti_from_bnr_by_data(data, bti_name)
    else:
      bti_name = os.path.splitext(file_entry.name)[0]
      self.bti_tab.import_bti_by_data(data, bti_name)
    
    self.window().set_tab_by_name("BTI Images")
  
  def replace_image_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMImage.data()
    
    self.bti_tab.bti.save_changes()
    data = fs.make_copy_data(self.bti_tab.bti.data)
    
    if self.is_banner_filename(file_entry.name):
      if self.bti_tab.bti.image_format != ImageFormat.RGB5A3 or self.bti_tab.bti.width != 96 or self.bti_tab.bti.height != 32 or fs.data_len(self.bti_tab.bti.image_data) != 0x1800:
        QMessageBox.warning(self, "Invalid banner image", "Invalid banner image. Banner images must be exactly 96x32 pixels in size and use the RGB5A3 image format.")
        return
      
      orig_banner_data = self.gcm.get_changed_file_data(file_entry.file_path)
      image_data_bytes = fs.read_bytes(self.bti_tab.bti.image_data, 0x00, 0x1800)
      data = fs.make_copy_data(orig_banner_data)
      fs.write_bytes(data, 0x20, image_data_bytes)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    self.update_changed_file_size_in_gcm(file_entry)
    
    self.window().ui.statusbar.showMessage("Replaced %s." % file_entry.file_path, 3000)
  
  def open_jpc_in_gcm(self):
    file_entry = self.ui.actionOpenGCMJPC.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = fs.make_copy_data(data)
    
    jpc_name = os.path.splitext(file_entry.name)[0]
    
    self.jpc_tab.import_jpc_by_data(data, jpc_name)
    
    self.window().set_tab_by_name("JPC Particle Archives")
  
  def replace_jpc_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMJPC.data()
    
    self.jpc_tab.jpc.save_changes()
    data = fs.make_copy_data(self.jpc_tab.jpc.data)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    self.update_changed_file_size_in_gcm(file_entry)
    
    self.window().ui.statusbar.showMessage("Replaced %s." % file_entry.file_path, 3000)
  
  def open_dol_in_gcm(self):
    file_entry = self.ui.actionOpenGCMDOL.data()
    
    data = self.gcm.get_changed_file_data(file_entry.file_path)
    data = fs.make_copy_data(data)
    
    dol_name = os.path.splitext(file_entry.name)[0]
    
    self.dol_tab.import_dol_by_data(data, dol_name)
    
    self.window().set_tab_by_name("DOL Executables")
  
  def replace_dol_in_gcm(self):
    file_entry = self.ui.actionReplaceGCMDOL.data()
    
    self.dol_tab.dol.save_changes()
    data = fs.make_copy_data(self.dol_tab.dol.data)
    
    self.gcm.changed_files[file_entry.file_path] = data
    
    self.update_changed_file_size_in_gcm(file_entry)
    
    self.window().ui.statusbar.showMessage("Replaced %s." % file_entry.file_path, 3000)
  
  def add_file_to_gcm_by_path(self, file_path):
    dir_entry = self.ui.actionAddGCMFile.data()
    
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
      file_data = BytesIO(f.read())
    file_size = fs.data_len(file_data)
    file_size_str = self.window().stringify_number(file_size)
    
    gcm_file_path = dir_entry.file_path + "/" + file_name
    if gcm_file_path.lower() in self.gcm.files_by_path_lowercase:
      QMessageBox.warning(self, "File already exists", "Cannot add new file. The selected folder already contains a file named \"%s\".\n\nIf you wish to replace the existing file, right click on it in the files tree and select 'Replace File'." % file_name)
      return
    file_entry = self.gcm.add_new_file(gcm_file_path, file_data)
    
    name_item = self.add_gcm_file_entry_to_files_tree(file_entry)
    
    # Select the newly added entry.
    self.selection_model.reset()
    new_index = self.proxy.mapFromSource(name_item.index())
    self.selection_model.setCurrentIndex(new_index, QItemSelectionModel.SelectionFlag.Select)
  
  def add_folder_to_gcm(self):
    parent_dir_entry = self.ui.actionAddGCMFolder.data()
    
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
    
    gcm_dir_path = parent_dir_entry.file_path + "/" + dir_name
    if gcm_dir_path.lower() in self.gcm.dirs_by_path_lowercase:
      QMessageBox.warning(self, "Directory already exists", "Cannot add new folder. A folder named \"%s\" already exists in the specified location." % dir_name)
      return
    dir_entry = self.gcm.add_new_directory(gcm_dir_path)
    
    name_item = self.add_gcm_file_entry_to_files_tree(dir_entry)
    
    # Select the newly added entry.
    self.selection_model.reset()
    new_index = self.proxy.mapFromSource(name_item.index())
    self.selection_model.setCurrentIndex(new_index, QItemSelectionModel.SelectionFlag.Select)
  
  
  def gcm_file_tree_item_text_changed(self, top_left_index: QModelIndex, bottom_right_index: QModelIndex, roles: list[int]):
    if top_left_index.column() == self.column_names.index("File Name"):
      item = self.model.itemFromIndex(top_left_index)
      self.change_gcm_file_name(item)
  
  def change_gcm_file_name(self, item: QStandardItem):
    file_entry: GCMBaseFile = item.data()
    new_file_name = item.text()
    
    try:
      self.gcm.rename_file_or_directory(file_entry, new_file_name)
    except Exception as e:
      QMessageBox.warning(self, "Invalid file name", str(e))
      item.setText(file_entry.name) # Revert changed file name in the GUI
      return
    
    item.setText(new_file_name)
  
  
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
      file_entry = item.data()
      if not isinstance(file_entry, GCMBaseFile):
        return
      
      file_path = file_entry.file_path
      
      QApplication.clipboard().setText(file_path)
      event.accept()
