
from pyside2uic import compileUi
import glob
import os

for input_path in glob.glob('*.ui'):
  base_name = os.path.splitext(input_path)[0]
  output_path = "ui_%s.py" % base_name
  
  if os.path.isfile(output_path):
    with open(output_path) as f:
      orig = f.read()
  else:
    orig = None
  
  with open(output_path, "w") as output_file:
    compileUi(input_path, output_file)
  
  if orig is not None:
    with open(output_path) as f:
      new = f.read()
    
    orig_lines = orig.splitlines()
    orig_lines[5] = ""
    new_lines = new.splitlines()
    new_lines[5] = ""
    
    # Check if the old and new version of the file are identical except for the timestamp.
    # If so, revert the file to the old version so a ton of files don't show up as changed in git despite only the timestamp changing.
    if orig_lines == new_lines:
      with open(output_path, "w") as f:
        f.write(orig)
