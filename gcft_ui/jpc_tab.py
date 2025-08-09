
import os
import glob
from io import BytesIO
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.jpc import JPC
from gclib.jpa import JParticle
from gclib.jchunk import JPAChunk
from gclib.jpa_chunks.bem1 import BEM1
from gclib.jpa_chunks.bsp1 import BSP1, ColorAnimationKeyframe
from gclib.jpa_chunks.esp1 import ESP1
from gclib.jpa_chunks.etx1 import ETX1
from gclib.jpa_chunks.ssp1 import SSP1
# from gclib.jpa_chunks.fld1 import FLD1
# from gclib.jpa_chunks.kfa1 import KFA1
from gclib.jpa_chunks.tdb1 import TDB1
from gclib.jpa_chunks.tex1 import TEX1

from gcft_ui.bunfoe_editor import BunfoeEditor
from gcft_ui.gcft_common import RecursiveFilterProxyModel

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_jpc_tab import Ui_JPCTab
else:
  Ui_JPCTab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "jpc_tab.ui"))

class JPCTab(BunfoeEditor):
  def __init__(self):
    super().__init__()
    self.ui = Ui_JPCTab()
    self.ui.setupUi(self)
    
    self.jpc: JPC | None = None
    self.jpc_name = None
    
    self.model = QStandardItemModel()
    self.proxy = RecursiveFilterProxyModel()
    self.proxy.setSourceModel(self.model)
    self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    
    self.ui.jpc_particles_tree.setModel(self.proxy)
    self.selection_model = self.ui.jpc_particles_tree.selectionModel()
    self.ui.jpc_particles_tree.setHeaderHidden(True)
    
    self.selection_model.currentChanged.connect(self.widget_item_selected)
    self.ui.filter.textChanged.connect(self.filter_particles)
    
    self.ui.export_jpc.setDisabled(True)
    self.ui.add_particles_from_folder.setDisabled(True)
    self.ui.export_jpc_folder.setDisabled(True)
    self.ui.add_particle.setDisabled(True)
    
    self.ui.import_jpc.clicked.connect(self.import_jpc)
    self.ui.export_jpc.clicked.connect(self.export_jpc)
    self.ui.add_particles_from_folder.clicked.connect(self.add_particles_from_folder)
    self.ui.export_jpc_folder.clicked.connect(self.export_jpc_folder)
    self.ui.add_particle.clicked.connect(self.add_particle)
    
    self.ui.jpc_particles_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.ui.jpc_particles_tree.customContextMenuRequested.connect(self.show_jpc_particles_tree_context_menu)
    self.ui.actionExtract_Particle.triggered.connect(self.extract_particle)
    self.ui.actionReplace_Particle.triggered.connect(self.replace_particle)
    self.ui.actionDelete_Particle.triggered.connect(self.delete_particle)
    self.ui.actionOpenJPCImage.triggered.connect(self.open_image_in_jpc)
    self.ui.actionReplaceJPCImage.triggered.connect(self.replace_image_in_jpc)
  
  def get_particle_id_str(self, particle: JParticle):
    return self.gcft_window.stringify_number(particle.particle_id, min_hex_chars=4)
  
  
  def import_jpc(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.import_jpc_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="JPC", file_filters=["JPC Files (*.jpc)"],
    )
  
  def export_jpc(self):
    jpc_name = self.jpc_name + ".jpc"
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_jpc_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="JPC", file_filters=["JPC Files (*.jpc)"],
      default_file_name=jpc_name
    )
  
  def extract_particle(self):
    particle: JParticle = self.ui.actionExtract_Particle.data()
    particle_filename = "%04X.jpa" % particle.particle_id
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.extract_particle_by_path,
      is_opening=False, is_saving=True, is_folder=False,
      file_type="JPA", file_filters=["JPA Files (*.jpa)"],
      default_file_name=particle_filename
    )
  
  def replace_particle(self):
    particle: JParticle = self.ui.actionExtract_Particle.data()
    particle_filename = "%04X.jpa" % particle.particle_id
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.replace_particle_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="JPA", file_filters=["JPA Files (*.jpa)"],
      default_file_name=particle_filename
    )
  
  def add_particles_from_folder(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.add_particles_from_folder_by_path,
      is_opening=True, is_saving=False, is_folder=True,
      file_type="JPC"
    )
  
  def export_jpc_folder(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.export_jpc_folder_by_path,
      is_opening=False, is_saving=True, is_folder=True,
      file_type="JPC"
    )
  
  def add_particle(self):
    self.gcft_window.generic_do_gui_file_operation(
      op_callback=self.add_particle_by_path,
      is_opening=True, is_saving=False, is_folder=False,
      file_type="JPA", file_filters=["JPA Files (*.jpa)"],
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
    self.ui.add_particle.setDisabled(False)
  
  def reload_jpc_particles_tree(self):
    assert self.jpc is not None
    
    self.model.removeRows(0, self.model.rowCount())
    
    for particle in self.jpc.particles:
      self.add_new_tree_row_for_particle(particle)
    
    self.filter_particles()
  
  def add_new_tree_row_for_particle(self, particle: JParticle, row_index: int | None = None):
    particle_id_str = self.get_particle_id_str(particle)
    
    particle_item = QStandardItem(particle_id_str)
    particle_item.setData(particle)
    if row_index is None:
      # Add to the end by default.
      self.model.appendRow(particle_item)
    else:
      # Insert at a specific index.
      self.model.insertRow(row_index, particle_item)
    
    for chunk in particle.chunks:
      #chunk_size_str = self.gcft_window.stringify_number(chunk.size, min_hex_chars=5)
      
      chunk_item = QStandardItem(chunk.magic)
      chunk_item.setData(chunk)
      particle_item.appendRow(chunk_item)
      
      if isinstance(chunk, BEM1):
        self.add_bem1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, BSP1):
        self.add_bsp1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, ESP1):
        self.add_esp1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, ETX1):
        self.add_etx1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, SSP1):
        self.add_ssp1_chunk_to_tree(chunk, chunk_item)
      # elif isinstance(chunk, FLD1):
      #   self.add_fld1_chunk_to_tree(chunk, chunk_item)
      # elif isinstance(chunk, KFA1):
      #   self.add_kfa1_chunk_to_tree(chunk, chunk_item)
      elif isinstance(chunk, TDB1):
        self.add_tdb1_chunk_to_tree(chunk, chunk_item)
    
    return particle_item
  
  def expand_item(self, item: QStandardItem):
    self.ui.jpc_particles_tree.expand(self.proxy.mapFromSource(item.index()))
  
  def is_expanded(self, item: QStandardItem):
    return self.ui.jpc_particles_tree.isExpanded(self.proxy.mapFromSource(item.index()))
  
  def find_item_by_data(self, column, value):
    matched_indexes = self.model.match(
      self.model.index(0, column),
      Qt.ItemDataRole.UserRole + 1, # Equivalent to item.data()
      value,
      1,
      Qt.MatchFlag.MatchRecursive
    )
    assert len(matched_indexes) == 1
    return self.model.itemFromIndex(matched_indexes[0])
  
  def filter_particles(self):
    query = self.ui.filter.text()
    self.proxy.setFilterFixedString(query)
  
  def widget_item_selected(self, current_index: QModelIndex, previous_index: QModelIndex):
    layout = self.ui.scrollAreaWidgetContents.layout()
    self.clear_layout_recursive(layout)
    
    self.ui.jpc_sidebar_label.setText("Extra information will be displayed here as necessary.")
    
    if not current_index.isValid():
      return
    current_index = self.proxy.mapToSource(current_index)
    item = self.model.itemFromIndex(current_index)
    if item is None:
      return
    
    data = item.data()
    if isinstance(data, JPAChunk):
      chunk = data
      if isinstance(chunk, BEM1):
        self.bem1_chunk_selected(chunk)
        return
      elif isinstance(chunk, BSP1):
        self.bsp1_chunk_selected(chunk)
        return
      elif isinstance(chunk, ESP1):
        self.esp1_chunk_selected(chunk)
        return
      elif isinstance(chunk, ETX1):
        self.etx1_chunk_selected(chunk)
        return
      elif isinstance(chunk, SSP1):
        self.ssp1_chunk_selected(chunk)
        return
      # elif isinstance(chunk, FLD1):
      #   self.fld1_chunk_selected(chunk)
      #   return
      # elif isinstance(chunk, KFA1):
      #   self.kfa1_chunk_selected(chunk)
      #   return
      # elif isinstance(chunk, TDB1):
      #   self.tdb1_chunk_selected(chunk)
      #   return
    elif isinstance(data, ColorAnimationKeyframe):
      keyframe = data
      self.color_anim_keyframe_selected(keyframe)
      return
  
  
  def add_bem1_chunk_to_tree(self, bem1: BEM1, chunk_item: QStandardItem):
    assert self.jpc is not None
    
    pass
  
  def add_bsp1_chunk_to_tree(self, bsp1: BSP1, chunk_item: QStandardItem):
    assert self.jpc is not None
    
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
  
  def add_esp1_chunk_to_tree(self, esp1: ESP1, chunk_item: QStandardItem):
    assert self.jpc is not None
    
    pass
  
  def add_etx1_chunk_to_tree(self, etx1: ETX1, chunk_item: QStandardItem):
    assert self.jpc is not None
    
    pass
  
  def add_ssp1_chunk_to_tree(self, ssp1: SSP1, chunk_item: QStandardItem):
    assert self.jpc is not None
    
    pass
  
  def add_tdb1_chunk_to_tree(self, tdb1: TDB1, chunk_item: QStandardItem):
    assert self.jpc is not None
    
    # Expand TDB1 chunks by default.
    chunk_index = self.proxy.mapFromSource(self.model.indexFromItem(chunk_item))
    self.ui.jpc_particles_tree.expand(chunk_index)
    
    for texture_filename in tdb1.texture_filenames:
      texture = self.jpc.textures_by_filename[texture_filename]
      texture_item = QStandardItem(texture_filename)
      texture_item.setData(texture)
      chunk_item.appendRow(texture_item)
  
  
  def bem1_chunk_selected(self, bem1: BEM1):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing BEM1 (Dynamics Block) chunk with emitter/simulation settings.")
    
    bunfoe_editor_widget = super().setup_editor_widget_for_bunfoe_instance(bem1)
    layout.addWidget(bunfoe_editor_widget)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def bsp1_chunk_selected(self, bsp1: BSP1):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing BSP1 (Base Shape) chunk with particle draw settings.")
    
    self.gcft_window.make_color_selector_button(bsp1, "color_prm", "Color PRM", layout)
    self.gcft_window.make_color_selector_button(bsp1, "color_env", "Color ENV", layout)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def esp1_chunk_selected(self, esp1: ESP1):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing ESP1 (Extra Shape) chunk with misc extra particle draw settings.")
    
    bunfoe_editor_widget = super().setup_editor_widget_for_bunfoe_instance(esp1)
    layout.addWidget(bunfoe_editor_widget)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def etx1_chunk_selected(self, etx1: ETX1):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing ETX1 (Extra Texture Shape) chunk with extra texture draw settings.")
    
    bunfoe_editor_widget = super().setup_editor_widget_for_bunfoe_instance(etx1)
    layout.addWidget(bunfoe_editor_widget)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def ssp1_chunk_selected(self, ssp1: SSP1):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing SSP1 (Child Shape) chunk with child particle draw settings.")
    
    bunfoe_editor_widget = super().setup_editor_widget_for_bunfoe_instance(ssp1)
    layout.addWidget(bunfoe_editor_widget)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def color_anim_keyframe_selected(self, keyframe):
    layout = self.ui.scrollAreaWidgetContents.layout()
    
    self.ui.jpc_sidebar_label.setText("Showing color animation keyframe.")
    
    label = QLabel()
    label.setText("Time: %d" % keyframe.time)
    layout.addWidget(label)
    
    self.gcft_window.make_color_selector_button(keyframe, "color", "Color", layout)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
    layout.addItem(spacer)
  
  def export_jpc_by_path(self, jpc_path):
    assert self.jpc is not None
    
    self.jpc.save()
    
    with open(jpc_path, "wb") as f:
      self.jpc.data.seek(0)
      f.write(self.jpc.data.read())
    
    self.jpc_name = os.path.splitext(os.path.basename(jpc_path))[0]
    
    QMessageBox.information(self, "JPC saved", "Successfully saved JPC.")
  
  def add_particles_from_folder_by_path(self, folder_path):
    assert self.jpc is not None
    
    all_jpa_file_paths = glob.glob(glob.escape(folder_path) + "/*.jpa")
    jpa_paths_to_particle_ids: dict[str, int | None] = {
      jpa_path: None for jpa_path in all_jpa_file_paths
    }
    num_particles_added, num_particles_overwritten, num_textures_added, num_textures_overwritten = self.jpc.add_or_replace_particles_from_disk(jpa_paths_to_particle_ids)
    
    if num_particles_added == num_particles_overwritten == num_textures_added == num_textures_overwritten == 0:
      QMessageBox.warning(self, "No matching files found", "The selected folder does not contain any files with the extension .jpa. No particles imported.")
      return
    
    self.reload_jpc_particles_tree()
    
    QMessageBox.information(self, "Folder imported", "Successfully imported particles from \"%s\".\n\nStats:\nParticles added: %d\nParticles overwritten: %d\nTextures added: %d\nTextures overwritten: %d" % (folder_path, num_particles_added, num_particles_overwritten, num_textures_added, num_textures_overwritten))
  
  def export_jpc_folder_by_path(self, folder_path):
    self.jpc.extract_all_particles_to_disk(output_directory=folder_path)
    
    QMessageBox.information(self, "JPC extracted", "Successfully extracted all JPA particles from the JPC to \"%s\"." % folder_path)
  
  def add_particle_by_path(self, file_path: str):
    assert self.jpc is not None
    
    with open(file_path, "rb") as f:
      jpa_data = BytesIO(f.read())
    particle = JParticle(jpa_data, 0, self.jpc.version)
    
    particle_id_str, confirmed = QInputDialog.getText(
      self, "Input Particle ID", "What particle ID to give the new particle? (The default value is the ID from the file you just imported.)",
      text="%04X" % particle.particle_id,
      flags=Qt.WindowType.WindowSystemMenuHint | Qt.WindowType.WindowTitleHint,
    )
    if not confirmed:
      return
    
    particle_id = int(particle_id_str, 16)
    
    replacing = False
    orig_particle = None
    if particle_id in self.jpc.particles_by_id:
      message = ("A particle with ID 0x%04X already exists in this JPC.\n\n" + \
        "Do you want to replace it with the particle you just imported?") % (particle_id)
      response = QMessageBox.question(self, 
        "Confirm replace files",
        message,
        QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes,
        QMessageBox.StandardButton.Cancel
      )
      if response != QMessageBox.StandardButton.Yes:
        return
      replacing = True
      orig_particle = self.jpc.particles_by_id[particle_id]
    
    self.jpc.add_or_replace_particle_from_disk(file_path, particle_id)
    new_particle = self.jpc.particles_by_id[particle_id]
    
    if replacing:
      orig_item = self.find_item_by_data(0, orig_particle)
      row_index = orig_item.row()
      orig_was_expanded = self.is_expanded(orig_item)
      # Add the new item at the old one's index, then delete the old one afterwards.
      # Doing it in this order preserves the user's selection on the now-replaced row.
      new_item = self.add_new_tree_row_for_particle(new_particle, row_index)
      assert self.model.removeRow(orig_item.row())
      if orig_was_expanded:
        self.expand_item(new_item)
    else:
      self.add_new_tree_row_for_particle(new_particle)
    
    action_verb = "Replaced" if replacing else "Added"
    particle_id_str = self.get_particle_id_str(new_particle)
    self.gcft_window.ui.statusbar.showMessage("%s %s." % (action_verb, particle_id_str), 3000)
  
  
  def show_jpc_particles_tree_context_menu(self, pos: QPoint):
    if self.jpc is None:
      return
    
    index = self.ui.jpc_particles_tree.indexAt(pos)
    if not index.isValid():
      return
    item = self.model.itemFromIndex(self.proxy.mapToSource(index))
    if item is None:
      return
    
    data = item.data()
    if isinstance(data, JParticle):
      particle = data
      
      menu = QMenu(self)
      
      menu.addAction(self.ui.actionExtract_Particle)
      self.ui.actionExtract_Particle.setData(particle)
      menu.addAction(self.ui.actionReplace_Particle)
      self.ui.actionReplace_Particle.setData(particle)
      menu.addAction(self.ui.actionDelete_Particle)
      self.ui.actionDelete_Particle.setData(particle)
      
      menu.exec_(self.ui.jpc_particles_tree.mapToGlobal(pos))
    elif isinstance(data, TEX1):
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
  
  def extract_particle_by_path(self, file_path: str):
    assert self.jpc is not None
    
    particle: JParticle = self.ui.actionDelete_Particle.data()
    particle_id_str = self.get_particle_id_str(particle)
    
    self.jpc.extract_particle_to_disk(file_path, particle.particle_id)
    
    self.gcft_window.ui.statusbar.showMessage("Extracted particle %s." % particle_id_str, 3000)
  
  def replace_particle_by_path(self, file_path: str):
    assert self.jpc is not None
    
    orig_particle: JParticle = self.ui.actionDelete_Particle.data()
    
    self.jpc.add_or_replace_particle_from_disk(file_path, orig_particle.particle_id)
    new_particle = self.jpc.particles_by_id[orig_particle.particle_id]
    
    orig_item = self.find_item_by_data(0, orig_particle)
    row_index = orig_item.row()
    orig_was_expanded = self.is_expanded(orig_item)
    # Add the new item at the old one's index, then delete the old one afterwards.
    # Doing it in this order preserves the user's selection on the now-replaced row.
    new_item = self.add_new_tree_row_for_particle(new_particle, row_index)
    assert self.model.removeRow(orig_item.row())
    if orig_was_expanded:
      self.expand_item(new_item)
    
    particle_id_str = self.get_particle_id_str(new_particle)
    self.gcft_window.ui.statusbar.showMessage("Replaced %s." % particle_id_str, 3000)
  
  def delete_particle(self):
    assert self.jpc is not None
    
    particle: JParticle = self.ui.actionDelete_Particle.data()
    particle_id_str = self.get_particle_id_str(particle)
    
    if not self.gcft_window.confirm_delete(particle_id_str):
      return
    
    self.jpc.delete_particle(particle.particle_id)
    
    item = self.find_item_by_data(0, particle)
    assert self.model.removeRow(item.row())
  
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
    
    self.gcft_window.set_tab_by_name("BTI Images")
  
  def replace_image_in_jpc(self):
    assert self.jpc is not None
    
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
        QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes,
        QMessageBox.StandardButton.Cancel
      )
      if response != QMessageBox.StandardButton.Yes:
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
    
    self.gcft_window.ui.statusbar.showMessage("Replaced %s." % texture.filename, 3000)
  
  
  def keyPressEvent(self, event: QKeyEvent):
    event.ignore()
    if event.matches(QKeySequence.StandardKey.Copy):
      selected_indexes = self.selection_model.selectedIndexes()
      if not selected_indexes:
        selected_indexes = [self.selection_model.currentIndex()]
      
      particle_id_strs = []
      for selected_index in selected_indexes:
        if not selected_index.isValid():
          continue
        selected_index = self.proxy.mapToSource(selected_index)
        # if selected_index.column() != self.column_names.index("Particle ID"):
        #   continue
        item = self.model.itemFromIndex(selected_index)
        if item is None:
          continue
        particle = item.data()
        if not isinstance(particle, JParticle):
          continue
        
        particle_id_str = self.get_particle_id_str(particle)
        particle_id_strs.append(particle_id_str)
      
      if not particle_id_strs:
        return
      
      joined_paths = "\n".join(particle_id_strs)
      QApplication.clipboard().setText(joined_paths)
      event.accept()
