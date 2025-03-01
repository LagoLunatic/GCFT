
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

import os

from gcft_ui.qt_init import load_ui_file
from gcft_paths import GCFT_ROOT_PATH
if os.environ["QT_API"] == "pyside6":
  from gcft_ui.uic.ui_anim_control import Ui_AnimControl
else:
  Ui_CosmeticTab = load_ui_file(os.path.join(GCFT_ROOT_PATH, "gcft_ui", "anim_control.ui"))

class AnimControl(QGroupBox):
  anim_type_paused_changed = Signal(str, bool)
  anim_type_slider_frame_changed = Signal(str, int)
  anim_type_detached = Signal(str)
  
  def __init__(self, parent=None):
    super().__init__(parent)
    self.ui = Ui_AnimControl()
    self.ui.setupUi(self)
    
    self.paused = False
    self.duration = 0
    
    self.ui.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
    self.ui.pause_button.clicked.connect(self.toggle_anim_paused)
    self.ui.seek_slider.valueChanged.connect(self.update_anim_frame_by_type)
    self.ui.detach_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))
    self.ui.detach_button.clicked.connect(self.detach_anim)
    
    self.update_anim_pause_button_icon()
    
    self.hide()
  
  def toggle_anim_paused(self):
    if self.paused and self.ui.seek_slider.value() >= self.ui.seek_slider.maximum():
      # If paused at the end of the animation, restart from the beginning.
      self.ui.seek_slider.setValue(0)
    self.paused = not self.paused
    self.anim_type_paused_changed.emit(self.property("anim_type"), self.paused)
    self.update_anim_pause_button_icon()
  
  def update_anim_frame_by_type(self, frame: int):
    self.anim_type_slider_frame_changed.emit(self.property("anim_type"), frame)
    self.paused = True
    self.update_anim_pause_button_icon()
  
  def detach_anim(self):
    self.anim_type_detached.emit(self.property("anim_type"))
    self.hide()
  
  def update_anim_pause_button_icon(self):
    if self.paused:
      self.ui.pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
    else:
      self.ui.pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
  
  def update_slider_from_anim_frame(self, frame: float):
    self.ui.seek_slider.blockSignals(True)
    self.ui.seek_slider.setValue(frame)
    self.ui.seek_slider.blockSignals(False)
    if frame >= self.duration:
      self.paused = True
      self.anim_type_paused_changed.emit(self.property("anim_type"), self.paused)
      self.update_anim_pause_button_icon()
  
  def load_anim(self, duration: int, anim_format_name: str, anim_name: str):
    self.duration = duration
    
    max_frame = self.duration-1
    if max_frame < 0:
      max_frame = 0
    
    title = anim_format_name
    if anim_name:
      title += f": {anim_name}"
    self.setTitle(title)
    
    self.ui.seek_slider.setMinimum(0)
    self.ui.seek_slider.setMaximum(max_frame)
    self.ui.seek_slider.setValue(0)
    
    self.paused = False
    self.anim_type_paused_changed.emit(self.property("anim_type"), self.paused)
    self.update_anim_pause_button_icon()
    
    self.show()
