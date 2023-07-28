import time
import os
import mss
import numpy as np
import utils
from process import process_image, draw_results
import cv2
import chromadb

# chroma_client = chromadb.Client()
# collection = chroma_client.create_collection(name="pmr")

os.makedirs("screenshots", exist_ok=True)
sct = mss.mss()

i = 0
while True:
    window_title = utils.get_active_window()
    print(window_title)
    im = np.array(sct.grab(sct.monitors[1]))
    results = process_image(im)
    im = draw_results(results, im)
    cv2.imshow("image", im)
    cv2.waitKey(0)
    print(results)
    exit()
    # cv2.imwrite("screenshots/" + str(i) + ".png", im)
    i += 1
    time.sleep(1)
