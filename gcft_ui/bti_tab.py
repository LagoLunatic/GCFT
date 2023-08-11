
import os
import re
import traceback
from io import BytesIO
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.bti import BTI, WrapMode, FilterMode
from gclib.texture_utils import ImageFormat, PaletteFormat, MAX_COLORS_FOR_IMAGE_FORMAT
from gcft_ui.uic.ui_bti_tab import Ui_BTITab
from gcft_paths import ASSETS_PATH
from PIL import Image

BTI_ENUM_FIELDS = [
  ("image_format", ImageFormat),
  ("palette_format", PaletteFormat),
  ("wrap_s", WrapMode),
  ("wrap_t", WrapMode),
  ("min_filter", FilterMode),
  ("mag_filter", FilterMode),
]

BTI_INTEGER_FIELDS = [
  ("alpha_setting", 1),
  ("min_lod", 1),
  ("max_lod", 1),
  ("lod_bias", 2),
]

class BTITab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_BTITab()
    self.ui.setupUi(self)
    
    self.bti = None
    self.bti_name = None
    
    self.ui.export_bti.setDisabled(True)
    self.ui.export_bti_image.setDisabled(True)
    
    self.ui.bti_file_size.setText("")
    self.ui.bti_resolution.setText("")
    self.ui.bti_num_colors.setText("")
    self.ui.bti_max_colors.setText("")
    
    checkerboard_path = os.path.join(ASSETS_PATH, "checkerboard.png")
    checkerboard_path = checkerboard_path.replace("\\", "/")
    self.ui.bti_image_label.setStyleSheet("border-image: url(%s) repeat;" % checkerboard_path)
    self.ui.bti_image_label.hide()
    
    self.ui.import_bti.clicked.connect(self.import_bti)
    self.ui.export_bti.clicked.connect(self.export_bti)
    self.ui.import_bti_image.clicked.connect(self.import_bti_image)
    self.ui.export_bti_image.clicked.connect(self.export_bti_image)
    self.ui.import_bti_from_bnr.clicked.connect(self.import_bti_from_bnr)
    
    for field_name, field_enum in BTI_ENUM_FIELDS:
      widget_name = "bti_" + field_name
      combobox_widget = getattr(self.ui, widget_name)
      combobox_widget.setDisabled(True)
      
      for enum_value in field_enum:
        combobox_widget.addItem(enum_value.name)
      combobox_widget.currentIndexChanged.connect(self.bti_header_field_changed)
    
    for field_name, byte_size in BTI_INTEGER_FIELDS:
      widget_name = "bti_" + field_name
      line_edit_widget = getattr(self.ui, widget_name)
      line_edit_widget.setDisabled(True)
      
      value_str = ""
      line_edit_widget.setText(value_str)
      line_edit_widget.editingFinished.connect(self.bti_header_field_changed)
  
  
  def import_bti(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_bti_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="BTI", file_filter="BTI files (*.bti)"
    )
  
  def export_bti(self):
    bti_name = self.bti_name + ".bti"
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_bti_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="BTI", file_filter="BTI files (*.bti)",
      default_file_name=bti_name
    )
  
  def import_bti_image(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_bti_image_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="image", file_filter="PNG Files (*.png)"
    )
  
  def export_bti_image(self):
    png_name = self.bti_name + ".png"
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_bti_image_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="image", file_filter="PNG Files (*.png)",
      default_file_name=png_name
    )
  
  def import_bti_from_bnr(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_bti_from_bnr_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="BNR", file_filter="All files (*.*)"
    )
  
  
  def import_bti_by_path(self, bti_path):
    with open(bti_path, "rb") as f:
      data = BytesIO(f.read())
    
    bti_name = os.path.splitext(os.path.basename(bti_path))[0]
    
    self.import_bti_by_data(data, bti_name)
  
  def import_bti_by_data(self, data, bti_name):
    prev_bti = self.bti
    self.bti = BTI(data)
    
    try:
      self.reload_bti_image()
    except Exception as e:
      self.bti = prev_bti # Revert back to whatever BTI was already loaded and abort
      stack_trace = traceback.format_exc()
      error_message_title = "Failed to render BTI image"
      error_message = "Failed to render BTI image with error:\n%s\n\n%s" % (str(e), stack_trace)
      QMessageBox.critical(self, error_message_title, error_message)
      return
    
    self.original_bti_image = self.bti_image
    
    self.bti_name = bti_name
    
    
    for field_name, field_enum in BTI_ENUM_FIELDS:
      widget_name = "bti_" + field_name
      combobox_widget = getattr(self.ui, widget_name)
      combobox_widget.setDisabled(False)
      
      current_enum_value = getattr(self.bti, field_name)
      current_enum_name = current_enum_value.name
      
      index_of_value = None
      for i in range(combobox_widget.count()):
        text = combobox_widget.itemText(i)
        if text == current_enum_name:
          index_of_value = i
          break
      if index_of_value is None:
        print("Cannot find value %s in combobox %s" % (current_enum_name, widget_name))
        index_of_value = 0
      
      combobox_widget.blockSignals(True)
      combobox_widget.setCurrentIndex(index_of_value)
      combobox_widget.blockSignals(False)
    
    
    for field_name, byte_size in BTI_INTEGER_FIELDS:
      widget_name = "bti_" + field_name
      line_edit_widget = getattr(self.ui, widget_name)
      line_edit_widget.setDisabled(False)
      
      value = getattr(self.bti, field_name)
      value_str = self.window().stringify_number(value, min_hex_chars=2*byte_size)
      combobox_widget.blockSignals(True)
      line_edit_widget.setText(value_str)
      combobox_widget.blockSignals(False)
    
    # Disable the palette format dropdown when the image format doesn't use palettes.
    if self.bti.needs_palettes():
      self.ui.bti_palette_format.setDisabled(False)
    else:
      self.ui.bti_palette_format.setDisabled(True)
    
    
    self.ui.export_bti.setDisabled(False)
    self.ui.export_bti_image.setDisabled(False)
  
  def reload_bti_image(self):
    self.bti_image = self.bti.render()
    
    image_bytes = self.bti_image.tobytes('raw', 'BGRA')
    qimage = QImage(image_bytes, self.bti_image.width, self.bti_image.height, QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(qimage)
    self.ui.bti_image_label.setPixmap(pixmap)
    
    file_size_str = self.window().stringify_number(fs.data_len(self.bti.data))
    resolution_str = "%dx%d" % (self.bti_image.width, self.bti_image.height)
    self.ui.bti_file_size.setText(file_size_str)
    self.ui.bti_resolution.setText(resolution_str)
    if self.bti.needs_palettes():
      self.ui.bti_num_colors.setText("%d" % self.bti.num_colors)
      self.ui.bti_max_colors.setText("%d" % MAX_COLORS_FOR_IMAGE_FORMAT[self.bti.image_format])
    else:
      self.ui.bti_num_colors.setText("N/A")
      self.ui.bti_max_colors.setText("N/A")
    
    self.ui.bti_image_label.setFixedWidth(self.bti_image.width)
    self.ui.bti_image_label.setFixedHeight(self.bti_image.height)
    self.ui.bti_image_label.show()
  
  def export_bti_by_path(self, bti_path):
    self.bti.save_changes()
    
    with open(bti_path, "wb") as f:
      self.bti.data.seek(0)
      f.write(self.bti.data.read())
    
    self.bti_name = os.path.splitext(os.path.basename(bti_path))[0]
    
    QMessageBox.information(self, "BTI saved", "Successfully saved BTI.")
  
  def import_bti_image_by_path(self, image_path):
    try:
      if self.bti is None:
        # No BTI is already loaded. Create a dummy one from scratch to allow importing this image.
        data = BytesIO()
        image_data = b"\0"*0x20
        fs.write_bytes(data, 0x20, image_data)
        palette_data = b"\0"*2
        fs.write_bytes(data, 0x20+len(image_data), palette_data)
        fs.write_u8(data,  0x00, ImageFormat.C8.value) # Image format
        fs.write_u16(data, 0x02, 8) # Width
        fs.write_u16(data, 0x04, 4) # Height
        fs.write_u8(data,  0x08, 1) # Palettes enabled
        fs.write_u8(data,  0x09, PaletteFormat.RGB5A3.value) # Palette format
        fs.write_u16(data, 0x0A, 1) # Num colors
        fs.write_u32(data, 0x0C, 0x20+len(image_data)) # Palette data offset
        fs.write_u32(data, 0x1C, 0x20) # Image data offset
        
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        
        self.import_bti_by_data(data, image_name)
      
      self.original_bti_image = Image.open(image_path)
      
      self.bti.replace_image(self.original_bti_image)
      
      self.bti.save_changes()
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message_title = "Failed to import image"
      error_message = "Failed to import image with error:\n%s\n\n%s" % (str(e), stack_trace)
      QMessageBox.critical(self, error_message_title, error_message)
      return
    
    self.reload_bti_image()
  
  def export_bti_image_by_path(self, image_path):
    self.bti_image.save(image_path)
    
    QMessageBox.information(self, "BTI saved", "Successfully saved image.")
  
  def import_bti_from_bnr_by_path(self, bnr_path):
    with open(bnr_path, "rb") as f:
      data = BytesIO(f.read())
    
    bti_name = os.path.basename(bnr_path)
    
    self.import_bti_from_bnr_by_data(data, bti_name)
  
  def import_bti_from_bnr_by_data(self, data, bti_name):
    if fs.data_len(data) != 0x1960:
      QMessageBox.warning(self, "Not a banner", "The specified file does not appear to be a GameCube banner.\nGameCube banners must be 0x1960 bytes long, this file is 0x%X bytes long." % fs.data_len(data))
      return
    if fs.read_str(data, 0, 4) != "BNR1":
      QMessageBox.warning(self, "Not a banner", "The specified file does not appear to be a GameCube banner.\nGameCube banners must have the magic bytes 'BNR1', this file has the magic bytes '%s'." % fs.read_str(data, 0, 4))
      return
    
    image_data = fs.read_bytes(data, 0x20, 0x1800)
    data = BytesIO()
    fs.write_bytes(data, 0x20, image_data)
    
    fs.write_u8(data, 0x00, ImageFormat.RGB5A3.value) # Image format
    fs.write_u16(data, 0x02, 96) # Width
    fs.write_u16(data, 0x04, 32) # Height
    fs.write_u32(data, 0x1C, 0x20) # Image data offset
    
    self.import_bti_by_data(data, bti_name)
  
  def bti_header_field_changed(self):
    for field_name, field_enum in BTI_ENUM_FIELDS:
      widget_name = "bti_" + field_name
      combobox_widget = getattr(self.ui, widget_name)
      
      current_enum_name = combobox_widget.itemText(combobox_widget.currentIndex())
      current_enum_value = field_enum[current_enum_name]
      
      setattr(self.bti, field_name, current_enum_value)
    
    
    for field_name, byte_size in BTI_INTEGER_FIELDS:
      widget_name = "bti_" + field_name
      line_edit_widget = getattr(self.ui, widget_name)
      new_str_value = line_edit_widget.text()
      old_value = getattr(self.bti, field_name)
      
      line_edit_widget.blockSignals(True)
      
      if self.window().display_hexadecimal_numbers:
        hexadecimal_match = re.search(r"^\s*(?:0x)?([0-9a-f]+)\s*$", new_str_value, re.IGNORECASE)
        if hexadecimal_match:
          new_value = int(hexadecimal_match.group(1), 16)
        else:
          QMessageBox.warning(self, "Invalid value", "\"%s\" is not a valid hexadecimal number." % new_str_value)
          new_value = old_value
      else:
        decimal_match = re.search(r"^\s*(\d+)\s*$", new_str_value, re.IGNORECASE)
        if decimal_match:
          new_value = int(decimal_match.group(1))
        else:
          QMessageBox.warning(self, "Invalid value", "\"%s\" is not a valid decimal number." % new_str_value)
          new_value = old_value
      
      if new_value < 0:
        QMessageBox.warning(self, "Invalid value", "Value cannot be negative.")
        new_value = old_value
      if new_value >= 2**(byte_size*8):
        QMessageBox.warning(
          self, "Invalid value",
          "Value is too large to fit in field %s (maximum value: 0x%X)" % (field_name, (2**(byte_size*8))-1)
        )
        new_value = old_value
      
      setattr(self.bti, field_name, new_value)
      
      new_str_value = self.window().stringify_number(new_value, min_hex_chars=2*byte_size)
      line_edit_widget.setText(new_str_value)
      line_edit_widget.blockSignals(False)
    
    # Disable the palette format dropdown when the image format doesn't use palettes.
    if self.bti.needs_palettes():
      self.ui.bti_palette_format.setDisabled(False)
    else:
      self.ui.bti_palette_format.setDisabled(True)
    
    try:
      self.bti.replace_image(self.original_bti_image)
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message_title = "Failed to import image"
      error_message = "Failed to import image with error:\n%s\n\n%s" % (str(e), stack_trace)
      QMessageBox.critical(self, error_message_title, error_message)
      return
    
    self.bti.save_changes()
    
    self.reload_bti_image()
