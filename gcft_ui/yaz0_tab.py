
import os
import re
import traceback
from io import BytesIO
from fs_helpers import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from wwlib.yaz0 import Yaz0
from gcft_ui.uic.ui_yaz0_tab import Ui_Yaz0Tab

class Yaz0Tab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_Yaz0Tab()
    self.ui.setupUi(self)
    
    self.ui.decompress_yaz0.clicked.connect(self.decompress_yaz0)
    self.ui.compress_yaz0.clicked.connect(self.compress_yaz0)
  
  
  def decompress_yaz0(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.decompress_yaz0_by_paths,
      is_opening=True, is_saving=True, is_folder=False,
      file_type="Yaz0", file_filter=""
    )
  
  def compress_yaz0(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.compress_yaz0_by_paths,
      is_opening=True, is_saving=True, is_folder=False,
      file_type="Yaz0", file_filter=""
    )
  
  
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
