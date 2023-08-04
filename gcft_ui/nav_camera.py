import numpy as np
from pyrr import matrix44, Quaternion, Vector3

class Camera:
  def __init__(self, distance=10.0, pitch=0.0, yaw=0.0, target=np.zeros(3)):
    self.distance = distance
    self.pitch = pitch
    self.yaw = yaw
    self.target = target
    self.update()
  
  def update(self, orbit=True):
    # Calculate the camera's position based on distance, pitch, and yaw
    cos_pitch = np.cos(np.radians(self.pitch))
    sin_pitch = np.sin(np.radians(self.pitch))
    cos_yaw = np.cos(np.radians(self.yaw))
    sin_yaw = np.sin(np.radians(self.yaw))

    offset = self.distance * np.array([cos_pitch * sin_yaw, sin_pitch, cos_pitch * cos_yaw])
    
    if orbit:
      # Rotate the camera around the target.
      self.position = self.target + offset
    else:
      # Rotate the target around the camera.
      self.target = self.position - offset

    # Calculate the view matrix
    self.view_matrix = matrix44.create_look_at(self.position, self.target, [0, 1, 0])
  
  def rotate_orbit(self, d_pitch, d_yaw):
    self.pitch += d_pitch
    self.yaw += d_yaw
    self.pitch = np.clip(self.pitch, -90, 90.0)
    self.update()
  
  def rotate_look(self, d_pitch, d_yaw):
    self.pitch += d_pitch
    self.yaw += d_yaw
    self.pitch = np.clip(self.pitch, -90, 90.0)
    self.update(orbit=False)
  
  def zoom(self, delta_distance):
    self.distance -= delta_distance
    self.distance = max(10.0, self.distance)
    self.update()
  
  def set_target(self, target):
    self.target = target
    self.update()
  
  def move(self, delta_position):
    rotation = Quaternion.from_y_rotation(np.radians(self.yaw))
    rotation *= Quaternion.from_x_rotation(np.radians(-self.pitch))
    
    # Y movement is unaffacted by camera angle.
    delta_position_y = delta_position[1]
    delta_position[1] = 0
    rotated_delta = rotation * Vector3(delta_position)
    rotated_delta[1] += delta_position_y
    
    self.target += rotated_delta
    self.update()
