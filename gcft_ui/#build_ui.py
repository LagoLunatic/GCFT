
from subprocess import call
import glob
import os

if not os.path.isdir("uic"):
  os.makedirs("uic")
for input_path in glob.glob('*.ui'):
  base_name = os.path.splitext(input_path)[0]
  output_path = "uic/ui_%s.py" % base_name
  
  command = [
    "pyside6-uic",
    input_path,
    "-o", output_path
  ]
  result = call(command)
