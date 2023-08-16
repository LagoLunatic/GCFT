
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

# TODO: bignum spinbox should take an option to be in hexadecimal
# spinbox.displayIntegerBase(16) setPrefix
# https://stackoverflow.com/questions/26581444/qspinbox-with-unsigned-int-for-hex-input

# TODO: need a custom rotation spinbox class
# internally it would store a u16, but would display it as e.g.:
# 90° instead of 0x4000, 25.6° instead of 0x1234, etc

class BigIntSpinbox(QAbstractSpinBox):
  # The default QSpinbox uses signed 32-bit integers internally, so if you try to make it display an
  # unsigned 32-bit integer you will get an overflow error.
  # This class basically just reimplements QSpinbox in Python to take advantage of Python integers.
  
  # Signal(int) would overflow if the value doesn't fit in a 32-bit signed integer, so use a Python
  # object to send the value through the signal instead.
  valueChanged = Signal(object)
  
  def __init__(self, parent: QWidget = None):
    super().__init__(parent)
    
    self._minimum = 0
    self._maximum = 99
    self._value = 0
    self._singleStep = 1
    self._validator = BigIntValidator(self._minimum, self._maximum)
    self.lineEdit().setValidator(self._validator)
    self.lineEdit().editingFinished.connect(self.setText)
  
  def minimum(self) -> int:
    return self._minimum
  
  def maximum(self) -> int:
    return self._maximum
  
  def setMinimum(self, min: int):
    assert isinstance(min, int)
    self._minimum = min
    self._validator.setRange(self._minimum, self._maximum)
  
  def setMaximum(self, max: int):
    assert isinstance(max, int)
    self._maximum = max
    self._validator.setRange(self._minimum, self._maximum)
  
  def setRange(self, min: int, max: int):
    self.setMinimum(min)
    self.setMaximum(max)
  
  def value(self) -> int:
    return self._value
  
  def setValue(self, val: int):
    assert isinstance(val, int)
    self._value = val
    self.lineEdit().setText(str(val))
    self.valueChanged.emit(self._value)
  
  def singleStep(self):
    return self._singleStep
  
  def setSingleStep(self, singleStep: int):
    assert isinstance(singleStep, int)
    self._singleStep = abs(singleStep)
  
  def stepBy(self, steps: int):
    new_val = self._value + steps*self._singleStep
    new_val = max(self._minimum, new_val)
    new_val = min(self._maximum, new_val)
    self.setValue(new_val)
  
  def stepEnabled(self):
    return self.StepEnabledFlag.StepUpEnabled | self.StepEnabledFlag.StepDownEnabled
  
  def setText(self):
    self.setValue(int(self.lineEdit().text()))

class BigIntValidator(QIntValidator):
  def __init__(self, minimum, maximum, parent=None):
    super().__init__(parent)
    self._minimum = minimum
    self._maximum = maximum
  
  def validate(self, input, pos):
    input = input.strip()
    if input == '':
      return QValidator.State.Intermediate, input, 0
    if input == '-' and self._minimum < 0:
      return QValidator.State.Intermediate, input, pos
    try:
      val = int(input)
    except ValueError:
      return QValidator.State.Invalid, input, pos
    
    if val > self._maximum:
      return QValidator.State.Invalid, input, pos
    elif val < self._minimum:
      return QValidator.State.Invalid, input, pos
    else:
      return QValidator.State.Acceptable, input, pos
  
  def fixup(self, input):
    input = input.strip()
    try:
      val = int(input)
    except ValueError:
      if self._minimum <= 0 <= self._maximum:
        return str(0)
      return str((self._minimum + self._maximum) // 2)
    return input
  
  def setRange(self, minimum, maximum):
    self._minimum = minimum
    self._maximum = maximum
