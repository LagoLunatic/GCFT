
import os
from io import BytesIO
import re
import traceback
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from gcft_paths import ASSETS_PATH

from gclib import fs_helpers as fs
from gclib.bunfoe import BUNFOE
from gclib import gx_enums as GX
from gclib.j3d import J3D
from gclib.jchunk import JChunk
from gclib.j3d_chunks.vtx1 import VertexFormat
from gclib.j3d_chunks.mat3 import Material
from gclib.animation import AnimationKeyframe
from gclib.j3d_chunks.mdl3 import MDLEntry, BPRegister, XFRegister
from gclib.j3d_chunks.trk1 import ColorAnimation
from gclib.j3d_chunks.ttk1 import UVAnimation
from gclib.bti import BTI

from gcft_ui.uic.ui_j3d_tab import Ui_J3DTab
from gcft_ui.bunfoe_editor import BunfoeEditor, BunfoeWidget

class J3DTab(BunfoeEditor):
  def __init__(self):
    super().__init__()
    self.ui = Ui_J3DTab()
    self.ui.setupUi(self)
    
    self.j3d = None
    self.j3d_name = None
    self.model_loaded = False
    self.ui.j3d_chunks_tree.setColumnWidth(1, 200)
    self.ui.j3d_chunks_tree.setColumnWidth(2, 70)
    
    self.j3d_col_name_to_index = {}
    for col in range(self.ui.j3d_chunks_tree.columnCount()):
      column_name = self.ui.j3d_chunks_tree.headerItem().text(col)
      self.j3d_col_name_to_index[column_name] = col
    
    # TODO: save to settings file?
    self.chunk_type_is_expanded = {
      "TEX1": True,
      "MAT3": True,
      "TRK1": True,
    }
    
    self.isolated_visibility = False
    
    self.ui.export_j3d.setDisabled(True)
    self.ui.load_anim.setDisabled(True)
    
    self.ui.import_j3d.clicked.connect(self.import_j3d)
    self.ui.export_j3d.clicked.connect(self.export_j3d)
    
    self.ui.load_anim.clicked.connect(self.load_anim)
    
    self.ui.j3d_chunks_tree.itemSelectionChanged.connect(self.widget_item_selected)
    self.ui.j3d_chunks_tree.itemExpanded.connect(self.item_expanded)
    self.ui.j3d_chunks_tree.itemCollapsed.connect(self.item_collapsed)
    
    self.ui.j3d_chunks_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.j3d_chunks_tree.customContextMenuRequested.connect(self.show_j3d_chunks_tree_context_menu)
    self.ui.actionOpenJ3DImage.triggered.connect(self.open_image_in_j3d)
    self.ui.actionReplaceJ3DImage.triggered.connect(self.replace_image_in_j3d)
    
    self.ui.j3d_viewer.error_showing_preview.connect(self.display_j3d_preview_error)
    self.ui.j3d_viewer.hide()
    self.ui.j3dultra_error_area.hide()
    
    self.field_value_changed.connect(self.update_j3d_preview)
    self.ui.update_j3d_preview.clicked.connect(self.update_j3d_preview)
    self.ui.update_j3d_preview.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
    self.ui.toggle_visibility.clicked.connect(self.toggle_isolated_visibility)
    self.icon_visible_all = QIcon(os.path.join(ASSETS_PATH, "visible_all.png"))
    self.icon_visible_isolated = QIcon(os.path.join(ASSETS_PATH, "visible_isolated.png"))
    self.ui.toggle_visibility.setIcon(self.icon_visible_all)
    # This is just the max size, doesn't need to be exact.
    self.ui.toggle_visibility.setIconSize(QSize(32, 8))
    
    # Make the splitter start out evenly split between all three widgets.
    # TODO: the J3D preview column should be collapsed whenever the preview is not visible
    self.ui.splitter.setSizes([2**30, 2**30, 2**30])
    
    # self.ui.anim_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
    self.ui.anim_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
    self.ui.anim_slider.valueChanged.connect(self.update_anim_frame)
  
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
  
  def load_anim(self):
    filters = []
    filters.append("J3D animations (*.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)")
    
    self.window().generic_do_gui_file_operation(
      op_callback=self.load_anim_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="J3D animation", file_filter=";;".join(filters),
    )
  
  
  def import_j3d_by_path(self, j3d_path):
    with open(j3d_path, "rb") as f:
      data = BytesIO(f.read())
    
    j3d_name = os.path.splitext(os.path.basename(j3d_path))[0]
    
    self.import_j3d_by_data(data, j3d_name)
  
  def import_j3d_by_data(self, data, j3d_name):
    j3d = self.try_read_j3d(data)
    if j3d is None:
      return
    self.j3d = j3d
    
    self.j3d_name = j3d_name
    
    self.model_loaded = False
    if self.j3d.file_type[:3] in ["bmd", "bdl"]:
      self.model_loaded = True
    
    self.reload_j3d_chunks_tree()
    
    self.try_show_model_preview(True)
    
    self.ui.export_j3d.setDisabled(False)
    self.ui.load_anim.setDisabled(not self.model_loaded)
  
  def load_anim_by_data(self, data, anim_name):
    j3d = J3D(data)
    if j3d.file_type[:3] != "brk":
      return
    brk = j3d
    
    self.ui.j3d_viewer.load_brk(brk)
    
    self.ui.anim_slider.setMinimum(0)
    self.ui.anim_slider.setMaximum(brk.trk1.duration-1)
    self.ui.anim_slider.setValue(0)
  
  def update_anim_frame(self, frame: int):
    self.ui.j3d_viewer.set_anim_frame(frame)
  
  def try_read_j3d(self, data):
    try:
      return J3D(data)
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message_title = "Failed to load J3D"
      error_message = "Failed to load J3D with error:\n%s\n\n%s" % (str(e), stack_trace)
      QMessageBox.critical(self, error_message_title, error_message)
      return None
  
  def try_save_j3d(self):
    try:
      self.j3d.save()
      return True
    except Exception as e:
      stack_trace = traceback.format_exc()
      error_message_title = "Failed to save J3D"
      error_message = "Failed to save J3D with error:\n%s\n\n%s" % (str(e), stack_trace)
      QMessageBox.critical(self, error_message_title, error_message)
      return False
  
  def reload_j3d_chunks_tree(self):
    self.ui.j3d_chunks_tree.clear()
    
    if self.isolated_visibility:
      self.toggle_isolated_visibility(update_preview=False)
    
    self.tree_widget_item_to_object = {}
    
    for chunk in self.j3d.chunks:
      chunk_size_str = self.window().stringify_number(chunk.size, min_hex_chars=5)
      
      chunk_item = QTreeWidgetItem([chunk.magic, "", chunk_size_str])
      self.ui.j3d_chunks_tree.addTopLevelItem(chunk_item)
      
      self.tree_widget_item_to_object[chunk_item] = chunk
      
      chunk_item.setExpanded(self.chunk_type_is_expanded.get(chunk.magic, False))
      
      if chunk.magic == "TEX1":
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
        for mat_index, material in enumerate(chunk.materials):
          mat_name = chunk.mat_names[mat_index]
          mat_item = self.make_tree_widget_item(material, chunk_item, ["", mat_name, ""])
          indirect = chunk.indirects[mat_index]
          self.make_tree_widget_item(indirect, mat_item, ["", f"Indirect Texturing", ""])
      elif chunk.magic == "MDL3":
        for i, mdl_entry in enumerate(chunk.entries):
          mat_name = self.j3d.mat3.mat_names[i]
          self.make_tree_widget_item(mdl_entry, chunk_item, ["", mat_name, ""])
      elif chunk.magic == "TRK1":
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
      elif chunk.magic == "JNT1":
        for joint_index, joint in enumerate(chunk.joints):
          joint_index_str = self.window().stringify_number(joint_index, min_hex_chars=2)
          joint_name = chunk.joint_names[joint_index]
          self.make_tree_widget_item(joint, chunk_item, ["", f"{joint_index_str}: {joint_name}", ""])
      elif chunk.magic == "SHP1":
        for shape_index, shape in enumerate(chunk.shapes):
          shape_index_str = self.window().stringify_number(shape_index, min_hex_chars=2)
          self.make_tree_widget_item(shape, chunk_item, ["", shape_index_str, ""])
      elif chunk.magic == "VTX1":
        for vtx_fmt in chunk.vertex_formats:
          if vtx_fmt.attribute_type == GX.Attr.NULL:
            vtx_fmt_size_str = ""
          else:
            vtx_fmt_size = vtx_fmt.component_size * vtx_fmt.component_count * len(chunk.attributes[vtx_fmt.attribute_type])
            vtx_fmt_size_str = self.window().stringify_number(vtx_fmt_size, min_hex_chars=2)
          self.make_tree_widget_item(vtx_fmt, chunk_item, ["", vtx_fmt.attribute_type.name, vtx_fmt_size_str])
      elif chunk.magic == "INF1":
        for node_index, inf1_node in enumerate(chunk.flat_hierarchy):
          node_index_str = self.window().stringify_number(node_index, min_hex_chars=2)
          self.make_tree_widget_item(inf1_node, chunk_item, ["", node_index_str, ""])
    
    # Expand all items in the tree (for debugging):
    #for item in self.ui.j3d_chunks_tree.findItems("*", Qt.MatchFlag.MatchWildcard | Qt.MatchFlag.MatchRecursive):
    #  item.setExpanded(True)
  
  def make_tree_widget_item(self, obj, parent, item_args, expanded=False):
    item = QTreeWidgetItem(item_args)
    parent.addChild(item)
    item.setExpanded(expanded)
    
    if obj is not None:
      self.tree_widget_item_to_object[item] = obj
    
    return item
  
  def item_expanded(self, item):
    obj = self.tree_widget_item_to_object.get(item)
    if isinstance(obj, JChunk):
      self.chunk_type_is_expanded[obj.magic] = True
  
  def item_collapsed(self, item):
    obj = self.tree_widget_item_to_object.get(item)
    if isinstance(obj, JChunk):
      self.chunk_type_is_expanded[obj.magic] = False
  
  def widget_item_selected(self):
    layout = self.ui.scrollAreaWidgetContents.layout()
    self.clear_layout_recursive(layout)
    
    self.ui.j3d_sidebar_label.setText("Extra information will be displayed here as necessary.")
    
    
    selected_items = self.ui.j3d_chunks_tree.selectedItems()
    if not selected_items:
      return
    item = selected_items[0]
    obj = self.tree_widget_item_to_object.get(item)
    
    # import cProfile, pstats
    # profiler = cProfile.Profile()
    # profiler.enable()
    
    if isinstance(obj, MDLEntry):
      self.mdl_entry_selected(obj)
    elif isinstance(obj, AnimationKeyframe):
      self.keyframe_selected(obj)
    elif isinstance(obj, UVAnimation):
      self.uv_anim_selected(obj)
    elif isinstance(obj, ColorAnimation):
      self.color_anim_selected(obj)
    elif isinstance(obj, VertexFormat):
      self.vertex_format_selected(obj)
    elif isinstance(obj, BUNFOE):
      self.bunfoe_instance_selected(obj)
    
    if self.isolated_visibility:
      self.update_j3d_preview()
    
    # profiler.disable()
    # with open("profileresults.txt", "w") as f:
    #   ps = pstats.Stats(profiler, stream=f).sort_stats("cumulative")
    #   ps.print_stats()
  
  def bunfoe_instance_selected(self, instance, text=None, disabled=False):
    if text:
      self.ui.j3d_sidebar_label.setText(f"Showing {text}.")
    else:
      cls_name = instance.__class__.__name__
      # Split camel case words.
      cls_name_words = re.split(r"(?<=[a-z])(?=[A-Z])", cls_name)
      cls_name_spaced = " ".join(cls_name_words)
      if re.search(r"[a-z]", cls_name_spaced):
        # Lowercase but only if the name isn't all uppercase letters.
        cls_name_spaced = cls_name_spaced.lower()
      self.ui.j3d_sidebar_label.setText(f"Showing {cls_name_spaced}.")
    
    layout: QBoxLayout = self.ui.scrollAreaWidgetContents.layout()
    
    bunfoe_editor_widget = super().setup_editor_widget_for_bunfoe_instance(instance, disabled=disabled)
    
    layout.addWidget(bunfoe_editor_widget)
    layout.addStretch(1)
    
    return bunfoe_editor_widget
  
  def mdl_entry_selected(self, mdl_entry):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
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
  
  def vertex_format_selected(self, vtx_fmt: VertexFormat):
    # TODO: j3dultra segfaults if you try changing, say, an attribute type from tex0 to tex1 for
    # example (many other cases too). need to disable editing these.
    
    widget = self.bunfoe_instance_selected(vtx_fmt, "vertex format")
    
    for i in range(widget.layout().rowCount()):
      field_item = widget.layout().itemAt(i, QFormLayout.ItemRole.FieldRole)
      field_widget = field_item.widget()
      if field_widget.property('access_path') == [('attr', 'attribute_type')]:
        combobox: QComboBox = field_widget
        combobox.currentIndexChanged.connect(self.update_vertex_format_component_type_combobox)
    
    self.update_vertex_format_component_type_combobox()
  
  def update_vertex_format_component_type_combobox(self):
    # The component type combobox needs to have the text of its items updated dynamically depending
    # on what the currently selected attribute type is.
    # If a color attribute type is selected, display the duplicate enum names for color types.
    # Otherwise, display the duplicate enum names for number types.
    
    layout = self.ui.scrollAreaWidgetContents.layout()
    if layout.count() <= 0:
      return
    bunfoe_widget = layout.itemAt(0).widget()
    if not isinstance(bunfoe_widget, BunfoeWidget):
      return
    
    vtx_fmt = bunfoe_widget.property('bunfoe_instance')
    assert isinstance(vtx_fmt, VertexFormat)
    
    if vtx_fmt.is_color_attr:
      # Colors are at the end of GX.ComponentType's members, so go through the list forwards, so that the
      # later members overwrite the earlier ones in the dict.
      enum_value_order = {v: k for k, v in GX.ComponentType.__members__.items()}
    else:
      # Numbers are at the start of GX.ComponentType's members, so go through the list backwards, so that
      # the earlier members overwrite the later ones in the dict.
      enum_value_order = {v: k for k, v in reversed(GX.ComponentType.__members__.items())}
    
    for i in range(bunfoe_widget.layout().rowCount()):
      field_item = bunfoe_widget.layout().itemAt(i, QFormLayout.ItemRole.FieldRole)
      field_widget = field_item.widget()
      if field_widget.property('access_path') == [('attr', 'component_type')]:
        combobox = field_widget
        for i in range(combobox.count()):
          enum_value = combobox.itemData(i)
          pretty_name = self.prettify_name(enum_value_order[enum_value], title=False)
          combobox.setItemText(i, pretty_name)
  
  
  def export_j3d_by_path(self, j3d_path):
    success = self.try_save_j3d()
    if not success:
      return
    
    with open(j3d_path, "wb") as f:
      self.j3d.data.seek(0)
      f.write(self.j3d.data.read())
    
    self.j3d_name = os.path.splitext(os.path.basename(j3d_path))[0]
    
    QMessageBox.information(self, "J3D file saved", "Successfully saved J3D file.")
  
  def load_anim_by_path(self, anim_path):
    with open(anim_path, "rb") as f:
      data = BytesIO(f.read())
    
    anim_name = os.path.splitext(os.path.basename(anim_path))[0]
    
    self.load_anim_by_data(data, anim_name)
  
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
    
    # Do a full reload in order to update texture size displayed in the UI.
    self.reload_j3d_chunks_tree()
    
    self.update_j3d_preview()
    
    texture_index = self.j3d.tex1.textures.index(texture)
    texture_name = self.j3d.tex1.texture_names[texture_index]
    self.window().ui.statusbar.showMessage("Replaced %s." % texture_name, 3000)
  
  def try_show_model_preview(self, reset_camera=False):
    self.ui.j3dultra_error_area.hide()
    self.ui.j3d_viewer.load_model(self.j3d, reset_camera, self.get_hidden_material_indexes())
  
  def update_j3d_preview(self):
    if self.j3d is None:
      return
    
    # TODO: implement copying just the instance, without having to serialize and deserialize it here.
    success = self.try_save_j3d()
    if not success:
      return
    
    self.try_show_model_preview(False)
  
  def update_j3d_preview(self):
    if self.j3d is None:
      return
    self.try_show_model_preview(False)
  
  def display_j3d_preview_error(self, error: str):
    self.ui.j3dultra_error_area.show()
    self.ui.j3dultra_error_label.setText(error)
    self.ui.j3d_viewer.hide()
  
  def toggle_isolated_visibility(self, checked=None, update_preview=True):
    self.isolated_visibility = not self.isolated_visibility
    if self.isolated_visibility:
      self.ui.toggle_visibility.setIcon(self.icon_visible_isolated)
    else:
      self.ui.toggle_visibility.setIcon(self.icon_visible_all)
    if update_preview:
      self.update_j3d_preview()
  
  def get_hidden_material_indexes(self):
    indexes = []
    if not self.isolated_visibility:
      return indexes
    
    selected_items = self.ui.j3d_chunks_tree.selectedItems()
    selected_mat_indexes = []
    for item in selected_items:
      if not isinstance(self.tree_widget_item_to_object.get(item), Material):
        continue
      mat_index = self.ui.j3d_chunks_tree.indexFromItem(item).row()
      selected_mat_indexes.append(mat_index)
    if not selected_mat_indexes:
      return indexes
    
    for mat_index in range(len(self.j3d.mat3.materials)):
      if mat_index not in selected_mat_indexes:
        indexes.append(mat_index)
    return indexes
