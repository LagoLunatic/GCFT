# -*- mode: python -*-

block_cipher = None

from version import VERSION
build_version = VERSION

import os
import glob
def build_datas_recursive(paths):
  datas = []
  
  for path in paths:
    for filename in glob.iglob(path, recursive=True):
      dest_dirname = os.path.dirname(filename)
      if dest_dirname == "":
        dest_dirname = "."
      
      data_entry = (filename, dest_dirname)
      datas.append(data_entry)
      #print(data_entry)
  
  return datas

import sys
def get_hidden_imports():
  import_modules = []
  
  sys.path.insert(0, "./gclib")
  import gclib
  for module_name in gclib.__all__:
    import_modules.append(f"gclib.{module_name}")
  for module_name in gclib.j3d_chunks.__all__:
    import_modules.append(f"gclib.j3d_chunks.{module_name}")
  for module_name in gclib.jpa_chunks.__all__:
    import_modules.append(f"gclib.jpa_chunks.{module_name}")
  
  return import_modules

import platform
import glob
def get_binaries():
  if platform.system() in ["Darwin", "Linux"]:
    return [('./PyJ3DUltra/build/J3DUltra*.so', '.')]
  assert platform.system() == "Windows"
  for glob_pattern in [
    './PyJ3DUltra/build/J3DUltra*.pyd',
    './PyJ3DUltra/build/Debug/J3DUltra*.pyd',
    './PyJ3DUltra/build/Release/J3DUltra*.pyd',
  ]:
    if glob.glob(glob_pattern):
      return [(glob_pattern, '.')]
  raise Exception("Could not find Windows PyJ3DUltra executable")


a = Analysis(['gcft.py'],
             pathex=[],
             binaries=get_binaries(),
             datas=build_datas_recursive([
               'assets/**/*.*',
               'version.txt',
             ]),
             hiddenimports=get_hidden_imports(),
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='GameCube File Tools',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
          icon="assets/icon.ico" )

app = BUNDLE(exe,
          name='GameCube File Tools.app',
          icon="assets/icon.icns",
          bundle_identifier=None,
          info_plist={
              "LSBackgroundOnly": False,
              "CFBundleDisplayName": "GameCube File Tools",
              "CFBundleName": "GCFT", # 15 character maximum
              "CFBundleShortVersionString": build_version,
          }
          )
