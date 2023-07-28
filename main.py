import time
import os
import mss
import numpy as np
import utils
from process import process_image
import chromadb

chroma_client = chromadb.Client()

os.makedirs("screenshots", exist_ok=True)
sct = mss.mss()

i = 0
while True:
    window_title = utils.get_active_window()
    print(window_title)
    im = np.array(sct.grab(sct.monitors[1]))
    result = process_image(im)
    # cv2.imwrite("screenshots/" + str(i) + ".png", im)
    i += 1
    time.sleep(0.5)
