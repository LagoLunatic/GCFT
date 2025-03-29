
import os
from io import BytesIO
import re
import traceback
from typing import Any
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *
from gcft_paths import ASSETS_PATH

from gclib import fs_helpers as fs
from gclib.bunfoe import BUNFOE
from gclib import gx_enums as GX
from gclib.j3d import J3D
from gclib.jchunk import JChunk
from gclib.animation import AnimationKeyframe
from gclib.j3d_chunks.inf1 import INF1, INF1Node, INF1NodeType
from gclib.j3d_chunks.vtx1 import VTX1, VertexFormat
from gclib.j3d_chunks.evp1 import EVP1
from gclib.j3d_chunks.drw1 import DRW1
from gclib.j3d_chunks.jnt1 import JNT1
from gclib.j3d_chunks.shp1 import SHP1
from gclib.j3d_chunks.mat3 import MAT3, Material
from gclib.j3d_chunks.mdl3 import MDL3, MDLEntry, BPRegister, XFRegister
from gclib.j3d_chunks.mdl_command import MDLCommand
import gclib.j3d_chunks.bp_command as BP
import gclib.j3d_chunks.xf_command as XF
from gclib.j3d_chunks.tex1 import TEX1
from gclib.j3d_chunks.trk1 import TRK1, ColorAnimation
from gclib.j3d_chunks.ttk1 import TTK1, UVAnimation
from gclib.bti import BTI

from gcft_ui.bunfoe_editor import BunfoeEditor, BunfoeWidget, BunfoeDialog
from gcft_ui.gcft_common import RecursiveFilterProxyModel

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_j3d_tab import Ui_J3DTab
else:
  Ui_J3DTab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "j3d_tab.ui"))

class J3DTab(BunfoeEditor):
  def __init__(self):
    super().__init__()
    self.ui = Ui_J3DTab()
    self.ui.setupUi(self)
    
    self.j3d: J3D | None = None
    self.j3d_name = None
    self.model_loaded = False
    
    self.column_names = [
      "Chunk Type",
      "Name",
      "Size",
    ]
    
    self.model = QStandardItemModel()
    self.model.setHorizontalHeaderLabels(self.column_names)
    self.model.setColumnCount(len(self.column_names))
    self.proxy = RecursiveFilterProxyModel()
    self.proxy.setSourceModel(self.model)
    self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    
    self.ui.j3d_chunks_tree.setModel(self.proxy)
    self.selection_model = self.ui.j3d_chunks_tree.selectionModel()
    
    self.ui.filter.textChanged.connect(self.filter_rows)
    
    # TODO: save to settings file?
    self.chunk_type_is_expanded = {
      "TEX1": True,
      "MAT3": True,
      "MDL3": False,
      "TRK1": True,
    }
    
    self.isolated_visibility = False
    
    self.ui.export_j3d.setDisabled(True)
    self.ui.load_anim.setDisabled(True)
    
    self.ui.import_j3d.clicked.connect(self.import_j3d)
    self.ui.export_j3d.clicked.connect(self.export_j3d)
    
    self.ui.load_anim.clicked.connect(self.load_anim)
    
    self.selection_model.currentChanged.connect(self.widget_item_selected)
    self.ui.j3d_chunks_tree.expanded.connect(self.item_expanded)
    self.ui.j3d_chunks_tree.collapsed.connect(self.item_collapsed)
    
    self.ui.j3d_chunks_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.ui.j3d_chunks_tree.customContextMenuRequested.connect(self.show_j3d_chunks_tree_context_menu)
    self.ui.actionOpenJ3DImage.triggered.connect(self.open_image_in_j3d)
    self.ui.actionReplaceJ3DImage.triggered.connect(self.replace_image_in_j3d)
    
    self.ui.j3d_viewer.joint_anim_frame_changed.connect(self.ui.joint_anim_control.update_slider_from_anim_frame)
    self.ui.j3d_viewer.reg_anim_frame_changed.connect(self.ui.reg_anim_control.update_slider_from_anim_frame)
    self.ui.j3d_viewer.texidx_anim_frame_changed.connect(self.ui.texidx_anim_control.update_slider_from_anim_frame)
    self.ui.j3d_viewer.texmtx_anim_frame_changed.connect(self.ui.texmtx_anim_control.update_slider_from_anim_frame)
    self.ui.j3d_viewer.vis_anim_frame_changed.connect(self.ui.vis_anim_control.update_slider_from_anim_frame)
    
    self.ui.j3d_viewer.error_showing_preview.connect(self.display_j3d_preview_error)
    self.ui.j3d_viewer.hide()
    self.ui.j3dultra_error_area.hide()
    
    self.field_value_changed.connect(self.update_j3d_preview)
    self.ui.update_j3d_preview.clicked.connect(self.update_j3d_preview)
    self.ui.update_j3d_preview.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
    self.ui.toggle_visibility.clicked.connect(self.toggle_isolated_visibility)
    self.icon_visible_all = QIcon(os.path.join(ASSETS_PATH, "visible_all.png"))
    self.icon_visible_isolated = QIcon(os.path.join(ASSETS_PATH, "visible_isolated.png"))
    self.ui.toggle_visibility.setIcon(self.icon_visible_all)
    # This is just the max size, doesn't need to be exact.
    self.ui.toggle_visibility.setIconSize(QSize(32, 8))
    
    # Make the splitter start out evenly split between all three widgets.
    # TODO: the J3D preview column should be collapsed whenever the preview is not visible
    self.ui.splitter.setSizes([250, 500, 500])
    
    self.anim_controls = [
      self.ui.joint_anim_control,
      self.ui.reg_anim_control,
      self.ui.texidx_anim_control,
      self.ui.texmtx_anim_control,
      self.ui.vis_anim_control,
    ]
    for anim_control in self.anim_controls:
      anim_control.anim_type_paused_changed.connect(self.ui.j3d_viewer.set_anim_type_paused)
      anim_control.anim_type_slider_frame_changed.connect(self.ui.j3d_viewer.set_anim_frame_by_type)
      anim_control.anim_type_detached.connect(self.ui.j3d_viewer.detach_anim_type)
  
  def import_j3d(self):
    filters = [
      "All J3D files (*.bmd *.bdl *.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)",
      "Models and material tables (*.bmd *.bdl *.bmt)",
    ]
    
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.import_j3d_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="J3D file", file_filters=filters,
    )
  
  def export_j3d(self):
    assert self.j3d is not None
    
    filters = []
    current_filter = self.get_file_filter_by_current_j3d_file_type()
    if current_filter is not None:
      filters.append(current_filter)
    filters.append("All J3D files (*.bmd *.bdl *.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)")
    
    j3d_name = "%s.%s" % (self.j3d_name, self.j3d.file_type[:3])
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_j3d_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="J3D file", file_filters=filters,
      default_file_name=j3d_name
    )
  
  def load_anim(self):
    filters = []
    filters.append("J3D animations (*.bmt *.bls *.btk *.bck *.brk *.bpk *.btp *.bca *.bva *.bla)")
    
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.load_anim_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="J3D animation", file_filters=filters,
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
    
    for anim_control in self.anim_controls:
      # Detach anims for the previously loaded model.
      anim_control.hide()
      anim_control.detach_anim()
    
    self.j3d = j3d
    
    self.j3d_name = j3d_name
    
    self.model_loaded = False
    if self.j3d.file_type[:3] in ["bmd", "bdl"]:
      self.model_loaded = True
    
    self.reload_j3d_chunks_tree()
    
    self.try_show_model_preview(reload_same_model=False)
    
    self.ui.export_j3d.setDisabled(False)
    self.ui.load_anim.setDisabled(not self.model_loaded)
  
  def load_anim_by_data(self, data, anim_name):
    j3d = J3D(data)
    duration = None
    if j3d.file_type[:3] == "bck":
      bck = j3d
      duration = bck.ank1.duration
      if self.ui.j3d_viewer.load_bck(bck):
        self.ui.joint_anim_control.load_anim(duration, "BCK (Keyframed Joint Animation)", anim_name)
    elif j3d.file_type[:3] == "brk":
      brk = j3d
      duration = brk.trk1.duration
      if self.ui.j3d_viewer.load_brk(brk):
        self.ui.reg_anim_control.load_anim(duration, "BRK (Register Color Animation)", anim_name)
    elif j3d.file_type[:3] == "btk":
      btk = j3d
      duration = btk.ttk1.duration
      if self.ui.j3d_viewer.load_btk(btk):
        self.ui.texmtx_anim_control.load_anim(duration, "BTK (Texture Matrix Animation)", anim_name)
    elif j3d.file_type[:3] == "btp":
      btp = j3d
      duration = btp.tpt1.duration
      if self.ui.j3d_viewer.load_btp(btp):
        self.ui.texidx_anim_control.load_anim(duration, "BTP (Texture Swap Animation)", anim_name)
    elif j3d.file_type[:3] == "bca":
      bca = j3d
      duration = bca.anf1.duration
      if self.ui.j3d_viewer.load_bca(bca):
        self.ui.joint_anim_control.load_anim(duration, "BCA (Full Joint Animation)", anim_name)
    elif j3d.file_type[:3] == "bva":
      bva = j3d
      duration = bva.vaf1.duration
      if self.ui.j3d_viewer.load_bva(bva):
        self.ui.vis_anim_control.load_anim(duration, "BVA (Visibility Animation)", anim_name)
    else:
      QMessageBox.warning(self, "Unsupported animation type", f"Previewing animations of type {j3d.file_type!r} is not currently supported.")
  
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
    assert self.j3d is not None
    
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
    assert self.j3d is not None
    
    self.model.removeRows(0, self.model.rowCount())
    
    if self.isolated_visibility:
      self.toggle_isolated_visibility(update_preview=False)
    
    for chunk in self.j3d.chunks:
      chunk_size_str = self.gcft_window.stringify_number(chunk.size, min_hex_chars=5)
      
      chunk_item = QStandardItem(chunk.magic)
      chunk_item.setEditable(False)
      name_item = QStandardItem("")
      name_item.setEditable(False)
      size_item = QStandardItem(chunk_size_str)
      size_item.setEditable(False)
      self.model.appendRow([chunk_item, name_item, size_item])
      self.set_object_for_model_index(chunk_item.index(), chunk)
      if self.chunk_type_is_expanded.get(chunk.magic, False):
        self.expand_item(chunk_item)
      
      if isinstance(chunk, INF1):
        self.add_inf1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, VTX1):
        self.add_vtx1_chunk_to_tree(chunk, chunk_item)
      # elif isinstance(chunk, EVP1):
      #   self.add_evp1_chunk_to_tree(chunk, chunk_item)
      # elif isinstance(chunk, DRW1):
      #   self.add_drw1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, JNT1):
        self.add_jnt1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, SHP1):
        self.add_shp1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, MAT3):
        self.add_mat3_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, MDL3):
        self.add_mdl3_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, TEX1):
        self.add_tex1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, TRK1):
        self.add_trk1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, TTK1):
        self.add_ttk1_chunk_to_tree(chunk, chunk_item)
    
    self.ui.j3d_chunks_tree.setColumnWidth(self.column_names.index("Name"), 170)
    self.ui.j3d_chunks_tree.setColumnWidth(self.column_names.index("Size"), 60)
    
    # Expand all items in the tree (for debugging):
    # for item in self.model.findItems("*", Qt.MatchFlag.MatchWildcard | Qt.MatchFlag.MatchRecursive):
    #   self.expand_item(item)
  
  def make_tree_model_item(self, obj, parent_item: QStandardItem, item_args: list[str], expanded=False):
    assert len(item_args) == 3
    chunk_type_arg, name_arg, size_arg = item_args
    chunk_item = QStandardItem(chunk_type_arg)
    chunk_item.setEditable(False)
    name_item = QStandardItem(name_arg)
    name_item.setEditable(False)
    size_item = QStandardItem(size_arg)
    size_item.setEditable(False)
    parent_item.appendRow([chunk_item, name_item, size_item])
    self.set_object_for_model_index(chunk_item.index(), obj)
    if expanded:
      self.expand_item(chunk_item)
    
    return chunk_item
  
  def item_expanded(self, index: QModelIndex):
    index = self.proxy.mapToSource(index)
    obj = self.get_object_for_model_index(index)
    if isinstance(obj, JChunk):
      self.chunk_type_is_expanded[obj.magic] = True
  
  def item_collapsed(self, index: QModelIndex):
    index = self.proxy.mapToSource(index)
    obj = self.get_object_for_model_index(index)
    if isinstance(obj, JChunk):
      self.chunk_type_is_expanded[obj.magic] = False
  
  def widget_item_selected(self, current_index: QModelIndex, previous_index: QModelIndex):
    layout = self.ui.scrollAreaWidgetContents.layout()
    self.clear_layout_recursive(layout)
    
    self.ui.j3d_sidebar_label.setText("Extra information will be displayed here as necessary.")
    
    if not current_index.isValid():
      return
    current_index = self.proxy.mapToSource(current_index)
    obj = self.get_object_for_model_index(current_index)
    
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
    elif isinstance(obj, INF1Node):
      self.inf1_node_selected(obj)
    elif isinstance(obj, BUNFOE):
      self.bunfoe_instance_selected(obj)
    
    if self.isolated_visibility:
      self.update_j3d_preview()
    
    # profiler.disable()
    # with open("profileresults.txt", "w") as f:
    #   ps = pstats.Stats(profiler, stream=f).sort_stats("cumulative")
    #   ps.print_stats()
  
  
  def add_inf1_chunk_to_tree(self, inf1: INF1, chunk_item: QStandardItem):
    root_node = inf1.flat_hierarchy[0]
    self.add_inf1_node_to_tree_recursive(root_node, chunk_item)
  
  def add_inf1_node_to_tree_recursive(self, inf1_node: INF1Node, parent_item: QStandardItem):
    type_name = None
    names_list = None
    if inf1_node.type == INF1NodeType.JOINT:
      type_name = "Joint"
      names_list = self.j3d.jnt1.joint_names
    elif inf1_node.type == INF1NodeType.MATERIAL:
      if self.j3d.mat3 is not None:
        type_name = "Material"
        names_list = self.j3d.mat3.mat_names
    elif inf1_node.type == INF1NodeType.SHAPE:
      type_name = "Shape"
      names_list = self.j3d.shp1.shape_names
    
    index_str = self.gcft_window.stringify_number(inf1_node.index, min_hex_chars=2)
    if type_name is None:
      node_name = ""
    elif names_list is None:
      node_name = f"{type_name} {index_str}"
    else:
      node_name = f"{type_name} {index_str}: {names_list[inf1_node.index]}"
    
    node_item = self.make_tree_model_item(inf1_node, parent_item, [node_name, node_name, ""], expanded=True)
    
    for child_node in inf1_node.children:
      self.add_inf1_node_to_tree_recursive(child_node, node_item)
  
  def add_vtx1_chunk_to_tree(self, vtx1: VTX1, chunk_item: QStandardItem):
    for vtx_fmt in vtx1.vertex_formats:
      if vtx_fmt.attribute_type == GX.Attr.NULL:
        vtx_fmt_size_str = ""
      else:
        vtx_fmt_size = vtx_fmt.component_size * vtx_fmt.component_count * len(vtx1.attributes[vtx_fmt.attribute_type])
        vtx_fmt_size_str = self.gcft_window.stringify_number(vtx_fmt_size, min_hex_chars=2)
      self.make_tree_model_item(vtx_fmt, chunk_item, ["", vtx_fmt.attribute_type.name, vtx_fmt_size_str])
  
  # def add_evp1_chunk_to_tree(self, evp1: EVP1, chunk_item: QStandardItem):
  #   pass
  
  # def add_drw1_chunk_to_tree(self, drw1: DRW1, chunk_item: QStandardItem):
  #   pass
  
  def add_jnt1_chunk_to_tree(self, jnt1: JNT1, chunk_item: QStandardItem):
    for joint_index, joint in enumerate(jnt1.joints):
      joint_index_str = self.gcft_window.stringify_number(joint_index, min_hex_chars=2)
      joint_name = jnt1.joint_names[joint_index]
      self.make_tree_model_item(joint, chunk_item, ["", f"{joint_index_str}: {joint_name}", ""])
  
  def add_shp1_chunk_to_tree(self, shp1: SHP1, chunk_item: QStandardItem):
    for shape_index, shape in enumerate(shp1.shapes):
      shape_index_str = self.gcft_window.stringify_number(shape_index, min_hex_chars=2)
      self.make_tree_model_item(shape, chunk_item, ["", shape_index_str, ""])
  
  def add_mat3_chunk_to_tree(self, mat3: MAT3, chunk_item: QStandardItem):
    for mat_index, material in enumerate(mat3.materials):
      mat_name = mat3.mat_names[mat_index]
      mat_item = self.make_tree_model_item(material, chunk_item, ["", mat_name, ""])
      if len(mat3.indirects) != 0:
        indirect = mat3.indirects[mat_index]
        self.make_tree_model_item(indirect, mat_item, ["", f"Indirect Texturing", ""])
  
  def add_mdl3_chunk_to_tree(self, mdl3: MDL3, chunk_item: QStandardItem):
    for i, mdl_entry in enumerate(mdl3.entries):
      mat_name = self.j3d.mat3.mat_names[i]
      self.make_tree_model_item(mdl_entry, chunk_item, ["", mat_name, ""])
  
  def add_tex1_chunk_to_tree(self, tex1: TEX1, chunk_item: QStandardItem):
    seen_image_data_offsets = []
    seen_palette_data_offsets = []
    
    for i, texture in enumerate(tex1.textures):
      texture_name = tex1.texture_names[i]
      
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
        texture_size_str = self.gcft_window.stringify_number(texture_total_size, min_hex_chars=5)
      
      self.make_tree_model_item(texture, chunk_item, ["", texture_name, texture_size_str])
  
  def add_trk1_chunk_to_tree(self, trk1: TRK1, chunk_item: QStandardItem):
    for anim_type_index, anim_type_dict in enumerate([trk1.mat_name_to_reg_anims, trk1.mat_name_to_konst_anims]):
      anim_type = ["Register", "Konstant"][anim_type_index]
      anim_type_item = self.make_tree_model_item(None, chunk_item, ["", anim_type, ""], True)
      for mat_name, anims in anim_type_dict.items():
        mat_item = self.make_tree_model_item(None, anim_type_item, ["", mat_name, ""])
        for anim_index, anim in enumerate(anims):
          anim_item = self.make_tree_model_item(anim, mat_item, ["", "0x%02X" % anim_index, ""])
          for track_name in ["r", "g", "b", "a"]:
            track_item = self.make_tree_model_item(None, anim_item, ["", track_name.upper(), ""], True)
            track = getattr(anim, track_name)
            for keyframe_index, keyframe in enumerate(track.keyframes):
              self.make_tree_model_item(keyframe, track_item, ["", "0x%02X" % keyframe_index, ""])
  
  def add_ttk1_chunk_to_tree(self, ttk1: TTK1, chunk_item: QStandardItem):
    self.expand_item(chunk_item)
    for mat_name, anims in ttk1.mat_name_to_anims.items():
      mat_item = self.make_tree_model_item(None, chunk_item, ["", mat_name, ""])
      for anim_index, anim in enumerate(anims):
        anim_item = self.make_tree_model_item(anim, mat_item, ["", "0x%02X" % anim_index, ""])
        for track_name, track in anim.tracks.items():
          track_item = self.make_tree_model_item(track, anim_item, ["", track_name.upper(), ""], True)
          for keyframe_index, keyframe in enumerate(track.keyframes):
            self.make_tree_model_item(keyframe, track_item, ["", "0x%02X" % keyframe_index, ""])
  
  def expand_item(self, item: QStandardItem):
    self.ui.j3d_chunks_tree.expand(self.proxy.mapFromSource(item.index()))
  
  def set_object_for_model_index(self, index: QModelIndex, obj: Any):
    chunk_type_index = index.siblingAtColumn(self.column_names.index("Chunk Type"))
    item = self.model.itemFromIndex(chunk_type_index)
    item.setData(obj)
  
  def get_object_for_model_index(self, index: QModelIndex) -> Any:
    chunk_type_index = index.siblingAtColumn(self.column_names.index("Chunk Type"))
    item = self.model.itemFromIndex(chunk_type_index)
    obj = item.data()
    assert obj is not None
    return obj
  
  def filter_rows(self):
    query = self.ui.filter.text()
    self.proxy.setFilterFixedString(query)
  
  
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
  
  def mdl_entry_selected(self, mdl_entry: MDLEntry):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    entry_index = self.j3d.mdl3.entries.index(mdl_entry)
    mat_name = self.j3d.mat3.mat_names[entry_index]
    sidebar_label_text = "Showing material display list for: %s" % mat_name
    sidebar_label_text += "\n(MDL3 is generated automatically from MAT3.)"
    self.ui.j3d_sidebar_label.setText(sidebar_label_text)
    
    bp_commands_widget = QWidget()
    bp_commands_layout = QFormLayout(bp_commands_widget)
    xf_commands_widget = QWidget()
    xf_commands_layout = QFormLayout(xf_commands_widget)
    
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
        reg_name = f"0x{bp_command.register:02X}"
      
      command_text = f"0x{bp_command.bitfield:06X}"
      field_widget = QPushButton(command_text)
      field_widget.setProperty('mdl_command', bp_command)
      field_widget.setSizePolicy(QSizePolicy.Policy.Maximum, field_widget.sizePolicy().verticalPolicy())
      field_widget.clicked.connect(self.open_mdl_command_editor)
      
      bp_commands_layout.addRow(reg_name, field_widget)
    
    for xf_command in mdl_entry.xf_commands:
      if xf_command.register in [entry.value for entry in XFRegister]:
        reg_name = XFRegister(xf_command.register).name
      else:
        reg_name = f"0x{xf_command.register:04X}"
      
      command_text = ", ".join([f"0x{arg.bitfield:08X}" for arg in xf_command.args])
      field_widget = QPushButton(command_text)
      field_widget.setProperty('mdl_command', xf_command)
      field_widget.setSizePolicy(QSizePolicy.Policy.Maximum, field_widget.sizePolicy().verticalPolicy())
      field_widget.clicked.connect(self.open_mdl_command_editor)
      
      xf_commands_layout.addRow(reg_name, field_widget)
  
  def open_mdl_command_editor(self):
    button: QPushButton = self.sender()
    mdl_command: MDLCommand = button.property('mdl_command')
    # print(mdl_command)
    
    dialog = BunfoeDialog.show_dialog_for_bunfoe(mdl_command, self, "Edit MDL Command")
    dialog.finished.connect(lambda result: self.mdl_command_editor_closed(mdl_command, button))
  
  def mdl_command_editor_closed(self, mdl_command: MDLCommand, button: QPushButton):
    # Update the text on the button.
    self.j3d.mdl3.save()
    if isinstance(mdl_command, BP.BPCommand):
      command_text = f"0x{mdl_command.bitfield:06X}"
    elif isinstance(mdl_command, XF.XFCommand):
      command_text = ", ".join([f"0x{arg.bitfield:08X}" for arg in mdl_command.args])
    button.setText(command_text)
  
  def keyframe_selected(self, keyframe: AnimationKeyframe):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.j3d_sidebar_label.setText("Showing animation keyframe.")
    
    form_widget = QWidget()
    form_layout = QFormLayout(form_widget)
    form_layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(form_widget)
    
    form_layout.addRow("Time", QLabel(f"{keyframe.time:f}"))
    
    form_layout.addRow("Value", QLabel(f"{keyframe.value:f}"))
    
    form_layout.addRow("Tangent in", QLabel(f"{keyframe.tangent_in:f}"))
    
    form_layout.addRow("Tangent out", QLabel(f"{keyframe.tangent_out:f}"))
  
  def uv_anim_selected(self, uv_anim: UVAnimation):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.j3d_sidebar_label.setText("Showing UV animation.")
    
    form_widget = QWidget()
    form_layout = QFormLayout(form_widget)
    form_layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(form_widget)
    
    form_layout.addRow("Center", QLabel("(%f, %f, %f)" % uv_anim.center_coords))
    
    form_layout.addRow("Tex gen index", QLabel(f"0x{uv_anim.tex_gen_index:02X}"))
  
  def color_anim_selected(self, color_anim: ColorAnimation):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.j3d_sidebar_label.setText("Showing color animation.")
    
    form_widget = QWidget()
    form_layout = QFormLayout(form_widget)
    form_layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(form_widget)
    
    form_layout.addRow("Color ID", QLabel(f"0x{color_anim.color_id:02X}"))
    
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
  
  def inf1_node_selected(self, inf1_node: INF1Node):
    # When an INF1 node is selected, we want to allow editing the corresponding object referenced by
    # that node, not the node itself.
    if inf1_node.type == INF1NodeType.JOINT:
      node_to_select = self.j3d.jnt1.joints[inf1_node.index]
    elif inf1_node.type == INF1NodeType.MATERIAL:
      node_to_select = self.j3d.mat3.materials[inf1_node.index]
    elif inf1_node.type == INF1NodeType.SHAPE:
      node_to_select = self.j3d.shp1.shapes[inf1_node.index]
    else:
      # Fall back to showing the INF1 node itself if something went wrong.
      node_to_select = inf1_node
    
    self.bunfoe_instance_selected(node_to_select)
  
  
  def export_j3d_by_path(self, j3d_path):
    assert self.j3d is not None
    
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
  
  def show_j3d_chunks_tree_context_menu(self, pos: QPoint):
    if self.j3d is None:
      return
    
    index = self.ui.j3d_chunks_tree.indexAt(pos)
    if not index.isValid():
      return
    item = self.model.itemFromIndex(self.proxy.mapToSource(index))
    if item is None:
      return
    
    obj = self.get_object_for_model_index(item.index())
    
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
    texture: BTI = self.ui.actionOpenJ3DImage.data()
    
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
    
    self.gcft_window.set_tab_by_name("BTI Images")
  
  def replace_image_in_j3d(self):
    assert self.j3d is not None
    
    texture: BTI = self.ui.actionReplaceJ3DImage.data()
    
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
    self.gcft_window.ui.statusbar.showMessage("Replaced %s." % texture_name, 3000)
  
  def try_show_model_preview(self, *, reload_same_model: bool):
    assert self.j3d is not None
    
    self.ui.j3dultra_error_area.hide()
    self.ui.j3d_viewer.load_model(self.j3d, reload_same_model, self.get_hidden_material_indexes())
  
  def update_j3d_preview(self):
    if self.j3d is None:
      return
    
    # # TODO: implement copying just the instance, without having to serialize and deserialize it here.
    # success = self.try_save_j3d()
    # if not success:
    #   return
    
    self.try_show_model_preview(reload_same_model=True)
  
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
    assert self.j3d is not None
    
    indexes = []
    if not self.isolated_visibility:
      return indexes
    if self.j3d.mat3 is None:
      return indexes
    
    selected_model_indexes = self.ui.j3d_chunks_tree.selectedIndexes()
    selected_mat_indexes = []
    for model_index in selected_model_indexes:
      model_index = self.proxy.mapToSource(model_index)
      obj = self.get_object_for_model_index(model_index)
      if not isinstance(obj, Material):
        continue
      mat_index = self.j3d.mat3.materials.index(obj)
      selected_mat_indexes.append(mat_index)
    if not selected_mat_indexes:
      return indexes
    
    for mat_index in range(len(self.j3d.mat3.materials)):
      if mat_index not in selected_mat_indexes:
        indexes.append(mat_index)
    return indexes
