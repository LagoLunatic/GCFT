
import sys
sys.path.insert(0, "./gclib")

# import gclib
# print(gclib.read_u16)
# print(fs.read_u16)

from gclib.gcm import GCM
import os
from gclib.j3d import J3D
from gclib import fs_helpers as fs
from gclib.j3d_chunks import bp_command as BP
from gclib.j3d_chunks import xf_command as XF
from collections import Counter
import json
# from deepdiff import DeepDiff
from pprint import pprint
import subprocess
import time
import difflib
# from multiprocessing import Pool
import multiprocessing as mp
import itertools
from collections import deque

# TODO: would multiprocessing help speed this up?
# no multiprocessing, subprocess.run on git diff (200 files): 11.1s
# same but skip the diff step entirely: 4.5s
# same but with a difflib.unified_diff diff: 4.8s
# with multiprocessing and difflib.unified diff, 12 processes: 23.7s
# back to no multiprocessing, using deque(itertools.starmap: 152.2s

# before fog fixes: took 72.5s, patches take up 9.89MB, 287/10755 match perfectly
# after fog fixes: took 45.2s, patches take up 6.67MB, 6686/10755 match perfectly
# after TEX_LOADTLUT0 ignoring: took 34.5s, patches take up 6.33MB, 7150/10755 match perfectly
# after min/max lod: took 30.7, patches take up 6.19MB, 7608/10755 match perfectly
# after TEV_REGISTER color & 0x7FF: took 87.1, patches take up 6.15MB, 7614/10755 match perfectly
# after implementing more indirect properties: took 31s, patches take up 5.88MB, 7614/10755 match perfectly
# after implementing indirect tex coord scale: 5.31MB, 7614/10755
# after adding tex mtx tiling x/y values of 0.5 instead of 0.0: 4.99MB, 7649/10755
# after adding tex mtx tiling x/y values of tex mtx's center: 4.96MB, 7651/10755
# after tex mtx rounding to float32: 4.94MB, 7653/10755
# after bti header fixes: 4.91MB, 7660/10755
# after ignoring RAS1_TREF oob read stuff: 3.80MB, 5679/8319
# after multiple RAS1_TREF fixes: 3.27MB, 6282/8319
# after fog range implementation: 2.88MB, 6524/8319
# after tev op fix: 2.82MB, 6540/8319
# after ignoring oob ksel stuff: 2.64MB, 6739/8319
# after switch tex mtx removal to be based on tex coord gen usage: 2.70MB, 6830/8319
# after ignoring TEXMTX args: 295KB, 7978/8319
# after fixing TEXMTXINFO source_row: 260KB, 8034/8319
# after using float32 for fog: 238KB, 8099/8319

iso_path = "D:/WW/Vanilla ISOs/The Legend of Zelda - The Wind Waker.iso"
# iso_path = "D:/Emulation/GC/#Games/Legend of Zelda, The - Twilight Princess (USA).iso"
# iso_path = "D:/Emulation/GC/#Games/Super Mario Sunshine (USA)/Super Mario Sunshine (USA).iso"
# iso_path = "D:/Emulation/GC/#Games/Mario Kart - Double Dash (USA).nkit.iso"

base_out_dir = "D:/dev/GCFT/wip/mdl3diffs"

gcm = GCM(iso_path)
gcm.read_entire_disc()

game_id = gcm.read_file_raw_data("sys/boot.bin")[0:6].decode("ASCII")

base_out_dir = f"{base_out_dir}_{game_id}"

# n = 0
# errors = 0
# total_chunk_types = Counter()
# nonmatching_chunk_types = Counter()

# for file_path, file_data in gcm.each_file_data(only_file_exts=[".bdl", ".bmd"]):
#   if n % 200 == 0:
#     print(n, nonmatching_chunk_types)
#     if n > 0:
#       break
#   n += 1

def print_mdl3_diff_for_file(file_path, file_data):
  n = 0
  errors = 0
  total_chunk_types = Counter()
  nonmatching_chunk_types = Counter()
  
  out_diffs_dir_for_j3d = os.path.splitext(os.path.join(base_out_dir, file_path))[0]
  
  try:
    orig_j3d = J3D(file_data)
    n += 1
    for chunk_type in orig_j3d.chunk_by_type:
      total_chunk_types[chunk_type] += 1
    new_j3d = J3D(file_data)
    new_j3d.save()
  except Exception as e:
    print(f"Error on: {file_path}")
    print(e)
    errors += 1
    # raise
    # continue
    return n, errors, total_chunk_types, nonmatching_chunk_types
  
  if orig_j3d.mdl3 is None:
    # print(f"BMD: {file_path}")
    pass
  else:
    dict_1s = []
    for mat_index, entry in enumerate(orig_j3d.mdl3.entries):
      mat = orig_j3d.mat3.materials[mat_index]
      for bp_command in entry.bp_commands:
        if isinstance(bp_command, BP.TEX_LOADTLUT0):
          bp_command.src = 0
          bp_command.bitfield = 0
        
        if isinstance(bp_command, BP.RAS1_TREF):
          last_tev_order_index = None
          for i, tev_order in enumerate(mat.tev_orders):
            if tev_order is not None:
              last_tev_order_index = i
          reg_index = bp_command.VALID_REGISTERS.index(bp_command.register)
          if last_tev_order_index % 2 == 0 and reg_index == last_tev_order_index//2:
            bp_command.channel_id_1 = BP.MDLColorChannelID.COLOR0
            bp_command.bitfield &= ~0x380000
        
        if isinstance(bp_command, BP.TEV_KSEL):
          last_swap_mode_table_index = None
          for i, swap_mode_table in enumerate(mat.tev_swap_mode_tables):
            if swap_mode_table is not None:
              last_swap_mode_table_index = i
          reg_index = bp_command.VALID_REGISTERS.index(bp_command.register)
          if reg_index//2 > last_swap_mode_table_index:
            if reg_index % 2 == 0:
              bp_command.r_or_b = 0
              bp_command.g_or_a = 1
              bp_command.bitfield &= ~0x000003
              bp_command.bitfield |= 0 << 0
              bp_command.bitfield &= ~0x00000C
              bp_command.bitfield |= 1 << 2
            else:
              bp_command.r_or_b = 2
              bp_command.g_or_a = 3
              bp_command.bitfield &= ~0x000003
              bp_command.bitfield |= 2 << 0
              bp_command.bitfield &= ~0x00000C
              bp_command.bitfield |= 3 << 2
      
      for xf_command in entry.xf_commands:
        if isinstance(xf_command, XF.TEXMTX):
          for arg in xf_command.args:
            arg.value = 0.0
            arg.bitfield = 0
      
      dict_1 = entry.asdict()
      dict_1s.append(dict_1)
    
    orig_j3d.mdl3.generate_from_mat3(orig_j3d.mat3, orig_j3d.tex1)
    
    for i, entry in enumerate(orig_j3d.mdl3.entries):
      mat_name = orig_j3d.mdl3.mat_names[i]
      sanitized_mat_name = mat_name.replace(":", "_")
      out_diff_path_for_mat = os.path.join(out_diffs_dir_for_j3d, sanitized_mat_name)
      
      # if os.path.isfile(out_diff_path_for_mat + ".patch"): # TEMP FOR TESTING
      #   continue
      
      dict_1 = dict_1s.pop(0)
      dict_2 = entry.asdict()
      # reload from json to fix spurious diffs from the types being different, e.g. u32 -> int
      # dict_1 = json.loads(json.dumps(dict_1))
      # dict_2 = json.loads(json.dumps(dict_2))
      dict_str_1 = json.dumps(dict_1, indent=4)
      dict_str_2 = json.dumps(dict_2, indent=4)
      
      os.makedirs(out_diffs_dir_for_j3d, exist_ok=True)
      with open(out_diff_path_for_mat + ".1.json", "w", newline="\n") as f: f.write(dict_str_1)
      with open(out_diff_path_for_mat + ".2.json", "w", newline="\n") as f: f.write(dict_str_2)
      
      # with open(out_diff_path_for_mat + ".patch", "w", newline="\n") as f:
      #   subprocess.run([
      #     "git", "diff", "--no-index",
      #     out_diff_path_for_mat + ".1.json", out_diff_path_for_mat + ".2.json",
      #   ], stdout=f)
      
      diff = difflib.unified_diff(dict_str_1.split("\n"), dict_str_2.split("\n"))
      with open(out_diff_path_for_mat + ".patch", "w", newline="\n") as f:
        f.write("\n".join(diff))
    
    # break
  
  for chunk_type in orig_j3d.chunk_by_type:
    orig_bytes = fs.read_all_bytes(orig_j3d.chunk_by_type[chunk_type].data)
    new_bytes = fs.read_all_bytes(new_j3d.chunk_by_type[chunk_type].data)
    if orig_bytes != new_bytes:
      # print(file_path, chunk_type)
      nonmatching_chunk_types[chunk_type] += 1
  
  return n, errors, total_chunk_types, nonmatching_chunk_types

if __name__ == "__main__":
  start = time.perf_counter()
  
  # deque(itertools.starmap(print_mdl3_diff_for_file, gcm.each_file_data(only_file_exts=[".bdl", ".bmd"])), maxlen=0)
  
  with mp.Pool() as p:
    results = p.starmap(print_mdl3_diff_for_file, gcm.each_file_data(only_file_exts=[".bdl", ".bmd"]))
    n, errors, total_chunk_types, nonmatching_chunk_types = [sum(x, start=type(x[0])()) for x in zip(*results)]
  
  print()
  print(f"{total_chunk_types=}")
  print(f"{nonmatching_chunk_types=}")
  print(f"{n=}")
  print(f"{errors=}")
  print(f"Time taken: {time.perf_counter() - start}")
