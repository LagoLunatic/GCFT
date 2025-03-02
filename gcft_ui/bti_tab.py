
import os
import re
import traceback
from io import BytesIO
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.bti import BTI, WrapMode, FilterMode
from gclib.texture_utils import ImageFormat, PaletteFormat, MAX_COLORS_FOR_IMAGE_FORMAT
from gcft_paths import ASSETS_PATH
from PIL import Image

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from gcft_ui.main_window import GCFTWindow

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_bti_tab import Ui_BTITab
else:
  Ui_BTITab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "bti_tab.ui"))

BTI_ENUM_FIELDS = {
  "image_format": ImageFormat,
  "palette_format": PaletteFormat,
  "wrap_s": WrapMode,
  "wrap_t": WrapMode,
  "min_filter": FilterMode,
  "mag_filter": FilterMode,
}

BTI_INTEGER_FIELDS = {
  "alpha_setting": 1,
  "min_lod": 1,
  "max_lod": 1,
  "lod_bias": 2,
  "mipmap_count": 1,
}

class BTITab(QWidget):
  gcft_window: 'GCFTWindow'
  
  def __init__(self):
    super().__init__()
    self.ui = Ui_BTITab()
    self.ui.setupUi(self)
    
    self.bti: BTI | None = None
    self.bti_name = None
    
    self.ui.export_bti.setDisabled(True)
    self.ui.export_bti_image.setDisabled(True)
    self.ui.bti_curr_mipmap.setDisabled(True)
    self.ui.replace_bti_mipmap.setDisabled(True)
    
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
    self.ui.bti_curr_mipmap.currentIndexChanged.connect(self.reload_bti_image)
    self.ui.replace_bti_mipmap.clicked.connect(self.replace_bti_mipmap_image)
    
    for field_name, field_enum in BTI_ENUM_FIELDS.items():
      widget_name = "bti_" + field_name
      combobox_widget = getattr(self.ui, widget_name)
      combobox_widget.setDisabled(True)
      
      for enum_value in field_enum:
        combobox_widget.addItem(enum_value.name)
      combobox_widget.currentIndexChanged.connect(self.bti_header_field_changed)
    
    for field_name, byte_size in BTI_INTEGER_FIELDS.items():
      widget_name = "bti_" + field_name
      line_edit_widget = getattr(self.ui, widget_name)
      line_edit_widget.setDisabled(True)
      
      value_str = ""
      line_edit_widget.setText(value_str)
      line_edit_widget.editingFinished.connect(self.bti_header_field_changed)
  
  
  def import_bti(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.import_bti_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="BTI", file_filters=["BTI files (*.bti)"],
    )
  
  def export_bti(self):
    bti_name = self.bti_name + ".bti"
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_bti_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="BTI", file_filters=["BTI files (*.bti)"],
      default_file_name=bti_name
    )
  
  def import_bti_image(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.import_bti_image_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="image", file_filters=["PNG Files (*.png)"],
    )
  
  def export_bti_image(self):
    png_name = self.bti_name + ".png"
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_bti_image_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="image", file_filters=["PNG Files (*.png)"],
      default_file_name=png_name
    )
  
  def import_bti_from_bnr(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.import_bti_from_bnr_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="BNR", file_filters=[],
    )
  
  def replace_bti_mipmap_image(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.replace_bti_mipmap_image_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="image", file_filters=["PNG Files (*.png)"],
    )
  
  
  def import_bti_by_path(self, bti_path):
    with open(bti_path, "rb") as f:
      data = BytesIO(f.read())
    
    bti_name = os.path.splitext(os.path.basename(bti_path))[0]
    
    self.import_bti_by_data(data, bti_name)
  
  def import_bti_by_data(self, data, bti_name):
    self.ui.bti_curr_mipmap.setCurrentIndex(0)
    
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
    
    
    for field_name, field_enum in BTI_ENUM_FIELDS.items():
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
    
    
    for field_name, byte_size in BTI_INTEGER_FIELDS.items():
      widget_name = "bti_" + field_name
      line_edit_widget = getattr(self.ui, widget_name)
      line_edit_widget.setDisabled(False)
      
      value = getattr(self.bti, field_name)
      value_str = self.gcft_window.stringify_number(value, min_hex_chars=2*byte_size)
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
    self.ui.replace_bti_mipmap.setDisabled(False)
    self.ui.bti_curr_mipmap.setDisabled(False)
  
  def reload_bti_image(self):
    assert self.bti is not None
    
    selected_mipmap_index = self.ui.bti_curr_mipmap.currentIndex()
    selected_mipmap_index = max(0, selected_mipmap_index)
    selected_mipmap_index = min(self.bti.mipmap_count-1, selected_mipmap_index)
    
    self.bti_image = self.bti.render_mipmap(selected_mipmap_index)
    
    image_bytes = self.bti_image.tobytes('raw', 'BGRA')
    qimage = QImage(image_bytes, self.bti_image.width, self.bti_image.height, QImage.Format.Format_ARGB32)
    pixmap = QPixmap.fromImage(qimage)
    self.ui.bti_image_label.setPixmap(pixmap)
    
    file_size_str = self.gcft_window.stringify_number(fs.data_len(self.bti.data))
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
    
    self.ui.bti_curr_mipmap.blockSignals(True)
    self.ui.bti_curr_mipmap.clear()
    for i in range(self.bti.mipmap_count):
      _, _, mipmap_width, mipmap_height = self.bti.get_mipmap_offset_and_size(i)
      self.ui.bti_curr_mipmap.addItem(f"{i}: {mipmap_width}x{mipmap_height}")
    self.ui.bti_curr_mipmap.setCurrentIndex(selected_mipmap_index)
    self.ui.bti_curr_mipmap.blockSignals(False)
  
  def export_bti_by_path(self, bti_path):
    assert self.bti is not None
    
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
        # TODO: this is a hack, should really be handled within the BTI class
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
        fs.write_u8(data, 0x18, 1) # Mipmap count
        fs.write_u32(data, 0x1C, 0x20) # Image data offset
        
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        
        self.import_bti_by_data(data, image_name)
      
      assert self.bti is not None
      
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
  
  def replace_bti_mipmap_image_by_path(self, image_path):
    assert self.bti is not None
    
    _, _, width, height = self.bti.get_mipmap_offset_and_size(self.ui.bti_curr_mipmap.currentIndex())
    image = Image.open(image_path)
    if image.width != width or image.height != height:
      QMessageBox.warning(self,
        "Invalid mipmap size",
        "The image you selected has the wrong size for this mipmap.\n" +
        "Each mipmap must be exactly half the size of the previous one.\n" +
        f"Expected size: {width}x{height}\n" +
        f"Instead got: {image.width}x{image.height}\n\n" +
        "If you want to completely replace all mipmaps with an image of a different size, select \"Import Image\" instead."
      )
    
    self.bti.replace_mipmap(self.ui.bti_curr_mipmap.currentIndex(), image)
    
    self.bti.save_changes()
    print(self.bti.num_colors)
    
    self.reload_bti_image()
  
  def bti_header_field_changed(self):
    assert self.bti is not None
    
    field_name = self.sender().objectName()
    assert field_name.startswith("bti_")
    field_name = field_name[len("bti_"):]
    
    if field_name in BTI_ENUM_FIELDS:
      field_enum = BTI_ENUM_FIELDS[field_name]
      combobox_widget: QComboBox = self.sender()
      
      current_enum_name = combobox_widget.itemText(combobox_widget.currentIndex())
      current_enum_value = field_enum[current_enum_name]
      
      setattr(self.bti, field_name, current_enum_value)
    elif field_name in BTI_INTEGER_FIELDS:
      byte_size = BTI_INTEGER_FIELDS[field_name]
      line_edit_widget: QLineEdit = self.sender()
      new_str_value = line_edit_widget.text()
      old_value = getattr(self.bti, field_name)
      
      line_edit_widget.blockSignals(True)
      
      if self.gcft_window.display_hexadecimal_numbers:
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
      
      if field_name == "mipmap_count":
        min_value = 1
        max_value = self.bti.get_max_valid_mipmap_count()
      else:
        min_value = 0
        max_value = max_value = (2**(byte_size*8)) - 1
      
      if new_value < min_value:
        QMessageBox.warning(self, "Invalid value", f"Value is too small (minimum value: 0x{min_value:X})")
        new_value = old_value
      if new_value > max_value:
        QMessageBox.warning(
          self, "Invalid value",
          "Value is too large to fit in field %s (maximum value: 0x%X)" % (field_name, max_value)
        )
        new_value = old_value
      
      setattr(self.bti, field_name, new_value)
      
      new_str_value = self.gcft_window.stringify_number(new_value, min_hex_chars=2*byte_size)
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
