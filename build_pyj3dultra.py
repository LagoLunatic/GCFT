#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import shutil

def call_command(command):
  print(" ".join(command))
  result = subprocess.call(command)
  if result != 0:
    raise Exception("Command call failed")

if not os.path.isdir("./PyJ3DUltra/J3DUltra"):
  git_path = shutil.which("git")
  if git_path is None:
    raise Exception("PyJ3DUltra has not been cloned, and git is not installed (or not in PATH).\nDownload git here: https://git-scm.com/downloads")
  git_command = ["git", "submodule", "update", "--init", "--recursive", "PyJ3DUltra"]
  call_command(git_command)

cmake_command = ["cmake", "PyJ3DUltra", "-BPyJ3DUltra/build"]
python_path = sys.executable
cmake_command += ["-DPYTHON_EXECUTABLE=%s" % sys.executable]
if platform.system() == "Windows":
  vcpkg_path = shutil.which("vcpkg")
  if vcpkg_path is None:
    raise Exception("vcpkg is not installed (or not in PATH).\nSee here for instructions on installing vcpkg: https://vcpkg.io/en/getting-started")
  vcpkg_cmake_path = os.path.dirname(vcpkg_path) + "/scripts/buildsystems/vcpkg.cmake"
  cmake_command += ["-DCMAKE_TOOLCHAIN_FILE=%s" % vcpkg_cmake_path]
call_command(cmake_command)

build_command = ["cmake", "--build", "PyJ3DUltra/build"]
build_type = "Release"
if len(sys.argv) > 1:
  build_type = sys.argv[1]
build_command += ["--config %s" % build_type]
call_command(build_command)

print("Successfully compiled PyJ3DUltra.")
