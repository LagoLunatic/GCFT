
import os
import re
import traceback
from io import BytesIO
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.dol import DOL
from gcft_ui.uic.ui_dol_tab import Ui_DOLTab

class DOLTab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_DOLTab()
    self.ui.setupUi(self)
    
    self.dol = None
    self.dolname = None
    
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
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_dol_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="DOL executable", file_filter="DOL Executables (*.dol)",
    )
  
  def export_dol(self):
    dol_name = self.dol_name + ".dol"
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_dol_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="DOL executable", file_filter="DOL Executables (*.dol)",
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
    self.ui.dol_sections_tree.clear()
    
    for section_index, section in enumerate(self.dol.sections):
      if section_index < DOL.TEXT_SECTION_COUNT:
        section_name = ".text%d" % section_index
      else:
        section_name = ".data%d" % (section_index-DOL.TEXT_SECTION_COUNT)
      
      if section.offset == section.address == section.size == 0:
        section_columns = [section_name, "", "", ""]
      else:
        section_columns = [section_name, "0x%06X" % section.offset, "0x%08X" % section.address, "0x%06X" % section.size]
      section_item = QTreeWidgetItem(section_columns)
      self.ui.dol_sections_tree.addTopLevelItem(section_item)
  
  def export_dol_by_path(self, dol_path):
    self.dol.save_changes()
    
    with open(dol_path, "wb") as f:
      self.dol.data.seek(0)
      f.write(self.dol.data.read())
    
    self.dol_name = os.path.splitext(os.path.basename(dol_path))[0]
    
    QMessageBox.information(self, "DOL saved", "Successfully saved DOL.")
  
  def convert_from_dol_offset(self):
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
