
import os
import re

from wwlib.rarc import RARC
from wwlib.j3d import J3DFile
from wwlib.bti import BTIFile

class AssetDumper:
  def __init__(self):
    self.succeeded_file_count = 0
    self.failed_file_paths = []
  
  def get_all_gcm_file_paths(self, gcm):
    all_file_paths = list(gcm.files_by_path.keys())
    
    # Sort the file names for determinism. And use natural sorting so the room numbers are in order.
    try_int_convert = lambda string: int(string) if string.isdigit() else string
    all_file_paths.sort(key=lambda filename: [try_int_convert(c) for c in re.split("([0-9]+)", filename)])
    
    return all_file_paths
  
  def dump_all_textures_in_gcm(self, gcm, out_dir):
    all_file_paths = self.get_all_gcm_file_paths(gcm)
    
    files_checked = 0
    yield("Initializing...", files_checked)
    
    for file_path in all_file_paths:
      rel_dir = os.path.dirname(file_path)
      base_name, file_ext = os.path.splitext(os.path.basename(file_path))
      
      try:
        if file_ext == ".arc":
          out_path = os.path.join(out_dir, rel_dir, base_name)
          rarc = RARC(gcm.get_changed_file_data(file_path))
          self.dump_all_textures_in_rarc(rarc, out_path, display_path_prefix=file_path)
        elif file_ext == ".bti":
          out_path = os.path.join(out_dir, rel_dir, base_name + ".png")
          bti = BTIFile(gcm.get_changed_file_data(file_path))
          self.dump_texture(bti, out_path)
        elif file_ext in [".bmd", ".bdl", ".bmt"]:
          out_path = os.path.join(out_dir, rel_dir, base_name + file_ext)
          j3d_file = J3DFile(gcm.get_changed_file_data(file_path))
          self.dump_all_textures_in_j3d_file(j3d_file, out_path)
      except Exception as e:
        display_path = file_path
        self.failed_file_paths.append(display_path)
      
      files_checked += 1
      yield(file_path, files_checked)
    
    yield("Done", -1)
  
  def dump_all_textures_in_rarc(self, rarc, out_dir, display_path_prefix=None):
    for file_entry in rarc.file_entries:
      rel_dir = file_entry.parent_node.name
      base_name, file_ext = os.path.splitext(file_entry.name)
      
      try:
        if file_ext == ".bti":
          out_path = os.path.join(out_dir, rel_dir, base_name + ".png")
          bti = rarc.get_file(file_entry.name)
          self.dump_texture(bti, out_path)
        elif file_ext in [".bmd", ".bdl", ".bmt"]:
          out_path = os.path.join(out_dir, rel_dir, base_name + file_ext)
          j3d_file = rarc.get_file(file_entry.name)
          self.dump_all_textures_in_j3d_file(j3d_file, out_path)
      except Exception as e:
        display_path = rel_dir + "/" + base_name + file_ext
        if display_path_prefix is not None:
          display_path = display_path_prefix + "/" + display_path
        self.failed_file_paths.append(display_path)
  
  def dump_all_textures_in_j3d_file(self, j3d_file, out_dir):
    if not hasattr(j3d_file, "tex1"):
      return
    if not os.path.isdir(out_dir):
      os.makedirs(out_dir)
    
    for texture_name, textures in j3d_file.tex1.textures_by_name.items():
      if len(textures) == 0:
        continue
      
      images = []
      for i, texture in enumerate(textures):
        is_duplicate = False
        for prev_texture in textures[:i]:
          if texture.is_visually_equal_to(prev_texture):
            # Visual duplicate. Don't render.
            is_duplicate = True
            break
        if is_duplicate:
          continue
        
        image = texture.render()
        
        if image in images:
          # A duplicate not detected by is_visually_equal_to().
          # For example, if one version uses C8 format with RGB565 palette and the other uses RGB565 format, they can be identical, but is_visually_equal_to() will not detect this.
          continue
        
        images.append(image)
      
      has_different_duplicates = len(images) > 1
      for i, image in enumerate(images):
        if has_different_duplicates:
          # If there's more than one unique version of this texture, append _dupe0 _dupe1 etc to all the images.
          out_path = os.path.join(out_dir, texture_name + "_dupe%d.png" % i)
        else:
          out_path = os.path.join(out_dir, texture_name + ".png")
        
        image.save(out_path)
        
        self.succeeded_file_count += 1
  
  def dump_texture(self, bti, out_path):
    out_dir = os.path.dirname(out_path)
    if not os.path.isdir(out_dir):
      os.makedirs(out_dir)
    
    image = bti.render()
    image.save(out_path)
    
    self.succeeded_file_count += 1
