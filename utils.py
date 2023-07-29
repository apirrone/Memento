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


# check that a y coordinate is within a line with a tolerance of y_tol
def is_within_line(y, line, y_tol=5):
    return abs(y - line) < y_tol


# check if there is already a line of coordinate y
def line_exists(y, lines, y_tol=5):
    for line in lines.keys():
        if is_within_line(y, line, y_tol):
            return line
    return None
