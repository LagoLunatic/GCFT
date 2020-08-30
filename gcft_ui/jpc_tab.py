
import os
import re
import traceback
from io import BytesIO
from fs_helpers import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

from wwlib.jpc import JPC
from gcft_ui.uic.ui_jpc_tab import Ui_JPCTab

class JPCTab(QWidget):
  def __init__(self):
    super().__init__()
    self.ui = Ui_JPCTab()
    self.ui.setupUi(self)
    
    self.jpc = None
    self.jpc_name = None
    
    self.ui.jpc_particles_tree.setColumnWidth(0, 100)
    
    self.ui.export_jpc.setDisabled(True)
    self.ui.add_particles_from_folder.setDisabled(True)
    self.ui.export_jpc_folder.setDisabled(True)
    
    self.ui.import_jpc.clicked.connect(self.import_jpc)
    self.ui.export_jpc.clicked.connect(self.export_jpc)
    self.ui.add_particles_from_folder.clicked.connect(self.add_particles_from_folder)
    self.ui.export_jpc_folder.clicked.connect(self.export_jpc_folder)
    
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
    self.ui.jpc_particles_tree.clear()
    
    self.jpc_particle_to_tree_widget_item = {}
    self.jpc_tree_widget_item_to_particle = {}
    self.jpc_texture_to_tree_widget_item = {}
    self.jpc_tree_widget_item_to_texture = {}
    
    for particle in self.jpc.particles:
      particle_id_str = self.window().stringify_number(particle.particle_id, min_hex_chars=4)
      
      particle_item = QTreeWidgetItem([particle_id_str, ""])
      self.ui.jpc_particles_tree.addTopLevelItem(particle_item)
      
      self.jpc_particle_to_tree_widget_item[particle] = particle_item
      self.jpc_tree_widget_item_to_particle[particle_item] = particle
      
      for texture_filename in particle.tdb1.texture_filenames:
        texture_item = QTreeWidgetItem(["", texture_filename])
        particle_item.addChild(texture_item)
        
        texture = self.jpc.textures_by_filename[texture_filename]
        self.jpc_texture_to_tree_widget_item[texture] = texture_item
        self.jpc_tree_widget_item_to_texture[texture_item] = texture
  
  def export_jpc_by_path(self, jpc_path):
    self.jpc.save_changes()
    
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
  
  
  def get_jpc_particle_by_tree_item(self, item):
    if item not in self.jpc_tree_widget_item_to_particle:
      return None
    
    return self.jpc_tree_widget_item_to_particle[item]
  
  def get_jpc_tree_item_by_particle(self, particle):
    if particle not in self.jpc_particle_to_tree_widget_item:
      return None
    
    return self.jpc_particle_to_tree_widget_item[particle]
  
  def get_jpc_texture_by_tree_item(self, item):
    if item not in self.jpc_tree_widget_item_to_texture:
      return None
    
    return self.jpc_tree_widget_item_to_texture[item]
  
  def get_jpc_tree_item_by_texture(self, texture):
    if texture not in self.jpc_texture_to_tree_widget_item:
      return None
    
    return self.jpc_texture_to_tree_widget_item[texture]
  
  def show_jpc_particles_tree_context_menu(self, pos):
    if self.jpc is None:
      return
    
    item = self.ui.jpc_particles_tree.itemAt(pos)
    if item is None:
      return
    
    texture = self.get_jpc_texture_by_tree_item(item)
    if texture:
      menu = QMenu(self)
      
      menu.addAction(self.ui.actionOpenJPCImage)
      self.ui.actionOpenJPCImage.setData(texture)
        
      menu.addAction(self.ui.actionReplaceJPCImage)
      self.ui.actionReplaceJPCImage.setData(texture)
      if self.bti_tab.bti is None:
        self.ui.actionReplaceJPCImage.setDisabled(True)
      else:
        self.ui.actionReplaceJPCImage.setDisabled(False)
      
      menu.exec_(self.ui.jpc_particles_tree.mapToGlobal(pos))
  
  def open_image_in_jpc(self):
    texture = self.ui.actionOpenJPCImage.data()
    
    # Need to make a fake standalone BTI texture data so we can load it without it being the TEX1 format.
    data = BytesIO()
    bti_header_bytes = read_bytes(texture.bti.data, texture.bti.header_offset, 0x20)
    write_bytes(data, 0x00, bti_header_bytes)
    
    bti_image_data = read_all_bytes(texture.bti.image_data)
    write_bytes(data, 0x20, bti_image_data)
    image_data_offset = 0x20
    write_u32(data, 0x1C, image_data_offset)
    
    if data_len(texture.bti.palette_data) == 0:
      palette_data_offset = 0
    else:
      bti_palette_data = read_all_bytes(texture.bti.palette_data)
      write_bytes(data, 0x20 + data_len(texture.bti.image_data), bti_palette_data)
      palette_data_offset = 0x20 + data_len(texture.bti.image_data)
    write_u32(data, 0x0C, palette_data_offset)
    
    self.bti_tab.import_bti_by_data(data, texture.filename)
    
    self.window().set_tab_by_name("BTI Images")
  
  def replace_image_in_jpc(self):
    texture = self.ui.actionOpenJPCImage.data()
    
    self.bti_tab.bti.save_changes()
    
    # Need to make a fake BTI header for it to read from.
    data = BytesIO()
    bti_header_bytes = read_bytes(self.bti_tab.bti.data, self.bti_tab.bti.header_offset, 0x20)
    write_bytes(data, 0x00, bti_header_bytes)
    
    texture.bti.read_header(data)
    
    texture.bti.image_data = make_copy_data(self.bti_tab.bti.image_data)
    texture.bti.palette_data = make_copy_data(self.bti_tab.bti.palette_data)
    
    texture.bti.save_header_changes()
