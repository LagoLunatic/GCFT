import typing
from types import GenericAlias
from enum import Enum
import colorsys
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *

from gclib import fs_helpers as fs
from gclib.bunfoe import BUNFOE, Field, fields

from gcft_ui.custom_widgets import BigIntSpinbox
from gclib.bunfoe_types import Vector, Matrix, RGBA

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from gcft_ui.main_window import GCFTWindow

class BunfoeWidget(QWidget):
  pass

class BunfoeEditor(QWidget):
  gcft_window: 'GCFTWindow'
  
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
      assert item is not None
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
    assert layout is not None
    self.set_field_values_for_bunfoe_instance_recursive(instance, layout, disabled=disabled)
  
  def set_field_values_for_bunfoe_instance_recursive(self, instance, layout: QLayout, disabled=None):
    for i in range(layout.count()):
      item = layout.itemAt(i)
      assert item is not None
      widget = item.widget()
      if widget:
        field_type = widget.property('field_type')
        access_path = widget.property('access_path')
        if access_path is not None:
          final_access_type, final_access_arg = access_path[-1]
          if final_access_type == 'item' and isinstance(final_access_arg, QComboBox):
            # Dynamic widget indexing.
            combobox = final_access_arg
            list_value = self.get_instance_value(instance, access_path[:-1])
            self.populate_combobox_from_list(combobox, list_value)
            if len(list_value) > 0:
              value = self.get_instance_value(instance, access_path)
              self.set_widget_value(widget, value, field_type, instance, disabled=disabled)
              # Select the first item and update the new/delete buttons to be initially disabled or not.
              combobox.setCurrentIndex(0)
            else:
              self.set_widget_value(widget, None, field_type, instance, disabled=disabled)
              # Update the new/delete buttons to be initially disabled or not.
              combobox.currentIndexChanged.emit(combobox.currentIndex())
          else:
            # Static list layout.
            value = self.get_instance_value(instance, access_path)
            self.set_widget_value(widget, value, field_type, instance, disabled=disabled)
        
        # Uncomment the below code to make index comboboxes reset to element zero every time the
        # selection changes.
        # arg_widget = widget.property('indexed_widget')
        # if arg_widget is not None:
        #   combobox: QComboBox = widget
        #   combobox.setCurrentIndex(0)
      
      sublayout = item.layout()
      if sublayout:
        field_type = sublayout.property('field_type')
        access_path = sublayout.property('access_path')
        if access_path is not None:
          assert not issubclass(field_type, BUNFOE)
          value = self.get_instance_value(instance, access_path)
          assert value is not None
        self.set_field_values_for_bunfoe_instance_recursive(instance, sublayout, disabled=disabled)
  
  def populate_combobox_from_list(self, combobox: QComboBox, list_value: list):
    combobox.blockSignals(True)
    combobox.clear()
    for i in range(len(list_value)):
      index_str = self.gcft_window.stringify_number(i, min_hex_chars=1)
      combobox.addItem(index_str)
    combobox.setCurrentIndex(-1)
    combobox.blockSignals(False)
  
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
    
    if isinstance(field.length, int) and field.length > 0:
      # Fixed-length list.
      initial_length = field.length
      if 'indexed_by' in field.metadata:
        # MAT3 list that can have None in it. Allow adding and removing elements.
        allow_add_remove = True
      else:
        # Normal fixed-length list, cannot have None. Do not allow adding or removing elements.
        allow_add_remove = False
    else:
      # Dynamic-length list. Allow adding and removing elements from the list.
      initial_length = 0
      allow_add_remove = True
    
    type_args = typing.get_args(field.type)
    assert len(type_args) == 1
    arg_type = type_args[0]
    
    use_static_layout = False
    if not all(at == arg_type for at in type_args):
      # Can't use a dynamic layout if the args aren't all the same type.
      use_static_layout = True
    elif issubclass(arg_type, RGBA) or arg_type == bool or issubclass(arg_type, fs.MappedBool):
      # The widgets for these types are small and simple, so allow showing multiple at once.
      use_static_layout = True
    # if len(type_args) > 4:
    #   use_static_layout = False
    
    if use_static_layout:
      return self.add_all_sequence_elements_to_static_layout(arg_type, initial_length, [('attr', field.name)], allow_add_remove=allow_add_remove)
    else:
      return self.add_all_sequence_elements_to_dynamic_layout(arg_type, initial_length, [('attr', field.name)], allow_add_remove=allow_add_remove)
  
  def add_all_sequence_elements_to_static_layout(self, arg_type, field_length, access_path, show_indexes=True, allow_add_remove=False) -> QLayout:
    # Creates a widget for each element of a sequence, arranged horizontally.
    
    box_layout = QHBoxLayout()
    
    prev_arg_widget = None
    for i in range(field_length):
      arg_widget = self.make_widget_for_type(arg_type, access_path + [('item', i)])
      
      column_layout = QVBoxLayout()
      box_layout.addLayout(column_layout)
      
      if show_indexes:
        if field_length > 10:
          index_str = self.gcft_window.stringify_number(i, min_hex_chars=1)
        else:
          # Force decimal for small numbers to avoid taking up space.
          index_str = str(i)
        column_header_label = QLabel(index_str)
        column_header_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        column_layout.addWidget(column_header_label, stretch=0)
      
      if isinstance(arg_widget, QWidget):
        column_layout.addWidget(arg_widget)
      else:
        raise NotImplementedError
      
      arg_widget.setProperty('fixed_list_length', field_length)
      arg_widget.setProperty('prev_arg_widget', prev_arg_widget)
      arg_widget.setProperty('next_arg_widget', None)
      
      if allow_add_remove:
        new_button = QPushButton("+")
        new_button.setMaximumWidth(20)
        column_layout.addWidget(new_button)
        new_button.hide()
        
        delete_button = QPushButton("-")
        delete_button.setMaximumWidth(20)
        column_layout.addWidget(delete_button)
        delete_button.hide()
        
        new_button.setProperty('arg_widget', arg_widget)
        new_button.clicked.connect(self.add_new_to_static_layout_sequence_button_clicked)
        delete_button.setProperty('arg_widget', arg_widget)
        delete_button.clicked.connect(self.delete_from_static_layout_sequence_button_clicked)
        
        arg_widget.setProperty('static_seq_new_button', new_button)
        arg_widget.setProperty('static_seq_delete_button', delete_button)
        if prev_arg_widget is not None:
          prev_arg_widget.setProperty('next_arg_widget', arg_widget)
    
      column_layout.addStretch(1)
      
      prev_arg_widget = arg_widget
    
    box_layout.addStretch(1)
    
    return box_layout
  
  def add_new_to_static_layout_sequence_button_clicked(self, checked: bool):
    new_button = self.sender()
    assert isinstance(new_button, QPushButton)
    arg_widget: QWidget = new_button.property('arg_widget')
    prev_arg_widget: QWidget = arg_widget.property('prev_arg_widget')
    next_arg_widget: QWidget = arg_widget.property('next_arg_widget')
    field_type = arg_widget.property('field_type')
    access_path = arg_widget.property('access_path')
    instance = arg_widget.property('field_owner')
    fixed_list_length = arg_widget.property('fixed_list_length')
    
    curr_value = self.get_instance_value(instance, access_path)
    list_access_path = access_path[:-1]
    final_access_type, final_access_arg = access_path[-1]
    assert final_access_type == 'item'
    clicked_index: int = final_access_arg
    list_value: list = self.get_instance_value(instance, list_access_path)
    assert fixed_list_length > 0 # Fixed-length list.
    assert curr_value is None
    assert clicked_index < fixed_list_length
    new_element = field_type()
    list_value[clicked_index] = new_element
    
    # Update the GUI.
    self.set_widget_value(arg_widget, new_element, field_type, instance)
    prev_index = clicked_index - 1
    if prev_index >= 0:
      assert list_value[prev_index] is not None
      assert prev_arg_widget is not None
      
      # Update the GUI for the previous widget (to hide the delete button for that one).
      prev_access_path = prev_arg_widget.property('access_path')
      prev_instance = prev_arg_widget.property('field_owner')
      prev_value = self.get_instance_value(prev_instance, prev_access_path)
      self.set_widget_value(prev_arg_widget, prev_value, field_type, instance)
    next_index = clicked_index + 1
    if next_index < fixed_list_length:
      assert list_value[next_index] is None
      assert next_arg_widget is not None
      
      # Update the GUI for the next widget (to show the new button for that one).
      next_access_path = next_arg_widget.property('access_path')
      next_instance = next_arg_widget.property('field_owner')
      next_value = self.get_instance_value(next_instance, next_access_path)
      self.set_widget_value(next_arg_widget, next_value, field_type, instance)
  
  def delete_from_static_layout_sequence_button_clicked(self, checked: bool):
    delete_button = self.sender()
    assert isinstance(delete_button, QPushButton)
    arg_widget: QWidget = delete_button.property('arg_widget')
    prev_arg_widget: QWidget = arg_widget.property('prev_arg_widget')
    next_arg_widget: QWidget = arg_widget.property('next_arg_widget')
    field_type = arg_widget.property('field_type')
    access_path = arg_widget.property('access_path')
    instance = arg_widget.property('field_owner')
    fixed_list_length = arg_widget.property('fixed_list_length')
    
    curr_value = self.get_instance_value(instance, access_path)
    list_access_path = access_path[:-1]
    final_access_type, final_access_arg = access_path[-1]
    assert final_access_type == 'item'
    clicked_index: int = final_access_arg
    list_value: list = self.get_instance_value(instance, list_access_path)
    assert fixed_list_length > 0 # Fixed-length list.
    assert curr_value is not None
    assert clicked_index < fixed_list_length
    list_value[clicked_index] = None
    
    # Update the GUI.
    self.set_widget_value(arg_widget, None, field_type, instance)
    prev_index = clicked_index - 1
    if prev_index >= 0:
      assert list_value[prev_index] is not None
      assert prev_arg_widget is not None
      
      # Update the GUI for the previous widget (to show the delete button for that one).
      prev_access_path = prev_arg_widget.property('access_path')
      prev_instance = prev_arg_widget.property('field_owner')
      prev_value = self.get_instance_value(prev_instance, prev_access_path)
      self.set_widget_value(prev_arg_widget, prev_value, field_type, instance)
    next_index = clicked_index + 1
    if next_index < fixed_list_length:
      assert list_value[next_index] is None
      assert next_arg_widget is not None
      
      # Update the GUI for the next widget (to hide the new button for that one).
      next_access_path = next_arg_widget.property('access_path')
      next_instance = next_arg_widget.property('field_owner')
      next_value = self.get_instance_value(next_instance, next_access_path)
      self.set_widget_value(next_arg_widget, next_value, field_type, instance)
  
  def add_all_sequence_elements_to_dynamic_layout(self, arg_type, field_length, access_path, allow_add_remove=False) -> QLayout:
    # Creates one widget to be shared by all elements of a sequence, plus a combobox that allows
    # for switching which one is actively being edited.
    
    box_layout = QVBoxLayout()
    
    top_row_layout = QHBoxLayout()
    box_layout.addLayout(top_row_layout)
    
    combobox = QComboBox()
    combobox.setSizePolicy(QSizePolicy.Policy.Maximum, combobox.sizePolicy().verticalPolicy())
    for i in range(field_length):
      index_str = self.gcft_window.stringify_number(i, min_hex_chars=1)
      combobox.addItem(index_str)
    top_row_layout.addWidget(combobox)
    
    if allow_add_remove:
      new_button = QPushButton("+")
      new_button.setMaximumWidth(20)
      top_row_layout.addWidget(new_button)
      
      delete_button = QPushButton("-")
      delete_button.setMaximumWidth(20)
      top_row_layout.addWidget(delete_button)
    
    spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    top_row_layout.addItem(spacer)
    
    # Use the combobox itself as the 'index' into this sequence.
    arg_widget = self.make_widget_for_type(arg_type, access_path + [('item', combobox)])
    
    # When selecting a blank (None) element, we don't want the rest of the layout to get messed up.
    # So we make the widget still take up its normal amount of space even when it isn't visible.
    size_policy = arg_widget.sizePolicy()
    size_policy.setRetainSizeWhenHidden(True)
    arg_widget.setSizePolicy(size_policy)
    
    box_layout.addWidget(arg_widget)
    
    combobox.setProperty('indexed_widget', arg_widget)
    combobox.setProperty('fixed_list_length', field_length)
    combobox.currentIndexChanged.connect(self.dynamic_layout_sequence_index_combobox_value_changed)
    
    if allow_add_remove:
      new_button.setProperty('index_combobox', combobox)
      combobox.setProperty('dynamic_seq_new_button', new_button)
      new_button.clicked.connect(self.add_new_to_dynamic_layout_sequence_button_clicked)
      
      delete_button.setProperty('index_combobox', combobox)
      combobox.setProperty('dynamic_seq_delete_button', delete_button)
      delete_button.clicked.connect(self.delete_from_dynamic_layout_sequence_button_clicked)
    
    box_layout.addStretch(1)
    
    return box_layout
  
  def dynamic_layout_sequence_index_combobox_value_changed(self, new_index: int):
    combobox = self.sender()
    assert isinstance(combobox, QComboBox)
    indexed_widget: QWidget = combobox.property('indexed_widget')
    field_type = indexed_widget.property('field_type')
    access_path = indexed_widget.property('access_path')
    instance = indexed_widget.property('field_owner')
    fixed_list_length = combobox.property('fixed_list_length')
    value = self.get_instance_value(instance, access_path)
    self.set_widget_value(indexed_widget, value, field_type, instance)
    
    new_button = combobox.property('dynamic_seq_new_button')
    delete_button = combobox.property('dynamic_seq_delete_button')
    if new_button is not None:
      assert isinstance(new_button, QPushButton)
      assert isinstance(delete_button, QPushButton)
      if fixed_list_length > 0:
        # For fixed-length lists:
        # Grey out the add button if the current slot is already filled.
        # Grey out the remove button if the current slot is already empty.
        new_button.setDisabled(value is not None)
        delete_button.setDisabled(value is None)
      else:
        # For dynamic-length lists:
        # Grey out the remove button if the list is empty.
        # Never grey out the add button. (Limit dynamic-length lists to a maximum size is not currently supported.)
        delete_button.setDisabled(value is None)
  
  def add_new_to_dynamic_layout_sequence_button_clicked(self, checked: bool):
    new_button = self.sender()
    assert isinstance(new_button, QPushButton)
    combobox: QComboBox = new_button.property('index_combobox')
    indexed_widget: QWidget = combobox.property('indexed_widget')
    field_type = indexed_widget.property('field_type')
    access_path = indexed_widget.property('access_path')
    instance = indexed_widget.property('field_owner')
    fixed_list_length = combobox.property('fixed_list_length')
    
    curr_value = self.get_instance_value(instance, access_path)
    list_access_path = access_path[:-1]
    list_value: list = self.get_instance_value(instance, list_access_path)
    curr_index = combobox.currentIndex()
    if fixed_list_length > 0:
      # Fixed-length list. Cannot actually add/delete elements, instead 'empty' slots are filled with None.
      assert curr_value is None
      new_element = field_type()
      list_value[curr_index] = new_element
      combobox.currentIndexChanged.emit(curr_index) # Update the widget
    else:
      # Dynamic-length list.
      new_element = field_type()
      new_element_index = combobox.currentIndex() + 1 # Insert the new element after the currently selected one
      list_value.insert(new_element_index, new_element)
      self.populate_combobox_from_list(combobox, list_value)
      combobox.setCurrentIndex(new_element_index)
      # If new_element_index was -1 we would need to emit the signal, but that should be impossible here so we just assert instead.
      # combobox.currentIndexChanged.emit(new_element_index)
      assert new_element_index >= 0
  
  def delete_from_dynamic_layout_sequence_button_clicked(self, checked: bool):
    delete_button = self.sender()
    assert isinstance(delete_button, QPushButton)
    combobox: QComboBox = delete_button.property('index_combobox')
    indexed_widget: QWidget = combobox.property('indexed_widget')
    field_type = indexed_widget.property('field_type')
    access_path = indexed_widget.property('access_path')
    instance = indexed_widget.property('field_owner')
    fixed_list_length = combobox.property('fixed_list_length')
    
    curr_value = self.get_instance_value(instance, access_path)
    list_access_path = access_path[:-1]
    list_value: list = self.get_instance_value(instance, list_access_path)
    curr_index = combobox.currentIndex()
    if fixed_list_length > 0:
      # Fixed-length list. Cannot actually add/delete elements, instead 'empty' slots are filled with None.
      assert curr_value is not None
      list_value[curr_index] = None
      combobox.currentIndexChanged.emit(curr_index) # Update the widget
    else:
      # Dynamic-length list.
      del list_value[curr_index]
      self.populate_combobox_from_list(combobox, list_value)
      if curr_index >= len(list_value):
        curr_index = len(list_value) - 1
      combobox.setCurrentIndex(curr_index)
      if curr_index == -1:
        # Empty list, force the combobox to emit its signal since called setCurrentIndex(-1) won't do it.
        combobox.currentIndexChanged.emit(curr_index)
  
  def make_widget_for_field(self, field: Field):
    if field.name.startswith('_padding') or field.assert_default or field.bitfield:
      # No need to show these.
      return None
    
    if isinstance(field.type, GenericAlias) and field.type.__origin__ == list:
      return self.add_all_sequence_elements_to_new_layout(field)
    else:
      assert field.type is not None
      return self.make_widget_for_type(field.type, [('attr', field.name)])
  
  def make_widget_for_type(self, field_type: typing.Type, access_path: list[tuple]) -> QWidget:
    if issubclass(field_type, int) and field_type in fs.PRIMITIVE_TYPE_TO_BYTE_SIZE:
      widget = self.make_spinbox_for_int(field_type)
    elif issubclass(field_type, float):
      widget = self.make_spinbox_for_float(field_type)
    elif field_type == bool or issubclass(field_type, fs.MappedBool):
      widget = self.make_checkbox_for_bool(field_type)
    elif issubclass(field_type, fs.u16Rot):
      widget = self.make_spinbox_for_rotation(field_type)
    elif isinstance(field_type, GenericAlias) and field_type.__origin__ in [fs.FixedStr, fs.MagicStr]:
      widget = self.make_line_edit_for_str(field_type)
    elif issubclass(field_type, Enum):
      widget = self.make_combobox_for_enum(field_type)
    elif issubclass(field_type, RGBA):
      widget = self.make_button_for_color(field_type)
    elif issubclass(field_type, BUNFOE):
      widget = self.make_bunfoe_editor_widget_for_type(field_type)
    else:
      raise NotImplementedError(f"Field type not implemented: {field_type}")
    
    widget.setProperty('field_type', field_type)
    widget.setProperty('access_path', access_path)
    
    assert isinstance(widget, QWidget)
    # Prevent widgets from expanding to take up the full width of the scroll area.
    widget.setSizePolicy(QSizePolicy.Policy.Maximum, widget.sizePolicy().verticalPolicy())
    
    return widget
  
  def set_widget_value(self, widget: QWidget, value, field_type: typing.Type, instance, disabled=None):
    widget.setProperty('field_owner', instance)
    
    new_button: QPushButton = widget.property('static_seq_new_button')
    delete_button: QPushButton = widget.property('static_seq_delete_button')
    is_static_seq_item = False
    is_first_empty_static_seq_item = False
    is_last_nonempty_static_seq_item = False
    if new_button:
      is_static_seq_item = True
      access_path = widget.property('access_path')
      list_value: list = self.get_instance_value(instance, access_path[:-1])
      final_access_type, final_access_arg = access_path[-1]
      assert final_access_type == 'item'
      index_of_first_empty_item = list_value.index(None) if None in list_value else len(list_value)
      if final_access_arg == index_of_first_empty_item:
        is_first_empty_static_seq_item = True
      elif final_access_arg == index_of_first_empty_item - 1:
        is_last_nonempty_static_seq_item = True
    
    if value is None:
      # For blank entries in a list, put the add button as a placeholder where the widget would go.
      widget.hide()
      if is_static_seq_item:
        # Make this slot in a static sequence be a blank element.
        if is_first_empty_static_seq_item:
          # Only display the new button for the first None in the list.
          # We don't want to allow the user to create gaps by adding values later on, after the first None.
          # Note: Not sure if this restriction is really necessary or not, just adding it to be safe.
          new_button.show()
        else:
          new_button.hide()
        delete_button.hide()
      return
    
    if is_static_seq_item:
      if is_last_nonempty_static_seq_item:
        delete_button.show()
      else:
        delete_button.hide()
      new_button.hide()
    
    widget.show()
    
    widget.blockSignals(True)
    
    if isinstance(widget, BigIntSpinbox):
      assert issubclass(field_type, int)
      widget.setValue(value)
    elif isinstance(widget, QDoubleSpinBox):
      assert issubclass(field_type, float)
      widget.setValue(value)
    elif isinstance(widget, QCheckBox):
      assert field_type == bool or issubclass(field_type, fs.MappedBool)
      widget.setChecked(bool(value))
    elif isinstance(widget, QLineEdit):
      assert issubclass(field_type, str)
      widget.setText(value)
    elif isinstance(widget, QComboBox):
      assert issubclass(field_type, Enum)
      if len(field_type) > 0 and isinstance(value, field_type):
        index_of_value = list(field_type).index(value)
        widget.setCurrentIndex(index_of_value)
      else:
        # TODO: Is there some way we could display invalid values for enums instead of a blank combobox?
        widget.setCurrentIndex(-1)
    elif isinstance(widget, QPushButton):
      assert issubclass(field_type, RGBA)
      self.set_background_for_color_button(widget, value)
    elif issubclass(field_type, BUNFOE):
      assert isinstance(widget, BunfoeWidget)
      self.set_field_values_for_bunfoe_instance(value, widget, disabled=disabled)
    else:
      raise NotImplementedError(f"Field type not implemented: {field_type}")
    
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
        instance = self.get_instance_item(instance, access_arg)
      else:
        raise NotImplementedError
    return instance
  
  def set_instance_value(self, instance, access_path: list[tuple], value):
    for access_type, access_arg in access_path[:-1]:
      if access_type == 'attr':
        instance = getattr(instance, access_arg)
      elif access_type == 'item':
        instance = self.get_instance_item(instance, access_arg)
      else:
        raise NotImplementedError
    
    access_type, access_arg = access_path[-1]
    if access_type == 'attr':
      setattr(instance, access_arg, value)
    elif access_type == 'item':
      self.set_instance_item(instance, access_arg, value)
    else:
      raise NotImplementedError
  
  def get_instance_item(self, instance, index):
    if isinstance(index, QComboBox):
      # Dynamic widget indexing.
      index = index.currentIndex()
    if index == -1:
      return None
    return instance[index]
  
  def set_instance_item(self, instance, index, value):
    if isinstance(index, QComboBox):
      # Dynamic widget indexing.
      index = index.currentIndex()
    instance[index] = value
  
  def make_checkbox_for_bool(self, field_type: typing.Type):
    checkbox = QCheckBox()
    checkbox.stateChanged.connect(self.checkbox_state_changed)
    return checkbox
  
  def checkbox_state_changed(self, state: int):
    checkbox = self.sender()
    assert isinstance(checkbox, QCheckBox)
    field_owner: object = checkbox.property('field_owner')
    access_path = checkbox.property('access_path')
    self.set_instance_value(field_owner, access_path, checkbox.isChecked())
    self.field_value_changed.emit()
  
  def make_combobox_for_enum(self, field_type: typing.Type[Enum]):
    combobox = QComboBox()
    for i, enum_value in enumerate(field_type):
      pretty_name = self.prettify_name(enum_value.name, title=False)
      combobox.addItem(pretty_name)
      combobox.setItemData(i, enum_value)
    
    combobox.currentIndexChanged.connect(self.combobox_value_changed)
    
    return combobox
  
  def combobox_value_changed(self, new_index: int):
    combobox = self.sender()
    assert isinstance(combobox, QComboBox)
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
    spinbox = self.sender()
    assert isinstance(spinbox, QAbstractSpinBox)
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
    line_edit = self.sender()
    assert isinstance(line_edit, QLineEdit)
    field_owner: object = line_edit.property('field_owner')
    access_path = line_edit.property('access_path')
    new_value = line_edit.text()
    self.set_instance_value(field_owner, access_path, new_value)
    self.field_value_changed.emit()
  
  def make_button_for_color(self, field_type):
    button = QPushButton()
    button.setText("")
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
    if v > 0.7:
      text_color = (0, 0, 0)
    else:
      text_color = (255, 255, 255)
    
    button.setStyleSheet(
      "background-color: rgb(%d, %d, %d);" % (r, g, b) + \
      "color: rgb(%d, %d, %d);" % text_color,
    )
    button.setText("#%02X%02X%02X%02X" % color.rgba)
  
  def open_color_chooser(self):
    button = self.sender()
    assert isinstance(button, QPushButton)
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
      color_dialog_options |= QColorDialog.ColorDialogOption.ShowAlphaChannel
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

class BunfoeDialog(QDialog):
  @staticmethod
  def show_dialog_for_bunfoe(bunfoe_inst: BUNFOE, parent: BunfoeEditor, title):
    dialog = BunfoeDialog(parent)
    dialog.set_bunfoe_instance(bunfoe_inst, title)
    dialog.open()
    return dialog
  
  def __init__(self, parent: BunfoeEditor):
    super().__init__(parent)
    QVBoxLayout(self)
    self.bunfoe_editor = parent
    self.setModal(True)
  
  def set_bunfoe_instance(self, bunfoe_inst: BUNFOE, title: str):
    self.setWindowTitle(title)
    bunfoe_editor_widget = self.bunfoe_editor.setup_editor_widget_for_bunfoe_instance(bunfoe_inst)
    layout = self.layout()
    assert layout is not None
    layout.addWidget(bunfoe_editor_widget)
