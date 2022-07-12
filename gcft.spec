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

a = Analysis(['gcft.py'],
             pathex=["./wwrando"],
             binaries=[],
             datas=build_datas_recursive([
               'assets/**/*.*',
               'version.txt',
             ]),
             hiddenimports=[],
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
          console=False,
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
