
import os
import re
from io import BytesIO
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.dol import DOL

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from gcft_ui.main_window import GCFTWindow

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_dol_tab import Ui_DOLTab
else:
  Ui_DOLTab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "dol_tab.ui"))

class DOLTab(QWidget):
  gcft_window: 'GCFTWindow'
  
  def __init__(self):
    super().__init__()
    self.ui = Ui_DOLTab()
    self.ui.setupUi(self)
    
    self.dol: DOL | None = None
    self.dolname = None
    
    self.column_names = [
      "Section Name",
      "Offset",
      "RAM Address",
      "Size",
    ]
    
    self.model = QStandardItemModel()
    self.model.setHorizontalHeaderLabels(self.column_names)
    self.model.setColumnCount(len(self.column_names))
    
    self.ui.dol_sections_tree.setModel(self.model)
    
    self.ui.export_dol.setDisabled(True)
    self.ui.convert_from_dol_offset.setDisabled(True)
    self.ui.convert_from_dol_address.setDisabled(True)
    self.ui.dol_offset.setDisabled(True)
    self.ui.dol_address.setDisabled(True)
    
    self.ui.import_dol.clicked.connect(self.import_dol)
    self.ui.export_dol.clicked.connect(self.export_dol)
    self.ui.convert_from_dol_offset.clicked.connect(self.convert_from_dol_offset)
    self.ui.convert_from_dol_address.clicked.connect(self.convert_from_dol_address)
    self.ui.dol_offset.returnPressed.connect(self.convert_from_dol_offset)
    self.ui.dol_address.returnPressed.connect(self.convert_from_dol_address)
  
  
  def import_dol(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.import_dol_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="DOL executable", file_filters=["DOL Executables (*.dol)"],
    )
  
  def export_dol(self):
    dol_name = self.dol_name + ".dol"
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_dol_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="DOL executable", file_filters=["DOL Executables (*.dol)"],
      default_file_name=dol_name
    )
  
  
  def import_dol_by_path(self, dol_path):
    with open(dol_path, "rb") as f:
      data = BytesIO(f.read())
    
    dol_name = os.path.splitext(os.path.basename(dol_path))[0]
    
    self.import_dol_by_data(data, dol_name)
  
  def import_dol_by_data(self, data, dol_name):
    self.dol = DOL()
    self.dol.read(data)
    
    self.dol_name = dol_name
    
    self.reload_dol_sections_tree()
    
    self.ui.export_dol.setDisabled(False)
    self.ui.convert_from_dol_offset.setDisabled(False)
    self.ui.convert_from_dol_address.setDisabled(False)
    self.ui.dol_offset.setDisabled(False)
    self.ui.dol_address.setDisabled(False)
  
  def reload_dol_sections_tree(self):
    assert self.dol is not None
    
    self.model.removeRows(0, self.model.rowCount())
    
    for section_index, section in enumerate(self.dol.sections):
      if section_index < DOL.TEXT_SECTION_COUNT:
        section_name = ".text%d" % section_index
      else:
        section_name = ".data%d" % (section_index-DOL.TEXT_SECTION_COUNT)
      
      section_name_item = QStandardItem(section_name)
      section_name_item.setEditable(False)
      if section.offset == section.address == section.size == 0:
        section_columns = [section_name, "", "", ""]
        self.model.appendRow(section_name_item)
      else:
        offset_item = QStandardItem("0x%06X" % section.offset)
        offset_item.setEditable(False)
        address_item = QStandardItem("0x%08X" % section.address)
        address_item.setEditable(False)
        size_item = QStandardItem("0x%06X" % section.size)
        size_item.setEditable(False)
        self.model.appendRow([section_name_item, offset_item, address_item, size_item])
  
  def export_dol_by_path(self, dol_path):
    assert self.dol is not None
    
    self.dol.save_changes()
    
    with open(dol_path, "wb") as f:
      self.dol.data.seek(0)
      f.write(self.dol.data.read())
    
    self.dol_name = os.path.splitext(os.path.basename(dol_path))[0]
    
    QMessageBox.information(self, "DOL saved", "Successfully saved DOL.")
  
  def convert_from_dol_offset(self):
    assert self.dol is not None
    
    offset_str = self.ui.dol_offset.text().strip()
    if not offset_str:
      QMessageBox.warning(self, "Conversion failed", "No offset given.")
      return
    if not re.search(r"^(?:0x)?[0-9a-f]+$", offset_str, re.IGNORECASE):
      QMessageBox.warning(self, "Conversion failed", "'%s' is not a valid hexadecimal number." % offset_str)
      return
    
    offset = int(offset_str, 16)
    
    if offset < 0:
      QMessageBox.warning(self, "Conversion failed", "Offset can not be a negative number.")
      return
    if offset >= fs.data_len(self.dol.data):
      QMessageBox.warning(self, "Conversion failed", "Offset is past the end of the DOL.")
      return
    
    address = self.dol.convert_offset_to_address(offset)
    
    if address is None:
      QMessageBox.warning(self, "Conversion failed", "Offset is not in any of the DOL sections, so it is not loaded to RAM.")
      return
    
    self.ui.dol_address.setText("%08X" % address)
    self.ui.dol_offset.setText("%06X" % offset)
  
  def convert_from_dol_address(self):
    assert self.dol is not None
    
    address_str = self.ui.dol_address.text().strip()
    if not address_str:
      QMessageBox.warning(self, "Conversion failed", "No address given.")
      return
    if not re.search(r"^(?:0x)?[0-9a-f]+$", address_str, re.IGNORECASE):
      QMessageBox.warning(self, "Conversion failed", "'%s' is not a valid hexadecimal number." % address_str)
      return
    
    address = int(address_str, 16)
    
    if address < 0:
      QMessageBox.warning(self, "Conversion failed", "Address can not be a negative number.")
      return
    
    offset = self.dol.convert_address_to_offset(address)
    
    if offset is None:
      QMessageBox.warning(self, "Conversion failed", "Address is not in any of the DOL sections, so it is not loaded from the DOL.")
      return
    
    self.ui.dol_offset.setText("%06X" % offset)
    self.ui.dol_address.setText("%08X" % address)
