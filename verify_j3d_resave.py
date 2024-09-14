
import sys
sys.path.insert(0, "./gclib")

from gclib.gcm import GCM
import os
from gclib.j3d import J3D
from gclib import fs_helpers as fs
from collections import Counter

# TODO: verify that fog_type can be read for all files in all games.
# are there any where it fails because they have & 0x80 set? for orthographic? idk if that's real or not.

iso_path = r"D:\WW\Vanilla ISOs\The Legend of Zelda - The Wind Waker.iso"
# iso_path = r"D:\Emulation\GC\#Games\Legend of Zelda, The - Twilight Princess (USA).iso"
# iso_path = r"D:\Emulation\GC\#Games\Super Mario Sunshine (USA)\Super Mario Sunshine (USA).iso"

gcm = GCM(iso_path)
gcm.read_entire_disc()

n = 0
errors = 0
total_chunk_types = Counter()
nonmatching_chunk_types = Counter()
for file_path, file_data in gcm.each_file_data(only_file_exts=[".bdl", ".bmd"]):
  if n % 100 == 0:
    print(n, nonmatching_chunk_types)
  n += 1
  
  try:
    orig_j3d = J3D(file_data)
    for chunk_type in orig_j3d.chunk_by_type:
      total_chunk_types[chunk_type] += 1
    new_j3d = J3D(file_data)
    new_j3d.save()
  except Exception as e:
    print(f"Error on: {file_path}")
    print(e)
    errors += 1
    # raise
    continue
  
  for chunk_type in orig_j3d.chunk_by_type:
    orig_bytes = fs.read_all_bytes(orig_j3d.chunk_by_type[chunk_type].data)
    new_bytes = fs.read_all_bytes(new_j3d.chunk_by_type[chunk_type].data)
    if orig_bytes != new_bytes:
      # print(file_path, chunk_type)
      nonmatching_chunk_types[chunk_type] += 1

print()
print(f"{total_chunk_types=}")
print(f"{nonmatching_chunk_types=}")
print(f"{errors=}")
