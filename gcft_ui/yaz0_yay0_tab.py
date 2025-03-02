
import os
from io import BytesIO
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from gclib.yaz0_yay0 import Yaz0, Yay0

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from gcft_ui.main_window import GCFTWindow

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_yaz0_yay0_tab import Ui_Yaz0Yay0Tab
else:
  Ui_Yaz0Yay0Tab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "yaz0_yay0_tab.ui"))

class Yaz0Yay0Tab(QWidget):
  gcft_window: 'GCFTWindow'
  
  def __init__(self):
    super().__init__()
    self.ui = Ui_Yaz0Yay0Tab()
    self.ui.setupUi(self)
    
    self.ui.decompress_yaz0.clicked.connect(self.decompress_yaz0)
    self.ui.compress_yaz0.clicked.connect(self.compress_yaz0)
    self.ui.decompress_yay0.clicked.connect(self.decompress_yay0)
    self.ui.compress_yay0.clicked.connect(self.compress_yay0)
  
  
  def decompress_yaz0(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.decompress_yaz0_by_paths,
      is_opening=True, is_saving=True, is_folder=False,
      file_type="Yaz0", file_filters=[]
    )
  
  def compress_yaz0(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.compress_yaz0_by_paths,
      is_opening=True, is_saving=True, is_folder=False,
      file_type="Yaz0", file_filters=[]
    )
  
  def decompress_yay0(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.decompress_yay0_by_paths,
      is_opening=True, is_saving=True, is_folder=False,
      file_type="Yay0", file_filters=[]
    )
  
  def compress_yay0(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.compress_yay0_by_paths,
      is_opening=True, is_saving=True, is_folder=False,
      file_type="Yay0", file_filters=[]
    )
  
  
  def decompress_yaz0_by_paths(self, comp_path, decomp_path):
    with open(comp_path, "rb") as f:
      comp_data = BytesIO(f.read())
    if not Yaz0.check_is_compressed(comp_data):
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
    if Yaz0.check_is_compressed(decomp_data):
      QMessageBox.warning(self, "Already Yaz0 compressed", "The selected file is already Yaz0 compressed. Cannot compress.")
      return
    
    search_depth, should_pad_data = self.get_search_depth_and_should_pad()
    
    # TODO: progress bar?
    comp_data = Yaz0.compress(decomp_data, search_depth=search_depth, should_pad_data=should_pad_data)
    
    with open(comp_path, "wb") as f:
      comp_data.seek(0)
      f.write(comp_data.read())
    
    QMessageBox.information(self, "Compressed file saved", "Successfully compressed and saved file.")
  
  def decompress_yay0_by_paths(self, comp_path, decomp_path):
    with open(comp_path, "rb") as f:
      comp_data = BytesIO(f.read())
    if not Yay0.check_is_compressed(comp_data):
      QMessageBox.warning(self, "Not Yay0 compressed", "The selected file is not Yay0 compressed. Cannot decompress.")
      return
    
    decomp_data = Yay0.decompress(comp_data)
    
    with open(decomp_path, "wb") as f:
      decomp_data.seek(0)
      f.write(decomp_data.read())
    
    QMessageBox.information(self, "Decompressed file saved", "Successfully decompressed and saved file.")
  
  def compress_yay0_by_paths(self, decomp_path, comp_path):
    with open(decomp_path, "rb") as f:
      decomp_data = BytesIO(f.read())
    if Yay0.check_is_compressed(decomp_data):
      QMessageBox.warning(self, "Already Yay0 compressed", "The selected file is already Yay0 compressed. Cannot compress.")
      return
    
    search_depth, should_pad_data = self.get_search_depth_and_should_pad()
    
    # TODO: progress bar?
    comp_data = Yay0.compress(decomp_data, search_depth=search_depth, should_pad_data=should_pad_data)
    
    with open(comp_path, "wb") as f:
      comp_data.seek(0)
      f.write(comp_data.read())
    
    QMessageBox.information(self, "Compressed file saved", "Successfully compressed and saved file.")
  
  
  def get_search_depth_and_should_pad(self):
    compression_level = self.ui.compression_level.value()
    search_depth = compression_level*0x100
    assert 0 <= search_depth <= 0x1000
    
    should_pad_data = self.ui.pad_compressed_files.isChecked()
    
    return (search_depth, should_pad_data)
