import Xlib.display

def get_active_window():
    display = Xlib.display.Display()
    window = display.get_input_focus().focus
    wmclass = window.get_wm_class()
    if wmclass is None:
        window = window.query_tree().parent
        wmclass = window.get_wm_class()
    if wmclass is None:
        return None
    winclass = wmclass[1]
    return winclass
