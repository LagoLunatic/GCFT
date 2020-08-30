
import os
import re
import traceback
from io import BytesIO
from fs_helpers import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from wwlib.j3d import J3DFile
from gcft_ui.uic.ui_j3d_tab import Ui_J3DTab

class J3DTab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_J3DTab()
    self.ui.setupUi(self)
    
    self.j3d = None
    self.j3d_name = None
    
    self.j3d_col_name_to_index = {}
    for col in range(self.ui.j3d_chunks_tree.columnCount()):
      column_name = self.ui.j3d_chunks_tree.headerItem().text(col)
      self.j3d_col_name_to_index[column_name] = col
    
    self.ui.export_j3d.setDisabled(True)
    
    self.ui.import_j3d.clicked.connect(self.import_j3d)
    self.ui.export_j3d.clicked.connect(self.export_j3d)
    
    self.ui.j3d_chunks_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.j3d_chunks_tree.customContextMenuRequested.connect(self.show_j3d_chunks_tree_context_menu)
    self.ui.actionOpenJ3DImage.triggered.connect(self.open_image_in_j3d)
    self.ui.actionReplaceJ3DImage.triggered.connect(self.replace_image_in_j3d)
  
  
  def import_j3d(self):
    filters = [
      "Models and material tables (*.bmd *.bdl *.bmt)",
      "All J3D files (*.bmd *.bdl *.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)",
    ]
    
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_j3d_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="J3D file", file_filter=";;".join(filters)
    )
  
  def export_j3d(self):
    filters = []
    current_filter = self.get_file_filter_by_current_j3d_file_type()
    if current_filter is not None:
      filters.append(current_filter)
    filters.append("All J3D files (*.bmd *.bdl *.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)")
    
    j3d_name = "%s.%s" % (self.j3d_name, self.j3d.file_type[:3])
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_j3d_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="J3D file", file_filter=";;".join(filters),
      default_file_name=j3d_name
    )
  
  
  def import_j3d_by_path(self, j3d_path):
    with open(j3d_path, "rb") as f:
      data = BytesIO(f.read())
    
    j3d_name = os.path.splitext(os.path.basename(j3d_path))[0]
    
    self.import_j3d_by_data(data, j3d_name)
  
  def import_j3d_by_data(self, data, j3d_name):
    self.j3d = J3DFile(data)
    
    self.j3d_name = j3d_name
    
    self.reload_j3d_chunks_tree()
    
    self.ui.export_j3d.setDisabled(False)
  
  def reload_j3d_chunks_tree(self):
    self.ui.j3d_chunks_tree.clear()
    
    self.j3d_chunk_to_tree_widget_item = {}
    self.j3d_tree_widget_item_to_chunk = {}
    self.j3d_texture_to_tree_widget_item = {}
    self.j3d_tree_widget_item_to_texture = {}
    
    for chunk in self.j3d.chunks:
      chunk_size_str = self.window().stringify_number(chunk.size, min_hex_chars=5)
      
      chunk_item = QTreeWidgetItem([chunk.magic, "", chunk_size_str])
      self.ui.j3d_chunks_tree.addTopLevelItem(chunk_item)
      
      self.j3d_chunk_to_tree_widget_item[chunk] = chunk_item
      self.j3d_tree_widget_item_to_chunk[chunk_item] = chunk
      
      if chunk.magic == "TEX1":
        # Expand TEX1 chunks by default.
        chunk_item.setExpanded(True)
        
        seen_image_data_offsets = []
        seen_palette_data_offsets = []
        
        for i, texture in enumerate(chunk.textures):
          texture_name = chunk.texture_names[i]
          
          # We don't display sizes for texture headers that use image/palette datas duplicated from an earlier tex header.
          # We also don't display the 0x20 byte size of any of the headers.
          texture_total_size = 0
          if texture.image_data_offset+texture.header_offset not in seen_image_data_offsets:
            texture_total_size += data_len(texture.image_data)
            seen_image_data_offsets.append(texture.image_data_offset+texture.header_offset)
          if texture.palette_data_offset+texture.header_offset not in seen_palette_data_offsets:
            texture_total_size += data_len(texture.palette_data)
            seen_palette_data_offsets.append(texture.palette_data_offset+texture.header_offset)
          
          if texture_total_size == 0:
            texture_size_str = ""
          else:
            texture_size_str = self.window().stringify_number(texture_total_size, min_hex_chars=5)
          
          texture_item = QTreeWidgetItem(["", texture_name, texture_size_str])
          chunk_item.addChild(texture_item)
          
          self.j3d_texture_to_tree_widget_item[texture] = texture_item
          self.j3d_tree_widget_item_to_texture[texture_item] = texture
  
  def export_j3d_by_path(self, j3d_path):
    self.j3d.save_changes()
    
    with open(j3d_path, "wb") as f:
      self.j3d.data.seek(0)
      f.write(self.j3d.data.read())
    
    self.j3d_name = os.path.splitext(os.path.basename(j3d_path))[0]
    
    QMessageBox.information(self, "J3D file saved", "Successfully saved J3D file.")
  
  def get_file_filter_by_current_j3d_file_type(self):
    if self.j3d.file_type == "bdl4":
      return "Binary Display List Models (*.bdl)"
    elif self.j3d.file_type == "bmd3":
      return "Binary Models (*.bmd)"
    elif self.j3d.file_type == "bmt3":
      return "Binary Material Tables (*.bmt)"
    elif self.j3d.file_type == "btk1":
      return "Texture SRT Animations (*.btk)"
    elif self.j3d.file_type == "bck1":
      return "Joint Animations (*.bck)"
    elif self.j3d.file_type == "brk1":
      return "Texture Register Animations (*.brk)"
    elif self.j3d.file_type == "btp1":
      return "Texture Swap Animations (*.btp)"
    else:
      return None
  
  def get_j3d_chunk_by_tree_item(self, item):
    if item not in self.j3d_tree_widget_item_to_chunk:
      return None
    
    return self.j3d_tree_widget_item_to_chunk[item]
  
  def get_j3d_tree_item_by_chunk(self, chunk):
    if chunk not in self.j3d_chunk_to_tree_widget_item:
      return None
    
    return self.j3d_chunk_to_tree_widget_item[chunk]
  
  def get_j3d_texture_by_tree_item(self, item):
    if item not in self.j3d_tree_widget_item_to_texture:
      return None
    
    return self.j3d_tree_widget_item_to_texture[item]
  
  def get_jpc_tree_item_by_texture(self, texture):
    if texture not in self.j3d_texture_to_tree_widget_item:
      return None
    
    return self.j3d_texture_to_tree_widget_item[texture]
  
  def show_j3d_chunks_tree_context_menu(self, pos):
    if self.j3d is None:
      return
    
    item = self.ui.j3d_chunks_tree.itemAt(pos)
    if item is None:
      return
    
    texture = self.get_j3d_texture_by_tree_item(item)
    if texture:
      menu = QMenu(self)
      
      menu.addAction(self.ui.actionOpenJ3DImage)
      self.ui.actionOpenJ3DImage.setData(texture)
      
      menu.addAction(self.ui.actionReplaceJ3DImage)
      self.ui.actionReplaceJ3DImage.setData(texture)
      if self.bti_tab.bti is None:
        self.ui.actionReplaceJ3DImage.setDisabled(True)
      else:
        self.ui.actionReplaceJ3DImage.setDisabled(False)
      
      menu.exec_(self.ui.j3d_chunks_tree.mapToGlobal(pos))
  
  def open_image_in_j3d(self):
    texture = self.ui.actionOpenJ3DImage.data()
    
    # Need to make a fake standalone BTI texture data so we can load it without it being the TEX1 format.
    data = BytesIO()
    bti_header_bytes = read_bytes(texture.data, texture.header_offset, 0x20)
    write_bytes(data, 0x00, bti_header_bytes)
    
    bti_image_data = read_all_bytes(texture.image_data)
    write_bytes(data, 0x20, bti_image_data)
    image_data_offset = 0x20
    write_u32(data, 0x1C, image_data_offset)
    
    if data_len(texture.palette_data) == 0:
      palette_data_offset = 0
    else:
      bti_palette_data = read_all_bytes(texture.palette_data)
      write_bytes(data, 0x20 + data_len(texture.image_data), bti_palette_data)
      palette_data_offset = 0x20 + data_len(texture.image_data)
    write_u32(data, 0x0C, palette_data_offset)
    
    texture_index = self.j3d.tex1.textures.index(texture)
    bti_name = self.j3d.tex1.texture_names[texture_index]
    
    self.bti_tab.import_bti_by_data(data, bti_name)
    
    self.window().set_tab_by_name("BTI Images")
  
  def replace_image_in_j3d(self):
    texture = self.ui.actionOpenJ3DImage.data()
    
    self.bti_tab.bti.save_changes()
    
    # Need to make a fake BTI header for it to read from.
    data = BytesIO()
    bti_header_bytes = read_bytes(self.bti_tab.bti.data, self.bti_tab.bti.header_offset, 0x20)
    write_bytes(data, 0x00, bti_header_bytes)
    
    texture.read_header(data)
    
    texture.image_data = make_copy_data(self.bti_tab.bti.image_data)
    texture.palette_data = make_copy_data(self.bti_tab.bti.palette_data)
    
    texture.save_header_changes()
    
    # Update texture size displayed in the UI.
    texture_total_size = 0
    texture_total_size += data_len(texture.image_data)
    texture_total_size += data_len(texture.palette_data)
    texture_size_str = self.window().stringify_number(texture_total_size, min_hex_chars=5)
    
    item = self.get_jpc_tree_item_by_texture(texture)
    item.setText(self.j3d_col_name_to_index["Size"], texture_size_str)
