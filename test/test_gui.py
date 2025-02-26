
def test_gui_launches(qtbot):
  from gcft_ui.main_window import GCFTWindow
  window = GCFTWindow()
  window.save_settings()
