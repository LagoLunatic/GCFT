
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
    
    for file_path in all_file_paths:
      rel_dir = os.path.dirname(file_path)
      base_name, file_ext = os.path.splitext(os.path.basename(file_path))
      
      try:
        if file_ext == ".arc":
          out_path = os.path.join(out_dir, rel_dir, base_name)
          rarc = RARC(gcm.get_changed_file_data(file_path))
          self.dump_all_textures_in_rarc(rarc, out_path)
        elif file_ext == ".bti":
          out_path = os.path.join(out_dir, rel_dir, base_name + ".png")
          bti = BTIFile(gcm.get_changed_file_data(file_path))
          self.dump_texture(bti, out_path)
        elif file_ext in [".bmd", ".bdl", ".bmt"]:
          out_path = os.path.join(out_dir, rel_dir, base_name + file_ext)
          j3d_file = J3DFile(gcm.get_changed_file_data(file_path))
          self.dump_all_textures_in_j3d_file(j3d_file, out_path)
      except Exception as e:
        self.failed_file_paths.append(out_path)
  
  def dump_all_textures_in_rarc(self, rarc, out_dir):
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
        self.failed_file_paths.append(out_path)
  
  def dump_all_textures_in_j3d_file(self, j3d_file, out_dir):
    if not hasattr(j3d_file, "tex1"):
      return
    
    for texture_name, textures in j3d_file.tex1.textures_by_name.items():
      for i, texture in enumerate(textures):
        try:
          out_path = os.path.join(out_dir, texture_name + "_%d.png" % i)
          self.dump_texture(texture, out_path)
        except Exception as e:
          self.failed_file_paths.append(out_path)
  
  def dump_texture(self, bti, out_path):
    out_dir = os.path.dirname(out_path)
    if not os.path.isdir(out_dir):
      os.makedirs(out_dir)
    
    image = bti.render()
    image.save(out_path)
    
    self.succeeded_file_count += 1
