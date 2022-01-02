
import os
import re
import traceback
from io import BytesIO
from fs_helpers import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from wwlib.j3d import J3DFile, BPRegister, XFRegister
from gcft_ui.uic.ui_j3d_tab import Ui_J3DTab

class J3DTab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_J3DTab()
    self.ui.setupUi(self)
    
    self.j3d = None
    self.j3d_name = None
    self.ui.j3d_chunks_tree.setColumnWidth(1, 200)
    self.ui.j3d_chunks_tree.setColumnWidth(2, 70)
    
    self.j3d_col_name_to_index = {}
    for col in range(self.ui.j3d_chunks_tree.columnCount()):
      column_name = self.ui.j3d_chunks_tree.headerItem().text(col)
      self.j3d_col_name_to_index[column_name] = col
    
    self.ui.export_j3d.setDisabled(True)
    
    self.ui.import_j3d.clicked.connect(self.import_j3d)
    self.ui.export_j3d.clicked.connect(self.export_j3d)
    
    self.ui.j3d_chunks_tree.itemSelectionChanged.connect(self.widget_item_selected)
    
    self.ui.j3d_chunks_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.j3d_chunks_tree.customContextMenuRequested.connect(self.show_j3d_chunks_tree_context_menu)
    self.ui.actionOpenJ3DImage.triggered.connect(self.open_image_in_j3d)
    self.ui.actionReplaceJ3DImage.triggered.connect(self.replace_image_in_j3d)
  
  
  def import_j3d(self):
    filters = [
      "All J3D files (*.bmd *.bdl *.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)",
      "Models and material tables (*.bmd *.bdl *.bmt)",
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
    self.j3d_mdl_entry_to_tree_widget_item = {}
    self.j3d_tree_widget_item_to_mdl_entry = {}
    self.j3d_keyframe_to_tree_widget_item = {}
    self.j3d_tree_widget_item_to_keyframe = {}
    
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
            texture_total_size += pad_offset_to_nearest(data_len(texture.image_data), 0x20)
            seen_image_data_offsets.append(texture.image_data_offset+texture.header_offset)
          if texture.palette_data_offset+texture.header_offset not in seen_palette_data_offsets:
            texture_total_size += pad_offset_to_nearest(data_len(texture.palette_data), 0x20)
            seen_palette_data_offsets.append(texture.palette_data_offset+texture.header_offset)
          
          if texture_total_size == 0:
            texture_size_str = ""
          else:
            texture_size_str = self.window().stringify_number(texture_total_size, min_hex_chars=5)
          
          texture_item = QTreeWidgetItem(["", texture_name, texture_size_str])
          chunk_item.addChild(texture_item)
          
          self.j3d_texture_to_tree_widget_item[texture] = texture_item
          self.j3d_tree_widget_item_to_texture[texture_item] = texture
      elif chunk.magic == "MAT3":
        for mat_name in chunk.mat_names:
          mat_item = QTreeWidgetItem(["", mat_name, ""])
          chunk_item.addChild(mat_item)
      elif chunk.magic == "MDL3":
        for i, mdl_entry in enumerate(chunk.entries):
          mat_name = self.j3d.mat3.mat_names[i]
          mat_item = QTreeWidgetItem(["", mat_name, ""])
          chunk_item.addChild(mat_item)
          
          self.j3d_mdl_entry_to_tree_widget_item[mdl_entry] = mat_item
          self.j3d_tree_widget_item_to_mdl_entry[mat_item] = mdl_entry
      elif chunk.magic == "TRK1":
        chunk_item.setExpanded(True)
        for anim_type_index, anim_type_dict in enumerate([chunk.mat_name_to_reg_anims, chunk.mat_name_to_konst_anims]):
          anim_type_item = QTreeWidgetItem(["", ["Register", "Konstant"][anim_type_index], ""])
          chunk_item.addChild(anim_type_item)
          anim_type_item.setExpanded(True)
          for mat_name, anims in anim_type_dict.items():
            mat_item = QTreeWidgetItem(["", mat_name, ""])
            anim_type_item.addChild(mat_item)
            for anim_index, anim in enumerate(anims):
              anim_item = QTreeWidgetItem(["", "0x%02X" % anim_index, ""])
              mat_item.addChild(anim_item)
              for track_name in ["r", "g", "b", "a"]:
                track = getattr(anim, track_name)
                track_item = QTreeWidgetItem(["", track_name.upper(), ""])
                anim_item.addChild(track_item)
                track_item.setExpanded(True)
                for keyframe_index, keyframe in enumerate(track.keyframes):
                  keyframe_item = QTreeWidgetItem(["", "0x%02X" % keyframe_index, ""])
                  track_item.addChild(keyframe_item)
                  
                  self.j3d_keyframe_to_tree_widget_item[keyframe] = keyframe_item
                  self.j3d_tree_widget_item_to_keyframe[keyframe_item] = keyframe
    
    # Expand all items in the tree (for debugging):
    #for item in self.ui.j3d_chunks_tree.findItems("*", Qt.MatchFlag.MatchWildcard | Qt.MatchFlag.MatchRecursive):
    #  item.setExpanded(True)
  
  def widget_item_selected(self):
    layout = self.ui.scrollAreaWidgetContents.layout()
    while layout.count():
      item = layout.takeAt(0)
      widget = item.widget()
      if widget:
        widget.deleteLater()
    self.ui.j3d_sidebar_label.setText("Extra information will be displayed here as necessary.")
    
    selected_items = self.ui.j3d_chunks_tree.selectedItems()
    if not selected_items:
      return
    item = selected_items[0]
    
    mdl_entry = self.j3d_tree_widget_item_to_mdl_entry.get(item)
    if mdl_entry:
      self.mdl_entry_selected(mdl_entry)
      return
    
    keyframe = self.j3d_tree_widget_item_to_keyframe.get(item)
    if keyframe:
      self.keyframe_selected(keyframe)
      return
  
  def mdl_entry_selected(self, mdl_entry):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    entry_index = self.j3d.mdl3.entries.index(mdl_entry)
    mat_name = self.j3d.mat3.mat_names[entry_index]
    self.ui.j3d_sidebar_label.setText("Showing material display list for: %s" % mat_name)
    
    label = QLabel()
    label.setText("BP commands:")
    layout.addWidget(label)
    for bp_command in mdl_entry.bp_commands:
      if bp_command.register in [entry.value for entry in BPRegister]:
        reg_name = BPRegister(bp_command.register).name
      else:
        reg_name = "0x%02X" % bp_command.register
      command_text = "%s: 0x%08X" % (reg_name, bp_command.value)
      label = QLabel()
      label.setText(command_text)
      layout.addWidget(label)
    
    label = QLabel()
    label.setText("XF commands:")
    layout.addWidget(label)
    for xf_command in mdl_entry.xf_commands:
      if xf_command.register in [entry.value for entry in XFRegister]:
        reg_name = XFRegister(xf_command.register).name
      else:
        reg_name = "0x%04X" % xf_command.register
      command_text = "%s: %s" % (reg_name, ", ".join(["0x%08X" % arg for arg in xf_command.args]))
      label = QLabel()
      label.setText(command_text)
      layout.addWidget(label)
  
  def keyframe_selected(self, keyframe):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.j3d_sidebar_label.setText("Showing animation keyframe.")
    
    label = QLabel()
    label.setText("Time: %d" % keyframe.time)
    layout.addWidget(label)
    
    label = QLabel()
    label.setText("Value: %d" % keyframe.value)
    layout.addWidget(label)
    
    label = QLabel()
    label.setText("Tangent in: %d" % keyframe.tangent_in)
    layout.addWidget(label)
    
    label = QLabel()
    label.setText("Tangent out: %d" % keyframe.tangent_out)
    layout.addWidget(label)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
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
  
  def show_j3d_chunks_tree_context_menu(self, pos):
    if self.j3d is None:
      return
    
    item = self.ui.j3d_chunks_tree.itemAt(pos)
    if item is None:
      return
    
    texture = self.j3d_tree_widget_item_to_texture.get(item)
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
    texture = self.ui.actionReplaceJ3DImage.data()
    
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
    
    item = self.j3d_texture_to_tree_widget_item.get(texture)
    item.setText(self.j3d_col_name_to_index["Size"], texture_size_str)
    
    texture_index = self.j3d.tex1.textures.index(texture)
    texture_name = self.j3d.tex1.texture_names[texture_index]
    self.window().ui.statusbar.showMessage("Replaced %s." % texture_name, 3000)
