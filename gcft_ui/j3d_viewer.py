
import sys
import os
import re
from io import BytesIO
import time
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtOpenGLWidgets import *

from gcft_paths import ASSETS_PATH, IS_RUNNING_FROM_SOURCE
from gcft_ui.nav_camera import Camera
from gclib.j3d import J3D
from gclib.bti import BTI
import gclib.gx_enums as GX
from gclib import fs_helpers as fs

import numpy as np
from pyrr import matrix44
from OpenGL.GL import *
from OpenGL.GLU import *

try:
  import J3DUltra as ultra # type: ignore
  from J3DUltra import J3DLight # type: ignore
  J3DULTRA_INSTALLED = True
except ImportError as e:
  print(f"Failed to import J3DUltra with error: {e}")
  print("Current Python module search paths are:")
  print(sys.path)
  J3DULTRA_INSTALLED = False

REQUIRED_OPENGL_VERSION = (4, 5)

class J3DViewer(QOpenGLWidget):
  error_showing_preview = Signal(str)
  
  bck_frame_changed = Signal(float)
  
  DESIRED_FPS = 30
  DELAY_BETWEEN_FRAMES = 1000 // DESIRED_FPS
  
  KEY_TO_MOVE_DIR = {
    Qt.Key.Key_W: [0, 0, -1],
    Qt.Key.Key_A: [-1, 0, 0],
    Qt.Key.Key_S: [0, 0, 1],
    Qt.Key.Key_D: [1, 0, 0],
    Qt.Key.Key_Q: [0, -1, 0],
    Qt.Key.Key_E: [0, 1, 0],
  }
  KEY_TO_SPEED_MULTIPLIER = {
    Qt.Key.Key_Shift: 4.0,
    Qt.Key.Key_Control: 0.25,
  }
  BASE_CAMERA_MOVE_SPEED = 40.0
  
  KEY_TO_CAMERA_ANGLE = {
    Qt.Key.Key_1: [0.0, 0.0],  # Front
    Qt.Key.Key_3: [0.0, 90.0], # Right
    Qt.Key.Key_7: [90.0, 0.0], # Top
    # TODO: keys for bottom/left/right
    # TODO: key for orthographic/perspective toggle
    # TODO: key 9 for rotating the current view 180 degrees
  }
  
  def __init__(self, parent):
    super().__init__(parent)
    
    # Start off assuming J3DUltra isn't supported.
    # Once OpenGL has been initialized we can check if it's actually supported or not.
    self.enable_j3dultra = False
    
    self.j3d = None
    self.load_model_is_queued = False
    self.should_update_render = False
    self.animate_light = False
    self.show_debug_light_widget = True
    self.prev_mouse_pos = None
    self.key_is_held = {}
    for key in self.KEY_TO_MOVE_DIR:
      self.key_is_held[key] = False
    for key in self.KEY_TO_SPEED_MULTIPLIER:
      self.key_is_held[key] = False
    self.show_widgets = False # TODO remove or rewrite widgets
    self.hidden_material_indexes = []
    
    self.base_cam_move_speed = self.BASE_CAMERA_MOVE_SPEED
    self.fovy = 45.0
    self.near_plane = 0.1
    self.far_plane = 1000.0
    self.base_cam_dist = 1000.0
    self.base_pitch = 30.0
    self.base_yaw = 35.0
    self.base_center = np.zeros(3)
    self.aspect = 1.0
    self.model = None
    
    self.anim_paused = False
    self.brk = None
    self.j3dultra_brk = None
    self.btp = None
    self.j3dultra_btp = None
    self.btk = None
    self.j3dultra_btk = None
    self.bck = None
    self.j3dultra_bck = None
    self.bca = None
    self.j3dultra_bca = None
    self.bva = None
    self.j3dultra_bva = None
    
    self.camera = Camera(
      distance=self.base_cam_dist,
      pitch=self.base_pitch, yaw=self.base_yaw,
      target=self.base_center
    )
    
    self.lights = []
    
    self.frame_timer = QTimer()
    self.frame_timer.setInterval(self.DELAY_BETWEEN_FRAMES)
    self.frame_timer.timeout.connect(self.process_frame)
    
    self.last_render_time = time.monotonic()
    self.total_time_elapsed = 0.0
    
    self.frame_timer.start()
  
  def initializeGL(self):
    self.enable_j3dultra = self.check_should_j3dultra_be_enabled()
    if not self.enable_j3dultra:
      return
    if not ultra.init():
      raise Exception("Failed to initialize J3DUltra.")
    
    self.init_lights()
    
    glClearColor(0.25, 0.3, 0.4, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    width = self.width()
    height = self.height()
    self.aspect = width / height
    
    if self.load_model_is_queued:
      self.load_queued_model()
  
  def resizeGL(self, width: int, height: int):
    self.aspect = width / height
    self.update()
  
  def paintGL(self):
    if self.show_widgets:
      self.draw_grid_widget()
    
    self.draw_model()
    
    if self.show_widgets:
      self.draw_viewport_orientation_widget()
    
    if self.show_widgets:
      self.draw_light_widget()
  
  def check_should_j3dultra_be_enabled(self) -> bool:
    # This function must only be called after OpenGL is initialized.
    if not J3DULTRA_INSTALLED:
      return False
    
    try:
      opengl_version = self.get_supported_opengl_version()
    except GLError as e:
      opengl_version = None
    
    if opengl_version is None:
      error_msg = "Cannot show J3D previews, there was an error when checking your " + \
        "graphics driver's supported OpenGL version."
      self.error_showing_preview.emit(error_msg)
      return False
    elif opengl_version < REQUIRED_OPENGL_VERSION:
      curr_version_str = f"{opengl_version[0]}.{opengl_version[1]}"
      req_version_str = f"{REQUIRED_OPENGL_VERSION[0]}.{REQUIRED_OPENGL_VERSION[1]}"
      error_msg = f"Your graphics driver only supports OpenGL {curr_version_str}.\n" + \
        f"At least OpenGL {req_version_str} is required to show J3D previews."
      self.error_showing_preview.emit(error_msg)
      return False
    else:
      return True
  
  def get_supported_opengl_version(self) -> tuple[int, int]:
    # This function must only be called after OpenGL is initialized.
    major_ver = glGetIntegerv(GL_MAJOR_VERSION)
    minor_ver = glGetIntegerv(GL_MINOR_VERSION)
    return (major_ver, minor_ver)
  
  def load_model(self, j3d_model: J3D, reset_camera=False, hidden_material_indexes=None):
    if not J3DULTRA_INSTALLED:
      error_msg = "Cannot show J3D previews, J3DUltra could not be imported."
      if IS_RUNNING_FROM_SOURCE:
        error_msg += "\n\n"
        error_msg += "Make sure you compiled PyJ3DUltra by running the following command:\n"
        error_msg += "py build_pyj3dultra.py"
      elif sys.platform == "win32":
        error_msg += "\n\n"
        error_msg += "Make sure you have the Microsoft Visual C++ Redistributable installed."
      self.error_showing_preview.emit(error_msg)
      return
    
    if j3d_model.file_type not in ["bmd3", "bdl4", "bmd2"]:
      # Not a 3D model, or an older unsupported version.
      error_msg = f"The current J3D file is of type {j3d_model.file_type!r}, " + \
        "which GCFT does not currently support showing previews for."
      self.error_showing_preview.emit(error_msg)
      return
    
    if hidden_material_indexes is None:
      self.hidden_material_indexes = []
    else:
      self.hidden_material_indexes = hidden_material_indexes
    
    # TODO: preview hack edits should be made and saved in a seperate process (via multiprocessing).
    # that process can also try loading the model into j3dultra to check if it segfaults.
    self.j3d = self.get_preview_compatible_j3d(j3d_model)
    
    if reset_camera:
      bbox_min, bbox_max = self.guesstimate_model_bbox(self.j3d)
      self.base_center = (bbox_min + bbox_max) / 2
      aabb_diag_len = np.linalg.norm(bbox_max - bbox_min)
      if aabb_diag_len < 10.0:
        aabb_diag_len = 10.0
      self.base_cam_dist = (aabb_diag_len / 2) / abs(np.sin(np.radians(self.fovy)/2.0))
      # print("bbox", bbox_min, bbox_max)
      # print(self.base_center, self.base_cam_dist)
      
      self.reset_camera()
      
      self.total_time_elapsed = 0.0
    
    # Display the preview widget.
    self.show()
    
    if self.context() is None:
      # OpenGL has not yet been initialized.
      # It will be initialized whenever the widget actually gets shown on the users screen, so just
      # queue the model to load whenever initializeGL gets called.
      self.load_model_is_queued = True
    else:
      # OpenGL is already initialized, so we can immediately load the model.
      self.load_queued_model()
  
  def load_queued_model(self):
    self.load_model_is_queued = False
    
    if self.j3d is None:
      return
    
    if self.context() is None:
      error_msg = "OpenGL context was not properly initialized. Cannot show J3D model preview."
      self.error_showing_preview.emit(error_msg)
      self.hide()
      return
    
    self.check_should_j3dultra_be_enabled()
    if not self.enable_j3dultra:
      return
    
    self.unload_anims()
    self.model = ultra.loadModel(data=fs.read_all_bytes(self.j3d.data))
    if self.model is None:
      error_msg = "Failed to load J3D model preview."
      self.error_showing_preview.emit(error_msg)
      self.hide()
      return
    
    self.last_render_time = time.monotonic()
    
    error_codes = []
    while (err := glGetError()) and err != GL_NO_ERROR:
      error_codes.append(err)
    if error_codes:
      # TODO: make this a separate func called reset
      self.unload_model()
      error_msg = f"Encountered OpenGL error(s) when trying to render a J3D preview:\n"
      error_msg += "\n".join(f"Error code {err}: {gluErrorString(err).decode('ansi')}" for err in error_codes)
      self.error_showing_preview.emit(error_msg)
      return
    
    self.init_lights()
    
    self.update()
    self.show()
  
  def unload_model(self):
    self.model = None
    self.unload_anims()
    self.hide()
  
  def unload_anims(self):
    self.brk = None
    self.j3dultra_brk = None
    self.btp = None
    self.j3dultra_btp = None
    self.btk = None
    self.j3dultra_btk = None
    self.bck = None
    self.j3dultra_bck = None
    self.bca = None
    self.j3dultra_bca = None
    self.bva = None
    self.j3dultra_bva = None
  
  def guesstimate_model_bbox(self, j3d_model: J3D) -> tuple[np.ndarray, np.ndarray]:
    # Estimate the model's size based on its visual shape bounding boxes.
    points = []
    for shape in j3d_model.shp1.shapes:
      points.append(shape.bounding_box_min.xyz)
      points.append(shape.bounding_box_max.xyz)
    bbox_min = np.min(points, axis=0)
    bbox_max = np.max(points, axis=0)
    aabb_diag_len = np.linalg.norm(bbox_max - bbox_min)
    # print('shape', aabb_diag_len)
    
    if aabb_diag_len < 0.1:
      # If the shape bounding boxes aren't properly set, try to fall back on using the joint
      # positions and bounding boxes instead.
      points = []
      for joint in j3d_model.jnt1.joints:
        points.append(joint.translation.xyz)
        points.append(joint.bounding_box_min.xyz)
        points.append(joint.bounding_box_max.xyz)
      bbox_min = np.min(points, axis=0)
      bbox_max = np.max(points, axis=0)
      aabb_diag_len = np.linalg.norm(bbox_max - bbox_min)
      # print('joint', aabb_diag_len, bbox_min, bbox_max)
      
    if aabb_diag_len < 0.1:
      # If the shapes and joints both have bad bounding boxes set, we have to fall back on the raw
      # vertex coordinates. This is hacky and inaccurate because it doesn't take rigging into
      # account, so certain vertices will appear near the origin instead of near their joints.
      # TODO: Try to improve this hack in the future by looking at rigging.
      vertices = j3d_model.vtx1.attributes[GX.Attr.Position]
      bbox_min = np.min(vertices, axis=0)
      bbox_max = np.max(vertices, axis=0)
      aabb_diag_len = np.linalg.norm(bbox_max - bbox_min)
      # print('vtx1', aabb_diag_len)
    
    return bbox_min, bbox_max
  
  def get_preview_compatible_j3d(self, orig_j3d: J3D) -> J3D:
    # return orig_j3d
    
    # We have to save the original J3D for the changes to its chunks to be reflected properly.
    # Simply copying orig_j3d.data is not sufficient on its own.
    orig_j3d.save()
    # TODO: implement copying just the instance, without having to serialize and deserialize it here.
    hack_j3d = J3D(fs.make_copy_data(orig_j3d.data))
    chunks_modified = set()
    
    # Wind Waker has a hardcoded system where the textures that control toon shading are dynamically
    # replaced at runtime so they don't have to be packed into each model individually.
    # Any texture with a name starting with "ZA" gets replaced with: files/res/System.arc/toon.bti
    # Any texture with a name starting with "ZB" gets replaced with: files/res/System.arc/toonex.bti
    # We need to replace these textures or else the lighting will appear messed up in the preview.
    for texture_name, textures in hack_j3d.tex1.textures_by_name.items():
      replacement_filename = None
      if texture_name.startswith("ZA"):
        replacement_filename = "toon.bti"
      elif texture_name.startswith("ZB"):
        replacement_filename = "toonex.bti"
      if replacement_filename is None:
        continue
      
      with open(os.path.join(ASSETS_PATH, replacement_filename), "rb") as f:
        replacement_data = BytesIO(f.read())
      replacement_bti = BTI(replacement_data)
      
      for texture in textures:
        if fs.data_len(texture.image_data) != 0x20:
          # If the length of the image data doesn't exactly match the placeholder, then this might
          # not actually be a Wind Waker placeholder texture. It could be a different game that just
          # happens to have a texture starting with "ZA" or "ZB". So skip replacing the texutre.
          continue
        texture.read_header(replacement_bti.data)
        texture.image_data = fs.make_copy_data(replacement_bti.image_data)
        texture.palette_data = fs.make_copy_data(replacement_bti.palette_data)
        texture.save_header_changes()
        chunks_modified.add("TEX1")
    
    # Hack to simulate hiding certain materials.
    # We simply set the cull mode for all materials we want to hide to "Cull All".
    for mat_index in self.hidden_material_indexes:
    # self.hidden_material_indexes.sort()
    # for mat_index in reversed(self.hidden_material_indexes):
      if "MAT3" not in hack_j3d.chunk_by_type:
        continue
      if mat_index >= len(hack_j3d.mat3.materials):
        continue
      hack_j3d.mat3.materials[mat_index].cull_mode = GX.CullMode.Cull_All
      # del hack_j3d.mat3.materials[mat_index]
      chunks_modified.add("MAT3")
    
    if chunks_modified:
      hack_j3d.save(only_chunks=chunks_modified)
      return hack_j3d
    else:
      return orig_j3d
  
  #region Animation
  
  def load_brk(self, brk: J3D):
    self.brk = brk
    
    if self.model is None:
      return
    
    # NOTE: Loading a new brk does not reset the registers to how they originally were
    # this means loading several brks can have them all visible at once, depending on how
    # they're set up.
    self.model.attachBrk(data=fs.read_all_bytes(self.brk.data))
    self.j3dultra_brk = self.model.getBrk()
    
    self.set_anim_frame(0)
    
    # TODO: when reloading the model due to different isolated visibility, we need to re-attach the
    # brk. maybe make a separate func: load_model vs reload_model
  
  def load_btp(self, btp: J3D):
    self.btp = btp
    
    if self.model is None:
      return
    
    self.model.attachBtp(data=fs.read_all_bytes(self.btp.data))
    self.j3dultra_btp = self.model.getBtp()
    
    self.set_anim_frame(0)
  
  def load_btk(self, btk: J3D):
    self.btk = btk
    
    if self.model is None:
      return
    
    self.model.attachBtk(data=fs.read_all_bytes(self.btk.data))
    self.j3dultra_btk = self.model.getBtk()
    
    self.set_anim_frame(0)
    
    # TODO: when reloading the model due to different isolated visibility, we need to re-attach the
    # btk. maybe make a separate func: load_model vs reload_model
  
  def load_bck(self, bck: J3D):
    self.bck = bck
    
    if self.model is None:
      return
    
    if bck.ank1.anims_count != self.j3d.jnt1.joint_count:
      error_message = "This animation is not for this model.\nThe loaded BCK animation has animations for %s joints, while the currently loaded model has %s joints." % (
        self.window().stringify_number(bck.ank1.anims_count, min_hex_chars=2),
        self.window().stringify_number(self.j3d.jnt1.joint_count, min_hex_chars=2),
      )
      QMessageBox.warning(self, "Wrong joint count", error_message)
      return
    
    self.model.attachBck(data=fs.read_all_bytes(self.bck.data))
    self.j3dultra_bck = self.model.getBck()
    
    self.set_anim_frame(0)
  
  def load_bca(self, bca: J3D):
    self.bca = bca
    
    if self.model is None:
      return
    
    self.model.attachBca(data=fs.read_all_bytes(self.bca.data))
    self.j3dultra_bca = self.model.getBca()
    
    if self.j3dultra_bck:
      # BCK takes precedence over BCA, so we have to unload the BCK for the BCA to show up.
      self.model.detachBck()
      self.bck = None
      self.j3dultra_bck = None
    
    self.set_anim_frame(0)
  
  def load_bva(self, bva: J3D):
    self.bva = bva
    
    if self.model is None:
      return
    
    self.model.attachBva(data=fs.read_all_bytes(self.bva.data))
    self.j3dultra_bva = self.model.getBva()
    
    self.set_anim_frame(0)
  
  def each_anim(self):
    for anim in [self.j3dultra_brk, self.j3dultra_btp, self.j3dultra_btk, self.j3dultra_bck, self.j3dultra_bca, self.j3dultra_bva]:
      if anim is None:
        continue
      yield anim
  
  def set_anim_frame(self, frame: int):
    for anim in self.each_anim():
      anim.setFrame(frame, self.anim_paused)
      self.should_update_render = True
  
  def set_anim_paused(self, paused: bool):
    self.anim_paused = paused
    for anim in self.each_anim():
      anim.setPaused(paused)
  
  def tick_anims(self, delta_time: float):
    if delta_time <= 0:
      return
    
    for anim in self.each_anim():
      anim.tick(delta_time)
      self.should_update_render = True
  
  #endregion
  
  def calculate_light_pos(self, frac):
    angle = (frac % 1.0) * np.pi*2
    return np.cos(angle), np.sin(angle)
  
  def init_lights(self):
    if not self.enable_j3dultra:
      return
    if not self.model:
      return
    
    self.lights = []
    
    use_ww_toon_lighting = False
    if self.j3d is not None and any(re.search("^(?:Z[AB]|V_)?toon", texname) for texname in self.j3d.tex1.texture_names):
      # TODO: Hack to try to detect Wind Waker models. Not perfectly accurate.
      use_ww_toon_lighting = True
    
    if self.animate_light:
      light_anim_time = self.total_time_elapsed
    else:
      light_anim_time = 0
    
    if use_ww_toon_lighting:
      # Wind Waker lighting.
      x, z = self.calculate_light_pos(light_anim_time / 5)
      light_pos = [-5000*x, 4000, 5000*z]
      light_dir = -(light_pos / np.linalg.norm(light_pos))
      light_col = [1, 0, 0, 1]
      angle_atten = [1, 0, 0]
      dist_atten = [1, 0, 0]
      follow_camera = False
      light = J3DLight(light_pos, light_dir, light_col, angle_atten, dist_atten, follow_camera)
      self.lights.append(light)
      
      for i in range(1, 8):
        light_pos = [5000, -4000, -5000]
        light_dir = -(light_pos / np.linalg.norm(light_pos))
        light_col = [0, 0, 1, 0]
        angle_atten = [1, 0, 0]
        dist_atten = [1, 0, 0]
        follow_camera = False
        light = J3DLight(light_pos, light_dir, light_col, angle_atten, dist_atten, follow_camera)
        self.lights.append(light)
    else:
      # Plain default lighting.
      x, z = self.calculate_light_pos(light_anim_time / 5)
      light_pos = [-5000*x, 4000, 5000*z]
      light_dir = -(light_pos / np.linalg.norm(light_pos))
      light_col = [1, 1, 1, 1]
      light_col = [x*0.3 for x in light_col]
      angle_atten = [1, 0, 0]
      angle_atten = [x*0.5 for x in angle_atten]
      dist_atten = [1, 0, 0]
      dist_atten = [x*0.8 for x in dist_atten]
      follow_camera = False
      light = J3DLight(light_pos, light_dir, light_col, angle_atten, dist_atten, follow_camera)
      self.lights.append(light)
      
      for i in range(1, 8):
        x, z = self.calculate_light_pos((i - 1)/7)
        light_pos = [5000*x, -3000*x, -5000*z]
        light_dir = -(light_pos / np.linalg.norm(light_pos))
        light_col = [1, 1, 1, 1]
        light_col = [x*0.15 for x in light_col]
        angle_atten = [1, 0, 0]
        angle_atten = [x*0.5 for x in angle_atten]
        dist_atten = [1, 0, 0]
        dist_atten = [x*0.8 for x in dist_atten]
        follow_camera = False
        light = J3DLight(light_pos, light_dir, light_col, angle_atten, dist_atten, follow_camera)
        self.lights.append(light)
    
    for i, light in enumerate(self.lights):
      assert 0 <= i <= 7
      self.model.setLight(light, i)
  
  def update_lights(self):
    if not self.enable_j3dultra:
      return
    if not self.lights:
      return
    if not self.model:
      return
    
    if self.animate_light:
      light_anim_time = self.total_time_elapsed
    else:
      light_anim_time = 0
    
    x, z = self.calculate_light_pos(light_anim_time / 5)
    self.lights[0].position.x = -5000*x
    self.lights[0].position.z = 5000*z
    self.model.setLight(self.lights[0], 0)
    
    self.should_update_render = True
  
  def draw_grid_widget(self):
    # Tell OpenGL about the camera's current perspective.
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(self.fovy, self.aspect, self.near_plane, self.far_plane)
    gluLookAt(
      *self.camera.position,
      *self.camera.target,
      0, 1, 0
    )
    
    glMatrixMode(GL_MODELVIEW)
    
    # Draw the grid.
    grid_size = 1000
    grid_rows = 10
    grid_increments = grid_size / grid_rows
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glBegin(GL_LINES)
    
    glColor3f(0.5, 0.5, 0.5) # Grey
    for x in range(grid_rows+1):
      glVertex3f(x*grid_increments-grid_size/2, 0, -grid_size/2)
      glVertex3f(x*grid_increments-grid_size/2, 0, grid_size/2)
    for z in range(grid_rows+1):
      glVertex3f(-grid_size/2, 0, z*grid_increments-grid_size/2)
      glVertex3f(grid_size/2, 0, z*grid_increments-grid_size/2)
    
    # Make grid lines passing through the origin stand out.
    glColor3f(0.8, 0.8, 0.8) # Whiteish grey
    glVertex3f(0, 0, -grid_size/2)
    glVertex3f(0, 0, grid_size/2)
    glVertex3f(-grid_size/2, 0, 0)
    glVertex3f(grid_size/2, 0, 0)
    
    glEnd()
  
  def draw_viewport_orientation_widget(self):
    # Position the widget in the bottom left of the viewport.
    width = self.width()//5
    height = self.height()//5
    width = min(width, height)
    height = width
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(self.fovy, 1, 0.01, 10.0)
    cam_offset = self.camera.position - self.camera.target
    cam_offset = cam_offset / np.linalg.norm(cam_offset)
    cam_offset *= 2
    gluLookAt(
      *cam_offset,
      0, 0, 0,
      0, 1, 0
    )
    
    # Draw the axes.
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    axis_len = 0.5
    glBegin(GL_LINES)
    glColor3f(1.0, 0.0, 0.0) # Red
    glVertex3f(0, 0, 0)
    glVertex3f(axis_len, 0, 0) # X
    glColor3f(0.0, 1.0, 0.0) # Green
    glVertex3f(0, 0, 0)
    glVertex3f(0, axis_len, 0) # Y
    glColor3f(0.0, 0.0, 1.0) # Blue
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, axis_len) # Z
    glEnd()
  
  def draw_light_widget(self):
    if not self.show_debug_light_widget:
      # Light debugging function, don't show to the user.
      return
    if not self.lights:
      return
  
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(self.fovy, self.aspect, self.near_plane, self.far_plane)
    gluLookAt(
      *self.camera.position,
      *self.camera.target,
      0, 1, 0
    )
    
    glMatrixMode(GL_MODELVIEW)
    
    glBegin(GL_LINES)
    
    # Draw a colored line from the origin to each light.
    for light in self.lights:
      col = light.color
      glColor3f(col.x, col.y, col.z)
      pos = light.position
      glVertex3f(0, 0, 0)
      glVertex3f(pos.x, pos.y, pos.z)
    
    glEnd()
  
  def draw_model(self):
    if not self.enable_j3dultra:
      return
    
    if self.model is not None:
      self.model.render()
    ultra.render(0.0, self.camera.position)
  
  def update(self):
    if not self.enable_j3dultra:
      return
    
    # Automatically calculate near and far planes so that models of any size will be visible.
    self.far_plane = self.camera.distance * 10
    self.far_plane = max(self.far_plane, 40000.0)
    self.near_plane = self.far_plane / 10000.0
    
    proj = matrix44.create_perspective_projection_matrix(
      self.fovy,
      self.aspect,
      self.near_plane, self.far_plane
    )
    # TODO: This might sometimes divide by zero when looking straight down.
    ultra.setCamera(
      proj.ravel().tolist(),
      self.camera.view_matrix.ravel().tolist()
    )
    
    super().update()
  
  def process_frame(self):
    current_time = time.monotonic()
    delta_time = current_time - self.last_render_time
    self.total_time_elapsed += delta_time
    self.last_render_time = current_time
    
    if self.context() is None:
      # Not yet initialized.
      return
    
    self.process_camera_movement()
    
    if self.animate_light:
      self.update_lights()
    
    self.tick_anims(delta_time)
    
    if self.j3dultra_bck is not None:
      self.bck_frame_changed.emit(self.j3dultra_bck.getFrame())
    
    if self.should_update_render:
      self.update()
      self.should_update_render = False
  
  def process_camera_movement(self):
    adjusted_cam_move_speed = self.base_cam_move_speed * self.camera.distance / 1000.0
    for key, speed_mult in self.KEY_TO_SPEED_MULTIPLIER.items():
      if self.key_is_held[key]:
        adjusted_cam_move_speed *= speed_mult
    offset = np.zeros(3)
    for key, move_dir in self.KEY_TO_MOVE_DIR.items():
      if self.key_is_held[key]:
        offset += np.array(move_dir) * adjusted_cam_move_speed
    if offset.any():
      self.camera.move(offset)
      self.should_update_render = True
  
  def reset_camera(self, pitch=None, yaw=None):
    if pitch is None:
      pitch = self.base_pitch
    if yaw is None:
      yaw = self.base_yaw
    self.camera.distance = self.base_cam_dist
    self.camera.pitch = pitch
    self.camera.yaw = yaw
    self.camera.target = np.array(self.base_center) # Make a copy so we don't modify it
    self.camera.update()
    self.should_update_render = True
  
  def rotate_camera_orbit(self, x: float, y: float):
    self.camera.rotate_orbit(x, y)
    self.should_update_render = True
    
  def rotate_camera_look(self, x: float, y: float):
    self.camera.rotate_look(x, y)
    self.should_update_render = True
    
  def zoom_camera(self, zoom_amount):
    adjusted_zoom_amount = zoom_amount * self.camera.distance / 1000.0
    self.camera.zoom(adjusted_zoom_amount)
    self.should_update_render = True
  
  def keyPressEvent(self, event):
    if event.key() == Qt.Key.Key_R:
      self.reset_camera()
      event.accept()
    elif event.key() in self.KEY_TO_CAMERA_ANGLE:
      pitch, yaw = self.KEY_TO_CAMERA_ANGLE[event.key()]
      self.reset_camera(pitch=pitch, yaw=yaw)
    elif event.key() == Qt.Key.Key_Space:
      self.show_widgets = not self.show_widgets
      self.should_update_render = True
      event.accept()
    elif event.key() in self.key_is_held:
      self.key_is_held[event.key()] = True
      event.accept()
    else:
      event.ignore()
  
  def keyReleaseEvent(self, event):
    if event.key() in self.key_is_held:
      self.key_is_held[event.key()] = False
      event.accept()
    else:
      event.ignore()
    
  def mousePressEvent(self, event):
    self.prev_mouse_pos = event.position()
    
    super().mousePressEvent(event)
  
  def mouseMoveEvent(self, event):
    if self.prev_mouse_pos is not None:
      delta_pos = event.position() - self.prev_mouse_pos
      if event.buttons() == Qt.RightButton:
        self.rotate_camera_look(delta_pos.y(), -delta_pos.x())
      else:
        self.rotate_camera_orbit(delta_pos.y(), -delta_pos.x())
    
    self.prev_mouse_pos = event.position()
    
    super().mouseMoveEvent(event)
  
  def mouseReleaseEvent(self, event):
    self.prev_mouse_pos = None
    
    super().mouseReleaseEvent(event)
  
  def wheelEvent(self, event):
    delta = event.angleDelta().y()
    if event.buttons() == Qt.RightButton:
      if delta > 0:
        self.base_cam_move_speed += 4
      elif delta < 0:
        self.base_cam_move_speed -= 4
      self.base_cam_move_speed = max(4, self.base_cam_move_speed)
    else:
      self.zoom_camera(delta)
    
    event.accept()
  
  def focusOutEvent(self, event: QFocusEvent):
    for key in self.key_is_held:
      self.key_is_held[key] = False
    
    super().focusOutEvent(event)
  
  def closeEvent(self, event):
    if not self.enable_j3dultra:
      return
    
    ultra.cleanup()
