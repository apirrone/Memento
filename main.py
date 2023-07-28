import time
import os
import mss
import numpy as np
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


os.makedirs("screenshots", exist_ok=True)
sct = mss.mss()

i = 0
while True:
    window_title = get_active_window()
    print(window_title)
    im = np.array(sct.grab(sct.monitors[1]))
    # cv2.imwrite("screenshots/" + str(i) + ".png", im)
    i += 1
    time.sleep(0.5)
