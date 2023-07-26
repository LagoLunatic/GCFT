
import os
import re
import traceback
from io import BytesIO
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.j3d import J3DFile, BPRegister, XFRegister
from gclib.j3d import MDLEntry, AnimationKeyframe, ColorAnimation, UVAnimation
from gclib.bti import BTI
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
    
    self.object_to_tree_widget_item = {}
    self.tree_widget_item_to_object = {}
    
    for chunk in self.j3d.chunks:
      chunk_size_str = self.window().stringify_number(chunk.size, min_hex_chars=5)
      
      chunk_item = QTreeWidgetItem([chunk.magic, "", chunk_size_str])
      self.ui.j3d_chunks_tree.addTopLevelItem(chunk_item)
      
      self.object_to_tree_widget_item[chunk] = chunk_item
      self.tree_widget_item_to_object[chunk_item] = chunk
      
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
            texture_total_size += fs.pad_offset_to_nearest(fs.data_len(texture.image_data), 0x20)
            seen_image_data_offsets.append(texture.image_data_offset+texture.header_offset)
          if texture.palette_data_offset+texture.header_offset not in seen_palette_data_offsets:
            texture_total_size += fs.pad_offset_to_nearest(fs.data_len(texture.palette_data), 0x20)
            seen_palette_data_offsets.append(texture.palette_data_offset+texture.header_offset)
          
          if texture_total_size == 0:
            texture_size_str = ""
          else:
            texture_size_str = self.window().stringify_number(texture_total_size, min_hex_chars=5)
          
          self.make_tree_widget_item(texture, chunk_item, ["", texture_name, texture_size_str])
      elif chunk.magic == "MAT3":
        for mat_name in chunk.mat_names:
          self.make_tree_widget_item(None, chunk_item, ["", mat_name, ""])
      elif chunk.magic == "MDL3":
        for i, mdl_entry in enumerate(chunk.entries):
          mat_name = self.j3d.mat3.mat_names[i]
          self.make_tree_widget_item(mdl_entry, chunk_item, ["", mat_name, ""])
      elif chunk.magic == "TRK1":
        chunk_item.setExpanded(True)
        for anim_type_index, anim_type_dict in enumerate([chunk.mat_name_to_reg_anims, chunk.mat_name_to_konst_anims]):
          anim_type = ["Register", "Konstant"][anim_type_index]
          anim_type_item = self.make_tree_widget_item(None, chunk_item, ["", anim_type, ""], True)
          for mat_name, anims in anim_type_dict.items():
            mat_item = self.make_tree_widget_item(None, anim_type_item, ["", mat_name, ""])
            for anim_index, anim in enumerate(anims):
              anim_item = self.make_tree_widget_item(anim, mat_item, ["", "0x%02X" % anim_index, ""])
              for track_name in ["r", "g", "b", "a"]:
                track_item = self.make_tree_widget_item(None, anim_item, ["", track_name.upper(), ""], True)
                track = getattr(anim, track_name)
                for keyframe_index, keyframe in enumerate(track.keyframes):
                  self.make_tree_widget_item(keyframe, track_item, ["", "0x%02X" % keyframe_index, ""])
      elif chunk.magic == "TTK1":
        chunk_item.setExpanded(True)
        for mat_name, anims in chunk.mat_name_to_anims.items():
          mat_item = self.make_tree_widget_item(None, chunk_item, ["", mat_name, ""])
          for anim_index, anim in enumerate(anims):
            anim_item = self.make_tree_widget_item(anim, mat_item, ["", "0x%02X" % anim_index, ""])
            for track_name, track in anim.tracks.items():
              track_item = self.make_tree_widget_item(track, anim_item, ["", track_name.upper(), ""], True)
              for keyframe_index, keyframe in enumerate(track.keyframes):
                self.make_tree_widget_item(keyframe, track_item, ["", "0x%02X" % keyframe_index, ""])
    
    # Expand all items in the tree (for debugging):
    #for item in self.ui.j3d_chunks_tree.findItems("*", Qt.MatchFlag.MatchWildcard | Qt.MatchFlag.MatchRecursive):
    #  item.setExpanded(True)
  
  def make_tree_widget_item(self, obj, parent, item_args, expanded=False):
    item = QTreeWidgetItem(item_args)
    parent.addChild(item)
    item.setExpanded(expanded)
    
    if obj is not None:
      assert obj not in self.object_to_tree_widget_item
      self.object_to_tree_widget_item[obj] = item
      self.tree_widget_item_to_object[item] = obj
    
    return item
  
  def widget_item_selected(self):
    layout = self.ui.scrollAreaWidgetContents.layout()
    while layout.count():
      item = layout.takeAt(0)
      widget = item.widget()
      if widget:
        widget.deleteLater()
    self.ui.j3d_sidebar_label.setText("Extra information will be displayed here as necessary.")
    
    # Re-enable the main sidebar scrollarea by default in case it was disabled previously.
    self.ui.scrollArea.setWidgetResizable(True)
    
    selected_items = self.ui.j3d_chunks_tree.selectedItems()
    if not selected_items:
      return
    item = selected_items[0]
    obj = self.tree_widget_item_to_object.get(item)
    
    if isinstance(obj, MDLEntry):
      self.mdl_entry_selected(obj)
    elif isinstance(obj, AnimationKeyframe):
      self.keyframe_selected(obj)
    elif isinstance(obj, UVAnimation):
      self.uv_anim_selected(obj)
    elif isinstance(obj, ColorAnimation):
      self.color_anim_selected(obj)
  
  def mdl_entry_selected(self, mdl_entry):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    # Disable the main sidebar scrollarea since we will have two tabs with their own scrollareas instead.
    self.ui.scrollArea.setWidgetResizable(False)
    
    entry_index = self.j3d.mdl3.entries.index(mdl_entry)
    mat_name = self.j3d.mat3.mat_names[entry_index]
    self.ui.j3d_sidebar_label.setText("Showing material display list for: %s" % mat_name)
    
    bp_commands_widget = QWidget()
    bp_commands_layout = QVBoxLayout(bp_commands_widget)
    xf_commands_widget = QWidget()
    xf_commands_layout = QVBoxLayout(xf_commands_widget)
    
    bp_commands_scroll_area = QScrollArea()
    bp_commands_scroll_area.setWidgetResizable(True)
    bp_commands_scroll_area.setWidget(bp_commands_widget)
    
    xf_commands_scroll_area = QScrollArea()
    xf_commands_scroll_area.setWidgetResizable(True)
    xf_commands_scroll_area.setWidget(xf_commands_widget)
    
    tab_widget = QTabWidget()
    tab_widget.addTab(bp_commands_scroll_area, "BP Commands")
    tab_widget.addTab(xf_commands_scroll_area, "XF Commands")
    layout.addWidget(tab_widget)
    
    for bp_command in mdl_entry.bp_commands:
      if bp_command.register in [entry.value for entry in BPRegister]:
        reg_name = BPRegister(bp_command.register).name
      else:
        reg_name = "0x%02X" % bp_command.register
      command_text = "%s: 0x%06X" % (reg_name, bp_command.value)
      label = QLabel()
      label.setText(command_text)
      bp_commands_layout.addWidget(label)
    
    for xf_command in mdl_entry.xf_commands:
      if xf_command.register in [entry.value for entry in XFRegister]:
        reg_name = XFRegister(xf_command.register).name
      else:
        reg_name = "0x%04X" % xf_command.register
      command_text = "%s:\n%s" % (reg_name, "\n".join(["0x%08X" % arg for arg in xf_command.args]))
      label = QLabel()
      label.setText(command_text)
      xf_commands_layout.addWidget(label)
    
    bp_commands_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    xf_commands_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
  
  def keyframe_selected(self, keyframe):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.j3d_sidebar_label.setText("Showing animation keyframe.")
    
    label = QLabel()
    label.setText("Time: %f" % keyframe.time)
    layout.addWidget(label)
    
    label = QLabel()
    label.setText("Value: %f" % keyframe.value)
    layout.addWidget(label)
    
    label = QLabel()
    label.setText("Tangent in: %f" % keyframe.tangent_in)
    layout.addWidget(label)
    
    label = QLabel()
    label.setText("Tangent out: %f" % keyframe.tangent_out)
    layout.addWidget(label)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def uv_anim_selected(self, uv_anim):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.j3d_sidebar_label.setText("Showing UV animation.")
    
    label = QLabel()
    label.setText("Center: (%f, %f, %f)" % uv_anim.center_coords)
    layout.addWidget(label)
    
    label = QLabel()
    label.setText("Tex gen index: 0x%02X" % uv_anim.tex_gen_index)
    layout.addWidget(label)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def color_anim_selected(self, color_anim):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.j3d_sidebar_label.setText("Showing color animation.")
    
    label = QLabel()
    label.setText("Color ID: 0x%02X" % color_anim.color_id)
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
    obj = self.tree_widget_item_to_object.get(item)
    
    if isinstance(obj, BTI):
      texture = obj
      
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
    bti_header_bytes = fs.read_bytes(texture.data, texture.header_offset, 0x20)
    fs.write_bytes(data, 0x00, bti_header_bytes)
    
    bti_image_data = fs.read_all_bytes(texture.image_data)
    fs.write_bytes(data, 0x20, bti_image_data)
    image_data_offset = 0x20
    fs.write_u32(data, 0x1C, image_data_offset)
    
    if fs.data_len(texture.palette_data) == 0:
      palette_data_offset = 0
    else:
      bti_palette_data = fs.read_all_bytes(texture.palette_data)
      fs.write_bytes(data, 0x20 + fs.data_len(texture.image_data), bti_palette_data)
      palette_data_offset = 0x20 + fs.data_len(texture.image_data)
    fs.write_u32(data, 0x0C, palette_data_offset)
    
    texture_index = self.j3d.tex1.textures.index(texture)
    bti_name = self.j3d.tex1.texture_names[texture_index]
    
    self.bti_tab.import_bti_by_data(data, bti_name)
    
    self.window().set_tab_by_name("BTI Images")
  
  def replace_image_in_j3d(self):
    texture = self.ui.actionReplaceJ3DImage.data()
    
    self.bti_tab.bti.save_changes()
    
    # Need to make a fake BTI header for it to read from.
    data = BytesIO()
    bti_header_bytes = fs.read_bytes(self.bti_tab.bti.data, self.bti_tab.bti.header_offset, 0x20)
    fs.write_bytes(data, 0x00, bti_header_bytes)
    
    texture.read_header(data)
    
    texture.image_data = fs.make_copy_data(self.bti_tab.bti.image_data)
    texture.palette_data = fs.make_copy_data(self.bti_tab.bti.palette_data)
    
    texture.save_header_changes()
    
    # Update texture size displayed in the UI.
    texture_total_size = 0
    texture_total_size += fs.data_len(texture.image_data)
    texture_total_size += fs.data_len(texture.palette_data)
    texture_size_str = self.window().stringify_number(texture_total_size, min_hex_chars=5)
    
    item = self.j3d_texture_to_tree_widget_item.get(texture)
    item.setText(self.j3d_col_name_to_index["Size"], texture_size_str)
    
    texture_index = self.j3d.tex1.textures.index(texture)
    texture_name = self.j3d.tex1.texture_names[texture_index]
    self.window().ui.statusbar.showMessage("Replaced %s." % texture_name, 3000)
