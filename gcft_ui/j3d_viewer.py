
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtOpenGLWidgets import *

from gcft_ui.nav_camera import Camera
from gclib.j3d import J3DFile
from gclib.gx_enums import GXAttr
from gclib import fs_helpers as fs

try:
  print("j3dultra is installed")
  import J3DUltra as ultra # type: ignore
  from J3DUltra import J3DLight # type: ignore
  J3DULTRA_INSTALLED = True
except ImportError:
  print("j3dultra not installed")
  J3DULTRA_INSTALLED = False

import numpy as np
from pyrr import matrix44
from OpenGL.GL import *
from OpenGL.GLU import *

class J3DViewer(QOpenGLWidget):
  DESIRED_FPS = 30
  DELAY_BETWEEN_FRAMES = 1000 // 30
  
  KEY_TO_MOVE_DIR = {
    Qt.Key_W: [0, 0, -1],
    Qt.Key_A: [-1, 0, 0],
    Qt.Key_S: [0, 0, 1],
    Qt.Key_D: [1, 0, 0],
    Qt.Key_Q: [0, -1, 0],
    Qt.Key_E: [0, 1, 0],
  }
  KEY_TO_SPEED_MULTIPLIER = {
    Qt.Key_Shift: 4.0,
    Qt.Key_Control: 0.25,
  }
  BASE_CAMERA_MOVE_SPEED = 40.0
  
  def __init__(self, parent):
    super().__init__(parent)
    
    self.should_update_render = False
    self.animate_light = True
    self.show_debug_light_widget = True
    self.prev_mouse_pos = None
    self.key_is_held = {}
    for key in self.KEY_TO_MOVE_DIR:
      self.key_is_held[key] = False
    for key in self.KEY_TO_SPEED_MULTIPLIER:
      self.key_is_held[key] = False
    self.show_widgets = True
    
    self.base_cam_move_speed = self.BASE_CAMERA_MOVE_SPEED
    self.fovy = 45.0
    self.base_cam_dist = 1000.0
    self.base_pitch = 30.0
    self.base_yaw = 35.0
    self.base_center = np.zeros(3)
    self.aspect = 1.0
    self.model = None
    self.camera = Camera(
      distance=self.base_cam_dist,
      pitch=self.base_pitch, yaw=self.base_yaw,
      target=self.base_center
    )
    
    self.lights = []
    
    self.frame_timer = QTimer()
    self.frame_timer.setInterval(self.DELAY_BETWEEN_FRAMES)
    self.frame_timer.timeout.connect(self.process_frame)
    
    self.elapsed_timer= QElapsedTimer()
    
    self.frame_timer.start()
    self.elapsed_timer.start()
  
  def initializeGL(self):
    if not J3DULTRA_INSTALLED:
      return
    
    if not ultra.init():
      raise Exception("Failed to initialize J3DUltra.")
    
    self.init_lights()
    
    self.clear()

    width = self.width()
    height = self.height()
    self.aspect = width / height
    
    glViewport(0, 0, width, height)
  
  def resizeGL(self, width: int, height: int):
    glViewport(0, 0, width, height)
    self.aspect = self.width() / self.height()
    self.update()
  
  def paintGL(self):
    self.clear()
    
    if self.show_widgets:
      self.draw_grid_widget()
    
    self.draw_model()
    
    if self.show_widgets:
      self.draw_viewport_orientation_widget()
    
    if self.show_widgets:
      self.draw_light_widget()
  
  def clear(self):
    glClearColor(0.25, 0.3, 0.4, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  
  def load_model(self, j3d_model, reset_camera=False):
    if not J3DULTRA_INSTALLED:
      return
    
    self.model = ultra.loadModel(data=fs.read_all_bytes(j3d_model.data))
    self.elapsed_timer.restart()
    
    if reset_camera:
      bbox_min, bbox_max = self.guesstimate_model_bbox(j3d_model)
      self.base_center = (bbox_min + bbox_max) / 2
      aabb_diag_len = np.linalg.norm(bbox_max - bbox_min)
      if aabb_diag_len < 10.0:
        aabb_diag_len = 10.0
      self.base_cam_dist = (aabb_diag_len / 2) / abs(np.sin(np.radians(self.fovy)/2.0))
      # print("bbox", bbox_min, bbox_max)
      # print(self.base_center, self.base_cam_dist)
      
      self.reset_camera()
    
    self.update()
  
  def guesstimate_model_bbox(self, j3d_model: J3DFile) -> tuple[np.ndarray, np.ndarray]:
    # Estimate the model's size based on its visual shape bounding boxes.
    points = []
    for shape in j3d_model.shp1.shapes:
      points.append(shape.bbox_min)
      points.append(shape.bbox_max)
    bbox_min = np.min(points, axis=0)
    bbox_max = np.max(points, axis=0)
    aabb_diag_len = np.linalg.norm(bbox_max - bbox_min)
    # print('shape', aabb_diag_len)
    
    if aabb_diag_len < 0.1:
      # If the shape bounding boxes aren't properly set, try to fall back on using the joint
      # positions and bounding boxes instead.
      points = []
      for joint in j3d_model.jnt1.joints:
        points.append(joint.position)
        points.append(joint.bbox_min)
        points.append(joint.bbox_max)
      bbox_min = np.min(points, axis=0)
      bbox_max = np.max(points, axis=0)
      aabb_diag_len = np.linalg.norm(bbox_max - bbox_min)
      # print('joint', aabb_diag_len, bbox_min, bbox_max)
      
    if aabb_diag_len < 0.1:
      # If the shapes and joints both have bad bounding boxes set, we have to fall back on the raw
      # vertex coordinates. This is hacky and inaccurate because it doesn't take rigging into
      # account, so certain vertices will appear near the origin instead of near their joints.
      # TODO: Try to improve this hack in the future by looking at rigging.
      vertices = j3d_model.vtx1.attributes[GXAttr.Position]
      bbox_min = np.min(vertices, axis=0)
      bbox_max = np.max(vertices, axis=0)
      aabb_diag_len = np.linalg.norm(bbox_max - bbox_min)
      # print('vtx1', aabb_diag_len)
    
    return bbox_min, bbox_max
  
  def calculate_light_pos(self):
    angle = ((self.elapsed_timer.elapsed() / 5000) % 1.0) * np.pi*2
    return np.cos(angle), np.sin(angle)
  
  def init_lights(self):
    x, z = self.calculate_light_pos()
    
    if False:
      # Wind Waker lighting.
      # TODO: either detect WW materials automatically, or allow the user to change lighting mode
      light_pos = [-5000*x, 4000, 5000*z]
      light_dir = -(light_pos / np.linalg.norm(light_pos))
      light_col = [1, 0, 1, 1]
      angle_atten = [1.075, 0, 0]
      dist_atten = [1.075, 0, 0]
      light = J3DLight(light_pos, light_dir, light_col, angle_atten, dist_atten)
      self.lights.append(light)
      
      light_pos = [5000, 4000, -5000]
      light_dir = -(light_pos / np.linalg.norm(light_pos))
      light_col = [0, 0, 1, 1]
      angle_atten = [1.075, 0, 0]
      dist_atten = [1.075, 0, 0]
      light = J3DLight(light_pos, light_dir, light_col, angle_atten, dist_atten)
      self.lights.append(light)
    else:
      # Plain default lighting.
      # TODO: improve this
      light_pos = [-5000*x, 4000, 5000*z]
      light_dir = -(light_pos / np.linalg.norm(light_pos))
      light_col = [1, 1, 1, 1]
      angle_atten = [1, 1, 1]
      dist_atten = [1, 1, 1]
      light = J3DLight(light_pos, light_dir, light_col, angle_atten, dist_atten)
      self.lights.append(light)
      
      light_pos = [5000, 4000, -5000]
      light_dir = -(light_pos / np.linalg.norm(light_pos))
      light_col = [1, 1, 1, 1]
      angle_atten = [1, 1, 1]
      dist_atten = [1, 1, 1]
      light = J3DLight(light_pos, light_dir, light_col, angle_atten, dist_atten)
      self.lights.append(light)
      
      for i in range(2, 8):
        self.lights.append(light)
    
    for i, light in enumerate(self.lights):
      assert 0 <= i <= 7
      ultra.setLight(light, i)
  
  def update_lights(self):
    if not self.lights:
      return
    
    if not J3DULTRA_INSTALLED:
      return
    
    x, z = self.calculate_light_pos()
    self.lights[0].position.x = -5000*x
    self.lights[0].position.z = 5000*z
    ultra.setLight(self.lights[0], 0)
    
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
    glViewport(0, 0, width, width)
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
  
    glViewport(0, 0, self.width(), self.height())
    
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
    
    glColor3f(1.0, 1.0, 0.0) # Yellow
    
    # Draw a line from the origin to the rotating primary light.
    pos = (
      self.lights[0].position.x,
      self.lights[0].position.y,
      self.lights[0].position.z,
    )
    glVertex3f(0, 0, 0)
    glVertex3f(*pos)
    
    glEnd()
  
  def draw_model(self):
    glViewport(0, 0, self.width(), self.height())
    if self.model is not None:
      self.model.render()
    ultra.render(0.0, self.camera.position)
  
  def update(self):
    if not J3DULTRA_INSTALLED:
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
    self.process_camera_movement()
    
    if self.animate_light:
      self.update_lights()
    
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
  
  def reset_camera(self):
    self.camera.distance = self.base_cam_dist
    self.camera.pitch = self.base_pitch
    self.camera.yaw = self.base_yaw
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
    if event.key() == Qt.Key_R:
      self.reset_camera()
      event.accept()
    elif event.key() == Qt.Key_Space:
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
    if not J3DULTRA_INSTALLED:
      return
    
    ultra.cleanup()
