
import os
import re
from PIL import Image

from gclib.gcm import GCM
from gclib.rarc import RARC
from gclib.j3d import J3D
from gclib.j3d_chunks.tex1 import TEX1
from gclib.bti import BTI

class AssetDumper:
  def __init__(self):
    self.succeeded_file_count = 0
    self.failed_file_paths = []
  
  def get_all_gcm_file_paths(self, gcm: GCM):
    all_file_paths = list(gcm.files_by_path.keys())
    
    # Sort the file names for determinism. And use natural sorting so the room numbers are in order.
    try_int_convert = lambda string: int(string) if string.isdigit() else string
    all_file_paths.sort(key=lambda filename: [try_int_convert(c) for c in re.split("([0-9]+)", filename)])
    
    return all_file_paths
  
  def get_all_rarc_file_paths(self, rarc: RARC):
    all_file_paths = []
    for file_entry in rarc.file_entries:
      if file_entry.is_dir:
        continue
      
      file_path = "%s/%s" % (file_entry.parent_node.name, file_entry.name)
      all_file_paths.append(file_path)
      
    return all_file_paths
  
  def dump_all_textures_in_gcm(self, gcm: GCM, out_dir):
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
          rarc.read()
          for _ in self.dump_all_textures_in_rarc(rarc, out_path, display_path_prefix=file_path):
            continue
        elif file_ext == ".bti":
          out_path = os.path.join(out_dir, rel_dir, base_name)
          bti = BTI(gcm.get_changed_file_data(file_path))
          self.dump_texture(bti, out_path)
        elif file_ext in [".bmd", ".bdl", ".bmt"]:
          out_path = os.path.join(out_dir, rel_dir, base_name + file_ext)
          j3d_file = J3D(gcm.get_changed_file_data(file_path))
          if j3d_file.tex1 is not None:
            self.dump_all_textures_in_tex1(j3d_file.tex1, out_path)
      except Exception as e:
        display_path = file_path
        self.failed_file_paths.append(display_path)
      
      files_checked += 1
      yield(file_path, files_checked)
  
  def dump_all_textures_in_rarc(self, rarc: RARC, out_dir, display_path_prefix=None):
    files_checked = 0
    yield("Initializing...", files_checked)
    
    for file_entry in rarc.file_entries:
      if file_entry.is_dir:
        continue
      
      rel_dir = file_entry.parent_node.name
      base_name, file_ext = os.path.splitext(file_entry.name)
      display_path = rel_dir + "/" + base_name + file_ext
      if display_path_prefix is None:
        full_display_path = display_path
      else:
        full_display_path = display_path_prefix + "/" + display_path
      
      try:
        if file_ext == ".bti":
          out_path = os.path.join(out_dir, rel_dir, base_name)
          bti = rarc.get_file(file_entry.name, BTI)
          self.dump_texture(bti, out_path)
        elif file_ext in [".bmd", ".bdl", ".bmt"]:
          out_path = os.path.join(out_dir, rel_dir, base_name + file_ext)
          j3d_file = rarc.get_file(file_entry.name, J3D)
          if j3d_file.tex1 is not None:
            self.dump_all_textures_in_tex1(j3d_file.tex1, out_path)
        elif file_ext == ".arc":
          out_path = os.path.join(out_dir, rel_dir, base_name + file_ext)
          inner_rarc = rarc.get_file(file_entry.name, RARC)
          for _ in self.dump_all_textures_in_rarc(inner_rarc, out_path, display_path_prefix=full_display_path):
            continue
      except Exception as e:
        self.failed_file_paths.append(full_display_path)
      
      files_checked += 1
      yield(display_path, files_checked)
  
  def dump_all_textures_in_tex1(self, tex1: TEX1, out_dir):
    if not os.path.isdir(out_dir):
      os.makedirs(out_dir)
    
    for texture_name, textures in tex1.textures_by_name.items():
      if len(textures) == 0:
        continue
      
      unique_image_count = 0
      for i, texture in enumerate(textures):
        is_duplicate = False
        for prev_texture in textures[:i]:
          if texture.is_visually_equal_to(prev_texture):
            # Visual duplicate. Don't render.
            is_duplicate = True
            break
        if is_duplicate:
          continue
        unique_image_count += 1
      
      has_different_duplicates = unique_image_count > 1
      for i, texture in enumerate(textures):
        dupe_tex_name = texture_name
        if has_different_duplicates:
          # If there's more than one unique version of this texture, append _dupe0 _dupe1 etc to all the images.
          dupe_tex_name += ".dupe%d" % i
        
        out_path = os.path.join(out_dir, dupe_tex_name)
        
        self.dump_texture(texture, out_path)
  
  def dump_texture(self, bti: BTI, out_path):
    out_dir = os.path.dirname(out_path)
    os.makedirs(out_dir, exist_ok=True)
    
    for i in range(bti.mipmap_count):
      mip_out_path = out_path
      if (bti.mipmap_count) > 1:
        mip_out_path += ".mip%d" % i
      mip_out_path += ".png"
      # if os.path.isfile(mip_out_path):
      #   continue
      image = bti.render_mipmap(i)
      image.save(mip_out_path)
    
    self.succeeded_file_count += 1
