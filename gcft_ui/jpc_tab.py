
import os
import re
import traceback
from io import BytesIO
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.jpc import JPC, JPAChunk, JParticle
from gclib.jpa_chunks.bsp1 import BSP1, ColorAnimationKeyframe
from gclib.jpa_chunks.ssp1 import SSP1
from gclib.jpa_chunks.tdb1 import TDB1
from gclib.jpa_chunks.tex1 import TEX1
from gcft_ui.uic.ui_jpc_tab import Ui_JPCTab

class JPCFilterProxyModel(QSortFilterProxyModel):
  def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
    # Only filter top-level rows (the particles), not the child rows.
    if source_parent.isValid():
      return True
    return super().filterAcceptsRow(source_row, source_parent)

class JPCTab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_JPCTab()
    self.ui.setupUi(self)
    
    self.jpc = None
    self.jpc_name = None
    
    self.item_model = QStandardItemModel()
    self.proxy_model = JPCFilterProxyModel()
    self.proxy_model.setSourceModel(self.item_model)
    self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    
    self.ui.jpc_particles_tree.setColumnWidth(0, 100)
    self.ui.jpc_particles_tree.setModel(self.proxy_model)
    self.ui.jpc_particles_tree.setRootIndex(self.item_model.index(0, 0))
    self.selection_model = self.ui.jpc_particles_tree.selectionModel()
    self.ui.jpc_particles_tree.setHeaderHidden(True)
    
    self.ui.export_jpc.setDisabled(True)
    self.ui.add_particles_from_folder.setDisabled(True)
    self.ui.export_jpc_folder.setDisabled(True)
    
    self.ui.import_jpc.clicked.connect(self.import_jpc)
    self.ui.export_jpc.clicked.connect(self.export_jpc)
    self.ui.add_particles_from_folder.clicked.connect(self.add_particles_from_folder)
    self.ui.export_jpc_folder.clicked.connect(self.export_jpc_folder)
    
    self.selection_model.selectionChanged.connect(self.widget_item_selected)
    self.ui.filter_particles.textChanged.connect(self.filter_particles)
    
    self.ui.jpc_particles_tree.setContextMenuPolicy(Qt.CustomContextMenu)
    self.ui.jpc_particles_tree.customContextMenuRequested.connect(self.show_jpc_particles_tree_context_menu)
    self.ui.actionOpenJPCImage.triggered.connect(self.open_image_in_jpc)
    self.ui.actionReplaceJPCImage.triggered.connect(self.replace_image_in_jpc)
  
  
  def import_jpc(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.import_jpc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="JPC", file_filter="JPC Files (*.jpc)"
    )
  
  def export_jpc(self):
    jpc_name = self.jpc_name + ".jpc"
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_jpc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="JPC", file_filter="JPC Files (*.jpc)",
      default_file_name=jpc_name
    )
  
  def add_particles_from_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.add_particles_from_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="JPC"
    )
  
  def export_jpc_folder(self):
    self.window().generic_do_gui_file_operation(
      op_callback=self.export_jpc_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="JPC"
    )
  
  
  def import_jpc_by_path(self, jpc_path):
    with open(jpc_path, "rb") as f:
      data = BytesIO(f.read())
    
    jpc_name = os.path.splitext(os.path.basename(jpc_path))[0]
    
    self.import_jpc_by_data(data, jpc_name)
  
  def import_jpc_by_data(self, data, jpc_name):
    self.jpc = JPC(data)
    
    self.jpc_name = jpc_name
    
    self.reload_jpc_particles_tree()
    
    self.ui.export_jpc.setDisabled(False)
    self.ui.add_particles_from_folder.setDisabled(False)
    self.ui.export_jpc_folder.setDisabled(False)
  
  def reload_jpc_particles_tree(self):
    self.item_model.removeRows(0, self.item_model.rowCount())
    
    for particle in self.jpc.particles:
      particle_id_str = self.window().stringify_number(particle.particle_id, min_hex_chars=4)
      
      particle_item = QStandardItem(particle_id_str)
      particle_item.setData(particle)
      self.item_model.appendRow(particle_item)
      
      for chunk in particle.chunks:
        #chunk_size_str = self.window().stringify_number(chunk.size, min_hex_chars=5)
        
        chunk_item = QStandardItem(chunk.magic)
        chunk_item.setData(chunk)
        particle_item.appendRow(chunk_item)
        
        if isinstance(chunk, BSP1):
          self.add_bsp1_chunk_to_tree(chunk, chunk_item)
        elif isinstance(chunk, SSP1):
          self.add_ssp1_chunk_to_tree(chunk, chunk_item)
        elif isinstance(chunk, TDB1):
          self.add_tdb1_chunk_to_tree(chunk, chunk_item)
  
  def filter_particles(self):
    query = self.ui.filter_particles.text()
    self.proxy_model.setFilterFixedString(query)
  
  def widget_item_selected(self):
    layout = self.ui.scrollAreaWidgetContents.layout()
    while layout.count():
      item = layout.takeAt(0)
      widget = item.widget()
      if widget:
        widget.deleteLater()
    self.ui.jpc_sidebar_label.setText("Extra information will be displayed here as necessary.")
    
    selected_indexes = self.selection_model.selectedRows()
    if not selected_indexes:
      return
    selected_index = self.proxy_model.mapToSource(selected_indexes[0])
    item = self.item_model.itemFromIndex(selected_index)
    if item is None:
      return
    
    data = item.data()
    if isinstance(data, JPAChunk):
      chunk = data
      if chunk.magic == "BSP1":
        self.bsp1_chunk_selected(chunk)
        return
      elif chunk.magic == "SSP1":
        self.ssp1_chunk_selected(chunk)
        return
    elif isinstance(data, ColorAnimationKeyframe):
      keyframe = data
      self.color_anim_keyframe_selected(keyframe)
      return
  
  
  def add_bsp1_chunk_to_tree(self, bsp1: BSP1, chunk_item: QStandardItem):
    if bsp1.color_prm_anm_table:
      anim_item = QStandardItem("Color PRM Anim")
      chunk_item.appendRow(anim_item)
      for keyframe_index, keyframe in enumerate(bsp1.color_prm_anm_table):
        keyframe_item = QStandardItem("0x%02X" % keyframe_index)
        keyframe_item.setData(keyframe)
        anim_item.appendRow(keyframe_item)
    
    if bsp1.color_env_anm_table:
      anim_item = QStandardItem("Color ENV Anim")
      chunk_item.appendRow(anim_item)
      for keyframe_index, keyframe in enumerate(bsp1.color_env_anm_table):
        keyframe_item = QStandardItem("0x%02X" % keyframe_index)
        keyframe_item.setData(keyframe)
        anim_item.appendRow(keyframe_item)
  
  def add_ssp1_chunk_to_tree(self, ssp1: SSP1, chunk_item: QStandardItem):
    pass
  
  def add_tdb1_chunk_to_tree(self, tdb1: TDB1, chunk_item: QStandardItem):
    # Expand TDB1 chunks by default.
    chunk_index = self.proxy_model.mapFromSource(self.item_model.indexFromItem(chunk_item))
    self.ui.jpc_particles_tree.expand(chunk_index)
    
    for texture_filename in tdb1.texture_filenames:
      texture = self.jpc.textures_by_filename[texture_filename]
      texture_item = QStandardItem(texture_filename)
      texture_item.setData(texture)
      chunk_item.appendRow(texture_item)
  
  
  def bsp1_chunk_selected(self, bsp1):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing BSP1 (Base Shape) chunk.")
    
    self.window().make_color_selector_button(bsp1, "color_prm", "Color PRM", layout)
    self.window().make_color_selector_button(bsp1, "color_env", "Color ENV", layout)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def ssp1_chunk_selected(self, ssp1):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing SSP1 (Child Shape) chunk.")
    
    self.window().make_color_selector_button(ssp1, "color_prm", "Color PRM", layout)
    self.window().make_color_selector_button(ssp1, "color_env", "Color ENV", layout)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def color_anim_keyframe_selected(self, keyframe):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing color animation keyframe.")
    
    label = QLabel()
    label.setText("Time: %d" % keyframe.time)
    layout.addWidget(label)
    
    self.window().make_color_selector_button(keyframe, "color", "Color", layout)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def export_jpc_by_path(self, jpc_path):
    self.jpc.save()
    
    with open(jpc_path, "wb") as f:
      self.jpc.data.seek(0)
      f.write(self.jpc.data.read())
    
    self.jpc_name = os.path.splitext(os.path.basename(jpc_path))[0]
    
    QMessageBox.information(self, "JPC saved", "Successfully saved JPC.")
  
  def add_particles_from_folder_by_path(self, folder_path):
    num_particles_added, num_particles_overwritten, num_textures_added, num_textures_overwritten = self.jpc.import_particles_from_disk(folder_path)
    
    if num_particles_added == num_particles_overwritten == num_textures_added == num_textures_overwritten == 0:
      QMessageBox.warning(self, "No matching files found", "The selected folder does not contain any files with the extension .jpa. No particles imported.")
      return
    
    self.reload_jpc_particles_tree()
    
    QMessageBox.information(self, "Folder imported", "Successfully imported particles from \"%s\".\n\nStats:\nParticles added: %d\nParticles overwritten: %d\nTextures added: %d\nTextures overwritten: %d" % (folder_path, num_particles_added, num_particles_overwritten, num_textures_added, num_textures_overwritten))
  
  def export_jpc_folder_by_path(self, folder_path):
    self.jpc.extract_all_particles_to_disk(output_directory=folder_path)
    
    QMessageBox.information(self, "JPC extracted", "Successfully extracted all JPA particles from the JPC to \"%s\"." % folder_path)
  
  
  def show_jpc_particles_tree_context_menu(self, pos):
    if self.jpc is None:
      return
    
    index = self.ui.jpc_particles_tree.indexAt(pos)
    if not index.isValid():
      return
    item = self.item_model.itemFromIndex(self.proxy_model.mapToSource(index))
    if item is None:
      return
    
    data = item.data()
    if isinstance(data, TEX1):
      texture = data
      particle_item = item.parent().parent()
      particle: JParticle = particle_item.data()
      
      menu = QMenu(self)
      
      menu.addAction(self.ui.actionOpenJPCImage)
      self.ui.actionOpenJPCImage.setData(texture)
        
      menu.addAction(self.ui.actionReplaceJPCImage)
      self.ui.actionReplaceJPCImage.setData((particle, texture))
      if self.bti_tab.bti is None:
        self.ui.actionReplaceJPCImage.setDisabled(True)
      else:
        self.ui.actionReplaceJPCImage.setDisabled(False)
      
      menu.exec_(self.ui.jpc_particles_tree.mapToGlobal(pos))
  
  def open_image_in_jpc(self):
    texture = self.ui.actionOpenJPCImage.data()
    
    # Need to make a fake standalone BTI texture data so we can load it without it being the TEX1 format.
    data = BytesIO()
    bti_header_bytes = fs.read_bytes(texture.bti.data, texture.bti.header_offset, 0x20)
    fs.write_bytes(data, 0x00, bti_header_bytes)
    
    bti_image_data = fs.read_all_bytes(texture.bti.image_data)
    fs.write_bytes(data, 0x20, bti_image_data)
    image_data_offset = 0x20
    fs.write_u32(data, 0x1C, image_data_offset)
    
    if fs.data_len(texture.bti.palette_data) == 0:
      palette_data_offset = 0
    else:
      bti_palette_data = fs.read_all_bytes(texture.bti.palette_data)
      fs.write_bytes(data, 0x20 + fs.data_len(texture.bti.image_data), bti_palette_data)
      palette_data_offset = 0x20 + fs.data_len(texture.bti.image_data)
    fs.write_u32(data, 0x0C, palette_data_offset)
    
    self.bti_tab.import_bti_by_data(data, texture.filename)
    
    self.window().set_tab_by_name("BTI Images")
  
  def replace_image_in_jpc(self):
    particle, texture = self.ui.actionReplaceJPCImage.data()
    
    num_particles_sharing_texture = 0
    for other_particle in self.jpc.particles:
      for other_texture_id in other_particle.tdb1.texture_ids:
        other_texture = self.jpc.textures[other_texture_id]
        if other_texture == texture:
          num_particles_sharing_texture += 1
    
    if num_particles_sharing_texture > 1:
      # TODO: Add an option to create a new texture for this particle and replace that, so that editing the texture for all particles isn't the only choice.
      message = "The texture you are about to replace, '%s', is used by %d different particles in this JPC. If you replace it, it will affect all %d of those particles.\n\nAre you sure you want to replace this texture?" % (texture.filename, num_particles_sharing_texture, num_particles_sharing_texture)
      response = QMessageBox.question(self, 
        "Texture used by multiple particles",
        message,
        QMessageBox.Cancel | QMessageBox.Yes,
        QMessageBox.Cancel
      )
      if response != QMessageBox.Yes:
        return
    
    self.bti_tab.bti.save_changes()
    
    # Need to make a fake BTI header for it to read from.
    data = BytesIO()
    bti_header_bytes = fs.read_bytes(self.bti_tab.bti.data, self.bti_tab.bti.header_offset, 0x20)
    fs.write_bytes(data, 0x00, bti_header_bytes)
    
    texture.bti.read_header(data)
    
    texture.bti.image_data = fs.make_copy_data(self.bti_tab.bti.image_data)
    texture.bti.palette_data = fs.make_copy_data(self.bti_tab.bti.palette_data)
    
    texture.bti.save_header_changes()
    
    self.window().ui.statusbar.showMessage("Replaced %s." % texture.filename, 3000)
