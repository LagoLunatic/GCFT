import typing
from enum import Enum
import colorsys
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.bunfoe import BUNFOE, Field, fields

from gcft_ui.custom_widgets import BigIntSpinbox
from gclib.bunfoe_types import Vector, Matrix, RGBA

class BunfoeWidget(QWidget):
  pass

class BunfoeEditor(QWidget):
  field_value_changed = Signal()
  
  def __init__(self):
    super().__init__()
    
    self.cached_top_level_bunfoe_editor_widgets: dict[type, BunfoeWidget] = {}
  
  def clear_layout_recursive(self, layout: QLayout):
    while layout.count():
      item = layout.takeAt(0)
      widget = item.widget()
      if widget:
        if isinstance(widget, BunfoeWidget):
          widget.hide()
        else:
          widget.deleteLater()
      sublayout = item.layout()
      if sublayout:
        self.clear_layout_recursive(sublayout)
  
  def set_layout_disabled_recursive(self, layout: QLayout, disabled=True):
    for i in range(layout.count()):
      item = layout.itemAt(i)
      widget = item.widget()
      if widget:
        widget.setDisabled(disabled)
      sublayout = item.layout()
      if sublayout:
        self.set_layout_disabled_recursive(sublayout, disabled=disabled)
  
  def prettify_name(self, name: str, title: bool = True):
    pretty_name = name.replace("_", " ").strip()
    if title:
      pretty_name = pretty_name.title()
    return pretty_name
  
  def setup_editor_widget_for_bunfoe_instance(self, instance, disabled=None) -> BunfoeWidget:
    top_level_bunfoe_type = type(instance)
    if top_level_bunfoe_type not in self.cached_top_level_bunfoe_editor_widgets:
      bunfoe_editor_widget = self.make_bunfoe_editor_widget_for_type(top_level_bunfoe_type)
      self.cached_top_level_bunfoe_editor_widgets[top_level_bunfoe_type] = bunfoe_editor_widget
    bunfoe_editor_widget = self.cached_top_level_bunfoe_editor_widgets[top_level_bunfoe_type]
    bunfoe_editor_widget.show()
    
    self.set_field_values_for_bunfoe_instance(instance, bunfoe_editor_widget, disabled=disabled)
    bunfoe_editor_widget.setProperty('bunfoe_instance', instance)
    return bunfoe_editor_widget
  
  def make_bunfoe_editor_widget_for_type(self, bunfoe_type: typing.Type) -> BunfoeWidget:
    if issubclass(bunfoe_type, Vector):
      return self.make_bunfoe_editor_widget_for_vector_type(bunfoe_type)
    elif issubclass(bunfoe_type, Matrix):
      return self.make_bunfoe_editor_widget_for_matrix_type(bunfoe_type)
    
    form_layout = QFormLayout()
    form_layout.setContentsMargins(0, 0, 0, 0)
    
    for field in fields(bunfoe_type):
      field_widget = self.make_widget_for_field(field)
      if field_widget is None:
        continue
      pretty_field_name = self.prettify_name(field.name)
      form_layout.addRow(pretty_field_name, field_widget)
    
    bunfoe_editor_widget = BunfoeWidget(self)
    bunfoe_editor_widget.setLayout(form_layout)
    
    return bunfoe_editor_widget
  
  def set_field_values_for_bunfoe_instance(self, instance, bunfoe_widget: BunfoeWidget, disabled=None):
    layout = bunfoe_widget.layout()
    self.set_field_values_for_bunfoe_instance_recursive(instance, layout, disabled=disabled)
  
  def set_field_values_for_bunfoe_instance_recursive(self, instance, layout: QLayout, disabled=None):
    for i in range(layout.count()):
      item = layout.itemAt(i)
      widget = item.widget()
      if widget:
        field_type = widget.property('field_type')
        access_path = widget.property('access_path')
        if access_path is not None:
          value = self.get_instance_value(instance, access_path)
          self.set_widget_value(widget, value, field_type, instance, disabled=disabled)
      
      sublayout = item.layout()
      if sublayout:
        field_type = sublayout.property('field_type')
        access_path = sublayout.property('access_path')
        if access_path is not None:
          assert not issubclass(field_type, BUNFOE)
          value = self.get_instance_value(instance, access_path)
          assert value is not None
        self.set_field_values_for_bunfoe_instance_recursive(instance, sublayout, disabled=disabled)
  
  def make_bunfoe_editor_widget_for_vector_type(self, bunfoe_type: typing.Type) -> BunfoeWidget:
    box_layout = QHBoxLayout()
    box_layout.setContentsMargins(0, 0, 0, 0)
    
    for field in fields(bunfoe_type):
      field_widget = self.make_widget_for_field(field)
      if field_widget is None:
        continue
      
      field_layout = QHBoxLayout()
      box_layout.addLayout(field_layout)
      
      pretty_field_name = self.prettify_name(field.name)
      field_label = QLabel(pretty_field_name)
      field_layout.addWidget(field_label)
      
      if isinstance(field_widget, QWidget):
        field_layout.addWidget(field_widget)
      elif isinstance(field_widget, QLayout):
        field_layout.addLayout(field_widget)
      else:
        raise NotImplementedError
      
      field_layout.addStretch(1)
    
    box_layout.addStretch(1)
    
    bunfoe_editor_widget = BunfoeWidget(self)
    bunfoe_editor_widget.setLayout(box_layout)
    
    return bunfoe_editor_widget
  
  def make_bunfoe_editor_widget_for_matrix_type(self, bunfoe_type: typing.Type) -> BunfoeWidget:
    box_layout = QVBoxLayout()
    box_layout.setContentsMargins(0, 0, 0, 0)
    
    for field in fields(bunfoe_type):
      type_args = typing.get_args(field.type)
      arg_type = type_args[0]
      field_widget = self.add_all_sequence_elements_to_static_layout(arg_type, field.length, [('attr', field.name)], show_indexes=False)
      if field_widget is None:
        continue
      
      if isinstance(field_widget, QWidget):
        box_layout.addWidget(field_widget)
      elif isinstance(field_widget, QLayout):
        box_layout.addLayout(field_widget)
      else:
        raise NotImplementedError
    
    box_layout.addStretch(1)
    
    bunfoe_editor_widget = BunfoeWidget(self)
    bunfoe_editor_widget.setLayout(box_layout)
    
    return bunfoe_editor_widget
  
  def add_all_sequence_elements_to_new_layout(self, field: Field) -> QLayout:
    # Creates widgets to allow editing the elements of a sequence.
    # If we were to create a widget for each and every element of every sequence, it would take a
    # while to set up the widgets the first time, and also take up a lot of unnecessary space on the
    # screen. So instead, we try to create dynamic widgets wherever possible.
    # A dynamic widget is a single editor widget shared between all of the elements of the sequence,
    # plus a combobox to allow switching which one is currently selected and actively being edited.
    
    assert isinstance(field.length, int) and field.length > 0
    type_args = typing.get_args(field.type)
    assert len(type_args) == 1
    arg_type = type_args[0]
    
    use_static_layout = False
    if not all(at == arg_type for at in type_args):
      # Can't use a dynamic layout if the args aren't all the same type.
      use_static_layout = True
    elif issubclass(arg_type, RGBA):
      # Color selector buttons are small and simple, so allow showing multiple at once.
      use_static_layout = True
    # if len(type_args) > 4:
    #   use_static_layout = False
    
    if use_static_layout:
      return self.add_all_sequence_elements_to_static_layout(arg_type, field.length, [('attr', field.name)])
    else:
      return self.add_all_sequence_elements_to_dynamic_layout(arg_type, field.length, [('attr', field.name)])
  
  def add_all_sequence_elements_to_static_layout(self, arg_type, field_length, access_path, show_indexes=True) -> QLayout:
    # Creates a widget for each element of a sequence, arranged horizontally.
    
    box_layout = QHBoxLayout()
    
    for i in range(field_length):
      arg_widget = self.make_widget_for_type(arg_type, access_path + [('item', i)])
      
      column_layout = QVBoxLayout()
      box_layout.addLayout(column_layout)
      
      if show_indexes:
        if field_length > 10:
          index_str = self.window().stringify_number(i, min_hex_chars=1)
        else:
          # Force decimal for small numbers to avoid taking up space.
          index_str = str(i)
        column_header_label = QLabel(index_str)
        column_header_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        column_layout.addWidget(column_header_label, stretch=0)
      
      if isinstance(arg_widget, QWidget):
        column_layout.addWidget(arg_widget)
      elif isinstance(arg_widget, QLayout):
        column_layout.addLayout(arg_widget)
      else:
        raise NotImplementedError
      
      column_layout.addStretch(1)
    
    box_layout.addStretch(1)
    
    return box_layout
  
  def add_all_sequence_elements_to_dynamic_layout(self, arg_type, field_length, access_path) -> QLayout:
    # Creates one widget to be shared by all elements of a sequence, plus a combobox that allows
    # for switching which one is actively being edited.
    
    box_layout = QVBoxLayout()
    
    combobox = QComboBox()
    combobox.setSizePolicy(QSizePolicy.Policy.Maximum, combobox.sizePolicy().verticalPolicy())
    for i in range(field_length):
      index_str = self.window().stringify_number(i, min_hex_chars=1)
      combobox.addItem(f"Selected: {index_str}")
    box_layout.addWidget(combobox)
    
    # Use the combobox itself as the 'index' into this sequence.
    arg_widget = self.make_widget_for_type(arg_type, access_path + [('item', combobox)])
    
    # When selecting a blank (None) element, we don't want the rest of the layout to get messed up.
    # So we make the widget still take up its normal amount of space even when it isn't visible.
    size_policy = arg_widget.sizePolicy()
    size_policy.setRetainSizeWhenHidden(True)
    arg_widget.setSizePolicy(size_policy)
    
    box_layout.addWidget(arg_widget)
    
    combobox.setProperty('indexed_widget', arg_widget)
    combobox.currentIndexChanged.connect(self.index_combobox_value_changed)
    
    box_layout.addStretch(1)
    
    return box_layout
  
  def index_combobox_value_changed(self, new_index: int):
    combobox: QComboBox = self.sender()
    indexed_widget: QWidget = combobox.property('indexed_widget')
    field_type = indexed_widget.property('field_type')
    access_path = indexed_widget.property('access_path')
    instance = indexed_widget.property('field_owner')
    value = self.get_instance_value(instance, access_path)
    self.set_widget_value(indexed_widget, value, field_type, instance)
  
  def make_widget_for_field(self, field: Field):
    if field.name.startswith('_padding'):
      # No need to show these.
      return None
    
    if isinstance(field.type, typing.GenericAlias) and field.type.__origin__ == list:
      return self.add_all_sequence_elements_to_new_layout(field)
    else:
      return self.make_widget_for_type(field.type, [('attr', field.name)])
  
  def make_widget_for_type(self, field_type: typing.Type, access_path: list[tuple]):
    if issubclass(field_type, int) and field_type in fs.PRIMITIVE_TYPE_TO_BYTE_SIZE:
      widget = self.make_spinbox_for_int(field_type)
    elif issubclass(field_type, float):
      widget = self.make_spinbox_for_float(field_type)
    elif issubclass(field_type, bool):
      widget = self.make_checkbox_for_bool(field_type)
    elif issubclass(field_type, fs.u16Rot):
      widget = self.make_spinbox_for_rotation(field_type)
    elif isinstance(field_type, typing.GenericAlias) and field_type.__origin__ in [fs.FixedStr, fs.MagicStr]:
      widget = self.make_line_edit_for_str(field_type)
    elif issubclass(field_type, Enum):
      widget = self.make_combobox_for_enum(field_type)
    elif issubclass(field_type, RGBA):
      widget = self.make_button_for_color(field_type)
    elif issubclass(field_type, BUNFOE):
      widget = self.make_bunfoe_editor_widget_for_type(field_type)
    else:
      print(f"Field type not implemented: {field_type}")
      raise NotImplementedError
    
    widget.setProperty('field_type', field_type)
    widget.setProperty('access_path', access_path)
    if isinstance(widget, QWidget):
      # Prevent widgets from expanding to take up the full width of the scroll area.
      widget.setSizePolicy(QSizePolicy.Policy.Maximum, widget.sizePolicy().verticalPolicy())
    return widget
  
  def set_widget_value(self, widget: QWidget, value, field_type: typing.Type, instance, disabled=None):
    widget.setProperty('field_owner', instance)
    
    if value is None:
      # TODO: for blank entries in a list, put a placeholder button in place of the widget
      widget.hide()
      return
    widget.show()
    
    widget.blockSignals(True)
    
    if isinstance(widget, BigIntSpinbox):
      assert issubclass(field_type, int)
      widget.setValue(value)
    elif isinstance(widget, QDoubleSpinBox):
      assert issubclass(field_type, float)
      widget.setValue(value)
    elif isinstance(widget, QCheckBox):
      assert issubclass(field_type, bool)
      widget.setChecked(value)
    elif isinstance(widget, QLineEdit):
      assert issubclass(field_type, str)
      widget.setText(value)
    elif isinstance(widget, QComboBox):
      assert issubclass(field_type, Enum)
      if len(field_type) > 0:
        index_of_value = list(field_type).index(value)
        widget.setCurrentIndex(index_of_value)
      else:
        widget.setCurrentIndex(-1)
    elif isinstance(widget, QPushButton):
      assert issubclass(field_type, RGBA)
      self.set_background_for_color_button(widget, value)
    elif issubclass(field_type, BUNFOE):
      self.set_field_values_for_bunfoe_instance(value, widget, disabled=disabled)
    else:
      print(f"Field type not implemented: {field_type}")
      raise NotImplementedError
    
    if disabled is not None:
      if isinstance(widget, QWidget):
        widget.setDisabled(disabled)
      elif isinstance(widget, QLayout):
        self.set_layout_disabled_recursive(widget, disabled=disabled)
      else:
        raise NotImplementedError
    
    widget.blockSignals(False)
  
  def get_instance_value(self, instance, access_path: list[tuple]):
    for access_type, access_arg in access_path:
      if access_type == 'attr':
        instance = getattr(instance, access_arg)
      elif access_type == 'item':
        if isinstance(access_arg, QComboBox):
          # Dynamic widget indexing.
          access_arg = access_arg.currentIndex()
        instance = instance[access_arg]
      else:
        raise NotImplementedError
    return instance
  
  def set_instance_value(self, instance, access_path: list[tuple], value):
    for access_type, access_arg in access_path[:-1]:
      if access_type == 'attr':
        instance = getattr(instance, access_arg)
      elif access_type == 'item':
        if isinstance(access_arg, QComboBox):
          # Dynamic widget indexing.
          access_arg = access_arg.currentIndex()
        instance = instance[access_arg]
      else:
        raise NotImplementedError
    
    access_type, access_arg = access_path[-1]
    if access_type == 'attr':
      setattr(instance, access_arg, value)
    elif access_type == 'item':
      instance[access_arg] = value
    else:
      raise NotImplementedError
  
  def make_checkbox_for_bool(self, field_type: typing.Type):
    checkbox = QCheckBox()
    checkbox.stateChanged.connect(self.checkbox_state_changed)
    return checkbox
  
  def checkbox_state_changed(self, state: int):
    checkbox: QCheckBox = self.sender()
    field_owner: object = checkbox.property('field_owner')
    access_path = checkbox.property('access_path')
    self.set_instance_value(field_owner, access_path, checkbox.isChecked())
    self.field_value_changed.emit()
  
  def make_combobox_for_enum(self, field_type: typing.Type):
    combobox = QComboBox()
    for i, enum_value in enumerate(field_type):
      pretty_name = self.prettify_name(enum_value.name, title=False)
      combobox.addItem(pretty_name)
      combobox.setItemData(i, enum_value)
    
    combobox.currentIndexChanged.connect(self.combobox_value_changed)
    
    return combobox
  
  def combobox_value_changed(self, new_index: int):
    combobox: QComboBox = self.sender()
    enum_value = combobox.currentData()
    field_owner: object = combobox.property('field_owner')
    access_path = combobox.property('access_path')
    self.set_instance_value(field_owner, access_path, enum_value)
    self.field_value_changed.emit()
  
  def make_spinbox_for_int(self, field_type):
    assert field_type in fs.PRIMITIVE_TYPE_TO_BYTE_SIZE
    assert issubclass(field_type, int)
    spinbox = BigIntSpinbox()
    min_val = 0
    byte_size = fs.PRIMITIVE_TYPE_TO_BYTE_SIZE[field_type]
    max_val = (1 << byte_size*8) - 1
    if fs.PRIMITIVE_TYPE_IS_SIGNED[field_type]:
      min_val -= 1 << (byte_size*8 - 1)
      max_val -= 1 << (byte_size*8 - 1)
    spinbox.setRange(min_val, max_val)
    spinbox.setWrapping(True)
    
    fm = QFontMetrics(QFont())
    min_val_width = fm.horizontalAdvance(str(min_val))
    max_val_width = fm.horizontalAdvance(str(max_val))
    max_width = max(min_val_width, max_val_width)
    spinbox.setMinimumWidth(max_width+23)
    
    spinbox.valueChanged.connect(self.spinbox_value_changed)
    return spinbox
  
  def make_spinbox_for_float(self, field_type):
    spinbox = QDoubleSpinBox()
    assert field_type == float
    spinbox.setRange(float('-inf'), float('inf'))
    spinbox.setMinimumWidth(60)
    
    spinbox.valueChanged.connect(self.spinbox_value_changed)
    return spinbox
  
  def make_spinbox_for_rotation(self, field_type):
    # TODO: need a custom spinbox subclass for u16 rotations.
    assert field_type == fs.u16Rot
    return self.make_spinbox_for_int(fs.u16)
  
  def spinbox_value_changed(self, new_value):
    spinbox: QSpinBox = self.sender()
    field_owner: object = spinbox.property('field_owner')
    access_path = spinbox.property('access_path')
    self.set_instance_value(field_owner, access_path, new_value)
    self.field_value_changed.emit()
  
  def make_line_edit_for_str(self, field_type):
    line_edit = QLineEdit()
    max_len = typing.get_args(field_type)[0]
    line_edit.setMaxLength(max_len)
    line_edit.editingFinished.connect(self.line_edit_value_changed)
    return line_edit
  
  def line_edit_value_changed(self):
    line_edit: QLineEdit = self.sender()
    field_owner: object = line_edit.property('field_owner')
    access_path = line_edit.property('access_path')
    new_value = line_edit.text()
    self.set_instance_value(field_owner, access_path, new_value)
    self.field_value_changed.emit()
  
  def make_button_for_color(self, field_type):
    button = QPushButton()
    button.setText("Click to set color")
    button.clicked.connect(self.open_color_chooser)
    # TODO: set property to enable alpha or disable it, depending on the class of the color
    # or maybe we can just detect that from the existing 'field_type' property
    return button
  
  def set_background_for_color_button(self, button: QPushButton, color: RGBA):
    # TODO: RGB support
    # if len(color) == 3:
    #   r, g, b = color
    #   a = 255
    # elif len(color) == 4:
    #   r, g, b, a = color
    # else:
    #   QMessageBox.warning(self, "Unknown color format", "Color is neither RGB nor RGBA.")
    #   return
    
    r, g, b = color.r, color.g, color.b
    
    # Depending on the value of the background color of the button, we need to make the text color either black or white for contrast.
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    if v > 0.5:
      text_color = (0, 0, 0)
    else:
      text_color = (255, 255, 255)
    
    button.setStyleSheet(
      "background-color: rgb(%d, %d, %d);" % (r, g, b) + \
      "color: rgb(%d, %d, %d);" % text_color,
    )
  
  def open_color_chooser(self):
    button: QPushButton = self.sender()
    field_owner: object = button.property('field_owner')
    field_type = button.property('field_type')
    access_path = button.property('access_path')
    
    color = self.get_instance_value(field_owner, access_path)
    
    r, g, b = color.r, color.g, color.b
    a = 255
    has_alpha = True
    if has_alpha:
      a = color.a
    # TODO: RGB/RGBA support with field_type
    # has_alpha = False
    # if len(color) == 3:
    #   r, g, b = color
    #   a = 255
    # elif len(color) == 4:
    #   r, g, b, a = color
    #   has_alpha = True
    # else:
    #   QMessageBox.warning(self, "Unknown color format", "Color is neither RGB nor RGBA.")
    #   return
    
    initial_color = QColor(r, g, b, a)
    color_dialog_options = QColorDialog.ColorDialogOption(0)
    if has_alpha:
      color_dialog_options |= QColorDialog.ShowAlphaChannel
    qcolor = QColorDialog.getColor(initial_color, self, "Select color", options=color_dialog_options)
    if not qcolor.isValid():
      return
    
    color.r = qcolor.red()
    color.g = qcolor.green()
    color.b = qcolor.blue()
    if has_alpha:
      color.a = qcolor.alpha()
    
    self.set_background_for_color_button(button, color)
    self.field_value_changed.emit()
